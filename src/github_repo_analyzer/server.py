import asyncio
import os
from typing import Any
from mcp.server import FastMCP, Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from mcp.server.stdio import stdio_server

from github_repo_analyzer.github_client import GitHubClient
from github_repo_analyzer.analyzers.overview import OverviewAnalyzer
from github_repo_analyzer.analyzers.architecture import ArchitectureAnalyzer
from github_repo_analyzer.analyzers.code_structure import CodeStructureAnalyzer

class GitHubAnalyzerMCP(FastMCP):
    def __init__(self):
        super().__init__("github-repo-analyzer")
        self.github_client = None
        self.overview_analyzer = None
        self.architecture_analyzer = None
        self.code_analyzer = None
        
    def init_services(self):
        """Initialize services after FastMCP initialization."""
        if self.github_client is None:
            self.github_client = GitHubClient()
            self.overview_analyzer = OverviewAnalyzer()
            self.architecture_analyzer = ArchitectureAnalyzer()
            self.code_analyzer = CodeStructureAnalyzer()

    async def list_tools(self) -> list[Tool]:
        """List available tools."""
        return [
        Tool(
            name="analyze_repo_overview",
            description=(
                "Analyzes a GitHub repository from a user perspective.\n\n"
                "Provides high-level overview including:\n"
                "- Project description and purpose\n"
                "- Technology stack and languages\n"
                "- Repository statistics (stars, forks, issues)\n"
                "- README summary and key sections\n"
                "- License and topics\n"
                "- Usage and installation information\n\n"
                "Input: GitHub repository URL (e.g., https://github.com/owner/repo)"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_url": {"type": "string", "description": "Full GitHub repository URL"}
                },
                "required": ["repo_url"],
            },
        ),
        Tool(
            name="get_architecture_diagram",
            description=(
                "Analyzes repository architecture and structure (text-based).\n\n"
                "Provides architectural insights including:\n"
                "- Project type (web app, library, CLI, etc.)\n"
                "- Architectural pattern (MVC, microservices, etc.)\n"
                "- Major components and their relationships\n"
                "- Entry points and configuration files\n"
                "- Dependencies and package managers\n"
                "- Architectural layers\n\n"
                "Input: GitHub repository URL"
            ),
            inputSchema={"type": "object", "properties": {"repo_url": {"type": "string"}}, "required": ["repo_url"]},
        ),
        Tool(
            name="analyze_code_structure",
            description=(
                "Deep dive into code implementation and structure.\n\n"
                "Provides code-level analysis including:\n"
                "- Code organization patterns\n"
                "- File types and naming conventions\n"
                "- Key directories and their purposes\n"
                "- Testing setup and frameworks\n"
                "- Code quality indicators (CI/CD, linting, docs)\n"
                "- Important files to examine\n\n"
                "Input: GitHub repository URL"
            ),
            inputSchema={"type": "object", "properties": {"repo_url": {"type": "string"}}, "required": ["repo_url"]},
        ),
        Tool(
            name="get_file_contents",
            description=(
                "Retrieves the contents of a specific file from the repository.\n\n"
                "Useful for examining specific files identified in other analyses.\n\n"
                "Inputs:\n"
                "- repo_url: GitHub repository URL\n"
                "- file_path: Path to the file within the repository (e.g., 'src/main.py')"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_url": {"type": "string"},
                    "file_path": {"type": "string"},
                },
                "required": ["repo_url", "file_path"],
            },
        ),
    ]


    async def call_tool(self, name: str, arguments: Any) -> list[TextContent]:
        """Handle tool calls."""
        try:
            if name == "analyze_repo_overview":
                return await self.handle_overview_analysis(arguments["repo_url"])

            elif name == "get_architecture_diagram":
                return await self.handle_architecture_analysis(arguments["repo_url"])

            elif name == "analyze_code_structure":
                return await self.handle_code_analysis(arguments["repo_url"])

            elif name == "get_file_contents":
                return await self.handle_file_contents(arguments["repo_url"], arguments["file_path"])

            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}" )]

        except Exception as e:
            return [TextContent(type="text", text=f"Error executing {name}: {e}\nPlease check the repository URL and try again.")]


    async def handle_overview_analysis(self, repo_url: str) -> list[TextContent]:
        """Handle repository overview analysis."""
        self.init_services()
        repo = self.github_client.get_repo(repo_url)

        # Get necessary data
        languages = self.github_client.get_languages(repo)
        readme = self.github_client.get_readme(repo)

        # Analyze
        overview = self.overview_analyzer.analyze(repo, readme, languages)

        # Build response
        response = f"# Repository Overview: {overview.get('name', repo.name if hasattr(repo, 'name') else repo_url)}\n\n"
        response += "## Basic Information\n"
        response += f"- **Full Name**: {overview.get('full_name', '')}\n"
        response += f"- **Description**: {overview.get('description', '')}\n"
        response += f"- **URL**: {overview.get('url', repo_url)}\n"
        response += f"- **Primary Language**: {overview.get('primary_language', '')}\n"
        response += f"- **License**: {overview.get('license', '')}\n\n"
        response += "## Statistics\n"
        response += f"- ⭐ Stars: {overview.get('stars', 0)}\n"
        response += f"- 🍴 Forks: {overview.get('forks', 0)}\n"
        response += f"- 🐛 Open Issues: {overview.get('open_issues', 0)}\n\n"

        response += "## Languages Used\n"
        for lang, percentage in overview.get('languages', {}).items():
            response += f"- {lang}: {percentage}\n"

        response += "\n## Project Details\n"
        response += f"- Created: {overview.get('created_at', '')[:10]}\n"
        response += f"- Last Updated: {overview.get('updated_at', '')[:10]}\n"
        response += f"- Default Branch: {overview.get('default_branch', '')}\n"
        response += f"- Has Wiki: {'Yes' if overview.get('has_wiki') else 'No'}\n"
        response += f"- Has Pages: {'Yes' if overview.get('has_pages') else 'No'}\n"

        if overview.get('topics'):
            response += "\n## Topics\n"
            response += ", ".join(overview['topics']) + "\n"

        if readme and overview.get('readme_summary'):
            summary = overview['readme_summary']
            response += "\n## README Analysis\n"
            response += f"- Has Installation Guide: {'Yes' if summary.get('has_installation') else 'No'}\n"
            response += f"- Has Usage Instructions: {'Yes' if summary.get('has_usage') else 'No'}\n"
            response += f"- Has Contributing Guidelines: {'Yes' if summary.get('has_contributing') else 'No'}\n"
            response += f"- Key Sections: {', '.join(summary.get('sections_found', []))}\n"

        return [TextContent(type="text", text=response)]


    async def handle_architecture_analysis(self, repo_url: str) -> list[TextContent]:
        """Handle architecture analysis."""
        self.init_services()
        repo = self.github_client.get_repo(repo_url)
        tree_structure = self.github_client.get_repo_tree(repo, max_depth=4)
        languages = self.github_client.get_languages(repo)

        # Analyze architecture
        architecture = self.architecture_analyzer.analyze(repo, tree_structure, languages)

        # Build response
        response = f"# Architecture Analysis: {getattr(repo, 'name', repo_url)}\n\n"
        response += f"## Project Type\n**{architecture.get('project_type','').replace('_',' ').title()}**\n\n"
        response += f"## Architectural Pattern\n**{architecture.get('structure_pattern','')}**\n\n"
        response += "## Major Components\n"

        for component in architecture.get('components', []):
            response += f"\n### {component.get('name','component')}\n"
            response += f"- Files: {component.get('file_count', 0)}\n"
            response += "- Key Paths:\n"
            for path in component.get('paths', [])[:3]:
                response += f"  - `{path}`\n"

        response += "\n## Entry Points\n"
        for entry in architecture.get('entry_points', [])[:5]:
            response += f"- `{entry}`\n"

        response += "\n## Configuration Files\n"
        for config in architecture.get('configuration_files', [])[:8]:
            response += f"- `{config}`\n"

        deps = architecture.get('dependencies', {})
        if deps.get('package_managers'):
            response += "\n## Dependencies\n"
            response += f"Package Managers: {', '.join(deps.get('package_managers', []))}\n"
            response += "Dependency Files:\n"
            for dep_file in deps.get('dependency_files', []):
                response += f"- `{dep_file}`\n"

        if architecture.get('layers'):
            response += "\n## Architectural Layers\n"
            for layer in architecture.get('layers', []):
                response += f"- {layer}\n"

        return [TextContent(type="text", text=response)]


    async def handle_code_analysis(self, repo_url: str) -> list[TextContent]:
        """Handle code structure analysis."""
        self.init_services()
        repo = self.github_client.get_repo(repo_url)
        tree_structure = self.github_client.get_repo_tree(repo, max_depth=4)
        analysis = self.code_analyzer.analyze(repo, tree_structure, self.github_client)

        org = analysis.get('code_organization', {})
        response = f"# Code Structure Analysis: {getattr(repo,'name',repo_url)}\n\n"
        response += f"## Code Organization\n- Total Files: {org.get('total_files',0)}\n"
        response += f"- Directory Depth: {org.get('directory_depth',0)} levels\n"
        response += f"- Average Files per Directory: {org.get('avg_files_per_directory',0.0):.1f}\n"
        response += f"- Has `src/` directory: {'Yes' if org.get('has_src_directory') else 'No'}\n"
        response += f"- Has `lib/` directory: {'Yes' if org.get('has_lib_directory') else 'No'}\n"
        response += f"- Has tests directory: {'Yes' if org.get('has_tests_directory') else 'No'}\n\n"
        response += "## File Types Distribution\n"
        for ext, count in analysis.get('file_types', {}).items():
            response += f"- `.{ext}`: {count} files\n"

        naming = analysis.get('naming_conventions', {})
        response += f"\n## Naming Conventions\n- Dominant Style: **{naming.get('dominant_convention','')}**\n"
        response += f"- Breakdown: {', '.join(f'{k}: {v}' for k,v in naming.get('conventions_used',{}).items())}\n\n"

        response += "## Key Directories\n"
        for dir_info in analysis.get('key_directories', []):
            response += f"- `{dir_info.get('name','')}/` - {dir_info.get('file_count',0)} files\n"

        testing = analysis.get('test_coverage_indicators', {})
        response += f"\n## Testing Setup\n- Has Tests: {'Yes' if testing.get('has_tests') else 'No'}\n"
        response += f"- Test Files: {testing.get('test_files_count',0)}\n"
        if testing.get('test_frameworks'):
            response += f"- Frameworks: {', '.join(testing.get('test_frameworks',[]))}\n"

        quality = analysis.get('code_quality_indicators', {})
        response += "\n## Code Quality Indicators\n"
        response += f"- CI/CD: {'✅' if quality.get('has_ci_cd') else '❌'}\n"
        response += f"- Linting: {'✅' if quality.get('has_linting') else '❌'}\n"
        response += f"- Code Formatting: {'✅' if quality.get('has_formatting') else '❌'}\n"
        response += f"- Documentation: {'✅' if quality.get('has_documentation') else '❌'}\n"
        response += f"- Contributing Guide: {'✅' if quality.get('has_contributing_guide') else '❌'}\n"
        response += f"- License File: {'✅' if quality.get('has_license') else '❌'}\n"

        if analysis.get('key_files'):
            response += "\n## Key Files to Examine\n"
            for file in analysis['key_files'][:8]:
                response += f"- `{file}`\n"

        return [TextContent(type="text", text=response)]


    async def handle_file_contents(self, repo_url: str, file_path: str) -> list[TextContent]:
        """Handle file contents retrieval."""
        self.init_services()
        repo = self.github_client.get_repo(repo_url)
        content = self.github_client.get_file_content(repo, file_path)

        # Normalize content to string
        if isinstance(content, (bytes, bytearray)):
            try:
                content = content.decode('utf-8')
            except Exception:
                content = content.decode('latin-1', errors='replace')

        if content is None:
            content = ""

        # Trim very large files
        max_len = 20000
        if len(content) > max_len:
            snippet = content[:max_len] + "\n\n... (truncated) ..."
        else:
            snippet = content

        response = f"# File: {file_path}\n\n```\n{snippet}\n```\n"
        return [TextContent(type="text", text=response)]

# Initialize server instance
app = GitHubAnalyzerMCP()

async def main():
    """Run the MCP server."""
    # Run server
    server = Server(app)
    await server.stdio()


if __name__ == "__main__":
    asyncio.run(main())
