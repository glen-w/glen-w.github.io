---
layout: page
title: paperful
description: Fill the gaps in your Zotero library.
img: /assets/img/projects/thumbs/paperful.png
importance: 5
category: ongoing
---

<div align="center">
  <img src="/assets/img/projects/thumbs/paperful.png" alt="paperful logo" width="240"/>
</div>

**paperful** fills the gaps in your Zotero library. It fetches the PDFs your items are missing, keeps them in a folder tree that mirrors your collections, and attaches them back.

Work happens **on disk** (`out/`, `state/`). Zotero is a library adapter: read the catalogue in, write PDFs and metadata patches back. It is a local CLI, not a Zotero plugin and not a hosted service.

---

## Why paperful

Most tools in this space do one job well: find an OA PDF inside Zotero, tidy attachments, or lint a `.bib`. paperful is for **bulk missing-PDF fetch** with a resumable disk ledger:

- Open access first (Unpaywall, OpenAlex, arXiv, bioRxiv/medRxiv, Europe PMC, Semantic Scholar, CORE, optional Google Scholar)
- Campus **EZProxy** when you have a subscription
- **Sci-Hub is opt-in and off by default**
- Collection-shaped folders, identifier lint, proposed metadata patches you apply yourself

If you only need “Find Available PDF” for a handful of items, stay in Zotero. If you need a resumable CLI over a messy library, paperful is the tool.

---

## How it works

A typical run:

1. Scope a collection (or the whole library)
2. Prepare identifiers (verify or fill DOI)
3. Hit only the sources that match the item’s metadata
4. Write PDFs under `out/` and append `state/manifest.jsonl`
5. Optionally attach into Zotero 10+

`run` never rewrites bibliographic fields. `lint` is read-only. `fix-metadata --apply` is the write-back step.

---

## Getting started

Python 3.10+ and [uv](https://docs.astral.sh/uv/). Zotero running with the local API enabled.

```sh
git clone https://github.com/glen-w/Paperful.git
cd Paperful
uv sync
cp config.example.toml config.toml
uv run paperful doctor
uv run paperful run --collection interesting --dry-run
```

---

## Status

First usable CLI (`0.1`). **0.x** flags and report JSON may still move; **1.0**
will lock attach behaviour and `paperful.run_report.v1`.

## Links

- [GitHub](https://github.com/glen-w/Paperful)
- [Product site and docs](https://glenwright.earth/Paperful/)
- [How it compares](https://glenwright.earth/Paperful/guide/comparison.html)
