#!/bin/bash
# Ansible Apps Installation Script
# Install all applications, packages, and repositories

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

install_package_managers() {
    log_info "Installing package managers..."
    cd "$ANSIBLE_DIR"
    ansible-playbook -i inventory playbooks/package-managers.yml --become
}

install_flatpak_apps() {
    log_info "Installing Flatpak applications..."
    cd "$ANSIBLE_DIR"
    ansible-playbook -i inventory playbooks/flatpak-apps.yml --become
}

install_snap_apps() {
    log_info "Installing Snap applications..."
    cd "$ANSIBLE_DIR"
    ansible-playbook -i inventory playbooks/snap-apps.yml --become
}

install_python_packages() {
    log_info "Installing Python packages..."
    cd "$ANSIBLE_DIR"
    ansible-playbook -i inventory playbooks/python-packages.yml
}

install_docker_setup() {
    log_info "Setting up Docker and containers..."
    cd "$ANSIBLE_DIR"
    ansible-playbook -i inventory playbooks/docker-setup.yml --become
}

clone_github_repos() {
    log_info "Cloning GitHub repositories..."
    cd "$ANSIBLE_DIR"
    ansible-playbook -i inventory playbooks/github-repos.yml
}

install_all() {
    log_info "Installing complete environment..."
    install_package_managers
    install_flatpak_apps
    install_snap_apps
    install_python_packages
    install_docker_setup
    clone_github_repos
    log_success "Complete environment installation finished!"
}

show_help() {
    echo -e "${YELLOW}Ansible Apps Installation Script${NC}"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  package-managers    Install package managers (flatpak, snap, pip, uv, docker)"
    echo "  flatpak           Install Flatpak applications"
    echo "  snap              Install Snap applications"
    echo "  python            Install Python packages and UV tools"
    echo "  docker            Setup Docker and pull images"
    echo "  github            Clone GitHub repositories"
    echo "  all               Install everything"
    echo "  help              Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 all"
    echo "  $0 flatpak"
    echo "  $0 python"
}

# Main execution
main() {
    case "${1:-help}" in
        package-managers)
            check_prerequisites
            install_package_managers
            ;;
        flatpak)
            check_prerequisites
            install_flatpak_apps
            ;;
        snap)
            check_prerequisites
            install_snap_apps
            ;;
        python)
            check_prerequisites
            install_python_packages
            ;;
        docker)
            check_prerequisites
            install_docker_setup
            ;;
        github)
            check_prerequisites
            clone_github_repos
            ;;
        all)
            check_prerequisites
            install_all
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
