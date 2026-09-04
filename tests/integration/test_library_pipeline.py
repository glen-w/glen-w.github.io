#!/usr/bin/env python3
"""
Integration tests for the full library generation + content rendering pipeline:
BibTeX → pages → dynamic filters → front-matter contracts for Liquid layouts.
"""

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from processing.library.generator import LibraryPageGenerator
from processing.library.dynamic_filters import DynamicFiltersGenerator


def _read_front_matter(path: Path) -> dict:
    text = path.read_text(encoding='utf-8')
    assert text.startswith('---')
    parts = text.split('---', 2)
    return yaml.safe_load(parts[1])


@pytest.mark.library
@pytest.mark.integration
@pytest.mark.requires_bibtexparser
class TestLibraryPipelineEndToEnd:
    def test_run_generates_pages_and_filters(
        self, library_bib_file, library_project_root
    ):
        out = library_project_root / '_library'
        gen = LibraryPageGenerator(
            bib_file=str(library_bib_file),
            output_dir=str(out),
            skip_dynamic_filters=False,
        )

        # Point dynamic filters at the temp project root via output_dir parent
        # (generator uses dirname(output_dir) as project root)
        gen.run()

        md_files = list(out.glob('*.md'))
        assert len(md_files) >= 4

        filters_path = library_project_root / '_data' / 'dynamic_filters.yml'
        assert filters_path.exists()
        filters = yaml.safe_load(filters_path.read_text(encoding='utf-8'))
        assert len(filters['entry_types']) >= 1

        catalog_path = library_project_root / 'assets' / 'json' / 'library.json'
        assert catalog_path.exists()
        catalog = json.loads(catalog_path.read_text(encoding='utf-8'))
        assert len(catalog['items']) == len(md_files)

    def test_test_mode_limits_to_five(
        self, library_bib_file, library_project_root
    ):
        out = library_project_root / '_library'
        # Expand bib so there are more than 5 entries
        extra = '\n'.join(
            f'@article{{extra{i},\n  title = {{Extra {i}}},\n  author = {{Author}},\n  year = {{{2010 + i}}}\n}}'
            for i in range(10)
        )
        library_bib_file.write_text(
            library_bib_file.read_text(encoding='utf-8') + '\n' + extra,
            encoding='utf-8',
        )

        gen = LibraryPageGenerator(
            bib_file=str(library_bib_file),
            output_dir=str(out),
            test_mode=True,
            skip_dynamic_filters=True,
        )
        gen.run()
        assert len(list(out.glob('*.md'))) == 5

    def test_incremental_second_run_skips(
        self, library_bib_file, library_project_root, capsys
    ):
        out = library_project_root / '_library'
        gen = LibraryPageGenerator(
            bib_file=str(library_bib_file),
            output_dir=str(out),
            skip_dynamic_filters=True,
            incremental=True,
        )
        gen.run()
        first_count = len(list(out.glob('*.md')))
        gen.run()
        captured = capsys.readouterr().out
        assert 'Skipped' in captured or 'skipped' in captured.lower()
        assert len(list(out.glob('*.md'))) == first_count

    def test_regenerate_replaces_stale_pages(
        self, library_bib_file, library_project_root
    ):
        out = library_project_root / '_library'
        stale = out / 'obsolete-page.md'
        stale.write_text('---\ntitle: stale\n---\n', encoding='utf-8')

        gen = LibraryPageGenerator(
            bib_file=str(library_bib_file),
            output_dir=str(out),
            skip_dynamic_filters=True,
            regenerate=True,
        )
        gen.run()
        assert not stale.exists()
        assert len(list(out.glob('*.md'))) >= 4


