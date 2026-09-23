"""User-defined library exclusions.

Count list (``_data/library_exclude_from_counts.yml``, gitignored): items still
appear in the unfiltered catalogue and text search; they are omitted from
type/role/language chip counts and from those facet result lists on /library/.
Each entry may be a BibTeX key or a title (case-insensitive).

Timeline list (``_data/library_exclude_from_timeline.yml``, gitignored): GitHub
repo names or ``owner/name`` values omitted from the career timeline Code
series when ``github_repos.py`` writes ``assets/json/code-repos.json``.
"""

from __future__ import annotations

import os
import re
from typing import Any, Dict, Iterable, List, Optional, Set

import yaml

EXCLUDE_FILENAME = "library_exclude_from_counts.yml"
TIMELINE_EXCLUDE_FILENAME = "library_exclude_from_timeline.yml"


def exclude_list_path(project_root: str) -> str:
    return os.path.join(project_root, "_data", EXCLUDE_FILENAME)


def timeline_exclude_list_path(project_root: str) -> str:
    return os.path.join(project_root, "_data", TIMELINE_EXCLUDE_FILENAME)


def _normalize(value: str) -> str:
    text = re.sub(r"[{}]", "", str(value or ""))
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text


def _tokens_from_yaml(path: str) -> Set[str]:
    """Normalized string tokens from a list or an ``exclude`` / ``titles`` / ``ids`` / ``repos`` mapping."""
    if not os.path.isfile(path):
        return set()
    with open(path, encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)
    if raw is None:
        return set()
    if isinstance(raw, dict):
        items = (
            raw.get("exclude")
            or raw.get("titles")
            or raw.get("ids")
            or raw.get("repos")
            or []
        )
    elif isinstance(raw, list):
        items = raw
    else:
        return set()
    tokens: Set[str] = set()
    for item in items:
        if isinstance(item, str) and item.strip():
            tokens.add(_normalize(item))
        elif isinstance(item, dict):
            for key in ("id", "title", "key", "name", "repo"):
                value = item.get(key)
                if isinstance(value, str) and value.strip():
                    tokens.add(_normalize(value))
    return tokens


def load_exclude_tokens(project_root: str) -> Set[str]:
    """Return normalized title/key tokens from the local count-exclude list."""
    return _tokens_from_yaml(exclude_list_path(project_root))


def load_timeline_exclude_names(project_root: str) -> Set[str]:
    """Return normalized repo name / owner-name tokens omitted from the timeline."""
    return _tokens_from_yaml(timeline_exclude_list_path(project_root))


def entry_is_excluded(entry: Dict[str, Any], tokens: Iterable[str]) -> bool:
    """True when a BibTeX entry matches an exclude token by ID or title."""
    token_set = tokens if isinstance(tokens, set) else set(tokens)
    if not token_set:
        return False
    entry_id = str(
        entry.get("ID") or entry.get("id") or entry.get("citation_key") or ""
    ).strip()
    if entry_id and _normalize(entry_id) in token_set:
        return True
    title = entry.get("title")
    if title and _normalize(str(title)) in token_set:
        return True
    return False


def catalog_item_is_excluded(
    item: Dict[str, Any], tokens: Optional[Iterable[str]] = None
) -> bool:
    """True when a catalog item is marked nocount or matches exclude tokens."""
    if item.get("nocount"):
        return True
    flags = item.get("flags") or []
    if "nocount" in flags:
        return True
    if not tokens:
        return False
    token_set = tokens if isinstance(tokens, set) else set(tokens)
    item_id = str(item.get("id") or "").strip()
    if item_id and _normalize(item_id) in token_set:
        return True
    title = item.get("title")
    if title and _normalize(str(title)) in token_set:
        return True
    return False


def repo_is_excluded(repo: Dict[str, Any], tokens: Iterable[str]) -> bool:
    """True when a GitHub repo matches an exclude token by name or ``owner/name``."""
    token_set = tokens if isinstance(tokens, set) else set(tokens)
    if not token_set:
        return False
    name = _normalize(str(repo.get("name") or repo.get("title") or ""))
    full = _normalize(
        str(repo.get("repo") or repo.get("full_name") or repo.get("id") or "")
    )
    if name and name in token_set:
        return True
    if full and (full in token_set or full.split("/")[-1] in token_set):
        return True
    return False


def filter_timeline_repos(
    repos: Iterable[Dict[str, Any]], tokens: Iterable[str]
) -> List[Dict[str, Any]]:
    """Drop repos (or timeline marks) that match the timeline exclude list."""
    token_set = tokens if isinstance(tokens, set) else set(tokens)
    if not token_set:
        return list(repos)
    return [repo for repo in repos if not repo_is_excluded(repo, token_set)]
