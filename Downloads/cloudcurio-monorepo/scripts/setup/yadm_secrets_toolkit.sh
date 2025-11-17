#!/usr/bin/env bash
# ============================================================================
# Script Name: yadm_secrets_toolkit.sh
# Author: ChatGPT for cbwinslow
# Date: 2025-11-16
# Version: 0.1.1
# 
# Summary:
#   Helper toolkit for integrating yadm, SSH key templates, and Bitwarden
#   (bw / bws CLI) into a reusable secrets workflow.
#
#   Main capabilities:
#     - Initialize opinionated yadm templates for SSH config and private key
#       locations, using yadm's template system.
#     - Create a yadm bootstrap script that can materialize secrets from
#       Bitwarden into local files (SSH keys, tokens, .env files).
#     - Provide an 'apply' action to pull secrets from Bitwarden into the
#       filesystem, with correct permissions and minimal logging.
#
# Inputs:
#   Command-line arguments:
#     init-templates  - Create SSH/yadm template files and Bitwarden config.
#     apply           - Fetch secrets from Bitwarden into files as per config.
#     check           - Run basic diagnostics.
#
# Outputs:
#   - Template files under $HOME managed by yadm:
#       ~/.ssh/config##template
#       ~/.ssh/authorized_keys##template (optional skeleton)
#   - yadm bootstrap script:
#       ~/.config/yadm/bootstrap
#   - Bitwarden mapping config (non-secret metadata only):
#       ~/.config/yadm/bitwarden-secrets.conf
#
# Parameters / Environment:
#   YADM_SECRETS_CONFIG   - Path to the Bitwarden mapping config
#                           (default: ~/.config/yadm/bitwarden-secrets.conf)
#   BW_CMD                - Override path/name of 'bw' cli
#   BWS_CMD               - Override path/name of 'bws' cli
#
# Security Notes:
#   - Secrets are NEVER written into this script or into the mapping config.
#     Only Bitwarden item IDs / names and target paths are stored.
#   - Files created from secrets are chmod'ed to restrictive modes.
#   - The script assumes you have already logged in / unlocked Bitwarden
#     ('bw' with BW_SESSION, or 'bws' with its access token).
#
# Modification Log:
#   0.1.0 - 2025-11-16 - Initial version.
#   0.1.1 - 2025-11-16 - Fix function call syntax in init-templates branch.
# ============================================================================

set -euo pipefail

SCRIPT_NAME="$(basename "${BASH_SOURCE[0]:-$0}")"
LOG_FILE="/tmp/CBW-${SCRIPT_NAME%.sh}.log"

# ----------------------------------------------------------------------------
# Logging helpers
# ----------------------------------------------------------------------------

log() {
  local level="$1"; shift
  local msg="$*"
  local ts
  ts="$(date +"%Y-%m-%d %H:%M:%S")"
  printf '[%s] [%s] %s\n' "$ts" "$level" "$msg" | tee -a "$LOG_FILE" >&2
}

info()  { log "INFO"  "$*"; }
warn()  { log "WARN"  "$*"; }
error() { log "ERROR" "$*"; }

die() {
  error "$*"
  exit 1
}

# ----------------------------------------------------------------------------
# Global constants / defaults
# ----------------------------------------------------------------------------

YADM_SECRETS_CONFIG="${YADM_SECRETS_CONFIG:-$HOME/.config/yadm/bitwarden-secrets.conf}"
YADM_BOOTSTRAP_PATH="${HOME}/.config/yadm/bootstrap"
SSH_DIR="${HOME}/.ssh"

BW_CMD_DEFAULT="bw"
BWS_CMD_DEFAULT="bws"
BW_CMD="${BW_CMD:-$BW_CMD_DEFAULT}"
BWS_CMD="${BWS_CMD:-$BWS_CMD_DEFAULT}"

# ----------------------------------------------------------------------------
# Utility helpers
# ----------------------------------------------------------------------------

ensure_dir() {
  local dir="$1"
  if [[ ! -d "$dir" ]]; then
    info "Creating directory: $dir"
    mkdir -p "$dir"
  fi
}

