"""Export ORCID / homepage / Scholar profiles from Twenty CRM onto disk.

Twenty (Untangle) is the person store: Person.orcid, Person.homepage
(facultyPage as fallback), Person.googleScholar. This module writes
``_data/people_profiles.yml`` for the library explore lists.

Refresh: see ``processing/library/PEOPLE_PROFILES.md``.
Scratch dumps belong under gitignored paths (``.twenty/``, ``people_dump*.json``).
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, Iterable, List, Optional, Tuple

import yaml

from processing.library.person_profile import normalize_token
from processing.library.work_identity import normalize_orcid

PROFILES_YAML = os.path.join("_data", "people_profiles.yml")
SCHOLAR_USER_RE = re.compile(r"[?&]user=([A-Za-z0-9_-]+)")
USER_AGENT = "glenwright.earth-people-profiles/1.0 (+https://glenwright.earth)"


def normalize_scholar_id(value: str) -> str:
    """Bare Google Scholar user id from a URL or raw id string."""
    text = (value or "").strip()
    if not text:
        return ""
    match = SCHOLAR_USER_RE.search(text)
    if match:
        return match.group(1)
    if re.fullmatch(r"[A-Za-z0-9_-]{6,}", text) and "://" not in text:
        return text
    return ""


def scholar_profile_url(scholar_id: str) -> str:
    sid = normalize_scholar_id(scholar_id)
    return f"https://scholar.google.com/citations?user={sid}" if sid else ""


def orcid_profile_url(orcid: str) -> str:
    oid = normalize_orcid(orcid)
    return f"https://orcid.org/{oid}" if oid else ""


def _link_url(field: Any) -> str:
    if isinstance(field, dict):
        return str(field.get("primaryLinkUrl") or "").strip()
    return str(field or "").strip()


def _display_name(record: Dict[str, Any]) -> str:
    name = record.get("name")
    if isinstance(name, dict):
        first = str(name.get("firstName") or "").strip()
        last = str(name.get("lastName") or "").strip()
        return f"{first} {last}".strip()
    return str(name or "").strip()


def _website_url(record: Dict[str, Any]) -> str:
    """Personal/faculty page — never an ORCID or Scholar URL."""
    candidates = [
        _link_url(record.get("homepage")),
        _link_url(record.get("facultyPage")),
    ]
    for url in candidates:
        if not url:
            continue
        lower = url.lower()
        if "orcid.org" in lower or "scholar.google" in lower:
            continue
        return url
    return ""


def _scholar_id(record: Dict[str, Any]) -> str:
    return normalize_scholar_id(
        _link_url(record.get("googleScholar")) or str(record.get("scholar") or "")
    )


def normalize_twenty_record(record: Dict[str, Any]) -> Optional[Dict[str, str]]:
    """Map a Twenty Person record to ``{name, orcid?, url?, scholar?}``."""
    name = _display_name(record)
    if not name:
        return None
    orcid = normalize_orcid(str(record.get("orcid") or ""))
    url = _website_url(record)
    scholar = _scholar_id(record)
    if not orcid and not url and not scholar:
        return None
    row: Dict[str, str] = {"name": name}
    if orcid:
        row["orcid"] = orcid
    if url:
        row["url"] = url
    if scholar:
        row["scholar"] = scholar
    return row


def merge_profile_rows(rows: Iterable[Dict[str, str]]) -> List[Dict[str, str]]:
    """Dedupe by normalized name; prefer rows that have more fields."""
    by_key: Dict[str, Dict[str, str]] = {}
    for row in rows:
        name = str(row.get("name") or "").strip()
        if not name:
            continue
        key = normalize_token(name)
        orcid = normalize_orcid(str(row.get("orcid") or ""))
        url = str(row.get("url") or "").strip()
        scholar = normalize_scholar_id(str(row.get("scholar") or ""))
        if url and ("orcid.org" in url.lower() or "scholar.google" in url.lower()):
            url = ""
        if not orcid and not url and not scholar:
            continue
        existing = by_key.get(key)
        if not existing:
            out: Dict[str, str] = {"name": name}
            if orcid:
                out["orcid"] = orcid
            if url:
                out["url"] = url
            if scholar:
                out["scholar"] = scholar
            by_key[key] = out
            continue
        if orcid and not existing.get("orcid"):
            existing["orcid"] = orcid
        if url and not existing.get("url"):
            existing["url"] = url
        if scholar and not existing.get("scholar"):
            existing["scholar"] = scholar
        if len(name) > len(existing["name"]):
            existing["name"] = name
    return sorted(by_key.values(), key=lambda r: r["name"].lower())


def ingest_twenty_records(records: Iterable[Dict[str, Any]]) -> List[Dict[str, str]]:
    rows = []
    for record in records:
        if not isinstance(record, dict):
            continue
        row = normalize_twenty_record(record)
        if row:
            rows.append(row)
    return merge_profile_rows(rows)


def enrich_from_citations(project_root: str, rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Fill missing ORCID / Scholar from ``assets/json/citations.json`` by name."""
    path = os.path.join(project_root, "assets", "json", "citations.json")
    if not os.path.isfile(path):
        return merge_profile_rows(rows)
    try:
        with open(path, encoding="utf-8") as handle:
            graph = json.load(handle)
    except (OSError, json.JSONDecodeError, TypeError):
        return merge_profile_rows(rows)

    extras: List[Dict[str, str]] = list(rows)
    for person in graph.get("people") or []:
        if not isinstance(person, dict) or person.get("self"):
            continue
        name = str(person.get("name") or "").strip()
        if not name:
            continue
        orcid = normalize_orcid(str(person.get("orcid") or ""))
        scholar = normalize_scholar_id(str(person.get("scholar") or ""))
        if not orcid and not scholar:
            continue
        patch: Dict[str, str] = {"name": name}
        if orcid:
            patch["orcid"] = orcid
        if scholar:
            patch["scholar"] = scholar
        extras.append(patch)
    return merge_profile_rows(extras)


