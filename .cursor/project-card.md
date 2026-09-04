# Project card — glen-w.github.io

Filled from cursor_commands instantiate (2026-09-04). Slash commands stay self-contained; this file is the source of truth for re-fills.

```yaml
project: glen-w.github.io
package: processing
src_package: processing
ui_kind: none                 # Jekyll via Docker, not Streamlit — streamlit.md skipped
ui_port: 8080                 # docker-compose jekyll
ui_entry: docker compose up
sibling_ports:
  - 8501                      # TranscriptX
  - 8510                      # Transcribe
  - 8765                      # Rollup
small_fixture: tests/fixtures/golden/how_protect_ocean/
large_fixture_hint: real paper PDF/bib the user names, or a multi-entry slice of _bibliography/papers.bib
default_test_cmd: python -m pytest tests/unit tests/library -q
coverage_cmd: python -m pytest tests/unit tests/library --cov=processing --cov-report=term-missing -q
architecture_rules:
  - Liquid/Jekyll owns presentation; processing/ owns bib/library generation
  - Do not hand-edit generator-owned library pages
  - Do not bake _site/ or assets media into Docker layers
release_governance: none
backup_hub: sibling
backup_excludes:
  - _site
  - assets/img
  - assets/pdf
  - assets/libs
  - assets/zips
  - assets/audio
  - assets/video
  - assets/jupyter
  - assets/html
  - backups
  - vendor
  - archive
  - lighthouse_results
  - node_modules
  - .bundle
backup_includes:
  - _plugins/***
  - _includes/***
  - _layouts/***
  - _pages/***
  - _sass/***
  - _data/***
  - _bibliography/***
  - processing/***
  - bin/***
  - assets/js/***
  - assets/json/***
  - "*.liquid"
  - Gemfile*
  - CNAME
verify_paths:
  - processing
  - tests
  - Gemfile
  - _config.yml
  - .cursor/commands
  - assets/js/library.js
  - assets/json/library.json
staging_prefix: glen-site-backup
high_leverage_tests: library field fidelity, bibtex roundtrip/safety, golden how_protect rendering, CLI safety
probe_small: golden/library how_protect pytest
probe_large: real bib/PDF processing into /tmp/processing-deep-test-*
probe_extra: docker compose Jekyll smoke on :8080
doc_contracts: INSTALL.md, CUSTOMIZE.md, CONTRIBUTING.md, docs/processing/
```
