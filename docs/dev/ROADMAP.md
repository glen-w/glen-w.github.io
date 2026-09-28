# Site roadmap — glenwright.earth

**Updated:** 28 Sep 2026  
**This file is the living checklist.** Off-site / life-planning notes stay in Untangle: `/Users/89298/Documents/untangle/projects/website-updates.md`. Findability audit detail (what already shipped) is in [`seo-findability-plan.md`](seo-findability-plan.md) (gitignored). The old public `/roadmap/` tagging dump is unpublished.

Do not put this list on a visitor-facing page.

---

## Now

Work that should happen before new features pile on. Order is suggested, not sacred.

### 1. Unfurls (how a pasted link looks)

Source: 28 Sep 2026 deep dive. Default job of a share card is **hire-me** (consultant / ocean–energy), not a FOSS landing.

- [x] Point `og:image` / `twitter:image` at a dedicated **1200×630** social crop (<300 KB), or at least `prof_pic-800.webp` / a JPG export under ~200 KB — not `assets/img/prof_pic.jpg` (~1 MB). Add `og:image:width` / `og:image:height` once the asset is final. (`_config.yml` `og_image`, `_includes/metadata.liquid`)
- [x] Switch Twitter card to `summary_large_image` sitewide (or at least home, CV, services, projects).
- [ ] Unique `<title>` and meta descriptions for primary hubs. Pattern: human title, not the slug. Minimum: `/`, `/library/`, `/projects/`, `/code/`, `/creative/`, `/cv/` (already good), `/services/`, `/blog/`. Stop shipping Twitter title = `about` / `library` / `cv`.
- [ ] After the image swap, paste a link in Slack or iMessage and check the preview.

### 2. Services — rethink, then finalise

`/services/` exists (ocean, energy, facilitation, applied AI, coaching, copyediting, orientation) but it is not a finished offer. Nav is off (`nav: false`). Copy is seven parallel “I provide…” pages; orientation and coaching overlap; workshops and orientation share a thumbnail; there is no CTA.

- [ ] Decide the real offer set: keep, merge, or cut. Orientation is a different voice on purpose — keep it only if it is still an offer.
- [ ] Rewrite the index and remaining pages so the offer is obvious (who it is for, what you actually do). No pipeline talk. Soft mailto with subject presets is enough until a booking tool is confirmed.
- [ ] Unique title + description for `/services/` and each remaining service URL.
- [ ] Then put **Services** in primary nav (or the ⦿ menu) and add a quiet homepage pointer. Do not elevate a half-finished page.

Homepage “three quiet exits” (hire → `/services/`, use tool → `paperful.app`, read work → `/library/`) wait on this rewrite. Text + weight, not three primary buttons.

### 3. Catalogue of failures — check, mark outcomes, then go live

Local only until this is done. Gitignored: `_failures/`, `_pages/failures.md`, `assets/failures/`. Automated gate: `python3 scripts/check_failures_readiness.py` (and `--strict`). The script is a gate, **not** a substitute for a human pass.

- [ ] **Manual leak check** of every card (application, job ad, any leftover PDF). Look for referees, other people’s emails/phones, addresses, dates of birth, passport/visa rows, application numbers, local paths, mailbox names, unredacted supervisors. The script will miss things a person will not (partial blackouts, context that is identifying even without a name).
- [ ] **Manual status pass** — this is not a uniform rejection pile. Mark which applications you **got**, which you did not, which you withdrew, which had no reply. Status should be visible on the public cards so “catalogue of failures” is honest, not a dump of jobs you actually landed.
- [ ] Re-run `check_failures_readiness.py` (and `--strict` before un-ignoring).
- [ ] Un-gitignore, add `/failures/` where it belongs (likely ⦿, not primary nav), then ship.

Do not publish a subset “to see how it looks” with live PII still in the tree.

### 4. What’s in my backpack

New quiet page (permalink `/backpack/` or `/uses/` — prefer **backpack**). Everyday carry / tools / stack: hardware, software, and the few things you actually use. Show, don’t tell. No affiliate essays.

- [ ] Write the list (keep it current-tense and short).
- [ ] Page in the ⦿ menu, not primary nav.
- [ ] Unique title + one-line description.

### 5. Small honesty / wiring fixes (cheap, do with the unfurl pass)

- [x] Point the Paperful **project** card at `https://paperful.app` (today `_projects/paperful.md` still says `glenwright.earth/Paperful/`). Confirm `/code/` follows that URL. Folk Directory already points at `folkdirectory.co.uk`.
- [x] Deduplicate collaborator entities (Kristina Gjerde vs Kristina M. Gjerde vs Kristina Maria Gjerde in `_data/collaborators.yml` / `people_profiles.yml`). Same person twice on the frequent list hurts the library.
- [x] Fix the empty cache-buster on `main.css` (query hash is MD5 of an empty string). Personality CSS lives in that file; a broken fingerprint risks stale CSS after deploys.
- [ ] Replace the ⚡ emoji favicon with a simple sea-glass / earth mark (SVG + multi-size PNG).

