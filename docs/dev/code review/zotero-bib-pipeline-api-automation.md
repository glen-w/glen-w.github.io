# Code review: Zotero → site BibTeX pipeline and API automation

**Date:** 2026-09-04  
**Scope:** `processing/` pipeline that turns a Zotero BibTeX export into site-ready `_bibliography/papers.bib`, media under `assets/`, library pages, filters, and maps  
**Corpus:** ~360 BibTeX entries (`Exported Items.bib` → `papers.bib`), ~352 `_library/` pages  
**Verdict:** API automation is **feasible and worthwhile for the fetch/sync step**, but **should not replace** the existing post-processing core. Prefer a thin Zotero source adapter (local API first) that still feeds the current `PaperProcessor` contract.

---

## 1. What the system does today

### 1.1 Manual operator workflow

1. Export bibliography from Zotero as BibTeX (with Notes + file attachments).
2. Drop/overwrite `_bibliography/Exported Items.bib`.
3. Run `python processing/main.py` (often with `--incremental`).
4. Commit generated `papers.bib`, assets, `_library/`, filters, mapping outputs.

The export is the **only** Zotero touchpoint. Everything after that is local Python.

### 1.2 Pipeline stages (`processing/main.py`)

| Stage | Module(s) | Role |
|-------|-----------|------|
| Bib ingest + media | `PaperProcessor` → `EntryProcessor` | Copy/merge export → `papers.bib`; clean BibTeX; parse Notes tags; copy PDFs/images/audio from absolute Zotero `file` paths; thumbnails; zip archives |
| Cleanup | `PostProcessor` | Strip `file` (and optional other fields) from working bib |
| Validate | `EnhancedValidator` / `SimpleValidator` | Syntax, unrenamed Zotero filenames, path hygiene |
| Filters | `DynamicFiltersGenerator` | `_data/dynamic_filters.yml` from `[type]` / `[role]` / `[language]` |
| Library pages | `LibraryPageGenerator` | One markdown page per eligible entry under `_library/` |
| Mapping | `MappingProcessor` | Locations / map assets from bib |

Rough size of the hot path: **~8.6k LOC** across `processing/core`, `processing/utils`, and `processing/library` (excluding books/mapping extras).

### 1.3 Zotero-specific contracts the pipeline assumes

From a real export entry:

```bibtex
annote = {[type]
journal article
[role]
lead author
},
file = {PDF:/Users/.../storage/BGREJ9II/….pdf:application/pdf;thumbnail:…/thumbnail.png:image/png},
```

Hard dependencies:

1. **Notes field → `annote`** carrying bracket sections (`[type]`, `[role]`, `[language]`, `[speakers]`, `[video]`, `[abstract]`, …). Parsed by `NotesProcessor` / `TagExtractor`.
2. **`file` field** in Zotero’s `desc:absolute-path:mime` form (`;`-separated). Absolute paths must exist on the machine running the pipeline (`EntryProcessor` calls `os.path.exists` then copies).
3. **Snapshot filtering** (`text/html` / “Snapshot”) before media processing.
4. **Citation keys** stable across re-exports (incremental merge keys on citation key; pipeline output fields like `preview`/`pdf`/`photos` are preserved from existing `papers.bib`).
5. **Never hand-edit `papers.bib`** — it is overwritten from export + pipeline outputs (`main.py` header comment).

Enrichment APIs already in use (Crossref / Semantic Scholar via `MetadataFetcher`) are **orthogonal** to Zotero sync. Note: `EntryProcessor._update_entry_metadata` is currently a **stub (`pass`)**, so that enrichment path is not actually wired from entry processing despite roadmap/config support.

---

## 2. Code / system review

### 2.1 Strengths

- **Clear separation of concerns** after years of modularization: parse → notes/tags → files → format → validate → library/filters/map.
- **Documented Zotero Notes DSL** (`processing/ZOTERO_INTEGRATION.md`) with normalization rules and a shared `TagExtractor`.
- **Incremental mode** merges export with existing `papers.bib`, preserving `PIPELINE_OUTPUT_FIELDS` so re-exports do not blow away renamed media links.
- **Defensive BibTeX handling** for Zotero quirks (malformed/duplicated entry types, brace walking, snapshot attachments, Unicode conversion fallbacks in filter gen).
- **Strong test investment** under `tests/` (unit, library, golden, integration, CLI safety) — important if an API adapter is added.

### 2.2 Pain points (why automation is attractive)

| Pain | Evidence |
|------|----------|
| Manual export is the bottleneck | Operator must open Zotero, export, overwrite `Exported Items.bib`, then run Python |
| Machine-local absolute paths | `file = {…:/Users/89298/Documents/papers/storage/…}` — broken on another machine/CI without the same Zotero data dir |
| Dual bib files | Source (`Exported Items.bib`) vs working (`papers.bib`) is easy to confuse; library gen must read working only |
| cwd-sensitive CLI defaults | `main.py` still defaults to `../_bibliography/...` while `Configuration` uses absolute project-root paths |
| Duplicate module docstring | `main.py` repeats the same module docstring twice |
| Dead metadata hook | `_update_entry_metadata` stub means Crossref/S2 path may be unused in the main loop |
| Complexity concentrated in string BibTeX | Custom parsers + field rewrite (`_update_entry_content`) are fragile vs structured JSON |

