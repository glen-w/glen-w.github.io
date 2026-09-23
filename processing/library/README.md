# Library Page Generator

Automatically generates individual markdown pages for each bibliography item with rich features including share buttons, social posting, PDF embedding, and image galleries.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Test the Setup

```bash
python test_generator.py
```

### 3. Generate Pages (Test Mode)

```bash
python generate_library_pages.py --test
```

### 4. Generate All Pages

```bash
python generate_library_pages.py
```

## Usage

### Basic Usage

```bash
# Test mode (5 latest items with location)
python generate_library_pages.py --test

# Full generation
python generate_library_pages.py

# Custom BibTeX file
python generate_library_pages.py --bib-file _bibliography/Exported\ Items.bib

# Custom output directory
python generate_library_pages.py --output-dir _custom_library
```

### Command Line Options

- `--test`: Test mode - only process 5 most recent entries
- `--bib-file PATH`: Path to BibTeX file (default: \_bibliography/papers.bib)
- `--output-dir PATH`: Output directory for generated pages (default: \_library)
- `--catalog-only`: Write `assets/json/library.json` and `library-details.json` without regenerating markdown pages

### Index catalog JSON

A full library run (or `--catalog-only`) writes:

- `assets/json/library.json` — list fields for `/library/` (title, year, type, roles, authors, venue, pdf/url/doi, one 480px thumb)
- `assets/json/library-details.json` — abstracts, speakers, photos; fetched on first card expand
- `assets/json/coauthors.json` — collaboration graph for `/network/` (co-authors tab; people, edges, works)
- `assets/json/citations.json` — citation network for `/network/` (citations tab; OpenAlex, cached Scholar citers, Semantic Scholar)
- `_data/library_selected.yml` — noscript selected list
- `_data/library_exclude_from_counts.yml` — optional local list of titles/BibTeX keys omitted from filter chip counts and facet result lists (still in unfiltered catalogue / text search; gitignored; copy from `library_exclude_from_counts.example.yml`)
- `_data/library_exclude_from_timeline.yml` — optional local list of GitHub repo names or `owner/name` values omitted from the career timeline Code series (`github_repos.py` → `assets/json/code-repos.json`; gitignored; copy from `library_exclude_from_timeline.example.yml`)
- `_data/collaborators.yml` — frequent collaborators (2+ shared works) for the explore list; may include `orcid` / `url` / `scholar` from Twenty (`people_profiles.yml`)
- `_data/citers.yml` — frequent citers (2+ papers citing Glen) for the explore list; includes `orcid` / website `url` / `scholar` when known
- `_data/people_profiles.yml` — ORCID + homepage + Scholar export from Twenty CRM (Untangle); see [`PEOPLE_PROFILES.md`](PEOPLE_PROFILES.md)
- `_data/coauthor_aliases.yml` — optional forced name merges for the co-author graph
- `_data/openalex.yml` — citation-network build config (`author_id`, `seed`, caps)

Twenty REST (`twenty_people.py --fetch`) needs `TWENTY_API_KEY` and `TWENTY_BASE_URL` in the environment (see `.env.example`). Scratch dumps go in gitignored paths (`.twenty/`, `people_dump*.json`). Do not put Tailscale MagicDNS hosts or API keys in source.

Refresh the citation graph (needs network; use an API key — never commit it):

```bash
export OPENALEX_API_KEY=...   # from openalex.org/settings/api
# optional, raises the Semantic Scholar rate limit:
export SEMANTIC_SCHOLAR_API_KEY=...
PYTHONPATH=. python processing/library/citations.py
# optional full author footprint:
PYTHONPATH=. python processing/library/citations.py --seed author
```

The run re-merges `.cache/scholar/normalized.json` when that cache exists (no new SerpApi searches) and adds Semantic Scholar citation and reference edges for library DOIs. `--no-scholar` and `--no-s2` skip those layers. `--s2-only` repeats the Semantic Scholar merge onto the current `citations.json`. Duplicate works that share a DOI, or a near-identical title and year, are collapsed.