def profile_link_targets(row: Dict[str, str]) -> List[Tuple[str, str]]:
    """Return ``(label, url)`` pairs to ping for a profile row."""
    targets: List[Tuple[str, str]] = []
    orcid = orcid_profile_url(str(row.get("orcid") or ""))
    if orcid:
        targets.append(("orcid", orcid))
    url = str(row.get("url") or "").strip()
    if url:
        targets.append(("url", url))
    scholar = scholar_profile_url(str(row.get("scholar") or ""))
    if scholar:
        targets.append(("scholar", scholar))
    return targets


def _ping_url(url: str, *, timeout: float = 8.0) -> Tuple[bool, str]:
    """Return ``(ok, detail)``. Treat 2xx/3xx as ok; retry GET if HEAD is refused."""
    headers = {"User-Agent": USER_AGENT, "Accept": "*/*"}

    def once(method: str) -> Tuple[int, str]:
        req = urllib.request.Request(url, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return int(getattr(resp, "status", 200) or 200), ""
        except urllib.error.HTTPError as exc:
            return int(exc.code), str(exc.reason or "")
        except Exception as exc:  # noqa: BLE001 — report any network failure
            return -1, f"{type(exc).__name__}: {exc}"

    status, detail = once("HEAD")
    if status in {405, 403, 400} or status == -1 and "HEAD" in detail:
        status, detail = once("GET")
    if 200 <= status < 400:
        return True, str(status)
    if status == -1:
        return False, detail or "request failed"
    return False, f"HTTP {status}" + (f" {detail}" if detail else "")


def check_profile_links(
    rows: List[Dict[str, str]],
    *,
    workers: int = 8,
    timeout: float = 8.0,
) -> List[Dict[str, str]]:
    """Ping every profile URL; return list of ``{name, kind, url, error}`` failures."""
    jobs: List[Tuple[str, str, str]] = []
    for row in rows:
        name = str(row.get("name") or "")
        for kind, url in profile_link_targets(row):
            jobs.append((name, kind, url))

    broken: List[Dict[str, str]] = []
    if not jobs:
        return broken

    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        futures = {
            pool.submit(_ping_url, url, timeout=timeout): (name, kind, url)
            for name, kind, url in jobs
        }
        for future in as_completed(futures):
            name, kind, url = futures[future]
            try:
                ok, detail = future.result()
            except Exception as exc:  # noqa: BLE001
                ok, detail = False, f"{type(exc).__name__}: {exc}"
            if not ok:
                broken.append(
                    {"name": name, "kind": kind, "url": url, "error": detail}
                )
    broken.sort(key=lambda row: (row["name"].lower(), row["kind"]))
    return broken


def write_people_profiles(project_root: str, rows: List[Dict[str, str]]) -> str:
    path = os.path.join(project_root, PROFILES_YAML)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    payload = {
        "source": "twenty",
        "people": rows,
    }
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("# ORCID / website / Scholar profiles from Twenty CRM (Untangle).\n")
        handle.write("# Refresh: see processing/library/PEOPLE_PROFILES.md\n")
        yaml.dump(payload, handle, default_flow_style=False, allow_unicode=True, sort_keys=False)
    return path


def load_people_profiles(project_root: str) -> Dict[str, Dict[str, str]]:
    """Index ``_data/people_profiles.yml`` by normalized name (+ loose last+initial)."""
    from processing.library.person_profile import name_parts

    path = os.path.join(project_root, PROFILES_YAML)
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, encoding="utf-8") as handle:
            raw = yaml.safe_load(handle) or {}
    except (OSError, yaml.YAMLError):
        return {}

    people = raw.get("people") if isinstance(raw, dict) else raw
    if not isinstance(people, list):
        return {}

    by_full: Dict[str, Dict[str, str]] = {}
    by_initial: Dict[tuple, List[Dict[str, str]]] = {}
    for person in people:
        if not isinstance(person, dict):
            continue
        name = str(person.get("name") or "").strip()
        if not name:
            continue
        profile = {
            "orcid": normalize_orcid(str(person.get("orcid") or "")),
            "url": str(person.get("url") or "").strip(),
            "scholar": normalize_scholar_id(str(person.get("scholar") or "")),
        }
        if profile["url"] and (
            "orcid.org" in profile["url"].lower()
            or "scholar.google" in profile["url"].lower()
        ):
            profile["url"] = ""
        if not profile["orcid"] and not profile["url"] and not profile["scholar"]:
            continue
        key = normalize_token(name)
        existing = by_full.get(key)
        if not existing or (profile["orcid"] and not existing.get("orcid")):
            by_full[key] = {k: v for k, v in profile.items() if v}
        last, initial = name_parts(name)
        if last and initial:
            by_initial.setdefault((last, initial), []).append(profile)

    for (last, initial), profiles in by_initial.items():
        unique = []
        seen = set()
        for profile in profiles:
            stamp = (
                profile.get("orcid") or "",
                profile.get("url") or "",
                profile.get("scholar") or "",
            )
            if stamp in seen:
                continue
            seen.add(stamp)
            unique.append(profile)
        if len(unique) != 1:
            continue
        loose = f"{last}{initial}"
        if loose not in by_full:
            by_full[loose] = {k: v for k, v in unique[0].items() if v}
    return by_full


