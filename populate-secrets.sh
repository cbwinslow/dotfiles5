#!/usr/bin/env bash
set -euo pipefail
set -x

# Script to populate SSH and API key secrets from Bitwarden into chezmoi data
# This updates the secrets/ssh-secrets.yaml file with actual values from Bitwarden

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SECRETS_FILE="$SCRIPT_DIR/secrets/ssh-secrets.yaml"
SESSION_FILE="${HOME}/.bw_session"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Check if yq is available for YAML processing
if ! command -v yq >/dev/null 2>&1; then
    log "yq is not installed. Installing..."
    # Try to install yq
    if command -v snap >/dev/null 2>&1; then
        sudo snap install yq
    elif command -v apt >/dev/null 2>&1; then
        sudo apt update && sudo apt install -y yq
    else
        log "Please install yq manually: https://github.com/mikefarah/yq"
        exit 1
    fi
fi

# Unlock Bitwarden if needed
if [[ ! -f "$SESSION_FILE" ]] || ! bw status --session "$(cat "$SESSION_FILE" 2>/dev/null)" >/dev/null 2>&1; then
    log "Bitwarden vault is locked. Attempting to unlock..."

    if [[ -n "${BW_PASSWORD:-}" ]]; then
        BW_SESSION=$(bw unlock --raw "$BW_PASSWORD" 2>/dev/null)
        echo "$BW_SESSION" > "$SESSION_FILE"
        chmod 600 "$SESSION_FILE"
    else
        echo "Please enter your Bitwarden master password:"
        BW_SESSION=$(bw unlock --raw)
        echo "$BW_SESSION" > "$SESSION_FILE"
        chmod 600 "$SESSION_FILE"
    fi
else
    BW_SESSION=$(cat "$SESSION_FILE")
fi

export BW_SESSION

log "Searching for SSH keys and API tokens in Bitwarden..."

# Function to get secret value from Bitwarden item
get_bw_value() {
    local item_name="$1"
    local field="${2:-password}"

    # Try different methods to get the value
    local value=""

    # Method 1: Get password directly
    value=$(bw get password "$item_name" --session "$BW_SESSION" 2>/dev/null) || true

    # Method 2: Get item and extract field
    if [[ -z "$value" ]]; then
        value=$(bw get item "$item_name" --session "$BW_SESSION" 2>/dev/null | jq -r ".login.$field // empty" 2>/dev/null) || true
    fi

    # Method 3: Get from custom fields
    if [[ -z "$value" ]]; then
        value=$(bw get item "$item_name" --session "$BW_SESSION" 2>/dev/null | jq -r ".fields[]? | select(.name==\"$field\") | .value" 2>/dev/null) || true
    fi

    echo "$value"
}

# Function to detect SSH key type


get_ssh_key_type() {
    local key_content="$1"
    if [[ "$key_content" == *BEGIN\ RSA* ]]; then # Use glob matching for simplicity
        echo "rsa"
    elif [[ "$key_content" == *BEGIN\ EC* ]]; then
        echo "ecdsa"
    elif [[ "$key_content" == *BEGIN\ OPENSSH* ]]; then
        echo "ed25519"
    elif [[ "$key_content" == *BEGIN\ DSA* ]]; then
        echo "dsa"
    else
        echo "unknown"
    fi
}

