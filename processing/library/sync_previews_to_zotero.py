#!/usr/bin/env python3
"""Replace Zotero ``thumbnail`` child attachments from an attach manifest.

Better BibTeX exports attachments titled ``thumbnail`` into the ``file`` field;
the site pipeline prefers those over PDF-rendered previews. After upgrading
``assets/img/publication_preview/*.jpeg``, run this so a re-export does not
revert to the old tiny Zotero thumbs.

Requires:
  - Zotero 10+ running with local write API enabled
  - Better BibTeX (``item.attachments`` JSON-RPC)
  - Paperful on ``PYTHONPATH`` (``/Users/89298/Documents/paperful``)

Usage:
  PYTHONPATH=/Users/89298/Documents/paperful \\
    python processing/library/sync_previews_to_zotero.py \\
    --manifest /tmp/cover_upgrade/attach_manifest.json

Click **Always Allow** in the Zotero dialog on first write.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Any

BBT_RPC = "http://127.0.0.1:23119/better-bibtex/json-rpc"
ZOTERO_API = "http://127.0.0.1:23119/api/users/0"
HOST = {"Host": "localhost:23119", "Content-Type": "application/json"}


def bbt_rpc(method: str, params: list[Any]) -> Any:
    body = json.dumps({"jsonrpc": "2.0", "method": method, "params": params, "id": 1})
    req = urllib.request.Request(BBT_RPC, data=body.encode(), headers=HOST, method="POST")
    with urllib.request.urlopen(req, timeout=60) as resp:
        payload = json.load(resp)
    if payload.get("error"):
        raise RuntimeError(f"BBT {method}: {payload['error']}")
    return payload.get("result")


def zotero_get(path: str) -> Any:
    req = urllib.request.Request(
        f"{ZOTERO_API}{path}",
        headers={"Host": "localhost:23119"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def attachment_keys_for_citekey(citekey: str) -> list[str]:
    """Return Zotero attachment item keys for a Better BibTeX citekey."""
    rows = bbt_rpc("item.attachments", [citekey]) or []
    keys: list[str] = []
    for row in rows:
        path = str(row.get("path") or "")
        match = re.search(r"/storage/([A-Z0-9]+)/", path)
        if match:
            keys.append(match.group(1))
    return keys


def parent_and_thumbnails(citekey: str) -> tuple[str | None, list[str]]:
    """Resolve parent item key and existing thumbnail attachment keys."""
    att_keys = attachment_keys_for_citekey(citekey)
    if not att_keys:
        return None, []

    parent: str | None = None
    thumbs: list[str] = []
    for key in att_keys:
        try:
            data = zotero_get(f"/items/{key}")["data"]
        except Exception:
            continue
        parent = parent or data.get("parentItem")
        title = (data.get("title") or "").lower()
        filename = (data.get("filename") or "").lower()
        if "thumbnail" in title or "thumbnail" in filename:
            thumbs.append(key)
    return parent, thumbs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        required=True,
        help="JSON list of {citekey, attach_path, ...}",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Resolve parents / thumbs only; do not write to Zotero",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Process only the first N manifest rows (0 = all)",
    )
    args = parser.parse_args()

    # Import Paperful only when writing — keeps dry-run usable without venv quirks
    sys.path.insert(0, "/Users/89298/Documents/paperful")
    from paperful.attach import Attacher
    from paperful.config import load_config
    from paperful.library import ZoteroBackend

    manifest = json.loads(args.manifest.read_text())
    if args.limit:
        manifest = manifest[: args.limit]

    backend: ZoteroBackend | None = None
    attacher: Attacher | None = None
    if not args.dry_run:
        cfg = load_config()
        backend = ZoteroBackend(cfg)
        if not backend.supports_write():
            print("Zotero write API unavailable (need Zotero 10+).", file=sys.stderr)
            return 2
        # Force auth early so the dialog appears once
        backend._ensure_write()
        attacher = backend._attacher
        assert attacher is not None

    ok = fail = skip = 0
    for row in manifest:
        citekey = row["citekey"]
        path = Path(row["attach_path"])
        if not path.is_file():
            print(f"SKIP missing file {citekey}: {path}")
            skip += 1
            continue

        parent, thumbs = parent_and_thumbnails(citekey)
        if not parent:
            # Parent with no attachments yet: try citationkey reverse via export
            # Attachments RPC returned empty — item may exist without files
            print(f"SKIP no parent/attachments for {citekey}")
            skip += 1
            continue

        print(
            f"{citekey}: parent={parent} replace={thumbs or '[]'} "
            f"<- {path} ({row.get('pixels')})"
        )
        if args.dry_run:
            ok += 1
            continue

        assert backend is not None and attacher is not None
        zot = backend.zl.zot
        for thumb_key in thumbs:
            try:
                zot.delete_item(zot.item(thumb_key))
                print(f"  deleted old thumbnail {thumb_key}")
            except Exception as exc:
                print(f"  WARN delete {thumb_key}: {exc}")

        result = attacher.attach(
            parent,
            path,
            title="thumbnail",
            note="paperful site:preview-upgrade",
        )
        if result.ok:
            print(f"  attached {result.attachment_key} ({result.reason})")
            ok += 1
        else:
            print(f"  FAIL {result.code}: {result.reason}")
            fail += 1

    print(f"\nDone: ok={ok} fail={fail} skip={skip}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
