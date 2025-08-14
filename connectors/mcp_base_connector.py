# connectors/mcp_base_connector.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List
from llm.base import LLMClient
from llm.gemini_llm import GeminiLLM
from tools.tool_converter import mcp_to_gemini

class MCPBaseConnector(ABC):
    """Base para conectores MCP. Implementa process_query + LLM Strategy.

    Los hijos SOLO implementan la conexión MCP:
      - connect_to_server()
      - list_tools()
      - execute(tool_name, args)
    """

    def __init__(self, name: str, llm: LLMClient | None = None):
        self.name = name
        self.session = None
        self.llm: LLMClient = llm or GeminiLLM()  # Default: Gemini. Se puede inyectar otro.

    # ---- Métodos abstractos (cada conector los implementa) ----
    @abstractmethod
    async def connect_to_server(self) -> Any:
        ...

    @abstractmethod
    async def list_tools(self) -> List[Any]:
        ...

    @abstractmethod
    async def execute(self, tool_name: str, args: Dict[str, Any]) -> Any:
        ...

    # ---- Común: orquesta LLM + Tools (function calling) ----
    async def process_query(self, query: str) -> str:
        available_tools = await self.list_tools()
        gemini_tools = mcp_to_gemini(available_tools) if available_tools else []

        async def _call_tool(tool_name: str, args: Dict[str, Any]) -> str:
            result = await self.execute(tool_name, args)
            return self._stringify_tool_result(result)

        return await self.llm.generate_with_tools(query, gemini_tools, _call_tool)

    # ---- Helpers ----
    def _stringify_tool_result(self, result: Any) -> str:
        """Convierte la respuesta de MCP a texto (como hacías antes)."""
        # Respuesta típica de MCP: tiene .content con Partes de texto/data
        try:
            content = getattr(result, "content", None)
            if content:
                out: List[str] = []
                for c in content:
                    if hasattr(c, "text") and c.text:
                        out.append(c.text)
                    elif hasattr(c, "data"):
                        out.append(str(c.data))
                    else:
                        out.append(str(c))
                return "\n".join(out) if out else "Tool executed successfully but returned no content"
        except Exception:
            pass

        # Si ya es str o lista simple
        if isinstance(result, (list, tuple)):
            return "\n".join(str(x) for x in result)
        return str(result)