@pytest.mark.library
@pytest.mark.integration
@pytest.mark.rendering
class TestFrontMatterLiquidContract:
    """Assert front-matter shape expected by library-item layout / includes."""

    REQUIRED_KEYS = {'layout', 'title', 'date', 'entry_type', 'year', 'bibtex_key', 'is_event'}

    def test_every_generated_page_has_required_keys(
        self, library_bib_file, library_project_root
    ):
        out = library_project_root / '_library'
        gen = LibraryPageGenerator(
            bib_file=str(library_bib_file),
            output_dir=str(out),
            skip_dynamic_filters=True,
        )
        gen.run()

        for path in out.glob('*.md'):
            fm = _read_front_matter(path)
            missing = self.REQUIRED_KEYS - set(fm.keys())
            assert not missing, f'{path.name} missing keys: {missing}'
            assert fm['layout'] == 'library-item'
            assert isinstance(fm['is_event'], bool)
            assert isinstance(fm['year'], (str, int))

    def test_resources_schema_when_present(
        self, library_bib_file, library_project_root, tmp_path
    ):
        # Create a real PDF so resources include a local pdf entry
        pdf_dir = library_project_root / 'assets' / 'pdf'
        pdf_dir.mkdir(parents=True, exist_ok=True)
        (pdf_dir / 'wright_2023_ocean_governance.pdf').write_bytes(b'%PDF')

        out = library_project_root / '_library'
        gen = LibraryPageGenerator(
            bib_file=str(library_bib_file),
            output_dir=str(out),
            skip_dynamic_filters=True,
        )

        # Patch ContentGenerator config paths to the temp project
        from processing.config import Configuration
        with patch.object(Configuration, 'PDF_DIR', str(pdf_dir)), \
             patch.object(Configuration, 'PREVIEW_DIR', str(library_project_root / 'assets' / 'img' / 'publication_preview')), \
             patch.object(Configuration, 'IMAGES_DIR', str(library_project_root / 'assets' / 'img' / 'publications')), \
             patch.object(Configuration, 'ZIP_DIR', str(library_project_root / 'assets' / 'zips')):
            # Re-bind content generator after patch
            gen.content_generator = type(gen.content_generator)()
            gen.run()

        found_resources = False
        for path in out.glob('*.md'):
            fm = _read_front_matter(path)
            if 'resources' not in fm:
                continue
            found_resources = True
            for resource in fm['resources']:
                assert 'kind' in resource
                assert 'url' in resource
                assert 'label' in resource
                assert 'title' in resource
                assert resource['kind'] in {
                    'pdf', 'agenda', 'slides', 'poster', 'zip', 'video', 'landing'
                }
        assert found_resources, 'Expected at least one page with resources'

    def test_event_pages_flag_is_event(
        self, library_bib_file, library_project_root
    ):
        out = library_project_root / '_library'
        gen = LibraryPageGenerator(
            bib_file=str(library_bib_file),
            output_dir=str(out),
            skip_dynamic_filters=True,
        )
        gen.run()

        event_pages = []
        for path in out.glob('*.md'):
            fm = _read_front_matter(path)
            if fm.get('is_event'):
                event_pages.append(fm)
        assert len(event_pages) >= 1
        for fm in event_pages:
            # Events should typically have a landing or video when present in bib
            assert fm['entry_type']


@pytest.mark.library
@pytest.mark.integration
class TestDynamicFiltersWithGeneratorEntries:
    def test_filters_reflect_generated_entry_set(self, library_project_root):
        entries = [
            {
                'ID': 'a',
                'ENTRYTYPE': 'article',
                'annote': '[type]\nJournal Article\n[role]\nauthor\n[language]\ncatalan',
            },
            {
                'ID': 'b',
                'ENTRYTYPE': 'misc',
                'annote': '[type]\nWorkshop\n[role]\norganiser\n[language]\nchinese',
            },
        ]
        DynamicFiltersGenerator(str(library_project_root)).generate_filters(entries)
        data = yaml.safe_load(
            (library_project_root / '_data' / 'dynamic_filters.yml').read_text()
        )
        assert 'Journal Article' in data['entry_types']
        assert 'Workshop' in data['entry_types']
        assert 'author' in data['role_tags']
        assert 'organiser' in data['role_tags']
        assert set(data['language_tags']) >= {'catalan', 'chinese'}
        assert sum(data['entry_type_counts'].values()) == 2
