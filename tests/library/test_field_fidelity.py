#!/usr/bin/env python3
"""
Field-fidelity tests for library front matter (reqs 21–36, 38).

Verifies exact copy of media fields, multi speakers/quotes order, website/url
canonicalisation, website_date rename survival, and abstract / empty-key rules.
"""

from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from processing.config import Configuration


def _parse_front_matter(fm_str: str) -> dict:
    assert fm_str.startswith('---\n')
    assert fm_str.endswith('---')
    return yaml.safe_load(fm_str[4:-3])


def _plant_preview(tmp_path: Path, filename: str) -> Path:
    preview_dir = tmp_path / 'publication_preview'
    preview_dir.mkdir(parents=True, exist_ok=True)
    path = preview_dir / filename
    path.write_bytes(b'\xff\xd8\xff')
    return preview_dir


@pytest.mark.library
@pytest.mark.rendering
class TestMediaFieldFidelity:
    """Reqs 21–25: exact copy of preview/pdf/agenda/slides/video into FM."""

    def test_pdf_agenda_slides_video_copied_exactly(self, content_generator):
        entry = {
            'ID': 'media2024',
            'ENTRYTYPE': 'misc',
            'type': 'misc',
            'title': 'Media Fields',
            'year': '2024',
            'month': '1',
            'pdf': 'exact_paper.pdf',
            'agenda': 'exact_agenda.pdf',
            'slides': 'exact_slides.pdf',
            'video': 'https://www.youtube.com/watch?v=exact123',
        }
        fm = _parse_front_matter(content_generator.generate_front_matter(entry))
        assert fm['pdf'] == 'exact_paper.pdf'
        assert fm['agenda'] == 'exact_agenda.pdf'
        assert fm['slides'] == 'exact_slides.pdf'
        assert fm['video'] == 'https://www.youtube.com/watch?v=exact123'

    def test_preview_stem_from_bib_when_file_exists(self, content_generator, tmp_path):
        preview_name = 'fidelity_preview_image.jpeg'
        preview_dir = _plant_preview(tmp_path, preview_name)
        entry = {
            'ID': 'preview2024',
            'ENTRYTYPE': 'article',
            'type': 'article',
            'title': 'Preview Fidelity',
            'year': '2024',
            'month': '2',
            'preview': preview_name,
        }
        with patch.object(Configuration, 'PREVIEW_DIR', str(preview_dir)), \
             patch.object(content_generator.config, 'PREVIEW_DIR', str(preview_dir)):
            fm = _parse_front_matter(content_generator.generate_front_matter(entry))
        assert fm['preview'] == 'fidelity_preview_image'


@pytest.mark.library
@pytest.mark.rendering
class TestSpeakersRoleQuotesFidelity:
    """Reqs 26–28: multi speakers/quotes order and role fidelity."""

    def test_speakers_and_quotes_preserve_order(self, content_generator):
        entry = {
            'ID': 'panel2024',
            'ENTRYTYPE': 'misc',
            'type': 'misc',
            'title': 'Panel',
            'year': '2024',
            'month': '3',
            'annote': (
                '[quotes]\n'
                'First quotation about oceans.\n'
                'Second quotation about biodiversity.\n'
                'Third quotation about governance.\n'
                '[role]\n'
                'facilitator\n'
                '[speakers]\n'
                'Alice Alpha, Institute A\n'
                'Bob Beta, Institute B\n'
                'Carol Gamma, Institute C\n'
                '[type]\n'
                'conference'
            ),
        }
        fm = _parse_front_matter(content_generator.generate_front_matter(entry))
        assert fm['role'] == 'facilitator'
        assert fm['speakers'] == [
            'Alice Alpha, Institute A',
            'Bob Beta, Institute B',
            'Carol Gamma, Institute C',
        ]
        assert fm['quotes'] == [
            'First quotation about oceans.',
            'Second quotation about biodiversity.',
            'Third quotation about governance.',
        ]


