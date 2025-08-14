# main.py
import asyncio
import os
import gradio as gr
from connectors.ga4_connector import GA4Connector
from services.mcp_manager import MCPManager

async def run():
    manager = MCPManager()

    ga4 = GA4Connector()
    await ga4.connect_to_server()
    await manager.register(ga4)

    async def handler(msg, hist):
        # Aquí podrías rutear a otros conectores según intención; de momento GA4:
        return await ga4.process_query(msg)

    gr.ChatInterface(
        fn=handler,
        title="Multi-MCP Chat",
        description="Interfaz para interactuar con LLM y múltiples MCP tools",
    ).launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", 8080)),
    )

if __name__ == "__main__":
    asyncio.run(run())
