from typing import Any, Dict, List
from camphouse_mcp.tools.requests import make_request
from ...coordinator import mcp

@mcp.tool(title="Camphouse: Get media types details")
def get_mediatypes_data(mediatype_ids: List[str]) -> List[Dict[str, Any]]:
    """
    Camphouse: Get details of multiple media types by their IDs.
    Args:
        mediatype_ids (List[str]): A list of media type IDs to retrieve.
    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing the details of each requested media type.
    """
    mediatypes = []
    for mt_id in mediatype_ids:
        mt_details = make_request(f"mediatypes/{mt_id}", method='GET')
        mediatypes.append(mt_details.get('mediaType', {}))
    return mediatypes