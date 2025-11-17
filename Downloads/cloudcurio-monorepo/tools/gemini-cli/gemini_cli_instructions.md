# Gemini CLI Blueprint Instructions

## Overview
This document provides instructions and details for using the Gemini CLI Blueprint v2. It outlines installation steps, usage commands, configuration options, and project structure workflow.

## Installation
1. Unzip the provided `gemini_cli_blueprint_v2.zip`.
2. Navigate to the directory:
   ```bash
   cd gemini_cli_blueprint_v2
   ```
3. Install the package:
   ```bash
   pip install .
   ```

## Commands
### 1. Initialize a Project
```bash
gemini init-project --target my_project
```

### 2. View Status
```bash
gemini status
```

### 3. Install Extensions
```bash
gemini install-extensions --marketplace-url URL --api-token TOKEN
```

## Directory Structure
- `gemini_cli/` — main package
- `config_loader.py` — configuration manager
- `cli.py` — command handler
- `core/guard.py` — safe delete and filesystem protection
- `core/secrets.py` — .env discovery and secure permissions

## Configuration System
Gemini CLI loads configuration from:
1. Explicit path via `--config`
2. `./config/gemini_config.yaml`
3. `~/.gemini/config.yaml`

Environment variables override YAML:
- `GEMINI_JOURNAL_DIR`
- `GEMINI_MEMORY_DB`
- `GEMINI_SAFE_MODE`
- `GEMINI_EXT_STATE_FILE`

## Safety Rules
- No destructive action without user approval.
- Automatic backups before deletion.
- Secrets must be stored securely.
- Journaling must be persistent and consistent.

## Next Steps
- Create agent toolspecs (OpenAI-compatible)
- Implement `gemini doctor` diagnostic command
- Add real memory backend (SQLite + embeddings)
