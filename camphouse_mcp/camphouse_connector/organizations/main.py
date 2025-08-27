import json
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


@mcp.tool(title="Camphouse: Get all partners of an organization")
def get_list_partners_organization(organization_id: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Camphouse: Get all partners of a specific organization by its ID.
    Args:
        organization_id (str): The ID of the organization to retrieve partners for.
    Returns:
        Dict[str, List[Dict[str, Any]]]: A dictionary containing a list of dictionaries with the details of each partner.
    """

    endpoint = f"organizations/{organization_id}/partners"
    return make_request(endpoint, method='GET')


@mcp.tool(title="Camphouse: Get all campaigns of an organization")
def get_organization_campaigns(organization_id: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Camphouse: Get all campaigns of a specific organization by its ID.
    Args:
        organization_id (str): The ID of the organization to retrieve campaigns for.
    Returns:
        Dict[str, List[Dict[str, Any]]]: A dictionary containing a list of dictionaries with the details of each campaign.
    """

    endpoint = f"organizations/{organization_id}/campaigns"
    return make_request(endpoint, method='GET')

@mcp.tool(title="Camphouse: Get all media types of an organization")
def get_organization_mediatypes(organization_id: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Camphouse: Get all media types of a specific organization by its ID.
    Media types are the different mediums in which advertisement is made such as TV, Radio, SEM, Online Video. Organizations create their own media types and can have as many as they like. Media entries must always be connected to a media type.
    Args:
        organization_id (str): The ID of the organization to retrieve media types for.
    Returns:
        Dict[str, List[Dict[str, Any]]]: A dictionary containing a list of dictionaries with the details of each media type.
    """

    endpoint = f"organizations/{organization_id}/media_types"
    return make_request(endpoint, method='GET')

@mcp.tool(title="Camphouse: Get all vehicles of an organization")
def get_organization_vehicles(organization_id: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Camphouse: Get all vehicles of a specific organization by its ID.
    Vehicles are the different channels that advertisement are made throuhg. For TV they can be Fox News, BBC etc. Each vehicle must be connected to an organization and a media type. Each media entry must be connected to a vehicle.
    Args:
        organization_id (str): The ID of the organization to retrieve vehicles for.
    Returns:
        Dict[str, List[Dict[str, Any]]]: A dictionary containing a list of dictionaries with the details of each vehicle.
    """

    endpoint = f"organizations/{organization_id}/vehicles"
    return make_request(endpoint, method='GET')


@mcp.tool(title="Camphouse: Get all data fields of an organization")
def get_data_fields_for_organization(organization_id: str) -> Dict:
    """
    Camphouse: Get all data fields associated with a specific organization by its ID.
    Args:
        organization_id (str): The ID of the organization to retrieve data fields for.
    Returns:
        Dict[str, List[Dict[str, Any]]]: A dictionary containing a list of dictionaries with the details of each data field.
    """
    payload = {
        "q": json.dumps({"organizationId": str(organization_id)})
    }

    return make_request("fields", payload=payload, method='GET')