---

## Next

After the now list, or whenever a slice is free.

- [ ] **Homepage selected publications** — mix a Nature / high-signal ocean lead-author piece above the fold among the REN21 stack, so the first screen matches the High Seas decade in the bio.
- [ ] **Library shell weight** — `/library/` HTML is still ~159 KB (collaborator list + graph chrome). Keep the JSON catalogue; lazy-mount the network graph; collapse frequent collaborators behind interaction. Goal from the earlier refactor: shell closer to ~22 KB. Measure before inventing virtual scroll.
- [ ] **Blog in 2026** — sitemap has ~588 blog URLs, almost all 2012–2020. Decide: `noindex` pre-2021, split an archive sitemap, or curate a short notes index. Leaving 500+ thin posts in the main sitemap dilutes crawl next to the library. (Untangle also has “address blog”.)
- [ ] **`/media/`** — nearly empty (“No media so far…”). Populate a short press/talk list **or** drop from sitemap/footer until there are a few real items.
- [ ] **Library zips 404** — `assets/zips/` is excluded from the Pages build on purpose; either host downloads elsewhere or stop linking them. (Untangle)
- [ ] **Thin / missing project writeups** — Ocean webinars sheet, Tiny Seascape, Twitter analysis sheet, Tiny Bunyscape. (Untangle)
- [ ] **Book-with-me CTA** — only after Cal.com (or equivalent) is confirmed. See Untangle `decisions/booking-calendar.md`.
- [ ] **Creative page as unexpected artist portfolio** — `/creative/` currently reads like a craft dump. Thicken it so the first impression is a portfolio, not a folder listing. Bundle:
  - Update collages (refresh the set; short alt/caption on image-heavy items).
  - Build out the poetry collection (enough pieces that it feels like a body of work, not a stub).
  - Overall page weight and sequencing so craft sits inside an artist frame rather than the other way around.
- [ ] Re-click-test `/library/` scroll progress after any library JS change (must not jump to 100% on load).

---

## Later

Useful, not blocking invites or the consultant door.

- [ ] Light Person JSON-LD (`JobTitle` / `alumniOf` / `knowsAbout`). Do **not** expand `sameAs` beyond ORCID + Scholar + `.earth` until other profiles are cleaned (Untangle `findability-profiles.md`).
- [ ] Security headers on Pages (`Content-Security-Policy` / `Referrer-Policy`) when next touching infra.
- [ ] Self-host or subset Roboto / Roboto Slab (today Google Fonts).
- [ ] Career timeline polish (selected-only toggle, month axis only after `month: 1` is real) — [`career-timeline-plan.md`](career-timeline-plan.md).
- [ ] Domain engagement timeline — blocked on Paperful durable tags, same file.
- [ ] Library multilingual PDF filenames / language badges — leftover from the old tagging roadmap; still true, still not urgent.
- [ ] Cumulative library filters (type + role AND) — same vintage; still a real UX gap.

---

## Not doing

- **Paperful.io collision strip / “not that Paperful” disclaimer** on `paperful.app` (or here). Explicit no.
- Rewriting personality toward particles / WebGL. Sea-glass stays.
- Turning glenwright.earth into a Paperful shop. FOSS pages stay FOSS.
- Sci-Hub / hosting / storage-undercut claims on any page.
- Visitor-facing copy that explains Twenty, Zotero, pipelines, or filter thresholds.
- Expanding Person `sameAs` until Scholar / `.net` / other profiles are aligned.
- Treating `_library/` or `papers.bib` as the source of truth (Zotero `my pubs` is).

Paperful product work (OG logo weight on `paperful.app`, install friction) lives in the Paperful repo, not this one — except the outbound URL on `/projects/` and `/code/`.

---

## Related

| | |
| --- | --- |
| Untangle site lane | `/Users/89298/Documents/untangle/projects/website-updates.md` |
| On-site findability (shipped P0/P1) | [`seo-findability-plan.md`](seo-findability-plan.md) |
| Career / domain timeline | [`career-timeline-plan.md`](career-timeline-plan.md) |
| Project / code page passes | [`project-page-pass.md`](project-page-pass.md), [`code-page-pass.md`](code-page-pass.md) |
| Personality pack | [`personality-pack-notes.md`](personality-pack-notes.md) |
| Failures publish gate | `scripts/check_failures_readiness.py` |
| Deep dive (28 Sep 2026) | `/Users/89298/Downloads/glenwright-earth-deep-dive-2026-09-28.md` |
