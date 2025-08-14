import os
import google.generativeai as genai
from tools.tool_converter import mcp_to_gemini

class ChatService:
    def __init__(self, mcp_manager):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-1.5-turbo"))
        self.mcp_manager = mcp_manager

    async def process_message(self, query: str) -> str:
        all_tools = await self.mcp_manager.list_all_tools()
        gemini_tools = []
        for _, tools in all_tools.items():
            gemini_tools.extend(mcp_to_gemini(tools))

        if gemini_tools:
            response = self.model.generate_content(
                query,
                tools=gemini_tools,
                tool_config={'function_calling_config': {'mode': 'AUTO'}}
            )
        else:
            response = self.model.generate_content(query)

        return response.text or "No response generated"
