"""Build a co-author collaboration graph from library BibTeX entries."""

from __future__ import annotations

import json
import os
import re
import unicodedata
from collections import defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml

from processing.library.bib_parser import BibParser

SELF_LAST = "Wright"
SELF_FIRST_PREFIXES = ("Glen", "G.")
CLIQUE_AUTHOR_LIMIT = 8
MIN_LIST_COLLABORATIONS = 2


def is_self_author(person: Dict[str, str]) -> bool:
    """True when this author record is Glen Wright (including G. Wright)."""
    last = re.sub(r"[*∗†‡§¶‖&^]", "", (person.get("last") or "").strip())
    if last != SELF_LAST:
        return False
    first = (person.get("first") or "").strip()
    return any(
        first == prefix or first.startswith(prefix + " ")
        for prefix in SELF_FIRST_PREFIXES
    )


def fold_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text or "")
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def normalize_token(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", fold_accents(text).lower())


def first_initial(first: str) -> str:
    letters = re.sub(r"[^A-Za-z]", "", first or "")
    return letters[0].lower() if letters else ""


def is_initial_only(first: str) -> bool:
    return bool(re.match(r"^[A-Za-z]\.?$", (first or "").strip()))


def display_name(person: Dict[str, str]) -> str:
    first = (person.get("first") or "").strip()
    last = (person.get("last") or "").strip()
    full = f"{first} {last}".strip()
    return full or (person.get("full") or "").strip() or "Unknown"


def person_slug(name: str) -> str:
    folded = fold_accents(name).lower()
    slug = re.sub(r"[^a-z0-9]+", "-", folded).strip("-")
    return slug or "unknown"


def load_aliases(project_root: str) -> Dict[str, str]:
    """Map normalized variant display names → canonical display name."""
    path = os.path.join(project_root, "_data", "coauthor_aliases.yml")
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, encoding="utf-8") as handle:
            raw = yaml.safe_load(handle) or []
    except (OSError, yaml.YAMLError):
        return {}

    mapping: Dict[str, str] = {}
    if not isinstance(raw, list):
        return mapping
    for row in raw:
        if not isinstance(row, dict):
            continue
        canonical = str(row.get("name") or "").strip()
        if not canonical:
            continue
        mapping[normalize_token(canonical)] = canonical
        aliases = row.get("aliases") or []
        if not isinstance(aliases, list):
            continue
        for alias in aliases:
            text = str(alias or "").strip()
            if text:
                mapping[normalize_token(text)] = canonical
    return mapping


