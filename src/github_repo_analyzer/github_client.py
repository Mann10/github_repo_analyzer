import os
from typing import Dict, List, Optional
from github import Github, Repository
from pathlib import Path
import base64
from dotenv import load_dotenv
load_dotenv()

class GitHubClient:
    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub client with optional token for higher rate limits."""
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.client = Github(self.token) if self.token else Github()
    
    def get_repo(self, repo_url: str) -> Repository:
        """Extract owner/repo from URL and get repository object."""
        if not repo_url:
            raise ValueError("Repository URL cannot be empty")
            
        # Clean up URL: remove .git extension and trailing slashes
        repo_url = repo_url.rstrip('/')
        if repo_url.endswith('.git'):
            repo_url = repo_url[:-4]
            
        # Parse URL: https://github.com/owner/repo
        parts = repo_url.split('/')
        
        # Ensure we have enough parts for owner/repo
        if len(parts) < 2:
            raise ValueError("Invalid repository URL format. Expected: https://github.com/owner/repo")
            
        owner, repo_name = parts[-2], parts[-1]
        if not owner or not repo_name:
            raise ValueError("Could not extract owner and repository name from URL")
            
        try:
            repo = self.client.get_repo(f"{owner}/{repo_name}")
            # Try to access a property to verify we have access
            _ = repo.name
            return repo
        except Exception as e:
            if "404" in str(e):
                raise ValueError(
                    f"Repository '{owner}/{repo_name}' not found. Please check that:\n"
                    "1. The repository exists\n"
                    "2. The repository is public\n"
                    "3. You have provided the correct URL in format: https://github.com/owner/repo"
                ) from e
            elif "403" in str(e):
                raise ValueError(
                    f"Access denied to repository '{owner}/{repo_name}'. Please check that:\n"
                    "1. You have set a valid GITHUB_TOKEN environment variable\n"
                    "2. Your token has access to this repository\n"
                    "3. You haven't exceeded GitHub's API rate limits"
                ) from e
            else:
                raise ValueError(f"Error accessing repository: {str(e)}") from e
    
    def get_repo_contents(self, repo: Repository, path: str = "") -> List[Dict]:
        """Get contents of a directory in the repo."""
        contents = repo.get_contents(path)
        if not isinstance(contents, list):
            contents = [contents]
        
        return [{
            "name": content.name,
            "path": content.path,
            "type": content.type,
            "size": content.size,
        } for content in contents]
    
    def get_file_content(self, repo: Repository, file_path: str) -> str:
        """Get decoded content of a specific file."""
        try:
            content = repo.get_contents(file_path)
            if content.encoding == "base64":
                return base64.b64decode(content.content).decode('utf-8')
            return content.decoded_content.decode('utf-8')
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def get_repo_tree(self, repo: Repository, max_depth: int = 3) -> Dict:
        """Get recursive tree structure of repository."""
        tree = repo.get_git_tree(repo.default_branch, recursive=True)
        
        structure = {}
        for item in tree.tree:
            if item.path.count('/') < max_depth:
                parts = item.path.split('/')
                current = structure
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                if len(parts) > 0:
                    if item.type == 'tree':  # If it's a directory
                        current[parts[-1]] = {}
                    else:  # If it's a file
                        current[parts[-1]] = {'type': item.type}
        
        return structure
    
    def get_languages(self, repo: Repository) -> Dict[str, int]:
        """Get programming languages used in the repo."""
        return repo.get_languages()
    
    def get_readme(self, repo: Repository) -> Optional[str]:
        """Get README content."""
        try:
            readme = repo.get_readme()
            return readme.decoded_content.decode('utf-8')
        except:
            return None