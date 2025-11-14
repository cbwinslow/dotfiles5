# Bitwarden Integration with Chezmoi

This document describes how to use Bitwarden CLI to automatically populate secrets in your Chezmoi-managed dotfiles.

## Overview

The integration allows you to store API keys, passwords, and other secrets in Bitwarden and have them automatically retrieved when you run `chezmoi apply`. This ensures your secrets are:

- ✅ Stored securely in Bitwarden
- ✅ Automatically populated in your dotfiles
- ✅ Never committed to version control
- ✅ Available across all your machines

## Files Involved

- `run_before_bitwarden-secrets.sh` - Script that unlocks Bitwarden and prepares secrets
- `dot_bash_secrets` - Template for bash secrets (`.bashrc` integration)
- `private_dot_zsh_secrets` - Template for zsh secrets (`.zshrc` integration)
- `.chezmoi.toml` - Configuration file that controls execution order
- `test_bitwarden_integration.sh` - Test script to verify everything works

## Setup

### 1. Install Prerequisites

Make sure you have all required tools:

```bash
# Bitwarden CLI
# Linux: https://bitwarden.com/help/cli/#download-and-install
# macOS: brew install bitwarden-cli
# Windows: choco install bitwarden-cli

# jq (for JSON parsing)
# Ubuntu/Debian: sudo apt install jq
# macOS: brew install jq

# Chezmoi (if not already installed)
# https://chezmoi.io/
```

### 2. Configure Bitwarden CLI

```bash
# Login to Bitwarden
bw login

# Verify login
bw status
```

### 3. Add Secrets to Bitwarden

Create items in your Bitwarden vault with the following names (case-insensitive):

- `openrouter` - For OpenRouter API key
- `github` - For GitHub API token
- `openai` - For OpenAI API key
- `database` - For database connection string
- `aws` - For AWS credentials
- `twilio` - For Twilio credentials
- `sendgrid` - For SendGrid API key
- `slack` - For Slack webhook URL

Each item should have:
- **Name**: The service name (e.g., "openrouter")
- **Username**: Access key ID (for services that have separate key/secret)
- **Password**: The main secret (API key, password, token, etc.)
- **Custom Fields**: Additional fields if needed

### 4. Test the Integration

Run the test script to verify everything works:

```bash
# Unlock Bitwarden first
bw unlock

# Run the test
chezmoi execute-template < ~/.local/share/chezmoi/test_bitwarden_integration.sh
```

Or run it directly:

```bash
bash ~/.local/share/chezmoi/test_bitwarden_integration.sh
```

### 5. Apply Your Configuration

```bash
# Unlock Bitwarden
bw unlock

# Apply your dotfiles (secrets will be populated automatically)
chezmoi apply
```

### Quick manual pre-apply step

If you prefer an explicit, repeatable step that generates local secret files before `chezmoi apply`, use the helper script included in this repository.

```bash
bash ~/.local/share/chezmoi/run_before_bitwarden-secrets.sh
chezmoi apply
```

This script will:
- Ensure `bw` and `jq` are available
- Unlock the vault (interactive or via `BW_PASSWORD` env)
- Produce `~/.bash_secrets` and `~/.zsh_secrets` with restricted permissions (600)

If you want Chezmoi to run this automatically, you can wire the script into your local workflow (for example, by running it from a pre-apply hook or your shell initialization). Keep in mind that automatic unlocking without interactive prompts requires careful handling of `BW_PASSWORD` or existing `BW_SESSION` tokens.

## How It Works

### Execution Order

1. **Pre-apply hook**: `run_before_bitwarden-secrets.sh` runs first
   - Checks if Bitwarden CLI is available
   - Verifies authentication status
   - Unlocks vault if needed (with password prompt or environment variable)
   - Tests connectivity

2. **Template rendering**: Secret templates are processed
   - `dot_bash_secrets` generates `~/.bash_secrets`
   - `private_dot_zsh_secrets` generates `~/.zsh_secrets`
   - Templates use `bw get` commands to fetch secrets
   - Fallback to environment variables or placeholders if secrets not found

3. **File deployment**: Generated files are deployed to your home directory

### Template Functions

The templates use a `get_bw_secret()` function that:

1. Tries to fetch the secret from Bitwarden using `bw get`
2. Falls back to environment variables (e.g., `OPENROUTER_API_KEY`)
3. Uses placeholder values if neither is available

### Environment Variables

You can override any secret using environment variables:

```bash
export OPENROUTER_API_KEY="your-key-here"
export GITHUB_API_TOKEN="your-token-here"
chezmoi apply
```

## Security Considerations

### Password Protection

The integration supports multiple authentication methods:

