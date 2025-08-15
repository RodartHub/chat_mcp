# llm/gemini_llm.py

import os
from typing import Any, Callable, Dict, List
import google.generativeai as genai
from llm.base import LLMClient
from tools.tool_converter import clean_schema_for_gemini

class GeminiLLM(LLMClient):
    def __init__(self, connectors: List[Any] = None):
        super().__init__(connectors)
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("❌ GEMINI_API_KEY no configurado")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-1.5-turbo"))

    def convert_mcp_tools_to_gemini(self, mcp_tools: List) -> List[Dict]:
        gemini_tools = []
        for tool in mcp_tools:
            function_declaration = {
                "name": tool.name,
                "description": tool.description,
                "parameters": {"type": "object", "properties": {}, "required": []}
            }
            if hasattr(tool, 'inputSchema') and tool.inputSchema:
                schema = clean_schema_for_gemini(tool.inputSchema)
                if "properties" in schema:
                    cleaned_props = {}
                    for prop_name, prop_schema in schema["properties"].items():
                        cleaned_prop = {}
                        if isinstance(prop_schema, dict):
                            if "type" in prop_schema:
                                cleaned_prop["type"] = prop_schema["type"]
                            if "description" in prop_schema:
                                cleaned_prop["description"] = prop_schema["description"]
                            if "enum" in prop_schema:
                                cleaned_prop["enum"] = prop_schema["enum"]
                            if prop_schema.get("type") == "array":
                                cleaned_prop["items"] = prop_schema.get("items", {"type": "string"})
                        cleaned_props[prop_name] = cleaned_prop
                    function_declaration["parameters"]["properties"] = cleaned_props
                if "required" in schema:
                    function_declaration["parameters"]["required"] = schema["required"]
            gemini_tools.append({"function_declarations": [function_declaration]})
        return gemini_tools

    async def process_query(self, query: str) -> str:
        """
        Procesa el query soportando múltiples MCPs.
        """
        # 1. Combinar herramientas de todos los MCPs
        all_gemini_tools = []
        tool_connector_map = {}

        for connector_name, tools in self.tools_map.items():
            gemini_tools = self.convert_mcp_tools_to_gemini(tools)
            all_gemini_tools.extend(gemini_tools)

            # Mapear nombre de función a conector
            for t in tools:
                tool_connector_map[t.name] = connector_name

        try:
            if all_gemini_tools:
                response = self.model.generate_content(
                    query,
                    tools=all_gemini_tools,
                    tool_config={'function_calling_config': {'mode': 'AUTO'}}
                )
            else:
                response = self.model.generate_content(query)

            if response.candidates and response.candidates[0].content.parts:
                parts = response.candidates[0].content.parts
                final_parts = []

                for part in parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        fc = part.function_call
                        args = dict(fc.args) if hasattr(fc, 'args') else {}

                        connector_name = tool_connector_map.get(fc.name)
                        if not connector_name:
                            final_parts.append(f"⚠️ No se encontró conector para la función {fc.name}")
                            continue

                        connector = next((c for c in self.connectors if c.name == connector_name), None)
                        if not connector:
                            final_parts.append(f"⚠️ No se encontró instancia del conector {connector_name}")
                            continue

                        tool_result = await connector.execute(fc.name, args)

                        follow_up = [
                            {"role": "user", "parts": [{"text": query}]},
                            {"role": "model", "parts": [{"function_call": fc}]},
                            {"role": "user", "parts": [{
                                "function_response": {
                                    "name": fc.name,
                                    "response": {"output": tool_result}
                                }
                            }]}
                        ]

                        final = self.model.generate_content(follow_up)
                        if final.text:
                            final_parts.append(final.text)

                    elif hasattr(part, 'text') and part.text:
                        final_parts.append(part.text)

                return "\n".join(final_parts) if final_parts else "No response generated"

            return response.text if response.text else "No response generated"

        except Exception as e:
            return f"Error: {str(e)}"

