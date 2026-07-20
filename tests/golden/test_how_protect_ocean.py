#!/usr/bin/env python3
"""
Golden end-to-end test for “How to Protect Our Ocean” (reqs 1–2).

Regenerates a library page from a minimal BibTeX fixture and asserts front-matter
fields (preview, agenda, pdf, video, speakers, role, quotes) match the golden
expected YAML derived from `_library/how-protect-ocean.md`.
"""

from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from processing.config import Configuration
from processing.library.generator import LibraryPageGenerator

FIXTURE_DIR = Path(__file__).resolve().parent.parent / 'fixtures' / 'golden' / 'how_protect_ocean'


def _read_front_matter(path: Path) -> dict:
    text = path.read_text(encoding='utf-8')
    assert text.startswith('---'), f'{path} missing YAML front matter'
    parts = text.split('---', 2)
    return yaml.safe_load(parts[1])


def _plant_assets(root: Path, expected: dict, bib_text: str) -> None:
    """Create tiny placeholder files named as in the bib / expected FM."""
    pdf_dir = root / 'assets' / 'pdf'
    preview_dir = root / 'assets' / 'img' / 'publication_preview'
    zip_dir = root / 'assets' / 'zips'
    for d in (pdf_dir, preview_dir, zip_dir):
        d.mkdir(parents=True, exist_ok=True)

    (pdf_dir / expected['pdf']).write_bytes(b'%PDF-1.4 placeholder')
    (pdf_dir / expected['agenda']).write_bytes(b'%PDF-1.4 agenda')
    (preview_dir / f"{expected['preview']}.jpeg").write_bytes(b'\xff\xd8\xff jpeg')
    # zip name from bib
    assert '2024_how_protect_ocean_a.zip' in bib_text
    (zip_dir / '2024_how_protect_ocean_a.zip').write_bytes(b'PK\x03\x04')


@pytest.mark.golden
@pytest.mark.library
@pytest.mark.requires_bibtexparser
class TestHowProtectOceanGolden:
    """Req 1–2: golden regeneration for How to Protect Our Ocean."""

    def test_golden_front_matter_fields(self, library_project_root):
        bib_src = FIXTURE_DIR / 'entry.bib'
        expected = yaml.safe_load(
            (FIXTURE_DIR / 'expected_front_matter.yml').read_text(encoding='utf-8')
        )
        bib_text = bib_src.read_text(encoding='utf-8')

        bib_path = library_project_root / '_bibliography' / 'papers.bib'
        bib_path.write_text(bib_text, encoding='utf-8')
        _plant_assets(library_project_root, expected, bib_text)

        out = library_project_root / '_library'
        pdf_dir = library_project_root / 'assets' / 'pdf'
        preview_dir = library_project_root / 'assets' / 'img' / 'publication_preview'
        zip_dir = library_project_root / 'assets' / 'zips'
        images_dir = library_project_root / 'assets' / 'img' / 'publications'

        with patch.object(Configuration, 'PDF_DIR', str(pdf_dir)), \
             patch.object(Configuration, 'PREVIEW_DIR', str(preview_dir)), \
             patch.object(Configuration, 'ZIP_DIR', str(zip_dir)), \
             patch.object(Configuration, 'IMAGES_DIR', str(images_dir)):
            gen = LibraryPageGenerator(
                bib_file=str(bib_path),
                output_dir=str(out),
                skip_dynamic_filters=True,
            )
            gen.run()

        pages = list(out.glob('*.md'))
        assert len(pages) == 1, f'Expected one golden page, got {[p.name for p in pages]}'
        fm = _read_front_matter(pages[0])

        assert fm['layout'] == expected['layout']
        assert fm['title'] == expected['title']
        assert fm['bibtex_key'] == expected['bibtex_key']
        assert fm['preview'] == expected['preview']
        assert fm['agenda'] == expected['agenda']
        assert fm['pdf'] == expected['pdf']
        assert fm['video'] == expected['video']
        assert fm['role'] == expected['role']
        assert fm['speakers'] == expected['speakers']
        assert fm['quotes'] == expected['quotes']
