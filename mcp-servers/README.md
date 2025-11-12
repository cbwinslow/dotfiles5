# MCP Servers Directory

This directory contains Model Context Protocol (MCP) server configurations for integrating AI agents with external systems and tools.

## 🔌 Available MCP Servers

### 📁 File Operations Server (`file_operations_server.json`)
**Purpose**: Comprehensive file system operations via MCP

**Capabilities**:
- File read/write operations with encoding support
- Directory listing and management
- File search and filtering
- File copying, moving, and deletion
- File information and metadata
- Symbolic link handling

**Tools Provided**:
- `read_file` - Read file contents with optional line ranges
- `write_file` - Write content with directory creation
- `list_directory` - List directory contents recursively
- `search_files` - Search by name, content, or extension
- `create_directory` - Create directories with parents
- `delete_file_or_directory` - Safe deletion with options
- `get_file_info` - Detailed file information and hashing
- `copy_file_or_directory` - Copy with permission preservation
- `move_file_or_directory` - Move/rename operations

**Security Features**:
- Path validation and traversal protection
- Allowed/blocked path configurations
- File size limits (default: 100MB)
- Permission checks and audit logging
- Rate limiting for operations

**Use Cases**:
- Code file management
- Configuration file handling
- Data file processing
- Project organization

### 🌐 Web Operations Server (`web_operations_server.json`)
**Purpose**: Web scraping, API calls, and data extraction via MCP

**Capabilities**:
- HTTP requests with all methods
- Web page scraping and data extraction
- Search engine integration
- File downloads with integrity checking
- URL validation and accessibility
- Structured data extraction (JSON-LD, microdata)
- Website change monitoring
- Batch URL processing

**Tools Provided**:
- `fetch_url` - HTTP requests with comprehensive options
- `scrape_webpage` - Extract content, links, images, metadata
- `search_web` - Multi-engine search with filtering
- `download_file` - Resumable downloads with verification
- `validate_url` - URL format and accessibility checking
- `extract_structured_data` - JSON-LD, microdata extraction
- `monitor_website_changes` - Change detection and notifications
- `batch_process_urls` - Concurrent processing of multiple URLs

**Security Features**:
- Domain allowlist/blocklist
- Robots.txt compliance
- Content filtering and malware scanning
- Download size limits (default: 50MB)
- Request rate limiting
- SSL certificate verification

**Use Cases**:
- Web research and data collection
- Content aggregation
- API integration
- Website monitoring

## 🏗️ MCP Server Architecture

### Standard Server Structure

```json
{
  "server_name": "Server Name",
  "server_version": "1.0.0",
  "description": "Server description",
  "server_type": "category",
  "protocol_version": "2024-11-05",
  "capabilities": {...},
  "tools": [...],
  "resources": [...],
  "prompts": [...],
  "configuration": {...},
  "security": {...},
  "implementation": {...}
}
```

### Core Components

#### 🔧 Tools
- **Name**: Descriptive tool identifier
- **Description**: Clear tool purpose
- **Input Schema**: JSON Schema for parameters
- **Required Parameters**: Mandatory inputs
- **Optional Parameters**: Additional options

#### 📦 Resources
- **URI**: Unique resource identifier
- **Name**: Human-readable resource name
- **Description**: Resource purpose
- **MIME Type**: Data format specification

#### 💬 Prompts
- **Name**: Prompt identifier
- **Description**: Prompt purpose
- **Arguments**: Expected parameters

#### ⚙️ Configuration
- **Default Settings**: Operational parameters
- **Limits**: Size, time, and count limits
- **Logging**: Monitoring and debugging options

#### 🛡️ Security
- **Access Control**: Path/domain restrictions
- **Rate Limiting**: Request throttling
- **Content Filtering**: Malware and content protection
- **Audit Logging**: Operation tracking

## 🚀 Creating New MCP Servers

When creating new MCP server configurations:

### 1. Define Server Purpose
- Clear scope and capabilities
- Target use cases and scenarios
- Integration requirements

### 2. Design Tool Interface
- Comprehensive tool coverage
- Consistent parameter naming
- Clear input/output specifications

### 3. Implement Security
- Access control mechanisms
- Input validation and sanitization
- Rate limiting and resource protection

### 4. Configure Monitoring
- Operation logging
- Performance metrics
- Health checks

