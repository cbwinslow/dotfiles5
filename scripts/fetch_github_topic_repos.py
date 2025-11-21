#!/usr/bin/env python3
"""
Fetch the top starred GitHub repositories for a topic and clone them locally.

Usage examples:
  python scripts/fetch_github_topic_repos.py tui
  python scripts/fetch_github_topic_repos.py linux -n 50 --sort forks --order asc --download-dir ./tmp_repos
"""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request


GITHUB_SEARCH_URL = "https://api.github.com/search/repositories"


def fetch_repositories(
    topic: str,
    limit: int,
    token: str | None,
    sort: str,
    order: str,
) -> list[dict]:
    """Return a list of repositories for the topic, ordered by the provided sort key."""
    per_page = min(limit, 100)
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "topic-repo-downloader",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    repos: list[dict] = []
    page = 1
    while len(repos) < limit:
        query = urllib.parse.urlencode(
            {
                "q": f"topic:{topic}",
                "sort": sort,
                "order": order,
                "per_page": per_page,
                "page": page,
            }
        )
        url = f"{GITHUB_SEARCH_URL}?{query}"
        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request) as response:
                payload = json.load(response)
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(
                f"GitHub API error {exc.code}: {error_body or exc.reason}"
            ) from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Network error: {exc.reason}") from exc

        items = payload.get("items", [])
        if not items:
            break

        repos.extend(items)
        if len(items) < per_page:
            break
        page += 1

    return repos[:limit]


def clone_repository(clone_url: str, dest: Path) -> bool:
    """Clone the repository into dest. Returns True if cloned, False if skipped."""
    if dest.exists():
        print(f"Skipping {dest} (already exists)")
        return False

    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", clone_url, str(dest)],
            check=True,
        )
        return True
    except subprocess.CalledProcessError as exc:
        print(f"Failed to clone {clone_url} -> {dest}: {exc}", file=sys.stderr)
        return False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download the top starred GitHub repositories for a topic."
    )
    parser.add_argument("topic", help="GitHub topic to search for (e.g., tui)")
    parser.add_argument(
        "-n",
        "--limit",
        type=int,
        default=100,
        help="Number of repositories to fetch (max 100 per page, default: 100)",
    )
    parser.add_argument(
        "--download-dir",
        default="./downloaded_repos",
        help="Directory where repositories will be cloned",
    )
    parser.add_argument(
        "--list-file",
        help="Optional path to write the list of repository URLs. "
        "Defaults to <download-dir>/<topic>/<topic>_repos.txt",
    )
    parser.add_argument(
        "--sort",
        choices=["stars", "forks", "help-wanted-issues", "updated"],
        default="stars",
        help="Sort criteria supported by GitHub search API. Default: stars",
    )
    parser.add_argument(
        "--order",
        choices=["desc", "asc"],
        default="desc",
        help="Sort order. Default: desc",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    topic = args.topic.strip()
    limit = max(1, args.limit)
    token = os.environ.get("GITHUB_TOKEN")

    try:
        repos = fetch_repositories(topic, limit, token, args.sort, args.order)
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        return 1

    topic_dir = Path(args.download_dir).expanduser().resolve() / topic
    list_path = (
        Path(args.list_file).expanduser().resolve()
        if args.list_file
        else topic_dir / f"{topic}_repos.txt"
    )
    list_path.parent.mkdir(parents=True, exist_ok=True)

    cloned = 0
    for repo in repos:
        owner = repo.get("owner", {}).get("login", "unknown")
        name = repo.get("name", "unnamed")
        dest = topic_dir / f"{owner}__{name}"
        clone_url = repo.get("clone_url")
        if clone_url and clone_repository(clone_url, dest):
            cloned += 1

    with list_path.open("w", encoding="utf-8") as handle:
        for repo in repos:
            url = repo.get("html_url") or repo.get("clone_url") or ""
            handle.write(f"{url}\n")

    print(
        f"Fetched {len(repos)} repos for topic '{topic}'. "
        f"Cloned {cloned}. List written to {list_path}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
