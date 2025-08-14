import os
import google.generativeai as genai
from tools.tool_converter import mcp_to_gemini

class ChatService:
    def __init__(self, mcp_manager):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-1.5-turbo"))
        self.mcp_manager = mcp_manager

    async def process_message(self, query: str) -> str:
        # 1️⃣ Obtener todos los tools de todos los MCPs
        all_tools = await self.mcp_manager.list_all_tools()
        gemini_tools = []
        tool_index = {}  # mapa {tool_name: connector_name}

        for connector_name, tools in all_tools.items():
            for t in tools:
                gemini_tools.extend(mcp_to_gemini([t]))
                tool_index[t.name] = connector_name

        # 2️⃣ Preguntar a Gemini
        response = self.model.generate_content(
            query,
            tools=gemini_tools,
            tool_config={'function_calling_config': {'mode': 'AUTO'}}
        )

        final_parts = []

        if not hasattr(response, "candidates") or not response.candidates:
            return "No response generated"

        parts = response.candidates[0].content.parts

        for part in parts:
            # 3️⃣ Si Gemini quiere llamar a un tool
            if hasattr(part, "function_call") and part.function_call:
                fc = part.function_call
                connector_name = tool_index.get(fc.name)
                if not connector_name:
                    final_parts.append(f"⚠️ Tool {fc.name} no encontrado")
                    continue

                # 4️⃣ Ejecutar el tool en el conector correcto
                args = dict(fc.args) if hasattr(fc, "args") else {}
                tool_result = await self.mcp_manager.execute(connector_name, fc.name, args)

                # Convertir resultado a texto
                if isinstance(tool_result, list):
                    tool_text = "\n".join(
                        getattr(item, "text", str(item)) for item in tool_result
                    )
                else:
                    tool_text = str(tool_result)

                # 5️⃣ Seguir conversación con Gemini
                follow_up = [
                    {"role": "user", "parts": [{"text": query}]},
                    {"role": "model", "parts": [{"function_call": fc}]},
                    {"role": "user", "parts": [{
                        "function_response": {
                            "name": fc.name,
                            "response": {"output": tool_text}
                        }
                    }]}
                ]

                follow_response = self.model.generate_content(follow_up)
                if follow_response.text:
                    final_parts.append(follow_response.text)

            elif hasattr(part, "text") and part.text:
                final_parts.append(part.text)

        return "\n".join(final_parts) if final_parts else "No response generated"
