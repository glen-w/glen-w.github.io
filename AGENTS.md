# Agent instructions

## Library / publications: fix upstream first

Zotero is the source of truth for the publications library. Site files
(`_bibliography/papers.bib`, `_library/`, `assets/img/publication_preview/`,
`assets/pdf/`, etc.) are **derived** from a Zotero export + the paper-processing
pipeline. Edits that only land on the site will revert on the next
re-export/reprocess.

### Preference order (always)

1. **Zotero first** — fix the parent item in the **`my pubs`** collection
   (local write API via Paperful at `/Users/89298/Documents/paperful`,
   Better BibTeX citekeys; needs Zotero 10+).
2. **Then pipeline** — change `processing/` scripts only when the behaviour
   should apply to every future export (rename rules, thumbnail fit, tags, etc.).
3. **Site files last** — direct edits to bib / `_library` / preview JPEGs are
   fine for a quick fix, but **must** be pushed back to Zotero in the same task.

### When you edit library items on the site

If you change any of:

- preview / thumbnail images (`assets/img/publication_preview/`)
- PDFs or other attachments under `assets/`
- bibliographic fields that originate in Zotero (title, authors, DOI, notes/`annote`, keywords, etc.)

then you **must** also update the corresponding Zotero parent in **`my pubs`**
before finishing. Do not leave site-only diffs that the next export will clobber.

Concrete patterns:

| Site change | Push back to Zotero |
| --- | --- |
| Better preview JPEG | Replace the child’s attachment titled **`thumbnail`** (see `processing/library/sync_previews_to_zotero.py`) |
| PDF / slides / agenda | Attach or replace the matching child file via Paperful |
| Notes / type / role tags | Edit the Zotero **Notes** field (`[type]` / `[role]` / …) |
| Title, DOI, authors, ISBN | Patch the Zotero parent item fields |

### Do not

- Treat `_library/*.md` or `papers.bib` as the long-term store for content that
  Zotero owns.
- “Fix” a bad thumbnail only under `publication_preview/` and stop.
- Change export/processing to work around bad Zotero data when the data itself
  can be corrected upstream.

## Public-facing copy: show, don’t tell

This is a **public website**. Visitor-facing UI should not explain internals
(data sources like Twenty/Zotero, pipeline thresholds, “when known”, how icons
are populated). Prefer labels and self-evident UI; put docs in `processing/`
READMEs or agent notes, not in rendered Liquid/HTML.
