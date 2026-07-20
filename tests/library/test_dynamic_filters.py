#!/usr/bin/env python3
"""
Tests for DynamicFiltersGenerator — entry types, roles, languages YAML for
library index filters.
"""

from pathlib import Path

import pytest
import yaml

from processing.library.dynamic_filters import DynamicFiltersGenerator


@pytest.mark.library
@pytest.mark.unit
class TestDynamicFiltersGenerator:
    def test_generate_filters_writes_yaml(self, library_project_root):
        entries = [
            {
                'ID': 'a1',
                'ENTRYTYPE': 'article',
                'annote': '[type]\nJournal Article\n[role]\nauthor\n[language]\nfrench',
            },
            {
                'ID': 'w1',
                'ENTRYTYPE': 'misc',
                'annote': '[type]\nwebinar\n[role]\nmoderator\nspeaker\n[language]\nspanish',
            },
            {
                'ID': 'b1',
                'ENTRYTYPE': 'book',
            },
        ]
        gen = DynamicFiltersGenerator(str(library_project_root))
        gen.generate_filters(entries)

        out = library_project_root / '_data' / 'dynamic_filters.yml'
        assert out.exists()
        data = yaml.safe_load(out.read_text(encoding='utf-8'))

        assert 'entry_types' in data
        assert 'role_tags' in data
        assert 'language_tags' in data
        assert 'entry_type_counts' in data
        assert 'role_tag_counts' in data
        assert 'language_tag_counts' in data

        assert 'french' in data['language_tags']
        assert 'spanish' in data['language_tags']
        assert 'author' in data['role_tags']
        assert 'moderator' in data['role_tags']
        assert data['role_tag_counts']['speaker'] == 1
        assert data['language_tag_counts']['french'] == 1

    def test_counts_are_exact_not_substring(self, library_project_root):
        """Book Chapter must not inflate Book counts."""
        entries = [
            {'ID': '1', 'ENTRYTYPE': 'book', 'annote': '[type]\nBook'},
            {'ID': '2', 'ENTRYTYPE': 'incollection', 'annote': '[type]\nBook Chapter'},
            {'ID': '3', 'ENTRYTYPE': 'incollection', 'annote': '[type]\nBook Chapter'},
        ]
        gen = DynamicFiltersGenerator(str(library_project_root))
        gen.generate_filters(entries)
        data = yaml.safe_load(
            (library_project_root / '_data' / 'dynamic_filters.yml').read_text()
        )
        assert data['entry_type_counts'].get('Book') == 1
        assert data['entry_type_counts'].get('Book Chapter') == 2

    def test_invalid_languages_filtered(self, library_project_root):
        entries = [{
            'ID': 'x',
            'ENTRYTYPE': 'misc',
            'annote': '[language]\nklingon\nfrench',
        }]
        gen = DynamicFiltersGenerator(str(library_project_root))
        gen.generate_filters(entries)
        data = yaml.safe_load(
            (library_project_root / '_data' / 'dynamic_filters.yml').read_text()
        )
        assert 'french' in data['language_tags']
        assert 'klingon' not in data['language_tags']

    def test_empty_entries_still_writes_file(self, library_project_root):
        gen = DynamicFiltersGenerator(str(library_project_root))
        gen.generate_filters([])
        data = yaml.safe_load(
            (library_project_root / '_data' / 'dynamic_filters.yml').read_text()
        )
        assert data['entry_types'] == []
        assert data['role_tags'] == []
        assert data['language_tags'] == []

    def test_find_entry_end_balanced_braces(self, library_project_root):
        gen = DynamicFiltersGenerator(str(library_project_root))
        content = '@article{key, title = {A {Nested} Title}, year = {2023}}'
        end = gen._find_entry_end(content, 0)
        assert end == len(content) - 1
        assert content[end] == '}'

    def test_parse_entry_fields(self, library_project_root):
        gen = DynamicFiltersGenerator(str(library_project_root))
        content = '@article{key,\n  title = {Hello},\n  year = {2023}\n}'
        fields = gen._parse_entry_fields(content)
        assert fields['title'] == 'Hello'
        assert fields['year'] == '2023'

    def test_load_entries_from_file(self, library_project_root, sample_library_bib_content):
        bib_dir = library_project_root / '_bibliography'
        bib_dir.mkdir(exist_ok=True)
        (bib_dir / 'papers.bib').write_text(sample_library_bib_content, encoding='utf-8')
        gen = DynamicFiltersGenerator(str(library_project_root))
        entries = gen._load_entries_from_file()
        assert len(entries) >= 4
        assert all('ID' in e and 'ENTRYTYPE' in e for e in entries)
