# Practical Examples

This document provides real-world examples of using the YADM dotfiles configuration system.

## Table of Contents

- [System Setup Examples](#system-setup-examples)
- [Development Workflow Examples](#development-workflow-examples)
- [Configuration Management Examples](#configuration-management-examples)
- [Automation Examples](#automation-examples)
- [Troubleshooting Examples](#troubleshooting-examples)

## System Setup Examples

### Example 1: Fresh System Installation

Setting up a completely new system:

```bash
# 1. Bootstrap the system
curl -sSL https://gitlab.com/cbwinslow/dotfiles5/-/raw/backup-20251113/yadm-bootstrap.sh | bash

# 2. Verify installation
yadm status
# Expected: ✓ 3,787 files managed

# 3. Set up development environment
./scripts/ansible-deploy.sh

# 4. Configure AI tools
./scripts/ansible-install-apps.sh
# Choose option 2) Development Tools
```

### Example 2: Minimal Setup

For users who want only essential components:

```bash
# 1. Clone repository
git clone https://github.com/cbwinslow/dotfiles5.git
cd dotfiles5

# 2. Run bootstrap
./yadm-bootstrap.sh

# 3. Install only shell configuration
ansible-playbook -i ansible-environment/inventory/hosts ansible-environment/playbooks/shell-setup.yml
```

### Example 3: Development Machine Setup

Setting up a development-focused environment:

```bash
# 1. Bootstrap with development focus
curl -sSL https://gitlab.com/cbwinslow/dotfiles5/-/raw/backup-20251113/yadm-bootstrap.sh | bash

# 2. Install development tools
ansible-playbook -i ansible-environment/inventory/hosts ansible-environment/playbooks/dev-environment.yml \
  -e "python_dev=true" \
  -e "nodejs_dev=true" \
  -e "go_dev=true"

# 3. Set up AI tools
ansible-playbook -i ansible-environment/inventory/hosts ansible-environment/playbooks/ai-tools.yml
```

## Development Workflow Examples

### Example 1: Python Project Setup

Creating a new Python project with this configuration:

```bash
# 1. Create project directory
mkdir ~/projects/my-python-app
cd ~/projects/my-python-app

# 2. Initialize virtual environment
python -m venv venv
source venv/bin/activate

# 3. Create project structure
mkdir -p src tests docs
touch src/main.py tests/test_main.py docs/README.md

# 4. Initialize git (if not already done)
git init
git add .
git commit -m "Initial project structure"

# 5. Install dependencies
pip install requests pytest black flake8

# 6. Add to YADM tracking
yadm add ~/projects/my-python-app
yadm commit -m "feat: add Python project"
```

### Example 2: Node.js Project Setup

Setting up a Node.js development environment:

```bash
# 1. Install specific Node.js version
nvm install 18.17.0
nvm use 18.17.0

# 2. Create project
mkdir ~/projects/my-node-app
cd ~/projects/my-node-app

# 3. Initialize project
npm init -y
npm install express typescript @types/node ts-node nodemon

# 4. Create TypeScript configuration
cat > tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "outDir": "./dist",
    "rootDir": "./src"
  }
}
EOF

# 5. Add project to YADM
yadm add ~/projects/my-node-app
yadm commit -m "feat: add Node.js project with TypeScript"
```

### Example 3: Go Project Setup

Setting up a Go development project:

```bash
# 1. Create project directory
mkdir ~/projects/my-go-app
cd ~/projects/my-go-app

# 2. Initialize Go module
go mod init github.com/username/my-go-app

# 3. Create main file
cat > main.go << 'EOF'
package main

import (
    "fmt"
    "net/http"
)

func handler(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintf(w, "Hello, %s!", r.URL.Path[1:])
}

func main() {
    http.HandleFunc("/", handler)
    http.ListenAndServe(":8080", nil)
}
EOF

# 4. Add dependencies and build
go mod tidy
go build -o my-go-app

# 5. Track with YADM
yadm add ~/projects/my-go-app
yadm commit -m "feat: add Go web application"
```

## Configuration Management Examples

### Example 1: Adding New Application

Adding configuration for a new application:

```bash
# 1. Create configuration directory
mkdir -p ~/.config/my-new-app

# 2. Create configuration file
cat > ~/.config/my-new-app/config.conf << 'EOF'
[General]
theme = dark
auto_save = true
backup_interval = 3600

[Network]
timeout = 30
retry_attempts = 3
EOF

# 3. Add to YADM tracking
yadm add ~/.config/my-new-app

# 4. Commit with proper message
yadm commit -m "feat: add my-new-app configuration"

# 5. Sync to repositories
./scripts/sync-repos.sh
```

### Example 2: Custom Shell Configuration

Adding custom shell aliases and functions:

```bash
# 1. Create custom aliases
cat > ~/.zsh_aliases.d/custom-dev.zsh << 'EOF'
# Development aliases
alias gs='git status'
alias gc='git commit'
alias gp='git push'
alias gl='git log --oneline'

# Project navigation
alias pj='cd ~/projects'
alias dot='cd ~/.local/share/yadm/repo.git'

# Docker aliases
alias dps='docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"'
alias di='docker inspect'
alias drm='docker rm -f'
EOF

# 2. Create custom functions
cat > ~/.zsh_functions.d/custom-dev.zsh << 'EOF'
# Project creation function
create_project() {
    if [ -z "$1" ]; then
        echo "Usage: create_project <project_name>"
        return 1
    fi
    
    mkdir -p ~/projects/"$1"
    cd ~/projects/"$1"
    git init
    echo "Created project: $1"
}

# Quick backup function
backup_config() {
    local app_name="$1"
    if [ -z "$app_name" ]; then
        echo "Usage: backup_config <app_name>"
        return 1
    fi
    
    yadm encrypt ~/.config/"$app_name"
    echo "Backed up configuration for: $app_name"
}

# Environment switcher
env_switch() {
    local env="$1"
    case "$env" in
        dev)
            export NODE_ENV=development
            export DEBUG=true
            ;;
        prod)
            export NODE_ENV=production
            export DEBUG=false
            ;;
        *)
            echo "Unknown environment: $env"
            return 1
            ;;
    esac
    echo "Switched to $env environment"
}
EOF

# 3. Apply changes
source ~/.zshrc

# 4. Commit to YADM
yadm add ~/.zsh_aliases.d/custom-dev.zsh ~/.zsh_functions.d/custom-dev.zsh
yadm commit -m "feat: add custom development aliases and functions"
```

### Example 3: Ansible Custom Playbook

Creating a custom Ansible playbook for a specific application:

```yaml
# ansible-environment/playbooks/custom-app.yml
---
- name: Custom Application Setup
  hosts: localhost
  connection: local
  become: true
  vars_files:
    - ../group_vars/all.yml
  
  tasks:
    - name: Install custom application dependencies
      package:
        name:
          - curl
          - wget
          - unzip
        state: present
    
    - name: Create application directory
      file:
        path: /opt/custom-app
        state: directory
        mode: '0755'
    
    - name: Download custom application
      get_url:
        url: https://github.com/user/custom-app/releases/latest/download/custom-app-linux.tar.gz
        dest: /tmp/custom-app.tar.gz
        mode: '0644'
    
    - name: Extract custom application
      unarchive:
        src: /tmp/custom-app.tar.gz
        dest: /opt/custom-app
        remote_src: yes
    
    - name: Create configuration file
      copy:
        content: |
          [Application]
          version = 1.0.0
          auto_update = true
          log_level = info
        dest: /opt/custom-app/config.conf
        mode: '0644'
    
    - name: Create desktop shortcut
      copy:
        content: |
          [Desktop Entry]
          Version=1.0
          Type=Application
          Name=Custom App
          Comment=A custom application
          Exec=/opt/custom-app/bin/custom-app
          Icon=/opt/custom-app/icon.png
          Terminal=false
        dest: ~/.local/share/applications/custom-app.desktop
        mode: '0644'
    
    - name: Set executable permissions
      file:
        path: /opt/custom-app/bin/custom-app
        mode: '0755'
    
    - name: Clean up temporary files
      file:
        path:
          - /tmp/custom-app.tar.gz
        state: absent
```

Running the custom playbook:

```bash
# Validate syntax
ansible-playbook --syntax-check -i ansible-environment/inventory/hosts ansible-environment/playbooks/custom-app.yml

# Execute playbook
ansible-playbook -i ansible-environment/inventory/hosts ansible-environment/playbooks/custom-app.yml

# With custom variables
ansible-playbook -i ansible-environment/inventory/hosts ansible-environment/playbooks/custom-app.yml \
  -e "app_version=2.0.0" \
  -e "install_location=/usr/local"
```

## Automation Examples

### Example 1: Automated Daily Sync

Setting up automated repository synchronization:

```bash
# 1. Create daily sync script
cat > ~/.local/bin/daily-sync.sh << 'EOF'
#!/bin/bash
# Daily repository synchronization

echo "Starting daily sync..."

# Sync to GitLab
~/dotfiles5/scripts/sync-to-gitlab.sh

# Update system packages
sudo apt update && sudo apt upgrade -y

# Clean up old files
find ~/.local/share -name "*.tmp" -mtime +7 -delete

echo "Daily sync completed"
EOF

chmod +x ~/.local/bin/daily-sync.sh

# 2. Create systemd user service
mkdir -p ~/.config/systemd/user
cat > ~/.config/systemd/user/daily-sync.service << 'EOF'
[Unit]
Description=Daily Repository Sync
After=network-online.target

[Service]
Type=oneshot
ExecStart=%h/.local/bin/daily-sync.sh

[Install]
WantedBy=timers.target
EOF

# 3. Create timer for daily execution
cat > ~/.config/systemd/user/daily-sync.timer << 'EOF'
[Unit]
Description=Run daily sync every day
Requires=daily-sync.service

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
EOF

# 4. Enable and start timer
systemctl --user daemon-reload
systemctl --user enable --now daily-sync.timer
```

### Example 2: Automated Environment Validation

Creating automated validation script:

```bash
# 1. Create validation script
cat > ~/.local/bin/validate-env.sh << 'EOF'
#!/bin/bash
# Environment validation script

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Validating environment...${NC}"

# Check YADM status
if ! yadm status &> /dev/null; then
    echo -e "${RED}✗ YADM not working${NC}"
    exit 1
fi

# Check Ansible
if ! command -v ansible-playbook &> /dev/null; then
    echo -e "${RED}✗ Ansible not installed${NC}"
    exit 1
fi

# Validate configurations
if ./scripts/ansible-validate.sh; then
    echo -e "${GREEN}✓ All configurations valid${NC}"
else
    echo -e "${RED}✗ Configuration validation failed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Environment validation completed${NC}"
EOF

chmod +x ~/.local/bin/validate-env.sh

# 2. Add to shell startup
echo "# Run environment validation" >> ~/.zshrc
echo "validate-env.sh" >> ~/.zshrc
```

### Example 3: Automated Backup System

Setting up automated backup with encryption:

```bash
# 1. Create backup script
cat > ~/.local/bin/backup-configs.sh << 'EOF'
#!/bin/bash
# Automated configuration backup

BACKUP_DIR="$HOME/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="$BACKUP_DIR/config_backup_$DATE"

mkdir -p "$BACKUP_DIR"

echo "Starting configuration backup..."

# Backup shell configurations
tar -czf "$BACKUP_PATH/shell_configs.tar.gz" \
    ~/.zshrc ~/.bashrc ~/.zshenv \
    ~/.zsh_aliases.d ~/.zsh_functions.d

# Backup application configs
tar -czf "$BACKUP_PATH/app_configs.tar.gz" \
    ~/.config/git ~/.config/vim ~/.config/tmux

# Encrypt backup
gpg --symmetric --cipher-algo AES256 \
    --output "$BACKUP_PATH/configs.tar.gz.gpg" \
    "$BACKUP_PATH/configs.tar.gz"

# Clean up unencrypted backup
rm "$BACKUP_PATH/configs.tar.gz"

echo "Backup completed: $BACKUP_PATH/configs.tar.gz.gpg"
EOF

chmod +x ~/.local/bin/backup-configs.sh

# 2. Create weekly backup cron job
(crontab -l 2>/dev/null; echo "") | crontab -
echo "0 2 * * 0 $HOME/.local/bin/backup-configs.sh" | crontab -
```

## Troubleshooting Examples

### Example 1: YADM Recovery

Recovering from a broken YADM state:

```bash
# 1. Check YADM status
yadm status

# 2. If files are missing, restore from last known good state
yadm checkout HEAD~1 -- ~/.zshrc

# 3. Reset to working state
yadm reset --hard HEAD

# 4. Re-encrypt sensitive files if needed
yadm encrypt ~/.ssh/id_rsa
yadm encrypt ~/.gnupg/private-keys*

# 5. Commit recovery
yadm commit -m "fix: recover from broken state"
```

### Example 2: Ansible Debugging

Debugging failed Ansible playbooks:

```bash
# 1. Run with increased verbosity
ansible-playbook -i ansible-environment/inventory/hosts playbook.yml -vvv

# 2. Check syntax first
ansible-playbook --syntax-check -i ansible-environment/inventory/hosts playbook.yml

# 3. Test individual tasks
ansible-playbook -i ansible-environment/inventory/hosts playbook.yml \
  --step \
  --start-at-task="Install packages"

# 4. Dry run to see what would happen
ansible-playbook -i ansible-environment/inventory/hosts playbook.yml \
  --check \
  --diff
```

### Example 3: Sync Conflict Resolution

Resolving synchronization conflicts:

```bash
# 1. Check for conflicts
git status
# Look for "both modified" files

# 2. Stash local changes
git stash push -m "Local changes before sync"

# 3. Pull remote changes
git pull origin main

# 4. Apply stashed changes
git stash pop

# 5. Resolve conflicts manually
git mergetool

# 6. Commit resolved state
git add .
git commit -m "fix: resolve sync conflicts"
```

## Integration Examples

### Example 1: IDE Integration

Integrating with VS Code:

```bash
# 1. Install VS Code via Ansible
ansible-playbook -i ansible-environment/inventory/hosts ansible-environment/playbooks/applications.yml \
  -e "install_vscode=true"

# 2. Configure VS Code settings
mkdir -p ~/.config/Code/User
cat > ~/.config/Code/User/settings.json << 'EOF'
{
    "workbench.colorTheme": "Default Dark+",
    "editor.fontSize": 14,
    "editor.tabSize": 4,
    "editor.insertSpaces": true,
    "files.autoSave": "afterDelay",
    "files.autoSaveDelay": 1000,
    "terminal.integrated.shell.linux": "/bin/zsh"
}
EOF

# 3. Add VS Code configuration to YADM
yadm add ~/.config/Code
yadm commit -m "feat: configure VS Code"
```

### Example 2: Docker Integration

Setting up Docker development environment:

```bash
# 1. Install Docker
ansible-playbook -i ansible-environment/inventory/hosts ansible-environment/playbooks/docker-setup.yml

# 2. Create development containers
cat > ~/projects/docker-compose.yml << 'EOF'
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - .:/app
    environment:
      - NODE_ENV=development

  database:
    image: postgres:15
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_USER=dev
      - POSTGRES_PASSWORD=devpass
    volumes:
      - postgres_data:/var/lib/postgresql/data
EOF

# 3. Add Docker setup to YADM
yadm add ~/projects/docker-compose.yml
yadm commit -m "feat: add Docker development setup"
```

### Example 3: AI Tools Integration

Setting up AI development tools:

```bash
# 1. Install AI tools
ansible-playbook -i ansible-environment/inventory/hosts ansible-environment/playbooks/ai-tools.yml

# 2. Configure OpenCode
mkdir -p ~/.config/opencode
cat > ~/.config/opencode/config.json << 'EOF'
{
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 4096,
    "auto_save": true,
    "theme": "dark"
}
EOF

# 3. Configure Claude
mkdir -p ~/.config/claude
cat > ~/.config/claude/settings.json << 'EOF'
{
    "model": "claude-3-sonnet-20241022",
    "max_tokens": 4096,
    "workspace": "~/projects",
    "auto_save": true
}
EOF

# 4. Add AI configurations to YADM
yadm add ~/.config/opencode ~/.config/claude
yadm commit -m "feat: configure AI development tools"
```

---

**These examples demonstrate real-world usage patterns.** Adapt them to your specific needs and workflow preferences.

**Need help?** Check [documentation](README.md) or open an [issue](https://github.com/cbwinslow/dotfiles5/issues).