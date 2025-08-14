# services/mcp_manager.py
class MCPManager:
    def __init__(self):
        self._connectors = {}

    async def register(self, connector):
        self._connectors[connector.name] = connector

    def get(self, name: str):
        return self._connectors.get(name)

    def all(self):
        return self._connectors.values()
