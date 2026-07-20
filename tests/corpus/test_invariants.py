#!/usr/bin/env python3
"""
Corpus-level invariants for library page generation (reqs 3–4, 8–11, 14–20).

Uses a small temp BibTeX corpus (2–3 entries) and LibraryPageGenerator with
asset directories patched to the temp project root.
"""

from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from processing.config import Configuration
from processing.library.generator import LibraryPageGenerator

CORPUS_BIB = """
@article{alpha2023,
    title = {Alpha Ocean Paper},
    author = {Wright, Glen},
    year = {2023},
    month = {jan},
    abstract = {A non-empty abstract for alpha.},
    website = {https://example.com/alpha},
    preview = {alpha_preview.jpeg},
    pdf = {alpha_paper.pdf},
    agenda = {alpha_agenda.pdf},
    slides = {alpha_slides.pdf},
    zip_archive = {alpha_bundle.zip}
}

@misc{beta2024,
    title = {Beta High Seas Event},
    author = {Doe, Jane},
    year = {2024},
    month = {jun},
    annote = {[type]
conference
[role]
speaker},
    video = {https://www.youtube.com/watch?v=beta123},
    preview = {beta_preview.jpeg},
    pdf = {beta_handout.pdf}
}

@techreport{gamma2022,
    title = {Gamma Policy Brief},
    author = {Smith, Alice},
    year = {2022},
    month = {mar},
    abstract = {Gamma abstract text.},
    pdf = {gamma_report.pdf}
}
"""


def _read_front_matter(path: Path) -> dict:
    text = path.read_text(encoding='utf-8')
    assert text.startswith('---'), f'{path} missing YAML front matter'
    parts = text.split('---', 2)
    return yaml.safe_load(parts[1])


def _patch_dirs(root: Path):
    pdf_dir = root / 'assets' / 'pdf'
    preview_dir = root / 'assets' / 'img' / 'publication_preview'
    zip_dir = root / 'assets' / 'zips'
    images_dir = root / 'assets' / 'img' / 'publications'
    return (
        patch.object(Configuration, 'PDF_DIR', str(pdf_dir)),
        patch.object(Configuration, 'PREVIEW_DIR', str(preview_dir)),
        patch.object(Configuration, 'ZIP_DIR', str(zip_dir)),
        patch.object(Configuration, 'IMAGES_DIR', str(images_dir)),
    )


def _plant_corpus_assets(root: Path) -> None:
    pdf_dir = root / 'assets' / 'pdf'
    preview_dir = root / 'assets' / 'img' / 'publication_preview'
    zip_dir = root / 'assets' / 'zips'
    for name in (
        'alpha_paper.pdf',
        'alpha_agenda.pdf',
        'alpha_slides.pdf',
        'beta_handout.pdf',
        'gamma_report.pdf',
    ):
        (pdf_dir / name).write_bytes(b'%PDF-1.4')
    for name in ('alpha_preview.jpeg', 'beta_preview.jpeg'):
        (preview_dir / name).write_bytes(b'\xff\xd8\xff')
    (zip_dir / 'alpha_bundle.zip').write_bytes(b'PK\x03\x04')


def _write_corpus_bib(root: Path) -> Path:
    bib = root / '_bibliography' / 'papers.bib'
    bib.write_text(CORPUS_BIB, encoding='utf-8')
    return bib


def _run_generator(root: Path, bib: Path, *, regenerate=False, incremental=False):
    out = root / '_library'
    patches = _patch_dirs(root)
    with patches[0], patches[1], patches[2], patches[3]:
        gen = LibraryPageGenerator(
            bib_file=str(bib),
            output_dir=str(out),
            skip_dynamic_filters=True,
            regenerate=regenerate,
            incremental=incremental,
        )
        gen.run()
    return out


