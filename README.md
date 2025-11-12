# CBW Agents

Comprehensive collection of AI agent configurations, tools, and rules for building intelligent automation systems.

## 📁 Repository Structure

```
cbw-agents/
├── rules/                    # AI agent rules and guidelines
│   ├── README.md            # Rules overview and navigation
│   ├── RULES_INDEX.md       # Complete rule index and quick reference
│   ├── security_privacy_rules.md
│   ├── memory_management_rules.md
│   ├── code_quality_rules.md
│   ├── communication_rules.md
│   ├── error_handling_rules.md
│   ├── testing_quality_rules.md
│   ├── performance_rules.md
│   └── documentation_rules.md
├── tools/                    # Individual agent tools and utilities
│   ├── README.md            # Tools documentation and usage
│   ├── file_operations.py   # File system operations tool
│   ├── web_operations.py    # Web scraping and API tool
│   ├── data_processing.py   # Data analysis and processing tool
│   └── code_analysis.py    # Static code analysis tool
├── toolsets/                 # Combined toolsets for specific workflows
│   ├── README.md            # Toolsets documentation
│   ├── web_research.py      # Web research toolset
│   └── code_development.py # Code development toolset
├── agents/                   # Individual agent configurations
│   ├── README.md            # Agent documentation
│   ├── web_research_agent.json
│   ├── code_analysis_agent.json
│   └── data_processing_agent.json
├── crews/                    # CrewAI crew configurations
│   ├── README.md            # Crew documentation
│   ├── research_analysis_crew.json
│   └── software_development_crew.json
├── mcp-servers/              # MCP server configurations
│   ├── README.md            # MCP server documentation
│   ├── file_operations_server.json
│   └── web_operations_server.json
└── docs/                     # Additional documentation
```

## 🚀 Getting Started

### For AI Agent Developers
1. **Read the Rules First**: Start with `rules/README.md` to understand the guidelines
2. **Check the Rule Index**: Use `rules/RULES_INDEX.md` for quick reference
3. **Follow Priority Guidelines**: Critical rules must be followed, high-priority rules should be followed

### For System Administrators
1. **Review Security Rules**: `rules/security_privacy_rules.md` contains critical security guidelines
2. **Memory Management**: `rules/memory_management_rules.md` for resource optimization
3. **Performance Guidelines**: `rules/performance_rules.md` for system optimization

## 📋 Rule Categories

### 🔒 Critical (Must Follow)
- **Security and Privacy**: Data protection, access control, secure communication
- **Memory Management**: Allocation, cleanup, monitoring, optimization

### ⚡ High Priority (Should Follow)
- **Code Quality**: Testing, documentation, security practices
- **Communication**: Response quality, user experience, professional conduct
- **Error Handling**: Prevention, recovery, resilience patterns
- **Testing**: Coverage, automation, quality gates

### 🚀 Medium Priority (Recommended)
- **Performance**: Response time, resource usage, scalability
- **Documentation**: Standards, knowledge management

## 🛠️ Components

### 🔧 Tools (4 Available)
- **File Operations**: Comprehensive file system operations with safety features
- **Web Operations**: Web scraping, API calls, and data extraction
- **Data Processing**: Data analysis, cleaning, and transformation
- **Code Analysis**: Static code analysis and security scanning

### 🎯 Toolsets (2 Available)
- **Web Research**: Combined web research and data extraction workflow
- **Code Development**: Comprehensive code analysis and development workflow

### 🤖 Agents (3 Available)
- **Web Research Agent**: Specialized for online research and source validation
- **Code Analysis Agent**: Security auditing and code quality assessment
- **Data Processing Agent**: Data analysis and statistical processing

### 👥 Crews (2 Available)
- **Research Analysis Crew**: Multi-agent research and analysis team
- **Software Development Crew**: Code analysis and quality assurance team

### 🔌 MCP Servers (2 Available)
- **File Operations Server**: MCP interface for file system operations
- **Web Operations Server**: MCP interface for web operations and scraping

## 🤝 Contributing

1. Follow all applicable rules when contributing
2. Update documentation for any new tools or agents
3. Test thoroughly before submitting changes
4. Follow the established code quality standards

## 📄 License

This repository contains configurations and guidelines for AI agent development. Please review individual component licenses for specific usage terms.

## 🔗 Related Projects

- [Knowledge-Base](../Knowledge-Base) - Additional documentation and resources
- [MCP Gateway](../mcp-gateway) - MCP server management
- [Agent Configurations](../mcp) - Additional agent setups

---

**Last Updated**: 2025-11-12
**Maintainer**: CBW Development Team