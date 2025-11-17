#!/usr/bin/env python3
"""
Script Name: gemini_extension_installer.py
Author: Blaine & AI Copilot
Date: 2025-11-14

Summary:
    CLI utility to synchronize a local Gemini-CLI installation with all
    extensions available on the configured Gemini Extension Marketplace.

    The tool will:
      - Discover all extensions from a configurable HTTP API endpoint.
      - Optionally filter extensions by tag, category, or name pattern.
      - Install or update each extension via a configurable shell command.
      - Maintain a local state file with installed versions.
      - Provide dry-run and detailed logging options.

Inputs:
    - Marketplace URL (via CLI flag or environment variable GEMINI_MARKETPLACE_URL).
    - Optional API token (via CLI flag or GEMINI_MARKETPLACE_TOKEN env var).
    - Optional filters: --tag, --category, --name-pattern.
    - Logging options: --verbose, --quiet, --log-file.

Outputs:
    - Installed / updated extensions in the local Gemini-CLI environment.
    - A JSON state file (default: .gemini/extensions_state.json) tracking
      installed extensions and versions.
    - Log output to stdout and optional log file.

Modification Log:
    2025-11-14: Initial version.

Security Notes:
    - API tokens should be supplied via environment variables or secure
      secret managers (e.g., Bitwarden) and not hard-coded.
    - The script avoids logging sensitive tokens.
    - File permissions for the .gemini directory and state file should be
      restricted to the current user.
"""

import argparse
import json
import logging
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import requests
except ImportError as exc:  # pragma: no cover - import guard
    print("[ERROR] The 'requests' library is required. Install via: pip install requests", file=sys.stderr)
    raise


@dataclass
class Extension:
    """Represents a single extension from the marketplace."""

    id: str
    name: str
    version: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None


@dataclass
class InstallerConfig:
    """Configuration for installing extensions."""

    marketplace_url: str
    api_token: Optional[str]
    state_file: Path
    install_command_template: str
    dry_run: bool


def setup_logging(verbose: bool, quiet: bool, log_file: Optional[Path]) -> None:
    """Configure logging for the script.

    Priority: quiet < default < verbose.
    """

    if quiet:
        level = logging.WARNING
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    handlers: List[logging.Handler] = [logging.StreamHandler(sys.stdout)]

    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=level,
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        handlers=handlers,
    )


def load_state(path: Path) -> Dict[str, Any]:
    """Load the existing extension state from disk, if present.

    Returns an empty dict if the file does not exist or is invalid.
    """

    if not path.exists():
        logging.debug("No existing state file found at %s", path)
        return {}

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                logging.warning("State file %s is not a JSON object; ignoring", path)
                return {}
            return data
    except Exception as exc:  # pragma: no cover - defensive
        logging.error("Failed to load state file %s: %s", path, exc)
        return {}


