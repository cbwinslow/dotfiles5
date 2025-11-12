"""
Code Analysis Tool
Provides comprehensive code analysis capabilities for AI agents.
"""

import ast
import re
import os
import subprocess
from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path
import json
import hashlib

class CodeAnalysisTool:
    """
    Comprehensive code analysis tool for AI agents.
    Supports static analysis, complexity metrics, security scanning, and more.
    """
    
    def __init__(self, base_path: str = "."):
        """
        Initialize code analysis tool.
        
        Args:
            base_path: Base directory for code analysis
        """
        self.base_path = Path(base_path).resolve()
        self.supported_languages = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php'
        }
        
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a single code file.
        
        Args:
            file_path: Path to the code file
            
        Returns:
            Dictionary with analysis results
        """
        try:
            full_path = self._resolve_path(file_path)
            
            if not full_path.exists():
                return {"success": False, "error": "File not found"}
                
            language = self._detect_language(full_path)
            
            if language == 'python':
                return self._analyze_python_file(full_path)
            else:
                return self._analyze_generic_file(full_path, language)
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def analyze_directory(self, dir_path: str = ".", recursive: bool = True) -> Dict[str, Any]:
        """
        Analyze all code files in a directory.
        
        Args:
            dir_path: Directory path to analyze
            recursive: Whether to analyze recursively
            
        Returns:
            Dictionary with aggregated analysis results
        """
        try:
            full_path = self._resolve_path(dir_path)
            
            if not full_path.exists():
                return {"success": False, "error": "Directory not found"}
            
            # Find all code files
            code_files = []
            if recursive:
                for file_path in full_path.rglob("*"):
                    if file_path.is_file() and file_path.suffix in self.supported_languages:
                        code_files.append(file_path)
            else:
                for file_path in full_path.iterdir():
                    if file_path.is_file() and file_path.suffix in self.supported_languages:
                        code_files.append(file_path)
            
            # Analyze each file
            file_analyses = {}
            summary = {
                "total_files": len(code_files),
                "languages": {},
                "total_lines": 0,
                "total_functions": 0,
                "total_classes": 0,
                "security_issues": [],
                "complexity_metrics": {}
            }
            
            for file_path in code_files:
                analysis = self.analyze_file(str(file_path))
                if analysis["success"]:
                    file_analyses[str(file_path)] = analysis
                    
                    # Update summary
                    language = analysis.get("language", "unknown")
                    summary["languages"][language] = summary["languages"].get(language, 0) + 1
                    summary["total_lines"] += analysis.get("metrics", {}).get("lines_of_code", 0)
                    summary["total_functions"] += len(analysis.get("functions", []))
                    summary["total_classes"] += len(analysis.get("classes", []))
                    
                    # Collect security issues
                    if "security_issues" in analysis:
                        summary["security_issues"].extend(analysis["security_issues"])
            
            return {
                "success": True,
                "summary": summary,
                "files": file_analyses,
                "analyzed_at": str(Path.cwd())
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _analyze_python_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze Python file using AST."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            analysis = {
                "success": True,
                "file_path": str(file_path),
                "language": "python",
                "functions": [],
                "classes": [],
                "imports": [],
                "metrics": {},
                "security_issues": [],
                "complexity": {}
            }
            
            # Analyze AST nodes
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = self._analyze_function(node)
                    analysis["functions"].append(func_info)
                    
                elif isinstance(node, ast.ClassDef):
                    class_info = self._analyze_class(node)
                    analysis["classes"].append(class_info)
                    
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    import_info = self._analyze_import(node)
                    analysis["imports"].append(import_info)
            
            # Calculate metrics
            analysis["metrics"] = self._calculate_metrics(content, tree)
            
            # Security analysis
            analysis["security_issues"] = self._analyze_python_security(content, tree)
            
            # Complexity analysis
            analysis["complexity"] = self._calculate_complexity(tree)
            
            return analysis
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _analyze_generic_file(self, file_path: Path, language: str) -> Dict[str, Any]:
        """Analyze non-Python files with basic metrics."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            analysis = {
                "success": True,
                "file_path": str(file_path),
                "language": language,
                "metrics": {
                    "lines_of_code": len(lines),
                    "non_empty_lines": len([line for line in lines if line.strip()]),
                    "comment_lines": self._count_comment_lines(content, language),
                    "file_size": len(content)
                },
                "security_issues": self._analyze_generic_security(content, language)
            }
            
            return analysis
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _analyze_function(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """Analyze a Python function."""
        return {
            "name": node.name,
            "line_number": node.lineno,
            "arguments": [arg.arg for arg in node.args.args],
            "decorators": [d.id if isinstance(d, ast.Name) else str(d) for d in node.decorator_list],
            "docstring": ast.get_docstring(node),
            "complexity": self._calculate_function_complexity(node)
        }
    
    def _analyze_class(self, node: ast.ClassDef) -> Dict[str, Any]:
        """Analyze a Python class."""
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(item.name)
        
        return {
            "name": node.name,
            "line_number": node.lineno,
            "methods": methods,
            "decorators": [d.id if isinstance(d, ast.Name) else str(d) for d in node.decorator_list],
            "docstring": ast.get_docstring(node),
            "base_classes": [base.id if isinstance(base, ast.Name) else str(base) for base in node.bases]
        }
    
    def _analyze_import(self, node) -> Dict[str, Any]:
        """Analyze import statements."""
        if isinstance(node, ast.Import):
            return {
                "type": "import",
                "modules": [alias.name for alias in node.names],
                "line_number": node.lineno
            }
        elif isinstance(node, ast.ImportFrom):
            return {
                "type": "from_import",
                "module": node.module,
                "names": [alias.name for alias in node.names],
                "line_number": node.lineno
            }
    
    def _calculate_metrics(self, content: str, tree: ast.AST) -> Dict[str, Any]:
        """Calculate code metrics."""
        lines = content.split('\n')
        
        return {
            "lines_of_code": len(lines),
            "non_empty_lines": len([line for line in lines if line.strip()]),
            "comment_lines": len([line for line in lines if line.strip().startswith('#')]),
            "docstring_lines": len(re.findall(r'""".*?"""', content, re.DOTALL)) + 
                           len(re.findall(r"'''.*?'''", content, re.DOTALL)),
            "file_size": len(content)
        }
    
    def _analyze_python_security(self, content: str, tree: ast.AST) -> List[Dict[str, Any]]:
        """Analyze Python code for security issues."""
        issues = []
        
        # Check for dangerous functions
        dangerous_patterns = {
            r'eval\s*\(': "Use of eval() function",
            r'exec\s*\(': "Use of exec() function",
            r'shell=True': "Shell injection vulnerability",
            r'pickle\.loads?\s*\(': "Unsafe pickle usage",
            r'subprocess\.call\s*\([^)]*shell=True': "Shell injection in subprocess"
        }
        
        for pattern, description in dangerous_patterns.items():
            matches = re.finditer(pattern, content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues.append({
                    "type": "security",
                    "severity": "high",
                    "description": description,
                    "line_number": line_num,
                    "code_snippet": content.split('\n')[line_num-1].strip()
                })
        
        # Check for hardcoded passwords
        password_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'pwd\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']'
        ]
        
        for pattern in password_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues.append({
                    "type": "security",
                    "severity": "medium",
                    "description": "Potential hardcoded password/secret",
                    "line_number": line_num,
                    "code_snippet": content.split('\n')[line_num-1].strip()
                })
        
        return issues
    
    def _analyze_generic_security(self, content: str, language: str) -> List[Dict[str, Any]]:
        """Analyze non-Python code for security issues."""
        issues = []
        
        # Common security patterns across languages
        if language in ['javascript', 'typescript']:
            js_patterns = {
                r'eval\s*\(': "Use of eval() function",
                r'document\.write\s*\(': "XSS vulnerability",
                r'innerHTML\s*=': "Potential XSS vulnerability"
            }
            
            for pattern, description in js_patterns.items():
                matches = re.finditer(pattern, content)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    issues.append({
                        "type": "security",
                        "severity": "high",
                        "description": description,
                        "line_number": line_num
                    })
        
        return issues
    
    def _calculate_complexity(self, tree: ast.AST) -> Dict[str, Any]:
        """Calculate cyclomatic complexity."""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.With)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return {
            "cyclomatic_complexity": complexity,
            "complexity_level": "low" if complexity <= 5 else "medium" if complexity <= 10 else "high"
        }
    
    def _calculate_function_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate complexity for a single function."""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.With)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _count_comment_lines(self, content: str, language: str) -> int:
        """Count comment lines for different languages."""
        comment_patterns = {
            'python': r'^\s*#',
            'javascript': r'^\s*//|^\s*/\*',
            'typescript': r'^\s*//|^\s*/\*',
            'java': r'^\s*//|^\s*/\*',
            'cpp': r'^\s*//|^\s*/\*',
            'c': r'^\s*//|^\s*/\*',
            'go': r'^\s*//',
            'rust': r'^\s*//',
            'ruby': r'^\s*#',
            'php': r'^\s*//|^\s*/\*|^\s*\#'
        }
        
        pattern = comment_patterns.get(language, r'^\s*#')
        lines = content.split('\n')
        return len([line for line in lines if re.match(pattern, line)])
    
    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension."""
        return self.supported_languages.get(file_path.suffix, 'unknown')
    
    def _resolve_path(self, path: str) -> Path:
        """Resolve and validate path."""
        resolved_path = Path(path).resolve()
        
        # Ensure the path is within the base path
        try:
            resolved_path.relative_to(self.base_path)
        except ValueError:
            raise ValueError("Path outside allowed directory")
            
        return resolved_path

# Tool metadata
TOOL_INFO = {
    "name": "code_analysis",
    "description": "Comprehensive code analysis tool for static analysis and security scanning",
    "version": "1.0.0",
    "author": "CBW Agents",
    "capabilities": [
        "analyze_file",
        "analyze_directory",
        "security_scanning",
        "complexity_analysis",
        "metrics_calculation"
    ],
    "requirements": ["ast", "re", "pathlib", "json"],
    "safety_features": [
        "Path traversal protection",
        "Error handling",
        "Language detection",
        "Security pattern matching"
    ]
}

if __name__ == "__main__":
    # Example usage
    tool = CodeAnalysisTool()
    
    # Test file analysis
    result = tool.analyze_file("tools/code_analysis.py")
    print("Analysis result:", result["success"])