# AI Automation Stack Deployment - Conversation Notes

## Current Status (Nov 12, 2025)

### SSH Access Situation
- **Working Key**: `~/.ssh/cbwdellr720/id_cbwdellr720_to_network` (successfully connects)
- **Failed Keys**: `ssh_key_alt` from Bitwarden, other keys in Downloads
- **Connection Method**: NetBird VPN (100.90.23.60)
- **Issue**: Multiple SSH keys available but only one specific key works

### Stack Deployment
- **Local**: Partially deployed (Dify working at localhost:8180, n8n has encryption issues)
- **Remote (cbwdellr720)**: Files copied to `/home/cbwinslow/ai-automation`, Docker images pulling slowly
- **Domains**: Configured for cloudcurio.cc (n8n.cloudcurio.cc, dify.cloudcurio.cc)

### Key Files Locations
- **Local Stack**: `~/stacks/ai-automation/`
- **Remote Stack**: `/home/cbwinslow/ai-automation/`
- **SSH Keys**: `~/.ssh/cbwdellr720/id_cbwdellr720_to_network` (working)
- **Tools**: Various scripts in `~/Downloads/`

### SSH Access - FIXED ✅
- **Working Keys**: Added `id_ed25519` and `id_rsa` to authorized_keys
- **Easy Access**: `ssh cbwdellr720-prod` (ed25519) or `ssh cbwdellr720-rsa` (RSA)
- **Default Access**: `ssh cbwinslow@100.90.23.60` now works
- **Config Added**: SSH config entries in `~/.ssh/config`

### Current Deployment Status
- **Remote**: Docker images still pulling (very slow connection)
- **Command**: `docker-compose up -d` running in `/home/cbwinslow/ai-automation`
- **Issue**: Large images (n8n, dify) taking too long to download

### PostgreSQL Services Found on cbwdellr720
- **SonarQube DB**: postgres:13, user: sonar, db: sonar, network: infrastructure
- **Coolify DB**: postgres:15, user: coolify, db: coolify, network: coolify
- **Traefik**: v3.0 running, ports 8880/8843, Let's Encrypt ready
- **Let's Encrypt**: `/home/cbwinslow/monitoring_stack/letsencrypt`

### Infrastructure Available
- **Reverse Proxy**: Traefik v3.0 with SSL termination
- **Networks**: infrastructure, coolify (Docker bridge networks)
- **Domain**: cloudcurio.cc configured in Ansible configs

### Next Steps Needed
1. **Wait for Deployment**: Let Docker images finish pulling (or find alternative)
2. **Configure DNS**: Set up cloudcurio.cc domains to point to 100.90.23.60
3. **Set Up TLS**: Configure proper SSL certificates via Let's Encrypt
4. **Verify Services**: Test n8n.cloudcurio.cc and dify.cloudcurio.cc
5. **Alternative**: Consider using smaller images or pre-pulled images

### SSH Peculiarities Discovered
- Only specific key `id_cbwdellr720_to_network` works
- Standard key locations (`~/.ssh/id_*`) don't work
- Bitwarden-retrieved keys failed
- NetBird connection is stable

### Environment Variables
```
N8N_ENCRYPTION_KEY=9741904c0f2a3a01d8bf6112f6426f999f00ef805bfa3dc56135957b77530322
N8N_BASE_URL=https://n8n.cloudcurio.cc
DIFY_CONSOLE_URL=https://dify.cloudcurio.cc
N8N_HTTP_PORT=5678
DIFY_HTTP_PORT=8180
```

### Memory System
- Location: `~/Downloads/memory_manager.sh`
- Project: `AI-Automation-Stack`
- Status: Active development

---
*Generated: Wed Nov 12 2025*
*Purpose: Resume work in new opencode instance with full context*