# CloudCurio Monorepo

This is a unified monorepo for all CloudCurio projects, tools, and infrastructure.

## Structure

```
cloudcurio-monorepo/
├── apps/           # Applications and services
├── tools/           # Utility tools and scripts
├── docs/            # Documentation and guides
├── infrastructure/  # Infrastructure as code
├── projects/        # Project-specific code
├── scripts/         # Automation and setup scripts
└── configs/        # Configuration files
```

## Categories

### Apps
- `docbrain/` - Documentation processing MVP
- `cloudcurio-tui/` - Terminal user interface
- `url2md-toolkit/` - URL to Markdown converter

### Tools
- `ai-automation/` - AI automation frameworks (Linear, GitHub, GitLab, Jira)
- `ai-doc-framework/` - Documentation framework for AI projects
- `gemini-cli/` - Gemini CLI tools and extensions
- `openai-agents/` - OpenAI agents and CrewAI bridge
- `automation/` - General automation tools
- `github-sync/` - GitHub repository synchronization
- `networking/` - Network analysis and API tools

### Infrastructure
- `terraform/` - Infrastructure as code
- `ansible/` - Configuration management
- `docker/` - Container configurations

### Projects
- `cbw-master/` - Master project configuration
- `multi-agent/` - Multi-agent systems
- `retail-sleuth/` - Retail analysis platform

### Documentation
- `ai/` - AI and agent documentation
- `development/` - Development guides and patterns
- `tools/` - Tool documentation
- `personal/` - Personal notes and resumes

## Getting Started

Each subdirectory contains its own README with specific setup instructions.

## Repository Status

✅ **Organized**: All files have been extracted from zip archives and organized
✅ **Deduplicated**: Duplicate files have been removed
✅ **Structured**: Clear monorepo structure with logical categorization
✅ **Documented**: README files created for each major category