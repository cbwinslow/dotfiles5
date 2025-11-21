#!/bin/bash
# Chezmoi Deployment Script
# This script sets up chezmoi on a new machine with secure credential handling

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

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "This script should not be run as root"
        exit 1
    fi
}

# Install chezmoi
install_chezmoi() {
    log_info "Installing chezmoi..."

    if command -v chezmoi &> /dev/null; then
        log_warning "Chezmoi is already installed"
        return
    fi

    # Install chezmoi using the official installation script
    sh -c "$(curl -fsLS get.chezmoi.io)" -- -b $HOME/.local/bin

    # Add to PATH if not already there
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        export PATH="$HOME/.local/bin:$PATH"
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
        log_info "Added ~/.local/bin to PATH"
    fi

    log_success "Chezmoi installed successfully"
}

# Setup Bitwarden credentials
setup_bitwarden_credentials() {
    log_info "Setting up Bitwarden credentials..."

    # Check if credentials are already set
    if [[ -n "$BW_PASSWORD" && -n "$BW_CLIENTID" && -n "$BW_CLIENTSECRET" ]]; then
        log_info "Bitwarden credentials already configured"
        return
    fi

    # Create secure credential storage
    local cred_file="$HOME/.config/chezmoi/credentials.env"

    if [[ ! -f "$cred_file" ]]; then
        log_warning "Bitwarden credentials not found. Please run the secure setup script first."
        log_info "Run: ./scripts/setup-bitwarden-credentials.sh"
        return 1
    fi

    # Source the credentials
    set -a
    source "$cred_file"
    set +a

    log_success "Bitwarden credentials loaded"
}

# Initialize chezmoi
initialize_chezmoi() {
    log_info "Initializing chezmoi..."

    # Check if already initialized
    if [[ -d "$HOME/.local/share/chezmoi" ]]; then
        log_warning "Chezmoi already initialized"
        return
    fi

    # Detect machine type for appropriate initialization
    detect_machine_type

    # Initialize with your repository
    chezmoi init --apply blaine.winslow@gmail.com

    log_success "Chezmoi initialized"
}

# Detect machine type and OS
detect_machine_type() {
    log_info "Detecting machine type and OS..."

    # Get hostname
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

    log_info "Detected: OS=$MACHINE_OS, Distro=$MACHINE_DISTRO, Type=$MACHINE_TYPE, Hostname=$hostname"

    # Export for use in templates
    export MACHINE_OS MACHINE_DISTRO MACHINE_TYPE
}

# Apply configuration
apply_configuration() {
    log_info "Applying chezmoi configuration..."

    # Ensure Bitwarden is available and unlocked
    if ! command -v bw &> /dev/null; then
        log_error "Bitwarden CLI not found. Please install it first."
        exit 1
    fi

    # Check if Bitwarden is unlocked
    if ! bw status | jq -r '.status' | grep -q "unlocked"; then
        log_warning "Bitwarden vault is not unlocked. Attempting to unlock..."

        # Try to unlock using stored credentials
        if [[ -n "$BW_PASSWORD" ]]; then
            echo "$BW_PASSWORD" | bw unlock --passwordenv BW_PASSWORD > /dev/null 2>&1 || true
        fi

        # Check again
        if ! bw status | jq -r '.status' | grep -q "unlocked"; then
            log_error "Failed to unlock Bitwarden vault. Please unlock manually: bw unlock"
            exit 1
        fi
    fi

    # Apply configuration
    chezmoi apply

    log_success "Configuration applied successfully"
}

# Setup local configuration
setup_local_config() {
    log_info "Setting up local configuration..."

    local chezmoi_local="$HOME/.local/share/chezmoi/.chezmoi.toml.local"

    if [[ ! -f "$chezmoi_local" ]]; then
        cat > "$chezmoi_local" << 'EOF'
# Local chezmoi configuration - NOT committed to repository
# This file contains sensitive local configuration

[bitwarden]
# Local Bitwarden configuration
env = ["BW_PASSWORD", "BW_CLIENTID", "BW_CLIENTSECRET", "BW_SESSION"]
required = false
timeout = 30
max_retries = 3
EOF
        log_success "Local configuration created"
    else
        log_info "Local configuration already exists"
    fi
}

# Main deployment function
main() {
    log_info "Starting Chezmoi deployment..."

    check_root
    install_chezmoi
    setup_bitwarden_credentials
    initialize_chezmoi
    setup_local_config
    apply_configuration

    log_success "Chezmoi deployment completed successfully!"
    log_info "You may need to restart your shell or source ~/.bashrc for PATH changes to take effect."
}

# Run main function
main "$@"