# `lang_installer_framework.sh` – Usage Guide

This document explains how to use `lang_installer_framework.sh` to install and manage programming language runtimes in a consistent, idempotent, and logged way.

---
## 1. Overview

`lang_installer_framework.sh` is a Bash script that:

- Detects the **currently installed version** of a language.
- Compares it to a **required minimum version**.
- Installs or upgrades the language **only if needed** (idempotent).
- Supports multiple install methods:
  - System package manager (apt, dnf, yum, pacman, brew)
  - Custom shell command
  - Arbitrary local installer script/binary
  - Reusable "installer profile" scripts
- Logs all actions and errors to `/tmp/CBW-lang_installer_framework.log`.
- Supports dry-run and verbose modes.

You can use it directly from the CLI or call it from other scripts and automation.

---
## 2. Supported Languages

The script ships with presets for the following language identifiers (`--lang`):

- `python`, `python3`
- `node`, `nodejs`
- `go`, `golang`
- `rust`
- `java`, `jdk`, `openjdk`
- `ruby`
- `php`
- `bun`
- `deno`
- `custom` (for anything not covered above)

Each preset defines:

- A default **detection command** (`DETECT_CMD`), e.g. `python3`, `node`, `go`, `rustc`, `java`.
- Default **detection arguments** (`DETECT_ARGS`), usually `--version` or `-version`.
- A default **package name** (`PKG_NAME`) for the system package manager.
- A reasonable **default minimum version** (`MIN_VERSION`) if you do not supply one.

You can override any of these via CLI options.

---
## 3. Requirements

- Bash (the script uses Bash-specific features).
- A supported package manager if you use `auto` / `system` install methods:
  - `apt-get` (Debian/Ubuntu)
  - `dnf` or `yum` (Fedora/RHEL/CentOS)
  - `pacman` (Arch/Manjaro)
  - `brew` (macOS/Linuxbrew)
- Sufficient privileges to install software (e.g., `sudo` access).

The script is designed to be safe to re-run multiple times.

---
## 4. Basic Installation & Setup

1. Save the script as `lang_installer_framework.sh`.
2. Make it executable:

```bash
chmod +x lang_installer_framework.sh
```

3. (Optional) Put it somewhere in your `PATH`, e.g.:

```bash
mkdir -p "$HOME/bin"
cp lang_installer_framework.sh "$HOME/bin/"
export PATH="$HOME/bin:$PATH"
```

4. Run with `--help` to see usage:

```bash
lang_installer_framework.sh --help
```

---
## 5. Command-line Options

### Core options

- `--lang <name>`
  - Language identifier (e.g., `python`, `node`, `go`, `rust`, `java`, `ruby`, `php`, `bun`, `deno`, `custom`).
  - **Required.**

- `--min-version <ver>`
  - Minimum required version (e.g., `3.11.0`, `18.0.0`, `1.22.0`).
  - If omitted, the preset default is used (where defined).

- `--install-method <method>`
  - `auto` (default): use system packages unless `--installer-path` or `--installer-profile` is provided.
  - `system`: force using the system package manager.
  - `custom`: run a custom shell command.
  - `path`: run a specific local installer script/binary.
  - `profile`: run a named installer profile script.

- `--dry-run`
  - Log what would be done **without** making changes.

- `--verbose`
  - Enable detailed debug logging.

- `--force`
  - Reinstall or upgrade even if the currently installed version already meets `--min-version`.

### Detection overrides

- `--detect-cmd <cmd>`
  - Command used for version detection, e.g. `python3`, `mylang`.

- `--detect-args <args>`
  - Arguments passed to the detection command (default: `--version`).

### Package manager overrides

- `--pkg-name <name>`
  - Package name for the system package manager (e.g., `python3.11`, `nodejs-lts`).

### Custom installer command

- `--custom-install-cmd <cmd>`
  - Shell command used for `INSTALL_METHOD=custom`.
  - Example: `"curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt-get install -y nodejs"`.

### External installers

- `--installer-path <path>`
  - Path to a local installer script/binary.
  - Used when `INSTALL_METHOD=path` or when `INSTALL_METHOD=auto` and this value is present.

- `--installer-args <args>`
  - Arguments passed to the installer at `--installer-path` or to a profile script.

