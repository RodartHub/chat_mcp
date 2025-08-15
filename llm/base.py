# llm/base.py
from abc import ABC, abstractmethod
from typing import Any, Callable, List, Dict

class LLMClient(ABC):
    """Estrategia de LLM intercambiable (Gemini, Claude, GPT, etc.)."""

    def __init__(self, connectors: List[Any] = None):
        """Inicializa el cliente LLM con conectores opcionales."""
        self.connectors = connectors or []
        self.sessions = {}  # clave: nombre conector, valor: sesión o client
        self.tools_map = {} # clave: nombre conector, valor: lista de tools

    @abstractmethod
    async def generate_with_tools(
        self,
        query: str,
        tools: List[Dict[str, Any]],
        tool_caller: Callable[[str, Dict[str, Any]], Any],
    ) -> str:
        """Genera respuesta usando function calling."""
        raise NotImplementedError

    # @abstractmethod
    # async def process_query(self, query: str) -> str:
    #     """Procesa un query y devuelve la respuesta generada."""
    #     raise NotImplementedError

    async def connect_to_servers(self):
        """Inicializa todos los MCPs y almacena sus tools."""
        for connector in self.connectors:
            try:
                session = await connector.connect_to_server()
                self.sessions[connector.name] = session

                tools = await connector.list_tools()
                self.tools_map[connector.name] = tools
            except Exception as e:
                print(f"⚠️ Error inicializando conector {connector.name}: {e}")

        return self.tools_map