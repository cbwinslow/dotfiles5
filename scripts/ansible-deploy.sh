#!/bin/bash
# Ansible Deployment Script
# Recreates entire environment using Ansible

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
ANSIBLE_DIR="$(pwd)/ansible-environment"
INVENTORY="${ANSIBLE_DIR}/inventory"
HOSTS="${ANSIBLE_DIR}/hosts"
SITE_YML="${ANSIBLE_DIR}/site.yml"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v ansible >/dev/null 2>&1; then
        log_error "Ansible not installed. Installing..."
        sudo apt update && sudo apt install -y ansible
    fi
    
    if [ ! -d "$ANSIBLE_DIR" ]; then
        log_error "Ansible environment directory not found: $ANSIBLE_DIR"
        exit 1
    fi
    
    log_success "Prerequisites checked"
}

deploy_local() {
    log_info "Deploying to local system..."
    cd "$ANSIBLE_DIR"
    ansible-playbook -i inventory site.yml --connection=local --become
}

deploy_remote() {
    local host="$1"
    log_info "Deploying to remote host: $host"
    cd "$ANSIBLE_DIR"
    ansible-playbook -i inventory site.yml --limit "$host" --become
}

deploy_all() {
    log_info "Deploying to all hosts..."
    cd "$ANSIBLE_DIR"
    ansible-playbook -i inventory site.yml --become
}

show_help() {
    echo -e "${YELLOW}Ansible Deployment Script${NC}"
    echo ""
    echo "Usage: $0 [COMMAND] [HOST]"
    echo ""
    echo "Commands:"
    echo "  local     Deploy to local system"
    echo "  remote    Deploy to specific remote host"
    echo "  all       Deploy to all hosts"
    echo "  check     Check prerequisites only"
    echo "  help      Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 local"
    echo "  $0 remote server.example.com"
    echo "  $0 all"
}

# Main execution
main() {
    case "${1:-help}" in
        local)
            check_prerequisites
            deploy_local
            ;;
        remote)
            if [ -z "${2:-}" ]; then
                log_error "Host name required for remote deployment"
                show_help
                exit 1
            fi
            check_prerequisites
            deploy_remote "$2"
            ;;
        all)
            check_prerequisites
            deploy_all
            ;;
        check)
            check_prerequisites
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
