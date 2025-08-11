import asyncio
import os
import pickle
from contextlib import AsyncExitStack
from typing import Optional, List, Dict, Any

import google.generativeai as genai
import gradio as gr
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# ========================
# CONFIG
# ========================
load_dotenv()
SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]

# ========================
# OAUTH HANDLER
# ========================
def get_oauth_credentials():
    creds = None
    token_path = "token.pickle"

    if os.path.exists(token_path):
        with open(token_path, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # El archivo client_secret.json debe venir de GCP (OAuth Client ID tipo Desktop App)
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secret.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(token_path, "wb") as token:
            pickle.dump(creds, token)

    return creds


# ========================
# MCP CLIENT
# ========================
def clean_schema_for_gemini(schema: dict) -> dict:
    if not isinstance(schema, dict):
        return schema
    cleaned = {}
    for k, v in schema.items():
        if k == "additionalProperties":
            continue
        if isinstance(v, dict):
            cleaned[k] = clean_schema_for_gemini(v)
        elif isinstance(v, list):
            cleaned[k] = [clean_schema_for_gemini(i) for i in v]
        else:
            cleaned[k] = v
    return cleaned


class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

        api_key = os.getenv('GEMINI_API_KEY')
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(os.getenv('GEMINI_MODEL', 'gemini-1.5-turbo'))

    async def connect_to_server(self):
        creds = get_oauth_credentials()
        
        # Guardamos el token temporalmente para que el MCP lo use
        token_json_path = "oauth_token.json"
        with open(token_json_path, "w") as f:
            f.write(creds.to_json())

        server_params = StdioServerParameters(
            command="google-analytics-mcp",
            args=[],
            env={"OAUTH_TOKEN_PATH": token_json_path}
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()
        tools = await self.session.list_tools()
        return [tool.name for tool in tools.tools]

    def convert_mcp_tools_to_gemini(self, mcp_tools: List) -> List[Dict]:
        gemini_tools = []
        for tool in mcp_tools:
            function_declaration = {
                "name": tool.name,
                "description": tool.description,
                "parameters": {"type": "object", "properties": {}, "required": []}
            }
            if hasattr(tool, 'inputSchema') and tool.inputSchema:
                schema = clean_schema_for_gemini(tool.inputSchema)
                if "properties" in schema:
                    cleaned_props = {}
                    for prop_name, prop_schema in schema["properties"].items():
                        cleaned_prop = {}
                        if isinstance(prop_schema, dict):
                            if "type" in prop_schema:
                                cleaned_prop["type"] = prop_schema["type"]
                            if "description" in prop_schema:
                                cleaned_prop["description"] = prop_schema["description"]
                            if "enum" in prop_schema:
                                cleaned_prop["enum"] = prop_schema["enum"]
                            if prop_schema.get("type") == "array":
                                cleaned_prop["items"] = prop_schema.get("items", {"type": "string"})
                        cleaned_props[prop_name] = cleaned_prop
                    function_declaration["parameters"]["properties"] = cleaned_props
                if "required" in schema:
                    function_declaration["parameters"]["required"] = schema["required"]
            gemini_tools.append({"function_declarations": [function_declaration]})
        return gemini_tools

    async def execute_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        try:
            result = await self.session.call_tool(tool_name, arguments)
            if result.content:
                content_parts = []
                for content in result.content:
                    if hasattr(content, 'text'):
                        content_parts.append(content.text)
                    elif hasattr(content, 'data'):
                        content_parts.append(str(content.data))
                    else:
                        content_parts.append(str(content))
                return "\n".join(content_parts)
            return "Tool executed successfully but returned no content"
        except Exception as e:
            return f"Error executing tool {tool_name}: {str(e)}"

    async def process_query(self, query: str) -> str:
        available_tools = (await self.session.list_tools()).tools
        gemini_tools = self.convert_mcp_tools_to_gemini(available_tools)

        try:
            if gemini_tools:
                response = self.model.generate_content(
                    query,
                    tools=gemini_tools,
                    tool_config={'function_calling_config': {'mode': 'AUTO'}}
                )
            else:
                response = self.model.generate_content(query)

            if response.candidates and response.candidates[0].content.parts:
                parts = response.candidates[0].content.parts
                final_parts = []
                for part in parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        fc = part.function_call
                        args = dict(fc.args) if hasattr(fc, 'args') else {}
                        tool_result = await self.execute_tool_call(fc.name, args)
                        follow_up = [
                            {"role": "user", "parts": [{"text": query}]},
                            {"role": "model", "parts": [{"function_call": fc}]},
                            {"role": "user", "parts": [{"function_response": {
                                "name": fc.name, "response": {"result": tool_result}
                            }}]}
                        ]
                        final = self.model.generate_content(follow_up)
                        if final.text:
                            final_parts.append(final.text)
                    elif hasattr(part, 'text') and part.text:
                        final_parts.append(part.text)
                return "\n".join(final_parts) if final_parts else "No response generated"
            return response.text if response.text else "No response generated"
        except Exception as e:
            return f"Error: {str(e)}"

    async def cleanup(self):
        await self.exit_stack.aclose()


# ========================
# GRADIO
# ========================
client = MCPClient()
loop = asyncio.get_event_loop()

async def init_client():
    tools = await client.connect_to_server()
    print(f"✅ Conectado. Herramientas disponibles: {tools}")
    return tools

async def chat_response(message, history):
    return await client.process_query(message)

def start_gradio():
    loop.run_until_complete(init_client())
    gr.ChatInterface(
        fn=lambda msg, hist: loop.run_until_complete(chat_response(msg, hist)),
        title="MCP + Gemini Chat (OAuth)",
        description="Interfaz con autenticación OAuth para Google Analytics",
    ).launch(server_name="0.0.0.0", server_port=7860)

if __name__ == "__main__":
    start_gradio()
