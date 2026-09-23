#!/usr/bin/env python3
"""Add Google Scholar citers to the OpenAlex citation graph.

Spends SerpApi searches (default cap 70) on the Scholar author profile and
cited-by pages. The Cite API is not used: it returns formatted bibliography
strings, not authors or edges.

Raw responses are cached in .cache/scholar/ (gitignored). A later run with the
same cache spends nothing.

Auth (never commit the key):
    export SERPAPI_API_KEY=...
    PYTHONPATH=. python processing/library/scholar_citations.py
"""

from __future__ import annotations

import argparse
import copy
import hashlib
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
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import yaml

from processing.library.citations import normalize_doi, write_artifacts
from processing.library.work_identity import normalize_orcid

SELF_SLUG = "glen-wright"
GLEN_AUTHOR_ID = "QHaIr0sAAAAJ"
SEARCH_URL = "https://serpapi.com/search.json"
ACCOUNT_URL = "https://serpapi.com/account.json"
MIN_TITLE = 20
PAGE_SIZE = 20
AUTHOR_PAGE_SIZE = 100
MAX_AUTHOR_PAGES = 2
USER_AGENT = "glenwright.earth-scholar/1.0"

DOI_RE = re.compile(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", re.I)
YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")
API_KEY_RE = re.compile(r"api_key=[^&\s\"']+")


class SerpError(RuntimeError):
    pass


def project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        out = {}
        for key, item in value.items():
            if key == "api_key":
                out[key] = "REDACTED"
            else:
                out[key] = redact(item)
        return out
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, str) and "api_key=" in value:
        return API_KEY_RE.sub("api_key=REDACTED", value)
    return value


def redact_text(text: str) -> str:
    return API_KEY_RE.sub("api_key=REDACTED", text or "")


def scrub_chars(text: str) -> str:
    return (
        (text or "")
        .replace("\u2010", "-")
        .replace("\u2011", "-")
        .replace("\u2012", "-")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u2212", "-")
    )


def name_tokens(name: str) -> List[str]:
    raw = scrub_chars(name).replace(".", " ")
    if "," in raw:
        last, rest = raw.split(",", 1)
        raw = f"{rest} {last}"
    parts = []
    for part in re.split(r"\s+", raw.strip()):
        cleaned = re.sub(r"[^A-Za-z0-9\-]", "", part)
        if cleaned:
            parts.append(cleaned)
    return parts


def norm_name(name: str) -> str:
    return " ".join(part.lower() for part in name_tokens(name))


def name_key(name: str) -> Optional[Tuple[str, str]]:
    parts = name_tokens(name)
    if len(parts) < 2:
        return None
    last = re.sub(r"[^a-z\-]", "", parts[-1].lower())
    initial = parts[0][0].lower()
    if not last or not initial.isalpha():
        return None
    return (last, initial)


def norm_title(title: str) -> str:
    text = scrub_chars(title).lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def extract_doi(*values: str) -> str:
    for value in values:
        if not value:
            continue
        match = DOI_RE.search(value)
        if match:
            return normalize_doi(match.group(0).rstrip("."))
    return ""


def extract_year(text: str = "", explicit: Any = None) -> Optional[int]:
    if explicit is not None and str(explicit).strip().isdigit():
        year = int(str(explicit).strip())
        if 1800 <= year <= 2100:
            return year
    if text:
        match = YEAR_RE.search(str(text))
        if match:
            return int(match.group(0))
    return None


def parse_int(value: Any) -> int:
    if value is None or isinstance(value, bool):
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    text = str(value).replace(",", "").strip()
    try:
        return int(text)
    except ValueError:
        return 0


def usable_name(name: str) -> bool:
    low = (name or "").strip().lower().rstrip(".")
    if not low or low in {"et al", "and others"}:
        return False
    if "…" in name or "..." in name:
        return False
    return True


def is_glen(name: str, author_id: str = "", glen_author_id: str = GLEN_AUTHOR_ID) -> bool:
    if author_id and author_id == glen_author_id:
        return True
    parts = norm_name(name).split()
    if len(parts) >= 2 and parts[-1] == "wright" and parts[0] == "glen":
        return True
    if norm_name(name) in {"g wright", "glen w wright"}:
        return True
    return False


