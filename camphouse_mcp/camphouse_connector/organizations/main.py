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

@mcp.tool(title="Camphouse: Get all subsidiaries of an organization")
def get_subsidiaries_organization(organization_id: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Camphouse: Get all subsidiaries of a specific organization by its ID.
    Args:
        organization_id (str): The ID of the organization to retrieve subsidiaries for.
    Returns:
        Dict[str, List[Dict[str, Any]]]: A dictionary containing a list of dictionaries with the details of each subsidiary.
    """

    endpoint = f"organizations/{organization_id}/subsidiaries"
    return make_request(endpoint, method='GET')
           

