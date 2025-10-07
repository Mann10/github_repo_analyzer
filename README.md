# GitHub Repository Analyzer

A powerful tool for analyzing GitHub repositories through a Model Context Protocol (MCP) interface. Provides detailed insights about repository structure, code organization, and architecture.

## Features

- Repository Overview Analysis
- Architecture Analysis
- Code Structure Analysis
- File Content Retrieval

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Mann10/github_repo_analyzer.git
cd github_repo_analyzer
```

2. Create a virtual environment and activate it:
```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On Unix/MacOS
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up GitHub token (optional but recommended):
Create a `.env` file in the root directory and add your GitHub token:
```
GITHUB_TOKEN=your_github_token_here
```

## Usage

### Running as MCP Server

```bash
mcp dev src/github_repo_analyzer/server.py
```

### Integration with Claude

1. Make sure the server is running
2. In your Claude conversation, you can use tools like:
   - analyze_repo_overview
   - get_architecture_diagram
   - analyze_code_structure
   - get_file_contents

Example:
```json
{
    "tool": "analyze_repo_overview",
    "args": {
        "repo_url": "https://github.com/owner/repo"
    }
}
```

## Available Tools

1. **analyze_repo_overview**
   - High-level repository analysis
   - Project description and purpose
   - Technology stack and languages
   - Repository statistics

2. **get_architecture_diagram**
   - Project architecture analysis
   - Component relationships
   - Entry points and configuration
   - Dependency management

3. **analyze_code_structure**
   - Code organization patterns
   - File types and naming conventions
   - Testing setup and frameworks
   - Code quality indicators

4. **get_file_contents**
   - Retrieve specific file contents
   - Supports any file in the repository

## License

MIT License

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