class PersonRegistry:
    """Resolve author name variants to stable person records."""

    def __init__(self, aliases: Optional[Dict[str, str]] = None):
        self.aliases = aliases or {}
        self._people: Dict[str, Dict[str, Any]] = {}
        self._by_last_initial: Dict[Tuple[str, str], List[str]] = defaultdict(list)
        self._by_last_first: Dict[Tuple[str, str], str] = {}
        self._unmatched_initials: Dict[Tuple[str, str], str] = {}
        self._redirects: Dict[str, str] = {}

    def resolve(self, author: Dict[str, str]) -> str:
        if is_self_author(author):
            return self._ensure_self(author)

        name = display_name(author)
        alias_key = normalize_token(name)
        if alias_key in self.aliases:
            return self._ensure_named(self.aliases[alias_key], self_flag=False)

        last_key = normalize_token(author.get("last") or "")
        first = (author.get("first") or "").strip()
        if not last_key:
            return self._ensure_named(name, self_flag=False)

        if is_initial_only(first):
            return self._resolve_initial(author, last_key, first_initial(first))

        first_key = normalize_token(first)
        key = (last_key, first_key)
        if key in self._by_last_first:
            person_id = self._canonical(self._by_last_first[key])
            self._prefer_display(person_id, name)
            return person_id

        person_id = self._ensure_named(name, self_flag=False)
        self._by_last_first[key] = person_id
        initial = first_initial(first)
        if initial:
            bucket = (last_key, initial)
            if person_id not in self._by_last_initial[bucket]:
                self._by_last_initial[bucket].append(person_id)
            pending = self._unmatched_initials.pop(bucket, None)
            if pending:
                self._merge_into(self._canonical(pending), person_id)
        return person_id

    def _canonical(self, person_id: str) -> str:
        seen: Set[str] = set()
        while person_id in self._redirects and person_id not in seen:
            seen.add(person_id)
            person_id = self._redirects[person_id]
        return person_id

    def _resolve_initial(self, author: Dict[str, str], last_key: str, initial: str) -> str:
        if not initial:
            return self._ensure_named(display_name(author), self_flag=False)

        bucket = (last_key, initial)
        matches = [
            self._canonical(person_id)
            for person_id in (self._by_last_initial.get(bucket) or [])
        ]
        # Deduplicate after redirects
        unique: List[str] = []
        seen: Set[str] = set()
        for person_id in matches:
            if person_id not in seen and person_id in self._people:
                seen.add(person_id)
                unique.append(person_id)

        if len(unique) == 1:
            return unique[0]
        if len(unique) > 1:
            # Ambiguous: keep a distinct initial-only person.
            return self._ensure_named(display_name(author), self_flag=False)

        if bucket in self._unmatched_initials:
            return self._canonical(self._unmatched_initials[bucket])

        person_id = self._ensure_named(display_name(author), self_flag=False)
        self._unmatched_initials[bucket] = person_id
        return person_id

    def _ensure_self(self, author: Dict[str, str]) -> str:
        person_id = "glen-wright"
        if person_id not in self._people:
            self._people[person_id] = {
                "id": person_id,
                "name": "Glen Wright",
                "self": True,
            }
            last_key = normalize_token(SELF_LAST)
            self._by_last_first[(last_key, normalize_token("Glen"))] = person_id
            self._by_last_initial[(last_key, "g")].append(person_id)
        elif not is_initial_only(author.get("first") or ""):
            self._prefer_display(person_id, display_name(author))
        return person_id

    def _ensure_named(self, name: str, *, self_flag: bool) -> str:
        person_id = person_slug(name)
        base = person_id
        suffix = 2
        while person_id in self._people:
            existing = self._people[person_id]["name"]
            if normalize_token(existing) == normalize_token(name):
                self._prefer_display(person_id, name)
                return person_id
            person_id = f"{base}-{suffix}"
            suffix += 1
        self._people[person_id] = {
            "id": person_id,
            "name": name,
            "self": self_flag,
        }
        return person_id

    def _prefer_display(self, person_id: str, name: str) -> None:
        current = self._people[person_id]["name"]
        first_word = name.split()[0] if name.split() else ""
        if len(name) > len(current) and not is_initial_only(first_word):
            self._people[person_id]["name"] = name

    def _merge_into(self, source_id: str, target_id: str) -> None:
        source_id = self._canonical(source_id)
        target_id = self._canonical(target_id)
        if source_id == target_id or source_id not in self._people:
            return
        source = self._people.pop(source_id)
        self._redirects[source_id] = target_id
        self._prefer_display(target_id, source["name"])
        for key, value in list(self._by_last_first.items()):
            if self._canonical(value) == source_id or value == source_id:
                self._by_last_first[key] = target_id
        for key, ids in list(self._by_last_initial.items()):
            remapped = []
            seen: Set[str] = set()
            for item in ids:
                canonical = target_id if item == source_id else self._canonical(item)
                if canonical not in seen:
                    seen.add(canonical)
                    remapped.append(canonical)
            self._by_last_initial[key] = remapped

    def people(self) -> Dict[str, Dict[str, Any]]:
        return self._people


def build_coauthor_graph(
    entries: List[Dict[str, Any]],
    catalog_items: List[Dict[str, Any]],
    *,
    project_root: Optional[str] = None,
    bib_parser: Optional[BibParser] = None,
) -> Dict[str, Any]:
    """Return ``{v, people, edges, works}`` for the collaboration graph."""
    parser = bib_parser or BibParser()
    aliases = load_aliases(project_root) if project_root else {}
    registry = PersonRegistry(aliases)
    by_id = {str(item.get("id") or ""): item for item in catalog_items}

    # Pass 1: register every author name so initials can merge before edges exist.
    prepared: List[Tuple[str, str, str, List[Dict[str, str]], int]] = []
    for entry in entries:
        entry_id = str(entry.get("ID") or "").strip()
        if not entry_id:
            continue
        authors = parser.format_authors(entry)
        if len(authors) < 2:
            continue
        item = by_id.get(entry_id) or {}
        year = int(item.get("year") or 0)
        if not year:
            try:
                year = int(str(parser.extract_year(entry))[:4])
            except (TypeError, ValueError):
                year = 0
        title = item.get("title") or parser.clean_title(entry.get("title", "Untitled"))
        info = item.get("info") or ""
        for author in authors:
            registry.resolve(author)
        prepared.append((entry_id, title, info, authors, year))

    # Pass 2: resolve again (now fully merged) and build works / edges.
    works: Dict[str, Dict[str, Any]] = {}
    edge_works: Dict[Tuple[str, str], List[str]] = defaultdict(list)
    person_works: Dict[str, List[str]] = defaultdict(list)
    person_years: Dict[str, List[int]] = defaultdict(list)

    for entry_id, title, info, authors, year in prepared:
        person_ids: List[str] = []
        seen_in_work: Set[str] = set()
        for author in authors:
            person_id = registry.resolve(author)
            if person_id in seen_in_work:
                continue
            seen_in_work.add(person_id)
            person_ids.append(person_id)

        if "glen-wright" not in person_ids or len(person_ids) < 2:
            continue

        works[entry_id] = {
            "id": entry_id,
            "title": title,
            "year": year,
            "path": info,
        }

        for person_id in person_ids:
            if entry_id not in person_works[person_id]:
                person_works[person_id].append(entry_id)
            if year:
                person_years[person_id].append(year)

        if len(person_ids) <= CLIQUE_AUTHOR_LIMIT:
            pairs = [
                (person_ids[i], person_ids[j])
                for i in range(len(person_ids))
                for j in range(i + 1, len(person_ids))
            ]
        else:
            pairs = [
                ("glen-wright", other)
                for other in person_ids
                if other != "glen-wright"
            ]

        for left, right in pairs:
            key = tuple(sorted((left, right)))
            if entry_id not in edge_works[key]:
                edge_works[key].append(entry_id)

    people_out: List[Dict[str, Any]] = []
    for person_id, person in registry.people().items():
        work_ids = person_works.get(person_id) or []
        if not work_ids:
            continue
        years = person_years.get(person_id) or []
        row: Dict[str, Any] = {
            "id": person_id,
            "name": person["name"],
            "self": bool(person.get("self")),
            "count": len(work_ids),
        }
        if years:
            row["firstYear"] = min(years)
            row["lastYear"] = max(years)
        people_out.append(row)

    people_out.sort(
        key=lambda row: (not row.get("self"), -row["count"], row["name"].lower())
    )

    edges_out: List[Dict[str, Any]] = []
    for (source, target), work_ids in sorted(edge_works.items()):
        edges_out.append(
            {
                "source": source,
                "target": target,
                "count": len(work_ids),
                "works": work_ids,
            }
        )
    edges_out.sort(key=lambda row: (-row["count"], row["source"], row["target"]))

    works_out = sorted(
        works.values(), key=lambda row: (-int(row.get("year") or 0), row["title"])
    )

    return {
        "v": 1,
        "people": people_out,
        "edges": edges_out,
        "works": works_out,
    }


