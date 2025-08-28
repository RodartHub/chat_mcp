import os
from mcp.server.fastmcp import FastMCP

CAMPHOUSE_COMPANY_MAIN_ID = os.getenv("CAMPHOUSE_COMPANY_MAIN_ID", None)
print("CAMPHOUSE_COMPANY_MAIN_ID:", CAMPHOUSE_COMPANY_MAIN_ID)

mcp = FastMCP(
    name="Camphouse MCP",
    description="MCP for Camphouse",
    version="0.1.0",
    instructions="You are a helpful assistant that helps users to interact with the Camphouse API. Use the tools below to answer user questions. Always show names and IDs in the responses you get from the API if applicable.",
    
)