def save_state(path: Path, state: Dict[str, Any]) -> None:
    """Persist the extension state to disk safely using a temp file + rename."""

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")

    try:
        with tmp_path.open("w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, sort_keys=True)
        tmp_path.replace(path)
        logging.debug("Saved state to %s", path)
    except Exception as exc:  # pragma: no cover - defensive
        logging.error("Failed to save state file %s: %s", path, exc)


def build_auth_headers(api_token: Optional[str]) -> Dict[str, str]:
    """Build HTTP headers for authenticating with the marketplace.

    Avoid logging the token for security reasons.
    """

    headers: Dict[str, str] = {"Accept": "application/json"}
    if api_token:
        headers["Authorization"] = f"Bearer {api_token}"
    return headers


def fetch_extensions(config: InstallerConfig) -> List[Extension]:
    """Fetch the list of available extensions from the marketplace.

    The marketplace is expected to return JSON in the form:
        [{
            "id": "extension-id",
            "name": "Nice Extension",
            "version": "1.2.3",
            "description": "...",
            "tags": ["dev", "cli"],
            "category": "developer-tools"
        }, ...]
    """

    logging.info("Fetching extensions from %s", config.marketplace_url)

    try:
        response = requests.get(config.marketplace_url, headers=build_auth_headers(config.api_token), timeout=30)
        response.raise_for_status()
    except requests.RequestException as exc:
        logging.error("Failed to fetch extensions from marketplace: %s", exc)
        raise SystemExit(1) from exc

    try:
        data = response.json()
    except Exception as exc:  # pragma: no cover - defensive
        logging.error("Marketplace response is not valid JSON: %s", exc)
        raise SystemExit(1) from exc

    if not isinstance(data, list):
        logging.error("Marketplace response is not a list; got %r", type(data))
        raise SystemExit(1)

    extensions: List[Extension] = []
    for raw in data:
        if not isinstance(raw, dict):
            logging.debug("Skipping non-dict entry from marketplace: %r", raw)
            continue
        try:
            ext = Extension(
                id=str(raw.get("id")),
                name=str(raw.get("name")),
                version=str(raw.get("version")),
                description=raw.get("description"),
                tags=raw.get("tags") or [],
                category=raw.get("category"),
            )
            extensions.append(ext)
        except Exception as exc:  # pragma: no cover - defensive
            logging.warning("Failed to parse extension entry %r: %s", raw, exc)

    logging.info("Discovered %d extension(s) from marketplace", len(extensions))
    return extensions


def filter_extensions(
    extensions: List[Extension],
    tag: Optional[str] = None,
    category: Optional[str] = None,
    name_pattern: Optional[str] = None,
) -> List[Extension]:
    """Apply optional filters to the extension list."""

    filtered = extensions

    if tag:
        tag_lower = tag.lower()
        filtered = [e for e in filtered if any(t.lower() == tag_lower for t in (e.tags or []))]

    if category:
        cat_lower = category.lower()
        filtered = [e for e in filtered if (e.category or "").lower() == cat_lower]

    if name_pattern:
        pattern = re.compile(name_pattern, re.IGNORECASE)
        filtered = [e for e in filtered if pattern.search(e.name) or pattern.search(e.id)]

    logging.info("Filtered to %d extension(s) after applying criteria", len(filtered))
    return filtered


def extension_needs_install(ext: Extension, state: Dict[str, Any]) -> bool:
    """Determine whether an extension should be installed/updated."""

    existing = state.get(ext.id)
    if not isinstance(existing, dict):
        return True

    current_version = existing.get("version")
    needs = current_version != ext.version
    logging.debug(
        "Extension '%s' current_version=%r, marketplace_version=%r -> needs_install=%s",
        ext.id,
        current_version,
        ext.version,
        needs,
    )
    return needs


def install_extension(ext: Extension, config: InstallerConfig) -> bool:
    """Install or update a single extension.

    Returns True on success, False on failure.
    Uses a configurable shell command template with {id} substitution.
    """

    command = config.install_command_template.format(id=ext.id)
    logging.info("Installing extension '%s' (%s) with command: %s", ext.name, ext.id, command)

    if config.dry_run:
        logging.info("[DRY RUN] Skipping actual installation of '%s'", ext.id)
        return True

    try:
        result = subprocess.run(
            command,
            shell=True,
            check=False,
            capture_output=True,
            text=True,
        )
    except Exception as exc:  # pragma: no cover - defensive
        logging.error("Failed to execute install command for '%s': %s", ext.id, exc)
        return False

    if result.returncode != 0:
        logging.error(
            "Install command failed for '%s' (exit=%s): %s",
            ext.id,
            result.returncode,
            result.stderr.strip(),
        )
        return False

    logging.debug("Install command stdout for '%s': %s", ext.id, result.stdout.strip())
    logging.info("Successfully installed '%s' (%s)", ext.name, ext.id)
    return True


def sync_extensions(
    config: InstallerConfig,
    tag: Optional[str] = None,
    category: Optional[str] = None,
    name_pattern: Optional[str] = None,
) -> None:
    """High-level orchestration to fetch, filter, and install extensions."""

    state = load_state(config.state_file)
    all_extensions = fetch_extensions(config)
    target_extensions = filter_extensions(all_extensions, tag=tag, category=category, name_pattern=name_pattern)

    installed_count = 0
    skipped_count = 0
    failed_count = 0

    for ext in target_extensions:
        if not extension_needs_install(ext, state):
            logging.info("Extension '%s' (%s) already up-to-date; skipping", ext.name, ext.id)
            skipped_count += 1
            continue

        success = install_extension(ext, config)
        if success:
            state[ext.id] = {
                "name": ext.name,
                "version": ext.version,
                "category": ext.category,
                "tags": ext.tags,
            }
            installed_count += 1
        else:
            failed_count += 1

    save_state(config.state_file, state)

    logging.info(
        "Summary: installed=%d, skipped=%d, failed=%d (dry_run=%s)",
        installed_count,
        skipped_count,
        failed_count,
        config.dry_run,
    )

    if failed_count > 0:
        raise SystemExit(1)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description="Install all (or a subset of) Gemini-CLI extensions from the marketplace.",
    )

    parser.add_argument(
        "--marketplace-url",
        dest="marketplace_url",
        metavar="URL",
        help="Gemini Extension Marketplace URL (default: from GEMINI_MARKETPLACE_URL)",
    )

    parser.add_argument(
        "--api-token",
        dest="api_token",
        metavar="TOKEN",
        help="API token for the marketplace (default: from GEMINI_MARKETPLACE_TOKEN)",
    )

    parser.add_argument(
        "--state-file",
        dest="state_file",
        metavar="PATH",
        default=str(Path.home() / ".gemini" / "extensions_state.json"),
        help="Path to JSON state file tracking installed extensions (default: ~/.gemini/extensions_state.json)",
    )

    parser.add_argument(
        "--install-cmd",
        dest="install_cmd",
        metavar="CMD",
        default="gemini extensions install {id}",
        help="Shell command template used to install an extension (default: 'gemini extensions install {id}')",
    )

    parser.add_argument(
        "--tag",
        dest="tag",
        metavar="TAG",
        help="Only install extensions that have the given tag",
    )

    parser.add_argument(
        "--category",
        dest="category",
        metavar="CATEGORY",
        help="Only install extensions in the given category",
    )

    parser.add_argument(
        "--name-pattern",
        dest="name_pattern",
        metavar="REGEX",
        help="Only install extensions where name or id matches the regex pattern",
    )

    parser.add_argument(
        "--dry-run",
        dest="dry_run",
        action="store_true",
        help="Show what would be installed but do not make any changes",
    )

    parser.add_argument(
        "--verbose",
        dest="verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    parser.add_argument(
        "--quiet",
        dest="quiet",
        action="store_true",
        help="Reduce logging output to warnings and errors only",
    )

    parser.add_argument(
        "--log-file",
        dest="log_file",
        metavar="PATH",
        help="Optional path to a log file",
    )

    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> None:
    """Main entrypoint for the script."""

    args = parse_args(argv)

    marketplace_url = args.marketplace_url or os.getenv("GEMINI_MARKETPLACE_URL")
    if not marketplace_url:
        print(
            "[ERROR] Marketplace URL must be provided via --marketplace-url or GEMINI_MARKETPLACE_URL env var",
            file=sys.stderr,
        )
        raise SystemExit(1)

    api_token = args.api_token or os.getenv("GEMINI_MARKETPLACE_TOKEN")

    state_file = Path(args.state_file).expanduser()
    log_file = Path(args.log_file).expanduser() if args.log_file else None

    setup_logging(verbose=args.verbose, quiet=args.quiet, log_file=log_file)

    config = InstallerConfig(
        marketplace_url=marketplace_url,
        api_token=api_token,
        state_file=state_file,
        install_command_template=args.install_cmd,
        dry_run=args.dry_run,
    )

    logging.debug("Using config: %s", config)

    try:
        sync_extensions(
            config=config,
            tag=args.tag,
            category=args.category,
            name_pattern=args.name_pattern,
        )
    except SystemExit:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        logging.exception("Unexpected error while syncing extensions: %s", exc)
        raise SystemExit(1) from exc


if __name__ == "__main__":  # pragma: no cover
    main()
