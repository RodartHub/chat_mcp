from typing import Dict
from connectors.connector_interface import IConnector

class MCPManager:
    def __init__(self):
        self._connectors: Dict[str, IConnector] = {}

    async def register(self, connector: IConnector) -> None:
        await connector.connect()
        self._connectors[connector.name] = connector

    async def list_all_tools(self) -> Dict[str, list]:
        return {name: await conn.list_tools() for name, conn in self._connectors.items()}

    async def execute(self, connector_name: str, tool_name: str, args: dict):
        return await self._connectors[connector_name].execute_tool(tool_name, args)

    async def close_all(self) -> None:
        for conn in self._connectors.values():
            await conn.close()
