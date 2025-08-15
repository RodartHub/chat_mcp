# connectors/ga4_connector.py
import os
import json
import asyncio

from typing import Any, Callable, Dict, List
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
    