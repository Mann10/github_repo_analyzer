from github import Repository
from typing import Dict, Any, List, Set
import re
from pathlib import Path

class ArchitectureAnalyzer:
    """Analyzes repository architecture and component relationships."""
    
    def analyze(self, repo: Repository, tree_structure: Dict, languages: Dict[str, int]) -> Dict[str, Any]:
        """Analyze architectural patterns and structure."""
        
        architecture = {
            "project_type": self._detect_project_type(tree_structure, languages),
            "structure_pattern": self._detect_structure_pattern(tree_structure),
            "components": self._identify_components(tree_structure),
            "entry_points": self._find_entry_points(tree_structure),
            "configuration_files": self._find_config_files(tree_structure),
            "dependencies": self._analyze_dependencies(repo, tree_structure),
            "layers": self._identify_layers(tree_structure),
        }
        
        return architecture
    
    def _detect_project_type(self, structure: Dict, languages: Dict[str, int]) -> str:
        """Detect the type of project (web app, library, CLI tool, etc.)."""
        indicators = {
            "web_frontend": ["src/components", "public", "index.html", "package.json"],
            "web_backend": ["app.py", "server.js", "routes", "controllers", "api"],
            "mobile_app": ["android", "ios", "App.js", "MainActivity.java"],
            "library": ["setup.py", "lib", "package.json"],
            "cli_tool": ["cli.py", "bin", "cmd"],
            "microservice": ["Dockerfile", "docker-compose.yml", "k8s"],
            "data_science": ["notebooks", "models", "data", "requirements.txt"],
        }
        
        matches = []
        flat_structure = self._flatten_structure(structure)
        
        for proj_type, keywords in indicators.items():
            score = sum(1 for keyword in keywords if any(keyword in path for path in flat_structure))
            if score > 0:
                matches.append((proj_type, score))
        
        if matches:
            matches.sort(key=lambda x: x[1], reverse=True)
            return matches[0][0]
        
        # Fallback to language
        primary_lang = max(languages.items(), key=lambda x: x[1])[0] if languages else "Unknown"
        return f"{primary_lang.lower()}_project"
    
    def _detect_structure_pattern(self, structure: Dict) -> str:
        """Detect common architectural patterns (MVC, microservices, monolith, etc.)."""
        flat = self._flatten_structure(structure)
        
        patterns = {
            "MVC": ["models", "views", "controllers"],
            "Layered": ["domain", "application", "infrastructure"],
            "Microservices": ["services", "docker-compose", "kubernetes"],
            "Monorepo": ["packages", "apps", "libs"],
            "Feature-based": ["features", "modules"],
            "Clean Architecture": ["entities", "usecases", "adapters"],
        }
        
        for pattern_name, keywords in patterns.items():
            if sum(1 for k in keywords if any(k in p for p in flat)) >= 2:
                return pattern_name
        
        return "Standard"
    
    def _identify_components(self, structure: Dict) -> List[Dict[str, Any]]:
        """Identify major components and their purposes."""
        components = []
        
        component_indicators = {
            "Frontend": ["src/components", "frontend", "client", "ui"],
            "Backend/API": ["api", "backend", "server", "routes"],
            "Database": ["models", "migrations", "schema", "db"],
            "Authentication": ["auth", "authentication", "login"],
            "Testing": ["tests", "test", "__tests__", "spec"],
            "Documentation": ["docs", "documentation"],
            "Configuration": ["config", "settings", "env"],
            "Build/Deploy": ["build", "dist", "deployment", "scripts"],
            "Services": ["services", "workers", "jobs"],
            "Utils/Helpers": ["utils", "helpers", "common", "shared"],
        }
        
        flat = self._flatten_structure(structure)
        
        for component_name, keywords in component_indicators.items():
            matching_paths = [p for p in flat if any(k in p.lower() for k in keywords)]
            if matching_paths:
                components.append({
                    "name": component_name,
                    "paths": matching_paths[:5],  # Top 5 paths
                    "file_count": len(matching_paths)
                })
        
        return components
    
    def _find_entry_points(self, structure: Dict) -> List[str]:
        """Find main entry points of the application."""
        entry_patterns = [
            "main.py", "app.py", "index.js", "index.ts", "server.js",
            "main.go", "Main.java", "index.html", "App.js", "app.js",
            "__init__.py", "setup.py", "manage.py"
        ]
        
        flat = self._flatten_structure(structure)
        entry_points = [p for p in flat if any(pattern in p for pattern in entry_patterns)]
        
        return entry_points[:10]  # Top 10
    
    def _find_config_files(self, structure: Dict) -> List[str]:
        """Find configuration files."""
        config_patterns = [
            ".env", "config", "settings", ".yml", ".yaml", ".json",
            "Dockerfile", "docker-compose", "requirements.txt",
            "package.json", "tsconfig", "webpack", "babel"
        ]
        
        flat = self._flatten_structure(structure)
        configs = [p for p in flat if any(pattern in p.lower() for pattern in config_patterns)]
        
        return configs[:15]  # Top 15
    
    def _analyze_dependencies(self, repo: Repository, structure: Dict) -> Dict[str, Any]:
        """Analyze project dependencies."""
        deps = {
            "package_managers": [],
            "dependency_files": []
        }
        
        dep_files = {
            "Python": ["requirements.txt", "setup.py", "pyproject.toml", "Pipfile"],
            "Node.js": ["package.json", "yarn.lock", "package-lock.json"],
            "Java": ["pom.xml", "build.gradle"],
            "Ruby": ["Gemfile"],
            "Go": ["go.mod"],
            "Rust": ["Cargo.toml"],
            "PHP": ["composer.json"],
        }
        
        flat = self._flatten_structure(structure)
        
        for lang, files in dep_files.items():
            found = [f for f in files if any(f in p for p in flat)]
            if found:
                deps["package_managers"].append(lang)
                deps["dependency_files"].extend(found)
        
        return deps
    
    def _identify_layers(self, structure: Dict) -> List[str]:
        """Identify architectural layers."""
        layers = []
        layer_keywords = {
            "Presentation": ["ui", "views", "pages", "components", "frontend"],
            "Business Logic": ["services", "domain", "core", "business"],
            "Data Access": ["repositories", "dao", "models", "database"],
            "Infrastructure": ["infrastructure", "adapters", "external"],
        }
        
        flat = self._flatten_structure(structure)
        
        for layer_name, keywords in layer_keywords.items():
            if any(k in p.lower() for p in flat for k in keywords):
                layers.append(layer_name)
        
        return layers
    
    def _flatten_structure(self, structure: Dict, prefix: str = "") -> List[str]:
        """Flatten nested structure to list of paths."""
        paths = []
        for key, value in structure.items():
            path = f"{prefix}/{key}" if prefix else key
            paths.append(path)
            if isinstance(value, dict):
                paths.extend(self._flatten_structure(value, path))
        return paths