Preview JPEGs in `assets/img/publication_preview/` are fitted to a canonical 3:4 canvas (`480x640`) during paper processing so list and detail views can `object-fit: contain` without cropping. Undersized sources are scaled up to fill the frame (avoids postage-stamp thumbs). Landscape sources keep a sampled colour mat; portrait sources use a neutral pad so thin side shards do not appear. To refit existing previews without wiping PDFs:

```bash
python processing/main.py --normalize-previews
```

`/library/` is a JS-rendered catalogue on purpose. Crawlable pages remain `/library/:name/`. Count/type/role/lang drift vs the bib and `dynamic_filters.yml` fails the generator (`CatalogParityError`). Tests live in `tests/library/test_catalog.py`.

## Features

### Current Features (Phase 1)

- ✅ BibTeX parsing and processing
- ✅ Automatic filename generation with date prefix
- ✅ YAML front matter generation
- ✅ Basic markdown content generation
- ✅ Test mode for development
- ✅ Jekyll layout template

### Planned Features

- 🔄 Share panel with social media buttons
- 🔄 Social media post generation
- 🔄 PDF embedding with PDF.js
- 🔄 Image gallery with lightbox
- 🔄 Search and filtering
- 🔄 Related content suggestions

## File Structure

```
processing/library/
├── generate_library_pages.py    # Main generation script
├── bib_parser.py                # BibTeX parsing utilities
├── content_generator.py         # Markdown content generation
├── test_generator.py            # Test script
├── requirements.txt             # Python dependencies
├── README.md                    # This file
└── IMPLEMENTATION_PLAN.md       # Detailed implementation plan

_library/                        # Generated markdown pages
├── 250120_ship_has_reached_shore.md
├── 250120_30x30_target_implementation.md
└── ...

_layouts/
└── library-item.liquid          # Jekyll layout for library pages
```

## Generated Page Structure

Each generated page includes:

### Front Matter

```yaml
---
layout: library-item
title: "The ship has reached the shore"
date: 2023-03-04
description: "Why the historic Agreement to protect the High Seas matters"
tags: [ocean, governance, BBNJ]
categories: [publications]
entry_type: blog
authors: [Wright, Glen, Langlet, Arne, Tessnow-Von Wysocki, Ina]
venue: IDDRI
year: 2023
abstract: "On Saturday March 4, 2023..."
url: https://www.iddri.org/en/publications-and-events/blog-post/...
pdf: glen_wright_2023_The_ship_has_reached_the_shore.pdf
preview: glen_wright_2023_The_ship_has_reached_the_shore.jpeg
---
```

### Content Sections

- Abstract
- Publication Details
- Links and Resources
- Keywords
- Notes (if available)

## Jekyll Integration

### 1. Add Library Collection

Add to `_config.yml`:

```yaml
collections:
  library:
    output: true
    permalink: /library/:name/
```

### 2. Navigation

Add library section to your navigation menu.

### 3. Styling

The layout includes basic styling. Customize in `assets/css/library/`.

## Development

### Running Tests

```bash
python test_generator.py
```

### Adding New Features

1. Update the appropriate module (bib_parser.py, content_generator.py, etc.)
2. Test with `python test_generator.py`
3. Test with `python generate_library_pages.py --test`
4. Update documentation

### Debugging

- Use `--test` flag to limit processing to 5 items
- Check generated files in `_library/` directory
- Verify Jekyll build with `bundle exec jekyll serve`

## Troubleshooting

### Common Issues

1. **Missing dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **BibTeX file not found**

   - Check file path in `--bib-file` argument
   - Ensure file exists and is readable

3. **No entries found**

   - Test mode processes the 5 most recent entries by year
   - Use without `--test` flag to process all entries

4. **Jekyll build errors**
   - Check generated markdown files for syntax errors
   - Verify front matter YAML format
   - Check Jekyll logs for specific errors

### Getting Help

- Check the implementation plan in `IMPLEMENTATION_PLAN.md`
- Review generated files in `_library/` directory
- Test with a small subset using `--test` flag

## License

This project is part of the glen-w.github.io website and follows the same license terms.
