"""User-defined library items excluded from filter counts.

Items still appear in the unfiltered catalogue and text search; they are omitted
from type/role/language chip counts and from those facet result lists on
/library/. The list lives at ``_data/library_exclude_from_counts.yml``
(gitignored). Each entry may be a BibTeX key or a title (case-insensitive).
"""

from __future__ import annotations

import os
import re
from typing import Any, Dict, Iterable, Optional, Set

import yaml

EXCLUDE_FILENAME = "library_exclude_from_counts.yml"


def exclude_list_path(project_root: str) -> str:
    return os.path.join(project_root, "_data", EXCLUDE_FILENAME)


def _normalize(value: str) -> str:
    text = re.sub(r"[{}]", "", str(value or ""))
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text


def load_exclude_tokens(project_root: str) -> Set[str]:
    """Return normalized title/key tokens from the local exclude list."""
    path = exclude_list_path(project_root)
    if not os.path.isfile(path):
        return set()
    with open(path, encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)
    if raw is None:
        return set()
    if isinstance(raw, dict):
        items = raw.get("exclude") or raw.get("titles") or raw.get("ids") or []
    elif isinstance(raw, list):
        items = raw
    else:
        return set()
    tokens: Set[str] = set()
    for item in items:
        if isinstance(item, str) and item.strip():
            tokens.add(_normalize(item))
        elif isinstance(item, dict):
            for key in ("id", "title", "key"):
                value = item.get(key)
                if isinstance(value, str) and value.strip():
                    tokens.add(_normalize(value))
    return tokens


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
