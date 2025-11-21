#!/bin/bash
# Machine Detection and Data Update Script
# Automatically detects machine information and updates data.yaml

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

# Detect machine information
detect_machine() {
    local hostname=$(hostname)

    # Detect OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        MACHINE_OS="macos"
        MACHINE_DISTRO="macos"
    elif [[ -f /etc/os-release ]]; then
        . /etc/os-release
        MACHINE_OS="linux"
        MACHINE_DISTRO="${ID:-unknown}"
    else
        MACHINE_OS="unknown"
        MACHINE_DISTRO="unknown"
    fi

    # Determine machine type
    if [[ $hostname == *"server"* ]] || [[ $hostname == *"dell"* ]]; then
        MACHINE_TYPE="server"
    elif [[ $hostname == *"mac"* ]] || [[ $hostname == *"laptop"* ]]; then
        MACHINE_TYPE="laptop"
    else
        MACHINE_TYPE="desktop"
    fi

    log_info "Detected machine: $hostname"
    log_info "OS: $MACHINE_OS, Distro: $MACHINE_DISTRO, Type: $MACHINE_TYPE"
}

# Update data.yaml with machine information
update_data_yaml() {
    local chezmoi_dir="$HOME/.local/share/chezmoi"
    local data_file="$chezmoi_dir/data.yaml"

    if [[ ! -f "$data_file" ]]; then
        log_error "data.yaml not found at $data_file"
        exit 1
    fi

    log_info "Updating data.yaml with machine information..."

    # Create a backup
    cp "$data_file" "${data_file}.backup.$(date +%Y%m%d_%H%M%S)"

    # Check if yq is installed
    if ! command -v yq &> /dev/null; then
        log_warning "yq not found. Installing yq..."
        # Check for pip
        if ! command -v pip &> /dev/null; then
            log_error "pip not found. Please install pip first."
            exit 1
        fi
        pip install yq
    fi

    # Find the machine in the homelab_machines array and update it
    local hostname=$(hostname)
    yq -i ".homelab_machines[] |= select(.name == "$hostname") |= . + {"os": "$MACHINE_OS", "distro": "$MACHINE_DISTRO", "type": "$MACHINE_TYPE"}" "$data_file"

    log_success "Updated data.yaml with machine information"
}

# Main function
main() {
    log_info "Detecting and updating machine information..."

    detect_machine
    update_data_yaml

    log_success "Machine detection and data update complete!"
    log_info "Machine: OS=$MACHINE_OS, Distro=$MACHINE_DISTRO, Type=$MACHINE_TYPE"
}

# Run main function
main "$@"