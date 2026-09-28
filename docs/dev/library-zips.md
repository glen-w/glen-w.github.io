# Library zips — local only

**Decision:** 28 Sep 2026  
**Status:** closed  
**Also:** Untangle `decisions/library-zips-not-public.md`

## Call

Do **not** publish packaged “Download all” zips on glenwright.earth. Keep generating and storing them locally.

## Why

- `assets/zips/` is excluded from the Jekyll / GitHub Pages build (~4 GB folder; Pages soft-caps the published site ~1 GB).
- Public Materials links were therefore 404s.
- Hosting on `vps-helper` (OVH VPS-1, 40 GB) was considered and rejected: wrong role (AdGuard / Nord exits / Umami), thin disk budget, abuse/egress risk for unauthenticated bulk files. Linked zips alone are only ~0.26 GB, but the feature is not critical.

## What stays

| Keep | Drop from public |
| --- | --- |
| `assets/zips/` on disk + in git | Materials “Download all” links |
| Pipeline `ZipArchiveGenerator` | `kind: zip` entries in `page.resources` |
| Front matter `zip_archive` / `zip_file_*` | Any visitor-facing zip URL |

## Code

- `_config.yml` — `exclude: assets/zips/`
- `processing/library/content_generator.py` — records zip metadata; does not emit zip resources
- `_includes/library/materials.liquid` — never renders `kind: zip`

## Reopen if

A cheap object store (R2/B2) or similar hosts the packages, **or** demand for multi-file downloads is real enough to justify that glue.