### Template
```json
{
  "server_name": "New MCP Server",
  "server_version": "1.0.0",
  "description": "Clear description of server purpose",
  "server_type": "category",
  "protocol_version": "2024-11-05",
  "capabilities": {
    "tools": {
      "listChanged": true
    },
    "resources": {
      "subscribe": true,
      "listChanged": true
    },
    "prompts": {
      "listChanged": true
    },
    "logging": {
      "level": "info"
    }
  },
  "tools": [
    {
      "name": "tool_name",
      "description": "Tool description",
      "inputSchema": {
        "type": "object",
        "properties": {
          "parameter": {
            "type": "string",
            "description": "Parameter description"
          }
        },
        "required": ["parameter"]
      }
    }
  ],
  "resources": [
    {
      "uri": "protocol://localhost/",
      "name": "Resource Name",
      "description": "Resource description",
      "mimeType": "application/json"
    }
  ],
  "prompts": [
    {
      "name": "prompt_name",
      "description": "Prompt description",
      "arguments": [
        {
          "name": "argument",
          "description": "Argument description",
          "required": true
        }
      ]
    }
  ],
  "configuration": {
    "default_setting": "value",
    "max_operations": 100,
    "enable_logging": true,
    "log_level": "info"
  },
  "security": {
    "access_control": "strict",
    "rate_limiting": {
      "enabled": true,
      "requests_per_minute": 60
    },
    "audit_logging": true
  },
  "implementation": {
    "runtime": "python",
    "dependencies": ["mcp", "library1", "library2"],
    "entry_point": "server.py",
    "environment_variables": {
      "SERVER_LOG_LEVEL": "info"
    }
  },
  "monitoring": {
    "metrics": {
      "operation_count": true,
      "response_time": true,
      "error_rate": true
    },
    "health_checks": {
      "connectivity": true,
      "resource_usage": true
    }
  },
  "version_history": [
    {
      "version": "1.0.0",
      "date": "2025-11-12",
      "changes": "Initial release"
    }
  ],
  "maintenance": {
    "last_updated": "2025-11-12",
    "next_review": "2025-12-12",
    "update_frequency": "monthly"
  }
}
```

## 📊 Server Categories

### 📁 File & Data Operations
- **File Operations Server**: File system management
- **Database Server**: Database operations and queries
- **Cache Server**: Data caching and retrieval

### 🌐 Network & Web
- **Web Operations Server**: Web scraping and API calls
- **Email Server**: Email sending and receiving
- **FTP Server**: File transfer operations

### 🔧 Development & DevOps
- **Git Server**: Version control operations
- **CI/CD Server**: Build and deployment automation
- **Testing Server**: Automated testing operations

### 📈 Analytics & Monitoring
- **Metrics Server**: Performance and usage metrics
- **Logging Server**: Log aggregation and analysis
- **Alerting Server**: Notification and alerting

## ⚙️ Configuration Guidelines

### Security First
- Implement proper access controls
- Validate all inputs
- Enable comprehensive logging
- Set reasonable limits

### Performance Optimization
- Configure appropriate timeouts
- Enable caching where beneficial
- Set concurrency limits
- Monitor resource usage

### Reliability
- Implement error handling
- Enable retry mechanisms
- Configure health checks
- Plan for failover

## 🧪 Server Testing

Test MCP server configurations using:

```python
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_mcp_server(server_config_path):
    # Load server configuration
    with open(server_config_path, 'r') as f:
        config = json.load(f)
    
    # Create server parameters
    server_params = StdioServerParameters(
        command="python",
        args=[config["implementation"]["entry_point"]]
    )
    
    # Connect to server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize session
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print(f"Available tools: {[tool.name for tool in tools.tools]}")
            
            # Test a tool
            if tools.tools:
                result = await session.call_tool(tools.tools[0].name, {})
                print(f"Tool result: {result}")

# Test file operations server
import asyncio
asyncio.run(test_mcp_server("mcp-servers/file_operations_server.json"))
```

## 📞 Usage Examples

### Server Integration
```python
# Load and configure server
with open('mcp-servers/file_operations_server.json', 'r') as f:
    server_config = json.load(f)

# Initialize server with custom configuration
server = FileOperationsMCPServer(
    allowed_paths=["./workspace"],
    max_file_size=50 * 1024 * 1024  # 50MB
)

# Start server
await server.start()
```

### Client Usage
```python
# Connect to MCP server
client = MCPClient("file_operations_server")

# Use server tools
result = await client.call_tool("read_file", {
    "file_path": "./workspace/example.txt",
    "encoding": "utf-8"
})

print(result.content)
```

## 🔄 Server Management

### Monitoring
- Track operation metrics
- Monitor error rates
- Analyze performance trends
- Set up alerts

### Maintenance
- Regular configuration reviews
- Dependency updates
- Security audits
- Performance optimization

### Version Control
- Track configuration changes
- Document breaking changes
- Maintain compatibility
- Plan upgrade paths

## 📚 Additional Resources

- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Agent Configurations](../agents/)
- [Tools Documentation](../tools/README.md)
- [CrewAI Configurations](../crews/)