#!/usr/bin/env python3
"""
Script Name: repo_bootstrap.py
Author: cbwinslow (CloudCurio)
Date: 2025-11-16

Summary:
    Unified bootstrap tool for setting up the CloudCurio and OpenDiscourse
    monorepos locally, and creating matching repositories on GitHub, GitLab,
    and Gitea.

    The script will:
      - Create local directory trees for:
          * cloudcurio-kingdom/ (CloudCurio ecosystem)
          * opendiscourse/ (OpenDiscourse political intelligence platform)
      - Optionally create additional repos such as:
          * cbw-dotfiles
          * cbw-knowledge-base
      - Create remote repos via the respective APIs.

Inputs:
    Environment variables:
        GITHUB_TOKEN      - GitHub PAT with repo create permission.
        GITHUB_OWNER      - GitHub username or org (e.g. "cbwinslow").

        GITLAB_TOKEN      - GitLab Personal Access Token.
        GITLAB_BASE_URL   - Base URL for GitLab (default: https://gitlab.com).
        GITLAB_OWNER      - GitLab username or group (optional).

        GITEA_TOKEN       - Gitea API token (optional).
        GITEA_BASE_URL    - Base URL for Gitea (e.g. https://gitea.example.com).
        GITEA_OWNER       - Gitea username or org (optional).

    Command-line flags:
        --local-only       - Only create local trees, skip remote repo creation.
        --remote-only      - Only create remote repos, skip local trees.
        --platforms        - Comma-separated list of platforms to target
                             (github,gitlab,gitea). Default: all detected.
        --dry-run          - Do not perform destructive/remote actions.

Outputs:
    - Local directories and README files for each monorepo.
    - Remote repositories on configured platforms, where permitted.

Notes:
    - This script does NOT store any credentials; it only reads tokens
      from environment variables.
    - Safe to re-run: remote repo creation will no-op if the repo exists
      (best-effort; it logs errors instead of crashing).
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional

try:
    import requests  # type: ignore
except ImportError:
    print("[ERROR] The 'requests' package is required. Install with 'pip install requests'.", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
LOGGER = logging.getLogger("repo_bootstrap")
LOG_FILE = "/tmp/CBW-repo_bootstrap.log"


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    LOGGER.setLevel(level)

    formatter = logging.Formatter("[%(levelname)s] %(message)s")

    fh = logging.FileHandler(LOG_FILE)
    fh.setLevel(level)
    fh.setFormatter(formatter)
    LOGGER.addHandler(fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    ch.setFormatter(formatter)
    LOGGER.addHandler(ch)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------
@dataclass
class RepoDefinition:
    name: str
    description: str
    private: bool = True
    create_on_github: bool = True
    create_on_gitlab: bool = True
    create_on_gitea: bool = False
    local_path: Optional[str] = None
    extra_metadata: Dict[str, str] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Local tree creation
# ---------------------------------------------------------------------------

CLOUDCURIO_DIRS: List[str] = [
    "cloudcurio-kingdom/agents/crews",
    "cloudcurio-kingdom/agents/logs",
    "cloudcurio-kingdom/agents/tools",
    "cloudcurio-kingdom/apps/gui",
    "cloudcurio-kingdom/apps/tui",
    "cloudcurio-kingdom/apps/web",
    "cloudcurio-kingdom/data/knowledge-base",
    "cloudcurio-kingdom/data/indexes",
    "cloudcurio-kingdom/data/snapshots",
    "cloudcurio-kingdom/docs/handbook",
    "cloudcurio-kingdom/docs/projects",
    "cloudcurio-kingdom/docs/context",
    "cloudcurio-kingdom/docs/resume",
    "cloudcurio-kingdom/docs/bookmarks",
    "cloudcurio-kingdom/docs/journals",
    "cloudcurio-kingdom/docs/tasks",
    "cloudcurio-kingdom/infra/docker/stacks",
    "cloudcurio-kingdom/infra/terraform",
    "cloudcurio-kingdom/infra/pulumi",
    "cloudcurio-kingdom/infra/cloud-init",
    "cloudcurio-kingdom/infra/ubuntu-templates",
    "cloudcurio-kingdom/libs/python",
    "cloudcurio-kingdom/libs/go",
    "cloudcurio-kingdom/libs/typescript",
    "cloudcurio-kingdom/research/personal",
    "cloudcurio-kingdom/research/agents",
    "cloudcurio-kingdom/research/homelab",
    "cloudcurio-kingdom/services/rag",
    "cloudcurio-kingdom/services/monitoring",
    "cloudcurio-kingdom/tools/dotfiles",
    "cloudcurio-kingdom/tools/dotbins",
    "cloudcurio-kingdom/tools/config-snapshots",
    "cloudcurio-kingdom/tools/installers",
    "cloudcurio-kingdom/tools/scripts",
]

OPENDISCOURSE_DIRS: List[str] = [
    "opendiscourse/docs/specs",
    "opendiscourse/docs/design",
    "opendiscourse/docs/methodology",
    "opendiscourse/docs/datasets",
    "opendiscourse/data/raw/congress",
    "opendiscourse/data/raw/openstates",
    "opendiscourse/data/raw/fec",
    "opendiscourse/data/raw/lobbying",
    "opendiscourse/data/raw/ethics",
    "opendiscourse/data/raw/courts",
    "opendiscourse/data/raw/regulators",
    "opendiscourse/data/raw/social-media",
    "opendiscourse/data/raw/news",
    "opendiscourse/data/processed/entities",
    "opendiscourse/data/processed/votes",
    "opendiscourse/data/processed/bills",
    "opendiscourse/data/processed/trades",
    "opendiscourse/data/processed/donations",
    "opendiscourse/data/processed/graphs",
    "opendiscourse/data/processed/embeddings",
    "opendiscourse/data/processed/indices",
    "opendiscourse/services/api",
    "opendiscourse/services/ingestion",
    "opendiscourse/services/analytics",
    "opendiscourse/services/alerts",
    "opendiscourse/apps/dashboard",
    "opendiscourse/apps/admin",
    "opendiscourse/apps/api-clients",
    "opendiscourse/infra/docker",
    "opendiscourse/infra/terraform",
    "opendiscourse/infra/pulumi",
    "opendiscourse/infra/ci-cd",
    "opendiscourse/research/prototypes",
    "opendiscourse/research/ml",
    "opendiscourse/research/nlp",
    "opendiscourse/tools/scripts",
    "opendiscourse/tools/migrations",
]


def write_file_if_missing(path: str, content: str) -> None:
    if os.path.exists(path):
        return
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def create_cloudcurio_tree(base_dir: str = ".") -> None:
    LOGGER.info("Creating CloudCurio directory tree...")
    for rel in CLOUDCURIO_DIRS:
        full = os.path.join(base_dir, rel)
        os.makedirs(full, exist_ok=True)
    # Root README
    write_file_if_missing(
        os.path.join(base_dir, "cloudcurio-kingdom", "README.md"),
        """# CloudCurio Kingdom Monorepo \ud83d\udc51\n\nThis repo holds CloudCurio tools, agents, infra, knowledge-base scaffolding,\ndotfiles helpers, and related projects.\n""",
    )
    # Tasks + journals placeholders
    write_file_if_missing(
        os.path.join(base_dir, "cloudcurio-kingdom", "docs", "tasks", "TASKS.md"),
        """# Tasks (cbw-todo)\n\nUse this file to track micro-goals, pytest/unittest criteria, and completion\nchecklists for your projects.\n""",
    )
    write_file_if_missing(
        os.path.join(base_dir, "cloudcurio-kingdom", "docs", "journals", "JOURNALS.md"),
        """# Journals\n\nDaily notes, AI agent summaries, and work logs live here.\n""",
    )


