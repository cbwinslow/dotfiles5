# Complete YADM Dotfiles Configuration

[![YADM](https://img.shields.io/badge/YADM-Managed-blue?style=for-the-badge)](https://yadm.io/)
[![Ansible](https://img.shields.io/badge/Ansible-Automated-red?style=for-the-badge)](https://ansible.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

> 🚀 **Complete YADM-managed dotfiles configuration with Ansible automation, AI agents, and development tools**

## 📋 Overview

This repository contains a comprehensive master configuration system managed by YADM (Yet Another Dotfiles Manager) with encrypted sensitive data, automated deployment via Ansible, and extensive AI/development tooling.

### ✨ Key Features

- 🔐 **YADM Management**: 3,787+ files managed with encrypted sensitive data
- 🤖 **Ansible Automation**: Complete environment setup with 8+ specialized playbooks
- 🛠️ **Development Tools**: Comprehensive toolsets for multiple languages and frameworks
- 🤖 **AI Agents**: 8+ AI coding agents and frameworks configured
- 🔄 **Dual Repository Strategy**: GitHub (public) + GitLab (private/sensitive)
- 📚 **Extensive Documentation**: Complete setup guides and troubleshooting

## 🏗️ Repository Structure

```
├── yadm-bootstrap.sh              # Master bootstrap script
├── AGENTS.md                     # AI agent access instructions
├── ansible-environment/           # Complete Ansible setup
│   ├── site.yml                  # Master playbook
│   ├── playbooks/                # 8 specialized playbooks
│   ├── inventory/                # Host configurations
│   └── group_vars/               # Global variables
├── scripts/                      # Deployment & utility scripts
│   ├── ansible-deploy.sh          # Environment deployment
│   ├── ansible-install-apps.sh     # Application installer
│   └── ansible-validate.sh        # Configuration validator
├── tools/                        # Development tools and utilities
├── dot_*/                        # Application-specific configs
└── .yadm-archive                  # Encrypted sensitive data
```

## 🚀 Quick Start

### Method 1: Direct Bootstrap (Recommended)
```bash
curl -sSL https://gitlab.com/cbwinslow/dotfiles5/-/raw/backup-20251113/yadm-bootstrap.sh | bash
```

### Method 2: Manual Clone
```bash
# Clone GitLab repository (contains sensitive data)
git clone https://gitlab.com/cbwinslow/dotfiles5.git ~/.local/share/yadm/repo.git
cd ~ && ~/.local/share/yadm/repo.git/yadm-bootstrap.sh

# Or clone GitHub repository (public only)
git clone https://github.com/cbwinslow/dotfiles5.git
cd dotfiles5 && ./yadm-bootstrap.sh
```

### Method 3: Ansible Deployment
```bash
# Deploy complete environment
./scripts/ansible-deploy.sh

# Install applications only
./scripts/ansible-install-apps.sh

# Validate configuration
./scripts/ansible-validate.sh
```

## 🔄 Dual Repository Strategy

### 🌐 GitHub Repository (Public)
- **Purpose**: Public access, CI/CD, documentation
- **Content**: Configuration files, scripts, documentation, automation
- **Features**: GitHub Actions, issue tracking, community contributions

### 🔒 GitLab Repository (Private)
- **Purpose**: Private backup, encrypted sensitive data
- **Content**: Encrypted archive, personal configs, secrets
- **Features**: Enhanced security, private CI/CD, encrypted storage

### 🔄 Synchronization
```bash
# Sync from GitHub to GitLab
./scripts/sync-to-gitlab.sh

# Sync from GitLab to GitHub  
./scripts/sync-to-github.sh

# Full bidirectional sync
./scripts/sync-repos.sh
```

## 🛠️ Ansible Environment

### Available Playbooks
- `master-setup.yml` - Core system configuration
- `dev-environment.yml` - Development tools setup
- `security-setup.yml` - Security and encryption
- `ai-tools.yml` - AI agents and frameworks
- `shell-setup.yml` - Shell and terminal configuration
- `package-managers.yml` - Package manager installation
- `applications.yml` - Flatpak/Snap applications
- `docker-setup.yml` - Docker and containers

### Usage Examples
```bash
# Run complete setup
ansible-playbook -i ansible-environment/inventory/hosts ansible-environment/site.yml

# Run specific playbook
ansible-playbook -i ansible-environment/inventory/hosts ansible-environment/playbooks/dev-environment.yml

# Install applications only
ansible-playbook -i ansible-environment/inventory/hosts ansible-environment/playbooks/applications.yml
```

## 🤖 AI Agents & Tools

### Configured Agents
- **OpenCode**: Interactive CLI coding assistant
- **Claude**: Advanced reasoning and analysis
- **Cursor**: IDE-integrated coding
- **Continue**: Pair programming assistant
- **CodeGPT**: Code generation and review
- **Cline**: Autonomous development
- **CodeX**: Multi-language support
- **Jitera**: Workflow automation

### MCP Servers
- File operations and management
- Web research and documentation
- Database operations
- Vector search capabilities
- Browser automation

## 🔧 Development Tools

### Languages & Frameworks
- **Python**: Complete development environment with virtualenv
- **Node.js**: NVM, npm, yarn configuration
- **Go**: Go development tools and GOPATH setup
- **Rust**: Rust toolchain and Cargo configuration
- **Java**: JDK, Maven, Gradle setup
- **Docker**: Complete container development environment

### Tools & Utilities
- **Git**: Advanced configuration with aliases and hooks
- **Tmux**: Terminal multiplexer configuration
- **Vim/Neovim**: Complete editor configuration
- **Zsh**: Advanced shell with plugins and themes
- **Security**: GPG, SSH, password manager setup

## 📁 Configuration Areas

### Shell Configuration
- `.zshrc` - Zsh configuration with plugins
- `.bashrc` - Bash configuration
- `.zshenv` - Environment variables
- `.zsh_aliases.d/` - Organized aliases
- `.zsh_functions.d/` - Custom functions

### Application Configs
- `dot_git/` - Git configuration
- `dot_docker/` - Docker settings
- `dot_vscode/` - VS Code configuration
- `dot_ollama/` - Local AI setup
- `dot_claude/` - Claude configuration

### Security & Privacy
- `.ssh/` - SSH keys and configuration
- `.gnupg/` - GPG keys and setup
- `private_dot_*/` - Encrypted private configs
- `.yadm-archive` - Encrypted sensitive data

## 🔐 Security Features

### Encryption
- **YADM Encryption**: Sensitive files encrypted in `.yadm-archive`
- **GPG Integration**: Full GPG setup for signing and encryption
- **SSH Security**: Secure SSH configuration with key management
- **Password Management**: Integration with password managers

### Access Control
- **Permission Management**: Proper file permissions set automatically
- **Key Security**: Secure key storage and rotation
- **Audit Logging**: Security events logged and monitored

## 📚 Documentation

### Setup Guides
- [Initial Setup Guide](docs/SETUP.md)
- [Security Configuration](docs/SECURITY.md)
- [AI Agent Setup](docs/AI_AGENTS.md)
- [Ansible Playbook Guide](docs/ANSIBLE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

### API References
- [YADM Commands](docs/YADM_COMMANDS.md)
- [Ansible Playbooks](docs/ANSIBLE_PLAYBOOKS.md)
- [Script Reference](docs/SCRIPTS.md)
- [Configuration Reference](docs/CONFIGURATION.md)

## 🔄 CI/CD Integration

### GitHub Actions
- **Validation**: Automatic configuration validation
- **Testing**: Bootstrap process testing
- **Security**: Security scan and vulnerability check
- **Deployment**: Automated deployment to staging

### GitLab CI/CD
- **Private Pipeline**: Secure pipeline for sensitive operations
- **Encryption**: Automatic encryption of sensitive artifacts
- **Backup**: Automated backup to secure storage
- **Monitoring**: Continuous monitoring and alerting

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Guidelines
- Follow conventional commit format
- Add tests for new features
- Update documentation
- Ensure security best practices
- Test on fresh systems

## 🐛 Troubleshooting

### Common Issues
- **Bootstrap Fails**: Check GPG setup and permissions
- **Ansible Errors**: Verify inventory and variables
- **Sync Issues**: Check repository permissions and SSH keys
- **Encryption Problems**: Ensure YADM encryption is properly configured

### Getting Help
- Check [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
- Review [Common Issues](docs/COMMON_ISSUES.md)
- Open an [Issue](https://github.com/cbwinslow/dotfiles5/issues)
- Join our [Discussions](https://github.com/cbwinslow/dotfiles5/discussions)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **YADM**: Excellent dotfiles management tool
- **Ansible**: Powerful automation framework
- **GitHub/GitLab**: Reliable hosting platforms
- **Open Source Community**: Inspiration and contributions

## 📊 Statistics

- **Files Managed**: 3,787+ configuration files
- **Ansible Playbooks**: 8 specialized playbooks
- **AI Agents**: 8+ configured agents
- **Tools Included**: 50+ development tools
- **Documentation**: 15+ comprehensive guides

---

<div align="center">

**🚀 Ready to transform your development environment?**

[![Quick Start](https://img.shields.io/badge/Quick_Start-Ready-brightgreen?style=for-the-badge)](#quick-start)
[![Documentation](https://img.shields.io/badge/Documentation-Complete-blue?style=for-the-badge)](#documentation)
[![Get Started](https://img.shields.io/badge/Get_Started-Now-orange?style=for-the-badge)](#quick-start)

</div>