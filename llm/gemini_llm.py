# llm/gemini_llm.py
import os
from typing import Any, Callable, Dict, List
import google.generativeai as genai
from llm.base import LLMClient

class GeminiLLM(LLMClient):
    def __init__(self, model_name: str | None = None, api_key: str | None = None):
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("❌ GEMINI_API_KEY no configurado")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name or os.getenv("GEMINI_MODEL", "gemini-1.5-turbo"))

    async def generate_with_tools(
        self,
        query: str,
        tools: List[Dict[str, Any]],
        tool_caller: Callable[[str, Dict[str, Any]], Any],
    ) -> str:
        # 1) Primer turno: pedir a Gemini (AUTO function calling)
        response = self.model.generate_content(
            query,
            tools=tools if tools else None,
            tool_config={'function_calling_config': {'mode': 'AUTO'}} if tools else None,
        )

        # Si no hay candidates, devolvemos lo que haya
        if not getattr(response, "candidates", None):
            return getattr(response, "text", "No response generated")

        parts = response.candidates[0].content.parts
        final_chunks: List[str] = []

        # 2) Procesar parts (function_call o texto)
        for part in parts:
            fc = getattr(part, "function_call", None)
            if fc:
                # Ejecutar tool
                args = dict(getattr(fc, "args", {}) or {})
                tool_output = await tool_caller(fc.name, args)

                # Estructura de follow-up al estilo Gemini
                follow_up = [
                    {"role": "user", "parts": [{"text": query}]},
                    {"role": "model", "parts": [{"function_call": fc}]},
                    {"role": "user", "parts": [{
                        "function_response": {
                            "name": fc.name,
                            "response": {"output": tool_output}
                        }
                    }]}
                ]
                follow_response = self.model.generate_content(follow_up)
                if getattr(follow_response, "text", None):
                    final_chunks.append(follow_response.text)
            else:
                if getattr(part, "text", None):
                    final_chunks.append(part.text)

        # 3) Si no hubo parts, usar response.text
        if not final_chunks:
            return getattr(response, "text", "No response generated")

        return "\n".join(final_chunks)