def create_opendiscourse_tree(base_dir: str = ".") -> None:
    LOGGER.info("Creating OpenDiscourse directory tree...")
    for rel in OPENDISCOURSE_DIRS:
        full = os.path.join(base_dir, rel)
        os.makedirs(full, exist_ok=True)
    write_file_if_missing(
        os.path.join(base_dir, "opendiscourse", "README.md"),
        """# OpenDiscourse Monorepo\n\nOpenDiscourse focuses on political data: legislators, votes, bills, trades,\ndonations, hearings, regulators, and the narratives around them.\n""",
    )


# ---------------------------------------------------------------------------
# Remote repo creation helpers
# ---------------------------------------------------------------------------


def github_create_repo(repo: RepoDefinition, dry_run: bool = False) -> None:
    token = os.getenv("GITHUB_TOKEN")
    owner = os.getenv("GITHUB_OWNER")
    if not token:
        LOGGER.warning("GITHUB_TOKEN not set; skipping GitHub repo '%s'", repo.name)
        return

    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}

    if owner:
        url = f"https://api.github.com/orgs/{owner}/repos"
    else:
        url = "https://api.github.com/user/repos"

    payload = {
        "name": repo.name,
        "description": repo.description,
        "private": repo.private,
    }

    LOGGER.info("[GitHub] Creating repo '%s' (owner=%s)" , repo.name, owner or "<user>")
    if dry_run:
        LOGGER.info("[GitHub] DRY-RUN payload: %s", json.dumps(payload))
        return

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
    except Exception as exc:  # noqa: BLE001
        LOGGER.error("[GitHub] Error creating repo '%s': %s", repo.name, exc)
        return

    if resp.status_code in (200, 201):
        LOGGER.info("[GitHub] Repo '%s' created or already exists.", repo.name)
    elif resp.status_code == 422:
        # Likely already exists
        LOGGER.info("[GitHub] Repo '%s' already exists (422).", repo.name)
    else:
        LOGGER.error("[GitHub] Failed to create repo '%s': %s", repo.name, resp.text)


