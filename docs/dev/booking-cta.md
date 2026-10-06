# Booking CTA — Cal.rs (`meet.glenwright.earth`)

**Public booking URL:** [https://meet.glenwright.earth/u/book/half-hour](https://meet.glenwright.earth/u/book/half-hour) (30-minute call — only duration offered)

Cal.rs should align with the site brand palette (`--brand-linen`, `--brand-ink`, `--brand-sea` — see `.cursor/rules/brand-colors.mdc`). Infra runbook lives in the **homeserver** repo: `server/docs/apps/calrs.md` and `server/docs/operations/calrs-meet-bringup-2026-10-06.md`.

## Recommended: link (not iframe)

A nav item or button on `/`, `/services/`, or `/cv/` is simpler than embedding (mobile, Cap PoW, privacy tools, no CSP friction):

Prefer the contact page pattern (`_pages/contact.md`, `.contact-actions__link` in `_sass/_contact.scss`):

```markdown
[Book a meeting](https://meet.glenwright.earth/u/book/half-hour){: .contact-actions__link }
```

(Jekyll/kramdown attribute syntax — confirm in local `bundle exec jekyll serve` before deploy.)

## Optional: iframe embed

Cal.rs supports `?embed=1` on **booking** URLs only. In Cal.rs admin (Tailscale): **Event types → … → Embed** for generated markup.

```html
<iframe
  src="https://meet.glenwright.earth/u/book/half-hour?embed=1&amp;theme=light"
  title="Book a 30-minute call"
  style="width:100%;min-height:720px;border:0;border-radius:8px;"
  loading="lazy"
></iframe>
```

| | Link | iframe |
| --- | --- | --- |
| Setup | One URL | Tune `min-height` |
| Cap widget | On Cal.rs | Inside iframe |
| SEO / a11y | Better | OK with `title` |

**Preference:** link from the main site; iframe only on a dedicated page (e.g. `/meet/`) if you want the slot picker inline.

## Where to paste (site checklist)

- [ ] `_pages/about.md` — replace or supplement mailto “offer me money” line with schedule link
- [x] `_pages/services.md` — primary hire CTA (“Schedule a meeting”)
- [x] `_services/*.md` — per-page “Tell me…” + “Book a 30-minute call”
- [ ] Optional `_pages/meet.md` + permalink if using iframe embed

See also [`ROADMAP.md`](ROADMAP.md) § Services.
