#!/bin/bash
# Ansible Environment Validation Script
# Validates and tests Ansible configuration

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ANSIBLE_DIR="$(pwd)/ansible-environment"

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

validate_structure() {
    log_info "Validating Ansible directory structure..."
    
    local required_dirs=("playbooks" "group_vars" "host_vars" "roles" "files" "templates")
    local required_files=("inventory" "hosts" "site.yml")
    
    for dir in "${required_dirs[@]}"; do
        if [ -d "$ANSIBLE_DIR/$dir" ]; then
            log_success "✓ Directory exists: $dir"
        else
            log_error "✗ Missing directory: $dir"
        fi
    done
    
    for file in "${required_files[@]}"; do
        if [ -f "$ANSIBLE_DIR/$file" ]; then
            log_success "✓ File exists: $file"
        else
            log_error "✗ Missing file: $file"
        fi
    done
}

validate_syntax() {
    log_info "Validating Ansible syntax..."
    
    cd "$ANSIBLE_DIR"
    
    # Validate inventory
    if ansible-inventory -i inventory --list >/dev/null 2>&1; then
        log_success "✓ Inventory syntax valid"
    else
        log_error "✗ Inventory syntax error"
    fi
    
    # Validate playbooks
    for playbook in playbooks/*.yml; do
        if [ -f "$playbook" ]; then
            if ansible-playbook --syntax-check "$playbook" >/dev/null 2>&1; then
                log_success "✓ Playbook syntax valid: $(basename "$playbook")"
            else
                log_error "✗ Playbook syntax error: $(basename "$playbook")"
            fi
        fi
    done
    
    # Validate site.yml
    if ansible-playbook --syntax-check site.yml >/dev/null 2>&1; then
        log_success "✓ Site.yml syntax valid"
    else
        log_error "✗ Site.yml syntax error"
    fi
}

test_connectivity() {
    log_info "Testing host connectivity..."
    
    cd "$ANSIBLE_DIR"
    
    # Test local connection
    if ansible all -i inventory --connection=local -m ping >/dev/null 2>&1; then
        log_success "✓ Local connection successful"
    else
        log_error "✗ Local connection failed"
    fi
}

dry_run() {
    log_info "Performing dry run deployment..."
    
    cd "$ANSIBLE_DIR"
    ansible-playbook -i inventory site.yml --check --diff
}

show_help() {
    echo -e "${YELLOW}Ansible Validation Script${NC}"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  structure  Validate directory structure"
    echo "  syntax    Validate Ansible syntax"
    echo "  test      Test host connectivity"
    echo "  dry-run   Perform dry run deployment"
    echo "  all       Run all validations"
    echo "  help      Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 structure"
    echo "  $0 syntax"
    echo "  $0 dry-run"
}

main() {
    case "${1:-help}" in
        structure)
            validate_structure
            ;;
        syntax)
            validate_syntax
            ;;
        test)
            test_connectivity
            ;;
        dry-run)
            dry_run
            ;;
        all)
            validate_structure
            validate_syntax
            test_connectivity
            log_success "All validations completed"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
