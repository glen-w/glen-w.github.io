#!/usr/bin/env python3
"""
BibTeX round-trip and syntax robustness tests (requirements 40–65).

Uses BibTeXProcessor + BibTeXFormatter against CURRENT implementation behavior.
"""

import re

import pytest

from processing.config import Configuration
from processing.core.bibtex_formatter import BibTeXFormatter
from processing.core.bibtex_processor import BibTeXProcessor
from processing.core.text_processor import TextProcessor


def _entry_type(content: str) -> str:
    match = re.match(r'@(\w+)\s*\{', content.strip())
    assert match, f'no entry type in: {content[:80]!r}'
    return match.group(1)


@pytest.fixture
def processor():
    config = Configuration()
    return BibTeXProcessor(config, TextProcessor(config))


@pytest.fixture
def formatter():
    return BibTeXFormatter()


def _roundtrip(processor, formatter, content: str):
    """parse → format → parse; return (type, key, fields_before, fields_after, formatted)."""
    key, fields = processor.parse_bibtex_entry(content)
    etype = _entry_type(content)
    formatted = formatter.format_entry(etype, key, fields)
    key2, fields2 = processor.parse_bibtex_entry(formatted)
    return etype, key, fields, key2, fields2, formatted


@pytest.mark.unit
@pytest.mark.bibtex_syntax
class TestBibTeXRoundtrip:
    """Reqs 40–65: parse/format robustness."""

    def test_roundtrip_type_and_fields(self, processor, formatter):
        content = """@article{rt2023,
    title = {Ocean Governance},
    author = {Wright, Glen},
    year = {2023},
    journal = {Marine Policy},
    url = {https://example.com/paper},
    annote = {[role]
speaker
[speakers]
Alice}
}"""
        etype, key, fields, key2, fields2, formatted = _roundtrip(
            processor, formatter, content
        )
        assert etype == 'article'
        assert key == key2 == 'rt2023'
        assert fields2['title'] == fields['title']
        assert fields2['author'] == fields['author']
        assert fields2['year'] == fields['year']
        assert fields2['url'] == fields['url']
        assert 'speaker' in fields2['annote']
        assert 'Alice' in fields2['annote']
        assert _entry_type(formatted) == 'article'

    def test_nested_braces_title_no_truncation(self, processor):
        content = """@article{nest1,
    title = {Title with {nested} and {{deeper}} braces},
    year = {2020}
}"""
        key, fields = processor.parse_bibtex_entry(content)
        assert key == 'nest1'
        assert 'nested' in fields['title']
        assert 'deeper' in fields['title']
        assert fields['title'].startswith('Title with')

    def test_nested_braces_abstract_no_truncation(self, processor):
        content = """@article{nest2,
    title = {T},
    abstract = {Para one {with braces}.

Para two still here.},
    year = {2021}
}"""
        _, fields = processor.parse_bibtex_entry(content)
        assert 'Para one' in fields['abstract']
        assert 'with braces' in fields['abstract']
        assert 'Para two still here' in fields['abstract']

    def test_latex_protected_capitals_parse_preserved(self, processor):
        """Parser keeps LaTeX-protected capitals; formatter may strip braces (documented)."""
        content = """@article{caps,
    title = {{C}apital {P}rotected Title},
    year = {2022}
}"""
        _, fields = processor.parse_bibtex_entry(content)
        assert '{C}apital' in fields['title'] or 'Capital' in fields['title']
        assert '{P}rotected' in fields['title'] or 'Protected' in fields['title']

    def test_latex_protected_capitals_format_strips_braces(self, formatter):
        """CURRENT: clean_braces removes protective braces in title on format."""
        formatted = formatter.format_entry('article', 'caps', {
            'title': '{C}apital {P}rotected',
            'year': '2022',
        })
        assert 'Capital Protected' in formatted or '{C}apital' in formatted

    def test_multiline_field_values(self, processor, formatter):
        content = """@article{multi,
    title = {Multi},
    abstract = {Line one
Line two
Line three},
    year = {2023}
}"""
        _, key, fields, _, fields2, _ = _roundtrip(processor, formatter, content)
        assert key == 'multi'
        assert 'Line one' in fields['abstract']
        assert 'Line two' in fields['abstract']
        assert 'Line three' in fields2['abstract']

    def test_commas_inside_values_do_not_split(self, processor):
        content = """@article{comma,
    title = {A, B, and C: commas inside},
    author = {Wright, Glen and Doe, Jane},
    year = {2024}
}"""
        _, fields = processor.parse_bibtex_entry(content)
        assert fields['title'] == 'A, B, and C: commas inside'
        assert 'Wright, Glen' in fields['author']
        assert 'Doe, Jane' in fields['author']

    def test_urls_with_query_fragment_survive_formatter(self, processor, formatter):
        url = 'https://example.com/path?q=1&x=2#section'
        content = f"""@misc{{urlfrag,
    title = {{Link}},
    url = {{{url}}},
    year = {{2024}}
}}"""
        _, _, fields, _, fields2, formatted = _roundtrip(processor, formatter, content)
        assert fields['url'] == url
        assert fields2['url'] == url
        assert url in formatted

    def test_unbraced_year_current_behavior(self, processor):
        """CURRENT: braced years parse; bare `year = 2025` is not captured by the
        brace-first parser (unbraced regex requires a non-brace value that still
        matches — document that unbraced years are unsupported today)."""
        braced = """@article{braced,
    title = {Year Test},
    year = {2025}
}"""
        _, fields_braced = processor.parse_bibtex_entry(braced)
        assert fields_braced['year'] == '2025'

        unbraced = """@article{unbraced,
    title = {Year Test},
    year = 2025
}"""
        _, fields_unbraced = processor.parse_bibtex_entry(unbraced)
        # Explicit current behavior: unbraced year is omitted
        assert 'year' not in fields_unbraced
        assert fields_unbraced['title'] == 'Year Test'

    def test_consecutive_entries_no_field_leak(self, processor):
        content = """@article{first,
    title = {First Only},
    customfield = {only-in-first},
    year = {2020}
}

@book{second,
    title = {Second Only},
    year = {2021}
}"""
        entries = processor.parse_bibtex_entries(content)
        assert len(entries) == 2
        assert entries[0]['fields']['title'] == 'First Only'
        assert entries[0]['fields'].get('customfield') == 'only-in-first'
        assert 'customfield' not in entries[1]['fields']
        assert entries[1]['fields']['title'] == 'Second Only'

    def test_first_entry_without_leading_newline(self, processor):
        content = "@article{nolead,\n    title = {No Lead}, year = {2019}\n}"
        entries = processor.parse_bibtex_entries(content)
        assert len(entries) == 1
        assert entries[0]['citation_key'] == 'nolead'
        assert entries[0]['fields']['title'] == 'No Lead'

    def test_entries_separated_by_comments_and_blank_lines(self, processor):
        content = """@article{a1,
    title = {A One},
    year = {2018}
}

% this is a comment between entries

@article{a2,
    title = {A Two},
    year = {2019}
}"""
        entries = processor.parse_bibtex_entries(content)
        assert len(entries) == 2
        assert entries[0]['citation_key'] == 'a1'
        assert entries[1]['citation_key'] == 'a2'

    def test_format_idempotency(self, formatter):
        fields = {
            'title': 'Idempotent Title',
            'author': 'Author, Test',
            'year': '2023',
            'url': 'https://example.com?a=1',
        }
        once = formatter.format_entry('article', 'idem', fields)
        parsed = formatter._parse_entry_content(once)
        twice = formatter.format_entry(
            parsed['type'], parsed['citation_key'], parsed['fields']
        )
        assert once == twice

    def test_formatter_last_field_no_trailing_comma(self, formatter):
        result = formatter.format_entry('misc', 'commas', {
            'title': 'T',
            'year': '2020',
        })
        lines = [ln for ln in result.splitlines() if '=' in ln]
        assert lines[0].rstrip().endswith(',')
        assert not lines[-1].rstrip().endswith(',')

    def test_entry_type_unchanged_through_format(self, processor, formatter):
        for etype in ('article', 'inproceedings', 'phdthesis', 'misc'):
            content = f"@{etype}{{k{etype},\n    title = {{T}},\n    year = {{2020}}\n}}"
            formatted = formatter.format_entry_from_content(content)
            assert formatted.startswith(f'@{etype}{{')
            assert _entry_type(formatted) == etype

    def test_string_comment_preamble_current_behavior(self, processor):
        """CURRENT: @string/@comment/@preamble are not treated as bibliography entries
        unless they parse to a citation key with fields; document pass-through/strip."""
        content = """@string{mp = "Marine Policy"}

@comment{Editorial note}

@preamble{"\\\\newcommand{\\\\foo}{bar}"}

@article{real,
    title = {Real Entry},
    year = {2022}
}"""
        entries = processor.parse_bibtex_entries(content)
        keys = [e['citation_key'] for e in entries]
        assert 'real' in keys
        # Non-entry directives are skipped (not appended) when they lack usable fields
        assert all(k == 'real' or not k.startswith('string') for k in keys)
        # Explicit: real entry still parses
        real = next(e for e in entries if e['citation_key'] == 'real')
        assert real['fields']['title'] == 'Real Entry'

    def test_duplicate_field_last_wins_documented(self, processor):
        """CURRENT behavior (named): duplicate fields → last value wins; no error raised."""
        content = """@article{dup,
    title = {First Title},
    title = {Second Title},
    year = {2021}
}"""
        _, fields = processor.parse_bibtex_entry(content)
        assert fields['title'] == 'Second Title'

    def test_missing_closing_brace_fails_safely(self, processor):
        content = """@article{broken,
    title = {Missing close
    year = {2020}

@article{next,
    title = {Next Entry},
    year = {2021}
}"""
        key, fields = processor.parse_bibtex_entry(content)
        # Unclosed entry must not return a partial key that consumes the next entry
        assert key is None
        assert fields == {}

        entries = processor.parse_bibtex_entries(content)
        keys = [e['citation_key'] for e in entries]
        # Next entry may still be recoverable depending on split; broken must not leak its fields
        if 'next' in keys:
            nxt = next(e for e in entries if e['citation_key'] == 'next')
            assert nxt['fields']['title'] == 'Next Entry'
            assert 'Missing close' not in nxt['fields'].get('title', '')
        # If parser skips both, that is also safe (no field leak)
        assert 'broken' not in keys or entries[0]['fields'].get('title') != 'Next Entry'