require_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    return 1
  fi
  return 0
}

yadm_repo_path() {
  # Returns yadm repo path or empty string if yadm not available.
  if ! require_cmd yadm; then
    echo ""
    return 0
  fi
  # yadm introspect repo prints the repo path.
  local repo
  if ! repo="$(yadm introspect repo 2>/dev/null)"; then
    echo ""
  else
    echo "$repo"
  fi
}

# ----------------------------------------------------------------------------
# Bitwarden helpers (bw and bws)
# ----------------------------------------------------------------------------

detect_bitwarden_backend() {
  # Prefer bws (Bitwarden Secrets Manager) if available, else bw.
  if require_cmd "$BWS_CMD"; then
    echo "bws"
  elif require_cmd "$BW_CMD"; then
    echo "bw"
  else
    echo "none"
  fi
}

bw_get_field() {
  # Generic helper to get a field from Bitwarden.
  # Arguments differ depending on backend; see comments.
  #
  # Usage examples (see apply_secrets_from_config):
  #   bw_get_field "bw"  "item-id-or-name" "field-name"
  #   bw_get_field "bws" "secret-name"     ""   # bws uses names directly
  #
  local backend="$1"; shift
  local ref="$1"; shift
  local field="${1:-}"

  case "$backend" in
    bw)
      # For bw, we expect the user has a BW_SESSION already exported.
      # We fetch the full item JSON then extract a field.
      if [[ -z "${BW_SESSION:-}" ]]; then
        warn "BW_SESSION not set; 'bw' may prompt for unlock."
      fi
      # shellcheck disable=SC2086 # ref/field intentionally unquoted in jq expr
      "$BW_CMD" get item "$ref" | jq -r '
        .fields // [] | .[] | select(.name=="'""$field""'") | .value
      '
      ;;
    bws)
      # For bws, we expect BITWARDEN_ACCESS_TOKEN or appropriate auth already configured.
      "$BWS_CMD" secret get "$ref" --output json | jq -r '.value'
      ;;
    *)
      die "Unsupported Bitwarden backend: $backend"
      ;;
  esac
}

# ----------------------------------------------------------------------------
# Config file format and helpers
# ----------------------------------------------------------------------------
#
# The mapping file is an INI-like format with simple sections and key-value
# pairs, designed to be easy to edit and parse without extra dependencies.
#
# Example ~/.config/yadm/bitwarden-secrets.conf
#
#   # Version marker (reserved for future use)
#   version = 1
#
#   [ssh:primary_ed25519:private]
#   backend = bw            # bw or bws
#   ref     = cbw-ssh-main  # For bw: item id or name; for bws: secret name
#   field   = private_key   # For bw: field name; for bws: ignored
#   path    = ~/.ssh/id_ed25519
#   mode    = 600
#
#   [ssh:primary_ed25519:public]
#   backend = bw
#   ref     = cbw-ssh-main
#   field   = public_key
#   path    = ~/.ssh/id_ed25519.pub
#   mode    = 644
#
#   [secret:github_token]
#   backend = bws
#   ref     = github/pat/main
#   path    = ~/.config/github/pat
#   mode    = 600
#
# Each section describes ONE file to be written.
# This is intentionally minimal but can be extended later.
#
# ----------------------------------------------------------------------------