- `--installer-profile <name>`
  - Name of an installer profile script (e.g., `go_opt`).
  - The script will look for `${INSTALLER_DIR}/${name}.sh`.

- `--installer-dir <path>`
  - Directory containing installer profile scripts.
  - Default: `$HOME/.config/cbw/lang-installers` (or `CBW_LANG_INSTALLER_DIR` env var).

---
## 6. How Idempotency Works

1. A language preset sets defaults for detection and versions.
2. The script runs the detection command (`DETECT_CMD DETECT_ARGS`) and extracts the first `X.Y` or `X.Y.Z` token as the **current version**.
3. It compares the current version against `MIN_VERSION` using a semantic-style comparison.
4. If `current >= MIN_VERSION` and `--force` is **not** set:
   - The script logs that no action is needed and exits successfully.
5. If the language is not installed or the version is too low:
   - The selected install method runs.
6. After installation, the script detects the version again and verifies that it now meets `MIN_VERSION`.

The end result: running the script multiple times is safe and leads to a consistent language setup.

---
## 7. Using System Package Manager (auto / system)

### Example: Ensure Python ≥ 3.11 via system packages

```bash
./lang_installer_framework.sh \
  --lang python \
  --min-version 3.11.0
```

Behavior:

- Detects current `python3` version.
- Detects system package manager (`apt`, `dnf`, `yum`, `pacman`, `brew`).
- Installs or upgrades the default package (`python3`) if needed.
- Re-checks the version and ensures it meets the requirement.

### Example: Override package name

```bash
./lang_installer_framework.sh \
  --lang python \
  --min-version 3.11.0 \
  --pkg-name python3.11
```

Useful if your distro has specific package names (e.g., `python3.11` separate from `python3`).

---
## 8. Using a Custom Install Command

Use `INSTALL_METHOD=custom` when you already have a one-liner or script that installs a language (e.g., vendor installers, curl | bash, etc.).

### Example: Node.js via NodeSource script

```bash
./lang_installer_framework.sh \
  --lang node \
  --min-version 18.0.0 \
  --install-method custom \
  --custom-install-cmd "curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt-get install -y nodejs"
```

The framework will:

- Detect the current Node.js version (via `node --version`).
- If too low / missing, run the custom install command through its logging system.
- Verify the version afterwards.

---
## 9. Using a Local Installer Path

Use `INSTALL_METHOD=path` (or leave `install-method=auto` and provide `--installer-path`) to run **any** local script or binary.

### Example: Local Rust installer script

```bash
./lang_installer_framework.sh \
  --lang rust \
  --min-version 1.80.0 \
  --install-method path \
  --installer-path "$HOME/installers/install_rust.sh" \
  --installer-args "--channel stable"
```

Behavior:

- If `install_rust.sh` is executable, it’s run directly.
- If it’s just a plain script file, it is invoked via `bash "install_rust.sh" --channel stable`.
- If the file does not exist, the script logs an error and exits.

This allows you to maintain your own install scripts and still benefit from the detection and version logic.

---
## 10. Using Installer Profiles

Profiles are reusable scripts stored under a common directory (default: `$HOME/.config/cbw/lang-installers`).

### Directory layout example

```text
~/.config/cbw/lang-installers/
  go_opt.sh
  python-dev.sh
  java-lts.sh
```

### Example: Using a `go_opt` profile

```bash
./lang_installer_framework.sh \
  --lang go \
  --min-version 1.22.0 \
  --install-method profile \
  --installer-profile go_opt
```

What happens:

- The script looks for `$HOME/.config/cbw/lang-installers/go_opt.sh`.
- If found and executable, it runs that script.
- If not executable, it falls back to `bash go_opt.sh`.
- You can pass arguments using `--installer-args`:

```bash
./lang_installer_framework.sh \
  --lang go \
  --min-version 1.22.0 \
  --install-method profile \
  --installer-profile go_opt \
  --installer-args "--prefix /opt/go --channel stable"
```

### Changing the installer directory

```bash
./lang_installer_framework.sh \
  --lang python \
  --min-version 3.11.0 \
  --install-method profile \
  --installer-profile python-dev \
  --installer-dir "$HOME/dev/installers/lang"
```

You can also set `CBW_LANG_INSTALLER_DIR` in your environment and omit `--installer-dir`.