def gitlab_create_repo(repo: RepoDefinition, dry_run: bool = False) -> None:
    token = os.getenv("GITLAB_TOKEN")
    base_url = os.getenv("GITLAB_BASE_URL", "https://gitlab.com").rstrip("/")
    owner = os.getenv("GITLAB_OWNER")

    if not token:
        LOGGER.warning("GITLAB_TOKEN not set; skipping GitLab repo '%s'", repo.name)
        return

    headers = {"PRIVATE-TOKEN": token}
    url = f"{base_url}/api/v4/projects"

    visibility = "private" if repo.private else "public"

    payload = {
        "name": repo.name,
        "path": repo.name,
        "visibility": visibility,
    }

    if owner:
        payload["namespace_id"] = owner  # May need numeric ID in real usage

    LOGGER.info("[GitLab] Creating repo '%s' at %s", repo.name, base_url)
    if dry_run:
        LOGGER.info("[GitLab] DRY-RUN payload: %s", json.dumps(payload))
        return

    try:
        resp = requests.post(url, headers=headers, data=payload, timeout=15)
    except Exception as exc:  # noqa: BLE001
        LOGGER.error("[GitLab] Error creating repo '%s': %s", repo.name, exc)
        return

    if resp.status_code in (200, 201):
        LOGGER.info("[GitLab] Repo '%s' created or already exists.", repo.name)
    elif resp.status_code == 400 and "has already been taken" in resp.text:
        LOGGER.info("[GitLab] Repo '%s' already exists (400).", repo.name)
    else:
        LOGGER.error("[GitLab] Failed to create repo '%s': %s", repo.name, resp.text)


