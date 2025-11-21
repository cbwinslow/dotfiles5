#!/bin/bash
# Chezmoi Systemd Service Manager
# Installs and manages systemd services for chezmoi monitoring

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
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

# Check if systemd is available
check_systemd() {
    if ! command -v systemctl &> /dev/null; then
        log_error "systemd is not available on this system"
        exit 1
    fi
}

# Install systemd services
install_services() {
    local chezmoi_dir="$HOME/.local/share/chezmoi"
    local systemd_user_dir="$HOME/.config/systemd/user"

    # Create systemd user directory if it doesn't exist
    mkdir -p "$systemd_user_dir"

    log_info "Installing systemd services..."

    # Copy service files
    cp "$chezmoi_dir/systemd/chezmoi-health-monitor.service" "$systemd_user_dir/"
    cp "$chezmoi_dir/systemd/chezmoi-health-monitor.timer" "$systemd_user_dir/"

    # Replace %i and %h placeholders
    sed -i "s/%i/$(whoami)/g; s|%h|$HOME|g" "$systemd_user_dir/chezmoi-health-monitor.service"

    # Reload systemd daemon
    systemctl --user daemon-reload

    log_success "Systemd services installed"
}

# Enable services
enable_services() {
    log_info "Enabling systemd services..."

    systemctl --user enable chezmoi-health-monitor.timer
    systemctl --user start chezmoi-health-monitor.timer

    log_success "Systemd services enabled and started"
}

# Check service status
check_status() {
    log_info "Checking service status..."

    echo "Timer status:"
    systemctl --user status chezmoi-health-monitor.timer --no-pager -l

    echo ""
    echo "Service status:"
    systemctl --user status chezmoi-health-monitor.service --no-pager -l

    echo ""
    echo "Timer calendar:"
    systemctl --user list-timers chezmoi-health-monitor.timer --no-pager
}

# Disable services
disable_services() {
    log_info "Disabling systemd services..."

    systemctl --user stop chezmoi-health-monitor.timer
    systemctl --user disable chezmoi-health-monitor.timer

    log_success "Systemd services disabled"
}

# Uninstall services
uninstall_services() {
    log_info "Uninstalling systemd services..."

    disable_services

    local systemd_user_dir="$HOME/.config/systemd/user"
    rm -f "$systemd_user_dir/chezmoi-health-monitor.service"
    rm -f "$systemd_user_dir/chezmoi-health-monitor.timer"

    systemctl --user daemon-reload

    log_success "Systemd services uninstalled"
}

# Show usage
usage() {
    cat << EOF
Chezmoi Systemd Service Manager

Usage: $0 [COMMAND]

Commands:
    install     Install and enable systemd services
    uninstall   Disable and remove systemd services
    status      Show status of systemd services
    enable      Enable systemd services
    disable     Disable systemd services
    help        Show this help message

Examples:
    $0 install    # Install and enable monitoring services
    $0 status     # Check if services are running
    $0 uninstall  # Remove monitoring services

EOF
}

# Main function
main() {
    local command="$1"

    case "$command" in
        install)
            check_systemd
            install_services
            enable_services
            check_status
            ;;
        uninstall)
            check_systemd
            uninstall_services
            ;;
        status)
            check_systemd
            check_status
            ;;
        enable)
            check_systemd
            enable_services
            ;;
        disable)
            check_systemd
            disable_services
            ;;
        help|"")
            usage
            ;;
        *)
            log_error "Unknown command: $command"
            usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"