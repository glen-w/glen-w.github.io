# Code page pass

Repeat this when you add a public repository or refresh `/code/`. The reader is someone scanning repos, not browsing the story of the work. Projects stay personal; this page stays concrete.

## 1. Inventory

List public repositories under the GitHub user that are natively software: tools, libraries, prototypes, or developer templates. Skip content sites, book sidecars, note bundles, and other projects whose home belongs on `/projects/` (e.g. Folk Directory, Hoops, Academia Obscura, the BBNJ landscape notes). Keep real prototypes such as BBNJ CHM Prototype. For each candidate, note whether it already appears in `_data/repositories.yml`. Skip private repos.

## 2. Entry

Add or update the entry in `_data/repositories.yml`. Keep the file in ascending alphabetical order by `name`. Liquid also sorts ascending by `name` on the page (`sort_natural`).

Required:

- `repo` — `owner/name`
- `name` — Title Case display name (project `title` overrides this when `github` matches)
- `description` — one code-audience sentence (see Pitch)

Optional, only for real URLs and assets:

- `img` — thumb under `assets/img/projects/thumbs/`, copied from the product repo’s own logo (e.g. `assets/logo.png`, `website/images/logo.png`). Do not invent a mark that does not live in that repository.
- `url` — live site, docs, or project page
- `url_label` — `Site`, `Docs`, `Project page`, or `Website`

## 3. Pitch

Write one sentence for a developer or operator:

- what the repository is
- where it runs (local machine, static site, notes only)
- what you get when you open it

Do not reuse the project-page `description`. That pitch is for `/projects/`. YAML owns `/code/`. `_includes/repository/repo.liquid` matches project `title` by GitHub URL only; it does not pull project blurbs.

## 4. Links

Every card always links to GitHub. Add a second link when there is a useful door that is not the repo itself. Prefer the live site or docs over the project page when both exist.

If the matching project page should show a GitHub icon, set `github` on that project to `https://github.com/owner/name`.

## 5. Page framing

Keep a short intro on [`_pages/repositories.md`](../../_pages/repositories.md): public repos, local-first vs sites vs notes, graph is activity not ranking. No install commands.

## 6. Do not invent

No status, dates, collaborators, languages, or URLs that are not already on the site or in the repository.

## 7. Check

On `/code/`:

- Cards are alphabetical by display name.
- Each blurb reads as a clone/run pitch, not a personal project pitch.
- GitHub opens the repository; the second link opens its own URL.
- A repository with a project `github` match uses that project’s `title` as the heading.
- `/projects/` pitches are unchanged.
