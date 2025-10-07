import sys
from pathlib import Path

# Ensure package imports work by adding src to sys.path
ROOT = Path(__file__).parent.resolve()
SRC = str(ROOT / "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

# Import the package and expose `app` for MCP to load
from mcp.server import FastMCP
from github_repo_analyzer import server

# Create a fresh FastMCP instance
app = FastMCP("github-repo-analyzer-dev")

# Register handlers
app.list_tools_fn = server.list_tools
app.call_tool_fn = server.call_tool

if __name__ == "__main__":
    # Run standalone for quick testing
    from mcp.server.stdio import stdio_server
    server.app.run(*stdio_server())