def gitea_create_repo(repo: RepoDefinition, dry_run: bool = False) -> None:
    token = os.getenv("GITEA_TOKEN")
    base_url = os.getenv("GITEA_BASE_URL", "").rstrip("/")
    owner = os.getenv("GITEA_OWNER")

    if not token or not base_url:
        LOGGER.warning("GITEA_TOKEN or GITEA_BASE_URL not set; skipping Gitea repo '%s'", repo.name)
        return

    headers = {"Authorization": f"token {token}", "Content-Type": "application/json"}

    if owner:
        url = f"{base_url}/api/v1/orgs/{owner}/repos"
    else:
        url = f"{base_url}/api/v1/user/repos"

    payload = {
        "name": repo.name,
        "description": repo.description,
        "private": repo.private,
    }

    LOGGER.info("[Gitea] Creating repo '%s' at %s", repo.name, base_url)
    if dry_run:
        LOGGER.info("[Gitea] DRY-RUN payload: %s", json.dumps(payload))
        return

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
    except Exception as exc:  # noqa: BLE001
        LOGGER.error("[Gitea] Error creating repo '%s': %s", repo.name, exc)
        return

    if resp.status_code in (200, 201):
        LOGGER.info("[Gitea] Repo '%s' created or already exists.", repo.name)
    elif resp.status_code == 409:
        LOGGER.info("[Gitea] Repo '%s' already exists (409).", repo.name)
    else:
        LOGGER.error("[Gitea] Failed to create repo '%s': %s", repo.name, resp.text)


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def build_repo_definitions() -> List[RepoDefinition]:
    """Define the core repos we care about."""
    return [
        RepoDefinition(
            name="cloudcurio-kingdom",
            description="CloudCurio monorepo: tools, agents, infra, knowledge-base, and homelab glue.",
            create_on_gitea=True,
        ),
        RepoDefinition(
            name="opendiscourse",
            description="OpenDiscourse: political data intelligence platform (bills, votes, trades, donations, narratives).",
            create_on_gitea=True,
        ),
        RepoDefinition(
            name="cbw-dotfiles",
            description="Dotfiles, dotfolders, dotbins, and dev environment setup.",
            create_on_gitea=False,
        ),
        RepoDefinition(
            name="cbw-knowledge-base",
            description="Personal knowledge base, docs, bookmarks, context, and RAG-ready content.",
            create_on_gitea=False,
        ),
    ]


def create_local_trees(local_only: bool) -> None:
    """Create the local directory structures for the two monorepos."""
    create_cloudcurio_tree()
    create_opendiscourse_tree()


def create_remote_repos(
    repos: List[RepoDefinition],
    platforms: List[str],
    dry_run: bool = False,
) -> None:
    """Create remote repos on selected platforms."""
    for repo in repos:
        if "github" in platforms and repo.create_on_github:
            github_create_repo(repo, dry_run=dry_run)
        if "gitlab" in platforms and repo.create_on_gitlab:
            gitlab_create_repo(repo, dry_run=dry_run)
        if "gitea" in platforms and repo.create_on_gitea:
            gitea_create_repo(repo, dry_run=dry_run)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bootstrap CloudCurio + OpenDiscourse monorepos and remote repos.",
    )
    parser.add_argument(
        "--local-only",
        action="store_true",
        help="Only create local directory trees (no remote API calls).",
    )
    parser.add_argument(
        "--remote-only",
        action="store_true",
        help="Only create remote repos (no local directories).",
    )
    parser.add_argument(
        "--platforms",
        type=str,
        default="github,gitlab,gitea",
        help="Comma-separated list of platforms: github,gitlab,gitea.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making remote changes.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    setup_logging(verbose=args.verbose)

    if args.local_only and args.remote_only:
        LOGGER.error("Cannot use --local-only and --remote-only together.")
        return 1

    platforms = [p.strip().lower() for p in args.platforms.split(",") if p.strip()]
    valid_platforms = {"github", "gitlab", "gitea"}
    for p in platforms:
        if p not in valid_platforms:
            LOGGER.error("Invalid platform '%s'. Valid: github, gitlab, gitea.", p)
            return 1

    repos = build_repo_definitions()

    if not args.remote_only:
        create_local_trees(local_only=args.local_only)

    if not args.local_only:
        create_remote_repos(repos, platforms=platforms, dry_run=args.dry_run)

    LOGGER.info("Bootstrap completed.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
