from github import Repository
from typing import Dict, Any, List
import re

class CodeStructureAnalyzer:
    """Analyzes code implementation details and patterns."""
    
    def analyze(self, repo: Repository, tree_structure: Dict, github_client) -> Dict[str, Any]:
        """Analyze code structure, patterns, and quality indicators."""
        
        analysis = {
            "code_organization": self._analyze_organization(tree_structure),
            "file_types": self._analyze_file_types(tree_structure),
            "naming_conventions": self._analyze_naming(tree_structure),
            "key_directories": self._identify_key_directories(tree_structure),
            "test_coverage_indicators": self._analyze_testing(tree_structure),
            "code_quality_indicators": self._analyze_quality_indicators(tree_structure),
        }
        
        # Sample key files for deeper analysis
        key_files = self._identify_key_files(tree_structure)
        if key_files:
            analysis["key_files"] = key_files[:10]
        
        return analysis
    
    def _analyze_organization(self, structure: Dict) -> Dict[str, Any]:
        """Analyze how code is organized."""
        flat = self._flatten_structure(structure)
        
        return {
            "total_files": len(flat),
            "directory_depth": max((path.count('/') for path in flat), default=0),
            "avg_files_per_directory": len(flat) / max(len([p for p in flat if '/' not in p]), 1),
            "has_src_directory": any('src/' in p for p in flat),
            "has_lib_directory": any('lib/' in p for p in flat),
            "has_tests_directory": any('test' in p.lower() for p in flat),
        }
    
    def _analyze_file_types(self, structure: Dict) -> Dict[str, int]:
        """Count files by extension."""
        flat = self._flatten_structure(structure)
        extensions = {}
        
        for path in flat:
            if '.' in path:
                ext = path.split('.')[-1].lower()
                extensions[ext] = extensions.get(ext, 0) + 1
        
        # Sort by frequency
        return dict(sorted(extensions.items(), key=lambda x: x[1], reverse=True)[:15])
    
    def _analyze_naming(self, structure: Dict) -> Dict[str, Any]:
        """Analyze naming conventions used."""
        flat = self._flatten_structure(structure)
        
        conventions = {
            "snake_case": sum(1 for p in flat if '_' in p and p.islower()),
            "camelCase": sum(1 for p in flat if re.search(r'[a-z][A-Z]', p)),
            "PascalCase": sum(1 for p in flat if p and p[0].isupper() and re.search(r'[A-Z][a-z]', p)),
            "kebab-case": sum(1 for p in flat if '-' in p),
        }
        
        total = sum(conventions.values())
        if total > 0:
            dominant = max(conventions.items(), key=lambda x: x[1])
            return {
                "dominant_convention": dominant[0],
                "conventions_used": {k: f"{(v/total)*100:.1f}%" for k, v in conventions.items() if v > 0}
            }
        
        return {"dominant_convention": "mixed", "conventions_used": {}}
    
    def _identify_key_directories(self, structure: Dict) -> List[Dict[str, Any]]:
        """Identify important directories and their purposes."""
        directories = {}
        flat = self._flatten_structure(structure)
        
        for path in flat:
            if '/' in path:
                dir_name = path.split('/')[0]
                directories[dir_name] = directories.get(dir_name, 0) + 1
        
        # Sort by file count
        sorted_dirs = sorted(directories.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return [{"name": name, "file_count": count} for name, count in sorted_dirs]
    
    def _analyze_testing(self, structure: Dict) -> Dict[str, Any]:
        """Analyze testing setup."""
        flat = self._flatten_structure(structure)
        
        test_indicators = {
            "has_tests": any('test' in p.lower() for p in flat),
            "test_files_count": sum(1 for p in flat if 'test' in p.lower()),
            "test_frameworks": self._detect_test_frameworks(flat),
            "test_directories": [p for p in flat if 'test' in p.lower() and '/' not in p.replace('tests/', '').replace('test/', '')][:5]
        }
        
        return test_indicators
    
    def _detect_test_frameworks(self, paths: List[str]) -> List[str]:
        """Detect testing frameworks used."""
        frameworks = {
            "pytest": ["pytest", "conftest.py"],
            "unittest": ["unittest"],
            "jest": ["jest.config", ".spec.js", ".test.js"],
            "mocha": ["mocha"],
            "jasmine": ["jasmine"],
            "junit": ["junit", ".test.java"],
            "rspec": ["spec", "_spec.rb"],
        }
        
        detected = []
        for framework, indicators in frameworks.items():
            if any(ind in p.lower() for p in paths for ind in indicators):
                detected.append(framework)
        
        return detected
    
    def _analyze_quality_indicators(self, structure: Dict) -> Dict[str, Any]:
        """Analyze code quality indicators."""
        flat = self._flatten_structure(structure)
        
        return {
            "has_ci_cd": any(ci in p for p in flat for ci in ['.github/workflows', '.gitlab-ci', 'jenkins', '.circleci']),
            "has_linting": any(lint in p for p in flat for lint in ['.eslintrc', '.pylintrc', 'ruff.toml', '.rubocop']),
            "has_formatting": any(fmt in p for p in flat for fmt in ['.prettierrc', '.black', '.editorconfig']),
            "has_documentation": any('docs/' in p or 'documentation/' in p for p in flat),
            "has_contributing_guide": any('contributing' in p.lower() for p in flat),
            "has_license": any('license' in p.lower() for p in flat),
        }
    
    def _identify_key_files(self, structure: Dict) -> List[str]:
        """Identify key files worth examining."""
        flat = self._flatten_structure(structure)
        
        key_patterns = [
            "main", "app", "index", "server", "api", "core",
            "router", "controller", "service", "model", "view"
        ]
        
        key_files = []
        for path in flat:
            filename = path.split('/')[-1].lower()
            if any(pattern in filename for pattern in key_patterns):
                key_files.append(path)
        
        return key_files
    
    def _flatten_structure(self, structure: Dict, prefix: str = "") -> List[str]:
        """Flatten nested structure to list of paths."""
        if not isinstance(structure, dict):
            return []
            
        paths = []
        for key, value in structure.items():
            if not isinstance(key, str):
                continue
                
            path = f"{prefix}/{key}" if prefix else key
            paths.append(path)
            
            # Only recurse if value is a dictionary
            if isinstance(value, dict):
                paths.extend(self._flatten_structure(value, path))
        return paths