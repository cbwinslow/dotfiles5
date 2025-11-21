# AI Agents Repository Access Instructions

## Overview
This repository contains a complete master configuration managed by YADM with encrypted sensitive data.

## Repository Structure
- **YADM-managed files**: All configuration, scripts, tools
- **Encrypted archive**: `.yadm-archive` contains sensitive data
- **Bootstrap script**: `yadm-bootstrap.sh` for full restoration

## Access Instructions for AI Agents

### 1. Clone/Bootstrap Repository
```bash
# Method 1: Direct bootstrap (recommended)
curl -sSL https://gitlab.com/cbwinslow/dotfiles5/-/raw/backup-20251113/yadm-bootstrap.sh | bash

# Method 2: Manual clone
git clone https://gitlab.com/cbwinslow/dotfiles5.git ~/.local/share/yadm/repo.git
cd ~ && ~/.local/share/yadm/repo.git/yadm-bootstrap.sh
```

### 2. Decrypt Sensitive Files
```bash
# After bootstrap, decrypt sensitive configuration
~/.config/yadm/decrypt-config.sh

# Or manually if archive exists
yadm decrypt
```

### 3. Configuration Access
- **Shell configs**: `.zshrc`, `.bashrc`, `.zshenv`
- **Tools**: `tools/`, `scripts/`, `toolsets/`
- **AI configs**: `mcp-servers/`, `.ai_agent_rules`
- **Development**: `dot_*/` directories
- **Security**: `.ssh/`, `.gnupg/`, `private_dot_*/`

## Security Notes
- Sensitive files are encrypted in `.yadm-archive`
- Decryption requires proper GPG setup
- Never commit unencrypted secrets
- Use provided encryption/decryption scripts

## AI Agent Integration
The configuration includes:
- MCP servers for file operations, web research
- AI agent configurations and crews
- Development toolsets and automation
- Warning systems and monitoring

## Support
- Bootstrap script handles full restoration
- Encryption scripts secure sensitive data
- All configurations are versioned and tracked