### 2.3 Architecture diagram (current)

```
┌─────────────┐   manual BibTeX export    ┌──────────────────────┐
│   Zotero    │ ─────────────────────────▶│ Exported Items.bib   │
│  (desktop)  │   + absolute file paths   └──────────┬───────────┘
└─────────────┘                                      │
                                                     ▼
                                          ┌──────────────────────┐
                                          │  PaperProcessor      │
                                          │  notes + file copy   │
                                          │  thumbnails / zips   │
                                          └──────────┬───────────┘
                                                     ▼
                                          ┌──────────────────────┐
                                          │     papers.bib       │
                                          │  (+ assets/* media)  │
                                          └──────────┬───────────┘
                                ┌────────────────────┼────────────────────┐
                                ▼                    ▼                    ▼
                         filters.yml          _library/*.md            mapping/
```

The **replaceable** piece is only the left edge (Zotero → bib+paths). The right side is site-specific value and should stay.

---

## 3. API automation feasibility

### 3.1 Options compared

| Approach | What it automates | Attachment access | Notes / tags | Citation keys | Fit with current code |
|----------|-------------------|-------------------|--------------|---------------|------------------------|
| **A. Better BibTeX auto-export** | Watch/write `.bib` on change | Same local `file` paths as today | Same `annote` as today | BBT keys (stable if configured) | **Drop-in** — no Python API code |
| **B. Zotero 7 local API** (`pyzotero`, `local=True`) | Fetch items/children/versions without manual export | Local filesystem paths (or download via local API) | Child `note` items (HTML) — need adapter → `annote` DSL | Item keys ≠ BibTeX keys unless mapped | **Best API fit** for this repo’s local-path design |
| **C. Zotero Web API** (`pyzotero` cloud) | Sync from anywhere / CI | `GET …/items/{key}/file` download (needs file storage + quota) | Same note children | Same key issue | Good for CI/remote; worse for linked files / offline |
| **D. Full rewrite to CSL-JSON / Zotero JSON** | End-to-end structured pipeline | Explicit attachment objects | Structured fields / extra | Own ID scheme | Highest payoff long-term; **large** rewrite of parsers + library gen |

### 3.2 What the Web/Local APIs can provide

