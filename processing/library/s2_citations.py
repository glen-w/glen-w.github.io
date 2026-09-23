#!/usr/bin/env python3
"""Add Semantic Scholar citation and reference edges to the citation graph.

Seeds are the library DOIs. Citing authors become cites_me edges into Glen.
Authors of papers those seeds reference become i_cite edges out of Glen.
Raw pages are cached under .cache/s2/ so a later run spends nothing.

Auth (optional, never commit the key):
    export SEMANTIC_SCHOLAR_API_KEY=...
    PYTHONPATH=. python processing/library/citations.py
"""

from __future__ import annotations

import copy
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from itertools import combinations
from typing import Any, Dict, List, Optional, Tuple

from processing.library.citations import SELF_SLUG, library_dois, normalize_doi
from processing.library.scholar_citations import is_glen, name_key, norm_name, norm_title, usable_name
from processing.library.work_identity import MIN_TITLE, normalize_orcid, recompute_counts

API = "https://api.semanticscholar.org/graph/v1"
FIELDS = "paperId,title,year,url,externalIds,authors"
USER_AGENT = "glenwright.earth-citations/1.0"
PAGE_SIZE = 100
MAX_OFFSET = 1000


def project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def cache_dir(root: str) -> str:
    return os.path.join(root, ".cache", "s2")


def _safe_doi(doi: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "_", doi)[:120]


