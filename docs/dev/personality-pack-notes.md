# Personality pack

Restrained site-wide motion on the existing earthy al-folio fork: scroll reveals, collage hover, dotted-link underline draw, pub icon hit targets, CSS view transitions.

Kill switch: `personality.enabled: false` in `_config.yml` (JS skipped, `data-personality="off"`).

## Intensity dial

Top of [`_sass/_personality.scss`](../../_sass/_personality.scss):

| Variable | Default | Role |
|---|---|---|
| `--personality-ease` | `cubic-bezier(0.22, 1, 0.36, 1)` | shared easing |
| `--personality-reveal-y` | `10px` | scroll-reveal distance |
| `--personality-reveal-ms` | `550ms` | scroll-reveal duration |
| `--personality-lift` | `1px` | non-collage card hover |
| `--personality-hover-ms` | `220ms` | hover / underline |
| `--personality-vt-ms` | `250ms` | view-transition fade |
| `--personality-accent` | `#3d5f5c` | focus, underline draw, hairlines, wash |
| `--personality-wash-opacity` | `0.08` | homepage portrait radial wash (`0` = off) |
| `--personality-hairline-width` | `2px` | section title left rule |
| `--personality-hairline-inset` | `0.65rem` | hairline padding |

Dark-theme accent sibling: `#8aa8a4`.

**Pop patch (static):** 2px accent hairline on homepage `h2`, `#selectedPublicationsContainer h2`, and blog `.header-bar > h1`; soft radial wash behind homepage `.profile` portrait. Tone down: lower `--personality-wash-opacity` or set `personality.enabled: false`.

## What shipped

| File | Role |
|---|---|
| `_sass/_personality.scss` | tokens, hairlines, hero wash, reveals, collage, link draw, pub icons, VT, reduced-motion |
| `assets/js/personality.js` | allowlist IntersectionObserver reveals |

Hooks: `assets/css/main.scss` import, `_includes/scripts.liquid`, `_layouts/default.liquid` (`data-personality`), `_config.yml` flag.

Related visual follow-ups (not pack files): overflow title `⦿`, library type-badge hover aligned with tags, `/code/` repo-name fallback when GitHub stats images fail.

## Dropped after visual review

Good ideas that did not add much in practice — not restored later without a stronger reason:

- **Now-chip** (`currently` / `latest scribbling` pill in the header). Quiet, but it did not earn the chrome. `_includes/personality-chip.liquid` and `_data/now.yml` were removed.
- **Homepage portrait parallax.** Drift was capped at ~6px and was not perceptible, so the JS/CSS came out.

## Motion / a11y

- `prefers-reduced-motion: reduce`: no reveal classes, no hover transforms, no view transitions.
- Collage DNA is **not** on `.publications` or library cards.
- Library cards are not in the reveal allowlist.
- First-viewport nodes skip the reveal class so LCP is not delayed.
