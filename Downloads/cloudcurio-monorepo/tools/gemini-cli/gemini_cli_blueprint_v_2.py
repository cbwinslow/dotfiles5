# Gemini CLI Blueprint v2

This canvas holds the upgraded Gemini CLI core files (package + CLI + guards + config loader).

## Package Structure

- `gemini_cli/__init__.py`
- `gemini_cli/config_loader.py`
- `gemini_cli/cli.py`
- `gemini_cli/core/guard.py`
- `gemini_cli/core/secrets.py`

---

### `gemini_cli/__init__.py`

```python
"""Gemini CLI core package.

Provides constitution-driven tooling, CLI commands, and helpers for the
Gemini agent environment.
"""

__all__ = ["__version__"]
__version__ = "0.1.0"
```

---

### `gemini_cli/config_loader.py`

```python
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


@dataclass
class JournalingConfig:
    base_dir: Path
    max_prompts_without_flush: int
    max_minutes_without_flush: int


@dataclass
class MemoryConfig:
    backend: str
    db_path: Path
    embedding_model: str
    max_entries_per_project: int


@dataclass
class SecretsConfig:
    provider: str
    env_paths: list[Path]


@dataclass
class ExtensionsConfig:
    marketplace_url_env: str
    marketplace_token_env: str
    state_file: Path


@dataclass
class CLIConfig:
    default_project_root: Path
    safe_mode: bool


@dataclass
class GeminiConfig:
    journaling: JournalingConfig
    memory: MemoryConfig
    secrets: SecretsConfig
    extensions: ExtensionsConfig
    cli: CLIConfig


def _expand_path(value: str) -> Path:
    return Path(os.path.expanduser(value)).resolve()


def load_config(config_path: Optional[str] = None) -> GeminiConfig:
    """Load Gemini configuration from YAML and merge env overrides.

    Priority:
    1. Explicit config_path if provided.
    2. ./config/gemini_config.yaml relative to current working directory.
    3. ~/.gemini/config.yaml

    Environment overrides:
    - GEMINI_JOURNAL_DIR
    - GEMINI_MEMORY_DB
    - GEMINI_EXT_STATE_FILE
    - GEMINI_SAFE_MODE ("0"/"1" or "true"/"false")
    """
    # Determine config path
    if config_path is not None:
        cfg_path = Path(config_path).expanduser()
    else:
        local = Path.cwd() / "config" / "gemini_config.yaml"
        home = Path.home() / ".gemini" / "config.yaml"
        cfg_path = local if local.exists() else home

    if not cfg_path.exists():
        raise FileNotFoundError(f"Gemini config not found at {cfg_path}")

    with cfg_path.open("r", encoding="utf-8") as f:
        raw: Dict[str, Any] = yaml.safe_load(f) or {}

    # Journaling
    journaling_raw = raw.get("journaling", {})
    base_dir = os.getenv("GEMINI_JOURNAL_DIR", journaling_raw.get("base_dir", "~/.gemini/journals"))
    j_cfg = JournalingConfig(
        base_dir=_expand_path(base_dir),
        max_prompts_without_flush=int(
            journaling_raw.get("update_frequency", {}).get("max_prompts_without_flush", 3)
        ),
        max_minutes_without_flush=int(
            journaling_raw.get("update_frequency", {}).get("max_minutes_without_flush", 60)
        ),
    )

    # Memory
    memory_raw = raw.get("memory", {})
    mem_db = os.getenv("GEMINI_MEMORY_DB", memory_raw.get("db_path", "~/.gemini/memory.db"))
    m_cfg = MemoryConfig(
        backend=memory_raw.get("backend", "sqlite+vectors"),
        db_path=_expand_path(mem_db),
        embedding_model=memory_raw.get("embedding_model", "text-embedding-3-large"),
        max_entries_per_project=int(memory_raw.get("max_entries_per_project", 10000)),
    )

    # Secrets
    secrets_raw = raw.get("secrets", {})
    env_paths_raw = secrets_raw.get("env_paths", ["./.env", "~/.env"])
    s_cfg = SecretsConfig(
        provider=secrets_raw.get("provider", "bitwarden"),
        env_paths=[_expand_path(p) for p in env_paths_raw],
    )

    # Extensions
    ext_raw = raw.get("extensions", {})
    ext_state_file = os.getenv(
        "GEMINI_EXT_STATE_FILE", ext_raw.get("state_file", "~/.gemini/extensions_state.json")
    )
    e_cfg = ExtensionsConfig(
        marketplace_url_env=ext_raw.get("marketplace_url_env", "GEMINI_MARKETPLACE_URL"),
        marketplace_token_env=ext_raw.get("marketplace_token_env", "GEMINI_MARKETPLACE_TOKEN"),
        state_file=_expand_path(ext_state_file),
    )

    # CLI
    cli_raw = raw.get("cli", {})
    safe_mode_env = os.getenv("GEMINI_SAFE_MODE")
    if safe_mode_env is not None:
        safe_mode = safe_mode_env.lower() in {"1", "true", "yes", "on"}
    else:
        safe_mode = bool(cli_raw.get("safe_mode", True))

    c_cfg = CLIConfig(
        default_project_root=_expand_path(cli_raw.get("default_project_root", ".")),
        safe_mode=safe_mode,
    )

    return GeminiConfig(
        journaling=j_cfg,
        memory=m_cfg,
        secrets=s_cfg,
        extensions=e_cfg,
        cli=c_cfg,
    )
```