def enrich_people_profiles(graph: Dict[str, Any], project_root: str) -> None:
    """Attach ORCID / website URLs onto co-author people from on-disk sources."""
    from processing.library.person_profile import (
        attach_profile_fields,
        load_citation_profiles,
        load_coauthor_urls,
    )
    from processing.library.twenty_people import load_people_profiles

    twenty_profiles = load_people_profiles(project_root)
    citation_profiles = load_citation_profiles(project_root)
    coauthor_urls = load_coauthor_urls(project_root)
    if not twenty_profiles and not citation_profiles and not coauthor_urls:
        return

    for person in graph.get("people") or []:
        if not isinstance(person, dict) or person.get("self"):
            continue
        # Drop OpenAlex/Scholar stand-ins so only website icons remain.
        person.pop("url", None)
        attach_profile_fields(
            person,
            str(person.get("name") or ""),
            twenty_profiles=twenty_profiles,
            citation_profiles=citation_profiles,
            coauthor_urls=coauthor_urls,
        )


def collaborators_list(
    graph: Dict[str, Any],
    *,
    min_count: int = MIN_LIST_COLLABORATIONS,
    project_root: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Frequent collaborators for the noscript YAML list (excludes self)."""
    from processing.library.person_profile import (
        attach_profile_fields,
        load_citation_profiles,
        load_coauthor_urls,
    )
    from processing.library.twenty_people import load_people_profiles

    twenty_profiles = load_people_profiles(project_root) if project_root else {}
    citation_profiles = load_citation_profiles(project_root) if project_root else {}
    coauthor_urls = load_coauthor_urls(project_root) if project_root else {}

    rows = []
    for person in graph.get("people") or []:
        if person.get("self"):
            continue
        count = int(person.get("count") or 0)
        if count < min_count:
            continue
        row: Dict[str, Any] = {"name": person["name"], "count": count}
        if person.get("orcid"):
            row["orcid"] = person["orcid"]
        if person.get("url"):
            row["url"] = person["url"]
        if person.get("scholar"):
            row["scholar"] = person["scholar"]
        if "orcid" not in row or "url" not in row or "scholar" not in row:
            attach_profile_fields(
                row,
                person["name"],
                twenty_profiles=twenty_profiles,
                citation_profiles=citation_profiles,
                coauthor_urls=coauthor_urls,
            )
        rows.append(row)
    rows.sort(key=lambda row: (-row["count"], row["name"].lower()))
    return rows


def write_coauthor_artifacts(
    project_root: str,
    graph: Dict[str, Any],
) -> Tuple[str, str]:
    """Write ``coauthors.json`` and ``collaborators.yml``; return their paths."""
    enrich_people_profiles(graph, project_root)

    json_dir = os.path.join(project_root, "assets", "json")
    data_dir = os.path.join(project_root, "_data")
    os.makedirs(json_dir, exist_ok=True)
    os.makedirs(data_dir, exist_ok=True)

    graph_path = os.path.join(json_dir, "coauthors.json")
    with open(graph_path, "w", encoding="utf-8") as handle:
        json.dump(graph, handle, ensure_ascii=False, indent=2, sort_keys=False)
        handle.write("\n")

    list_path = os.path.join(data_dir, "collaborators.yml")
    rows = collaborators_list(graph, project_root=project_root)
    with open(list_path, "w", encoding="utf-8") as handle:
        yaml.dump(rows, handle, default_flow_style=False, allow_unicode=True, sort_keys=False)

    return graph_path, list_path
