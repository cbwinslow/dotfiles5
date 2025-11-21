#!/bin/bash
# Ansible Deployment Script
# Deploys complete environment using Ansible playbooks

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Ansible Environment Deployment ===${NC}"
echo -e "${YELLOW}Deploying complete development environment...${NC}"

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

echo -e "${YELLOW}Running master playbook...${NC}"

# Run the master site playbook
ansible-playbook -i ansible-environment/inventory/hosts ansible-environment/site.yml

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Environment deployed successfully!${NC}"
    echo -e "${BLUE}Your development environment is now configured.${NC}"
else
    echo -e "${RED}✗ Deployment failed${NC}"
    echo "Please check the error messages above"
    exit 1
fi
