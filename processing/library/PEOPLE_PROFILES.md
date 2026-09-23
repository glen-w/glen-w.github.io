# People profile icons (Twenty → library explore)

How to refresh ORCID / website / Google Scholar icons on Library → Explore
(collaborators + citers lists). Keep secrets and scratch dumps out of git.

## What lives where

| Path | Tracked? | Role |
|------|----------|------|
| `_data/people_profiles.yml` | yes | Committed snapshot: `name`, optional `orcid`, `url`, `scholar` |
| `_data/collaborators.yml` / `_data/citers.yml` | yes | List rows enriched from profiles (+ citation ORCID/scholar) |
| `.env` | **no** | `TWENTY_API_KEY`, `TWENTY_BASE_URL` (see `.env.example`) |
| `.twenty/` · `twenty_dump*.json` · `people_dump*.json` · `**/mcp_people*.json` | **no** | MCP/REST scratch dumps (may include emails) — see root `.gitignore` |

Untangle context: `decisions/twenty-crm-os.md`, `systems/work.md` (Twenty = person CRM; `homepage` = personal/faculty URL, not LinkedIn).

## Refresh (preferred: REST)

```bash
# From website repo root. Keys never go in source.
set -a && source .env && set +a   # or export TWENTY_API_KEY / TWENTY_BASE_URL

PYTHONPATH=. python processing/library/twenty_people.py --fetch --check-links
```

Then rebuild the explore list YAML / graphs so icons appear on the site:

```bash
PYTHONPATH=. python - <<'PY'
import json
from processing.library.coauthors import write_coauthor_artifacts
from processing.library.citations import write_artifacts

with open("assets/json/coauthors.json") as f:
    write_coauthor_artifacts(".", json.load(f))
with open("assets/json/citations.json") as f:
    write_artifacts(".", json.load(f))
PY
```

Or run a normal catalog / citations rebuild if you are already regenerating those.

`--check-links` HEADs (then GETs) every ORCID, website, and Scholar URL and prints broken ones. Use `--strict-links` to exit non-zero if any fail.

## Refresh (Cursor Twenty MCP, no API key)

1. `find_many_people` with `coAuthorWithGlen[gte]:1` and `citesGlenWright[gte]:1` (paginate; select at least `name`, `orcid`, `homepage`, `facultyPage`, `googleScholar`).
2. Save dumps under **gitignored** names, e.g. `.twenty/coauthors.json`, `people_dump_citers.json`.
3. Ingest:

```bash
PYTHONPATH=. python processing/library/twenty_people.py \
  --from-json .twenty/coauthors.json \
  --from-json .twenty/citers.json \
  --check-links
```

## Icons on the page

Liquid shows small icons next to each name when fields are present:

- ORCID → `ai ai-orcid` → `https://orcid.org/{id}`
- Website → `fa-solid fa-globe` → `url` (homepage / faculty; never ORCID pages)
- Google Scholar → `ai ai-google-scholar` → `https://scholar.google.com/citations?user={id}`

Priority when enriching lists: Twenty export → citation-graph ORCID/scholar → `_data/coauthors.yml` homepage.

## Do not

- Commit Tailscale MagicDNS hosts, API tokens, or full People dumps with emails.
- Treat OpenAlex / Semantic Scholar IDs as the website globe (those stay off the icon row).
- Hand-edit `people_profiles.yml` as the long-term source of truth — fix the Twenty card, then re-export.
