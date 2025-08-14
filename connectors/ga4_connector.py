# connectors/ga4_connector.py
import os
import json
from mcp import stdio_client, ClientSession, StdioServerParameters
from contextlib import AsyncExitStack
from .mcp_base_connector import MCPBaseConnector
from tools.tool_converter import mcp_to_gemini
import google.generativeai as genai

class GA4Connector(MCPBaseConnector):
    def __init__(self):
        super().__init__(name="GA4")
        self.exit_stack = AsyncExitStack()

        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise RuntimeError("❌ No se encontró GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(os.getenv('GEMINI_MODEL', 'gemini-1.5-turbo'))

    async def connect_to_server(self):
        creds_path = self._prepare_credentials()
        server_params = StdioServerParameters(
            command="google-analytics-mcp",
            args=[],
            env={"GOOGLE_APPLICATION_CREDENTIALS": creds_path}
        )
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()
        return await self.list_tools()

    async def list_tools(self):
        tools = await self.session.list_tools()
        return tools.tools

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
