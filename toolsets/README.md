# Toolsets Directory

This directory contains curated toolsets that combine individual tools for specific workflows and use cases.

## 🎯 Available Toolsets

### 🔍 Web Research Toolset (`web_research.py`)
**Purpose**: Comprehensive web research and data extraction

**Combines**: Web Operations + Data Processing + File Operations

**Capabilities**:
- Topic research with multiple sources
- Website structure analysis
- Website change monitoring
- Structured data extraction (JSON-LD, microdata)

**Use Cases**:
- Academic research
- Market analysis
- Competitive intelligence
- Content aggregation

**Safety Features**:
- Rate limiting between requests
- Depth limiting for web crawling
- Content validation
- Error handling and retries

**Example Usage**:
```python
from toolsets.web_research import WebResearchToolset

toolset = WebResearchToolset("./research_data")
result = toolset.research_topic("artificial intelligence ethics")
```

### 💻 Code Development Toolset (`code_development.py`)
**Purpose**: Comprehensive code analysis and development support

**Combines**: Code Analysis + File Operations + Data Processing

**Capabilities**:
- Project-wide code analysis
- Detailed code reviews
- Refactoring suggestions
- Automated documentation generation

**Use Cases**:
- Code quality assessment
- Security audits
- Performance analysis
- Documentation maintenance

**Safety Features**:
- Path traversal protection
- Non-destructive analysis
- Comprehensive error handling
- Score-based recommendations

**Example Usage**:
```python
from toolsets.code_development import CodeDevelopmentToolset

toolset = CodeDevelopmentToolset("./my_project")
result = toolset.analyze_project()
```

## 🏗️ Toolset Architecture

### Design Principles
1. **Composability**: Toolsets combine individual tools for complex workflows
2. **Safety First**: All toolsets inherit safety features from component tools
3. **Consistency**: Standardized interfaces and response formats
4. **Extensibility**: Easy to add new capabilities or modify existing ones

### Standard Structure
```python
class ToolsetName:
    def __init__(self, config_params):
        # Initialize component tools
        self.tool1 = Tool1()
        self.tool2 = Tool2()
    
    def workflow_method(self, params):
        # Combine tools for specific workflow
        pass
    
    def _helper_method(self, data):
        # Internal helper methods
        pass

# Metadata
TOOLSET_INFO = {
    "name": "toolset_name",
    "description": "Toolset description",
    "version": "1.0.0",
    "capabilities": ["method1", "method2"],
    "tools_used": ["tool1", "tool2"],
    "safety_features": ["feature1", "feature2"]
}
```

## 🚀 Creating New Toolsets

When creating new toolsets, follow these guidelines:

### 1. Identify the Workflow
- Define the specific problem or use case
- Determine which individual tools are needed
- Plan the workflow sequence

### 2. Design the Interface
- Use descriptive method names
- Provide comprehensive parameters
- Return consistent response format

### 3. Implement Safety Features
- Inherit safety from component tools
- Add workflow-specific validations
- Handle errors gracefully

### 4. Document Thoroughly
- Explain the purpose and use cases
- Provide usage examples
- Document safety features

### Template
```python
"""
New Toolset Template
Description of the toolset's purpose and capabilities.
"""

from typing import Dict, List, Any, Optional
from ..tools.tool1 import Tool1
from ..tools.tool2 import Tool2

class NewToolset:
    """
    Comprehensive toolset for specific workflow.
    
    Combines multiple tools to achieve complex tasks.
    """
    
    def __init__(self, config_param: str = "default"):
        """
        Initialize toolset.
        
        Args:
            config_param: Configuration parameter
        """
        self.tool1 = Tool1()
        self.tool2 = Tool2()
        self.config = config_param
    
    def primary_workflow(self, input_data: Any) -> Dict[str, Any]:
        """
        Primary workflow method.
        
        Args:
            input_data: Input data for processing
            
        Returns:
            Dictionary with workflow results
        """
        try:
            # Step 1: Use tool1
            result1 = self.tool1.method(input_data)
            if not result1["success"]:
                return {"success": False, "error": "Tool1 failed"}
            
            # Step 2: Process results
            processed_data = self._process_data(result1["data"])
            
            # Step 3: Use tool2
            result2 = self.tool2.method(processed_data)
            if not result2["success"]:
                return {"success": False, "error": "Tool2 failed"}
            
            return {
                "success": True,
                "result": result2["data"],
                "intermediate": result1["data"]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _process_data(self, data: Any) -> Any:
        """Internal data processing method."""
        # Processing logic here
        return data

# Toolset metadata
TOOLSET_INFO = {
    "name": "new_toolset",
    "description": "Description of the new toolset",
    "version": "1.0.0",
    "author": "CBW Agents",
    "capabilities": ["primary_workflow"],
    "tools_used": ["tool1", "tool2"],
    "safety_features": ["error_handling", "input_validation"]
}
```

## 📊 Toolset Categories

### Research & Analysis
- **Web Research**: Online research and data extraction
- **Data Analysis**: Statistical analysis and visualization
- **Market Research**: Competitive intelligence and market analysis

### Development & Engineering
- **Code Development**: Code analysis and review
- **Testing**: Automated testing and quality assurance
- **Deployment**: Deployment and monitoring

### Content & Media
- **Content Generation**: Automated content creation
- **Media Processing**: Image, video, and audio processing
- **SEO Optimization**: Search engine optimization tools

### Business & Operations
- **Business Intelligence**: Data-driven business insights
- **Workflow Automation**: Business process automation
- **Customer Support**: Automated customer service tools

## 🔧 Configuration and Customization

### Environment Variables
Toolsets can be configured using environment variables:
```bash
export RESEARCH_MAX_SOURCES=20
export CODE_ANALYSIS_DEPTH=3
export WEB_REQUEST_TIMEOUT=60
```

### Configuration Files
Create `config.json` in the toolset directory:
```json
{
    "web_research": {
        "max_sources": 15,
        "request_delay": 2.0,
        "content_length_limit": 1000000
    },
    "code_development": {
        "analysis_depth": "deep",
        "include_patterns": ["*.py", "*.js"],
        "exclude_patterns": ["test_*", "*_test.py"]
    }
}
```

## 🧪 Testing Toolsets

Each toolset includes example usage in the `if __name__ == "__main__":` block:

```python
if __name__ == "__main__":
    # Example usage
    toolset = NewToolset()
    result = toolset.primary_workflow("test_data")
    print("Result:", result["success"])
```

## 📞 Contributing

When contributing new toolsets:

1. **Follow the template structure**
2. **Include comprehensive documentation**
3. **Add safety features**
4. **Provide usage examples**
5. **Test with sample data**
6. **Update this README**

## 📚 Additional Resources

- [Individual Tools Documentation](../tools/README.md)
- [Agent Configurations](../agents/)
- [CrewAI Setups](../crews/)
- [MCP Server Configs](../mcp-servers/)