@pytest.mark.library
@pytest.mark.rendering
class TestWebsiteUrlCanonicalisation:
    """Reqs 29, 31–33: website/url canonicalisation and website_date survival."""

    def test_website_is_canonical_via_extract_links(self, bib_parser, content_generator):
        entry = {
            'ID': 'web2024',
            'ENTRYTYPE': 'article',
            'type': 'article',
            'title': 'Website Canonical',
            'year': '2024',
            'month': '4',
            'website': 'https://example.com/canonical',
        }
        links = bib_parser.extract_links(entry)
        assert links['url'] == 'https://example.com/canonical'
        fm = _parse_front_matter(content_generator.generate_front_matter(entry))
        assert fm['url'] == 'https://example.com/canonical'
        assert 'website' not in fm

    def test_notes_do_not_overwrite_website(self, bib_parser, content_generator):
        entry = {
            'ID': 'notesweb2024',
            'ENTRYTYPE': 'article',
            'type': 'article',
            'title': 'Notes vs Website',
            'year': '2024',
            'month': '5',
            'website': 'https://example.com/official',
            'note': 'See also https://example.com/from-notes and https://youtube.com/watch?v=abc',
        }
        links = bib_parser.extract_links(entry)
        assert links['url'] == 'https://example.com/official'
        fm = _parse_front_matter(content_generator.generate_front_matter(entry))
        assert fm['url'] == 'https://example.com/official'

    def test_url_and_website_do_not_duplicate_in_front_matter(
        self, bib_parser, content_generator
    ):
        entry = {
            'ID': 'both2024',
            'ENTRYTYPE': 'article',
            'type': 'article',
            'title': 'Both URL Fields',
            'year': '2024',
            'month': '6',
            'url': 'https://example.com/legacy-url',
            'website': 'https://example.com/website-preferred',
        }
        # extract_links prefers url when both present (url or website)
        links = bib_parser.extract_links(entry)
        assert links['url'] == 'https://example.com/legacy-url'
        fm = _parse_front_matter(content_generator.generate_front_matter(entry))
        assert list(fm.keys()).count('url') == 1
        assert 'website' not in fm
        assert fm['url'] == 'https://example.com/legacy-url'

    def test_website_date_survives_rename_url_fields(self, bibtex_processor):
        """Req 33: website_date survival via BibTeXProcessor.rename_url_fields."""
        content = """@article{dated2024,
    title = {Dated Entry},
    author = {Wright, Glen},
    year = {2024},
    url = {https://example.com/page},
    urldate = {2024-07-15}
}"""
        modified, count = bibtex_processor.rename_url_fields(content)
        assert count == 1
        assert 'website = {https://example.com/page}' in modified
        assert 'website_date = {2024-07-15}' in modified
        assert 'urldate' not in modified
        assert 'url = {' not in modified


@pytest.mark.library
@pytest.mark.rendering
class TestAbstractAndEmptyKeys:
    """Reqs 34–36, 38: abstract presence/omission and no empty optional YAML keys."""

    def test_nonempty_abstract_present(self, content_generator):
        entry = {
            'ID': 'abs2024',
            'ENTRYTYPE': 'article',
            'type': 'article',
            'title': 'Has Abstract',
            'year': '2024',
            'month': '7',
            'abstract': 'A substantive abstract about ocean governance.',
        }
        fm = _parse_front_matter(content_generator.generate_front_matter(entry))
        assert fm.get('abstract') == 'A substantive abstract about ocean governance.'

    def test_empty_and_whitespace_abstract_omitted(self, content_generator):
        for abstract in ('', '   ', '\t\n  '):
            entry = {
                'ID': 'emptyabs2024',
                'ENTRYTYPE': 'article',
                'type': 'article',
                'title': 'Empty Abstract',
                'year': '2024',
                'month': '8',
                'abstract': abstract,
            }
            fm = _parse_front_matter(content_generator.generate_front_matter(entry))
            assert 'abstract' not in fm, f'abstract={abstract!r} should be omitted'

    def test_missing_optional_fields_no_empty_yaml_keys(self, content_generator):
        entry = {
            'ID': 'sparse2024',
            'ENTRYTYPE': 'article',
            'type': 'article',
            'title': 'Sparse Entry',
            'year': '2024',
            'month': '9',
        }
        fm = _parse_front_matter(content_generator.generate_front_matter(entry))
        for key in (
            'abstract',
            'pdf',
            'agenda',
            'slides',
            'video',
            'preview',
            'speakers',
            'quotes',
            'role',
            'url',
            'doi',
            'venue',
            'institution',
            'publisher',
        ):
            if key in fm:
                value = fm[key]
                assert value not in (None, '', []), f'empty YAML key leaked: {key}={value!r}'
