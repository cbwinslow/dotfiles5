# AI Agent Rules Integration Guide

## Overview

This guide explains how to integrate the cbwinslow AI Agent Rules system with any AI agent or tool to ensure automatic compliance with safety rules and operational constraints.

## Quick Start

### For Any AI Agent

Add this line to the beginning of your AI agent's startup script or configuration:

```bash
# Load AI safety rules automatically
source ~/.ai_agent_startup.sh
```

Or for Python-based agents:

```python
from pathlib import Path
import sys
sys.path.append(str(Path.home()))

# Import and initialize AI rules
from ai_rules_integration import AIAgent, with_ai_rules

# Option 1: Use the base class
class MyAgent(AIAgent):
    def __init__(self):
        super().__initinit__("my_agent_name")
    
    def process_file(self, file_path):
        if self.validate_operation("read", file_path):
            # Safe to proceed
            return self.safe_file_operation("read", file_path)

# Option 2: Use the decorator
@with_ai_rules("my_agent_name")
def my_function(file_path):
    # Function automatically validates operations
    pass
```

## Integration Methods

### 1. Shell Script Integration

For bash/zsh based AI agents:

```bash
#!/bin/bash

# Load AI rules at the very beginning
source ~/.ai_agent_startup.sh

# Your agent code here
echo "AI agent starting up..."

# Validate operations before executing
if ai_validate_operation "read" "/path/to/file"; then
    cat "/path/to/file"
fi
```

### 2. Python Integration

For Python-based AI agents:

```python
#!/usr/bin/env python3

import os
import sys
from pathlib import Path

# Add home directory to path for imports
sys.path.append(str(Path.home()))

# Import AI rules integration
try:
    from ai_rules_integration import AIAgent, initialize_ai_rules, with_ai_rules
    AI_RULES_AVAILABLE = True
except ImportError:
    AI_RULES_AVAILABLE = False
    print("Warning: AI rules integration not available")

class MyAIAgent:
    def __init__(self, agent_name="my_agent"):
        self.agent_name = agent_name
        
        if AI_RULES_AVAILABLE:
            # Initialize with AI rules compliance
            self.ai_agent = AIAgent(agent_name)
            self.logger = self.ai_agent.logger
        else:
            self.ai_agent = None
            self.logger = None
    
    def safe_operation(self, operation, target):
        """Perform operation with safety validation"""
        if self.ai_agent:
            if not self.ai_agent.validate_operation(operation, target):
                raise Exception(f"Operation {operation} on {target} violates AI rules")
            
            # Log the operation
            self.ai_agent.log_action(operation, {"target": target})
        
        # Perform the actual operation
        print(f"Performing {operation} on {target}")
        return True

# Usage
if __name__ == "__main__":
    agent = MyAIAgent("example_agent")
    agent.safe_operation("read", "/home/user/safe_file.txt")
```

### 3. VSCode Extension Integration

For VSCode extensions:

```typescript
// In your extension's activation function
import * as path from 'path';
import { execSync } from 'child_process';

function activate(context: vscode.ExtensionContext) {
    // Load AI rules
    try {
        const homeDir = require('os').homedir();
        const startupScript = path.join(homeDir, '.ai_agent_startup.sh');
        
        execSync(`source ${startupScript}`, { cwd: homeDir });
        console.log('AI rules loaded successfully');
    } catch (error) {
        console.error('Failed to load AI rules:', error);
    }
    
    // Your extension code here
}
```

### 4. Docker Integration

For containerized AI agents:

```dockerfile
FROM python:3.9

# Copy AI rules (if they exist in build context)
COPY .ai_agent_rules /root/.ai_agent_rules
COPY .ai_agent_startup.sh /root/.ai_agent_startup.sh
COPY .ai_rules_integration.py /root/.ai_rules_integration.py

# Set up environment
ENV AI_AUTO_STARTUP=true
ENV AI_RULES_ACTIVE=true

# Your application code
COPY . /app
WORKDIR /app

# Run with AI rules
CMD ["bash", "-c", "source ~/.ai_agent_startup.sh && python your_agent.py"]
```

## Agent-Specific Configurations

### OpenCode Integration

OpenCode already has built-in safety features, but you can enhance it:

```bash
# In OpenCode configuration
export AI_AGENT_TYPE="opencode"
export AI_AGENT_CAPABILITIES="code_analysis,automated_refactoring,documentation"

# Load enhanced rules
source ~/.ai_agent_startup.sh
```

### Cursor Integration

```bash
# Cursor-specific setup
export AI_AGENT_TYPE="cursor"
export AI_AGENT_CAPABILITIES="ai_coding,code_generation,file_operations"

# Load rules with Cursor-specific validation
source ~/.ai_agent_startup.sh
```

### Claude Desktop Integration

```bash
# Claude desktop integration
export AI_AGENT_TYPE="claude"
export AI_AGENT_CAPABILITIES="conversation,code_assistance,analysis"

# Load rules
source ~/.ai_agent_startup.sh
```

## Custom Rules for Specific Agents

Create agent-specific rule files:

