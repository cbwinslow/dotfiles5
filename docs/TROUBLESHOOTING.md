# Troubleshooting Guide

## Overview

This guide provides solutions to common issues encountered with YADM dotfiles configuration system.

## Table of Contents

- [Installation Issues](#installation-issues)
- [YADM Problems](#yadm-problems)
- [Ansible Issues](#ansible-issues)
- [Shell Configuration Issues](#shell-configuration-issues)
- [Synchronization Issues](#synchronization-issues)
- [Permission Issues](#permission-issues)
- [Performance Issues](#performance-issues)
- [Getting Help](#getting-help)

## Installation Issues

### Problem: Bootstrap Script Fails

**Symptoms:**
- Script exits with error
- YADM repository not found
- Permission denied errors

**Solutions:**

#### Check Network Connection
```bash
# Test internet connectivity
curl -I https://gitlab.com

# Test DNS resolution
nslookup gitlab.com

# Try alternative mirror
curl -I https://github.com/cbwinslow/dotfiles5
```

#### Verify Script Integrity
```bash
# Download script manually
curl -o yadm-bootstrap.sh https://gitlab.com/cbwinslow/dotfiles5/-/raw/backup-20251113/yadm-bootstrap.sh

# Check script permissions
chmod +x yadm-bootstrap.sh

# Run with debug output
bash -x yadm-bootstrap.sh
```

#### Check Prerequisites
```bash
# Verify required tools
which git curl gnupg2

# Check system compatibility
uname -a
# Should support Linux with glibc 2.17+

# Check disk space
df -h
# Need at least 1GB free space
```

### Problem: Repository Clone Fails

**Symptoms:**
- Authentication errors
- Repository not found
- SSL/TLS errors

**Solutions:**

#### SSH Key Issues
```bash
# Check SSH key configuration
ssh -T git@gitlab.com
ssh -T git@github.com

# Add SSH key to agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_rsa

# Test SSH connection
ssh -vT git@gitlab.com
```

#### HTTPS Authentication
```bash
# Use personal access token
export GIT_TOKEN="your_token_here"

# Clone with token
git clone https://oauth2:${GIT_TOKEN}@gitlab.com/cbwinslow/dotfiles5.git

# Or configure credential helper
git config --global credential.helper store
```

## YADM Problems

### Problem: YADM Commands Not Found

**Symptoms:**
- `yadm: command not found`
- Permission denied on yadm commands
- YADM not working after shell restart

**Solutions:**

#### Install/Update YADM
```bash
# Install YADM
curl -fLo https://yadm.io/install | bash

# Or via package manager
sudo apt install yadm
sudo dnf install yadm
sudo pacman -S yadm

# Check YADM version
yadm version
# Should be 3.2.0 or higher
```

#### Check YADM Configuration
```bash
# Check YADM repository status
yadm status

# Verify YADM configuration
cat ~/.config/yadm/config

# Check YADM aliases
yadm config --list

# Manual YADM operations
yadm fetch origin
yadm checkout main
```

### Problem: Encrypted Files Not Accessible

**Symptoms:**
- Cannot decrypt sensitive files
- GPG passphrase prompts
- Encrypted files missing

**Solutions:**

#### Check GPG Setup
```bash
# List GPG keys
gpg --list-secret-keys

# Check GPG agent
gpg --card-status

# Test GPG encryption
echo "test" | gpg --symmetric --output test.gpg
gpg --decrypt test.gpg

# Clean up test files
rm test.gpg
```

#### YADM Encryption Issues
```bash
# Check encrypted files list
yadm encrypt -l

# Manually decrypt file
yadm decrypt ~/.ssh/id_rsa

# Re-encrypt problematic file
yadm encrypt ~/.ssh/id_rsa
```

## Ansible Issues

### Problem: Playbook Execution Fails

**Symptoms:**
- Syntax errors in YAML files
- Connection refused to localhost
- Task execution failures

**Solutions:**

#### YAML Syntax Validation
```bash
# Install yamllint
pip install yamllint

# Validate all YAML files
find ansible-environment -name "*.yml" -exec yamllint {} \;

# Check specific file
yamllint ansible-environment/playbooks/problem-playbook.yml
```

#### Ansible Connection Issues
```bash
# Check Ansible version
ansible --version
# Should be 2.14.0 or higher

# Test local connection
ansible localhost -m ping

# Check inventory file
ansible-inventory -i ansible-environment/inventory/hosts --list

# Run with verbose output
ansible-playbook -i ansible-environment/inventory/hosts playbook.yml -vvv
```

#### Python/Dependency Issues
```bash
# Check Ansible Python dependencies
pip list | grep -E "(ansible|jinja2|cryptography)"

# Update Ansible dependencies
pip install --upgrade ansible jinja2 cryptography

# Check Python path
which python3
python3 --version
```

### Problem: Permission Denied Errors

**Symptoms:**
- `sudo: password required`
- Permission denied on files
- Unable to write to system directories

**Solutions:**

#### Fix System Permissions
```bash
# Check current user
whoami
groups

# Add user to required groups
sudo usermod -aG sudo,docker,adm $USER

# Fix directory permissions
sudo chown -R $USER:$USER ~/.local
sudo chmod -R 755 ~/.local

# Fix script permissions
chmod +x scripts/*.sh
```

#### Configure Passwordless Sudo
```bash
# Add sudoers entry
echo "$USER ALL=(ALL) NOPASSWD: /usr/bin/apt, /usr/bin/dnf, /usr/bin/pacman" | sudo tee /etc/sudoers.d/$USER

# Test passwordless sudo
sudo -n true
```

## Shell Configuration Issues

### Problem: Shell Not Loading Configuration

**Symptoms:**
- Aliases not working
- Functions not found
- Custom prompt not showing

**Solutions:**

#### Check Shell Configuration
```bash
# Check current shell
echo $SHELL

# Check if Zsh is running
if [ -n "$ZSH_VERSION" ]; then
    echo "Zsh is active"
else
    echo "Not running Zsh"
fi

# Check configuration files
ls -la ~/.zshrc ~/.bashrc ~/.zshenv

# Test configuration loading
zsh -c 'echo $ZSH_VERSION'
bash -c 'echo $BASH_VERSION'
```

#### Fix Shell Startup Issues
```bash
# Source configuration manually
source ~/.zshrc

# Check for syntax errors
zsh -n ~/.zshrc

# Debug shell startup
zsh -x -c 'echo "Debug mode"'

# Check shell logs
tail -f ~/.zshrc.log
```

### Problem: Terminal/Display Issues

**Symptoms:**
- Colors not displaying correctly
- Unicode characters showing as squares
- Terminal performance issues

**Solutions:**

#### Fix Terminal Issues
```bash
# Check terminal type
echo $TERM

# Check locale settings
locale

# Set proper terminal type
export TERM=xterm-256color

# Fix locale issues
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# Test terminal capabilities
tput colors
infocmp $TERM
```

## Synchronization Issues

### Problem: Git Push/Pull Fails

**Symptoms:**
- Authentication failures
- Merge conflicts
- Network timeouts

**Solutions:**

#### Fix Authentication Issues
```bash
# Check Git configuration
git config --list

# Configure user name and email
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Configure credential helper
git config --global credential.helper store

# Test authentication
git config --global credential.helper
```

#### Resolve Merge Conflicts
```bash
# Check for conflicts
git status

# Stash local changes
git stash push -m "Local changes"

# Pull remote changes
git pull origin main

# Apply stashed changes
git stash pop

# Resolve conflicts manually
git mergetool

# Mark conflicts as resolved
git add .
git commit -m "fix: resolve merge conflicts"
```

#### Network Issues
```bash
# Test connectivity
ping -c 3 gitlab.com
ping -c 3 github.com

# Check DNS resolution
nslookup gitlab.com
nslookup github.com

# Use different protocol
git config --global url."https://gitlab.com".insteadOf "git@gitlab.com:"
```

## Permission Issues

### Problem: File Permission Errors

**Symptoms:**
- Permission denied on configuration files
- Cannot execute scripts
- SSH key permission errors

**Solutions:**

#### Fix File Permissions
```bash
# Fix SSH permissions
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub

# Fix GPG permissions
chmod 700 ~/.gnupg
chmod 600 ~/.gnupg/private-keys*

# Fix configuration permissions
chmod 755 ~/.config
chmod 644 ~/.config/*

# Fix script permissions
chmod +x scripts/*.sh
chmod +x ~/.local/bin/*
```

#### Fix Directory Permissions
```bash
# Create directories with correct permissions
mkdir -m 700 ~/.ssh ~/.gnupg
mkdir -m 755 ~/.local/bin ~/.local/share

# Fix ownership
sudo chown -R $USER:$USER ~/.local ~/.config

# Check current permissions
ls -la ~/.ssh ~/.gnupg ~/.config
```

## Performance Issues

### Problem: Slow Shell Startup

**Symptoms:**
- Shell takes long time to load
- High CPU usage during startup
- Memory usage issues

**Solutions:**

#### Optimize Shell Performance
```bash
# Profile shell startup
time zsh -i -c 'exit'

# Check shell configuration size
wc -l ~/.zshrc ~/.bashrc

# Disable slow features
# Comment out resource-intensive plugins
# Reduce function complexity

# Use shell profiling
zsh -c 'zmodload zsh/datetime; autoload -Uz zsh/datetime'
```

#### Optimize System Performance
```bash
# Check system resources
htop
iotop
free -h

# Clean up temporary files
find /tmp -type f -mtime +7 -delete

# Optimize package cache
sudo apt clean
sudo dnf clean all
sudo pacman -Scc
```

### Problem: High Memory Usage

**Symptoms:**
- System becomes unresponsive
- Out of memory errors
- Swap usage high

**Solutions:**

#### Monitor and Reduce Memory Usage
```bash
# Check memory usage
free -h
cat /proc/meminfo

# Find memory-intensive processes
ps aux --sort=-%mem | head -10

# Check for memory leaks
valgrind --tool=memcheck program_name

# Optimize memory usage
echo 1 > /proc/sys/vm/drop_caches
echo 2 > /proc/sys/vm/drop_caches
```

## Getting Help

### Self-Service Resources

#### Check Documentation
```bash
# Read main documentation
cat README.md

# Check usage guide
cat docs/USAGE.md

# Review examples
cat docs/EXAMPLES.md
```

#### Validate Configuration
```bash
# Run validation script
./scripts/ansible-validate.sh

# Check YADM status
yadm status

# Test scripts
./scripts/ansible-deploy.sh --dry-run
```

### Community Support

#### GitHub Issues
```bash
# Check existing issues
curl https://api.github.com/repos/cbwinslow/dotfiles5/issues

# Search issues
curl "https://api.github.com/search/issues?q=repo:cbwinslow/dotfiles5+problem"

# Create new issue
gh issue create \
  --title "Problem Description" \
  --body "Detailed description of the issue"
```

#### GitLab Issues
```bash
# Check GitLab issues
curl https://gitlab.com/api/v4/projects/cbwinslow%2Fdotfiles5/issues

# Search for solutions
curl "https://gitlab.com/api/v4/projects/cbwinslow%2Fdotfiles5/issues?search=problem"
```

### Debug Information Collection

#### Generate System Report
```bash
# Create system information script
cat > system-report.sh << 'EOF'
#!/bin/bash
echo "=== System Information ==="
echo "Date: $(date)"
echo "Uname: $(uname -a)"
echo "Memory: $(free -h)"
echo "Disk: $(df -h)"
echo "Git: $(git --version)"
echo "Ansible: $(ansible --version)"
echo "YADM: $(yadm version)"
echo "Shell: $SHELL"
echo "=== End Report ==="
EOF

chmod +x system-report.sh
./system-report.sh > system-info.txt

# Include system info when asking for help
cat system-info.txt
```

#### Enable Debug Mode
```bash
# Enable shell debug
set -x

# Enable Ansible debug
export ANSIBLE_DEBUG=1
export ANSIBLE_VERBOSITY=2

# Enable YADM debug
export YADM_TRACE=1

# Run with debug output
./scripts/ansible-deploy.sh 2>&1 | tee deploy-debug.log
```

---

**Still having issues?** Please provide:

1. **System Information**: OS version, shell, YADM/Ansible versions
2. **Error Messages**: Complete error output, not just summaries
3. **Steps Taken**: What you tried before the problem occurred
4. **Expected Behavior**: What you expected to happen

**Contact Options:**
- [GitHub Issues](https://github.com/cbwinslow/dotfiles5/issues)
- [GitLab Issues](https://gitlab.com/cbwinslow/dotfiles5/-/issues)
- [Discussions](https://github.com/cbwinslow/dotfiles5/discussions)