create_default_config_if_missing() {
  local cfg="$YADM_SECRETS_CONFIG"

  if [[ -f "$cfg" ]]; then
    info "Bitwarden mapping config already exists: $cfg"
    return 0
  fi

  ensure_dir "$(dirname "$cfg")"

  cat >"$cfg" <<'EOF'
# ============================================================================
# Bitwarden -> Filesystem mapping for yadm & SSH secrets
# This file intentionally contains NO actual secrets.
#
# Each section defines one target file that should be materialized from
# Bitwarden (bw or bws). Uncomment and adjust to your environment.
#
# Field reference:
#   backend  - "bw" or "bws" (autodetected if omitted)
#   ref      - For "bw": item id or name; for "bws": secret name
#   field    - For "bw": field name; for "bws": ignored
#   path     - Target file path (tilde is allowed)
#   mode     - Octal file mode (e.g. 600, 644)
#
# After editing, run:
#   yadm_secrets_toolkit.sh apply
#
# ============================================================================

version = 1

# --- SSH key example (Bitwarden item with custom fields "private_key" and "public_key") ---

[ssh:primary_ed25519:private]
# backend = bw
# ref     = cbw-ssh-main
# field   = private_key
# path    = ~/.ssh/id_ed25519
# mode    = 600

[ssh:primary_ed25519:public]
# backend = bw
# ref     = cbw-ssh-main
# field   = public_key
# path    = ~/.ssh/id_ed25519.pub
# mode    = 644

# --- Generic secret example (Bitwarden Secrets Manager "bws") ---

[secret:github_token]
# backend = bws
# ref     = github/pat/main
# path    = ~/.config/github/pat
# mode    = 600

EOF

  chmod 600 "$cfg"
  info "Created default Bitwarden mapping config template at: $cfg"
}

expand_path() {
  # Expand leading "~" in a path safely.
  local p="$1"
  if [[ "$p" == ~* ]]; then
    eval "printf '%s' \"$p\""
  else
    printf '%s' "$p"
  fi
}

apply_secrets_from_config() {
  local cfg="$YADM_SECRETS_CONFIG"

  if [[ ! -f "$cfg" ]]; then
    die "Config file not found: $cfg. Run '$SCRIPT_NAME init-templates' first."
  fi

  local backend_auto
  backend_auto="$(detect_bitwarden_backend)"
  if [[ "$backend_auto" == "none" ]]; then
    die "No Bitwarden CLI found (bw or bws). Please install and configure one."
  fi
  info "Detected Bitwarden backend: $backend_auto"

  local section=""
  local line key value backend ref field path mode

  while IFS='' read -r line || [[ -n "$line" ]]; do
    # Strip leading/trailing whitespace
    line="${line#"${line%%[![:space:]]*}"}"
    line="${line%"${line##*[![:space:]]}"}"

    # Skip comments/blank lines
    [[ -z "$line" ]] && continue
    [[ "$line" =~ ^# ]] && continue

    if [[ "$line" =~ ^\[.*\]$ ]]; then
      section="${line:1:${#line}-2}"
      backend="$backend_auto"
      ref=""
      field=""
      path=""
      mode=""
      info "Processing section: [$section]"
      continue
    fi

    # Parse key = value
    if [[ "$line" =~ ^([a-zA-Z0-9_]+)[[:space:]]*=[[:space:]]*(.*)$ ]]; then
      key="${BASH_REMATCH[1]}"
      value="${BASH_REMATCH[2]}"
      # Remove possible surrounding quotes
      value="${value%\"}"; value="${value#\"}"
      value="${value%\'}"; value="${value#\'}"

      case "$key" in
        backend) backend="$value" ;;
        ref)     ref="$value" ;;
        field)   field="$value" ;;
        path)    path="$value" ;;
        mode)    mode="$value" ;;
        version) ;; # ignore global
        *)
          warn "Unknown key '$key' in $cfg (section [$section])"
          ;;
      esac

      # When we have all required parameters for a section, try to apply it.
      if [[ -n "$section" && -n "$ref" && -n "$path" && -n "$mode" ]]; then
        local target backend_effective
        backend_effective="${backend:-$backend_auto}"
        target="$(expand_path "$path")"

        info "Materializing secret for [$section] -> $target (backend=$backend_effective, ref=$ref, field=$field)"

        local secret_value
        if ! secret_value="$(bw_get_field "$backend_effective" "$ref" "$field")"; then
          warn "Failed to retrieve secret for [$section]. Skipping."
        elif [[ -z "$secret_value" || "$secret_value" == "null" ]]; then
          warn "Secret value empty for [$section] (ref=$ref field=$field). Skipping."
        else
          ensure_dir "$(dirname "$target")"
          umask 177
          printf '%s\n' "$secret_value" >"$target"
          chmod "$mode" "$target"
          info "Wrote secret to $target with mode $mode"
        fi

        # Reset fields to avoid reusing for subsequent lines
        ref=""
        field=""
        path=""
        mode=""
      fi
    fi
  done <"$cfg"

  info "Finished applying secrets from config."
}