Via [pyzotero](https://github.com/urschrei/pyzotero) / Web API v3:

- Library items as JSON (creators, title, date, DOI, tags, relations, …).
- Child items: **attachments** (`contentType`, `filename`, `linkMode`, md5/mtime) and **notes** (`note` HTML).
- File download: `GET /users/{id}/items/{key}/file` (web) or local equivalents.
- Incremental sync: `format=versions` + `since=` library version.
- Optional `format=bibtex` export — but **API BibTeX is not identical** to desktop/BBT export (file paths, notes → `annote`, citekeys). Treat as a convenience, not a bit-for-bit replacement for `Exported Items.bib`.

### 3.3 Gaps relative to this pipeline

1. **Notes location:** Desktop BibTeX often puts the item Notes field into `annote`. API notes are usually **child note items** (HTML). The adapter must strip HTML and preserve `[type]` / `[role]` sections, or migrate tagging to Zotero tags / extra fields.
2. **Citekeys:** Pipeline and `_library` pages key off BibTeX citation keys (`Wright2011a`, Better BibTeX-style keys, occasional `zotero-item-#####`). Web API item keys are short opaque IDs. Without BBT or a stored mapping, incremental merge and page stability break.
3. **`file` field synthesis:** `EntryProcessor` expects BibTeX `file` strings and absolute paths. An API path must either:
   - synthesize a compatible `file` field after resolving local paths / downloading to a temp cache, **or**
   - refactor `EntryProcessor` to accept a list of attachment descriptors (cleaner, more work).
4. **Linked vs imported files:** Linked attachments may exist only on the author’s machine; Web API cannot download them. Local API / BBT auto-export remains safer for linked storage under `Documents/papers/storage`.
5. **Thumbnails / snapshots:** Same filtering rules apply; API may expose more HTML snapshots — keep `_filter_snapshot_attachments` semantics.
6. **Secrets / ops:** Web API needs user ID + API key (env, not committed). Local API needs Zotero 7 running with “Allow other applications…” enabled — fine for personal workflow, awkward for GitHub Actions.

### 3.4 Recommendation

**Do automate the source edge; do not rewrite the site pipeline in one leap.**

Recommended sequence:

1. **Short term (lowest risk):** Better BibTeX **automatic export** of the publications collection to `_bibliography/Exported Items.bib` (or a dedicated path), then keep `processing/main.py --incremental` as today. Removes the manual click without touching Python.
2. **Medium term (best automation ROI):** Add `processing/zotero_source.py` (name flexible) using **pyzotero local API** that:
   - pulls changed items since last library version,
   - resolves attachments to absolute paths (or downloads into a cache dir),
   - flattens notes into `annote`-compatible text,
   - maps citekeys (via Better BibTeX citekey API/plugin field, or a local `extra`/`citationKey` convention),
   - writes `Exported Items.bib` **or** hands structured entries into `PaperProcessor` without a full rewrite.
3. **Optional later:** Web API mode for machines without the Zotero data directory (download imported attachments only).
4. **Long term (optional):** Replace string BibTeX round-trips with an internal entry model; keep writing `papers.bib` only as the Jekyll Scholar artifact.

**Not recommended as first step:** Replacing Notes DSL with native Zotero tags alone (would require Liquid/filter/library changes and a migration of ~360 entries), or depending solely on Web API BibTeX export format.

---

## 4. Proposed adapter contract (if implementing API pull)

Minimal interface that preserves downstream code:

```text
fetch_library(since_version=None) -> SourceSnapshot
  SourceSnapshot:
    entries: list[SourceEntry]   # citation_key, fields, annote_text, attachments[]
    library_version: int
    written_bib_path?: Path      # optional: still emit Exported Items.bib

SourceAttachment:
    path_or_bytes, mime, role (pdf|slides|agenda|thumbnail|image|audio|other), description
```

Then either:

- **Compatibility mode:** render `file` + `annote` BibTeX and call existing `PaperProcessor.process_papers(source_bibtex_file=…)`, or  
- **Direct mode:** feed merged entry dicts into `_process_entries` / `EntryProcessor` after a thin attachment→path materializer.

Keep validation + library + filters unchanged until the adapter is proven on a `--test` subset.

---

## 5. Risks and mitigations

| Risk | Mitigation |
|------|------------|
| Citekey drift breaks `_library` / incremental merge | Require BBT citation keys or persist mapping `zoteroKey → citation_key`; golden tests for key stability |
| Notes HTML vs plain `annote` | Strip tags; round-trip tests with fixtures that include `[type]`/`[role]` |
| Missing linked files on CI | Document “local only” for full media; CI runs metadata-only or fixture-based tests |
| Rate limits / storage quota (web) | Prefer local API; cache file md5; incremental `since` |
| Dual sources (manual export + API) diverging | Single configured source; deprecate manual export once adapter is default |
| Accidental commit of API keys | Env vars + `.gitignore`; never write keys into `_bibliography` |

---

## 6. Suggested implementation phases

| Phase | Deliverable | Effort (order of magnitude) |
|-------|-------------|------------------------------|
| 0 | Document current export settings (collection, Notes included, file paths) + BBT auto-export trial | Hours |
| 1 | `zotero fetch` CLI: local API → `Exported Items.bib` (or temp bib) + smoke `--test` | Small |
| 2 | Wire `--from-zotero` into `main.py`; store last library version; incremental fetch | Small–medium |
| 3 | Attachment materializer (download/cache) so paths are not machine-specific | Medium |
| 4 | Refactor `EntryProcessor` off BibTeX `file` strings onto attachment objects | Medium–large |
| 5 | Optional Web API profile for remote sync | Medium |

Success criteria for Phase 1–2: byte-comparable or semantically equal `papers.bib` + media for a golden multi-entry fixture vs current manual export path.

---

## 7. Related cleanup (independent of API)

Worth doing whether or not API work proceeds:

1. Remove duplicate docstring in `processing/main.py`.
2. Align CLI defaults with `Configuration` absolute paths (drop cwd dependence).
3. Wire or remove `EntryProcessor._update_entry_metadata` stub (and the parallel stub on `PaperProcessor`).
4. Clarify in docs that library generation **must** read `papers.bib`, never the raw export (already noted in `run_library_generation`).
5. Consider moving operator docs from `processing/ZOTERO_INTEGRATION.md` under `docs/` for discoverability.

---

## 8. Conclusion

The scriptset is **complex for good reasons**: Zotero’s BibTeX export is lossy/quirky, and the site needs renamed media, tags, filters, and library pages. Most of that complexity should stay.

**Automating via API is possible** and mainly buys removal of the manual export step plus cleaner incremental sync. The highest-leverage path is **Better BibTeX auto-export and/or pyzotero local API → synthesized export**, keeping `PaperProcessor` as the site adapter. A full Web-API-first or JSON-native rewrite is viable later but is not required to get most of the operational win.

---

## References (in-repo)

- `processing/main.py` — orchestration  
- `processing/config.py` — paths, pipeline output fields, Crossref/S2 URLs  
- `processing/core/paper_processor.py` — export merge + writeback  
- `processing/core/entry_processor.py` — attachment processing  
- `processing/core/bibtex_processor.py` — notes + snapshot filter  
- `processing/core/notes_processor.py`, `tag_extractor.py` — Notes DSL  
- `processing/ZOTERO_INTEGRATION.md` — operator tag format  
- `_pages/roadmap.md` — historical “Zotero postprocessing” goals (partially superseded by current pipeline)
