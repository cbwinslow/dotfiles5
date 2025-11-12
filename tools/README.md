# Tools Directory

This directory contains comprehensive tools for AI agents to perform various operations safely and efficiently.

## 🛠️ Available Tools

### 📁 File Operations (`file_operations.py`)
**Purpose**: Comprehensive file system operations with safety features

**Capabilities**:
- Read/write files with encoding support
- Directory listing and creation
- File search (by name, content, extension)
- File hashing and validation
- Path traversal protection

**Safety Features**:
- File size limits (default: 100MB)
- Extension filtering
- Path validation
- Error handling

**Usage Example**:
```python
from tools.file_operations import FileOperationsTool

tool = FileOperationsTool(base_path="./safe_directory")
result = tool.read_file("example.txt")
```

### 🌐 Web Operations (`web_operations.py`)
**Purpose**: Safe web scraping and API interactions

**Capabilities**:
- HTTP requests with retry logic
- Web page scraping and data extraction
- File downloads
- URL validation
- JSON extraction from HTML
- Rate limiting

**Safety Features**:
- Request timeout (default: 30s)
- Rate limiting between requests
- User agent spoofing
- Error handling and retries

**Usage Example**:
```python
from tools.web_operations import WebOperationsTool

tool = WebOperationsTool()
result = tool.scrape_webpage("https://example.com")
```

### 📊 Data Processing (`data_processing.py`)
**Purpose**: Data analysis, cleaning, and transformation

**Capabilities**:
- Load data from multiple formats (CSV, JSON, Excel, Parquet)
- Data cleaning (duplicates, missing values, outliers)
- Statistical analysis and correlation
- Data transformation (normalization, encoding)
- Data export

**Safety Features**:
- Memory usage monitoring
- Data size limits
- Type validation
- Error handling

**Usage Example**:
```python
from tools.data_processing import DataProcessingTool
import pandas as pd

tool = DataProcessingTool()
result = tool.load_data("data.csv")
```

### 🔍 Code Analysis (`code_analysis.py`)
**Purpose**: Static code analysis and security scanning

**Capabilities**:
- Multi-language support (Python, JavaScript, Java, C++, etc.)
- AST-based analysis for Python
- Security vulnerability detection
- Complexity metrics calculation
- Code quality assessment

**Safety Features**:
- Path traversal protection
- Language detection
- Pattern-based security scanning
- Error handling

**Usage Example**:
```python
from tools.code_analysis import CodeAnalysisTool

tool = CodeAnalysisTool()
result = tool.analyze_directory("./src")
```

## 📋 Tool Standards

All tools follow these standards:

### 🔧 Interface Design
- Consistent method signatures
- Dictionary-based responses with `success` field
- Comprehensive error handling
- Type hints for better IDE support

### 🛡️ Safety Features
- Input validation and sanitization
- Resource limits (memory, file size, requests)
- Path traversal protection
- Rate limiting for external operations

### 📊 Response Format
```python
{
    "success": True/False,
    "data": ...,  # Operation result
    "metadata": {...},  # Additional information
    "error": "Error message"  # Only if success=False
}
```

### 📝 Documentation
- Comprehensive docstrings
- Usage examples
- Safety feature documentation
- Requirements and dependencies

## 🚀 Adding New Tools

When creating new tools, follow this template:

```python
"""
Tool Description
Brief description of what the tool does.
"""

class NewTool:
    """
    Comprehensive tool description.
    
    Safety features and capabilities.
    """
    
    def __init__(self, param1: type, param2: type = default):
        """Initialize tool with parameters."""
        pass
    
    def method_name(self, param: type) -> Dict[str, Any]:
        """
        Method description.
        
        Args:
            param: Parameter description
            
        Returns:
            Dictionary with operation result
        """
        pass

# Tool metadata
TOOL_INFO = {
    "name": "tool_name",
    "description": "Tool description",
    "version": "1.0.0",
    "author": "CBW Agents",
    "capabilities": ["method1", "method2"],
    "requirements": ["library1", "library2"],
    "safety_features": ["feature1", "feature2"]
}
```

## 🔗 Dependencies

Common dependencies across tools:
- `pathlib` - Path operations
- `typing` - Type hints
- `json` - JSON handling
- `re` - Regular expressions
- `datetime` - Date/time operations

Tool-specific dependencies are documented in each tool's metadata.

## 🧪 Testing

Each tool includes example usage in the `if __name__ == "__main__":` block for basic testing.

## 📞 Support

For tool issues or improvements:
1. Check the tool's documentation
2. Review safety features
3. Test with example usage
4. Follow the contribution guidelines in the main repository