def _read_json(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def _write_json(path: str, payload: Any) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def s2_person_id(name: str, author_id: str) -> str:
    base = "".join(ch.lower() if ch.isalnum() else "-" for ch in (name or "unknown"))
    base = "-".join(part for part in base.split("-") if part) or "unknown"
    suffix = re.sub(r"[^a-z0-9]", "", (author_id or "anon").lower()) or "anon"
    return f"{base}-s2-{suffix}"


def paper_from_s2(row: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Normalise a Graph API paper, or a citations/references wrapper."""
    paper = row.get("citingPaper") or row.get("citedPaper") or row
    if not isinstance(paper, dict):
        return None
    paper_id = str(paper.get("paperId") or paper.get("paper_id") or "").strip()
    title = (paper.get("title") or "").strip()
    preset = str(paper.get("id") or "").strip()
    work_id = preset or (f"s2-{paper_id}" if paper_id else "")
    if not work_id or work_id == "s2-":
        return None
    external = paper.get("externalIds") or {}
    doi = normalize_doi(external.get("DOI") or paper.get("doi") or "")
    authors: List[Dict[str, str]] = []
    for author in paper.get("authors") or []:
        if not isinstance(author, dict):
            continue
        name = (author.get("name") or "").strip()
        if not usable_name(name):
            continue
        author_external = author.get("externalIds") or {}
        authors.append(
            {
                "name": name,
                "author_id": str(author.get("authorId") or author.get("author_id") or ""),
                "orcid": normalize_orcid(author_external.get("ORCID") or author.get("orcid") or ""),
            }
        )
    out: Dict[str, Any] = {"id": work_id, "title": title or work_id, "authors": authors}
    year = paper.get("year")
    try:
        if year:
            out["year"] = int(year)
    except (TypeError, ValueError):
        pass
    if doi:
        out["doi"] = doi
    url = paper.get("url") or ""
    if url:
        out["url"] = url
    return out


class S2Client:
    def __init__(self, api_key: str = "", *, sleep_s: float = 1.1):
        self.api_key = api_key
        self.sleep_s = sleep_s
        self._last = 0.0

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        query = urllib.parse.urlencode(params or {})
        url = f"{API}{path}"
        if query:
            url = f"{url}?{query}"
        elapsed = time.monotonic() - self._last
        if elapsed < self.sleep_s:
            time.sleep(self.sleep_s - elapsed)
        headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
        if self.api_key:
            headers["x-api-key"] = self.api_key
        req = urllib.request.Request(url, headers=headers)
        for attempt in range(6):
            try:
                with urllib.request.urlopen(req, timeout=90) as resp:
                    self._last = time.monotonic()
                    return json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                self._last = time.monotonic()
                if exc.code == 404:
                    return None
                if exc.code == 400:
                    detail = exc.read().decode("utf-8", "replace")[:180].strip()
                    print(f"  Semantic Scholar 400 for {path}: {detail}", flush=True)
                    return None
                if exc.code in (429, 500, 502, 503, 504) and attempt < 5:
                    retry_after = exc.headers.get("Retry-After") if exc.headers else None
                    try:
                        wait = float(retry_after) if retry_after else min(2.0 * (attempt + 1), 30.0)
                    except ValueError:
                        wait = min(2.0 * (attempt + 1), 30.0)
                    print(f"  Semantic Scholar {exc.code}; sleeping {wait:.0f}s…", flush=True)
                    time.sleep(wait)
                    continue
                print(f"  Semantic Scholar {exc.code} for {path}", flush=True)
                return None
            except urllib.error.URLError as exc:
                if attempt < 5:
                    time.sleep(2.0 * (attempt + 1))
                    continue
                print(f"  Semantic Scholar unreachable ({exc})", flush=True)
                return None
        return None


def _page_path(root: str, doi: str, kind: str, offset: int) -> str:
    return os.path.join(cache_dir(root), "pages", _safe_doi(doi), f"{kind}-{offset}.json")


def _cached_pages(root: str, doi: str, kind: str) -> List[Dict[str, Any]]:
    folder = os.path.join(cache_dir(root), "pages", _safe_doi(doi))
    if not os.path.isdir(folder):
        return []
    rows: List[Tuple[int, Dict[str, Any]]] = []
    prefix = f"{kind}-"
    for name in os.listdir(folder):
        if not name.startswith(prefix) or not name.endswith(".json"):
            continue
        offset_text = name[len(prefix) : -len(".json")]
        if not offset_text.isdigit():
            continue
        rows.append((int(offset_text), _read_json(os.path.join(folder, name))))
    rows.sort(key=lambda item: item[0])
    papers: List[Dict[str, Any]] = []
    for _offset, payload in rows:
        for row in payload.get("data") or []:
            paper = paper_from_s2(row)
            if paper:
                papers.append(paper)
    return papers


def fetch_direction(
    client: S2Client,
    root: str,
    doi: str,
    kind: str,
    *,
    refresh: bool,
) -> List[Dict[str, Any]]:
    """kind is 'citations' or 'references'."""
    if not refresh and os.path.isfile(_page_path(root, doi, kind, 0)):
        return _cached_pages(root, doi, kind)

    paper_key = urllib.parse.quote(f"DOI:{doi}", safe="")
    nested = "citingPaper" if kind == "citations" else "citedPaper"
    papers: List[Dict[str, Any]] = []
    offset = 0
    while offset <= MAX_OFFSET:
        payload = client.get(
            f"/paper/{paper_key}/{kind}",
            {"fields": FIELDS, "limit": PAGE_SIZE, "offset": offset},
        )
        if payload is None:
            if offset == 0:
                return []
            break
        _write_json(_page_path(root, doi, kind, offset), payload)
        data = payload.get("data") or []
        for row in data:
            paper = paper_from_s2(row if isinstance(row, dict) else {nested: row})
            if paper:
                papers.append(paper)
        if len(data) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return papers


def _doi_index(graph: Dict[str, Any]) -> Dict[str, str]:
    index: Dict[str, str] = {}
    for work in graph.get("works") or []:
        doi = normalize_doi(work.get("doi") or "")
        if doi:
            index.setdefault(doi, work["id"])
    return index


def fetch_normalized(
    root: str,
    graph: Dict[str, Any],
    *,
    api_key: str,
    refresh: bool,
    sleep_s: float,
) -> Dict[str, Any]:
    normalized_path = os.path.join(cache_dir(root), "normalized.json")
    dois = library_dois(root)
    cached: Dict[str, Any] = {}
    if os.path.isfile(normalized_path) and not refresh:
        cached = _read_json(normalized_path)
    have = set(cached.get("dois") or [])
    missing = [doi for doi in dois if doi not in have]
    if cached and not missing and not refresh:
        print(f"Semantic Scholar cache hit ({len(have)} DOIs)", flush=True)
        return cached

    by_doi = _doi_index(graph)
    client = S2Client(api_key, sleep_s=sleep_s if not api_key else min(sleep_s, 0.4))
    citing_by_id: Dict[str, Dict[str, Any]] = {}
    for paper in cached.get("citing") or []:
        if paper.get("id"):
            citing_by_id[paper["id"]] = paper
    references: List[Dict[str, Any]] = list(cached.get("references") or [])
    seen_refs = {
        (row.get("seed_work_id"), (row.get("paper") or {}).get("id"))
        for row in references
    }

    for index, doi in enumerate(missing, start=1):
        print(f"  S2 [{index}/{len(missing)}] {doi}", flush=True)
        seed_id = by_doi.get(doi) or ""
        for paper in fetch_direction(client, root, doi, "citations", refresh=refresh):
            citing_by_id.setdefault(paper["id"], paper)
        if not seed_id:
            continue
        for paper in fetch_direction(client, root, doi, "references", refresh=refresh):
            key = (seed_id, paper["id"])
            if key in seen_refs:
                continue
            seen_refs.add(key)
            references.append({"seed_work_id": seed_id, "paper": paper})

    payload = {
        "v": 1,
        "fetched": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "dois": sorted(set(dois) | have),
        "citing": list(citing_by_id.values()),
        "references": references,
    }
    _write_json(normalized_path, payload)
    print(
        f"Semantic Scholar: {len(payload['citing'])} citing, {len(references)} reference rows",
        flush=True,
    )
    return payload


def merge_s2(
    graph: Dict[str, Any],
    normalized: Dict[str, Any],
    *,
    max_people: int = 200,
) -> Dict[str, Any]:
    """Fold Semantic Scholar papers into a citation graph. Keeps existing co_cite edges."""
    graph = copy.deepcopy(graph)
    people: Dict[str, Dict[str, Any]] = {person["id"]: person for person in graph.get("people") or []}
    if SELF_SLUG not in people:
        raise ValueError(f"citation graph is missing {SELF_SLUG}")

    works: Dict[str, Dict[str, Any]] = {work["id"]: work for work in graph.get("works") or []}
    original_ids = set(works)
    doi_index: Dict[str, str] = {}
    title_buckets: Dict[str, List[str]] = defaultdict(list)
    for work in works.values():
        doi = normalize_doi(work.get("doi") or "")
        if doi:
            doi_index.setdefault(doi, work["id"])
        title = norm_title(work.get("title") or "")
        if len(title) >= MIN_TITLE:
            title_buckets[title].append(work["id"])

    edges: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
    co_edges: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for edge in graph.get("edges") or []:
        if edge.get("direction") == "co_cite":
            pair = tuple(sorted((edge["source"], edge["target"])))
            co_edges[pair] = edge
            continue
        edges[(edge["source"], edge["target"], edge["direction"])] = edge

    by_s2: Dict[str, str] = {}
    by_orcid: Dict[str, str] = {}
    name_buckets: Dict[Tuple[str, str], List[str]] = defaultdict(list)
    for person in people.values():
        if person.get("s2"):
            by_s2[person["s2"]] = person["id"]
        orcid = normalize_orcid(person.get("orcid") or "")
        if orcid:
            person["orcid"] = orcid
            by_orcid[orcid] = person["id"]
        if person.get("self"):
            continue
        key = name_key(person.get("name") or "")
        if key:
            name_buckets[key].append(person["id"])
    unique_names = {key: ids[0] for key, ids in name_buckets.items() if len(ids) == 1}
    anon_names: Dict[str, str] = {}
    paper_authors: Dict[str, List[str]] = defaultdict(list)

    def remember_orcid(pid: str, orcid: str) -> None:
        if not orcid:
            return
        current = people[pid].get("orcid") or ""
        if current and current != orcid:
            return
        people[pid]["orcid"] = orcid
        by_orcid[orcid] = pid

    def resolve_person(author: Dict[str, str]) -> Optional[str]:
        name = (author.get("name") or "").strip()
        author_id = author.get("author_id") or ""
        orcid = normalize_orcid(author.get("orcid") or "")
        if not usable_name(name) or is_glen(name, author_id):
            return None
        if orcid and orcid in by_orcid:
            pid = by_orcid[orcid]
            if people[pid].get("self"):
                return None
            if author_id and not people[pid].get("s2"):
                people[pid]["s2"] = author_id
                by_s2[author_id] = pid
            return pid
        if author_id and author_id in by_s2:
            remember_orcid(by_s2[author_id], orcid)
            return by_s2[author_id]
        key = name_key(name)
        folded = norm_name(name)
        if not author_id and folded and folded in anon_names:
            remember_orcid(anon_names[folded], orcid)
            return anon_names[folded]
        if key and key in unique_names:
            pid = unique_names[key]
            existing = people[pid].get("orcid") or ""
            claimed = people[pid].get("s2") or ""
            conflict = (orcid and existing and existing != orcid) or (
                author_id and claimed and claimed != author_id
            )
            if not conflict:
                if author_id:
                    people[pid]["s2"] = author_id
                    by_s2[author_id] = pid
                elif folded:
                    anon_names[folded] = pid
                remember_orcid(pid, orcid)
                return pid
        suffix = author_id or re.sub(r"[^a-z0-9]", "", folded)[:24] or "anon"
        pid = s2_person_id(name, suffix)
        if pid in people and (people[pid].get("s2") or "") not in {"", author_id}:
            pid = f"{pid}-2"
        if pid not in people:
            people[pid] = {
                "id": pid,
                "name": name,
                "self": False,
                "citedMe": 0,
                "citedByMe": 0,
            }
            if author_id:
                people[pid]["s2"] = author_id
        if author_id:
            by_s2[author_id] = pid
        elif folded:
            anon_names[folded] = pid
        remember_orcid(pid, orcid)
        return pid

    def resolve_work(paper: Dict[str, Any]) -> str:
        doi = normalize_doi(paper.get("doi") or "")
        if doi and doi in doi_index:
            wid = doi_index[doi]
        else:
            title = norm_title(paper.get("title") or "")
            bucket = list(dict.fromkeys(title_buckets.get(title) or []))
            if len(title) >= MIN_TITLE and len(bucket) == 1:
                wid = bucket[0]
            else:
                wid = paper.get("id") or ""
                if wid not in works:
                    row: Dict[str, Any] = {"id": wid, "title": paper.get("title") or wid}
                    if paper.get("year"):
                        row["year"] = int(paper["year"])
                    if doi:
                        row["doi"] = doi
                    if paper.get("url"):
                        row["url"] = paper["url"]
                    works[wid] = row
                    if doi:
                        doi_index.setdefault(doi, wid)
                    if len(title) >= MIN_TITLE:
                        title_buckets[title].append(wid)
        existing = works.get(wid)
        if existing is not None:
            if doi and not existing.get("doi"):
                existing["doi"] = doi
                doi_index.setdefault(doi, wid)
            if paper.get("url") and not existing.get("url") and not existing.get("path"):
                existing["url"] = paper["url"]
        return wid

    def add_edge(source: str, target: str, work_id: str, direction: str) -> None:
        if not source or not target or source == target or not work_id:
            return
        key = (source, target, direction)
        edge = edges.get(key)
        if edge is None:
            edge = {
                "source": source,
                "target": target,
                "count": 0,
                "works": [],
                "direction": direction,
            }
            edges[key] = edge
        if work_id not in edge["works"]:
            edge["works"].append(work_id)
            edge["count"] = len(edge["works"])

    for paper in normalized.get("citing") or []:
        author_ids: List[str] = []
        for author in paper.get("authors") or []:
            pid = resolve_person(author)
            if pid and pid not in author_ids:
                author_ids.append(pid)
        if not author_ids:
            continue
        wid = resolve_work(paper)
        for pid in author_ids:
            add_edge(pid, SELF_SLUG, wid, "cites_me")
        for pid in author_ids:
            if pid not in paper_authors[wid]:
                paper_authors[wid].append(pid)

    for row in normalized.get("references") or []:
        seed_id = row.get("seed_work_id") or ""
        paper = row.get("paper") or {}
        if not seed_id or seed_id not in works:
            continue
        for author in paper.get("authors") or []:
            pid = resolve_person(author)
            if pid:
                add_edge(SELF_SLUG, pid, seed_id, "i_cite")

    recompute_counts({"people": list(people.values()), "edges": list(edges.values())})

    def score(person: Dict[str, Any]) -> int:
        return int(person.get("citedMe") or 0) + int(person.get("citedByMe") or 0)

    others = [person for person in people.values() if not person.get("self") and score(person) >= 1]
    others.sort(key=lambda person: (-score(person), -int(person.get("citedMe") or 0), person["name"].lower()))
    kept = others[: max(max_people, 0)]
    kept_ids = {SELF_SLUG} | {person["id"] for person in kept}

    kept_edges = [
        edge
        for edge in edges.values()
        if edge["source"] in kept_ids and edge["target"] in kept_ids
    ]
    co_out: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for edge in co_edges.values():
        if edge["source"] in kept_ids and edge["target"] in kept_ids:
            pair = tuple(sorted((edge["source"], edge["target"])))
            co_out[pair] = edge
    for wid, pids in paper_authors.items():
        pair_ids = sorted({pid for pid in pids if pid in kept_ids and pid != SELF_SLUG})
        for left, right in combinations(pair_ids, 2):
            pair = (left, right)
            edge = co_out.get(pair)
            if edge is None:
                edge = {
                    "source": left,
                    "target": right,
                    "count": 0,
                    "works": [],
                    "direction": "co_cite",
                }
                co_out[pair] = edge
            if wid not in edge["works"]:
                edge["works"].append(wid)
                edge["count"] = len(edge["works"])

    edges_out = kept_edges + list(co_out.values())
    edges_out.sort(key=lambda edge: (-int(edge["count"] or 0), edge["source"], edge["target"]))
    referenced = {wid for edge in edges_out for wid in edge.get("works") or []}
    works_out = [
        works[wid]
        for wid in works
        if wid in referenced or wid in original_ids or works[wid].get("path")
    ]
    works_out.sort(key=lambda row: (-(row.get("year") or 0), row.get("title") or ""))

    graph["people"] = [people[SELF_SLUG], *kept]
    graph["edges"] = edges_out
    graph["works"] = works_out
    source = graph.get("source") or "openalex"
    if "s2" not in source.split("+"):
        graph["source"] = source + "+s2"
    if normalized.get("fetched"):
        graph["s2Fetched"] = normalized["fetched"]
    recompute_counts(graph)
    return graph


def apply_s2(
    graph: Dict[str, Any],
    root: str,
    *,
    api_key: str = "",
    refresh: bool = False,
    sleep_s: float = 1.1,
    max_people: int = 200,
) -> Dict[str, Any]:
    normalized = fetch_normalized(
        root,
        graph,
        api_key=api_key,
        refresh=refresh,
        sleep_s=sleep_s,
    )
    if not normalized.get("citing") and not normalized.get("references"):
        print("Semantic Scholar returned no papers; graph unchanged.", flush=True)
        return graph
    return merge_s2(graph, normalized, max_people=max_people)