1. **Interactive**: Prompts for password when needed
2. **Environment Variable**: Set `BW_PASSWORD` environment variable
3. **Session Token**: Uses existing unlocked session

### Best Practices

- ✅ Use strong, unique passwords for your Bitwarden vault
- ✅ Enable 2FA on your Bitwarden account
- ✅ Regularly rotate your API keys
- ✅ Never commit `.env` files or secrets to version control
- ✅ Use descriptive names for your Bitwarden items
- ✅ Test the integration regularly

## Troubleshooting

### Common Issues

**"Bitwarden CLI not found"**
- Install Bitwarden CLI from the official website
- Ensure it's in your PATH

**"Bitwarden CLI not configured"**
- Run `bw login` to authenticate
- Verify with `bw status`

**"Vault is locked"**
- Run `bw unlock` to unlock your vault
- Or set `BW_PASSWORD` environment variable

**"Secret not found"**
- Check the item name in Bitwarden matches expected names
- Verify the item has the correct field (username/password)
- Check case sensitivity (searches are case-insensitive)

**"jq not found"**
- Install jq for JSON parsing: `sudo apt install jq` (Ubuntu/Debian)

### Debug Commands

```bash
# Check Bitwarden status
bw status

# List all items in your vault
bw list items

# Get a specific item
bw get password "openrouter"

# Test template rendering
chezmoi execute-template < ~/.local/share/chezmoi/dot_bash_secrets

# Check generated files
cat ~/.bash_secrets
cat ~/.zsh_secrets
```

## Customization

### Adding New Secrets

To add support for a new service:

1. **Add to Bitwarden**: Create an item with the service name
2. **Update templates**: Add the export statement to both secret templates
3. **Update function**: Modify `get_bw_secret()` calls if needed
4. **Test**: Run the test script to verify

### Changing Item Names

If you want to use different names for your Bitwarden items:

1. Edit the `get_bw_secret()` calls in both templates
2. Update the test script accordingly
3. Update this documentation

### Multiple Environments

For different environments (dev/staging/prod):

1. Create separate Bitwarden items with environment suffixes
2. Modify the templates to check environment variables first
3. Use Chezmoi's environment-specific features

## Files Structure

```
.local/share/chezmoi/
├── run_before_bitwarden-secrets.sh    # Main integration script
├── dot_bash_secrets                   # Bash secrets template
├── private_dot_zsh_secrets            # Zsh secrets template
├── .chezmoi.toml                      # Configuration
├── test_bitwarden_integration.sh      # Test script
└── BITWARDEN_INTEGRATION_README.md    # This file
```

## Homelab Machine Integration

This setup includes SSH configuration for the following homelab machines:

| Machine Name | IP Address | SSH Host Alias |
|-------------|------------|----------------|
| cbwdellr720 | 172.28.82.205 | `ssh cbwdellr720` |
| cbwhpz | 172.28.27.157 | `ssh cbwhpz` |
| cbwamd | 172.28.176.115 | `ssh cbwamd` |
| cbwlapkali | 172.28.196.74 | `ssh cbwlapkali` |
| cbwmac | 172.28.169.48 | `ssh cbwmac` |

### SSH Access

All machines use the same SSH key (`id_ed25519_personal` or `id_rsa_personal`) and user (`foomanchu8008`). To connect:

```bash
ssh cbwdellr720  # Connects to 172.28.82.205
ssh cbwhpz       # Connects to 172.28.27.157
# etc.
```

### Data Loading Issue Workaround

**Issue**: Chezmoi v2.66.0 has a bug where `chezmoi data` and `--override-data-file` cause a panic with "assignment to entry in nil map". This prevents loading the `data.yaml` file.

**Workaround**: Homelab machines are hardcoded in the SSH config template (`dot_ssh/config.tmpl`) instead of being loaded from data. The `data.yaml` file still exists for future use when the bug is fixed.

**Impact**: SSH configuration works correctly, but other templates that depend on data loading may not work until the chezmoi bug is resolved.

### Adding Machine-Specific Keys

If you need different SSH keys for specific machines, you can:

1. Add new key entries to `data.yml`
2. Update the SSH config template in `dot_ssh/config.tmpl`
3. Run `chezmoi apply` to regenerate the config

## Support

If you encounter issues:

1. Run the test script to diagnose problems
2. Check the troubleshooting section above
3. Verify your Bitwarden CLI installation
4. Ensure your vault items match the expected names
5. Check Chezmoi and Bitwarden CLI documentation

---

**Last updated**: {{ now.Format "2006-01-02 15:04:05" }}
**Managed by**: Chezmoi
**Do not edit manually** - This file is generated from the Chezmoi source
