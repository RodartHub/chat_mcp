from typing import Any, Dict, List
from camphouse_mcp.tools.requests import make_request
from ...coordinator import mcp


@mcp.tool(title="Camphouse: Get campaign details")
def get_campaign_details(campaign_id: str) -> Dict[str, Any]:
    """
    Camphouse: Get details of a specific campaign by its ID.
    Args:
        campaign_id (str): The ID of the campaign to retrieve.
    Returns:
        Dict[str, Any]: A dictionary containing the campaign's details.
    """

    endpoint = f"campaigns/{campaign_id}"
    return make_request(endpoint, method='GET')