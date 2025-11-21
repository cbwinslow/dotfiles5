#!/bin/bash
# Ansible Apps Installation Script
# Installs applications using Ansible playbooks

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Ansible Apps Installation ===${NC}"
echo -e "${YELLOW}Installing applications and tools...${NC}"

# Check if Ansible is installed
if ! command -v ansible &> /dev/null; then
    echo -e "${RED}✗ Ansible is not installed${NC}"
    echo "Please install Ansible first: pip install ansible"
    exit 1
fi

# Check if ansible-environment exists
if [ ! -d "ansible-environment" ]; then
    echo -e "${RED}✗ ansible-environment directory not found${NC}"
    echo "Please run this from the repository root"
    exit 1
fi

# Menu for installation options
echo -e "${BLUE}Select installation type:${NC}"
echo "1) Package Managers"
echo "2) Development Tools"
echo "3) Applications (Flatpak/Snap)"
echo "4) Docker Setup"
echo "5) Complete Installation"
echo -n "Enter choice [1-5]: "
read -r choice

case $choice in
    1)
        echo -e "${YELLOW}Installing package managers...${NC}"
        ansible-playbook -i ansible-environment/inventory/hosts ansible-environment/playbooks/package-managers.yml
        ;;
    2)
        echo -e "${YELLOW}Installing development tools...${NC}"
        ansible-playbook -i ansible-environment/inventory/hosts ansible-environment/playbooks/dev-environment.yml
        ;;
    3)
        echo -e "${YELLOW}Installing applications...${NC}"
        ansible-playbook -i ansible-environment/inventory/hosts ansible-environment/playbooks/applications.yml
        ;;
    4)
        echo -e "${YELLOW}Setting up Docker...${NC}"
        ansible-playbook -i ansible-environment/inventory/hosts ansible-environment/playbooks/docker-setup.yml
        ;;
    5)
        echo -e "${YELLOW}Running complete installation...${NC}"
        ansible-playbook -i ansible-environment/inventory/hosts ansible-environment/site.yml
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Installation completed successfully!${NC}"
else
    echo -e "${RED}✗ Installation failed${NC}"
    echo "Please check the error messages above"
    exit 1
fi
