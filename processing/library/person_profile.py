"""Resolve ORCID / public-profile links for people lists from on-disk data."""

from __future__ import annotations

import json
import os
import re
import unicodedata
from typing import Any, Dict, List, Optional, Tuple

import yaml

from processing.library.work_identity import normalize_orcid


def fold_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text or "")
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def normalize_token(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", fold_accents(text).lower())


def name_parts(name: str) -> Tuple[str, str]:
    """Return (last_key, first_initial) for loose matching."""
    tokens = [t for t in re.split(r"\s+", fold_accents(name or "").strip()) if t]
    if not tokens:
        return "", ""
    last = normalize_token(tokens[-1])
    first = tokens[0]
    letters = re.sub(r"[^A-Za-z]", "", first)
    initial = letters[0].lower() if letters else ""
    return last, initial


def profile_url(
    *,
    orcid: str = "",
    url: str = "",
    openalex: str = "",
    scholar: str = "",
) -> str:
    """Prefer ORCID, then an explicit homepage, then OpenAlex, then Scholar."""
    orcid = normalize_orcid(orcid)
    if orcid:
        return f"https://orcid.org/{orcid}"
    url = (url or "").strip()
    if url:
        return url
    openalex = (openalex or "").strip()
    if openalex:
        oid = openalex.rsplit("/", 1)[-1]
        if oid:
            return f"https://openalex.org/{oid}"
    scholar = (scholar or "").strip()
    if scholar:
        return f"https://scholar.google.com/citations?user={scholar}"
    return ""


def load_coauthor_urls(project_root: str) -> Dict[str, str]:
    """Map normalized full names → homepage URL from ``_data/coauthors.yml``."""
    path = os.path.join(project_root, "_data", "coauthors.yml")
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, encoding="utf-8") as handle:
            raw = yaml.safe_load(handle) or {}
    except (OSError, yaml.YAMLError):
        return {}
    if not isinstance(raw, dict):
        return {}

    mapping: Dict[str, str] = {}
    for last_name, entries in raw.items():
        if not isinstance(entries, list):
            continue
        last = str(last_name or "").strip()
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            url = str(entry.get("url") or "").strip()
            if not url:
                continue
            firstnames = entry.get("firstname") or []
            if not isinstance(firstnames, list):
                continue
            for first in firstnames:
                first_text = str(first or "").strip()
                if not first_text:
                    continue
                full = f"{first_text} {last}".strip()
                mapping[normalize_token(full)] = url
    return mapping


def load_citation_profiles(project_root: str) -> Dict[str, Dict[str, str]]:
    """Index citation-graph people by normalized name (and unique last+initial)."""
    path = os.path.join(project_root, "assets", "json", "citations.json")
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, encoding="utf-8") as handle:
            graph = json.load(handle)
    except (OSError, json.JSONDecodeError, TypeError):
        return {}

    by_full: Dict[str, Dict[str, str]] = {}
    by_initial: Dict[Tuple[str, str], List[Dict[str, str]]] = {}

    for person in graph.get("people") or []:
        if not isinstance(person, dict) or person.get("self"):
            continue
        name = str(person.get("name") or "").strip()
        if not name:
            continue
        profile = {
            "orcid": normalize_orcid(str(person.get("orcid") or "")),
            "openalex": str(person.get("openalex") or "").strip(),
            "scholar": str(person.get("scholar") or "").strip(),
        }
        if not any(profile.values()):
            continue
        key = normalize_token(name)
        # Prefer the row that already has an ORCID when names collide.
        existing = by_full.get(key)
        if not existing or (profile["orcid"] and not existing.get("orcid")):
            by_full[key] = profile
        last, initial = name_parts(name)
        if last and initial:
            by_initial.setdefault((last, initial), []).append(profile)

    # Promote unique last+initial buckets so "Kristina Gjerde" can find
    # "Kristina Maria Gjerde" when there is only one match.
    for key, profiles in by_initial.items():
        unique: List[Dict[str, str]] = []
        seen = set()
        for profile in profiles:
            stamp = (
                profile.get("orcid") or "",
                profile.get("openalex") or "",
                profile.get("scholar") or "",
            )
            if stamp in seen:
                continue
            seen.add(stamp)
            unique.append(profile)
        if len(unique) != 1:
            continue
        last, initial = key
        loose_key = f"{last}{initial}"
        if loose_key not in by_full:
            by_full[loose_key] = unique[0]

    return by_full


def lookup_profile(
    name: str,
    *,
    twenty_profiles: Optional[Dict[str, Dict[str, str]]] = None,
    citation_profiles: Optional[Dict[str, Dict[str, str]]] = None,
    coauthor_urls: Optional[Dict[str, str]] = None,
) -> Dict[str, str]:
    """Return ``{orcid?, url?, scholar?}`` for icon links.

    Priority: Twenty CRM export → citation ORCID/scholar → ``_data/coauthors.yml`` homepage.
    ``url`` is a personal/faculty website only (never OpenAlex/ORCID/Scholar pages).
    """
    from processing.library.twenty_people import normalize_scholar_id

    twenty_profiles = twenty_profiles or {}
    citation_profiles = citation_profiles or {}
    coauthor_urls = coauthor_urls or {}
    key = normalize_token(name)
    last, initial = name_parts(name)
    loose_key = f"{last}{initial}" if last and initial else ""

    def pick(index: Dict[str, Dict[str, str]]) -> Optional[Dict[str, str]]:
        return index.get(key) or (index.get(loose_key) if loose_key else None)

    twenty = pick(twenty_profiles)
    cited = pick(citation_profiles)
    homepage = ""
    if twenty and twenty.get("url"):
        homepage = twenty["url"]
    elif coauthor_urls.get(key):
        homepage = coauthor_urls[key]

    orcid = ""
    if twenty and twenty.get("orcid"):
        orcid = twenty["orcid"]
    elif cited and cited.get("orcid"):
        orcid = cited["orcid"]

    scholar = ""
    if twenty and twenty.get("scholar"):
        scholar = twenty["scholar"]
    elif cited and cited.get("scholar"):
        scholar = cited["scholar"]

    out: Dict[str, str] = {}
    if orcid:
        out["orcid"] = normalize_orcid(orcid) or orcid
    if homepage and "orcid.org" not in homepage.lower() and "scholar.google" not in homepage.lower():
        out["url"] = homepage
    scholar_id = normalize_scholar_id(scholar)
    if scholar_id:
        out["scholar"] = scholar_id
    return out


def attach_profile_fields(
    row: Dict[str, Any],
    name: str,
    *,
    twenty_profiles: Optional[Dict[str, Dict[str, str]]] = None,
    citation_profiles: Optional[Dict[str, Dict[str, str]]] = None,
    coauthor_urls: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Copy ORCID / website / Scholar onto a list row when known."""
    profile = lookup_profile(
        name,
        twenty_profiles=twenty_profiles,
        citation_profiles=citation_profiles,
        coauthor_urls=coauthor_urls,
    )
    if profile.get("orcid"):
        row["orcid"] = profile["orcid"]
    if profile.get("url"):
        row["url"] = profile["url"]
    if profile.get("scholar"):
        row["scholar"] = profile["scholar"]
    return row
