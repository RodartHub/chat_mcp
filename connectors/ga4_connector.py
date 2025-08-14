import os
import json
from .mcp_base_connector import MCPBaseConnector

class GA4Connector(MCPBaseConnector):
    def __init__(self):
        creds_path = self._prepare_credentials()
        super().__init__(name="GA4", command="google-analytics-mcp",
                         env_vars={"GOOGLE_APPLICATION_CREDENTIALS": creds_path})

    def _prepare_credentials(self) -> str:
        creds_var = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not creds_var:
            raise RuntimeError("No se encontró la variable GOOGLE_APPLICATION_CREDENTIALS.")
        if os.path.isfile(creds_var):
            return creds_var
        creds_json = json.loads(creds_var)
        temp_path = "/tmp/service_account.json"
        with open(temp_path, "w") as tmp:
            json.dump(creds_json, tmp)
        return temp_path
