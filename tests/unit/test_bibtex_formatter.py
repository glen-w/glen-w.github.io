#!/usr/bin/env python3
"""
Unit tests for BibTeXFormatter — multi-line entry formatting and field parsing.
"""

import pytest

from processing.core.bibtex_formatter import BibTeXFormatter


@pytest.fixture
def formatter():
    return BibTeXFormatter()


@pytest.mark.unit
@pytest.mark.bibtex_syntax
class TestBibTeXFormatter:
    def test_format_entry_basic(self, formatter):
        result = formatter.format_entry('article', 'key2023', {
            'title': 'Test Title',
            'year': '2023',
        })
        assert result.startswith('@article{key2023,')
        assert '\ttitle = {Test Title},' in result
        assert '\tyear = {2023}' in result  # last field, no trailing comma
        assert result.endswith('}')

    def test_format_entry_preserves_existing_braces(self, formatter):
        result = formatter.format_entry('article', 'k', {
            'title': '{Already Braced}',
            'year': '2020',
        })
        assert 'title = {Already Braced},' in result

    def test_format_entry_unicode(self, formatter):
        # Title/author fields run through brace cleaning which ASCII-folds accents
        result = formatter.format_entry('article', 'fr2023', {
            'title': 'Biodiversité en haute mer',
            'author': 'Dupont, François',
        })
        assert 'Biodiversit' in result
        assert 'haute mer' in result
        assert 'Dupont' in result
        assert 'Fran' in result

    def test_format_entry_from_content(self, formatter):
        content = '@article{old, title = {T}, year = {2021}}'
        formatted = formatter.format_entry_from_content(content)
        assert '@article{old,' in formatted
        assert 'title' in formatted

    def test_empty_fields(self, formatter):
        result = formatter.format_entry('misc', 'empty', {})
        assert result == '@misc{empty,\n}'

    def test_special_characters_in_values(self, formatter):
        result = formatter.format_entry('article', 'spec', {
            'title': 'A & B: 50% {ok}',
            'url': 'https://example.com/path?q=1',
        })
        assert 'A & B' in result
        assert 'https://example.com/path?q=1' in result
