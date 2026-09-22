# SEO / findability plan — glenwright.earth

**Access date / source:** 2026-09-22 findability package  
(`/Users/89298/Downloads/glenwright-earth-findability-2026-09-22`)

**Off-site profiles** (Scholar, ORCID, Conversation, `.net` 301, etc.) live in Untangle:  
`/Users/89298/Documents/untangle/projects/findability-profiles.md`

This file is the **on-site** implementation checklist only. Do not merge login-gated profile work here.

**Library durability:** DOI fills and cite hygiene (prefer `doi.org` over ScienceDirect/linkinghub) live in core processing — [`processing/config.py`](../../processing/config.py) `DOI_FILLS` + [`processing/core/bibtex_processor.py`](../../processing/core/bibtex_processor.py) `apply_doi_hygiene` / `inject_doi_hygiene_into_content`. They run on every `python processing/main.py` pass. Do not hand-edit `_library/` for those fixes.

---

## Repo truth (baseline)

| Fact | Where |
| --- | --- |
| OG + Schema **on** (was off) | [`_config.yml`](../../_config.yml): `serve_og_meta` / `serve_schema_org` + `og_image` |
| Person `sameAs` allowlist | [`_includes/metadata.liquid`](../../_includes/metadata.liquid) — ORCID + Scholar + site only |
| Library DOI / citation meta / `ScholarlyArticle` | Core processor DOI hygiene + library-item layout + metadata.liquid |
| Library hub description | [`_pages/library.md`](../../_pages/library.md) |
| Catalogue / generator | [`processing/library/`](../../processing/library/), `assets/json/library.json` |

---

## Locked decisions

- Canonical home: `https://glenwright.earth`
- Person `sameAs` allowlist until Semantic Scholar is cleaned **and** `glenwright.net` is 301’d: **ORCID + Google Scholar + `https://glenwright.earth` only**
- Default `og:image`: absolute `https://glenwright.earth/assets/img/prof_pic.jpg` (no `-800.webp` asset in repo)
- Prefer `doi.org` over ScienceDirect PII / linkinghub on library pages
- Wikidata: deferred (untangle plan, after identity alignment)

---

## P0 — identity wiring on-site

- [x] Turn on `serve_og_meta: true` and `serve_schema_org: true` in `_config.yml`; set `og_image` so rendered tags use the absolute portrait URL above.
- [x] Restrict Person `sameAs` in `metadata.liquid`: emit only ORCID + Scholar + site URL. Footer icons may stay (ResearchGate demoted separately).
- [x] Unique hub `description`s: `/library/`, `/books/`, Academia Obscura project + book, `/cv/`.
- [x] Library DOI surface via core processor DOI fill + regenerated pages (Getting Beyond Yes in `DOI_FILLS`; Highwire `citation_*` meta).
- [x] `ScholarlyArticle` JSON-LD on library items with DOI.

---

## P1 — make `/library/` the citation hub

- [x] CV publications → `/library/` first, DOI secondary (`assets/json/resume.json` + resume publications include).
- [x] Outbound cite hygiene: prefer doi.org over PII/linkinghub (`BibTeXProcessor.apply_doi_hygiene`).
- [ ] Remove catalogue contaminant Nordhaus AER “Climate Clubs” — Glen removes manually in Zotero/export.
- [x] Sitemap: books collection default `sitemap: false`; Academia Obscura book `sitemap: true`; `/dropdown/` `sitemap: false`.
- [x] Project URL aliases: hyphen → underscore redirects for academia-obscura, little-blue-letter, strong-high-seas.
- [x] Footer / chrome: ResearchGate commented out of `socials.yml` until bios match truth.

---

## P2 — polish

- [x] Cite-as blocks (BibTeX) on library pages with DOI (`_includes/library/cite_as.liquid`).
- [x] Library hub noscript: selected list prefers `/library/` landings (`catalog.py`).
- [ ] Optional 1200×630 OG crop later; per-page `og_image` for services already have topic images under `/assets/img/services/`.
- [ ] After off-site cleanup (untangle), reconsider expanding `sameAs` / footer endorsements.

---

## Out of scope (this repo)

- Google Scholar / ORCID / Conversation / IDDRI / LinkedIn / Academia / ResearchGate / Loop logins → Untangle `projects/findability-profiles.md`
- `glenwright.net` hard 301 → untangle (ops; not hosted in this Jekyll tree)

---

## Related

- Untangle ongoing site lane: `/Users/89298/Documents/untangle/projects/website-updates.md`
- Audit lanes: RESEARCHER-AUDIT, RESEARCHER-PUBLIC-PROFILES, SEO-BRO-PUBLIC-PROFILES, WEBDESIGN-PUBLIC-PROFILES (source package above)
