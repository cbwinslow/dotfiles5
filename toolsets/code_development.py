"""
Code Development Toolset
Combines code analysis, file operations, and data processing for development tasks.
"""

from typing import Dict, List, Any, Optional
import json
import os
from pathlib import Path
from datetime import datetime

from ..tools.code_analysis import CodeAnalysisTool
from ..tools.file_operations import FileOperationsTool
from ..tools.data_processing import DataProcessingTool

class CodeDevelopmentToolset:
    """
    Comprehensive code development toolset that combines code analysis,
    file operations, and data processing for software development tasks.
    """
    
    def __init__(self, project_path: str = "."):
        """
        Initialize code development toolset.
        
        Args:
            project_path: Path to the project directory
        """
        self.project_path = Path(project_path).resolve()
        self.code_tool = CodeAnalysisTool(project_path)
        self.file_tool = FileOperationsTool(project_path)
        self.data_tool = DataProcessingTool()
        
    def analyze_project(self, include_patterns: List[str] = None, 
                       exclude_patterns: List[str] = None) -> Dict[str, Any]:
        """
        Perform comprehensive project analysis.
        
        Args:
            include_patterns: File patterns to include
            exclude_patterns: File patterns to exclude
            
        Returns:
            Dictionary with project analysis
        """
        try:
            analysis = {
                "project_path": str(self.project_path),
                "timestamp": datetime.now().isoformat(),
                "summary": {},
                "files": {},
                "metrics": {},
                "security_issues": [],
                "recommendations": []
            }
            
            # Analyze directory
            dir_analysis = self.code_tool.analyze_directory(str(self.project_path))
            if not dir_analysis["success"]:
                return {"success": False, "error": "Failed to analyze project directory"}
            
            analysis["summary"] = dir_analysis["summary"]
            analysis["files"] = dir_analysis["files"]
            
            # Calculate project metrics
            analysis["metrics"] = self._calculate_project_metrics(analysis["files"])
            
            # Collect all security issues
            for file_path, file_analysis in analysis["files"].items():
                if "security_issues" in file_analysis:
                    for issue in file_analysis["security_issues"]:
                        issue["file"] = file_path
                        analysis["security_issues"].append(issue)
            
            # Generate recommendations
            analysis["recommendations"] = self._generate_recommendations(analysis)
            
            # Save analysis
            report_file = self.project_path / "project_analysis_report.json"
            self.file_tool.write_file(str(report_file), json.dumps(analysis, indent=2))
            
            return {
                "success": True,
                "analysis": analysis,
                "report_file": str(report_file)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def code_review(self, file_path: str, focus_areas: List[str] = None) -> Dict[str, Any]:
        """
        Perform detailed code review for a specific file.
        
        Args:
            file_path: Path to the file to review
            focus_areas: Areas to focus on (security, performance, style, etc.)
            
        Returns:
            Dictionary with code review results
        """
        try:
            if focus_areas is None:
                focus_areas = ["security", "performance", "style", "maintainability"]
            
            # Analyze the file
            file_analysis = self.code_tool.analyze_file(file_path)
            if not file_analysis["success"]:
                return {"success": False, "error": "Failed to analyze file"}
            
            review = {
                "file_path": file_path,
                "timestamp": datetime.now().isoformat(),
                "focus_areas": focus_areas,
                "analysis": file_analysis,
                "issues": [],
                "suggestions": [],
                "score": {}
            }
            
            # Security review
            if "security" in focus_areas:
                security_review = self._security_review(file_analysis)
                review["issues"].extend(security_review["issues"])
                review["suggestions"].extend(security_review["suggestions"])
                review["score"]["security"] = security_review["score"]
            
            # Performance review
            if "performance" in focus_areas:
                performance_review = self._performance_review(file_analysis)
                review["issues"].extend(performance_review["issues"])
                review["suggestions"].extend(performance_review["suggestions"])
                review["score"]["performance"] = performance_review["score"]
            
            # Style review
            if "style" in focus_areas:
                style_review = self._style_review(file_analysis)
                review["issues"].extend(style_review["issues"])
                review["suggestions"].extend(style_review["suggestions"])
                review["score"]["style"] = style_review["score"]
            
            # Maintainability review
            if "maintainability" in focus_areas:
                maintainability_review = self._maintainability_review(file_analysis)
                review["issues"].extend(maintainability_review["issues"])
                review["suggestions"].extend(maintainability_review["suggestions"])
                review["score"]["maintainability"] = maintainability_review["score"]
            
            # Calculate overall score
            review["overall_score"] = sum(review["score"].values()) / len(review["score"]) if review["score"] else 0
            
            # Save review
            review_file = self.project_path / f"code_review_{Path(file_path).stem}_{int(datetime.now().timestamp())}.json"
            self.file_tool.write_file(str(review_file), json.dumps(review, indent=2))
            
            return {
                "success": True,
                "review": review,
                "review_file": str(review_file)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def refactor_suggestions(self, file_path: str) -> Dict[str, Any]:
        """
        Generate refactoring suggestions for a file.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            Dictionary with refactoring suggestions
        """
        try:
            # Analyze the file
            file_analysis = self.code_tool.analyze_file(file_path)
            if not file_analysis["success"]:
                return {"success": False, "error": "Failed to analyze file"}
            
            suggestions = {
                "file_path": file_path,
                "timestamp": datetime.now().isoformat(),
                "suggestions": [],
                "priority": "medium"
            }
            
            # Analyze functions for refactoring opportunities
            if "functions" in file_analysis:
                for func in file_analysis["functions"]:
                    func_suggestions = self._analyze_function_for_refactoring(func)
                    suggestions["suggestions"].extend(func_suggestions)
            
            # Analyze classes for refactoring opportunities
            if "classes" in file_analysis:
                for cls in file_analysis["classes"]:
                    class_suggestions = self._analyze_class_for_refactoring(cls)
                    suggestions["suggestions"].extend(class_suggestions)
            
            # General code suggestions
            general_suggestions = self._general_refactoring_suggestions(file_analysis)
            suggestions["suggestions"].extend(general_suggestions)
            
            # Prioritize suggestions
            suggestions["suggestions"] = sorted(suggestions["suggestions"], 
                                              key=lambda x: x.get("priority", 3), 
                                              reverse=True)
            
            # Save suggestions
            suggestions_file = self.project_path / f"refactor_suggestions_{Path(file_path).stem}_{int(datetime.now().timestamp())}.json"
            self.file_tool.write_file(str(suggestions_file), json.dumps(suggestions, indent=2))
            
            return {
                "success": True,
                "suggestions": suggestions,
                "suggestions_file": str(suggestions_file)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def generate_documentation(self, file_path: str = None, output_format: str = "markdown") -> Dict[str, Any]:
        """
        Generate documentation for project or specific file.
        
        Args:
            file_path: Specific file to document (None for whole project)
            output_format: Output format (markdown, html, json)
            
        Returns:
            Dictionary with generated documentation
        """
        try:
            documentation = {
                "timestamp": datetime.now().isoformat(),
                "format": output_format,
                "content": ""
            }
            
            if file_path:
                # Document specific file
                file_analysis = self.code_tool.analyze_file(file_path)
                if not file_analysis["success"]:
                    return {"success": False, "error": "Failed to analyze file"}
                
                documentation["content"] = self._generate_file_documentation(file_analysis, output_format)
                documentation["file_path"] = file_path
            else:
                # Document entire project
                dir_analysis = self.code_tool.analyze_directory(str(self.project_path))
                if not dir_analysis["success"]:
                    return {"success": False, "error": "Failed to analyze project"}
                
                documentation["content"] = self._generate_project_documentation(dir_analysis, output_format)
                documentation["project_path"] = str(self.project_path)
            
            # Save documentation
            timestamp = int(datetime.now().timestamp())
            if output_format == "markdown":
                filename = f"documentation_{timestamp}.md"
            elif output_format == "html":
                filename = f"documentation_{timestamp}.html"
            else:
                filename = f"documentation_{timestamp}.json"
            
            doc_file = self.project_path / filename
            self.file_tool.write_file(str(doc_file), documentation["content"])
            
            return {
                "success": True,
                "documentation": documentation,
                "documentation_file": str(doc_file)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _calculate_project_metrics(self, files: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate project-level metrics."""
        metrics = {
            "total_files": len(files),
            "total_lines": 0,
            "total_functions": 0,
            "total_classes": 0,
            "languages": {},
            "complexity_distribution": {"low": 0, "medium": 0, "high": 0},
            "security_score": 0
        }
        
        total_security_issues = 0
        
        for file_path, file_analysis in files.items():
            if "metrics" in file_analysis:
                metrics["total_lines"] += file_analysis["metrics"].get("lines_of_code", 0)
            
            if "functions" in file_analysis:
                metrics["total_functions"] += len(file_analysis["functions"])
            
            if "classes" in file_analysis:
                metrics["total_classes"] += len(file_analysis["classes"])
            
            if "language" in file_analysis:
                lang = file_analysis["language"]
                metrics["languages"][lang] = metrics["languages"].get(lang, 0) + 1
            
            if "complexity" in file_analysis:
                complexity_level = file_analysis["complexity"].get("complexity_level", "low")
                metrics["complexity_distribution"][complexity_level] += 1
            
            if "security_issues" in file_analysis:
                total_security_issues += len(file_analysis["security_issues"])
        
        # Calculate security score (0-100, higher is better)
        if metrics["total_files"] > 0:
            issues_per_file = total_security_issues / metrics["total_files"]
            metrics["security_score"] = max(0, 100 - (issues_per_file * 20))
        
        return metrics
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate project recommendations."""
        recommendations = []
        
        # Security recommendations
        if len(analysis["security_issues"]) > 0:
            recommendations.append({
                "category": "security",
                "priority": "high",
                "description": f"Found {len(analysis['security_issues'])} security issues",
                "action": "Review and fix all security vulnerabilities"
            })
        
        # Complexity recommendations
        high_complexity = analysis["metrics"]["complexity_distribution"]["high"]
        if high_complexity > 0:
            recommendations.append({
                "category": "complexity",
                "priority": "medium",
                "description": f"Found {high_complexity} files with high complexity",
                "action": "Consider refactoring complex files"
            })
        
        # Documentation recommendations
        total_functions = analysis["metrics"]["total_functions"]
        if total_functions > 0:
            documented_functions = sum(
                len([f for f in file_analysis.get("functions", []) if f.get("docstring")])
                for file_analysis in analysis["files"].values()
            )
            
            if documented_functions < total_functions * 0.8:
                recommendations.append({
                    "category": "documentation",
                    "priority": "medium",
                    "description": f"Only {documented_functions}/{total_functions} functions have documentation",
                    "action": "Add documentation to improve code maintainability"
                })
        
        return recommendations
    
    def _security_review(self, file_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Perform security-focused review."""
        issues = []
        suggestions = []
        
        if "security_issues" in file_analysis:
            for issue in file_analysis["security_issues"]:
                issues.append({
                    "type": "security",
                    "severity": issue.get("severity", "medium"),
                    "description": issue.get("description", ""),
                    "line": issue.get("line_number", 0)
                })
        
        # Add security suggestions
        suggestions.extend([
            "Review all user input validation",
            "Use parameterized queries for database operations",
            "Implement proper error handling without information disclosure",
            "Keep dependencies updated"
        ])
        
        # Calculate security score
        score = max(0, 100 - (len(issues) * 10))
        
        return {
            "issues": issues,
            "suggestions": suggestions,
            "score": score
        }
    
    def _performance_review(self, file_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Perform performance-focused review."""
        issues = []
        suggestions = []
        
        # Check for performance issues
        if "functions" in file_analysis:
            for func in file_analysis["functions"]:
                complexity = func.get("complexity", 1)
                if complexity > 10:
                    issues.append({
                        "type": "performance",
                        "severity": "medium",
                        "description": f"Function {func['name']} has high complexity ({complexity})",
                        "line": func.get("line_number", 0)
                    })
        
        suggestions.extend([
            "Consider caching expensive computations",
            "Optimize database queries",
            "Use appropriate data structures",
            "Profile performance bottlenecks"
        ])
        
        # Calculate performance score
        score = max(0, 100 - (len(issues) * 5))
        
        return {
            "issues": issues,
            "suggestions": suggestions,
            "score": score
        }
    
    def _style_review(self, file_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Perform code style review."""
        issues = []
        suggestions = []
        
        # Style checks would be implemented here
        # For now, provide general suggestions
        
        suggestions.extend([
            "Follow consistent naming conventions",
            "Use meaningful variable names",
            "Keep line length reasonable",
            "Add appropriate comments"
        ])
        
        # Calculate style score (default for now)
        score = 85  # Would be calculated based on actual style violations
        
        return {
            "issues": issues,
            "suggestions": suggestions,
            "score": score
        }
    
    def _maintainability_review(self, file_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Perform maintainability review."""
        issues = []
        suggestions = []
        
        # Check maintainability factors
        if "functions" in file_analysis:
            for func in file_analysis["functions"]:
                if not func.get("docstring"):
                    issues.append({
                        "type": "maintainability",
                        "severity": "low",
                        "description": f"Function {func['name']} lacks documentation",
                        "line": func.get("line_number", 0)
                    })
        
        suggestions.extend([
            "Write comprehensive documentation",
            "Use design patterns appropriately",
            "Keep functions small and focused",
            "Implement proper error handling"
        ])
        
        # Calculate maintainability score
        score = max(0, 100 - (len(issues) * 3))
        
        return {
            "issues": issues,
            "suggestions": suggestions,
            "score": score
        }
    
    def _analyze_function_for_refactoring(self, func: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze function for refactoring opportunities."""
        suggestions = []
        
        complexity = func.get("complexity", 1)
        if complexity > 10:
            suggestions.append({
                "type": "extract_method",
                "priority": "high",
                "description": f"Function {func['name']} is too complex (complexity: {complexity})",
                "suggestion": "Extract smaller methods from this function"
            })
        
        args = func.get("arguments", [])
        if len(args) > 5:
            suggestions.append({
                "type": "parameter_object",
                "priority": "medium",
                "description": f"Function {func['name']} has too many parameters ({len(args)})",
                "suggestion": "Consider using a parameter object"
            })
        
        return suggestions
    
    def _analyze_class_for_refactoring(self, cls: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze class for refactoring opportunities."""
        suggestions = []
        
        methods = cls.get("methods", [])
        if len(methods) > 15:
            suggestions.append({
                "type": "extract_class",
                "priority": "medium",
                "description": f"Class {cls['name']} has too many methods ({len(methods)})",
                "suggestion": "Consider extracting some functionality into separate classes"
            })
        
        return suggestions
    
    def _general_refactoring_suggestions(self, file_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate general refactoring suggestions."""
        suggestions = []
        
        # Check for duplicate code (simplified)
        if "functions" in file_analysis:
            func_names = [f["name"] for f in file_analysis["functions"]]
            # Look for similar names that might indicate duplicate functionality
            for i, name1 in enumerate(func_names):
                for name2 in func_names[i+1:]:
                    if name1.lower() in name2.lower() or name2.lower() in name1.lower():
                        suggestions.append({
                            "type": "duplicate_code",
                            "priority": "medium",
                            "description": f"Functions {name1} and {name2} might have duplicate functionality",
                            "suggestion": "Review for potential code consolidation"
                        })
                        break
        
        return suggestions
    
    def _generate_file_documentation(self, file_analysis: Dict[str, Any], output_format: str) -> str:
        """Generate documentation for a specific file."""
        if output_format == "markdown":
            return self._generate_markdown_file_doc(file_analysis)
        elif output_format == "html":
            return self._generate_html_file_doc(file_analysis)
        else:
            return json.dumps(file_analysis, indent=2)
    
    def _generate_project_documentation(self, dir_analysis: Dict[str, Any], output_format: str) -> str:
        """Generate documentation for the entire project."""
        if output_format == "markdown":
            return self._generate_markdown_project_doc(dir_analysis)
        elif output_format == "html":
            return self._generate_html_project_doc(dir_analysis)
        else:
            return json.dumps(dir_analysis, indent=2)
    
    def _generate_markdown_file_doc(self, file_analysis: Dict[str, Any]) -> str:
        """Generate markdown documentation for a file."""
        doc = f"# {file_analysis.get('file_path', 'Unknown File')}\n\n"
        doc += f"**Language:** {file_analysis.get('language', 'Unknown')}\n\n"
        
        if "functions" in file_analysis:
            doc += "## Functions\n\n"
            for func in file_analysis["functions"]:
                doc += f"### {func['name']}\n\n"
                if func.get("docstring"):
                    doc += f"{func['docstring']}\n\n"
                doc += f"**Arguments:** {', '.join(func.get('arguments', []))}\n\n"
                doc += f"**Complexity:** {func.get('complexity', 'N/A')}\n\n"
        
        if "classes" in file_analysis:
            doc += "## Classes\n\n"
            for cls in file_analysis["classes"]:
                doc += f"### {cls['name']}\n\n"
                if cls.get("docstring"):
                    doc += f"{cls['docstring']}\n\n"
                doc += f"**Methods:** {', '.join(cls.get('methods', []))}\n\n"
        
        return doc
    
    def _generate_markdown_project_doc(self, dir_analysis: Dict[str, Any]) -> str:
        """Generate markdown documentation for the project."""
        summary = dir_analysis.get("summary", {})
        
        doc = "# Project Documentation\n\n"
        doc += f"**Total Files:** {summary.get('total_files', 0)}\n\n"
        doc += f"**Total Lines:** {summary.get('total_lines', 0)}\n\n"
        doc += f"**Total Functions:** {summary.get('total_functions', 0)}\n\n"
        doc += f"**Total Classes:** {summary.get('total_classes', 0)}\n\n"
        
        if "languages" in summary:
            doc += "## Languages\n\n"
            for lang, count in summary["languages"].items():
                doc += f"- {lang}: {count} files\n"
            doc += "\n"
        
        return doc
    
    def _generate_html_file_doc(self, file_analysis: Dict[str, Any]) -> str:
        """Generate HTML documentation for a file."""
        # Simplified HTML generation
        html = f"<h1>{file_analysis.get('file_path', 'Unknown File')}</h1>"
        html += f"<p><strong>Language:</strong> {file_analysis.get('language', 'Unknown')}</p>"
        
        if "functions" in file_analysis:
            html += "<h2>Functions</h2>"
            for func in file_analysis["functions"]:
                html += f"<h3>{func['name']}</h3>"
                if func.get("docstring"):
                    html += f"<p>{func['docstring']}</p>"
                html += f"<p><strong>Arguments:</strong> {', '.join(func.get('arguments', []))}</p>"
        
        return html
    
    def _generate_html_project_doc(self, dir_analysis: Dict[str, Any]) -> str:
        """Generate HTML documentation for the project."""
        summary = dir_analysis.get("summary", {})
        
        html = "<h1>Project Documentation</h1>"
        html += f"<p><strong>Total Files:</strong> {summary.get('total_files', 0)}</p>"
        html += f"<p><strong>Total Lines:</strong> {summary.get('total_lines', 0)}</p>"
        
        return html

# Toolset metadata
TOOLSET_INFO = {
    "name": "code_development",
    "description": "Comprehensive code development toolset for project analysis and review",
    "version": "1.0.0",
    "author": "CBW Agents",
    "capabilities": [
        "analyze_project",
        "code_review",
        "refactor_suggestions",
        "generate_documentation"
    ],
    "tools_used": ["code_analysis", "file_operations", "data_processing"],
    "safety_features": [
        "Path validation",
        "Error handling",
        "Comprehensive analysis",
        "Non-destructive operations"
    ]
}

if __name__ == "__main__":
    # Example usage
    toolset = CodeDevelopmentToolset()
    
    # Test project analysis
    result = toolset.analyze_project()
    print("Project analysis:", result["success"])