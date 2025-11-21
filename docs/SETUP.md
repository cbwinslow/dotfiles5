# Setup Guide

## Overview

This guide will help you set up the complete YADM dotfiles configuration on your system. The setup process involves cloning the repository, running the bootstrap script, and configuring your environment.

## Prerequisites

### System Requirements
- **Operating System**: Linux (Ubuntu, Fedora, Arch, or similar)
- **Shell**: Zsh (recommended) or Bash
- **Git**: Version 2.0 or higher
- **GPG**: For encrypted file access
- **Ansible**: For automated deployment (optional)

### Required Tools
```bash
# Install basic requirements
sudo apt update && sudo apt install -y git curl gnupg2 ansible

# Or on Fedora
sudo dnf install -y git curl gnupg2 ansible

# Or on Arch
sudo pacman -S git curl gnupg ansible
```

## Installation Methods

### Method 1: Direct Bootstrap (Recommended)

This is the fastest and easiest method to get started:

```bash
curl -sSL https://gitlab.com/cbwinslow/dotfiles5/-/raw/backup-20251113/yadm-bootstrap.sh | bash
```

**What this does:**
- Downloads and runs the bootstrap script
- Sets up YADM repository
- Configures shell environment
- Creates necessary directories
- Sets proper permissions

### Method 2: Manual Clone

For more control over the setup process:

```bash
# Clone the repository
git clone https://gitlab.com/cbwinslow/dotfiles5.git ~/.local/share/yadm/repo.git

# Run bootstrap
cd ~ && ~/.local/share/yadm/repo.git/yadm-bootstrap.sh
```

### Method 3: GitHub Clone (Public Only)

If you only need the public configuration:

```bash
# Clone GitHub repository
git clone https://github.com/cbwinslow/dotfiles5.git
cd dotfiles5

# Run bootstrap
./yadm-bootstrap.sh
```

## Post-Installation Setup

### 1. Decrypt Sensitive Files

If you have access to the encrypted archive:

```bash
# Decrypt sensitive configuration
~/.config/yadm/decrypt-config.sh

# Or manually
yadm decrypt
```

### 2. Configure Shell

Restart your shell or source the configuration:

```bash
# Source Zsh configuration
source ~/.zshrc

# Or Bash
source ~/.bashrc
```

### 3. Verify Installation

Check that everything is working:

```bash
# Check YADM status
yadm status

# Check Ansible playbooks
ls -la ansible-environment/playbooks/

# Test scripts
./scripts/ansible-validate.sh
```

## Ansible Deployment

### Quick Start

Deploy the complete environment with Ansible:

```bash
# Run complete setup
./scripts/ansible-deploy.sh

# Or install specific components
./scripts/ansible-install-apps.sh
```

### Manual Ansible Usage

```bash
# Run specific playbook
ansible-playbook -i ansible-environment/inventory/hosts ansible-environment/playbooks/dev-environment.yml

# Run with custom variables
ansible-playbook -i ansible-environment/inventory/hosts ansible-environment/site.yml -e "python_dev=true"
```

## Configuration

### Environment Variables

Key environment variables you can set:

```bash
# Development environment
export DEV_ENVIRONMENT=true
export AI_TOOLS_ENABLED=true

# Repository settings
export GITHUB_REPO="git@github.com:yourusername/dotfiles5.git"
export GITLAB_REPO="git@gitlab.com:yourusername/dotfiles5.git"
```

### Customization

#### Adding New Configurations

1. Create configuration files in appropriate directories
2. Add to YADM tracking: `yadm add ~/.config/new-app/config`
3. Commit changes: `yadm commit -m "Add new app configuration"`

#### Modifying Playbooks

1. Edit playbooks in `ansible-environment/playbooks/`
2. Test syntax: `ansible-playbook --syntax-check playbook.yml`
3. Validate: `./scripts/ansible-validate.sh`

## Troubleshooting

### Common Issues

#### Bootstrap Fails
```bash
# Check GPG setup
gpg --list-secret-keys

# Check YADM installation
which yadm

# Check permissions
ls -la ~/.local/share/
```

#### Permission Errors
```bash
# Fix directory permissions
chmod 700 ~/.ssh ~/.gnupg
chmod 755 ~/.local/bin ~/.local/share
```

#### Ansible Errors
```bash
# Check Ansible version
ansible --version

# Validate playbooks
./scripts/ansible-validate.sh

# Check inventory
ansible-inventory -i ansible-environment/inventory/hosts --list
```

### Getting Help

1. Check the [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Review [Common Issues](COMMON_ISSUES.md)
3. Open an [Issue](https://github.com/cbwinslow/dotfiles5/issues)
4. Join [Discussions](https://github.com/cbwinslow/dotfiles5/discussions)

## Next Steps

After successful setup:

1. **Explore Configuration**: Browse through the installed configurations
2. **Customize**: Modify settings to match your preferences
3. **Test Tools**: Try out the various development tools
4. **Set Up Sync**: Configure repository synchronization
5. **Contribute**: Consider contributing back to the project

## Security Considerations

- **Never commit unencrypted secrets** to public repositories
- **Use GPG encryption** for sensitive configuration
- **Review permissions** on security-critical files
- **Regular updates** for security patches
- **Backup regularly** using provided scripts

## Performance Tips

- **Use SSD storage** for better performance
- **Regular cleanup** of temporary files
- **Monitor resources** with system tools
- **Optimize shell startup** by reviewing configurations

---

**Need help?** Check the [documentation](README.md#documentation) or open an issue.