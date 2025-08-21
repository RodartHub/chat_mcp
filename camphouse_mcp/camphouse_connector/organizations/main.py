from typing import Any, Dict, List
from camphouse_mcp.tools.requests import make_request
from ...coordinator import mcp

@mcp.tool(title="Camphouse: Get organization details")
def get_organization(organization_id: str) -> Dict[str, Any]:
    """
    Camphouse: Get details of a specific organization by its ID.
    Args:
        organization_id (str): The ID of the organization to retrieve.
    Returns:
        Dict[str, Any]: A dictionary containing the organizations details.
    """

    endpoint = f"organizations/{organization_id}"
    return make_request(endpoint, method='GET')
           

