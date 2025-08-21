# connectors/ga4_connector.py
import os
import json
import asyncio

from typing import Any, Callable, Dict, List
from mcp import stdio_client, ClientSession, StdioServerParameters
from .mcp_base_connector import MCPBaseConnector
from tools.tool_converter import clean_schema_for_gemini

class CamphouseConnector(MCPBaseConnector):
    def __init__(self):
        super().__init__(name="Camphouse", cached_tools=None)

    async def connect_to_server(self):
        creds_path = self._prepare_credentials()
        server_params = StdioServerParameters(
            command="python",   
            args=["-m", "camphouse_mcp.server"],  
            env={"CAMPHOUSE_TOKEN_ID": creds_path}
        )
        self.stdio, self.write = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()

        # Cache tools una sola vez
        self.cached_tools = (await self.session.list_tools()).tools
        print(f"✅ Conectado. Herramientas disponibles: {[tool.name for tool in self.cached_tools]}")
        return self.cached_tools
    
    def _prepare_credentials(self):
        creds_var = os.getenv("CAMPHOUSE_TOKEN_ID")
        if not creds_var:
            raise RuntimeError("No se encontró la variable CAMPHOUSE_TOKEN_ID.")
        return creds_var