---

### `gemini_cli/core/guard.py`

```python
"""Guardrail utilities for enforcing Gemini's constitution in code.

These helpers provide safe wrappers around potentially destructive
filesystem operations. They are intentionally conservative and expect
the caller (CLI or agent) to provide user confirmation.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Callable


class DestructiveActionError(RuntimeError):
    """Raised when a destructive action is attempted without approval."""


def safe_delete_path(
    path: str | Path,
    confirm: Callable[[str], bool],
    backup: bool = True,
) -> None:
    """Safely delete a file or directory after explicit confirmation.

    - `confirm` is a callback that receives a human-readable description
      and must return True if the user explicitly approves.
    - If `backup` is True and the target is a file, a `.bak` copy is made
      alongside it before deletion.
    """
    p = Path(path)
    if not p.exists():
        return

    description = f"Delete '{p}' (type={'dir' if p.is_dir() else 'file'})"
    if not confirm(description):
        raise DestructiveActionError(f"Destructive action not approved: {description}")

    if backup and p.is_file():
        backup_path = p.with_suffix(p.suffix + ".bak" if p.suffix else ".bak")
        shutil.copy2(p, backup_path)

    if p.is_dir():
        shutil.rmtree(p)
    else:
        p.unlink()
```

---

### `gemini_cli/core/secrets.py`

```python
"""Secrets / .env discovery helpers for Gemini."""

from __future__ import annotations

import os
from pathlib import Path
from typing import List


def discover_env_files(project_root: str | Path) -> List[Path]:
    """Return a list of candidate .env files in priority order.

    1. <project_root>/.env
    2. ~/.env
    """
    root = Path(project_root).resolve()
    candidates = [
        root / ".env",
        Path.home() / ".env",
    ]
    return [c for c in candidates if c.exists()]


def ensure_env_permissions(path: Path) -> None:
    """Best-effort enforcement that .env is not world-readable.

    On POSIX systems, this attempts to set mode 0o600. On other systems,
    this function is effectively a no-op.
    """
    try:
        if os.name == "posix" and path.exists():
            os.chmod(path, 0o600)
    except Exception:
        # Best effort; do not raise in production flows.
        pass
```

---

### `gemini_cli/cli.py`

