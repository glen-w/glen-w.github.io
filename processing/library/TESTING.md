# Testing Guide for Library Generator

The library/content rendering tests live in the unified suite under `tests/`:

```
tests/library/                 # BibParser, ContentGenerator, Generator, DynamicFilters
tests/integration/test_library_pipeline.py
tests/unit/test_tag_extractor.py
tests/unit/test_notes_processor.py
```

```bash
# From repo root
pytest tests/ -m library -v
pytest tests/library/ tests/integration/test_library_pipeline.py -v
```

See `tests/TEST_PLAN.md` for the full plan, markers, and coverage map.

Fixtures for library tests are in `tests/conftest.py` (`sample_library_entry`,
`library_project_root`, `bib_parser`, `content_generator`, etc.).