def fetch_twenty_profiles(
    *,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
) -> List[Dict[str, str]]:
    """Pull co-authors + citers with ORCID/homepage/Scholar via Twenty REST."""
    key = api_key or os.environ.get("TWENTY_API_KEY") or ""
    base = (base_url or os.environ.get("TWENTY_BASE_URL") or "").rstrip("/")
    if not key:
        raise RuntimeError(
            "TWENTY_API_KEY not set. Use Cursor Twenty MCP to dump people, "
            "or export TWENTY_API_KEY (Windmill f/secrets/twenty). "
            "See processing/library/PEOPLE_PROFILES.md."
        )
    if not base:
        raise RuntimeError(
            "TWENTY_BASE_URL not set. Export your Twenty REST base "
            "(e.g. Tailscale MagicDNS URL) via env or .env — never commit it."
        )

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    records: List[Dict[str, Any]] = []
    for filter_expr in (
        "coAuthorWithGlen[gte]:1",
        "citesGlenWright[gte]:1",
    ):
        offset = 0
        while True:
            query = urllib.parse.urlencode(
                {
                    "filter": filter_expr,
                    "limit": 100,
                    "offset": offset,
                }
            )
            url = f"{base}/rest/people?{query}"
            req = urllib.request.Request(url, headers=headers)
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    payload = json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                raise RuntimeError(f"Twenty REST failed: HTTP {exc.code}") from exc
            batch = payload.get("data") or payload.get("people") or []
            if isinstance(payload, dict) and isinstance(payload.get("data"), dict):
                batch = payload["data"].get("people") or []
            if not isinstance(batch, list):
                batch = []
            records.extend(r for r in batch if isinstance(r, dict))
            if len(batch) < 100:
                break
            offset += len(batch)

    return ingest_twenty_records(records)


