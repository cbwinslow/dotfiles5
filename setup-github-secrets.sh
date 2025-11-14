#!/usr/bin/env bash
set -euo pipefail

# Script to set up GitHub secrets for GitLab auto-sync using Bitwarden
# This script retrieves the GitLab token and repo URL from Bitwarden
# and sets them as GitHub repository secrets

# Configuration
GITHUB_REPO="${GITHUB_REPO:-foomanchu8008/chezmoi}"  # Change this to your GitHub repo
BW_SESSION_FILE="${HOME}/.bw_session"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if GitHub CLI is available
if ! command -v gh >/dev/null 2>&1; then
    error "GitHub CLI (gh) is not installed. Please install it first:"
    echo "  curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg"
    echo "  echo \"deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main\" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null"
    echo "  sudo apt update && sudo apt install gh"
    exit 1
fi

# Check if Bitwarden CLI is available
if ! command -v bw >/dev/null 2>&1; then
    error "Bitwarden CLI (bw) is not installed. Please install it first."
    exit 1
fi

# Check if jq is available
if ! command -v jq >/dev/null 2>&1; then
    error "jq is not installed. Please install it first."
    exit 1
fi

# Unlock Bitwarden if not already unlocked
if [[ ! -f "$BW_SESSION_FILE" ]] || ! bw status --session "$(cat "$BW_SESSION_FILE")" >/dev/null 2>&1; then
    log "Bitwarden vault is locked. Unlocking..."

    if [[ -n "${BW_PASSWORD:-}" ]]; then
        log "Using BW_PASSWORD environment variable"
        BW_SESSION=$(bw unlock --raw "$BW_PASSWORD")
    else
        log "Please enter your Bitwarden master password:"
        BW_SESSION=$(bw unlock --raw)
    fi

    echo "$BW_SESSION" > "$BW_SESSION_FILE"
    chmod 600 "$BW_SESSION_FILE"
else
    BW_SESSION=$(cat "$BW_SESSION_FILE")
fi

export BW_SESSION

# Verify we can access the vault
if ! bw list items --session "$BW_SESSION" >/dev/null 2>&1; then
    error "Cannot access Bitwarden vault. Please check your credentials."
    exit 1
fi

log "Successfully connected to Bitwarden vault"

# Function to get secret from Bitwarden
get_bw_secret() {
    local item_name="$1"
    local field="${2:-password}"

    # Try different methods to get the secret
    local secret=""

    # Method 1: Get password directly
    secret=$(bw get password "$item_name" --session "$BW_SESSION" 2>/dev/null) || true

    # Method 2: Get item and extract field
    if [[ -z "$secret" ]]; then
        secret=$(bw get item "$item_name" --session "$BW_SESSION" 2>/dev/null | jq -r ".login.$field // empty" 2>/dev/null) || true
    fi

    # Method 3: Get from custom fields
    if [[ -z "$secret" ]]; then
        secret=$(bw get item "$item_name" --session "$BW_SESSION" 2>/dev/null | jq -r ".fields[]? | select(.name==\"$field\") | .value" 2>/dev/null) || true
    fi

    if [[ -z "$secret" ]] || [[ "$secret" == "null" ]]; then
        warn "Could not find $field for item '$item_name'"
        return 1
    fi

    echo "$secret"
}

# Get GitLab token
log "Retrieving GitLab token from Bitwarden..."
GITLAB_TOKEN=$(get_bw_secret "gitlab" "password") || GITLAB_TOKEN=$(get_bw_secret "gitlab-token") || GITLAB_TOKEN=$(get_bw_secret "gitlab token")

if [[ -z "$GITLAB_TOKEN" ]]; then
    error "Could not find GitLab token in Bitwarden. Please ensure you have an item named 'gitlab', 'gitlab-token', or 'gitlab token' with the token in the password field."
    exit 1
fi

log "Found GitLab token (length: ${#GITLAB_TOKEN})"

# Get GitLab repository URL
log "Retrieving GitLab repository URL from Bitwarden..."
GITLAB_REPO_URL=$(get_bw_secret "gitlab-repo" "url") || GITLAB_REPO_URL=$(get_bw_secret "gitlab-repo-url") || GITLAB_REPO_URL=$(get_bw_secret "gitlab repository")

if [[ -z "$GITLAB_REPO_URL" ]]; then
    warn "Could not find GitLab repository URL in Bitwarden. Please enter it manually:"
    read -r GITLAB_REPO_URL
fi

if [[ -z "$GITLAB_REPO_URL" ]]; then
    error "GitLab repository URL is required."
    exit 1
fi

log "Found GitLab repository URL: $GITLAB_REPO_URL"

# Check if user is authenticated with GitHub CLI
if ! gh auth status >/dev/null 2>&1; then
    log "GitHub CLI is not authenticated. Please run 'gh auth login' first."
    exit 1
fi

# Set GitHub secrets
log "Setting up GitHub secrets for repository: $GITHUB_REPO"

log "Setting GITLAB_TOKEN secret..."
if echo "$GITLAB_TOKEN" | gh secret set GITLAB_TOKEN --repo "$GITHUB_REPO"; then
    log "✅ GITLAB_TOKEN secret set successfully"
else
    error "Failed to set GITLAB_TOKEN secret"
    exit 1
fi

log "Setting GITLAB_REPO_URL secret..."
if echo "$GITLAB_REPO_URL" | gh secret set GITLAB_REPO_URL --repo "$GITHUB_REPO"; then
    log "✅ GITLAB_REPO_URL secret set successfully"
else
    error "Failed to set GITLAB_REPO_URL secret"
    exit 1
fi

log "🎉 GitHub secrets setup completed successfully!"
log ""
log "The GitLab auto-sync workflow should now work. You can:"
echo "  - Wait for the next scheduled run (every 6 hours)"
echo "  - Trigger it manually from the GitHub Actions tab"
echo "  - Check the Actions tab to monitor sync status"

# Clean up session file for security
if [[ -f "$BW_SESSION_FILE" ]]; then
    rm -f "$BW_SESSION_FILE"
    log "Cleaned up Bitwarden session file"
fi