@pytest.mark.corpus
@pytest.mark.library
@pytest.mark.integration
@pytest.mark.requires_bibtexparser
class TestCorpusInvariants:
    """Corpus invariants over a small generated library."""

    def test_bibtex_key_page_bijection_and_count(self, library_project_root):
        """Reqs 3–4, 8: 1:1 bibtex_key↔page; page count == eligible entries."""
        bib = _write_corpus_bib(library_project_root)
        _plant_corpus_assets(library_project_root)
        out = _run_generator(library_project_root, bib)

        pages = list(out.glob('*.md'))
        keys = []
        for path in pages:
            fm = _read_front_matter(path)
            assert 'bibtex_key' in fm
            keys.append(fm['bibtex_key'])

        expected_keys = {'alpha2023', 'beta2024', 'gamma2022'}
        assert len(pages) == len(expected_keys)
        assert set(keys) == expected_keys
        assert len(keys) == len(set(keys)), 'Duplicate bibtex_key across pages'

    def test_every_front_matter_yaml_parses(self, library_project_root):
        """Req 11: every FM YAML parses."""
        bib = _write_corpus_bib(library_project_root)
        out = _run_generator(library_project_root, bib)
        for path in out.glob('*.md'):
            fm = _read_front_matter(path)
            assert isinstance(fm, dict)
            assert fm.get('layout') == 'library-item'

    def test_no_zotero_absolute_paths(self, library_project_root):
        """Req 19: no absolute Zotero filesystem paths in generated pages."""
        bib = _write_corpus_bib(library_project_root)
        out = _run_generator(library_project_root, bib)
        forbidden = (
            '/Users/',
            '/zotero/storage/',
            'Zotero/storage',
            ':\\Users\\',
        )
        for path in out.glob('*.md'):
            text = path.read_text(encoding='utf-8')
            for needle in forbidden:
                assert needle not in text, f'{path.name} contains Zotero path {needle!r}'

    def test_no_stale_agenda_pdf_placeholder(self, library_project_root):
        """Req 20: no stale `agenda: agenda.pdf` placeholder in generated pages."""
        bib = _write_corpus_bib(library_project_root)
        _plant_corpus_assets(library_project_root)
        out = _run_generator(library_project_root, bib)
        for path in out.glob('*.md'):
            fm = _read_front_matter(path)
            if 'agenda' in fm:
                assert fm['agenda'] != 'agenda.pdf', (
                    f'{path.name} has stale agenda.pdf placeholder'
                )
            assert 'agenda: agenda.pdf' not in path.read_text(encoding='utf-8')

    def test_referenced_local_assets_exist_when_planted(self, library_project_root):
        """Reqs 14–18: referenced local PDF/preview/agenda/slides/zip exist when planted."""
        bib = _write_corpus_bib(library_project_root)
        _plant_corpus_assets(library_project_root)
        out = _run_generator(library_project_root, bib)

        pdf_dir = library_project_root / 'assets' / 'pdf'
        preview_dir = library_project_root / 'assets' / 'img' / 'publication_preview'
        zip_dir = library_project_root / 'assets' / 'zips'

        for path in out.glob('*.md'):
            fm = _read_front_matter(path)
            if fm.get('pdf'):
                assert (pdf_dir / fm['pdf']).is_file(), f"missing pdf {fm['pdf']}"
            if fm.get('agenda'):
                assert (pdf_dir / fm['agenda']).is_file(), f"missing agenda {fm['agenda']}"
            if fm.get('slides'):
                assert (pdf_dir / fm['slides']).is_file(), f"missing slides {fm['slides']}"
            if fm.get('preview'):
                stem = fm['preview']
                candidates = [
                    preview_dir / f'{stem}.jpeg',
                    preview_dir / f'{stem}.jpg',
                    preview_dir / f'{stem}.png',
                    preview_dir / stem,
                ]
                assert any(c.is_file() for c in candidates), f"missing preview {stem}"
            if fm.get('zip_archive'):
                assert (zip_dir / fm['zip_archive']).is_file(), (
                    f"missing zip {fm['zip_archive']}"
                )

    def test_regenerate_deletes_only_markdown_orphans(self, library_project_root):
        """Reqs 9–10: regenerate (prune simulation) deletes only .md; keeps other files."""
        bib = _write_corpus_bib(library_project_root)
        out = library_project_root / '_library'
        orphan_md = out / 'obsolete-orphan.md'
        orphan_md.write_text('---\ntitle: orphan\nbibtex_key: gone\n---\n', encoding='utf-8')
        keep_sidecar = out / 'notes.txt'
        keep_sidecar.write_text('do not delete', encoding='utf-8')
        keep_asset = out / 'readme.json'
        keep_asset.write_text('{"keep": true}', encoding='utf-8')

        _run_generator(library_project_root, bib, regenerate=False)
        assert orphan_md.exists()

        _run_generator(library_project_root, bib, regenerate=True)

        assert not orphan_md.exists(), 'Orphan markdown should be pruned on regenerate'
        assert keep_sidecar.exists(), 'Non-md sidecar must survive regenerate'
        assert keep_asset.exists(), 'Non-md asset must survive regenerate'
        assert keep_sidecar.read_text(encoding='utf-8') == 'do not delete'

        pages = list(out.glob('*.md'))
        assert len(pages) == 3
        keys = {_read_front_matter(p)['bibtex_key'] for p in pages}
        assert keys == {'alpha2023', 'beta2024', 'gamma2022'}
