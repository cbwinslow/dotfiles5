#!/bin/bash
# Secure Bitwarden Credentials Setup
# This script securely stores Bitwarden credentials for chezmoi deployment

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

# Create secure credentials directory
setup_credentials_directory() {
    local cred_dir="$HOME/.config/chezmoi"

    if [[ ! -d "$cred_dir" ]]; then
        mkdir -p "$cred_dir"
        chmod 700 "$cred_dir"
        log_success "Created secure credentials directory"
    fi
}

# Prompt for Bitwarden credentials
prompt_credentials() {
    log_info "Please enter your Bitwarden API credentials:"
    log_info "You can find these at: https://vault.bitwarden.com/#/settings/account-security/api-key"

    read -p "Bitwarden Password: " -s BW_PASSWORD
    echo
    read -p "Client ID: " BW_CLIENTID
    read -p "Client Secret: " -s BW_CLIENTSECRET
    echo

    # Validate inputs
    if [[ -z "$BW_PASSWORD" || -z "$BW_CLIENTID" || -z "$BW_CLIENTSECRET" ]]; then
        log_error "All credentials are required"
        exit 1
    fi
}

# Store credentials securely
store_credentials() {
    local cred_file="$HOME/.config/chezmoi/credentials.env"

    cat > "$cred_file" << EOF
# Bitwarden API Credentials
# This file contains sensitive information - keep it secure!
export BW_PASSWORD='$BW_PASSWORD'
export BW_CLIENTID='$BW_CLIENTID'
export BW_CLIENTSECRET='$BW_CLIENTSECRET'
EOF

    chmod 600 "$cred_file"
    log_success "Credentials stored securely in $cred_file"
}

# Test credentials
test_credentials() {
    log_info "Testing Bitwarden credentials..."

    # Source credentials
    set -a
    source "$HOME/.config/chezmoi/credentials.env"
    set +a

    # Test login
    if echo "$BW_PASSWORD" | bw login --passwordenv BW_PASSWORD > /dev/null 2>&1; then
        log_success "Bitwarden login successful"
    else
        log_error "Bitwarden login failed. Please check your credentials."
        exit 1
    fi

    # Test unlock
    if echo "$BW_PASSWORD" | bw unlock --passwordenv BW_PASSWORD > /dev/null 2>&1; then
        log_success "Bitwarden unlock successful"
    else
        log_error "Bitwarden unlock failed. Please check your credentials."
        exit 1
    fi
}

# Create shell integration
create_shell_integration() {
    local shell_rc="$HOME/.bashrc"

    if [[ -n "$ZSH_VERSION" ]]; then
        shell_rc="$HOME/.zshrc"
    fi

    if ! grep -q "chezmoi/credentials.env" "$shell_rc"; then
        echo "# Load Chezmoi Bitwarden credentials" >> "$shell_rc"
        echo "if [[ -f \$HOME/.config/chezmoi/credentials.env ]]; then" >> "$shell_rc"
        echo "    set -a" >> "$shell_rc"
        echo "    source \$HOME/.config/chezmoi/credentials.env" >> "$shell_rc"
        echo "    set +a" >> "$shell_rc"
        echo "fi" >> "$shell_rc"
        log_success "Added credential loading to $shell_rc"
    else
        log_info "Shell integration already exists"
    fi
}

# Main setup function
main() {
    log_info "Setting up secure Bitwarden credentials for Chezmoi..."

    check_root
    setup_credentials_directory
    prompt_credentials
    store_credentials
    test_credentials
    create_shell_integration

    log_success "Bitwarden credentials setup completed!"
    log_info "You can now run: ./scripts/deploy-chezmoi.sh"
}

# Run main function
main "$@"