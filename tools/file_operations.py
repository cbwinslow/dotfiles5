"""
File Operations Tool
Provides comprehensive file system operations for AI agents.
"""

import os
import shutil
import json
import yaml
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

class FileOperationsTool:
    """
    Comprehensive file operations tool for AI agents.
    Supports reading, writing, searching, and managing files safely.
    """
    
    def __init__(self, base_path: str = ".", max_file_size: int = 100 * 1024 * 1024):
        """
        Initialize file operations tool.
        
        Args:
            base_path: Base directory for operations
            max_file_size: Maximum file size in bytes (default: 100MB)
        """
        self.base_path = Path(base_path).resolve()
        self.max_file_size = max_file_size
        self.allowed_extensions = {'.txt', '.md', '.json', '.yaml', '.yml', '.py', '.js', '.ts', '.html', '.css', '.csv', '.xml'}
        
    def read_file(self, file_path: str, encoding: str = 'utf-8') -> Dict[str, Any]:
        """
        Safely read file contents.
        
        Args:
            file_path: Path to file
            encoding: File encoding
            
        Returns:
            Dictionary with file content and metadata
        """
        try:
            full_path = self._resolve_path(file_path)
            
            if not full_path.exists():
                return {"success": False, "error": "File not found"}
                
            if full_path.stat().st_size > self.max_file_size:
                return {"success": False, "error": "File too large"}
                
            with open(full_path, 'r', encoding=encoding) as f:
                content = f.read()
                
            return {
                "success": True,
                "content": content,
                "metadata": {
                    "size": full_path.stat().st_size,
                    "modified": datetime.fromtimestamp(full_path.stat().st_mtime).isoformat(),
                    "extension": full_path.suffix,
                    "path": str(full_path)
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def write_file(self, file_path: str, content: str, encoding: str = 'utf-8') -> Dict[str, Any]:
        """
        Safely write content to file.
        
        Args:
            file_path: Path to file
            content: Content to write
            encoding: File encoding
            
        Returns:
            Dictionary with operation result
        """
        try:
            full_path = self._resolve_path(file_path)
            
            # Create parent directories if they don't exist
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding=encoding) as f:
                f.write(content)
                
            return {
                "success": True,
                "message": "File written successfully",
                "path": str(full_path)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def search_files(self, pattern: str, search_type: str = "name") -> Dict[str, Any]:
        """
        Search for files matching pattern.
        
        Args:
            pattern: Search pattern
            search_type: Type of search ('name', 'content', 'extension')
            
        Returns:
            Dictionary with search results
        """
        try:
            results = []
            
            if search_type == "name":
                for file_path in self.base_path.rglob(f"*{pattern}*"):
                    if file_path.is_file():
                        results.append(str(file_path))
                        
            elif search_type == "extension":
                for file_path in self.base_path.rglob(f"*.{pattern}"):
                    if file_path.is_file():
                        results.append(str(file_path))
                        
            elif search_type == "content":
                for file_path in self.base_path.rglob("*"):
                    if file_path.is_file() and file_path.suffix in self.allowed_extensions:
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                if pattern in f.read():
                                    results.append(str(file_path))
                        except:
                            continue
                            
            return {
                "success": True,
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_directory(self, dir_path: str = ".", recursive: bool = False) -> Dict[str, Any]:
        """
        List directory contents.
        
        Args:
            dir_path: Directory path
            recursive: Whether to list recursively
            
        Returns:
            Dictionary with directory contents
        """
        try:
            full_path = self._resolve_path(dir_path)
            
            if not full_path.exists():
                return {"success": False, "error": "Directory not found"}
                
            items = []
            
            if recursive:
                for item in full_path.rglob("*"):
                    items.append({
                        "name": item.name,
                        "path": str(item),
                        "type": "directory" if item.is_dir() else "file",
                        "size": item.stat().st_size if item.is_file() else 0
                    })
            else:
                for item in full_path.iterdir():
                    items.append({
                        "name": item.name,
                        "path": str(item),
                        "type": "directory" if item.is_dir() else "file",
                        "size": item.stat().st_size if item.is_file() else 0
                    })
                    
            return {
                "success": True,
                "items": items,
                "count": len(items)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_directory(self, dir_path: str) -> Dict[str, Any]:
        """
        Create directory.
        
        Args:
            dir_path: Directory path
            
        Returns:
            Dictionary with operation result
        """
        try:
            full_path = self._resolve_path(dir_path)
            full_path.mkdir(parents=True, exist_ok=True)
            
            return {
                "success": True,
                "message": "Directory created successfully",
                "path": str(full_path)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_file(self, file_path: str) -> Dict[str, Any]:
        """
        Safely delete file or directory.
        
        Args:
            file_path: Path to delete
            
        Returns:
            Dictionary with operation result
        """
        try:
            full_path = self._resolve_path(file_path)
            
            if not full_path.exists():
                return {"success": False, "error": "Path not found"}
                
            if full_path.is_file():
                full_path.unlink()
            else:
                shutil.rmtree(full_path)
                
            return {
                "success": True,
                "message": "Deleted successfully",
                "path": str(full_path)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_file_hash(self, file_path: str, algorithm: str = "sha256") -> Dict[str, Any]:
        """
        Calculate file hash.
        
        Args:
            file_path: Path to file
            algorithm: Hash algorithm (md5, sha1, sha256)
            
        Returns:
            Dictionary with file hash
        """
        try:
            full_path = self._resolve_path(file_path)
            
            if not full_path.exists():
                return {"success": False, "error": "File not found"}
                
            hash_obj = hashlib.new(algorithm)
            with open(full_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
                    
            return {
                "success": True,
                "hash": hash_obj.hexdigest(),
                "algorithm": algorithm,
                "file": str(full_path)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _resolve_path(self, path: str) -> Path:
        """
        Resolve and validate path to prevent directory traversal.
        
        Args:
            path: Input path
            
        Returns:
            Resolved Path object
        """
        resolved_path = Path(path).resolve()
        
        # Ensure the path is within the base path
        try:
            resolved_path.relative_to(self.base_path)
        except ValueError:
            raise ValueError("Path outside allowed directory")
            
        return resolved_path

# Tool metadata
TOOL_INFO = {
    "name": "file_operations",
    "description": "Comprehensive file system operations tool",
    "version": "1.0.0",
    "author": "CBW Agents",
    "capabilities": [
        "read_file",
        "write_file", 
        "search_files",
        "list_directory",
        "create_directory",
        "delete_file",
        "get_file_hash"
    ],
    "requirements": ["pathlib", "shutil", "hashlib", "yaml", "pyyaml"],
    "safety_features": [
        "Path traversal protection",
        "File size limits",
        "Extension filtering",
        "Error handling"
    ]
}

if __name__ == "__main__":
    # Example usage
    tool = FileOperationsTool()
    
    # Test reading a file
    result = tool.read_file("README.md")
    print("Read result:", result)
    
    # Test listing directory
    result = tool.list_directory(".")
    print("List result:", result)