# ----------------------------------------------------------------------------
# yadm SSH templates
# ----------------------------------------------------------------------------

create_ssh_templates() {
  ensure_dir "$SSH_DIR"

  local ssh_config_tpl="${SSH_DIR}/config##template"
  local auth_keys_tpl="${SSH_DIR}/authorized_keys##template"

  if [[ -f "$ssh_config_tpl" ]]; then
    info "SSH config template already exists: $ssh_config_tpl"
  else
    cat >"$ssh_config_tpl" <<'EOF'
# ~/.ssh/config - yadm template
# WARNING: This file is generated from ~/.ssh/config##template by yadm.
# Edit the template, not the generated config.
#
# yadm template variables available (examples):
#   {{ yadm.user }}      - current user
#   {{ yadm.hostname }}  - hostname (no domain)
#   {{ yadm.os }}        - OS name (Linux, Darwin, etc.)
#
# You can use {% if ... %} blocks to customize per-host/OS if desired.

Host *
  ForwardAgent no
  ServerAliveInterval 60
  ServerAliveCountMax 3
  # Use the primary SSH key managed via Bitwarden:
  IdentityFile ~/.ssh/id_ed25519
  IdentitiesOnly yes
  StrictHostKeyChecking ask
  UserKnownHostsFile ~/.ssh/known_hosts
  Compression yes

# Example: cbwdellr720 over ZeroTier
Host cbwdellr720_zt
  HostName 172.28.82.205
  User cbwinslow
  IdentityFile ~/.ssh/id_ed25519
  IdentitiesOnly yes

# Example: cbwdellr720 over Tailscale
Host cbwdellr720_ts
  HostName 100.90.23.59
  User cbwinslow
  IdentityFile ~/.ssh/id_ed25519
  IdentitiesOnly yes

# Example: GitHub
Host github.com
  User git
  HostName github.com
  IdentityFile ~/.ssh/id_ed25519
  IdentitiesOnly yes

EOF
    chmod 600 "$ssh_config_tpl"
    info "Created SSH config template: $ssh_config_tpl"
  fi

  if [[ -f "$auth_keys_tpl" ]]; then
    info "authorized_keys template already exists: $auth_keys_tpl"
  else
    cat >"$auth_keys_tpl" <<'EOF'
# ~/.ssh/authorized_keys - yadm template
# WARNING: This file is generated from ~/.ssh/authorized_keys##template by yadm.
# Edit the template, not the generated file.
#
# Add your public keys here. Example Bitwarden-synced key:
#
# ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINIEs0Bgiq6JOaoYOUUcJgsgIs1MM0KqhwTF5W+Y1Hq3 cbwinslow@bitwarden
#
# You can manage keys via SyncThing, scripts, or manual edit of this template.

EOF
    chmod 600 "$auth_keys_tpl"
    info "Created authorized_keys template: $auth_keys_tpl"
  fi
}

# ----------------------------------------------------------------------------
# yadm bootstrap integration
# ----------------------------------------------------------------------------

create_yadm_bootstrap() {
  ensure_dir "$(dirname "$YADM_BOOTSTRAP_PATH")"

  if [[ -f "$YADM_BOOTSTRAP_PATH" ]]; then
    info "yadm bootstrap already exists: $YADM_BOOTSTRAP_PATH"
    warn "Review it and manually integrate a call to: $SCRIPT_NAME apply"
    return 0
  fi

  cat >"$YADM_BOOTSTRAP_PATH" <<EOF
#!/usr/bin/env bash
# ============================================================================
# yadm bootstrap for cbwinslow
# Generated by $SCRIPT_NAME
#
# This script runs after cloning or updating your yadm repo. It is a good
# place to materialize secrets (SSH keys, tokens, etc.) from Bitwarden using
# the yadm_secrets_toolkit.sh script.
# ============================================================================

set -euo pipefail

TOOLKIT="\${HOME}/bin/yadm_secrets_toolkit.sh"

if [[ -x "\$TOOLKIT" ]]; then
  echo "[yadm-bootstrap] Applying Bitwarden secrets via \$TOOLKIT ..."
  "\$TOOLKIT" apply
else
  echo "[yadm-bootstrap] WARNING: Toolkit script not found or not executable: \$TOOLKIT"
  echo "[yadm-bootstrap]         Please install it and then run '\$TOOLKIT apply' manually."
fi

EOF

  chmod +x "$YADM_BOOTSTRAP_PATH"
  info "Created yadm bootstrap script: $YADM_BOOTSTRAP_PATH"
  info "Remember to add and commit it with: yadm add $YADM_BOOTSTRAP_PATH && yadm commit"
}

