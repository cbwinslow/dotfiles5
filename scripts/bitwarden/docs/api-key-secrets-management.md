# API Key Secrets Management

This document explains how to manage API keys and tokens using chezmoi templates populated from Bitwarden.

## Overview

API keys and tokens are automatically discovered from Bitwarden and made available as environment variables. The system searches for:

1. **Items with `*_API_KEY` in the title** - API key value in the password field
2. **Custom fields containing "api key"** - API keys stored in custom fields

## How It Works

### 1. Bitwarden Item Structure

**For items with *_API_KEY in title:**
```
Item Name: OpenAI_API_KEY
Password Field: sk-your-actual-openai-key-here
```

**For items with API keys in custom fields:**
```
Item Name: API Keys Collection
Custom Fields:
  - Name: OpenAI API Key
    Value: sk-your-actual-openai-key-here
  - Name: GitHub Token
    Value: ghp_your-actual-github-token-here
```

### 2. Environment Variable Naming

API keys are automatically converted to environment variables:

- `OpenAI_API_KEY` → `OPENAI_API_KEY`
- `GitHub Personal Access Token` → `GITHUB_PERSONAL_ACCESS_TOKEN`
- Custom fields: `API Keys Collection` + field name → `API_KEYS_COLLECTION_OPENAI_API_KEY`

### 3. Template Processing

The `secrets/api-keys.tmpl` template generates shell environment variables:

```bash
export OPENAI_API_KEY="sk-your-key-here"
export GITHUB_API_KEY="ghp_your-token-here"
```

## Setup Instructions

### 1. Create API Key Secrets

Run the discovery script:

```bash
cd ~/.local/share/chezmoi
./create-api-key-secrets.sh
```

This will:
- Unlock your Bitwarden vault
- Search for API keys in item titles and custom fields
- Update `secrets/ssh-secrets.yaml` with found keys
- Create/update the API keys template

### 2. Apply Configuration

Apply the changes:

```bash
chezmoi apply
```

This generates `~/.bash_secrets` and `~/.zsh_secrets` with your API keys.

### 3. Load Secrets

The secrets are automatically loaded by your shell configuration. To test:

```bash
# Reload your shell or source the secrets file
source ~/.bash_secrets

# Check if API keys are available
echo $OPENAI_API_KEY | head -c 10  # Should show start of key
```

## Supported API Key Patterns

### Title-based Detection (`*_API_KEY`)

- `OPENAI_API_KEY` → `OPENAI_API_KEY`
- `GITHUB_API_KEY` → `GITHUB_API_KEY`
- `ANTHROPIC_API_KEY` → `ANTHROPIC_API_KEY`
- `STRIPE_API_KEY` → `STRIPE_API_KEY`

### Custom Field Detection

Any custom field with "api key" (case insensitive) in the name:

- `OpenAI API Key` → `OPENAI_API_KEY`
- `GitHub Personal Access Token` → `GITHUB_PERSONAL_ACCESS_TOKEN`
- `API Key for Service` → `API_KEY_FOR_SERVICE`

## Security Features

- ✅ **No plaintext keys in repository** - Only encrypted references
- ✅ **Bitwarden encryption** - Keys encrypted in your vault
- ✅ **Shell file permissions** - Secrets files are `chmod 600`
- ✅ **Automatic cleanup** - Session files are removed after use

## File Structure

```
~/.local/share/chezmoi/
├── secrets/
│   ├── api-keys.tmpl          # API keys template
│   └── ssh-secrets.yaml       # Secrets data file
├── create-api-key-secrets.sh  # Discovery script
└── run_before_bitwarden-secrets.sh  # Updated to include API keys
```

## Generated Files

After `chezmoi apply`:

```
~/
├── .bash_secrets              # Bash environment variables
└── .zsh_secrets               # Zsh environment variables
```

## Troubleshooting

### Keys Not Found

If API keys aren't being detected:

1. Check Bitwarden item names end with `_API_KEY`
2. Verify API keys are in password field or custom fields named "*api key*"
3. Run `./create-api-key-secrets.sh` again
4. Check `secrets/ssh-secrets.yaml` for detected keys

### Environment Variables Not Available

If API keys aren't in your shell:

```bash
# Check if secrets file exists and has content
ls -la ~/.bash_secrets
cat ~/.bash_secrets | head -5

# Manually source the file
source ~/.bash_secrets

# Check if variables are set
echo "${OPENAI_API_KEY:+SET}"  # Should show "SET" if available
```

### Permission Issues

If secrets files have wrong permissions:

```bash
chmod 600 ~/.bash_secrets ~/.zsh_secrets
```

## Advanced Usage

### Custom Environment Variable Names

Modify the script to customize variable naming:

```bash
# In create-api-key-secrets.sh, modify this line:
env_var=$(echo "$name" | sed 's/_API_KEY$//' | tr '[:lower:]' '[:upper:]' | sed 's/[^A-Z0-9_]/_/g')
```

### Additional API Key Sources

Extend the script to search additional patterns:

```bash
# Add to the api_patterns array
api_patterns+=("custom.*token:custom_token")
```

### Encrypted Secrets

For additional security, encrypt the secrets data:

```bash
chezmoi add --encrypt secrets/ssh-secrets.yaml
```

## Examples

### Bitwarden Item Examples

**OpenAI API Key:**
```
Name: OPENAI_API_KEY
Password: sk-proj-...your-actual-key...
```

**GitHub Token in Custom Field:**
```
Name: Development Tokens
Fields:
  - Name: GitHub API Key
    Value: ghp_...your-actual-token...
```

### Generated Environment Variables

```bash
export OPENAI_API_KEY="sk-proj-...your-key..."
export GITHUB_API_KEY="ghp_...your-token..."
```

### Usage in Scripts

```bash
#!/bin/bash
# API keys are automatically available
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "Hello"}]}' \
     https://api.openai.com/v1/chat/completions
```

This system provides secure, automated management of API keys across all your machines using chezmoi and Bitwarden.