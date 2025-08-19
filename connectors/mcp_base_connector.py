# connectors/mcp_base_connector.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List
from mcp import ClientSession
from llm.base import LLMClient
from contextlib import AsyncExitStack
from llm.gemini_llm import GeminiLLM
from typing import Optional, List, Dict, Any
from tools.tool_converter import clean_schema_for_gemini

class MCPBaseConnector(ABC):
    """Base para conectores MCP. Implementa process_query + LLM Strategy.

    Los hijos SOLO implementan la conexión MCP:
      - connect_to_server()
      - list_tools()
      - execute(tool_name, args)
    """

    def __init__(self, name: str, cached_tools: Optional[List[Any]] = None):
        self.cached_tools = cached_tools or []
        self.name = name
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()


    # ---- Métodos abstractos (cada conector los implementa) ----
    @abstractmethod
    async def connect_to_server(self) -> Any:
        ...

    async def list_tools(self) -> List[Any]:
        """Devuelve las herramientas disponibles en el MCP."""
        return self.cached_tools

    async def execute(self, tool_name: str, args: Dict[str, Any]) -> Any:
        if not self.session:
            raise RuntimeError("No hay sesión activa.")
        return await self.session.call_tool(tool_name, args)

    # ---- Común: orquesta LLM + Tools (function calling) ----
