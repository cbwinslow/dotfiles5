#!/usr/bin/env bash
# ============================================================================
# Script: cbw-ssh-key-trade.sh
# Date: 2025-11-07
# Author: cbwinslow <blaine.winslow@gmail.com>
# Summary: Idempotent "key trade" utility to exchange SSH public keys,
#          maintain authorized_keys, ssh config, and known_hosts entries
#          between the local machine (origin) and one or more remote
#          destination machines. Safe to run repeatedly.
#
# Features:
#  - Generates an ed25519 keypair if local key is missing (optionally RSA)
#  - Appends public keys to remote ~/.ssh/authorized_keys idempotently
#  - Retrieves remote public keys and stores them locally in ~/.ssh/remote-<host>.pub
#  - Adds remote host keys to local ~/.ssh/known_hosts (via ssh-keyscan)
#  - Optionally updates remote ~/.ssh/known_hosts with this origin's host key
#  - Creates/updates simple ~/.ssh/config host stanzas (identityfile + hostalias)
#  - Safe, verbose, supports --dry-run and --force
#
# Inputs / arguments:
#   -r|--remote USER@HOST[:PORT]   (repeatable) target to key-trade
#   --local-key PATH                (default: ~/.ssh/cbw_ed25519)
#   --rsa                          generate RSA keypair as well
#   --push-remote-known-hosts       attempt to add origin host key to remote known_hosts
#   --ssh-config-alias ALIAS        override Host alias used in ~/.ssh/config
#   --dry-run                       show actions but don't execute
#   --force                         overwrite local files when necessary
#   --help                          show usage
#
# Requirements:
#  - bash, ssh, scp, ssh-keygen, ssh-keyscan, awk, sed, mkdir, chmod
#  - remote must accept some kind of connection (password or key) initially
#
# Outputs:
#  - Local keys in ~/.ssh (private: restricted perms)
#  - Local known_hosts updated
#  - Remote ~/.ssh/authorized_keys updated
#  - /home/<remoteuser>/.ssh/known_hosts optionally updated
#
# Security notes:
#  - This script never transmits private keys to remote hosts.
#  - Private keys remain local only. Consider storing private keys in a
#    secure vault (Bitwarden CLI) after creation.
#
# Mod Log:
#  - 1.0.0 initial idempotent implementation
# ============================================================================
set -Eeuo pipefail
IFS=$'\n\t'

PROGRAM_NAME=$(basename "$0")
DRY_RUN=false
FORCE=false
GENERATE_RSA=false
PUSH_REMOTE_KNOWN=false
LOCAL_KEY_DEFAULT="$HOME/.ssh/cbw_ed25519"
LOCAL_KEY="$LOCAL_KEY_DEFAULT"
SSH_CONFIG_FILE="$HOME/.ssh/config"
KNOWN_HOSTS_FILE="$HOME/.ssh/known_hosts"
REMOTE_LIST=()

log(){ if ! $DRY_RUN; then echo -e "[+] $*"; else echo -e "[DRY] $*"; fi }
info(){ echo -e "[i] $*"; }
warn(){ echo -e "[!] $*" >&2; }
fail(){ echo -e "[x] $*" >&2; exit 1; }

usage(){ cat <<USAGE
Usage: $PROGRAM_NAME -r user@host[:port] [-r user2@host2] [options]
Options:
  -r, --remote USER@HOST[:PORT]   Remote target (repeatable)
  --local-key PATH                 Local private key path to use/create (default: $LOCAL_KEY_DEFAULT)
  --rsa                            Also generate RSA keypair (4096)
  --push-remote-known-hosts         Add origin host key to remote known_hosts
  --ssh-config-alias ALIAS          SSH config Host alias (default: derived from host)
  --dry-run                         Print actions but do not execute
  --force                           Overwrite existing local artifacts when required
  -h, --help                        Show help
Example:
  $PROGRAM_NAME -r cbwinslow@192.168.4.3 -r cbwinslow@192.168.4.10 --push-remote-known-hosts
USAGE
}

# --------------------------- arg parsing ------------------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    -r|--remote)
      shift; REM="$1"; REMOTE_LIST+=("$REM"); shift || true; ;;
    --local-key)
      shift; LOCAL_KEY="$1"; shift || true; ;;
    --rsa)
      GENERATE_RSA=true; shift || true; ;;
    --push-remote-known-hosts)
      PUSH_REMOTE_KNOWN=true; shift || true; ;;
    --ssh-config-alias)
      shift; SSH_ALIAS_OVERRIDE="$1"; shift || true; ;;
    --dry-run)
      DRY_RUN=true; shift || true; ;;
    --force)
      FORCE=true; shift || true; ;;
    -h|--help)
      usage; exit 0; ;;
    *) warn "Unknown argument: $1"; usage; exit 1; ;;
  esac
done

