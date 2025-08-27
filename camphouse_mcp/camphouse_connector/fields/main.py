from typing import Any, Dict, List
from camphouse_mcp.tools.requests import make_request
from ...coordinator import mcp


@mcp.tool(title="Camphouse:  List standard fields")
def get_standard_fields() -> Dict[str, List[Dict[str, Any]]]:
    """
    Camphouse: List all standard fields available in the system.
    Returns:
        Dict[str, List[Dict[str, Any]]]: A dictionary containing a list of dictionaries with the details of each standard field.
    """

    return make_request("standardfields", method='GET')

@mcp.tool(title="Camphouse:  Get data field")
def get_data_field(field_id: str) -> Dict[str, Any]:
    """
    Camphouse: Get details of a specific data field by its ID.
    Args:
        field_id (str): The ID of the data field to retrieve.
    Returns:
        Dict[str, Any]: A dictionary containing the details of the requested data field.
    """

    return make_request(f"/fields/{field_id}", method='GET')