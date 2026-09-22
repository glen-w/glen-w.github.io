#!/usr/bin/env python3
"""Push DOI fill + PII→doi.org URL hygiene into the live Zotero library.

Uses Paperful's local Zotero 10+ write path (same as ``paperful fix-metadata --apply``):
localhost:23119, Host localhost:23119, stored write key, ``update_item``.

Run from the paperful checkout so deps resolve::

    cd /Users/89298/Documents/paperful
    uv run python /Users/89298/Documents/website/glen-w.github.io/processing/zotero_doi_hygiene.py
    uv run python .../zotero_doi_hygiene.py --apply

Dry-run is the default. ``--apply`` writes.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

# Paperful package (this script is invoked via ``uv run`` from paperful/)
from paperful.attach import Attacher
from paperful.config import Config
from paperful.library import LibraryError, ZoteroBackend
from paperful.zot import SKIP_TYPES, ZoteroLocal

# Website processing config (DOI_FILLS)
SITE_ROOT = Path(__file__).resolve().parent.parent
if str(SITE_ROOT) not in sys.path:
    sys.path.insert(0, str(SITE_ROOT))
from processing.config import Configuration  # noqa: E402

_PII_RE = re.compile(
    r"(?:sciencedirect\.com|linkinghub\.elsevier\.com|api\.elsevier\.com)",
    re.IGNORECASE,
)
_DOI_URL_RE = re.compile(
    r"^https?://(?:dx\.)?doi\.org/(.+)$", re.IGNORECASE
)


def normalize_doi(value: str | None) -> str | None:
    if not value:
        return None
    text = str(value).strip()
    m = _DOI_URL_RE.match(text)
    if m:
        text = m.group(1)
    text = text.strip().rstrip("/")
    return text or None


def doi_url(value: str | None) -> str | None:
    bare = normalize_doi(value)
    return f"https://doi.org/{bare}" if bare else None


def is_pii_url(url: str | None) -> bool:
    return bool(url and _PII_RE.search(url))


def citation_key_from_extra(extra: str) -> str | None:
    """Better BibTeX / CSL often stores ``Citation Key: foo`` in Extra."""
    if not extra:
        return None
    for line in extra.splitlines():
        line = line.strip()
        if line.lower().startswith("citation key:"):
            return line.split(":", 1)[1].strip() or None
    return None


def load_papers_dois(bib_path: Path) -> set[str]:
    """Bare DOIs present in the site working bibliography."""
    text = bib_path.read_text(encoding="utf-8")
    found: set[str] = set()
    for match in re.finditer(r"(?im)^\s*doi\s*=\s*\{([^}]+)\}", text):
        bare = normalize_doi(match.group(1))
        if bare:
            found.add(bare.lower())
    return found


def propose_patches(
    zl: ZoteroLocal, *, papers_dois: set[str] | None = None
) -> list[dict[str, Any]]:
    """Scan top-level items; return proposed field patches.

    When ``papers_dois`` is set, only touch items whose DOI is in that set
    (site publications corpus), not the entire research library.
    """
    fills = dict(Configuration.DOI_FILLS)
    raw_items = zl.zot.everything(zl.zot.top())
    proposals: list[dict[str, Any]] = []

    for it in raw_items:
        data = it.get("data") or {}
        if data.get("itemType") in SKIP_TYPES or data.get("deleted"):
            continue
        key = it["key"]
        title = (data.get("title") or "").strip()
        extra = data.get("extra") or ""
        citekey = citation_key_from_extra(extra)
        current_doi = normalize_doi(data.get("DOI") or data.get("doi"))
        current_url = (data.get("url") or "").strip() or None

        after: dict[str, Any] = {}
        reasons: list[str] = []

        # 1) Known DOI fills (by Better BibTeX citation key)
        if citekey and citekey in fills:
            want = fills[citekey]
            if current_doi != want:
                after["doi"] = want
                reasons.append(f"DOI_FILLS[{citekey}]")

        # 2) Prefer doi.org over publisher PII URLs when a DOI exists (or will)
        effective_doi = normalize_doi(after.get("doi")) or current_doi
        if effective_doi and is_pii_url(current_url):
            want_url = doi_url(effective_doi)
            if want_url and current_url != want_url:
                after["url"] = want_url
                reasons.append("prefer doi.org over PII url")

        if not after:
            continue

        if papers_dois is not None:
            # Scope to site corpus: DOI fill keys always allowed; PII rewrites
            # only when the item's DOI is in papers.bib.
            fill_only = set(after.keys()) == {"doi"}
            doi_l = (effective_doi or "").lower()
            if not fill_only and doi_l not in papers_dois:
                continue

        proposals.append(
            {
                "itemKey": key,
                "title": title[:80],
                "citekey": citekey,
                "before": {"doi": current_doi, "url": current_url},
                "after": after,
                "reasons": reasons,
            }
        )
    return proposals


def apply_proposals(backend: ZoteroBackend, proposals: list[dict[str, Any]]) -> tuple[int, list[str]]:
    ok = 0
    errors: list[str] = []
    for p in proposals:
        try:
            backend.apply_patch(p["itemKey"], p["after"])
            ok += 1
            print(f"  ✅ {p['itemKey']}  {p['title'][:60]}")
        except Exception as exc:
            msg = f"{p['itemKey']}: {type(exc).__name__}: {exc}"
            errors.append(msg)
            print(f"  ❌ {msg}")
    return ok, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write patches into Zotero (default is dry-run)",
    )
    parser.add_argument(
        "--library-wide",
        action="store_true",
        help="Rewrite every PII URL in the library (default: only DOIs in papers.bib)",
    )
    args = parser.parse_args()

    paperful_root = Path.cwd()
    # Prefer paperful state next to where uv run was launched
    key_path = paperful_root / "state" / "zotero-local-api-key.json"
    key = None
    if key_path.exists():
        key = json.loads(key_path.read_text()).get("key")

    zl = ZoteroLocal(local_api_key=key)
    info = zl.ping()
    print(
        f"Zotero {info.get('zotero_version')}  write={info.get('supports_write')}  "
        f"key={'yes' if key else 'no'}"
    )
    if not info.get("supports_write"):
        print("Zotero 10+ with write API required.", file=sys.stderr)
        return 2

    papers_dois: set[str] | None = None
    if not args.library_wide:
        bib_path = SITE_ROOT / "_bibliography" / "papers.bib"
        papers_dois = load_papers_dois(bib_path)
        print(f"Scoping to {len(papers_dois)} DOIs from {bib_path.name}")

    proposals = propose_patches(zl, papers_dois=papers_dois)
    print(f"\nProposed patches: {len(proposals)}")
    for p in proposals:
        print(f"- {p['itemKey']}  citekey={p['citekey']!r}  {p['title']}")
        print(f"    before: {p['before']}")
        print(f"    after:  {p['after']}")
        print(f"    why:    {', '.join(p['reasons'])}")

    if not args.apply:
        print("\nDry-run only. Re-run with --apply to write into Zotero.")
        return 0

    if not proposals:
        print("Nothing to apply.")
        return 0

    cfg = Config()
    backend = ZoteroBackend(cfg, zl)
    backend._attacher = Attacher(cfg, zl)
    backend._attacher.key_path = key_path
    if key:
        backend._attacher.zl.zot.local_api_key = key
        backend.zl.zot.local_api_key = key

    print("\nApplying…")
    try:
        backend._ensure_write()
    except LibraryError as exc:
        print(f"Write authorisation failed: {exc}", file=sys.stderr)
        print("Click Allow / Always Allow in the Zotero dialog if it appears.", file=sys.stderr)
        return 2

    ok, errors = apply_proposals(backend, proposals)
    print(f"\nApplied {ok}/{len(proposals)}; errors={len(errors)}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
