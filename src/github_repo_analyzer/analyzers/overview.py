from github import Repository
from typing import Dict, Any

class OverviewAnalyzer:
    """Analyzes repository from user perspective."""
    
    def analyze(self, repo: Repository, readme: str, languages: Dict[str, int]) -> Dict[str, Any]:
        """Generate comprehensive overview of the repository."""
        
        # Calculate primary language
        total_bytes = sum(languages.values())
        primary_lang = max(languages.items(), key=lambda x: x[1])[0] if languages else "Unknown"
        
        overview = {
            "name": repo.name,
            "full_name": repo.full_name,
            "description": repo.description or "No description provided",
            "url": repo.html_url,
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "open_issues": repo.open_issues_count,
            "primary_language": primary_lang,
            "languages": {
                lang: f"{(bytes/total_bytes)*100:.1f}%" 
                for lang, bytes in sorted(languages.items(), key=lambda x: x[1], reverse=True)
            } if total_bytes > 0 else {},
            "created_at": repo.created_at.isoformat(),
            "updated_at": repo.updated_at.isoformat(),
            "default_branch": repo.default_branch,
            "has_wiki": repo.has_wiki,
            "has_pages": repo.has_pages,
            "license": repo.license.name if repo.license else "No license",
            "topics": repo.get_topics(),
        }
        
        # Extract key information from README
        if readme:
            overview["readme_summary"] = self._summarize_readme(readme)
        
        return overview
    
    def _summarize_readme(self, readme: str) -> Dict[str, Any]:
        """Extract key sections from README."""
        lines = readme.split('')
        sections = {}
        current_section = "intro"
        current_content = []
        
        for line in lines[:100]:  # First 100 lines
            if line.startswith('#'):
                if current_content:
                    sections[current_section] = ''.join(current_content).strip()
                current_section = line.strip('# ').lower()
                current_content = []
            else:
                current_content.append(line)
        
        if current_content:
            sections[current_section] = ''.join(current_content).strip()
        
        return {
            "has_installation": any('install' in s for s in sections.keys()),
            "has_usage": any('usage' in s or 'getting started' in s for s in sections.keys()),
            "has_contributing": any('contribut' in s for s in sections.keys()),
            "sections_found": list(sections.keys())[:5],  # Top 5 sections
        }