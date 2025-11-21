#!/bin/bash
# Homebrew Bundle Installation Script
# Installs all tools from Brewfile using Ansible

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
DEV_USER="${DEV_USER:-$(whoami)}"
ANSIBLE_DIR="/home/$DEV_USER/ansible-environment"
BREWFILE_PATH="/home/$DEV_USER/Brewfile"

echo -e "${BLUE}=== Homebrew Bundle Installation ===${NC}"
echo -e "${YELLOW}Installing tools from Brewfile via Ansible${NC}"

# Check if Brewfile exists
if [ ! -f "$BREWFILE_PATH" ]; then
    echo -e "${RED}✗ Brewfile not found at $BREWFILE_PATH${NC}"
    exit 1
fi

# Check if Ansible is available
if ! command -v ansible-playbook >/dev/null 2>&1; then
    echo -e "${RED}✗ Ansible not found. Installing Ansible...${NC}"
    if command -v pip3 >/dev/null 2>&1; then
        pip3 install --user ansible
    else
        echo -e "${RED}✗ pip3 not found. Cannot install Ansible.${NC}"
        exit 1
    fi
fi

# Function to parse Brewfile and create variables
parse_brewfile() {
    echo -e "${BLUE}Parsing Brewfile...${NC}"
    
    # Create temporary variable files
    local taps_file="/tmp/homebrew-taps.yml"
    local formulae_file="/tmp/homebrew-formulae.yml"
    local casks_file="/tmp/homebrew-casks.yml"
    
    # Parse taps
    echo "homebrew_taps:" > "$taps_file"
    grep '^tap ' "$BREWFILE_PATH" | sed "s/tap \"\(.*\)\"/      - \"\1\"/" >> "$taps_file"
    
    # Parse formulae
    echo "homebrew_formulae:" > "$formulae_file"
    grep '^brew ' "$BREWFILE_PATH" | while read -r line; do
        name=$(echo "$line" | sed 's/brew "\(.*\)".*/\1/')
        # Try to extract description from comments or use default
        description="CLI tool from Homebrew"
        echo "      - name: \"$name\"" >> "$formulae_file"
        echo "        description: \"$description\"" >> "$formulae_file"
    done
    
    # Parse casks
    echo "homebrew_casks:" > "$casks_file"
    grep '^cask ' "$BREWFILE_PATH" | while read -r line; do
        name=$(echo "$line" | sed 's/cask "\(.*\)".*/\1/')
        description="GUI application from Homebrew"
        echo "      - name: \"$name\"" >> "$casks_file"
        echo "        description: \"$description\"" >> "$casks_file"
    done
    
    echo -e "${GREEN}✓ Brewfile parsed successfully${NC}"
}

