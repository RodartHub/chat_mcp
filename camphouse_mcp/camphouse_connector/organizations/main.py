import os
import json
from typing import Any, Dict, List
from camphouse_mcp.tools.requests import make_request
from ...coordinator import mcp

CAMPHOUSE_COMPANY_MAIN_ID = os.getenv("CAMPHOUSE_COMPANY_MAIN_ID", None)

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
def get_subsidiaries_organization() -> Dict[str, List[Dict[str, Any]]]:
    """
    Camphouse: Get all subsidiaries of the main organization associated with the provided token.
    Returns:
        Dict[str, List[Dict[str, Any]]]: A dictionary containing a list of dictionaries with the details of each subsidiary.
    """
    endpoint = f"organizations/{CAMPHOUSE_COMPANY_MAIN_ID}/subsidiaries"
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

@mcp.tool(title="Camphouse: Get all media entries for an organization")
def get_media_entries_for_organization(organization_id: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Camphouse: Get all media entries associated with a specific organization by its ID.
    Args:
        organization_id (str): The ID of the organization to retrieve media entries for.
    Returns:
        Dict[str, List[Dict[str, Any]]]: A dictionary containing a list of dictionaries with the details of each media entry.
    """

    payload = {
        "q": json.dumps({"organizationId": str(organization_id)})
    }

    return make_request("searchmediaentries", payload=payload, method='GET')


@mcp.tool(title="Camphouse: Aggregate media entries for an organization")
def get_aggregate_media_entries(
    organization_id: str,
    media_type_id: str,
    from_date: str,
    to_date: str
) -> List[Dict]:
    """
    Camphouse: Get aggregated media entries for a specific organization by media type and date range.
    Args:
        organization_id (str): The ID of the organization to aggregate media entries for.
        media_type_id (str): The ID of the media type to filter by.
        from_date (str): The start date for the aggregation (YYYY-MM-DD).
        to_date (str): The end date for the aggregation (YYYY-MM-DD).
    Returns:
        List[Dict]: A list of dictionaries containing the aggregated media entry data.
    """

    payload = {
        "query": {
            "organizationId": [str(organization_id)],
            "dateRange": {
                "from": from_date,
                "to": to_date
            },
            "_mt_entry_type": [
                "planning",
                "result",
                "target"
            ],
            "mediaTypeId": [str(media_type_id)]
        },
        "aggregations": [
            {
                "measures": [
                    "spend",
                    "clicks",
                    "impressions",
                    "engagements",
                    "conversions"
                ],
                "dimensions": [
                    "campaign.name"
                ],
                "grain": "none",
                "limitOptions": {
                    "orderBy": "spend",
                    "order": "desc",
                    "size": 100,
                    "groupOthers": True
                }
            }
        ]
    }

    return make_request("aggregatemediaentries", payload=payload, method='POST')