```python
"""Gemini CLI entrypoint.

Provides a small argparse-based CLI that wraps core functionality:
- init-project: copy templates into a target directory.
- status: show configuration and key paths.
- install-extensions: delegate to the extension installer script.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Optional

from .config_loader import load_config


def _copy_templates(target: Path, overwrite: bool = False) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    templates_dir = repo_root / "templates"
    if not templates_dir.exists():
        raise FileNotFoundError(f"Templates directory not found at {templates_dir}")

    target.mkdir(parents=True, exist_ok=True)

    for src in templates_dir.glob("*.md"):
        dest = target / src.name
        if dest.exists() and not overwrite:
            continue
        dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")


def cmd_init_project(args: argparse.Namespace) -> int:
    target = Path(args.target).expanduser().resolve()
    overwrite = bool(args.overwrite)
    _copy_templates(target, overwrite=overwrite)
    print(f"Initialized Gemini project templates in {target}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    print("Gemini CLI Status")
    print("------------------")
    print(f"Journaling dir: {cfg.journaling.base_dir}")
    print(f"Memory db:      {cfg.memory.db_path}")
    print(f"Secrets mode:   {cfg.secrets.provider}")
    print(f"Extensions state: {cfg.extensions.state_file}")
    print(f"Safe mode:      {cfg.cli.safe_mode}")
    return 0


def cmd_install_extensions(args: argparse.Namespace) -> int:
    """Delegate to the gemini_extension_installer script in tools/."""
    repo_root = Path(__file__).resolve().parents[1]
    script = repo_root / "tools" / "gemini_extension_installer.py"
    if not script.exists():
        print(f"Extension installer script not found at {script}", file=sys.stderr)
        return 1

    cmd = [sys.executable, str(script)]
    if args.marketplace_url:
        cmd.extend(["--marketplace-url", args.marketplace_url])
    if args.api_token:
        cmd.extend(["--api-token", args.api_token])
    if args.state_file:
        cmd.extend(["--state-file", args.state_file])
    if args.install_cmd:
        cmd.extend(["--install-cmd", args.install_cmd])
    if args.tag:
        cmd.extend(["--tag", args.tag])
    if args.category:
        cmd.extend(["--category", args.category])
    if args.name_pattern:
        cmd.extend(["--name-pattern", args.name_pattern])
    if args.dry_run:
        cmd.append("--dry-run")
    if args.verbose:
        cmd.append("--verbose")
    if args.quiet:
        cmd.append("--quiet")
    if args.log_file:
        cmd.extend(["--log-file", args.log_file])

    return subprocess.call(cmd)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gemini", description="Gemini CLI helper commands.")
    sub = parser.add_subparsers(dest="command", required=True)

    # init-project
    p_init = sub.add_parser("init-project", help="Initialize Gemini project templates in a directory.")
    p_init.add_argument("--target", default=".", help="Target directory (default: .)")
    p_init.add_argument("--overwrite", action="store_true", help="Overwrite existing files if present.")
    p_init.set_defaults(func=cmd_init_project)

    # status
    p_status = sub.add_parser("status", help="Show configuration and key paths.")
    p_status.add_argument("--config", help="Path to config YAML (optional).")
    p_status.set_defaults(func=cmd_status)

    # install-extensions
    p_inst = sub.add_parser("install-extensions", help="Install extensions from the marketplace.")
    p_inst.add_argument("--marketplace-url", help="Marketplace URL (overrides env).")
    p_inst.add_argument("--api-token", help="Marketplace API token (overrides env).")
    p_inst.add_argument("--state-file", help="State file path (default: config setting).")
    p_inst.add_argument("--install-cmd", help="Install command template (default: script default).")
    p_inst.add_argument("--tag", help="Filter by tag.")
    p_inst.add_argument("--category", help="Filter by category.")
    p_inst.add_argument("--name-pattern", help="Filter by name/id regex.")
    p_inst.add_argument("--dry-run", action="store_true", help="Dry run mode.")
    p_inst.add_argument("--verbose", action="store_true", help="Verbose logging.")
    p_inst.add_argument("--quiet", action="store_true", help="Quiet mode.")
    p_inst.add_argument("--log-file", help="Path to log file.")
    p_inst.set_defaults(func=cmd_install_extensions)

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
