#!/bin/bash
# Local Binaries Installation Script
# Installs custom tools and binaries to ~/.local/bin

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
DEV_USER="${DEV_USER:-$(whoami)}"
LOCAL_BIN="/home/$DEV_USER/.local/bin"
TEMP_DIR="/tmp/local-bin-install"

echo -e "${BLUE}=== Local Binaries Installation ===${NC}"
echo -e "${YELLOW}Installing custom tools to $LOCAL_BIN${NC}"

# Create directories
mkdir -p "$LOCAL_BIN"
mkdir -p "$TEMP_DIR"

# Function to install from GitHub
install_github_tool() {
    local repo_url="$1"
    local tool_name="$2"
    local binary_name="$3"
    local install_method="$4"
    
    echo -e "${YELLOW}Installing $tool_name...${NC}"
    
    cd "$TEMP_DIR"
    git clone --depth 1 "$repo_url" "$tool_name" 2>/dev/null || {
        echo -e "${RED}✗ Failed to clone $tool_name${NC}"
        return 1
    }
    
    cd "$tool_name"
    
    case "$install_method" in
        "cargo")
            if command -v cargo >/dev/null 2>&1; then
                cargo build --release --quiet
                cp "target/release/$binary_name" "$LOCAL_BIN/"
                echo -e "${GREEN}✓ $tool_name installed via Cargo${NC}"
            else
                echo -e "${RED}✗ Cargo not found for $tool_name${NC}"
            fi
            ;;
        "go")
            if command -v go >/dev/null 2>&1; then
                go build -o "$LOCAL_BIN/$binary_name" ./cmd/"$binary_name"
                echo -e "${GREEN}✓ $tool_name installed via Go${NC}"
            else
                echo -e "${RED}✗ Go not found for $tool_name${NC}"
            fi
            ;;
        "make")
            if command -v make >/dev/null 2>&1; then
                make build --quiet
                cp "bin/$binary_name" "$LOCAL_BIN/" 2>/dev/null || cp "$binary_name" "$LOCAL_BIN/"
                echo -e "${GREEN}✓ $tool_name installed via Make${NC}"
            else
                echo -e "${RED}✗ Make not found for $tool_name${NC}"
            fi
            ;;
        "direct")
            cp "$binary_name" "$LOCAL_BIN/" 2>/dev/null || cp "$tool_name" "$LOCAL_BIN/"
            chmod +x "$LOCAL_BIN/$binary_name"
            echo -e "${GREEN}✓ $tool_name installed directly${NC}"
            ;;
        "npm")
            if command -v npm >/dev/null 2>&1; then
                npm install -g --silent
                echo -e "${GREEN}✓ $tool_name installed via NPM${NC}"
            else
                echo -e "${RED}✗ NPM not found for $tool_name${NC}"
            fi
            ;;
        "python")
            if command -v pip3 >/dev/null 2>&1; then
                pip3 install --user --quiet "$tool_name"
                echo -e "${GREEN}✓ $tool_name installed via pip3${NC}"
            else
                echo -e "${RED}✗ pip3 not found for $tool_name${NC}"
            fi
            ;;
        *)
                echo -e "${RED}✗ Unknown install method: $install_method${NC}"
                return 1
                ;;
    esac
    
    chmod +x "$LOCAL_BIN/$binary_name" 2>/dev/null || true
    cd ..
    rm -rf "$tool_name"
}

# Function to install from URL
install_from_url() {
    local url="$1"
    local binary_name="$2"
    local dest_name="$3"
    
    echo -e "${YELLOW}Downloading $dest_name...${NC}"
    
    cd "$TEMP_DIR"
    curl -fsSL "$url" -o "$dest_name" || {
        echo -e "${RED}✗ Failed to download $dest_name${NC}"
        return 1
    }
    
    chmod +x "$dest_name"
    mv "$dest_name" "$LOCAL_BIN/$binary_name"
    echo -e "${GREEN}✓ $dest_name installed${NC}"
}

# Install tools from GitHub repositories
echo -e "${BLUE}Installing GitHub tools...${NC}"

# Git UI - TUI for Git
install_github_tool \
    "https://github.com/extrawurst/gitui.git" \
    "gitui" \
    "gitui" \
    "cargo"

# New Relic CLI
install_github_tool \
    "https://github.com/newrelic/newrelic-cli.git" \
    "newrelic-cli" \
    "newrelic" \
    "go"

# OpenShift CLI (oc)
install_github_tool \
    "https://github.com/openshift/oc.git" \
    "oc" \
    "occtx" \
    "make"

# Install additional development tools
echo -e "${BLUE}Installing additional tools...${NC}"

# Coverage tool (Python)
if command -v pip3 >/dev/null 2>&1; then
    install_github_tool \
        "https://github.com/nedbat/coveragepy.git" \
        "coveragepy" \
        "coverage" \
        "python"
fi

# FastAPI CLI (if not already installed)
if ! command -v fastapi >/dev/null 2>&1 && command -v pip3 >/dev/null 2>&1; then
    echo -e "${YELLOW}Installing FastAPI CLI...${NC}"
    pip3 install --user --quiet "fastapi[all]"
fi

# Invoke task runner (if not already installed)
if ! command -v invoke >/dev/null 2>&1 && command -v pip3 >/dev/null 2>&1; then
    echo -e "${YELLOW}Installing Invoke...${NC}"
    pip3 install --user --quiet invoke
fi

# Fabric CLI (if available)
if command -v pip3 >/dev/null 2>&1; then
    install_github_tool \
        "https://github.com/danielmiessler/fabric.git" \
        "fabric" \
        "fabric" \
        "python"
