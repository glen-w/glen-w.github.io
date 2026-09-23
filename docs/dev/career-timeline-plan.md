# Career timeline plan — glenwright.earth

**Status:** implemented on `/network/#timeline` (type/role stack, year brush, library links). Month axis and domain mode remain later.  
**Depends on:** existing `assets/json/library.json` (+ D3 patterns from `/network/`)  
**Related (later):** [Domain engagement timeline](#later-domain-engagement-timeline) — needs durable domain tags from Paperful first

Off-site / life planning lives in Untangle:  
`/Users/89298/Documents/untangle/projects/website-updates.md`

This file is the **on-site** implementation plan for a brushable career timeline. Do not confuse it with the **domain** timeline (tags over time); that is a later phase below.

---

## Goal

A D3 visualization of Glen’s public catalogue over time: scrub by year, stack by `type` or `role`, click through into library filters. Same data spine as the library and the Co-authors / Citations network.

---

## Data (today)

Source of truth: [`assets/json/library.json`](../../assets/json/library.json) (`v: 1`, ~350 items). Built by `processing/library/`.

| Field | Coverage (approx.) | Timeline use |
| --- | --- | --- |
| `year` | 100% (2007–2026) | X-axis / brush extent |
| `month` | 100% present, but **all `1` today** | Treat as year-only until month is real |
| `type` | 100% | Stack / colour by publication or event kind |
| `roles` | ~99% (4 items missing) | Alternate stack; filter chips |
| `venue` | ~73% | Tooltip / detail panel |
| `authors` / `authorsHtml` | ~27% | Tooltip only; do not require for layout |
| `title`, `id`, `info` | near-complete | Label + deep link to library item |
| `thumb`, `pdf`, `url`, `flags`, … | optional | Detail panel / icons — not required for v1 |

**No keywords / tags / domains in `library.json` today.** Career timeline does **not** wait on tagging. Domain timeline does (see later section).

### Data gaps to note before build

- [ ] **Month precision** — every `month` is `1`; brush/zoom should be year-grained until BibTeX/Zotero months are trustworthy.
- [ ] **Missing `roles`** — four ids need a role (or an explicit “unspecified” bucket): `wrightShipHasReached2023`, `wrightMarineGovernanceIndustrialised2014`, `VisitingFellowshipInternational2013`, `wrightMarineEnergyDesigning2012`.
- [ ] **Missing `venue`** — ~1/4 of items; tooltips must tolerate empty venue.
- [ ] **Sparse `authors`** — fine for career view; co-author network already owns collaboration.
- [ ] **Type vocabulary is wide** (18 types) — stacking all at once will be noisy; v1 should allow type grouping or a short allowlist + “Other”.

---

## UX placement (choose one in Phase 0)

Fits the network / library pattern the user already likes (“View network” from library → `/network/` tabs).

| Option | Pros | Cons |
| --- | --- | --- |
| **A. Third `/network/` tab** (“Timeline”) | Same shell as Co-authors / Citations; hash already (`#co-authors`, `#citations` → add `#timeline`); one bookmarkable hub | Network page title/description becomes broader than “networks” |
| **B. Library companion link** only (“View timeline”) → Option A or C | Discoverable next to “View network” | Still needs a destination page |
| **C. New `/timeline/` page** | Clear IA; network page stays graph-only | Extra nav surface; duplicates tab chrome unless shared |

**Recommendation:** **A + B** — third Network tab, plus a library header link parallel to “View network”. Rename network intro copy slightly (“networks and timeline”) rather than inventing a third top-level nav item.

Reuse: [`_pages/network.md`](../../_pages/network.md), [`assets/js/network.js`](../../assets/js/network.js) tab/hash wiring, D3 load pattern from `coauthors.js` / `citations.js`.

### Interaction sketch (v1)

- Horizontal time axis (years); brush / scrubber for range.
- Stacked marks by **type** (default) or **role** (toggle).
- Hover: title, year, type, roles, venue.
- Click item → `/library/{slug}/` via `info`, or library filter chips:
  - type: `/library/?filter=<Type>` (existing `library.js` `filter` + chip kinds)
  - role: same `filter` param with role strings
  - year range: search/hash or extend library deep-link if needed (may need a small library.js addition)
- Empty states when brush excludes all items; respect `prefers-reduced-motion`.

---

## Phased build

### Phase 0 — Decide & measure

- [x] Lock placement (A+B vs C).
- [x] Confirm stack default: `type` vs `role` (recommend **type** default, role toggle).
- [x] Spot-check year coverage and the four role-less items.
- [x] Decide type grouping (e.g. collapse Blog/Oped/Newspaper → “Writing”; Workshop/Training/Webinar → “Events”) or show raw types with legend collapse.

### Phase 1 — Static timeline (read-only)

- [x] Load `library.json` client-side (same cache-bust pattern as network graphs).
- [x] Year histogram or stacked bars by type; no brush yet.
- [x] Detail aside (mirror coauthors panel): click → metadata + link to `info`.
- [x] Wire Network tab + hash `#timeline`; library “View timeline” link.
- [x] Basic a11y: tab labels, SVG `role`/`aria-label`, keyboard focus on brush later.

### Phase 2 — Brush / scrub + library click-through

- [x] D3 brush on year axis; focus chart updates to brushed range.
- [x] Stack toggle: type ↔ role.
- [x] Click-through to library filters (`?filter=` for type/role); document any year deep-link gap.
- [x] Mobile: brush usable or fall back to year chips / range selects.

### Phase 3 — Polish

- [x] Optional: sync brush with URL (`?from=2015&to=2020` on `#timeline`) for shareable views.
- [ ] Optional: selected-only toggle (library `selected` flag).
- [ ] Optional: month axis **only after** processing stops emitting placeholder `month: 1`.
- [ ] Visual pass: match network/library tokens; no new card-heavy chrome.

### Out of scope for career timeline

- Domain / topic tags (see below).
- Resume employment blocks (`assets/json/resume.json`) — different story; do not merge unless explicitly requested later.
- Replacing the library year headings or the map page.

---

## Later: domain engagement timeline

**Status:** roadmap stub — **after** durable domain tags exist on catalogue items  
**Distinct from career timeline:** career = type/role over years; domain = topic/domain tags over years  
**Upstream:** Paperful staged auto-tagging — [`/Users/89298/Documents/paperful/docs/ROADMAP.md`](/Users/89298/Documents/paperful/docs/ROADMAP.md) (section *Auto-tagging library items*)  
**Downstream site:** tags must land in `library.json` (or a sibling JSON) via the website processing pipeline before any D3 work here

### When unblocked

- [ ] Confirm tag schema on site items (`domains` / `tags` — name TBD; stable slugs).
- [ ] Decide placement: fourth Network tab vs shared timeline page with mode switch (Career | Domains). Prefer **mode switch on the same Timeline tab** once both exist, to avoid tab sprawl.
- [ ] D3: brushable years; stack or stream by domain; click → library filter by tag.
- [ ] Cross-link career vs domain views in UI copy so they stay distinguishable.

Do **not** start domain-timeline UI work until Paperful stages 1–2 (built-in keywords + extraction) produce reviewable tags and the site pipeline can publish them.

---

## Related

- Network page: [`_pages/network.md`](../../_pages/network.md)
- Library catalogue: [`assets/json/library.json`](../../assets/json/library.json), [`assets/js/library.js`](../../assets/js/library.js)
- Untangle site lane: `/Users/89298/Documents/untangle/projects/website-updates.md`
- Paperful auto-tagging (feeds domain timeline only): `/Users/89298/Documents/paperful/docs/ROADMAP.md`
