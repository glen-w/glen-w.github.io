#!/usr/bin/env python3
"""Find person names left in the local catalogue of failures.

Uses scripts/failure_ner.py, which follows TranscriptX NER (spaCy PERSON).

Usage:
  python3 scripts/scan_failure_names.py
  python3 scripts/scan_failure_names.py --censor
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict

from failure_ner import DEFAULT_MODEL, ROOT, censor_hits, iter_person_hits


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"spaCy model (default: {DEFAULT_MODEL})")
    parser.add_argument("--censor", action="store_true", help="replace the reported names with block bars")
    args = parser.parse_args()
    try:
        hits = iter_person_hits(args.model)
    except OSError as exc:
        print(
            f"Could not load spaCy model {args.model!r}: {exc}\n"
            f"Install it with: python3 -m spacy download {args.model}",
            file=sys.stderr,
        )
        return 1

    if args.censor and hits:
        changed = censor_hits(hits)
        print(f"Censored names in {changed} files.\n")
        hits = iter_person_hits(args.model)

    grouped: dict[str, dict] = defaultdict(lambda: {"count": 0, "hits": []})
    for hit in hits:
        key = " ".join(hit.surface.split()).casefold()
        entry = grouped[key]
        entry["display"] = hit.surface if len(hit.surface) >= len(entry.get("display", "")) else entry["display"]
        entry["count"] += 1
        if len(entry["hits"]) < 8:
            rel = hit.path.relative_to(ROOT)
            text = hit.path.read_text(encoding="utf-8", errors="replace")
            start = text.rfind("\n", 0, hit.start) + 1
            end = text.find("\n", hit.start)
            snippet = " ".join(text[start : end if end >= 0 else None].split())
            if len(snippet) > 160:
                snippet = snippet[:157] + "..."
            entry["hits"].append(f"{rel}:{hit.line}  {snippet}")

    people = sorted(grouped.values(), key=lambda row: (-row["count"], row["display"].casefold()))
    files = {hit.path for hit in hits}
    print(f"{len(people)} person names other than Glen Wright in {len(files)} files.\n")
    for person in people:
        print(f"{person['display']} ({person['count']})")
        for line in person["hits"]:
            print(f"  {line}")
    return 1 if people else 0


if __name__ == "__main__":
    sys.exit(main())