fi

# Install from direct URLs
echo -e "${BLUE}Installing tools from URLs...${NC}"

# Example: Install a custom script
install_from_url \
    "https://raw.githubusercontent.com/github/copilot.vim/main/install.sh" \
    "copilot-install" \
    "copilot-install"

# Create utility scripts
echo -e "${BLUE}Creating utility scripts...${NC}"

# Create a dev environment switcher
cat > "$LOCAL_BIN/dev-env" << 'EOF'
#!/bin/bash
# Development environment switcher
case "${1:-help}" in
    "python")
        echo "Activating Python environment"
        source ~/.pythonenv/bin/activate 2>/dev/null || echo "Python env not found"
        ;;
    "node")
        echo "Activating Node.js environment"
        export NVM_DIR="$HOME/.nvm"
        [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
        nvm use 2>/dev/null || echo "NVM not available"
        ;;
    "go")
        echo "Setting up Go environment"
        export GOPATH="$HOME/go"
        export PATH="$PATH:$GOPATH/bin"
        ;;
    "rust")
        echo "Setting up Rust environment"
        source ~/.cargo/env 2>/dev/null || echo "Cargo not found"
        ;;
    *)
        echo "Usage: dev-env [python|node|go|rust]"
        echo "Available environments:"
        echo "  python - Python virtual environment"
        echo "  node   - Node.js with NVM"
        echo "  go     - Go development"
        echo "  rust   - Rust with Cargo"
        ;;
esac
EOF

chmod +x "$LOCAL_BIN/dev-env"

# Create a quick project initializer
cat > "$LOCAL_BIN/quick-init" << 'EOF'
#!/bin/bash
# Quick project initializer
PROJECT_TYPE="${1:-help}"
PROJECT_NAME="${2:-project}"

case "$PROJECT_TYPE" in
    "python")
        mkdir -p "$PROJECT_NAME"/{src,tests,docs}
        cat > "$PROJECT_NAME/README.md" << PROJECTREADME
# $PROJECT_NAME

Python project template.

## Setup
\`\`\`bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
\`\`\`

## Development
- Source virtual environment: \`source venv/bin/activate\`
- Run tests: \`python -m pytest\`
- Install dependencies: \`pip install -r requirements.txt\`
PROJECTREADME
        touch "$PROJECT_NAME/requirements.txt"
        touch "$PROJECT_NAME/src/__init__.py"
        touch "$PROJECT_NAME/tests/__init__.py"
        echo -e "${GREEN}✓ Python project '$PROJECT_NAME' created${NC}"
        ;;
    "node")
        mkdir -p "$PROJECT_NAME"/{src,tests,dist}
        cat > "$PROJECT_NAME/package.json" << PROJECTJSON
{
  "name": "$PROJECT_NAME",
  "version": "1.0.0",
  "description": "Node.js project template",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/index.js",
    "test": "jest",
    "build": "webpack --mode production"
  },
  "dependencies": {},
  "devDependencies": {
    "jest": "^29.0.0",
    "webpack": "^5.0.0"
  }
}
PROJECTJSON
        cat > "$PROJECT_NAME/src/index.js" << PROJECTJS
// Main entry point for $PROJECT_NAME
console.log('Hello from $PROJECT_NAME!');
PROJECTJS
        echo -e "${GREEN}✓ Node.js project '$PROJECT_NAME' created${NC}"
        ;;
    "go")
        mkdir -p "$PROJECT_NAME"/{cmd,internal,pkg}
        cat > "$PROJECT_NAME/go.mod" << GOMOD
module $PROJECT_NAME

go 1.21

require (
    // Add dependencies here
)
GOMOD
        cat > "$PROJECT_NAME/main.go" << GOMAIN
package main

import "fmt"

func main() {
    fmt.Println("Hello from $PROJECT_NAME!")
}
GOMAIN
        echo -e "${GREEN}✓ Go project '$PROJECT_NAME' created${NC}"
        ;;
    *)
        echo "Usage: quick-init [python|node|go] [project-name]"
        echo "Available types:"
        echo "  python - Python project with venv, pytest structure"
        echo "  node   - Node.js project with webpack, jest"
        echo "  go     - Go module with standard layout"
        ;;
esac
EOF

chmod +x "$LOCAL_BIN/quick-init"

# Cleanup
rm -rf "$TEMP_DIR"

# Set proper ownership
chown -R "$DEV_USER:$DEV_USER" "$LOCAL_BIN"

# Add to PATH if not already there
if ! echo "$PATH" | grep -q "$LOCAL_BIN"; then
    echo -e "${YELLOW}Adding $LOCAL_BIN to PATH...${NC}"
    echo "export PATH=\"\$PATH:$LOCAL_BIN\"" >> "/home/$DEV_USER/.zshrc.local" 2>/dev/null || \
    echo "export PATH=\"\$PATH:$LOCAL_BIN\"" >> "/home/$DEV_USER/.bashrc.local" 2>/dev/null || true
fi

echo -e "${GREEN}✓ Local binaries installation completed!${NC}"
echo -e "${BLUE}Installed tools:${NC}"
echo "  - gitui (Git TUI)"
echo "  - newrelic (New Relic CLI)"
echo "  - occtx (OpenShift CLI)"
echo "  - coverage (Python coverage)"
echo "  - fastapi (FastAPI CLI)"
echo "  - invoke (Task runner)"
echo "  - fabric (Fabric CLI)"
echo "  - dev-env (Environment switcher)"
echo "  - quick-init (Project initializer)"

echo -e "${YELLOW}Note: You may need to restart your shell to use the new tools.${NC}"