def explode_authors(authors: Sequence[Dict[str, str]]) -> List[Dict[str, str]]:
    """Split Scholar fields that contain several people joined by ideographic commas."""
    out: List[Dict[str, str]] = []
    for author in authors:
        name = (author.get("name") or "").strip()
        orcid = author.get("orcid") or ""
        pieces = [part.strip() for part in re.split(r"\s*[，、；]\s*", name) if part.strip()]
        if len(pieces) <= 1:
            if name:
                row = {"name": name, "author_id": author.get("author_id") or ""}
                if orcid:
                    row["orcid"] = orcid
                out.append(row)
            continue
        for piece in pieces:
            if usable_name(piece):
                out.append({"name": piece, "author_id": ""})
    return out


def _anon_suffix(name: str) -> str:
    ascii_part = re.sub(r"[^a-z0-9]", "", norm_name(name))[:24]
    if ascii_part:
        return "n" + ascii_part
    identity = norm_name(name) or (name or "").strip().lower()
    return "n" + hashlib.sha1(identity.encode("utf-8")).hexdigest()[:10]


def scholar_person_id(name: str, author_id: str) -> str:
    base = "".join(ch.lower() if ch.isalnum() else "-" for ch in (name or "unknown"))
    base = "-".join(part for part in base.split("-") if part) or "unknown"
    suffix = re.sub(r"[^a-z0-9]", "", (author_id or "anon").lower()) or "anon"
    return f"{base}-gs-{suffix}"


def extract_authors(result: Dict[str, Any]) -> List[Dict[str, str]]:
    info = result.get("publication_info") or {}
    authors: List[Dict[str, str]] = []
    for author in info.get("authors") or []:
        name = (author.get("name") or "").strip()
        if not usable_name(name):
            continue
        authors.append({"name": name, "author_id": author.get("author_id") or ""})
    if authors:
        return explode_authors(authors)
    summary = info.get("summary") or ""
    head = summary.split(" - ")[0]
    for part in re.split(r"[,，、；]", head):
        name = part.strip()
        if usable_name(name) and not YEAR_RE.fullmatch(name):
            authors.append({"name": name, "author_id": ""})
    return explode_authors(authors)


