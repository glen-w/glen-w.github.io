"""Build timeline marks from public GitHub repositories.

Source: GitHub REST API for the username in ``_data/socials.yml``.
Each public owned repo contributes one timeline item per distinct year among
``created_at`` and ``pushed_at`` (unique projects per year — not commit counts).

Writes ``assets/json/code-repos.json`` for the career timeline.

Refresh from repo root::

    PYTHONPATH=. python processing/library/github_repos.py

Optional ``GITHUB_TOKEN`` / ``GH_TOKEN`` raises the rate limit.
"""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set

import yaml

USER_AGENT = "glenwright.earth-code-repos/1.0 (+https://glenwright.earth)"
API_BASE = "https://api.github.com"


def project_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def github_username(root: str) -> str:
    path = os.path.join(root, "_data", "socials.yml")
    with open(path, encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    username = str(data.get("github_username") or "").strip()
    if not username:
        raise SystemExit("github_username missing from _data/socials.yml")
    return username


def _auth_headers() -> Dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": USER_AGENT,
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = (os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def github_get(url: str) -> Any:
    request = urllib.request.Request(url, headers=_auth_headers())
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"GitHub API {exc.code} for {url}: {body[:400]}") from exc


def year_from_iso(value: Optional[str]) -> Optional[int]:
    if not value or len(value) < 4:
        return None
    try:
        return int(value[:4])
    except ValueError:
        return None


def fetch_public_repos(username: str) -> List[Dict[str, Any]]:
    """All public non-fork repos owned by ``username`` (paginated)."""
    repos: List[Dict[str, Any]] = []
    page = 1
    while True:
        url = (
            f"{API_BASE}/users/{urllib.parse.quote(username)}/repos"
            f"?type=owner&per_page=100&page={page}&sort=full_name"
        )
        batch = github_get(url)
        if not isinstance(batch, list) or not batch:
            break
        for raw in batch:
            if not isinstance(raw, dict):
                continue
            if raw.get("private"):
                continue
            if raw.get("fork"):
                continue
            full_name = str(raw.get("full_name") or "").strip()
            name = str(raw.get("name") or "").strip()
            if not full_name or not name:
                continue
            created = year_from_iso(raw.get("created_at"))
            pushed = year_from_iso(raw.get("pushed_at"))
            if created is None and pushed is None:
                continue
            repos.append(
                {
                    "id": full_name,
                    "name": name,
                    "url": str(raw.get("html_url") or f"https://github.com/{full_name}"),
                    "description": (str(raw.get("description") or "").strip() or None),
                    "created_year": created,
                    "pushed_year": pushed,
                    "archived": bool(raw.get("archived")),
                }
            )
        if len(batch) < 100:
            break
        page += 1
    repos.sort(key=lambda row: row["id"].lower())
    return repos


def timeline_items(repos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """One catalogue-shaped item per (repo, year) for created/pushed years."""
    items: List[Dict[str, Any]] = []
    for repo in repos:
        years: Set[int] = set()
        if repo.get("created_year") is not None:
            years.add(int(repo["created_year"]))
        if repo.get("pushed_year") is not None:
            years.add(int(repo["pushed_year"]))
        for year in sorted(years):
            items.append(
                {
                    "id": f"repo:{repo['id']}:{year}",
                    "repo": repo["id"],
                    "title": repo["name"],
                    "year": year,
                    "type": "Code",
                    "roles": ["contributor"],
                    "venue": "GitHub",
                    "url": repo["url"],
                    "info": repo["url"],
                    "description": repo.get("description"),
                }
            )
    items.sort(key=lambda row: (-row["year"], row["title"].lower()))
    return items


def write_catalog(root: str, username: str, repos: List[Dict[str, Any]]) -> str:
    out_dir = os.path.join(root, "assets", "json")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "code-repos.json")
    payload = {
        "v": 1,
        "username": username,
        "fetched": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "rule": "unique public non-fork repos per year from created_at and pushed_at",
        "repos": repos,
        "items": timeline_items(repos),
    }
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--username",
        default=None,
        help="GitHub login (default: _data/socials.yml github_username)",
    )
    args = parser.parse_args()
    root = project_root()
    username = args.username or github_username(root)
    repos = fetch_public_repos(username)
    path = write_catalog(root, username, repos)
    items = timeline_items(repos)
    years = sorted({item["year"] for item in items})
    print(f"Wrote {path}")
    print(f"{len(repos)} public repos → {len(items)} year marks ({years[0]}–{years[-1]})" if years else "no marks")


if __name__ == "__main__":
    main()
