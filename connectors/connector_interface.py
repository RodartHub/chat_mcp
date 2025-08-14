from typing import List, Dict, Any
from abc import ABC, abstractmethod

class IConnector(ABC):
    """Interface que define cómo interactuar con un conector MCP"""

    @abstractmethod
    async def connect(self) -> None:
        pass

    @abstractmethod
    async def list_tools(self) -> List[Any]:
        pass

    @abstractmethod
    async def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        pass

    @abstractmethod
    async def close(self) -> None:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass
