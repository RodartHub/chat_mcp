# llm/base.py
from abc import ABC, abstractmethod
from typing import Any, Callable, List, Dict

class LLMClient(ABC):
    """Estrategia de LLM intercambiable (Gemini, Claude, GPT, etc.)."""

    @abstractmethod
    async def generate_with_tools(
        self,
        query: str,
        tools: List[Dict[str, Any]],
        tool_caller: Callable[[str, Dict[str, Any]], Any],
    ) -> str:
        """Genera respuesta usando function calling. tool_caller ejecuta la tool y devuelve el resultado."""
        raise NotImplementedError
