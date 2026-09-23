"""Collapse duplicate citation-graph works and recompute edge counts.

DOI identity wins. Otherwise two works merge when their titles are almost the
same and their years do not conflict. Two different DOIs never merge.
"""

from __future__ import annotations

import copy
import html
import re
import unicodedata
from collections import defaultdict
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional

TITLE_MERGE = 0.92
MIN_TITLE = 20
ORCID_RE = re.compile(r"\d{4}-\d{4}-\d{4}-\d{3}[\dX]", re.I)


def normalize_orcid(value: str) -> str:
    match = ORCID_RE.search(value or "")
    return match.group(0).upper() if match else ""


def normalize_doi(value: str) -> str:
    text = (value or "").strip().lower()
    for prefix in ("https://doi.org/", "http://doi.org/", "https://dx.doi.org/", "http://dx.doi.org/", "doi:"):
        if text.startswith(prefix):
            text = text[len(prefix) :]
    text = text.strip().rstrip(".").rstrip("/")
    text = re.sub(r"/(?:full|abstract|pdf|epdf|meta|summary)$", "", text)
    text = re.sub(r"\.pdf$", "", text)
    return text


def normalize_title(title: str) -> str:
    text = html.unescape(title or "")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower()
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = " ".join(text.split())
    return re.sub(r"^(the|a|an)\s+", "", text)


def title_similarity(a: str, b: str) -> float:
    left, right = normalize_title(a), normalize_title(b)
    if not left or not right:
        return 0.0
    if left == right:
        return 1.0
    return SequenceMatcher(None, left, right).ratio()


def _year(work: Dict[str, Any]) -> Optional[int]:
    year = work.get("year")
    if year is None or year == "":
        return None
    try:
        return int(year)
    except (TypeError, ValueError):
        return None


def _work_rank(work_id: str) -> tuple:
    """Lower sorts first. OpenAlex work ids outrank Scholar and S2 stubs."""
    if re.fullmatch(r"W\d+", work_id or ""):
        return (0, work_id)
    if (work_id or "").startswith(("gs-", "s2-")):
        return (2, work_id)
    return (1, work_id)


def prefer_work_id(left: str, right: str) -> str:
    return left if _work_rank(left) <= _work_rank(right) else right


def _years_compatible(left: Optional[int], right: Optional[int]) -> bool:
    if left is None or right is None:
        return True
    return left == right


def _block_key(title: str) -> str:
    width = max(18, int(len(title) * 0.08))
    return title[:width]


class _UnionFind:
    def __init__(self, ids: List[str]):
        self.parent = {work_id: work_id for work_id in ids}

    def find(self, work_id: str) -> str:
        parent = self.parent
        while parent[work_id] != work_id:
            parent[work_id] = parent[parent[work_id]]
            work_id = parent[work_id]
        return work_id

    def union(self, left: str, right: str) -> None:
        left_root, right_root = self.find(left), self.find(right)
        if left_root == right_root:
            return
        keep = prefer_work_id(left_root, right_root)
        drop = right_root if keep == left_root else left_root
        self.parent[drop] = keep


def _merge_record(canonical: Dict[str, Any], other: Dict[str, Any]) -> None:
    if not canonical.get("doi") and other.get("doi"):
        canonical["doi"] = other["doi"]
    if not canonical.get("year") and other.get("year"):
        canonical["year"] = other["year"]
    if not canonical.get("path") and other.get("path"):
        canonical["path"] = other["path"]
    if not canonical.get("url") and other.get("url") and not canonical.get("path"):
        canonical["url"] = other["url"]
    if len(other.get("title") or "") > len(canonical.get("title") or ""):
        canonical["title"] = other["title"]


def recompute_counts(graph: Dict[str, Any]) -> None:
    people = {person["id"]: person for person in graph.get("people") or []}
    for person in people.values():
        person["citedMe"] = 0
        person["citedByMe"] = 0
    for edge in graph.get("edges") or []:
        count = int(edge.get("count") or 0)
        source = people.get(edge.get("source") or "")
        target = people.get(edge.get("target") or "")
        if edge.get("direction") == "cites_me":
            if source:
                source["citedMe"] += count
            if target:
                target["citedMe"] += count
        elif edge.get("direction") == "i_cite":
            if source:
                source["citedByMe"] += count
            if target:
                target["citedByMe"] += count


def dedupe_graph(graph: Dict[str, Any]) -> Dict[str, Any]:
    """Return a copy with duplicate works collapsed and edge work lists rewritten."""
    graph = copy.deepcopy(graph)
    works = {work["id"]: work for work in graph.get("works") or [] if work.get("id")}
    if len(works) < 2:
        recompute_counts(graph)
        return graph

    ids = list(works)
    uf = _UnionFind(ids)
    dois = {work_id: normalize_doi(works[work_id].get("doi") or "") for work_id in ids}
    years = {work_id: _year(works[work_id]) for work_id in ids}
    titles = {work_id: normalize_title(works[work_id].get("title") or "") for work_id in ids}

    by_doi: Dict[str, List[str]] = defaultdict(list)
    for work_id, doi in dois.items():
        if doi:
            by_doi[doi].append(work_id)
    for members in by_doi.values():
        head = members[0]
        for other in members[1:]:
            uf.union(head, other)

    blocks: Dict[str, List[str]] = defaultdict(list)
    for work_id, title in titles.items():
        if len(title) >= MIN_TITLE:
            blocks[_block_key(title)].append(work_id)

    for members in blocks.values():
        for index, left in enumerate(members):
            for right in members[index + 1 :]:
                if uf.find(left) == uf.find(right):
                    continue
                left_doi, right_doi = dois[left], dois[right]
                if left_doi and right_doi and left_doi != right_doi:
                    continue
                if not _years_compatible(years[left], years[right]):
                    continue
                left_title, right_title = titles[left], titles[right]
                if left_title == right_title or title_similarity(left_title, right_title) >= TITLE_MERGE:
                    uf.union(left, right)

    clusters: Dict[str, List[str]] = defaultdict(list)
    for work_id in ids:
        clusters[uf.find(work_id)].append(work_id)

    id_map: Dict[str, str] = {}
    merged: Dict[str, Dict[str, Any]] = {}
    for members in clusters.values():
        canonical = members[0]
        for member in members[1:]:
            canonical = prefer_work_id(canonical, member)
        record = dict(works[canonical])
        record["id"] = canonical
        for member in members:
            id_map[member] = canonical
            if member != canonical:
                _merge_record(record, works[member])
        merged[canonical] = record

    edges: List[Dict[str, Any]] = []
    for edge in graph.get("edges") or []:
        seen: List[str] = []
        for work_id in edge.get("works") or []:
            mapped = id_map.get(work_id, work_id)
            if mapped not in seen:
                seen.append(mapped)
        if not seen:
            continue
        row = dict(edge)
        row["works"] = seen
        row["count"] = len(seen)
        edges.append(row)

    referenced = {work_id for edge in edges for work_id in edge["works"]}
    kept = [
        record
        for record in merged.values()
        if record["id"] in referenced or record.get("path")
    ]
    kept.sort(key=lambda row: (-(row.get("year") or 0), row.get("title") or ""))
    edges.sort(
        key=lambda row: (
            -int(row.get("count") or 0),
            row.get("source") or "",
            row.get("target") or "",
        )
    )

    graph["works"] = kept
    graph["edges"] = edges
    recompute_counts(graph)
    return graph