# Search for SSH keys
log "Searching for SSH keys..."
bw list items --session "$BW_SESSION" 2>/dev/null | jq -c '.[]' | while read -r item; do
    name=$(echo "$item" | jq -r '.name')
    id=$(echo "$item" | jq -r '.id')

    # Check password field for SSH keys
    password=$(echo "$item" | jq -r '.login.password // empty')
    if [[ -n "$password" ]] && [[ "$password" != "null" ]]; then
        if [[ "$password" =~ ^-----BEGIN ]]; then
            key_type=$(get_ssh_key_type "$password")
            log "Found SSH $key_type private key: $name"

            # Determine which config variable to update based on name
            if [[ "$name" =~ (?i)github ]]; then
                if [[ "$key_type" == "ed25519" ]]; then
                    yq -i ".ssh_key_ed25519_github = \"$password\"" "$SECRETS_FILE"
                    yq -i ".ssh_key_ed25519_github_name = \"$name\"" "$SECRETS_FILE"
                elif [[ "$key_type" == "rsa" ]]; then
                    yq -i ".ssh_key_rsa_github = \"$password\"" "$SECRETS_FILE"
                    yq -i ".ssh_key_rsa_github_name = \"$name\"" "$SECRETS_FILE"
                fi
            elif [[ "$name" =~ (?i)gitlab ]]; then
                if [[ "$key_type" == "ed25519" ]]; then
                    yq -i ".ssh_key_ed25519_gitlab = \"$password\"" "$SECRETS_FILE"
                    yq -i ".ssh_key_ed25519_gitlab_name = \"$name\"" "$SECRETS_FILE"
                elif [[ "$key_type" == "rsa" ]]; then
                    yq -i ".ssh_key_rsa_gitlab = \"$password\"" "$SECRETS_FILE"
                    yq -i ".ssh_key_rsa_gitlab_name = \"$name\"" "$SECRETS_FILE"
                fi
            elif [[ "$name" =~ (?i)personal ]]; then
                if [[ "$key_type" == "rsa" ]]; then
                    yq -i ".ssh_key_rsa_personal = \"$password\"" "$SECRETS_FILE"
                    yq -i ".ssh_key_rsa_personal_name = \"$name\"" "$SECRETS_FILE"
                fi
            elif [[ "$name" =~ (?i)work ]]; then
                if [[ "$key_type" == "rsa" ]]; then
                    yq -i ".ssh_key_rsa_work = \"$password\"" "$SECRETS_FILE"
                    yq -i ".ssh_key_rsa_work_name = \"$name\"" "$SECRETS_FILE"
                fi
            fi
        fi
    fi

    # Check custom fields for SSH keys
    echo "$item" | jq -c '.fields[]?' 2>/dev/null | while read -r field; do
        field_name=$(echo "$field" | jq -r '.name')
        field_value=$(echo "$field" | jq -r '.value')

        if [[ -n "$field_value" ]] && [[ "$field_value" =~ ^-----BEGIN ]]; then
            key_type=$(get_ssh_key_type "$field_value")
            log "Found SSH $key_type private key in field '$field_name': $name"

            # Similar logic as above for field-based keys
            if [[ "$name" =~ (?i)github ]] || [[ "$field_name" =~ (?i)github ]]; then
                if [[ "$key_type" == "ed25519" ]]; then
                    yq -i ".ssh_key_ed25519_github = \"$field_value\"" "$SECRETS_FILE"
                    yq -i ".ssh_key_ed25519_github_name = \"$name ($field_name)\"" "$SECRETS_FILE"
                elif [[ "$key_type" == "rsa" ]]; then
                    yq -i ".ssh_key_rsa_github = \"$field_value\"" "$SECRETS_FILE"
                    yq -i ".ssh_key_rsa_github_name = \"$name ($field_name)\"" "$SECRETS_FILE"
                fi
            # Add similar logic for other services...
            fi
        fi
    done
done

# Search for API keys and tokens
log "Searching for API keys and tokens..."

# Common API key patterns to search for
api_patterns=(
    "github.*token:github_token"
    "gitlab.*token:gitlab_token"
    "openai.*api:key:openai_api_key"
    "anthropic.*api:key:anthropic_api_key"
    "openrouter.*api:key:openrouter_api_key"
)

for pattern in "${api_patterns[@]}"; do
    IFS=':' read -r search_pattern yaml_key <<< "$pattern"

    # Search for items matching the pattern
    bw list items --session "$BW_SESSION" 2>/dev/null | jq -c '.[]' | while read -r item; do
        name=$(echo "$item" | jq -r '.name')

        if [[ "$name" =~ (?i)$search_pattern ]]; then
            value=$(get_bw_value "$name")
            if [[ -n "$value" ]] && [[ "$value" != "null" ]]; then
                log "Found $yaml_key: $name"
                yq -i ".$yaml_key = \"$value\"" "$SECRETS_FILE"
            fi
        fi
    done
done

# Search in custom fields for API keys
bw list items --session "$BW_SESSION" 2>/dev/null | jq -c '.[]' | while read -r item; do
    name=$(echo "$item" | jq -r '.name')

    echo "$item" | jq -c '.fields[]?' 2>/dev/null | while read -r field; do
        field_name=$(echo "$field" | jq -r '.name')
        field_value=$(echo "$field" | jq -r '.value')

        if [[ -n "$field_value" ]] && [[ "$field_value" != "null" ]]; then
            # Check if field name indicates an API key
            lower_field_name=$(echo "$field_name" | tr '[:upper:]' '[:lower:]')
            if [[ "$lower_field_name" =~ (api.?key|token|secret|key) ]]; then
                log "Found API key in field '$field_name': $name"

                # Map to appropriate YAML key
                if [[ "$field_name" =~ (?i)github ]]; then
                    yq -i ".github_token = \"$field_value\"" "$SECRETS_FILE"
                elif [[ "$field_name" =~ (?i)gitlab ]]; then
                    yq -i ".gitlab_token = \"$field_value\"" "$SECRETS_FILE"
                elif [[ "$field_name" =~ (?i)openai ]]; then
                    yq -i ".openai_api_key = \"$field_value\"" "$SECRETS_FILE"
                elif [[ "$field_name" =~ (?i)anthropic ]]; then
                    yq -i ".anthropic_api_key = \"$field_value\"" "$SECRETS_FILE"
                elif [[ "$field_name" =~ (?i)openrouter ]]; then
                    yq -i ".openrouter_api_key = \"$field_value\"" "$SECRETS_FILE"
                fi
            fi
        fi
    done
done

log "Secrets population completed!"
log "Updated: $SECRETS_FILE"
log "Run 'chezmoi apply' to apply the new SSH keys and configurations."