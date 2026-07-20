# Paper Processing & Library Rendering Test Suite

## Overview

Comprehensive pytest suite for the paper processing pipeline and the library
content rendering system (BibTeX → markdown front matter → Liquid layouts).

## Test Structure

```
tests/
├── conftest.py                         # Shared fixtures (bib, library, processors)
├── run_tests.py                        # Test runner script
├── TEST_PLAN.md                        # This file
├── unit/                               # Paper-processing component tests
│   ├── test_bibtex_processor.py
│   ├── test_bibtex_roundtrip.py        # Reqs 40–65
│   ├── test_bibtex_syntax_validation.py
│   ├── test_bibtex_formatter.py
│   ├── test_cli_safety.py              # Reqs 80–99 subset
│   ├── test_enhanced_validator.py
│   ├── test_entry_processor.py
│   ├── test_field_cleaner.py
│   ├── test_file_*.py
│   ├── test_notes_processor.py         # Reqs 66–79
│   ├── test_paper_processor.py
│   ├── test_pdf_processor.py
│   ├── test_tag_extractor.py
│   ├── test_text_processor.py
│   └── test_zip_archive_generator.py
├── rendering/                          # Liquid / static HTML contracts (req 100)
│   └── test_header_actions.py
├── fixtures/rendering/                 # Static HTML action/header variants
├── library/                            # Library / content-rendering tests
│   ├── test_bib_parser.py
│   ├── test_content_generator.py
│   ├── test_dynamic_filters.py
│   ├── test_field_fidelity.py
│   └── test_generator.py
├── golden/ / corpus/                   # Exemplars + invariants
├── integration/
│   ├── test_end_to_end_processing.py
│   └── test_library_pipeline.py        # Full BibTeX → pages → filters
└── performance/
    └── test_large_file_processing.py
```

## Markers

| Marker | Meaning |
|--------|---------|
| `unit` | Isolated component tests |
| `integration` | Multi-component workflows |
| `library` | Library page generation / filters |
| `rendering` | Front-matter / Liquid contract tests |
| `bibtex_syntax` | BibTeX syntax validation |
| `performance` / `slow` | Heavy / timing-sensitive tests |

## Running Tests

```bash
# All fast tests
pytest tests/ -m "not slow"

# Library + rendering only
pytest tests/ -m library

# Paper processing unit tests
pytest tests/unit/ -m unit

# With coverage
pytest tests/ --cov=processing --cov-report=html -m "not slow"

# Via runner
python tests/run_tests.py --fast
```

## Library / Content Rendering Coverage

- **BibParser**: titles, authors, types, dates, venues, keywords, links, images, abstracts
- **ContentGenerator**: YAML front matter, standfirst/description, event detection, resources (local PDF verification, dedupe, zip metadata), categories, preview/gallery, notes body
- **LibraryPageGenerator**: load/filter/filename/page write, incremental skip, regenerate cleanup
- **DynamicFiltersGenerator**: entry types / roles / languages YAML with exact counts
- **TagExtractor / NotesProcessor**: annote `[type]`/`[role]`/`[language]`/`[selected]` shared with processing
- **Liquid contract**: every generated page has `layout`, `title`, `date`, `entry_type`, `year`, `bibtex_key`, `is_event`; resources schema when present

## Critical Paper-Processing Areas

BibTeX syntax validation remains mission-critical — see `test_bibtex_syntax_validation.py`.
Additional coverage: formatter, field cleaner, notes processor, tag extractor, entry/paper/PDF processors, zip archives.

## Requirement → test matrix (1–100)

| Req # | Theme | Primary tests |
|------:|-------|---------------|
| 1–9 | Golden e2e / 1:1 bib↔page / regen | `tests/golden/test_how_protect_ocean.py`, `tests/corpus/test_zero_diff.py`, `tests/corpus/test_invariants.py` |
| 10 | Page-deletion policy | `tests/library/test_generator.py`, `tests/corpus/test_invariants.py` |
| 11–18 | YAML + Jekyll + assets | `tests/library/test_content_generator.py`, `tests/library/test_generator.py`, `tests/integration/test_library_pipeline.py` |
| 19–20 | No Zotero paths / stale agenda | `tests/corpus/test_invariants.py`, `tests/library/test_field_fidelity.py` |
| 21–33 | Field fidelity (media, speakers, role, quotes, website) | `tests/library/test_field_fidelity.py` |
| 34–39 | Abstracts / empty keys / selected | `tests/library/test_field_fidelity.py`, `tests/unit/test_tag_extractor.py`, `tests/unit/test_notes_processor.py` |
| 40–65 | BibTeX parse/format round-trip | `tests/unit/test_bibtex_roundtrip.py`, `tests/unit/test_bibtex_formatter.py`, `tests/unit/test_bibtex_syntax_validation.py` |
| 66–79 | Notes / tags / video / audio / @@ escape | `tests/unit/test_notes_processor.py`, `tests/unit/test_tag_extractor.py`, `tests/unit/test_bibtex_processor.py` |
| 80–99 | Incremental / force / regenerate / CLI safety | `tests/unit/test_cli_safety.py`, `tests/unit/test_entry_processor.py`, `tests/unit/test_paper_processor.py`, `tests/integration/test_end_to_end_processing.py` |
| 100 | Header / action a11y snapshots | `tests/rendering/test_header_actions.py`, fixtures in `tests/fixtures/rendering/` |

### Markers used by new coverage

- `unit`, `bibtex_syntax` — round-trip / notes / CLI safety
- `library`, `rendering` — Liquid contracts + HTML fixtures

## Dependencies

```bash
pip install -r requirements-test.txt
# or
pip install -r tests/requirements-test.txt
```
