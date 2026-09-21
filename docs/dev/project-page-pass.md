# Project page pass

Repeat this when you add a project or refresh the project pages. The pitch is one sentence. The page is personal. The card links to the page; icons link out.

## 1. Inventory

List every file in `_projects/`. For each, note:

- `hidden` (hidden pages are out of scope until you unhide them)
- `category`
- whether the body is empty

## 2. Title

Set `title` in Title Case. That string is the card heading, the project-page heading, the sitemap entry, and the `/code/` heading when a repository’s GitHub URL matches `github`.

## 3. Pitch

Put one sentence in `description`.

That sentence is the card text, the project-page header, and the `/code/` blurb when a repository’s GitHub URL matches `github`. `_includes/repository/repo.liquid` does the match. Repositories with no project page keep the text in `_data/repositories.yml`.

The body does not open by restating the sentence.

## 4. Links

Set these only for real URLs, and only when the URLs differ:

- `github` — repository
- `website` — live site or product site
- `docs` — documentation

Do not set `redirect`. The card goes to the project page. The same icons sit under the pitch on the project page. `_includes/project_card_links.liquid` renders them.

## 5. Body

After the header pitch, write four beats. Do not label them. Do not explain the page itself. The icons under the pitch carry the links.

1. Pitch — already in `description`. Do not restate it as the first body sentence.
2. Problem → opportunity → solution — why this exists, in the first person, before any machinery.
3. Technical overview, simple — what it does, on whose machine, what it refuses. No command names, paths, flags, or version numbers.
4. Current intent — a non-codey sentence on where the work stands and what you are aiming at.

- If `website` or `docs` is set, do not paste install commands.
- If this page is the only home, the body has to stand alone.
- Do not flatten a long teaching or archive page. Put the four beats in the framing paragraphs and leave the rest.

## 6. Do not invent

No status, dates, collaborators, repositories, or URLs that are not already on the site or in the repository entry.

## 7. Check

On `/projects/`:

- Clicking the card opens the project page.
- Each icon opens its own URL.
- Folk Directory stays on this site when you click the card. The globe leaves.

Open one thin page and one software page. The header pitch matches the card, and the first paragraph does not repeat it. On `/code/`, a repository that has a project page uses that project’s `description`.
