#!/usr/bin/env python3
"""
Zero-diff regeneration tests for the library corpus (reqs 5–7).

Full and incremental generation must be stable across repeated runs and
converge on the same filenames and front-matter key sets.
"""

from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from processing.config import Configuration
from processing.library.generator import LibraryPageGenerator

ZERO_DIFF_BIB = """
@article{stableAlpha2023,
    title = {Stable Alpha Paper},
    author = {Wright, Glen},
    year = {2023},
    month = {feb},
    abstract = {Stable abstract alpha.},
    pdf = {stable_alpha.pdf},
    preview = {stable_alpha.jpeg}
}

@misc{stableBeta2024,
    title = {Stable Beta Event},
    author = {Doe, Jane},
    year = {2024},
    month = {aug},
    annote = {[type]
workshop
[role]
organiser},
    video = {https://example.com/video/beta},
    pdf = {stable_beta.pdf}
}
"""


def _read_front_matter(path: Path) -> dict:
    text = path.read_text(encoding='utf-8')
    parts = text.split('---', 2)
    return yaml.safe_load(parts[1])


def _snapshot_library(out: Path) -> dict:
    """Map filename -> full file text for every .md page."""
    return {p.name: p.read_text(encoding='utf-8') for p in sorted(out.glob('*.md'))}


def _patch_and_run(root: Path, bib: Path, out: Path, *, regenerate=False, incremental=False):
    pdf_dir = root / 'assets' / 'pdf'
    preview_dir = root / 'assets' / 'img' / 'publication_preview'
    zip_dir = root / 'assets' / 'zips'
    images_dir = root / 'assets' / 'img' / 'publications'
    with patch.object(Configuration, 'PDF_DIR', str(pdf_dir)), \
         patch.object(Configuration, 'PREVIEW_DIR', str(preview_dir)), \
         patch.object(Configuration, 'ZIP_DIR', str(zip_dir)), \
         patch.object(Configuration, 'IMAGES_DIR', str(images_dir)):
        LibraryPageGenerator(
            bib_file=str(bib),
            output_dir=str(out),
            skip_dynamic_filters=True,
            regenerate=regenerate,
            incremental=incremental,
        ).run()


def _prepare(root: Path) -> Path:
    bib = root / '_bibliography' / 'papers.bib'
    bib.write_text(ZERO_DIFF_BIB, encoding='utf-8')
    pdf_dir = root / 'assets' / 'pdf'
    preview_dir = root / 'assets' / 'img' / 'publication_preview'
    (pdf_dir / 'stable_alpha.pdf').write_bytes(b'%PDF')
    (pdf_dir / 'stable_beta.pdf').write_bytes(b'%PDF')
    (preview_dir / 'stable_alpha.jpeg').write_bytes(b'\xff\xd8\xff')
    return bib


@pytest.mark.corpus
@pytest.mark.integration
@pytest.mark.requires_bibtexparser
class TestZeroDiffRegeneration:
    """Reqs 5–7: full/incremental zero-diff and convergence."""

    def test_full_regeneration_twice_zero_diff(self, library_project_root):
        """Req 5: full regeneration twice → identical file set + content."""
        bib = _prepare(library_project_root)
        out = library_project_root / '_library'

        _patch_and_run(library_project_root, bib, out, regenerate=True)
        first = _snapshot_library(out)
        assert first

        _patch_and_run(library_project_root, bib, out, regenerate=True)
        second = _snapshot_library(out)

        assert set(first) == set(second)
        for name in first:
            assert first[name] == second[name], f'Content drift on full regen: {name}'

    def test_incremental_twice_zero_content_diff(self, library_project_root):
        """Req 6: incremental twice → zero content diff."""
        bib = _prepare(library_project_root)
        out = library_project_root / '_library'

        _patch_and_run(library_project_root, bib, out, incremental=True)
        first = _snapshot_library(out)
        assert first

        _patch_and_run(library_project_root, bib, out, incremental=True)
        second = _snapshot_library(out)

        assert set(first) == set(second)
        for name in first:
            assert first[name] == second[name], f'Content drift on incremental: {name}'

    def test_full_and_incremental_converge(self, library_project_root, tmp_path):
        """Req 7: full vs incremental → same filenames + same FM keys for shared entries."""
        # Full into one library dir
        full_root = library_project_root
        bib = _prepare(full_root)
        full_out = full_root / '_library'
        _patch_and_run(full_root, bib, full_out, regenerate=True)
        full_snap = _snapshot_library(full_out)

        # Incremental from empty into a sibling project root
        incr_root = tmp_path / 'incr_project'
        for rel in (
            '_bibliography',
            '_library',
            '_data',
            'assets/pdf',
            'assets/img/publication_preview',
            'assets/img/publications',
            'assets/zips',
        ):
            (incr_root / rel).mkdir(parents=True, exist_ok=True)
        incr_bib = _prepare(incr_root)
        incr_out = incr_root / '_library'
        _patch_and_run(incr_root, incr_bib, incr_out, incremental=True)
        incr_snap = _snapshot_library(incr_out)

        assert set(full_snap) == set(incr_snap), (
            f'Filename mismatch: full={set(full_snap)} incr={set(incr_snap)}'
        )

        for name in full_snap:
            full_keys = set(_read_front_matter(full_out / name).keys())
            incr_keys = set(_read_front_matter(incr_out / name).keys())
            assert full_keys == incr_keys, (
                f'Front-matter key mismatch for {name}: '
                f'only_full={full_keys - incr_keys} only_incr={incr_keys - full_keys}'
            )