def main(argv: Optional[List[str]] = None) -> int:
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--from-json",
        action="append",
        default=[],
        help="Path to MCP/REST JSON dump containing result.records or a bare list",
    )
    parser.add_argument(
        "--fetch",
        action="store_true",
        help="Fetch live from Twenty REST (needs TWENTY_API_KEY + TWENTY_BASE_URL)",
    )
    parser.add_argument(
        "--enrich-citations",
        action="store_true",
        default=True,
        help="Merge missing ORCID/Scholar from assets/json/citations.json (default on)",
    )
    parser.add_argument(
        "--no-enrich-citations",
        action="store_true",
        help="Do not merge citation-graph ORCID/Scholar ids",
    )
    parser.add_argument(
        "--check-links",
        action="store_true",
        help="HEAD/GET every ORCID, website, and Scholar URL after writing",
    )
    parser.add_argument(
        "--strict-links",
        action="store_true",
        help="With --check-links, exit 1 if any URL is broken",
    )
    parser.add_argument(
        "--root",
        default=str(Path(__file__).resolve().parents[2]),
        help="Website project root",
    )
    args = parser.parse_args(argv)

    rows: List[Dict[str, str]] = []
    if args.fetch:
        rows.extend(fetch_twenty_profiles())

    for path in args.from_json:
        with open(path, encoding="utf-8") as handle:
            raw = json.load(handle)
        if isinstance(raw, list):
            records = raw
        elif isinstance(raw, dict):
            records = (
                (raw.get("result") or {}).get("records")
                or raw.get("records")
                or raw.get("people")
                or []
            )
        else:
            records = []
        rows.extend(ingest_twenty_records(records))

    if not rows and not args.from_json and not args.fetch:
        # Allow re-check / citation enrich of the existing YAML alone.
        existing = load_people_profiles(args.root)
        if not existing and not args.check_links:
            parser.error("Pass --fetch and/or --from-json PATH (see PEOPLE_PROFILES.md)")
        # Reconstruct rows from the on-disk index (loose keys skipped via name field).
        path = os.path.join(args.root, PROFILES_YAML)
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as handle:
                raw = yaml.safe_load(handle) or {}
            people = raw.get("people") if isinstance(raw, dict) else raw
            if isinstance(people, list):
                rows = [p for p in people if isinstance(p, dict) and p.get("name")]

    if args.enrich_citations and not args.no_enrich_citations:
        rows = enrich_from_citations(args.root, rows)
    else:
        rows = merge_profile_rows(rows)

    out = write_people_profiles(args.root, rows)
    print(f"Wrote {len(rows)} profiles → {out}")
    print(
        f"  orcid={sum(1 for r in rows if r.get('orcid'))} "
        f"url={sum(1 for r in rows if r.get('url'))} "
        f"scholar={sum(1 for r in rows if r.get('scholar'))}"
    )

    if args.check_links or args.strict_links:
        print("Checking profile links…")
        broken = check_profile_links(rows)
        if not broken:
            print("  all links ok")
        else:
            print(f"  {len(broken)} broken:")
            for item in broken:
                print(
                    f"  - {item['name']} [{item['kind']}] {item['url']} → {item['error']}"
                )
            if args.strict_links:
                return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
