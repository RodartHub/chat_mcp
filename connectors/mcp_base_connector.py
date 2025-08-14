from .connector_interface import IConnector
from typing import List, Dict, Any, Optional
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPBaseConnector(IConnector):
    def __init__(self, name: str, command: str, env_vars: Dict[str, str]):
        self._name = name
        self.command = command
        self.env_vars = env_vars
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

    @property
    def name(self) -> str:
        return self._name

    async def connect(self) -> None:
        server_params = StdioServerParameters(command=self.command, args=[], env=self.env_vars)
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()

    async def list_tools(self) -> List[Any]:
        tools = await self.session.list_tools()
        return tools.tools

    async def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        result = await self.session.call_tool(tool_name, args)
        return result.content

    async def close(self) -> None:
        await self.exit_stack.aclose()
