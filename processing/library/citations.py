#!/usr/bin/env python3
"""Build an author citation network from OpenAlex (incoming + outgoing).

Seeded by DOIs in assets/json/library.json by default. Writes:

  - assets/json/citations.json
  - _data/citers.yml  (people who cite Glen at least twice)

Auth (recommended — do not commit keys):
  export OPENALEX_API_KEY=...
  export SEMANTIC_SCHOLAR_API_KEY=...   # optional
  PYTHONPATH=. python processing/library/citations.py

After OpenAlex, the run re-merges .cache/scholar/normalized.json (no SerpApi
calls) and adds Semantic Scholar edges for the library DOIs.

Usage:
  PYTHONPATH=. python processing/library/citations.py
  PYTHONPATH=. python processing/library/citations.py --seed author
  PYTHONPATH=. python processing/library/citations.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

import yaml

from processing.library.work_identity import dedupe_graph, normalize_orcid
from processing.library.work_identity import normalize_doi as _normalize_doi

API = "https://api.openalex.org"
SELF_SLUG = "glen-wright"
USER_AGENT = "glenwright.earth-citations/1.0 (mailto:{mailto})"

SELECT_WORK = (
    "id,doi,title,display_name,publication_year,cited_by_count,"
    "referenced_works,authorships"
)


def project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_config(root: str) -> Dict[str, Any]:
    path = os.path.join(root, "_data", "openalex.yml")
    with open(path, encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not data.get("author_id"):
        raise SystemExit(f"Missing author_id in {path}")
    if not data.get("mailto"):
        raise SystemExit(f"Missing mailto in {path}")
    data.setdefault("min_links", 1)
    data.setdefault("max_people", 200)
    data.setdefault("seed", "library")
    return data


def normalize_doi(value: str) -> str:
    return _normalize_doi(value)


def short_id(openalex_url: str) -> str:
    return (openalex_url or "").rstrip("/").split("/")[-1]


def library_dois(root: str) -> List[str]:
    catalog_path = os.path.join(root, "assets", "json", "library.json")
    if not os.path.isfile(catalog_path):
        return []
    with open(catalog_path, encoding="utf-8") as handle:
        catalog = json.load(handle)
    dois: List[str] = []
    seen: Set[str] = set()
    for item in catalog.get("items") or []:
        doi = normalize_doi(item.get("doi") or "")
        if doi and doi not in seen:
            seen.add(doi)
            dois.append(doi)
    return dois


def load_library_doi_paths(root: str) -> Dict[str, str]:
    catalog_path = os.path.join(root, "assets", "json", "library.json")
    if not os.path.isfile(catalog_path):
        return {}
    with open(catalog_path, encoding="utf-8") as handle:
        catalog = json.load(handle)
    mapping: Dict[str, str] = {}
    for item in catalog.get("items") or []:
        doi = normalize_doi(item.get("doi") or "")
        path = item.get("info") or ""
        if doi and path:
            mapping[doi] = path
    return mapping


def person_slug(name: str, openalex_id: str) -> str:
    base = "".join(ch.lower() if ch.isalnum() else "-" for ch in (name or "unknown"))
    base = "-".join(part for part in base.split("-") if part) or "unknown"
    return f"{base}-{short_id(openalex_id).lower()}"


class OpenAlexClient:
    def __init__(
        self,
        mailto: str,
        *,
        api_key: Optional[str] = None,
        sleep_s: float = 0.15,
    ):
        self.mailto = mailto
        self.api_key = api_key
        self.sleep_s = sleep_s
        self._last = 0.0

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        query = dict(params or {})
        query["mailto"] = self.mailto
        url = f"{API}{path}?{urllib.parse.urlencode(query, doseq=True)}"
        elapsed = time.monotonic() - self._last
        if elapsed < self.sleep_s:
            time.sleep(self.sleep_s - elapsed)
        headers = {
            "User-Agent": USER_AGENT.format(mailto=self.mailto),
            "Accept": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        req = urllib.request.Request(url, headers=headers)
        for attempt in range(8):
            try:
                with urllib.request.urlopen(req, timeout=90) as resp:
                    self._last = time.monotonic()
                    return json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                if exc.code in (429, 500, 502, 503, 504) and attempt < 7:
                    retry_after = exc.headers.get("Retry-After") if exc.headers else None
                    try:
                        wait = float(retry_after) if retry_after else (2.0 * (attempt + 1))
                    except ValueError:
                        wait = 2.0 * (attempt + 1)
                    wait = min(max(wait, 1.0), 60.0)
                    print(f"  OpenAlex {exc.code}; sleeping {wait:.1f}s…", flush=True)
                    time.sleep(wait)
                    continue
                raise
            except urllib.error.URLError:
                if attempt < 7:
                    time.sleep(2.0 * (attempt + 1))
                    continue
                raise
        raise RuntimeError(f"Failed GET {path}")

    def paginate(
        self, path: str, params: Optional[Dict[str, Any]] = None, *, per_page: int = 200
    ) -> Iterable[Dict[str, Any]]:
        page = 1
        query = dict(params or {})
        query["per_page"] = per_page
        while True:
            query["page"] = page
            payload = self.get(path, query)
            results = payload.get("results") or []
            for row in results:
                yield row
            meta = payload.get("meta") or {}
            count = int(meta.get("count") or 0)
            if page * per_page >= count or not results:
                break
            page += 1


def authorship_people(work: Dict[str, Any]) -> List[Tuple[str, str, str]]:
    """OpenAlex authors as (id, display name, bare ORCID)."""
    people: List[Tuple[str, str, str]] = []
    seen: Set[str] = set()
    for authorship in work.get("authorships") or []:
        author = authorship.get("author") or {}
        aid = short_id(author.get("id") or "")
        name = (author.get("display_name") or authorship.get("raw_author_name") or "").strip()
        orcid = normalize_orcid(author.get("orcid") or "")
        if not aid or not name or aid in seen:
            continue
        seen.add(aid)
        people.append((aid, name, orcid))
    return people


def work_record(work: Dict[str, Any], doi_paths: Dict[str, str]) -> Dict[str, Any]:
    wid = short_id(work.get("id") or "")
    doi = normalize_doi(work.get("doi") or "")
    row: Dict[str, Any] = {
        "id": wid,
        "title": work.get("display_name") or work.get("title") or wid,
        "year": int(work.get("publication_year") or 0) or None,
    }
    if doi:
        row["doi"] = doi
        if doi in doi_paths:
            row["path"] = doi_paths[doi]
    return row


def fetch_works_by_dois(client: OpenAlexClient, dois: List[str]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    seen: Set[str] = set()
    chunk = 20
    for i in range(0, len(dois), chunk):
        batch = dois[i : i + chunk]
        if not batch:
            continue
        print(f"  doi batch {i // chunk + 1}/{(len(dois) + chunk - 1) // chunk}", flush=True)
        payload = client.get(
            "/works",
            {
                "filter": "doi:" + "|".join(batch),
                "per_page": max(len(batch), 1),
                "select": SELECT_WORK,
            },
        )
        for work in payload.get("results") or []:
            wid = short_id(work.get("id") or "")
            if wid and wid not in seen:
                seen.add(wid)
                out.append(work)
    return out


def fetch_own_works_by_author(client: OpenAlexClient, author_id: str) -> List[Dict[str, Any]]:
    return list(
        client.paginate(
            "/works",
            {
                "filter": f"author.id:{author_id}",
                "select": SELECT_WORK,
                "sort": "publication_year:desc",
            },
        )
    )


def fetch_works_by_ids(client: OpenAlexClient, work_ids: List[str]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    chunk = 50
    total = len(work_ids)
    for i in range(0, total, chunk):
        batch = work_ids[i : i + chunk]
        if not batch:
            continue
        print(f"  refs batch {i // chunk + 1}/{(total + chunk - 1) // chunk}", flush=True)
        payload = client.get(
            "/works",
            {
                "filter": "openalex:" + "|".join(batch),
                "per_page": len(batch),
                "select": SELECT_WORK,
            },
        )
        out.extend(payload.get("results") or [])
    return out


def build_citation_graph(
    *,
    root: str,
    config: Dict[str, Any],
    client: OpenAlexClient,
    dry_run: bool = False,
    seed: str = "library",
) -> Dict[str, Any]:
    author_id = short_id(str(config["author_id"]))
    doi_paths = load_library_doi_paths(root)
    min_links = int(config.get("min_links") or 1)
    max_people = int(config.get("max_people") or 200)

    if seed == "library":
        dois = library_dois(root)
        print(f"Resolving {len(dois)} library DOIs…", flush=True)
        own_works = [] if dry_run else fetch_works_by_dois(client, dois)
        print(f"  {len(own_works)} OpenAlex works matched", flush=True)
    else:
        print(f"Fetching works for {author_id}…", flush=True)
        own_works = [] if dry_run else fetch_own_works_by_author(client, author_id)
        print(f"  {len(own_works)} works", flush=True)

    if not own_works and not dry_run:
        raise SystemExit("No seed works found — check DOIs / author_id / API key.")

    works_out: Dict[str, Dict[str, Any]] = {}
    for work in own_works:
        rec = work_record(work, doi_paths)
        works_out[rec["id"]] = rec

    self_orcid = normalize_orcid(str(config.get("orcid") or ""))
    people: Dict[str, Dict[str, Any]] = {
        SELF_SLUG: {
            "id": SELF_SLUG,
            "name": "Glen Wright",
            "self": True,
            "openalex": author_id,
            "citedMe": 0,
            "citedByMe": 0,
            "years": [],
        }
    }
    if self_orcid:
        people[SELF_SLUG]["orcid"] = self_orcid
    edges: Dict[Tuple[str, str], Dict[str, Any]] = {}

    def ensure_person(oa_id: str, name: str, orcid: str = "") -> str:
        if oa_id == author_id:
            return SELF_SLUG
        slug = person_slug(name, oa_id)
        if slug not in people:
            people[slug] = {
                "id": slug,
                "name": name,
                "self": False,
                "openalex": oa_id,
                "citedMe": 0,
                "citedByMe": 0,
                "years": [],
            }
        if orcid and not people[slug].get("orcid"):
            people[slug]["orcid"] = orcid
        return slug

    def add_edge(source: str, target: str, work_id: str, year: Optional[int], direction: str) -> None:
        if source == target:
            return
        key = (source, target)
        row = edges.get(key)
        if row is None:
            row = {
                "source": source,
                "target": target,
                "count": 0,
                "works": [],
                "direction": direction,
            }
            edges[key] = row
        if work_id not in row["works"]:
            row["works"].append(work_id)
            row["count"] = len(row["works"])
        if year:
            people[source]["years"].append(year)
            people[target]["years"].append(year)

    # Outgoing references
    ref_ids: List[str] = []
    own_ref_map: Dict[str, List[str]] = defaultdict(list)
    for work in own_works:
        wid = short_id(work.get("id") or "")
        for ref in work.get("referenced_works") or []:
            rid = short_id(ref)
            if not rid or rid == wid:
                continue
            own_ref_map[rid].append(wid)
            ref_ids.append(rid)
    ref_ids = sorted(set(ref_ids))
    print(f"Fetching {len(ref_ids)} referenced works…", flush=True)
    referenced = [] if dry_run else fetch_works_by_ids(client, ref_ids)
    print(f"  resolved {len(referenced)}", flush=True)
    for ref in referenced:
        rid = short_id(ref.get("id") or "")
        works_out.setdefault(rid, work_record(ref, doi_paths))
        year = int(ref.get("publication_year") or 0) or None
        for oa_id, name, orcid in authorship_people(ref):
            if oa_id == author_id:
                continue
            other = ensure_person(oa_id, name, orcid)
            for own_wid in own_ref_map.get(rid, []):
                add_edge(SELF_SLUG, other, own_wid, year, "i_cite")

    # Incoming citations
    print("Fetching citing works…", flush=True)
    citing_total = 0
    for idx, work in enumerate(own_works, start=1):
        wid = short_id(work.get("id") or "")
        cited_by = int(work.get("cited_by_count") or 0)
        if cited_by <= 0 or dry_run:
            continue
        print(f"  [{idx}/{len(own_works)}] {wid} cited_by={cited_by}", flush=True)
        for citer in client.paginate(
            "/works",
            {
                "filter": f"cites:{wid}",
                "select": SELECT_WORK,
                "sort": "publication_year:desc",
            },
        ):
            citing_total += 1
            cid = short_id(citer.get("id") or "")
            works_out.setdefault(cid, work_record(citer, doi_paths))
            year = int(citer.get("publication_year") or 0) or None
            for oa_id, name, orcid in authorship_people(citer):
                if oa_id == author_id:
                    continue
                other = ensure_person(oa_id, name, orcid)
                add_edge(other, SELF_SLUG, cid, year, "cites_me")
    print(f"  citing works scanned: {citing_total}", flush=True)

    for person in people.values():
        person["citedMe"] = 0
        person["citedByMe"] = 0
    for (source, target), edge in edges.items():
        count = int(edge["count"] or 0)
        if edge["direction"] == "cites_me":
            if source in people:
                people[source]["citedMe"] += count
            if target in people:
                people[target]["citedMe"] += count
        elif edge["direction"] == "i_cite":
            if source in people:
                people[source]["citedByMe"] += count
            if target in people:
                people[target]["citedByMe"] += count

    def score(person: Dict[str, Any]) -> int:
        return int(person.get("citedMe") or 0) + int(person.get("citedByMe") or 0)

    others = [p for p in people.values() if not p.get("self") and score(p) >= min_links]
    others.sort(key=lambda p: (-score(p), -(p.get("citedMe") or 0), p["name"].lower()))
    kept = others[:max_people]
    kept_ids = {SELF_SLUG} | {p["id"] for p in kept}

    people_out: List[Dict[str, Any]] = []
    for person in [people[SELF_SLUG], *kept]:
        years = [y for y in person.get("years") or [] if y]
        row: Dict[str, Any] = {
            "id": person["id"],
            "name": person["name"],
            "self": bool(person.get("self")),
            "citedMe": int(person.get("citedMe") or 0),
            "citedByMe": int(person.get("citedByMe") or 0),
        }
        if person.get("openalex"):
            row["openalex"] = person["openalex"]
        if person.get("orcid"):
            row["orcid"] = person["orcid"]
        if years:
            row["firstYear"] = min(years)
            row["lastYear"] = max(years)
        people_out.append(row)

    edges_out: List[Dict[str, Any]] = []
    for (source, target), edge in edges.items():
        if source not in kept_ids or target not in kept_ids:
            continue
        edges_out.append(
            {
                "source": source,
                "target": target,
                "count": edge["count"],
                "works": edge["works"],
                "direction": edge["direction"],
            }
        )
    edges_out.sort(key=lambda e: (-e["count"], e["source"], e["target"]))

    used_works: Set[str] = {short_id(w.get("id") or "") for w in own_works}
    for edge in edges_out:
        used_works.update(edge["works"])
    works_list = [works_out[wid] for wid in used_works if wid in works_out]
    works_list.sort(key=lambda row: (-(row.get("year") or 0), row.get("title") or ""))

    return {
        "v": 1,
        "source": "openalex",
        "authorId": author_id,
        "seed": seed,
        "fetched": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "people": people_out,
        "edges": edges_out,
        "works": works_list,
    }


def citers_list(graph: Dict[str, Any], *, min_count: int = 2, project_root: Optional[str] = None) -> List[Dict[str, Any]]:
    from processing.library.person_profile import attach_profile_fields, load_coauthor_urls
    from processing.library.twenty_people import load_people_profiles
    from processing.library.work_identity import normalize_orcid

    twenty_profiles = load_people_profiles(project_root) if project_root else {}
    coauthor_urls = load_coauthor_urls(project_root) if project_root else {}

    rows = []
    for person in graph.get("people") or []:
        if person.get("self"):
            continue
        cited_me = int(person.get("citedMe") or 0)
        if cited_me < min_count:
            continue
        row: Dict[str, Any] = {"name": person["name"], "count": cited_me}
        orcid = normalize_orcid(str(person.get("orcid") or ""))
        if orcid:
            row["orcid"] = orcid
        scholar = str(person.get("scholar") or "").strip()
        if scholar:
            from processing.library.twenty_people import normalize_scholar_id

            sid = normalize_scholar_id(scholar)
            if sid:
                row["scholar"] = sid
        attach_profile_fields(
            row,
            person["name"],
            twenty_profiles=twenty_profiles,
            coauthor_urls=coauthor_urls,
        )
        rows.append(row)
    rows.sort(key=lambda row: (-row["count"], row["name"].lower()))
    return rows


def write_artifacts(root: str, graph: Dict[str, Any]) -> Tuple[str, str]:
    from processing.library.person_profile import attach_profile_fields, load_coauthor_urls
    from processing.library.twenty_people import load_people_profiles

    twenty_profiles = load_people_profiles(root)
    coauthor_urls = load_coauthor_urls(root)
    if twenty_profiles or coauthor_urls:
        for person in graph.get("people") or []:
            if not isinstance(person, dict) or person.get("self"):
                continue
            attach_profile_fields(
                person,
                str(person.get("name") or ""),
                twenty_profiles=twenty_profiles,
                coauthor_urls=coauthor_urls,
            )

    json_dir = os.path.join(root, "assets", "json")
    data_dir = os.path.join(root, "_data")
    os.makedirs(json_dir, exist_ok=True)
    os.makedirs(data_dir, exist_ok=True)

    graph_path = os.path.join(json_dir, "citations.json")
    with open(graph_path, "w", encoding="utf-8") as handle:
        json.dump(graph, handle, ensure_ascii=False, indent=2, sort_keys=False)
        handle.write("\n")

    list_path = os.path.join(data_dir, "citers.yml")
    with open(list_path, "w", encoding="utf-8") as handle:
        yaml.dump(
            citers_list(graph, project_root=root),
            handle,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )
    return graph_path, list_path


def _merge_scholar_cache(graph: Dict[str, Any], root: str, max_people: int) -> Dict[str, Any]:
    from processing.library.scholar_citations import cache_dir, merge_scholar

    path = os.path.join(cache_dir(root), "normalized.json")
    if not os.path.isfile(path):
        print("No Scholar cache; skipping SerpApi merge.", flush=True)
        return graph
    print("Merging cached Google Scholar citers (no new searches)…", flush=True)
    with open(path, encoding="utf-8") as handle:
        normalized = json.load(handle)
    return merge_scholar(graph, normalized, max_people=max_people)


def _merge_s2(
    graph: Dict[str, Any],
    root: str,
    *,
    api_key: str,
    refresh: bool,
    sleep_s: float,
    max_people: int,
) -> Dict[str, Any]:
    from processing.library.s2_citations import apply_s2

    print("Adding Semantic Scholar edges…", flush=True)
    try:
        return apply_s2(
            graph,
            root,
            api_key=api_key,
            refresh=refresh,
            sleep_s=sleep_s,
            max_people=max_people,
        )
    except Exception as exc:
        print(f"Semantic Scholar merge failed ({exc}); keeping the graph so far.", flush=True)
        return graph


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build the citation network JSON")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--seed",
        choices=("library", "author"),
        default=None,
        help="library = DOIs from library.json (default); author = all OpenAlex works",
    )
    parser.add_argument("--root", type=str, default=None)
    parser.add_argument("--sleep", type=float, default=0.12)
    parser.add_argument("--no-scholar", action="store_true", help="Do not re-merge the Scholar cache")
    parser.add_argument("--no-s2", action="store_true", help="Do not fetch Semantic Scholar edges")
    parser.add_argument(
        "--s2-only",
        action="store_true",
        help="Skip OpenAlex and Scholar. Merge Semantic Scholar into the current citations.json",
    )
    parser.add_argument("--s2-refresh", action="store_true", help="Ignore the Semantic Scholar page cache")
    parser.add_argument("--s2-sleep", type=float, default=1.1)
    parser.add_argument(
        "--api-key",
        type=str,
        default=os.environ.get("OPENALEX_API_KEY"),
        help="OpenAlex API key (or OPENALEX_API_KEY). Never commit this.",
    )
    parser.add_argument(
        "--s2-api-key",
        type=str,
        default=os.environ.get("SEMANTIC_SCHOLAR_API_KEY") or os.environ.get("S2_API_KEY") or "",
        help="Semantic Scholar API key. Never commit this.",
    )
    args = parser.parse_args(argv)

    root = args.root or project_root()
    config = load_config(root)
    seed = args.seed or str(config.get("seed") or "library")
    max_people = int(config.get("max_people") or 200)
    if args.s2_only:
        graph_path = os.path.join(root, "assets", "json", "citations.json")
        with open(graph_path, encoding="utf-8") as handle:
            graph = json.load(handle)
        graph = dedupe_graph(
            _merge_s2(
                graph,
                root,
                api_key=args.s2_api_key,
                refresh=args.s2_refresh,
                sleep_s=args.s2_sleep,
                max_people=max_people,
            )
        )
        graph_path, list_path = write_artifacts(root, graph)
        print(
            f"Wrote {len(graph['people'])} people, {len(graph['edges'])} edges, "
            f"{len(graph['works'])} works ({graph.get('source')})",
            flush=True,
        )
        print(f"  {graph_path}", flush=True)
        print(f"  {list_path}", flush=True)
        return 0
    if not args.api_key:
        print(
            "Warning: no OPENALEX_API_KEY — using shared polite pool (easy to hit 429).",
            flush=True,
        )
    client = OpenAlexClient(
        str(config["mailto"]),
        api_key=args.api_key,
        sleep_s=args.sleep,
    )
    graph = build_citation_graph(
        root=root,
        config=config,
        client=client,
        dry_run=args.dry_run,
        seed=seed,
    )
    if args.dry_run:
        print(
            f"Dry run: {len(graph['people'])} people, {len(graph['edges'])} edges "
            "(not written)",
            flush=True,
        )
        return 0

    graph = dedupe_graph(graph)
    if not args.no_scholar:
        graph = dedupe_graph(_merge_scholar_cache(graph, root, max_people))
    if not args.no_s2:
        graph = dedupe_graph(
            _merge_s2(
                graph,
                root,
                api_key=args.s2_api_key,
                refresh=args.s2_refresh,
                sleep_s=args.s2_sleep,
                max_people=max_people,
            )
        )
    graph_path, list_path = write_artifacts(root, graph)
    print(
        f"Wrote {len(graph['people'])} people, {len(graph['edges'])} edges, "
        f"{len(graph['works'])} works ({graph.get('source')})",
        flush=True,
    )
    print(f"  {graph_path}", flush=True)
    print(f"  {list_path}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
