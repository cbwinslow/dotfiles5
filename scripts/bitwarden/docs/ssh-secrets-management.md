# SSH Keys and Secrets Management

This document explains how to manage SSH keys and API secrets using chezmoi templates populated from Bitwarden.

## Overview

Your SSH keys and API tokens are now managed through chezmoi templates that are automatically populated from your Bitwarden vault. This ensures:

- ✅ Secure storage of private keys in Bitwarden
- ✅ Automatic synchronization across machines via chezmoi
- ✅ No plaintext secrets in your dotfiles repository
- ✅ Easy key rotation and management

## SSH Key Management

### Supported Key Types

- **Ed25519 keys**: Modern, secure, recommended for new keys
- **RSA keys**: Legacy support for existing keys
- **ECDSA keys**: Supported but less common

### Key Naming Convention

Keys are automatically detected and assigned based on naming patterns:

- `*_github*` → GitHub SSH keys
- `*_gitlab*` → GitLab SSH keys
- `*_personal*` → Personal server keys
- `*_work*` → Work server keys

### SSH Configuration

Your `~/.ssh/config` includes pre-configured hosts:

```bash
# GitHub
Host github.com
    IdentityFile ~/.ssh/id_ed25519_github
    IdentityFile ~/.ssh/id_rsa_github

# GitLab
Host gitlab.com
    IdentityFile ~/.ssh/id_ed25519_gitlab
    IdentityFile ~/.ssh/id_rsa_gitlab

# Personal/Work servers
Host personal
Host work
```

## Setting Up Secrets

### 1. Populate Secrets from Bitwarden

Run the population script:

```bash
cd ~/.local/share/chezmoi
./populate-secrets.sh
```

This will:
- Unlock your Bitwarden vault
- Search for SSH keys and API tokens
- Update `secrets/ssh-secrets.yaml` with the found secrets
- Generate SSH private key files

### 2. Apply Configuration

Apply the changes to your system:

```bash
chezmoi apply
```

This will:
- Generate SSH private key files from templates
- Update `~/.ssh/config`
- Update `~/.ssh/known_hosts`
- Update `~/.ssh/authorized_keys`

### 3. Set Key Permissions

Ensure SSH keys have correct permissions:

```bash
chmod 600 ~/.ssh/id_*
chmod 644 ~/.ssh/known_hosts ~/.ssh/config
```

## Bitwarden Item Structure

### SSH Keys

Store SSH private keys in Bitwarden items with these patterns:

**Item Name**: `GitHub Ed25519 Key`, `Personal RSA Key`, etc.
**Password Field**: The full private key content
**Custom Fields**: Optional additional metadata

### API Keys and Tokens

**Item Name**: `GitHub Token`, `OpenAI API Key`, etc.
**Password Field**: The API key/token value
**Custom Fields**: Optional metadata

### Supported Services

The system automatically detects and configures:

- **GitHub**: Personal access tokens
- **GitLab**: Personal access tokens
- **OpenAI**: API keys
- **Anthropic**: API keys
- **OpenRouter**: API keys

## File Structure

```
~/.local/share/chezmoi/
├── secrets/
│   └── ssh-secrets.yaml          # Secrets data file
├── dot_ssh/
│   ├── config.tmpl              # SSH config template
│   ├── known_hosts.tmpl         # Known hosts template
│   ├── authorized_keys.tmpl     # Authorized keys template
│   └── private_keys/            # SSH private key templates
│       ├── id_ed25519_github.tmpl
│       ├── id_ed25519_gitlab.tmpl
│       └── id_rsa_personal.tmpl
├── populate-secrets.sh          # Population script
└── discover-secrets.sh          # Discovery script
```

## Generated Files

After running `chezmoi apply`, these files are created:

```
~/.ssh/
├── config                    # SSH client configuration
├── known_hosts              # Known host keys
├── authorized_keys          # Authorized public keys
├── id_ed25519_github        # GitHub Ed25519 private key
├── id_ed25519_gitlab        # GitLab Ed25519 private key
├── id_rsa_personal          # Personal RSA private key
└── id_ed25519_github.pub    # Corresponding public keys (if available)
```

## Security Notes

- **Private keys never committed**: Only templates and data references are stored
- **Bitwarden encryption**: Keys are encrypted in your Bitwarden vault
- **Local encryption**: chezmoi can encrypt the secrets data file if configured
- **Access control**: Only you can decrypt and access the keys

## Troubleshooting

### Keys Not Found

If SSH keys aren't being populated:

1. Check Bitwarden item names match expected patterns
2. Verify private keys are in the password field
3. Run `./populate-secrets.sh` again
4. Check `secrets/ssh-secrets.yaml` for populated values

### Permission Denied

If SSH connections fail:

```bash
# Fix permissions
chmod 600 ~/.ssh/id_*
chmod 644 ~/.ssh/config ~/.ssh/known_hosts

# Test connection
ssh -T git@github.com
```

### Template Errors

If chezmoi apply fails:

```bash
# Check template syntax
chezmoi verify

# Debug template rendering
chezmoi cat ~/.ssh/config
```

## Advanced Usage

### Custom Key Types

Add new key templates in `dot_ssh/private_keys/`:

```bash
# Create template
cat > dot_ssh/private_keys/id_ed25519_custom.tmpl << 'EOF'
{{ .ssh_key_ed25519_custom | default "# Replace with your custom Ed25519 key" }}
EOF

# Add to secrets file
echo "ssh_key_ed25519_custom: \"\"" >> secrets/ssh-secrets.yaml
```

### Additional Services

Extend `populate-secrets.sh` to support new services:

```bash
# Add new API key pattern
api_patterns+=("custom.*api:key:custom_api_key")
```

### Encrypted Secrets

For additional security, encrypt the secrets file:

```bash
# Configure chezmoi encryption
chezmoi add --encrypt secrets/ssh-secrets.yaml
```

## Maintenance

### Key Rotation

To rotate SSH keys:

1. Generate new key pair
2. Update Bitwarden item with new private key
3. Run `./populate-secrets.sh`
4. Run `chezmoi apply`
5. Update public keys on remote services

### Adding New Keys

1. Store private key in Bitwarden
2. Run `./populate-secrets.sh`
3. Run `chezmoi apply`
4. Test SSH connection

This system provides a secure, automated way to manage SSH keys and API secrets across all your machines using chezmoi and Bitwarden.