---
## 11. Dry-run, Verbose Mode, and Logging

### Dry-run (`--dry-run`)

- Skips actual system changes.
- Logs all commands that **would** have been executed.

Example:

```bash
./lang_installer_framework.sh \
  --lang node \
  --min-version 20.0.0 \
  --dry-run \
  --verbose
```

This is ideal for auditing what the script will do on a fresh system.

### Verbose (`--verbose`)

- Enables additional debug logging: raw version command output, internal decisions, etc.

### Log file

- All logs are written to:

```text
/tmp/CBW-lang_installer_framework.log
```

- On exit, the script prints a summary and reminds you of the log location.

---
## 12. Examples by Language

### Python

```bash
# Use system package manager
./lang_installer_framework.sh --lang python --min-version 3.11.0

# Use custom installer profile
./lang_installer_framework.sh \
  --lang python \
  --min-version 3.11.0 \
  --install-method profile \
  --installer-profile python-dev
```

### Node.js

```bash
# System packages (e.g., Debian/Ubuntu repo)
./lang_installer_framework.sh --lang node --min-version 18.0.0

# NodeSource installer via custom command
./lang_installer_framework.sh \
  --lang node \
  --min-version 18.0.0 \
  --install-method custom \
  --custom-install-cmd "curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt-get install -y nodejs"
```

### Go

```bash
# System package manager
./lang_installer_framework.sh --lang go --min-version 1.22.0

# /opt-based installer profile (e.g., manual tarball script)
./lang_installer_framework.sh \
  --lang go \
  --min-version 1.22.0 \
  --install-method profile \
  --installer-profile go_opt
```

### Rust

```bash
./lang_installer_framework.sh \
  --lang rust \
  --min-version 1.80.0 \
  --install-method path \
  --installer-path "$HOME/installers/install_rust.sh" \
  --installer-args "--channel stable"
```

---
## 13. Integrating into Other Scripts

You can call `lang_installer_framework.sh` from higher-level setup scripts, for example in a dev-environment bootstrap:

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$HOME/dev/bootstrap"
LANG_INSTALLER="$ROOT_DIR/lang_installer_framework.sh"

"$LANG_INSTALLER" --lang python --min-version 3.11.0
"$LANG_INSTALLER" --lang node   --min-version 20.0.0
"$LANG_INSTALLER" --lang go     --min-version 1.22.0
"$LANG_INSTALLER" --lang rust   --min-version 1.80.0
```

This gives you a declarative list of language requirements that can be enforced on any machine.

---
## 14. Troubleshooting

- **No language found on PATH**
  - The script will log that the detection command is missing and treat the language as "not installed".
  - Ensure the correct `--detect-cmd` is configured, especially in `custom` mode.

- **Version detection fails**
  - Check the log: raw output from `DETECT_CMD DETECT_ARGS` is recorded.
  - Adjust `--detect-args` or use a custom detection command.

- **Package manager not detected**
  - Ensure your OS uses one of: `apt-get`, `dnf`, `yum`, `pacman`, `brew`.
  - For other managers (e.g., `zypper`, `apk`), you can:
    - Extend the script, or
    - Use `INSTALL_METHOD=custom`, `path`, or `profile`.

- **Post-install version too low**
  - This usually means your package repository or installer provided an older version than requested.
  - Either relax `--min-version`, use an external installer, or use a profile that installs from upstream.

- **Permissions issues**
  - Most installs require `sudo` privileges. Run the script in a context where you can use `sudo`.

---
## 15. Exit Codes

- `0` – Success (requirements satisfied; may or may not have required an install).
- Non-zero – A failure occurred (e.g., package manager error, missing installer, validation failure).

On failure, consult `/tmp/CBW-lang_installer_framework.log` for full details.

---
## 16. Recommended Next Steps

- Create installer profiles under `$HOME/.config/cbw/lang-installers` for your "golden" setups:
  - `go_opt.sh` for /opt-based Go installs.
  - `python-dev.sh` for dev-focused Python stacks.
  - `node-lts.sh` for your preferred Node LTS.
- Wire this script into your master dev/homelab setup scripts.
- Add a small test suite (e.g., with BATS) to validate version parsing and dry-run behavior whenever you modify the script.

