#!/bin/bash
# Chezmoi Health Monitor
# Monitors the health and status of chezmoi configuration

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

# Check if chezmoi is installed
check_chezmoi_installation() {
    if ! command -v chezmoi &> /dev/null; then
        log_error "Chezmoi is not installed"
        return 1
    fi
    log_success "Chezmoi is installed"
}

# Check chezmoi repository status
check_repository_status() {
    local chezmoi_dir="$HOME/.local/share/chezmoi"

    if [[ ! -d "$chezmoi_dir/.git" ]]; then
        log_error "Chezmoi directory is not a git repository"
        return 1
    fi

    # Check for uncommitted changes
    if [[ -n $(cd "$chezmoi_dir" && git status --porcelain) ]]; then
        log_warning "Uncommitted changes in chezmoi repository"
    else
        log_success "Repository is clean"
    fi

    # Check if behind remote
    local behind_count=$(cd "$chezmoi_dir" && git rev-list HEAD...origin/main --count 2>/dev/null || echo "0")
    if [[ "$behind_count" -gt 0 ]]; then
        log_warning "Repository is $behind_count commits behind remote"
    else
        log_success "Repository is up to date"
    fi
}

# Check Bitwarden integration
check_bitwarden_integration() {
    # Check if bw is available
    if ! command -v bw &> /dev/null; then
        log_error "Bitwarden CLI is not installed"
        return 1
    fi

    # Check if credentials are configured
    if [[ ! -f "$HOME/.config/chezmoi/credentials.env" ]]; then
        log_error "Bitwarden credentials not configured"
        return 1
    fi

    # Check if vault is unlocked
    local status=$(bw status | jq -r '.status' 2>/dev/null || echo "unknown")
    case "$status" in
        "unlocked")
            log_success "Bitwarden vault is unlocked"
            ;;
        "locked")
            log_warning "Bitwarden vault is locked"
            ;;
        *)
            log_error "Bitwarden status unknown: $status"
            return 1
            ;;
    esac
}

# Check template rendering
check_template_rendering() {
    local chezmoi_dir="$HOME/.local/share/chezmoi"

    # Find all .tmpl files
    local tmpl_files=$(find "$chezmoi_dir" -name "*.tmpl" -type f)

    for tmpl_file in $tmpl_files; do
        local relative_path=${tmpl_file#"$chezmoi_dir/"}
        local target_file=${relative_path%.tmpl}

        log_info "Checking template: $relative_path"

        # Try to render template
        if ! chezmoi cat "$target_file" &> /dev/null; then
            log_error "Failed to render template: $relative_path"
            return 1
        fi
    done

    log_success "All templates render successfully"
}

# Check for configuration drift
check_configuration_drift() {
    log_info "Checking for configuration drift..."

    # Get list of files that would be changed
    local drift_files=$(chezmoi status --porcelain 2>/dev/null | wc -l)

    if [[ "$drift_files" -gt 0 ]]; then
        log_warning "Configuration drift detected: $drift_files files differ"
        chezmoi status
    else
        log_success "No configuration drift detected"
    fi
}

# Check secret expiry (if applicable)
check_secret_expiry() {
    log_info "Checking for expired secrets..."

    # This would need to be customized based on your secret storage
    # For now, just check if key files exist and are readable
    local key_files=(
        "$HOME/.ssh/id_ed25519_github"
        "$HOME/.ssh/id_ed25519_gitlab"
        "$HOME/.ssh/id_rsa_personal"
        "$HOME/.ssh/id_rsa_work"
    )

    for key_file in "${key_files[@]}"; do
        if [[ -f "$key_file" ]]; then
            # Check if key is readable
            if [[ ! -r "$key_file" ]]; then
                log_error "SSH key not readable: $key_file"
            else
                log_success "SSH key accessible: $(basename "$key_file")"
            fi
        fi
    done
}

# Generate health report
generate_report() {
    local report_file="$HOME/.cache/chezmoi/health-report-$(date +%Y%m%d-%H%M%S).txt"

    {
        echo "Chezmoi Health Report - $(date)"
        echo "=================================="
        echo ""
        echo "System Information:"
        echo "- OS: $(uname -s)"
        echo "- Hostname: $(hostname)"
        echo "- User: $(whoami)"
        echo ""
        echo "Chezmoi Status:"
        chezmoi --version
        echo ""
        echo "Repository Status:"
        cd "$HOME/.local/share/chezmoi" && git status --short
        echo ""
        echo "Configuration Drift:"
        chezmoi status
    } > "$report_file"

    log_info "Health report saved to: $report_file"
}

# Main monitoring function
main() {
    log_info "Starting Chezmoi health check..."

    local exit_code=0

    # Run all checks
    check_chezmoi_installation || exit_code=1
    check_repository_status || exit_code=1
    check_bitwarden_integration || exit_code=1
    check_template_rendering || exit_code=1
    check_configuration_drift || exit_code=1
    check_secret_expiry || exit_code=1

    # Generate report
    generate_report

    if [[ $exit_code -eq 0 ]]; then
        log_success "All health checks passed"
    else
        log_error "Some health checks failed"
    fi

    return $exit_code
}

# Run main function
main "$@"