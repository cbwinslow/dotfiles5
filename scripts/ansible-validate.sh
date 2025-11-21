#!/bin/bash
# Ansible Configuration Validation Script
# Validates and tests Ansible configuration

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Ansible Configuration Validation ===${NC}"
echo -e "${YELLOW}Validating configuration files...${NC}"

# Check if ansible-environment exists
if [ ! -d "ansible-environment" ]; then
    echo -e "${RED}✗ ansible-environment directory not found${NC}"
    echo "Please run this from the repository root"
    exit 1
fi

# Validate YAML syntax
echo -e "${YELLOW}Checking YAML syntax...${NC}"

yaml_files=(
    "ansible-environment/site.yml"
    "ansible-environment/group_vars/all.yml"
    ansible-environment/playbooks/*.yml
)

valid=true
for file in "${yaml_files[@]}"; do
    if [ -f "$file" ]; then
        if command -v yamllint &> /dev/null; then
            if yamllint "$file" &> /dev/null; then
                echo -e "${GREEN}✓ $file${NC}"
            else
                echo -e "${RED}✗ $file - YAML syntax error${NC}"
                valid=false
            fi
        else
            echo -e "${YELLOW}⚠ $file - yamllint not available, skipping syntax check${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ $file - not found${NC}"
    fi
done

# Validate Ansible syntax
echo -e "${YELLOW}Checking Ansible syntax...${NC}"

playbooks=(
    "ansible-environment/site.yml"
    ansible-environment/playbooks/*.yml
)

for playbook in "${playbooks[@]}"; do
    if [ -f "$playbook" ]; then
        if ansible-playbook --syntax-check -i ansible-environment/inventory/hosts "$playbook" &> /dev/null; then
            echo -e "${GREEN}✓ $playbook${NC}"
        else
            echo -e "${RED}✗ $playbook - Ansible syntax error${NC}"
            ansible-playbook --syntax-check -i ansible-environment/inventory/hosts "$playbook"
            valid=false
        fi
    fi
done

# Check inventory file
echo -e "${YELLOW}Checking inventory...${NC}"
if [ -f "ansible-environment/inventory/hosts" ]; then
    if ansible-inventory -i ansible-environment/inventory/hosts --list &> /dev/null; then
        echo -e "${GREEN}✓ Inventory file is valid${NC}"
    else
        echo -e "${RED}✗ Inventory file is invalid${NC}"
        valid=false
    fi
else
    echo -e "${RED}✗ Inventory file not found${NC}"
    valid=false
fi

# Final result
if [ "$valid" = true ]; then
    echo -e "${GREEN}✓ All validations passed!${NC}"
    echo -e "${BLUE}Configuration is ready for deployment.${NC}"
else
    echo -e "${RED}✗ Validation failed${NC}"
    echo "Please fix the errors above before deploying"
    exit 1
fi
