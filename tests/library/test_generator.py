#!/usr/bin/env python3
"""
Unit and workflow tests for LibraryPageGenerator.
"""

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from processing.library.generator import LibraryPageGenerator


@pytest.mark.library
@pytest.mark.unit
class TestLibraryPageGeneratorInit:
    def test_defaults_create_output_dir(self, library_bib_file, library_project_root):
        out = library_project_root / '_library'
        gen = LibraryPageGenerator(
            bib_file=str(library_bib_file),
            output_dir=str(out),
            skip_dynamic_filters=True,
        )
        assert out.exists()
        assert gen.test_mode is False
        assert gen.incremental is False

    def test_test_mode_flag(self, library_bib_file, library_project_root):
        gen = LibraryPageGenerator(
            bib_file=str(library_bib_file),
            output_dir=str(library_project_root / '_library'),
            test_mode=True,
            skip_dynamic_filters=True,
        )
        assert gen.test_mode is True


@pytest.mark.library
@pytest.mark.unit
class TestFilterAndFilename:
    def test_filter_test_entries_takes_five_most_recent(
        self, library_bib_file, library_project_root
    ):
        gen = LibraryPageGenerator(
            bib_file=str(library_bib_file),
            output_dir=str(library_project_root / '_library'),
            test_mode=True,
            skip_dynamic_filters=True,
        )
        entries = [
            {'title': f'T{i}', 'year': str(2000 + i)} for i in range(10)
        ]
        filtered = gen.filter_test_entries(entries)
        assert len(filtered) == 5
        years = [int(e['year']) for e in filtered]
        assert years == sorted(years, reverse=True)
        assert years[0] == 2009

    def test_filter_passthrough_when_not_test_mode(
        self, library_bib_file, library_project_root
    ):
        gen = LibraryPageGenerator(
            bib_file=str(library_bib_file),
            output_dir=str(library_project_root / '_library'),
            test_mode=False,
            skip_dynamic_filters=True,
        )
        entries = [{'title': 'A', 'year': '2020'}]
        assert gen.filter_test_entries(entries) is entries

    def test_filter_handles_invalid_years(
        self, library_bib_file, library_project_root
    ):
        gen = LibraryPageGenerator(
            bib_file=str(library_bib_file),
            output_dir=str(library_project_root / '_library'),
            test_mode=True,
            skip_dynamic_filters=True,
        )
        entries = [
            {'title': 'Bad', 'year': 'n/a'},
            {'title': 'Good', 'year': '2024'},
            {'title': 'Missing'},
        ]
        filtered = gen.filter_test_entries(entries)
        assert filtered[0]['title'] == 'Good'

    def test_generate_filename_includes_author_prefix(
        self, library_bib_file, library_project_root
    ):
        gen = LibraryPageGenerator(
            bib_file=str(library_bib_file),
            output_dir=str(library_project_root / '_library'),
            skip_dynamic_filters=True,
        )
        filename = gen.generate_filename({
            'author': 'Wright, Glen',
            'title': 'The Ocean Governance Challenge',
        })
        assert filename.endswith('.md')
        assert 'wright' in filename.lower()
        assert 'ocean' in filename.lower()
        # filler words removed
        assert '_the_' not in filename.lower()

    def test_generate_filename_untitled_fallback(
        self, library_bib_file, library_project_root
    ):
        gen = LibraryPageGenerator(
            bib_file=str(library_bib_file),
            output_dir=str(library_project_root / '_library'),
            skip_dynamic_filters=True,
        )
        filename = gen.generate_filename({'title': '', 'author': ''})
        assert 'untitled' in filename.lower()
        assert filename.endswith('.md')