# Function to create dynamic Ansible playbook
create_ansible_playbook() {
    local playbook_file="/tmp/homebrew-dynamic.yml"
    
    cat > "$playbook_file" << EOF
---
- name: Dynamic Homebrew Installation
  hosts: localhost
  connection: local
  become: false
  vars:
    homebrew_taps:$(grep '^tap ' "$BREWFILE_PATH" | sed 's/tap "\(.*\)".*/\n      - "\1"/' | grep -v '^$')
    homebrew_formulae:$(grep '^brew ' "$BREWFILE_PATH" | sed 's/brew "\(.*\)".*/\n      - { name: "\1", description: "CLI tool" }/' | grep -v '^$')
    homebrew_casks:$(grep '^cask ' "$BREWFILE_PATH" | sed 's/cask "\(.*\)".*/\n      - { name: "\1", description: "GUI application" }/' | grep -v '^$')
    
  tasks:
    - name: Add Homebrew taps
      shell: |
        {% for tap in homebrew_taps %}
          echo "Adding tap: {{ tap }}"
          brew tap {{ tap }} 2>/dev/null || echo "Tap {{ tap }} already exists"
        {% endfor %}
      args:
        executable: /bin/bash
        
    - name: Install Homebrew formulae
      shell: |
        {% for formula in homebrew_formulae %}
          echo "Installing formula: {{ formula.name }}"
          if brew list {{ formula.name }} >/dev/null 2>&1; then
            echo "{{ formula.name }} is already installed"
          else
            brew install {{ formula.name }}
          fi
        {% endfor %}
      args:
        executable: /bin/bash
        
    - name: Install Homebrew casks
      shell: |
        {% for cask in homebrew_casks %}
          echo "Installing cask: {{ cask.name }}"
          if brew list --cask {{ cask.name }} >/dev/null 2>&1; then
            echo "{{ cask.name }} is already installed"
          else
            brew install --cask {{ cask.name }}
          fi
        {% endfor %}
      args:
        executable: /bin/bash
        
    - name: Update Homebrew
      shell: |
        echo "Updating Homebrew..."
        brew update
        
    - name: Installation summary
      shell: |
        echo "=== Installation Summary ==="
        echo "Total formulae: \$(grep '^brew ' "$BREWFILE_PATH" | wc -l)"
        echo "Total casks: \$(grep '^cask ' "$BREWFILE_PATH" | wc -l)"
        echo "Installation completed!"
      args:
        executable: /bin/bash
EOF
    
    echo "$playbook_file"
}

# Function to run installation
run_installation() {
    echo -e "${YELLOW}Starting Homebrew installation...${NC}"
    
    # Check if Homebrew is installed
    if ! command -v brew >/dev/null 2>&1; then
        echo -e "${RED}✗ Homebrew not found. Installing Homebrew first...${NC}"
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Add Homebrew to PATH
        if [ -d "/home/linuxbrew/.linuxbrew" ]; then
            echo 'export PATH="/home/linuxbrew/.linuxbrew/bin:$PATH"' >> "/home/$DEV_USER/.zshrc"
            export PATH="/home/linuxbrew/.linuxbrew/bin:$PATH"
        elif [ -d "/opt/homebrew" ]; then
            echo 'export PATH="/opt/homebrew/bin:$PATH"' >> "/home/$DEV_USER/.zshrc"
            export PATH="/opt/homebrew/bin:$PATH"
        fi
    fi
    
    # Parse Brewfile
    parse_brewfile
    
    # Create and run dynamic playbook
    local playbook_file=$(create_ansible_playbook)
    
    echo -e "${BLUE}Running Ansible playbook...${NC}"
    ansible-playbook "$playbook_file" --connection=local
    
    # Cleanup
    rm -f "$playbook_file"
    rm -f /tmp/homebrew-taps.yml
    rm -f /tmp/homebrew-formulae.yml
    rm -f /tmp/homebrew-casks.yml
    
    echo -e "${GREEN}✓ Homebrew bundle installation completed!${NC}"
}

# Function to show help
show_help() {
    echo "Homebrew Bundle Installation Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -u, --update    Update existing installations only"
    echo "  -c, --clean     Clean up after installation"
    echo "  -v, --verbose   Verbose output"
    echo ""
    echo "Examples:"
    echo "  $0                    # Install all tools from Brewfile"
    echo "  $0 --update         # Update existing tools"
    echo "  $0 --clean          # Clean up after installation"
}

# Parse command line arguments
UPDATE_ONLY=false
CLEAN_UP=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -u|--update)
            UPDATE_ONLY=true
            shift
            ;;
        -c|--clean)
            CLEAN_UP=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Main execution
if [ "$UPDATE_ONLY" = true ]; then
    echo -e "${BLUE}Updating existing Homebrew installations...${NC}"
    brew update && brew upgrade
elif [ "$CLEAN_UP" = true ]; then
    echo -e "${BLUE}Cleaning up Homebrew...${NC}"
    brew cleanup --prune=30
else
    run_installation
fi

echo -e "${GREEN}All operations completed!${NC}"