if [[ ${#REMOTE_LIST[@]} -eq 0 ]]; then
  warn "No remote hosts provided. Use -r user@host[:port] to specify at least one."; usage; exit 1
fi

# --------------------------- helpers ---------------------------------------
ensure_ssh_dir(){
  mkdir -p "$HOME/.ssh"
  chmod 700 "$HOME/.ssh"
  touch "$KNOWN_HOSTS_FILE"
  chmod 644 "$KNOWN_HOSTS_FILE"
}

generate_key_if_missing(){
  local priv="$1"
  if [[ -f "$priv" ]]; then
    info "Local key exists: $priv"
    return
  fi
  if $DRY_RUN; then
    info "(dry-run) Would generate ed25519 key at $priv"
    return
  fi
  info "Generating ed25519 key at $priv"
  ssh-keygen -t ed25519 -f "$priv" -C "cbwinslow <blaine.winslow@gmail.com> (auto)" -N "" || fail "ssh-keygen failed"
  chmod 600 "$priv"
}

generate_rsa_if_missing(){
  local priv_rsa="$1"
  if [[ -f "$priv_rsa" ]]; then info "RSA key exists: $priv_rsa"; return; fi
  if $DRY_RUN; then info "(dry-run) Would generate RSA key at $priv_rsa"; return; fi
  info "Generating RSA 4096 key at $priv_rsa"
  ssh-keygen -t rsa -b 4096 -f "$priv_rsa" -C "cbwinslow <blaine.winslow@gmail.com> (auto)" -N "" || fail "ssh-keygen rsa failed"
  chmod 600 "$priv_rsa"
}

append_if_missing(){
  # $1 file, $2 content
  local file="$1"; local content="$2"
  grep -Fxq -- "$content" "$file" 2>/dev/null || {
    if $DRY_RUN; then
      info "(dry-run) Would append to $file: $content"
    else
      echo "$content" >> "$file" && info "Appended to $file"
    fi
  }
}

remote_exec(){
  # run a command on remote; $1 is "user@host[:port]", rest are command pieces
  local target="$1"; shift
  if [[ "$target" =~ :[0-9]+$ ]]; then
    # parse port
    local hostpart port; hostpart="${target%%:*}"; port="${target##*:}"
    ssh -o StrictHostKeyChecking=no -p "$port" "$hostpart" "$@"
  else
    ssh -o StrictHostKeyChecking=no "$target" "$@"
  fi
}

scp_to_remote(){
  local src="$1"; local dest_target="$2"; local dest_path="$3"
  if [[ "$dest_target" =~ :[0-9]+$ ]]; then
    local hostpart port; hostpart="${dest_target%%:*}"; port="${dest_target##*:}"
    scp -P "$port" "$src" "$hostpart":"$dest_path"
  else
    scp "$src" "$dest_target":"$dest_path"
  fi
}

ssh_keyscan_to_file(){
  local host="$1"; local port_opt=""; local out="$2"
  if [[ "$host" =~ :[0-9]+$ ]]; then
    port="${host##*:}"
    host_noport="${host%%:*}"
    port_opt="-p $port"
    ssh-keyscan -T 5 -p "$port" "$host_noport" >> "$out" 2>/dev/null || true
  else
    ssh-keyscan -T 5 "$host" >> "$out" 2>/dev/null || true
  fi
}

# --------------------------- main ------------------------------------------
ensure_ssh_dir

# Local primary key
generate_key_if_missing "$LOCAL_KEY"
LOCAL_PUB="$LOCAL_KEY.pub"
if [[ ! -f "$LOCAL_PUB" ]]; then fail "Local public key missing at $LOCAL_PUB"; fi

# Optional RSA
if $GENERATE_RSA; then
  RSA_PRIV="${LOCAL_KEY%.pub}_rsa"
  RSA_PRIV="$HOME/.ssh/cbw_rsa"
  generate_rsa_if_missing "$RSA_PRIV"
  RSA_PUB="$RSA_PRIV.pub"
fi

for tgt in "${REMOTE_LIST[@]}"; do
  info "Processing remote: $tgt"

  # derive host alias
  host_alias="${SSH_ALIAS_OVERRIDE:-}" || true
  if [[ -z "$host_alias" ]]; then
    # derive alias from host part
    hostpart="${tgt%%@*}"; hostrest="${tgt##*@}"
    # hostrest may be host:port or just host
    host_noport="${hostrest%%:*}"
    host_alias="${host_noport}"
  fi

  # ensure remote .ssh exists and perms
  if $DRY_RUN; then
    info "(dry-run) Would ensure remote ~/.ssh exists and perms"
  else
    remote_exec "$tgt" "mkdir -p ~/.ssh && chmod 700 ~/.ssh || true" || warn "Could not ensure .ssh on $tgt"
  fi

  # append local pub to remote authorized_keys idempotently
  pub_content=$(<"$LOCAL_PUB")
  if $DRY_RUN; then
    info "(dry-run) Would ensure local pub is in remote authorized_keys"
  else
    # check remotely if present
    if remote_exec "$tgt" "grep -Fxq -- '$pub_content' ~/.ssh/authorized_keys 2>/dev/null || echo MISSING" | grep -q MISSING; then
      info "Appending our pub to remote authorized_keys on $tgt"
      # use printf to avoid variable interpolation
      remote_exec "$tgt" "bash -lc 'printf "%s\n" "$(echo "$pub_content" | sed "s/'/'\\''/g")" >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys'" || warn "Failed to append pub to $tgt"
    else
      info "Our key already present in remote authorized_keys"
    fi
  fi

  # fetch remote's public keys (any files in ~/.ssh/*.pub) and save locally
  tmp_remote_publist="/tmp/remote_pub_list_$$.txt"
  if $DRY_RUN; then
    info "(dry-run) Would collect remote public keys list"
  else
    remote_exec "$tgt" "ls -1 ~/.ssh/*.pub 2>/dev/null || true" > "$tmp_remote_publist" || true
    if [[ -s "$tmp_remote_publist" ]]; then
      while IFS= read -r remote_pub_path; do
        remote_pub_content=$(remote_exec "$tgt" "cat $remote_pub_path" 2>/dev/null || true)
        if [[ -n "$remote_pub_content" ]]; then
          local_name="$HOME/.ssh/remote-$(echo "$tgt" | sed 's/[^a-zA-Z0-9._-]/_/g').pub"
          # append remote pub content to a local per-host pubfile if missing
          if [[ -f "$local_name" ]]; then
            grep -Fxq -- "$remote_pub_content" "$local_name" || echo "$remote_pub_content" >> "$local_name" && info "Appended remote pub to $local_name"
          else
            echo "$remote_pub_content" > "$local_name" && chmod 644 "$local_name" && info "Saved remote pub to $local_name"
          fi
        fi
      done < "$tmp_remote_publist"
    fi
    rm -f "$tmp_remote_publist" || true
  fi

  # add remote host key entry to local known_hosts via ssh-keyscan
  info "Updating local known_hosts for $tgt"
  if $DRY_RUN; then
    info "(dry-run) Would ssh-keyscan $tgt and append to $KNOWN_HOSTS_FILE"
  else
    # perform scan
    ssh_keyscan_to_file "$tgt" "$KNOWN_HOSTS_FILE"
    info "Appended ssh-keyscan entries to $KNOWN_HOSTS_FILE"
  fi

  # Optionally push origin host key to remote known_hosts
  if $PUSH_REMOTE_KNOWN; then
    info "Pushing origin host key to remote known_hosts on $tgt"
    if $DRY_RUN; then
      info "(dry-run) Would push local host key to remote known_hosts"
    else
      # get our own host key (scan local hostname / localhost)
      # We'll try scanning the local address and add to remote's known_hosts
      local_host_entry=$(ssh-keyscan -T 5 $(hostname -f) 2>/dev/null || true)
      if [[ -z "$local_host_entry" ]]; then
        # fall back to localhost
        local_host_entry=$(ssh-keyscan -T 5 localhost 2>/dev/null || true)
      fi
      if [[ -n "$local_host_entry" ]]; then
        # escape single quotes for remote echo
        escaped=$(printf '%s' "$local_host_entry" | sed "s/'/'\\''/g")
        remote_exec "$tgt" "bash -lc 'mkdir -p ~/.ssh; chmod 700 ~/.ssh; printf "%s\n" '$escaped' >> ~/.ssh/known_hosts && chmod 644 ~/.ssh/known_hosts'" || warn "Could not push known_hosts to $tgt"
        info "Pushed origin host key to remote known_hosts"
      else
        warn "Could not determine local host key via ssh-keyscan"
      fi
    fi
  fi

  # Update local ~/.ssh/config with a Host stanza for convenience
  config_entry=""
  config_entry+="Host $host_alias\n"
  config_entry+="  HostName ${tgt##*@}\n"
  if [[ "$tgt" == *":"* ]]; then
    portpart="${tgt##*:}"
    config_entry+="  Port $portpart\n"
  fi
  config_entry+="  User ${tgt%%@*}\n"
  config_entry+="  IdentityFile $LOCAL_KEY\n"
  config_entry+="  IdentitiesOnly yes\n"

  # ensure idempotent ssh config append
  if grep -q "^Host[[:space:]]\+$host_alias\b" "$SSH_CONFIG_FILE" 2>/dev/null; then
    info "SSH config already has Host $host_alias — skipping (you can edit $SSH_CONFIG_FILE to change)"
  else
    if $DRY_RUN; then
      info "(dry-run) Would append Host $host_alias entry to $SSH_CONFIG_FILE"
    else
      printf "\n%s\n" "$config_entry" >> "$SSH_CONFIG_FILE" && chmod 600 "$SSH_CONFIG_FILE" && info "Appended Host $host_alias to $SSH_CONFIG_FILE"
    fi
  fi

  info "Finished processing $tgt"
  echo
done

info "All done. Re-run as needed — script is idempotent and safe to run repeatedly."

# Suggestions for next steps (printed to user)
if ! $DRY_RUN; then
  cat <<EOF

Next recommendations:
 1) After you confirm key login works, run the server-side hardening: set PasswordAuthentication no in /etc/ssh/sshd_config and restart sshd.
 2) Consider storing your private key(s) in Bitwarden CLI (bw) as an encrypted note or item.
 3) Use ssh certificates (SSH CA) to avoid having to distribute keys for many users/hosts.

EOF
fi