@pytest.mark.library
@pytest.mark.unit
class TestGeneratePage:
    def test_generate_page_writes_front_matter(
        self, library_bib_file, library_project_root, sample_library_entry
    ):
        out = library_project_root / '_library'
        gen = LibraryPageGenerator(
            bib_file=str(library_bib_file),
            output_dir=str(out),
            skip_dynamic_filters=True,
        )
        filepath, skipped = gen.generate_page(sample_library_entry)
        assert skipped is False
        assert os.path.isfile(filepath)
        text = Path(filepath).read_text(encoding='utf-8')
        assert text.startswith('---\n')
        parts = text.split('---', 2)
        fm = yaml.safe_load(parts[1])
        assert fm['layout'] == 'library-item'
        assert fm['bibtex_key'] == 'wright2023ocean'

    def test_incremental_skips_existing(
        self, library_bib_file, library_project_root, sample_library_entry
    ):
        out = library_project_root / '_library'
        gen = LibraryPageGenerator(
            bib_file=str(library_bib_file),
            output_dir=str(out),
            skip_dynamic_filters=True,
            incremental=True,
        )
        path1, skipped1 = gen.generate_page(sample_library_entry)
        assert skipped1 is False
        mtime1 = os.path.getmtime(path1)

        path2, skipped2 = gen.generate_page(sample_library_entry)
        assert skipped2 is True
        assert path2 == path1
        assert os.path.getmtime(path2) == mtime1

    def test_regenerate_cleans_markdown_files(
        self, library_bib_file, library_project_root
    ):
        out = library_project_root / '_library'
        stale = out / 'stale.md'
        stale.write_text('old', encoding='utf-8')
        (out / 'keep.txt').write_text('not md', encoding='utf-8')

        gen = LibraryPageGenerator(
            bib_file=str(library_bib_file),
            output_dir=str(out),
            skip_dynamic_filters=True,
            regenerate=True,
        )
        gen.cleanup_existing_files()
        assert not stale.exists()
        assert (out / 'keep.txt').exists()


@pytest.mark.library
@pytest.mark.unit
@pytest.mark.requires_bibtexparser
class TestLoadBibliography:
    def test_load_bibliography_parses_entries(
        self, library_bib_file, library_project_root
    ):
        gen = LibraryPageGenerator(
            bib_file=str(library_bib_file),
            output_dir=str(library_project_root / '_library'),
            skip_dynamic_filters=True,
        )
        entries = gen.load_bibliography()
        assert len(entries) >= 4
        ids = {e.get('ID') for e in entries}
        assert 'wright2023ocean' in ids
        assert 'webinar2024bbnj' in ids

    def test_load_bibliography_dedupes_duplicate_keys(
        self, library_project_root, tmp_path
    ):
        bib = tmp_path / 'dupes.bib'
        bib.write_text(
            """@inproceedings{Wright2011,
  title = {Marine Energy},
  year = {2011}
}

@inproceedings{Wright2011,
  title = {Marine Energy},
  year = {2011},
  pdf = {x.pdf}
}

@article{Wright2014,
  title = {Paper One},
  year = {2014}
}

@techreport{Wright2014,
  title = {Paper Two},
  year = {2014}
}
""",
            encoding='utf-8',
        )
        gen = LibraryPageGenerator(
            bib_file=str(bib),
            output_dir=str(library_project_root / '_library'),
            skip_dynamic_filters=True,
        )
        entries = gen.load_bibliography()
        assert len(entries) == 3
        wright2011 = [e for e in entries if e['ID'] == 'Wright2011']
        assert len(wright2011) == 1
        assert wright2011[0].get('pdf') == 'x.pdf'
        assert sum(1 for e in entries if e['ID'] == 'Wright2014') == 2

    def test_load_bibliography_missing_file_exits(
        self, library_project_root
    ):
        gen = LibraryPageGenerator(
            bib_file=str(library_project_root / 'missing.bib'),
            output_dir=str(library_project_root / '_library'),
            skip_dynamic_filters=True,
        )
        with pytest.raises(SystemExit):
            gen.load_bibliography()

    def test_catalog_only_writes_json_not_pages(
        self, library_bib_file, library_project_root
    ):
        out = library_project_root / '_library'
        gen = LibraryPageGenerator(
            bib_file=str(library_bib_file),
            output_dir=str(out),
            catalog_only=True,
            skip_dynamic_filters=True,
        )
        gen.run()
        assert list(out.glob('*.md')) == []
        catalog_path = library_project_root / 'assets' / 'json' / 'library.json'
        catalog = json.loads(catalog_path.read_text(encoding='utf-8'))
        assert catalog['v'] == 1
        assert catalog['items']
