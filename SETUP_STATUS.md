# Development Environment Setup Guide

## ✅ Current Status

### Shell Environment
- **Zsh Configuration**: ✅ Working (123 aliases, 1,640 functions)
- **OpenCode Integration**: ✅ Working (version: local)
- **Bitwarden Functions**: ✅ Working (env_from_bw, bw_search, etc.)
- **Development Aliases**: ✅ Working (git, docker, k8s, etc.)

### MCP Services
- **Context7**: ✅ Running
- **Octocode**: ✅ Running  
- **ShadCN**: ✅ Running
- **Chrome DevTools**: ✅ Running

## ⚠️ Issues to Fix

### 1. Default Shell
- **Current**: `/bin/bash`
- **Needed**: `/bin/zsh`
- **Fix**: Run `sudo chsh -s /bin/zsh cbwinslow` (requires sudo)

### 2. API Keys
- **Status**: Not configured
- **Needed**: ANTHROPIC_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY
- **Fix**: Add to `~/.env` or run `dev-env` script

### 3. MCP Integration
- **Status**: Services running but not connected to OpenCode
- **Issue**: OpenCode config validation errors with MCP servers
- **Fix**: Use external MCP gateway approach

## 🔧 Quick Fixes

### Set API Keys
```bash
# Create .env file
cat > ~/.env << EOF
ANTHROPIC_API_KEY="your_key_here"
OPENAI_API_KEY="your_key_here" 
GOOGLE_API_KEY="your_key_here"
EOF

# Or use the dev-env script
echo "source ~/.local/bin/dev-env" >> ~/.zshrc
```

### Change Default Shell
```bash
# Requires sudo password
sudo chsh -s /bin/zsh cbwinslow
```

### Test Everything
```bash
# Test shell
zsh -c "source ~/.zshrc && alias | wc -l"

# Test OpenCode
zsh -c "source ~/.zshrc && opencode --version"

# Test MCP services
ps aux | grep -E "(context7|octocode|shadcn|chrome-devtools)" | grep -v grep
```

## 📋 Next Steps

1. **Configure API keys** for OpenCode to work with AI models
2. **Change default shell** to zsh for persistent environment
3. **Set up MCP gateway** for proper integration
4. **Generate auth tokens** for remote MCP access
5. **Test complete workflow** end-to-end

## 🚀 Working Components

- ✅ Zsh with comprehensive dotfiles
- ✅ OpenCode CLI and wrapper script
- ✅ Bitwarden environment management
- ✅ Development tool aliases (git, docker, k8s)
- ✅ MCP services running independently
- ✅ PATH configuration
- ✅ Function loading (1,640 functions available)