def parse_author_articles(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    articles = payload.get("articles") or []
    rows: List[Dict[str, Any]] = []
    for article in articles:
        cited = article.get("cited_by") or {}
        if not isinstance(cited, dict):
            cited = {}
        rows.append(
            {
                "title": article.get("title") or "",
                "year": extract_year(article.get("publication") or "", article.get("year")),
                "cited_by": parse_int(cited.get("value") if cited.get("value") is not None else cited.get("total")),
                "cites_id": str(cited.get("cites_id") or ""),
                "link": article.get("link") or "",
                "citation_id": article.get("citation_id") or "",
            }
        )
    return rows


def wants_another_author_page(article_count: int, page_size: int = AUTHOR_PAGE_SIZE) -> bool:
    return article_count >= page_size


def parse_organic(result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    title = (result.get("title") or "").strip()
    if not title:
        return None
    result_id = (result.get("result_id") or "").strip()
    if not result_id:
        result_id = "t" + re.sub(r"[^a-z0-9]", "", norm_title(title))[:24]
    info = result.get("publication_info") or {}
    link = result.get("link") or ""
    return {
        "id": f"gs-{result_id}",
        "result_id": result_id,
        "title": title,
        "year": extract_year(info.get("summary") or "", None),
        "doi": extract_doi(link, title, info.get("summary") or ""),
        "link": link,
        "authors": extract_authors(result),
    }


def plan_first_pages(papers: Sequence[Dict[str, Any]], budget: int) -> List[Dict[str, Any]]:
    ranked = sorted(
        (
            paper
            for paper in papers
            if paper.get("cites_id") and parse_int(paper.get("cited_by")) > 0
        ),
        key=lambda paper: (-parse_int(paper.get("cited_by")), paper.get("title") or ""),
    )
    if budget <= 0:
        return []
    return list(ranked[:budget])


def plan_second_pages(papers: Sequence[Dict[str, Any]], budget: int) -> List[str]:
    """Second cited-by page when the count exceeds 20 and page 1 was full."""
    chosen: List[str] = []
    remaining = budget
    ordered = sorted(
        papers,
        key=lambda paper: (-parse_int(paper.get("cited_by")), paper.get("title") or ""),
    )
    for paper in ordered:
        if remaining <= 0:
            break
        if parse_int(paper.get("cited_by")) > PAGE_SIZE and parse_int(paper.get("page1_count")) >= PAGE_SIZE:
            cites_id = str(paper.get("cites_id") or "")
            if cites_id:
                chosen.append(cites_id)
                remaining -= 1
    return chosen


MAX_CITE_START = 980


def next_cited_by_page(
    paper: Dict[str, Any],
    fetched_counts: Dict[int, int],
    *,
    page_size: int = PAGE_SIZE,
    max_start: int = MAX_CITE_START,
) -> Optional[int]:
    """Next cited-by offset, or None when the paper is exhausted.

    A short page ends the paper. Offsets at or past max_start are not requested;
    Scholar stops returning results around 1000.
    """
    cited_by = parse_int(paper.get("cited_by"))
    start = 0
    while start < cited_by and start <= max_start:
        count = fetched_counts.get(start)
        if count is None:
            return start
        if count < page_size:
            return None
        start += page_size
    return None


def rank_next_pages(
    papers: Sequence[Dict[str, Any]],
    counts_by_id: Dict[str, Dict[int, int]],
) -> List[Tuple[int, int, str, str]]:
    """Next page per paper, deeper pages of highly cited work before one-citation papers.

    Each tuple is (start, negative cited_by, title, cites_id).
    """
    jobs: List[Tuple[int, int, str, str]] = []
    for paper in papers:
        cites_id = str(paper.get("cites_id") or "")
        if not cites_id:
            continue
        start = next_cited_by_page(paper, counts_by_id.get(cites_id) or {})
        if start is None:
            continue
        cited_by = parse_int(paper.get("cited_by"))
        # Finish real bibliographies before opening papers cited once.
        tail = 1 if cited_by <= 2 else 0
        jobs.append((tail, start, -cited_by, paper.get("title") or "", cites_id))
    jobs.sort()
    return [(start, cited_by, title, cites_id) for tail, start, cited_by, title, cites_id in jobs]


def _note_year(person: Dict[str, Any], year: Optional[int]) -> None:
    if not year:
        return
    year = int(year)
    first = person.get("firstYear")
    last = person.get("lastYear")
    person["firstYear"] = year if first is None else min(int(first), year)
    person["lastYear"] = year if last is None else max(int(last), year)


def merge_scholar(
    graph: Dict[str, Any],
    normalized: Dict[str, Any],
    *,
    max_people: int = 200,
    glen_author_id: str = GLEN_AUTHOR_ID,
) -> Dict[str, Any]:
    """Fold Scholar citing papers into a citation graph.

    New citers become spokes into Glen. co_cite edges join kept people who
    co-author a citing paper. co_cite does not change who is kept.
    """
    graph = copy.deepcopy(graph)
    people: Dict[str, Dict[str, Any]] = {person["id"]: person for person in graph.get("people") or []}
    if SELF_SLUG not in people:
        raise ValueError(f"citation graph is missing {SELF_SLUG}")

    works: Dict[str, Dict[str, Any]] = {work["id"]: work for work in graph.get("works") or []}
    original_work_ids = set(works)
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
    for edge in graph.get("edges") or []:
        if edge.get("direction") == "co_cite":
            continue
        key = (edge["source"], edge["target"], edge["direction"])
        edges[key] = edge

    name_buckets: Dict[Tuple[str, str], List[str]] = defaultdict(list)
    for person in people.values():
        if person.get("self"):
            continue
        key = name_key(person.get("name") or "")
        if key:
            name_buckets[key].append(person["id"])
    unique_names = {key: ids[0] for key, ids in name_buckets.items() if len(ids) == 1}

    by_scholar: Dict[str, str] = {}
    by_orcid: Dict[str, str] = {}
    anon_names: Dict[str, str] = {}
    for person in people.values():
        scholar_id = person.get("scholar") or ""
        if scholar_id:
            by_scholar[scholar_id] = person["id"]
        orcid = normalize_orcid(person.get("orcid") or "")
        if orcid:
            person["orcid"] = orcid
            by_orcid[orcid] = person["id"]
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
        if not usable_name(name) or is_glen(name, author_id, glen_author_id):
            return None
        if orcid and orcid in by_orcid:
            pid = by_orcid[orcid]
            if people[pid].get("self"):
                return None
            if author_id:
                claimed = people[pid].get("scholar") or ""
                if not claimed or claimed == author_id:
                    people[pid]["scholar"] = author_id
                    by_scholar[author_id] = pid
            return pid
        if author_id and author_id in by_scholar:
            pid = by_scholar[author_id]
            current = people[pid]
            if not current.get("openalex") and len(name) > len(current.get("name") or ""):
                current["name"] = name
            remember_orcid(pid, orcid)
            return pid
        key = name_key(name)
        folded = norm_name(name)
        if not author_id and folded:
            seen = anon_names.get(folded)
            if seen:
                remember_orcid(seen, orcid)
                return seen
        if key and key in unique_names:
            pid = unique_names[key]
            existing_orcid = people[pid].get("orcid") or ""
            if orcid and existing_orcid and existing_orcid != orcid:
                pass
            else:
                claimed = people[pid].get("scholar") or ""
                if author_id and claimed and claimed != author_id:
                    pass
                else:
                    if author_id:
                        people[pid]["scholar"] = author_id
                        by_scholar[author_id] = pid
                    else:
                        if folded:
                            anon_names[folded] = pid
                    remember_orcid(pid, orcid)
                    return pid
        suffix = author_id or _anon_suffix(name)
        pid = scholar_person_id(name, suffix)
        if pid in people and (people[pid].get("scholar") or "") not in {"", author_id}:
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
                people[pid]["scholar"] = author_id
            remember_orcid(pid, orcid)
        if author_id:
            by_scholar[author_id] = pid
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
            bucket = title_buckets.get(title) or []
            unique = list(dict.fromkeys(bucket))
            if len(title) >= MIN_TITLE and len(unique) == 1:
                wid = unique[0]
            else:
                wid = paper.get("id") or ""
                if not wid:
                    wid = "gs-" + re.sub(r"[^a-z0-9]", "", title)[:24]
                if wid not in works:
                    row: Dict[str, Any] = {
                        "id": wid,
                        "title": paper.get("title") or wid,
                    }
                    if paper.get("year"):
                        row["year"] = int(paper["year"])
                    if doi:
                        row["doi"] = doi
                    if paper.get("link"):
                        row["url"] = paper["link"]
                    works[wid] = row
                    if doi:
                        doi_index[doi] = wid
                    if len(title) >= MIN_TITLE:
                        title_buckets[title].append(wid)
        existing = works.get(wid)
        if existing is not None:
            if doi and not existing.get("doi"):
                existing["doi"] = doi
                doi_index.setdefault(doi, wid)
            if paper.get("link") and not existing.get("url") and not existing.get("path"):
                existing["url"] = paper["link"]
        return wid

    def add_cites(pid: str, wid: str, year: Optional[int]) -> None:
        key = (pid, SELF_SLUG, "cites_me")
        edge = edges.get(key)
        if edge is None:
            edge = {
                "source": pid,
                "target": SELF_SLUG,
                "count": 0,
                "works": [],
                "direction": "cites_me",
            }
            edges[key] = edge
        if wid in edge["works"]:
            return
        edge["works"].append(wid)
        edge["count"] = len(edge["works"])
        people[pid]["citedMe"] = int(people[pid].get("citedMe") or 0) + 1
        people[SELF_SLUG]["citedMe"] = int(people[SELF_SLUG].get("citedMe") or 0) + 1
        _note_year(people[pid], year)
        _note_year(people[SELF_SLUG], year)

    for paper in normalized.get("citing") or []:
        author_ids: List[str] = []
        for author in explode_authors(paper.get("authors") or []):
            pid = resolve_person(author)
            if pid and pid not in author_ids:
                author_ids.append(pid)
        if not author_ids:
            continue
        wid = resolve_work(paper)
        year = paper.get("year")
        for pid in author_ids:
            add_cites(pid, wid, int(year) if year else None)
        paper_authors[wid].extend(pid for pid in author_ids if pid not in paper_authors[wid])

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

    co_edges: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for wid, pids in paper_authors.items():
        pair_ids = sorted({pid for pid in pids if pid in kept_ids and pid != SELF_SLUG})
        for left, right in combinations(pair_ids, 2):
            key = (left, right)
            edge = co_edges.get(key)
            if edge is None:
                edge = {
                    "source": left,
                    "target": right,
                    "count": 0,
                    "works": [],
                    "direction": "co_cite",
                }
                co_edges[key] = edge
            if wid not in edge["works"]:
                edge["works"].append(wid)
                edge["count"] = len(edge["works"])

    edges_out = kept_edges + list(co_edges.values())
    edges_out.sort(key=lambda edge: (-int(edge["count"] or 0), edge["source"], edge["target"]))

    people_out = [people[SELF_SLUG], *kept]
    referenced = {wid for edge in edges_out for wid in edge.get("works") or []}
    works_out = [
        works[wid]
        for wid in works
        if wid in referenced or wid in original_work_ids
    ]
    works_out.sort(key=lambda row: (-(row.get("year") or 0), row.get("title") or ""))

    graph["people"] = people_out
    graph["edges"] = edges_out
    graph["works"] = works_out
    graph["source"] = "openalex+scholar"
    if normalized.get("fetched"):
        graph["scholarFetched"] = normalized["fetched"]
    if normalized.get("author_id"):
        graph["scholarAuthorId"] = normalized["author_id"]
    if normalized.get("searches") is not None:
        graph["scholarSearches"] = normalized["searches"]
    return graph


def load_scholar_userid(root: str) -> str:
    path = os.path.join(root, "_data", "socials.yml")
    with open(path, encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    author_id = (data.get("scholar_userid") or "").strip()
    if not author_id:
        raise SystemExit(f"Missing scholar_userid in {path}")
    return author_id


def load_max_people(root: str) -> int:
    path = os.path.join(root, "_data", "openalex.yml")
    if not os.path.isfile(path):
        return 200
    with open(path, encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return int(data.get("max_people") or 200)


def cache_dir(root: str) -> str:
    return os.path.join(root, ".cache", "scholar")


def _read_json(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def _write_json(path: str, payload: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def serp_get(params: Dict[str, Any], api_key: str, *, timeout: int = 90) -> Dict[str, Any]:
    query = dict(params)
    query["api_key"] = api_key
    url = SEARCH_URL + "?" + urllib.parse.urlencode(query)
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": USER_AGENT},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = redact_text(exc.read().decode("utf-8", errors="replace")[:500])
        raise SerpError(f"SerpApi HTTP {exc.code}: {body}") from None
    except urllib.error.URLError as exc:
        raise SerpError(f"SerpApi network error: {redact_text(str(exc.reason))}") from None
    if not isinstance(payload, dict):
        raise SerpError("SerpApi returned a non-object payload")
    if payload.get("error"):
        raise SerpError(f"SerpApi error: {payload['error']}")
    status = (payload.get("search_metadata") or {}).get("status")
    if status and status not in {"Success", "Cached"}:
        raise SerpError(f"SerpApi status {status}")
    return redact(payload)


def account_searches_left(api_key: str, *, timeout: int = 30) -> int:
    url = ACCOUNT_URL + "?" + urllib.parse.urlencode({"api_key": api_key})
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": USER_AGENT},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = redact_text(exc.read().decode("utf-8", errors="replace")[:500])
        raise SerpError(f"SerpApi account HTTP {exc.code}: {body}") from None
    except urllib.error.URLError as exc:
        raise SerpError(f"SerpApi account network error: {redact_text(str(exc.reason))}") from None
    if payload.get("error"):
        raise SerpError(f"SerpApi account error: {payload['error']}")
    return parse_int(payload.get("total_searches_left"))


def _describe(params: Dict[str, Any]) -> str:
    engine = params.get("engine") or ""
    if engine == "google_scholar_author":
        return f"author start={params.get('start', 0)} num={params.get('num')}"
    return f"cites={params.get('cites')} start={params.get('start', 0)} num={params.get('num')}"


class SearchBudget:
    def __init__(self, api_key: str, max_searches: int):
        self.api_key = api_key
        self.max_searches = max_searches
        self.spent = 0
        self._checked = False
        self.left: Optional[int] = None

    def allow(self) -> bool:
        if not self._checked:
            self.left = account_searches_left(self.api_key)
            self._checked = True
            print(f"SerpApi searches left this month: {self.left}", flush=True)
            if self.left < 1:
                print("No SerpApi searches left; using cache only.", flush=True)
                self.max_searches = 0
            elif self.left < self.max_searches:
                print(f"Capping this run at {self.left} searches.", flush=True)
                self.max_searches = self.left
        return self.spent < self.max_searches


def load_or_fetch(
    path: str,
    params: Dict[str, Any],
    *,
    budget: SearchBudget,
    refresh: bool,
    sleep_s: float,
) -> Optional[Dict[str, Any]]:
    if os.path.isfile(path) and not refresh:
        print(f"  cache {_describe(params)}", flush=True)
        return _read_json(path)
    if not budget.allow():
        print(f"  skip {_describe(params)} (budget reached)", flush=True)
        return None
    print(f"  search {budget.spent + 1}/{budget.max_searches} {_describe(params)}", flush=True)
    payload = serp_get(params, budget.api_key)
    budget.spent += 1
    _write_json(path, payload)
    if sleep_s:
        time.sleep(sleep_s)
    return payload


def _dedupe_articles(articles: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen: set = set()
    rows: List[Dict[str, Any]] = []
    for article in articles:
        key = article.get("cites_id") or article.get("citation_id") or norm_title(article.get("title") or "")
        if not key or key in seen:
            continue
        seen.add(key)
        rows.append(article)
    return rows


def collect_citing(pages: Iterable[Tuple[str, Dict[str, Any]]]) -> List[Dict[str, Any]]:
    by_id: Dict[str, Dict[str, Any]] = {}
    for cites_id, payload in pages:
        for organic in payload.get("organic_results") or []:
            row = parse_organic(organic)
            if not row:
                continue
            existing = by_id.get(row["result_id"])
            if existing is None:
                row["cites_ids"] = [cites_id] if cites_id else []
                by_id[row["result_id"]] = row
                continue
            if cites_id and cites_id not in existing["cites_ids"]:
                existing["cites_ids"].append(cites_id)
            if len(row["authors"]) > len(existing["authors"]):
                existing["authors"] = row["authors"]
            if row.get("doi") and not existing.get("doi"):
                existing["doi"] = row["doi"]
            if row.get("year") and not existing.get("year"):
                existing["year"] = row["year"]
    citing = list(by_id.values())
    citing.sort(key=lambda row: (-(row.get("year") or 0), row.get("title") or ""))
    return citing


def fetch_normalized(
    root: str,
    *,
    api_key: str,
    max_searches: int,
    refresh: bool,
    sleep_s: float = 0.3,
) -> Dict[str, Any]:
    author_id = load_scholar_userid(root)
    raw = os.path.join(cache_dir(root), "raw")
    os.makedirs(raw, exist_ok=True)
    budget = SearchBudget(api_key, max_searches)

    articles: List[Dict[str, Any]] = []
    for page in range(MAX_AUTHOR_PAGES):
        start = page * AUTHOR_PAGE_SIZE
        path = os.path.join(raw, f"author-start-{start}.json")
        payload = load_or_fetch(
            path,
            {
                "engine": "google_scholar_author",
                "author_id": author_id,
                "num": AUTHOR_PAGE_SIZE,
                "start": start,
                "sort": "pubdate",
                "hl": "en",
            },
            budget=budget,
            refresh=refresh,
            sleep_s=sleep_s,
        )
        if payload is None:
            break
        batch = parse_author_articles(payload)
        articles.extend(batch)
        print(f"  author page start={start}: {len(batch)} articles", flush=True)
        if not wants_another_author_page(len(batch)):
            break
    articles = _dedupe_articles(articles)
    cited = [article for article in articles if article.get("cites_id") and article.get("cited_by", 0) > 0]
    print(
        f"Profile articles: {len(articles)} ({len(cited)} with citation ids)",
        flush=True,
    )

    pages: List[Tuple[str, Dict[str, Any]]] = []
    counts: Dict[str, Dict[int, int]] = defaultdict(dict)

    def absorb(cites_id: str, start: int, payload: Dict[str, Any]) -> int:
        organic = payload.get("organic_results") or []
        counts[cites_id][start] = len(organic)
        pages.append((cites_id, payload))
        return len(organic)

    for paper in cited:
        cites_id = str(paper["cites_id"])
        start = 0
        while start <= MAX_CITE_START and start < parse_int(paper.get("cited_by")):
            path = os.path.join(raw, f"cites-{_safe(cites_id)}-start-{start}.json")
            if not os.path.isfile(path):
                break
            payload = _read_json(path)
            found = absorb(cites_id, start, payload)
            if found < PAGE_SIZE:
                break
            start += PAGE_SIZE

    skipped = 0
    pagination_checked = False
    while True:
        jobs = rank_next_pages(cited, counts)
        if not jobs:
            break
        start, _neg_cited, title, cites_id = jobs[0]
        path = os.path.join(raw, f"cites-{_safe(cites_id)}-start-{start}.json")
        if _over_budget(path, budget, refresh):
            skipped = len(jobs)
            break
        try:
            payload = load_or_fetch(
                path,
                {
                    "engine": "google_scholar",
                    "cites": cites_id,
                    "num": PAGE_SIZE,
                    "start": start,
                    "hl": "en",
                },
                budget=budget,
                refresh=refresh,
                sleep_s=sleep_s,
            )
        except SerpError as exc:
            message = str(exc)
            print(f"  stop {cites_id} start={start}: {message}", flush=True)
            counts[cites_id][start] = 0
            if "searches" in message.lower() or "run out" in message.lower():
                skipped = len(jobs)
                break
            continue
        if payload is None:
            skipped = len(jobs)
            break
        found = absorb(cites_id, start, payload)
        if start > 0 and found:
            prev_path = os.path.join(raw, f"cites-{_safe(cites_id)}-start-{start - PAGE_SIZE}.json")
            if os.path.isfile(prev_path):
                prev_ids = _result_ids(_read_json(prev_path))
                new_ids = _result_ids(payload)
                overlap = len(prev_ids & new_ids) / max(len(new_ids), 1)
                if overlap >= 0.8:
                    counts[cites_id][start] = min(found, PAGE_SIZE - 1)
                    print(
                        f"  page repeats ({overlap:.0%}) · {title[:70]}",
                        flush=True,
                    )
                    if not pagination_checked and "," not in cites_id:
                        print("  cited-by pagination is repeating; stopping deeper pages.", flush=True)
                        skipped = len(rank_next_pages(cited, counts))
                        break
                elif "," not in cites_id:
                    pagination_checked = True
        if found and counts[cites_id][start] >= PAGE_SIZE:
            print(f"    {found} citing papers · {title[:70]}", flush=True)
    if skipped:
        print(f"  {skipped} cited-by pages left unfetched (budget reached)", flush=True)

    citing = collect_citing(pages)
    print(
        f"Citing papers: {len(citing)} from {len(pages)} pages; searches spent: {budget.spent}",
        flush=True,
    )
    return {
        "v": 1,
        "author_id": author_id,
        "fetched": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "searches": budget.spent,
        "papers": articles,
        "citing": citing,
    }


def _safe(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "_", value)[:80]


def _result_ids(payload: Dict[str, Any]) -> set:
    return {
        result.get("result_id")
        for result in payload.get("organic_results") or []
        if result.get("result_id")
    }


def _over_budget(path: str, budget: SearchBudget, refresh: bool) -> bool:
    if os.path.isfile(path) and not refresh:
        return False
    return budget._checked and budget.spent >= budget.max_searches


def dry_run_plan(root: str, max_searches: int) -> int:
    raw = os.path.join(cache_dir(root), "raw")
    author_path = os.path.join(raw, "author-start-0.json")
    print(f"Dry run. Cap {max_searches} searches. Cite API is not called.", flush=True)
    if not os.path.isfile(author_path):
        print("No author cache yet. The first live run spends 1 search on the author profile,", flush=True)
        print("then one cited-by search per paper with citations, highest counts first,", flush=True)
        print("and a second page only when cited_by > 20 and the first page is full.", flush=True)
        return 0
    articles = _dedupe_articles(parse_author_articles(_read_json(author_path)))
    second = os.path.join(raw, "author-start-100.json")
    if os.path.isfile(second):
        articles = _dedupe_articles(articles + parse_author_articles(_read_json(second)))
    first = plan_first_pages(articles, max_searches)
    print(f"Cached profile articles: {len(articles)}. First pages that fit in {max_searches}: {len(first)}.", flush=True)
    for paper in first[:15]:
        print(f"  cites={paper['cites_id']} cited_by={paper['cited_by']} {paper['title'][:80]}", flush=True)
    if len(first) > 15:
        print(f"  … {len(first) - 15} more", flush=True)
    return 0


def strip_scholar_layer(graph: Dict[str, Any]) -> Dict[str, Any]:
    """Drop Scholar-added works and people so a merge can be reapplied cleanly."""
    graph = copy.deepcopy(graph)
    people = {person["id"]: person for person in graph.get("people") or []}
    edges: List[Dict[str, Any]] = []
    for edge in graph.get("edges") or []:
        if edge.get("direction") == "co_cite":
            continue
        works = [work for work in edge.get("works") or [] if not str(work).startswith("gs-")]
        if not works:
            continue
        row = dict(edge)
        row["works"] = works
        row["count"] = len(works)
        edges.append(row)
    kept = {SELF_SLUG}
    for edge in edges:
        kept.add(edge["source"])
        kept.add(edge["target"])
    people = {
        pid: person
        for pid, person in people.items()
        if pid in kept and (person.get("self") or person.get("openalex") or "-gs-" not in pid)
    }
    edges = [edge for edge in edges if edge["source"] in people and edge["target"] in people]
    for person in people.values():
        person["citedMe"] = 0
        person["citedByMe"] = 0
    for edge in edges:
        count = int(edge["count"] or 0)
        if edge["direction"] == "cites_me":
            people[edge["source"]]["citedMe"] += count
            if edge["target"] in people:
                people[edge["target"]]["citedMe"] += count
        elif edge["direction"] == "i_cite":
            people[edge["source"]]["citedByMe"] += count
            if edge["target"] in people:
                people[edge["target"]]["citedByMe"] += count
    graph["people"] = list(people.values())
    graph["edges"] = edges
    return graph


def merge_cache(root: str, normalized: Dict[str, Any]) -> Tuple[str, str]:
    graph_path = os.path.join(root, "assets", "json", "citations.json")
    with open(graph_path, encoding="utf-8") as handle:
        graph = strip_scholar_layer(json.load(handle))
    before_people = len(graph.get("people") or [])
    before_edges = len(graph.get("edges") or [])
    merged = merge_scholar(graph, normalized, max_people=load_max_people(root))
    graph_path, list_path = write_artifacts(root, merged)
    directions: Dict[str, int] = defaultdict(int)
    for edge in merged["edges"]:
        directions[edge["direction"]] += 1
    print(
        f"People {before_people} → {len(merged['people'])}, "
        f"edges {before_edges} → {len(merged['edges'])} "
        f"({dict(directions)})",
        flush=True,
    )
    print(f"  {graph_path}", flush=True)
    print(f"  {list_path}", flush=True)
    return graph_path, list_path


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Merge Google Scholar citers into citations.json")
    parser.add_argument("--max-searches", type=int, default=70)
    parser.add_argument("--refresh", action="store_true", help="Ignore the local cache and spend searches again")
    parser.add_argument("--dry-run", action="store_true", help="Print the search plan and do not spend credits or merge")
    parser.add_argument("--merge-only", action="store_true", help="Merge .cache/scholar/normalized.json and do not call SerpApi")
    parser.add_argument("--root", type=str, default=None)
    parser.add_argument("--sleep", type=float, default=0.3)
    parser.add_argument(
        "--api-key",
        type=str,
        default=os.environ.get("SERPAPI_API_KEY") or os.environ.get("SERPAPI_KEY") or "",
    )
    args = parser.parse_args(argv)
    root = args.root or project_root()
    normalized_path = os.path.join(cache_dir(root), "normalized.json")

    if args.dry_run:
        return dry_run_plan(root, args.max_searches)

    if args.merge_only:
        if not os.path.isfile(normalized_path):
            raise SystemExit(f"No cache at {normalized_path}")
        merge_cache(root, _read_json(normalized_path))
        return 0

    if not args.api_key:
        raise SystemExit("Set SERPAPI_API_KEY. The key is not read from the repo.")

    normalized = fetch_normalized(
        root,
        api_key=args.api_key,
        max_searches=args.max_searches,
        refresh=args.refresh,
        sleep_s=args.sleep,
    )
    _write_json(normalized_path, normalized)
    print(f"Wrote {normalized_path}", flush=True)
    if not normalized.get("citing"):
        print("No citing papers collected; citations.json left unchanged.", flush=True)
        return 1
    merge_cache(root, normalized)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