```bash
# Create directory for agent-specific rules
mkdir -p ~/.ai_agent_rules.d

# Create agent-specific rules file
cat > ~/.ai_agent_rules.d/my_agent.rules << 'EOF'
#!/bin/bash
# Custom rules for my_agent

# Agent-specific validation
my_agent_validate() {
    local operation="$1"
    local target="$2"
    
    # Custom validation logic
    case "$operation" in
        "deploy")
            if [[ ! "$target" =~ ^/home/user/safe_deploy/ ]]; then
                echo "🚫 Deployment only allowed in safe directory"
                return 1
            fi
            ;;
        "api_call")
            if [[ "$target" =~ (delete|drop|truncate) ]]; then
                echo "🚫 Destructive API calls not allowed"
                return 1
            fi
            ;;
    esac
    
    return 0
}

# Hook into main validation
ai_validate_operation() {
    # Run custom validation first
    if ! my_agent_validate "$1" "$2"; then
        return 1
    fi
    
    # Then run standard validation
    # (This would call the original ai_validate_operation)
    return 0
}
EOF
```

## Monitoring and Compliance

### Check Compliance Status

```bash
# Check current compliance
show_compliance_status

# Generate detailed report
create_compliance_report

# View AI rules
ai_show_rules
```

### Python Compliance Check

```python
from ai_rules_integration import check_compliance

# Get compliance status
status = check_compliance()
print(f"Rules Active: {status['rules_active']}")
print(f"Agent Name: {status['agent_name']}")
```

### Log Monitoring

Monitor AI agent operations:

```bash
# View recent AI operations
tail -f ~/logs/ai_rules_enforcement.log

# View startup logs
tail -f ~/logs/ai_agent_startup.log

# Filter by specific agent
grep "my_agent" ~/logs/ai_rules_enforcement.log
```

## Environment Variables

### Core Variables

- `AI_RULES_ACTIVE`: Boolean indicating if rules are loaded
- `AI_AGENT_NAME`: Name of the current AI agent
- `AI_SESSION_ID`: Unique session identifier
- `AI_RULES_VERSION`: Version of the rules system
- `AI_AGENT_TYPE`: Type of AI agent (vscode, cursor, etc.)
- `AI_AGENT_CAPABILITIES`: Capabilities of the agent

### Configuration Variables

- `AI_AUTO_STARTUP`: Automatically load rules on shell startup (default: true)
- `AI_AUTO_LOAD_RULES`: Automatically load rules when agents detected (default: true)
- `AI_RULES_FILE`: Path to the main rules file (default: ~/.ai_agent_rules)

## Troubleshooting

### Common Issues

1. **Rules not loading**
   ```bash
   # Check if rules file exists
   ls -la ~/.ai_agent_rules
   
   # Check permissions
   chmod 644 ~/.ai_agent_rules
   
   # Manually load rules
   source ~/.ai_agent_startup.sh
   ```

2. **Agent not detected**
   ```bash
   # Check detection
   detect_current_agent
   
   # Manually specify agent type
   export AI_AGENT_NAME="my_custom_agent"
   source ~/.ai_agent_startup.sh
   ```

3. **Python import errors**
   ```python
   # Check if integration file exists
   from pathlib import Path
   integration_file = Path.home() / ".ai_rules_integration.py"
   print(integration_file.exists())
   ```

### Debug Mode

Enable debug logging:

```bash
export AI_DEBUG=true
source ~/.ai_agent_startup.sh
```

### Reset Rules

Reset AI rules system:

```bash
# Unset all AI variables
unset $(env | grep '^AI_' | cut -d= -f1)

# Reload
source ~/.ai_agent_startup.sh
```

## Best Practices

1. **Always load rules first**: Load AI rules before any other operations
2. **Validate all operations**: Use validation functions before file operations
3. **Log everything**: Use the logging functions for audit trails
4. **Test compliance**: Regularly check compliance status
5. **Update rules**: Keep rules updated with new safety requirements
6. **Monitor logs**: Regularly review operation logs for anomalies

## Examples

### Example 1: File Processing Agent

```python
from ai_rules_integration import AIAgent

class FileProcessor(AIAgent):
    def __init__(self):
        super().__init__("file_processor")
    
    def process_file(self, file_path):
        # Validate before processing
        if not self.validate_operation("read", file_path):
            raise Exception(f"Cannot read {file_path} - violates AI rules")
        
        # Log the operation
        self.log_action("file_processing", {"file": file_path})
        
        # Process the file safely
        with open(file_path, 'r') as f:
            content = f.read()
        
        return content
```

### Example 2: Shell Script Agent

```bash
#!/bin/bash

# Load AI rules
source ~/.ai_agent_startup.sh

# Safe file operations
safe_read() {
    local file="$1"
    if ai_validate_operation "read" "$file"; then
        cat "$file"
    else
        echo "Cannot read $file - blocked by AI rules"
        return 1
    fi
}

# Safe write operations
safe_write() {
    local file="$1"
    local content="$2"
    
    if ai_validate_operation "write" "$file"; then
        echo "$content" > "$file"
        echo "Successfully wrote to $file"
    else
        echo "Cannot write to $file - blocked by AI rules"
        return 1
    fi
}

# Usage
safe_read "/home/user/safe_file.txt"
safe_write "/home/user/output.txt" "Hello, World!"
```

This integration system ensures that all AI agents in your environment automatically comply with your safety rules and operational constraints.