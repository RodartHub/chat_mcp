# main.py
import asyncio
import os
import gradio as gr
from connectors.ga4_connector import GA4Connector
from connectors.camphouse_connector import CamphouseConnector
from llm.gemini_llm import GeminiLLM


llm_client = GeminiLLM(connectors=[
    GA4Connector(),
    CamphouseConnector(),
    # Aquí podrías añadir más MCPs en el futuro
])

async def init_client():
    await llm_client.connect_to_servers()


async def run():
    async def handler(msg, hist):
        if not llm_client.tools_map:
            try:
                await init_client()
            except Exception as e:
                return f"⚠️ Error conectando a los MCP servers: {e}"

        return await llm_client.process_query(msg)

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
