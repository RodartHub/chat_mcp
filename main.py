import asyncio
import gradio as gr
from connectors.ga4_connector import GA4Connector
from services.mcp_manager import MCPManager
from services.chat_service import ChatService

async def run():
    manager = MCPManager()
    await manager.register(GA4Connector())

    chat_service = ChatService(manager)

    async def handler(msg, hist):
        return await chat_service.process_message(msg)

    gr.ChatInterface(fn=handler, title="Multi-MCP Chat").launch(server_name="0.0.0.0", server_port=8080)

if __name__ == "__main__":
    asyncio.run(run())