# ----------------------------------------------------------------------------
# Diagnostics
# ----------------------------------------------------------------------------

run_diagnostics() {
  info "Running diagnostics for $SCRIPT_NAME"

  local repo
  repo="$(yadm_repo_path || true)"
  if [[ -n "$repo" ]]; then
    info "yadm repo detected at: $repo"
  else
    warn "No yadm repo detected (yadm introspect repo). Are you inside your main environment?"
  fi

  if require_cmd "$BW_CMD"; then
    info "Found Bitwarden CLI 'bw' as: $(command -v "$BW_CMD")"
  else
    warn "Bitwarden CLI 'bw' not found."
  fi

  if require_cmd "$BWS_CMD"; then
    info "Found Bitwarden Secrets Manager CLI 'bws' as: $(command -v "$BWS_CMD")"
  else
    warn "Bitwarden Secrets Manager CLI 'bws' not found."
  fi

  if [[ -f "$YADM_SECRETS_CONFIG" ]]; then
    info "Config file exists: $YADM_SECRETS_CONFIG"
  else
    warn "Config file missing: $YADM_SECRETS_CONFIG"
  fi

  if [[ -f "$YADM_BOOTSTRAP_PATH" ]]; then
    info "yadm bootstrap exists: $YADM_BOOTSTRAP_PATH"
  else
    warn "yadm bootstrap missing: $YADM_BOOTSTRAP_PATH"
  fi

  info "Diagnostics finished. See $LOG_FILE for full log."
}

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

usage() {
  cat <<EOF
$SCRIPT_NAME - yadm + SSH + Bitwarden integration toolkit

Usage:
  $SCRIPT_NAME init-templates   # Create SSH/yadm templates and default Bitwarden config
  $SCRIPT_NAME apply            # Materialize secrets from Bitwarden into files
  $SCRIPT_NAME check            # Run diagnostics

Environment:
  YADM_SECRETS_CONFIG   Path to mapping config (default: $YADM_SECRETS_CONFIG)
  BW_CMD                Override bw CLI command (default: $BW_CMD_DEFAULT)
  BWS_CMD               Override bws CLI command (default: $BWS_CMD_DEFAULT)

Typical workflow:
  1) Save this script as ~/bin/yadm_secrets_toolkit.sh and make it executable.
  2) Run:  ~/bin/yadm_secrets_toolkit.sh init-templates
  3) Edit: $YADM_SECRETS_CONFIG to point at your Bitwarden items/secrets.
  4) Run:  ~/bin/yadm_secrets_toolkit.sh apply
  5) Commit templates & bootstrap with yadm.

EOF
}

main() {
  local cmd="${1:-}"
  if [[ -z "$cmd" ]]; then
    usage
    exit 1
  fi

  case "$cmd" in
    init-templates)
      info "Initializing yadm SSH templates and Bitwarden config ..."
      create_ssh_templates
      create_default_config_if_missing
      create_yadm_bootstrap
      info "Initialization complete. Now edit: $YADM_SECRETS_CONFIG"
      ;;
    apply)
      info "Applying secrets from Bitwarden config ..."
      apply_secrets_from_config
      ;;
    check)
      run_diagnostics
      ;;
    -h|--help|help)
      usage
      ;;
    *)
      usage
      die "Unknown command: $cmd"
      ;;
  esac
}

main "$@"
