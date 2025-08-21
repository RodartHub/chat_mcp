from typing import Any, Dict, List

from ...coordinator import mcp

@mcp.tool(title="Get organization details")
def get_organization() -> List[Dict[str, Any]]:
    """Returns the organization details."""
    return mcp.get_organization()