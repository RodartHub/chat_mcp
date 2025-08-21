
from .coordinator import mcp

def run_server() -> None:
    """Runs the server.

    Serves as the entrypoint for the 'runmcp' command.
    """
    mcp.run()


if __name__ == "__main__":
    run_server()
