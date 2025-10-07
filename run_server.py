import asyncio
from github_repo_analyzer.server import app
from mcp.server.stdio import stdio_server

async def run():
    async with stdio_server() as (r, w):
        await app.run(r, w, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(run())