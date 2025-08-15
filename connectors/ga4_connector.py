# connectors/ga4_connector.py
import os
import json
import asyncio

from mcp import stdio_client, ClientSession, StdioServerParameters
from .mcp_base_connector import MCPBaseConnector
from tools.tool_converter import clean_schema_for_gemini

class GA4Connector(MCPBaseConnector):
    def __init__(self):
        super().__init__(name="GA4")
        
    async def connect_to_server(self):
        creds_path = self._prepare_credentials()
        server_params = StdioServerParameters(
            command="google-analytics-mcp",
            args=[],
            env={"GOOGLE_APPLICATION_CREDENTIALS": creds_path}
        )
        self.stdio, self.write = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()
    
        # Cache tools una sola vez
        self.cached_tools = (await self.session.list_tools()).tools
        print(f"✅ Conectado. Herramientas disponibles: {[tool.name for tool in self.cached_tools]}")
        return self.cached_tools
    
    async def list_tools(self):
        return getattr(self, "cached_tools", [])

    async def execute(self, tool_name, args):
        return await self.session.call_tool(tool_name, args)

    def _prepare_credentials(self):
        creds_var = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not creds_var:
            raise RuntimeError("No se encontró la variable GOOGLE_APPLICATION_CREDENTIALS.")
        if os.path.isfile(creds_var):
            return creds_var
        creds_json = json.loads(creds_var)
        temp_path = "/tmp/service_account.json"
        with open(temp_path, "w") as tmp:
            json.dump(creds_json, tmp)
        return temp_path
    
    async def process_query(self, query: str) -> str:
        available_tools = (await self.session.list_tools()).tools
        gemini_tools = self.llm.convert_mcp_tools_to_gemini(available_tools)
        
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

                        # Buscar el schema original de la herramienta
                        tool_schema = None
                        for t in available_tools:
                            if t.name == fc.name and hasattr(t, 'inputSchema'):
                                tool_schema = clean_schema_for_gemini(t.inputSchema)
                                break

                        # Determinar la key de salida correcta
                        if tool_schema and "properties" in tool_schema and tool_schema["properties"]:
                            first_key = list(tool_schema["properties"].keys())[0]
                            response_payload = {first_key: tool_result}
                        else:
                            response_payload = {"output": tool_result}

                        follow_up = [
                            {"role": "user", "parts": [{"text": query}]},
                            {"role": "model", "parts": [{"function_call": fc}]},
                            {"role": "user", "parts": [{"function_response": {
                                "name": fc.name,
                                "response": response_payload
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
