#!/usr/bin/env python3
"""
Comprehensive tests for ContentGenerator — YAML front matter and body content
that drive library-item Liquid rendering.
"""

import os
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from processing.library.content_generator import ContentGenerator


def _parse_front_matter(fm_str: str) -> dict:
    assert fm_str.startswith('---\n')
    assert fm_str.endswith('---')
    body = fm_str[4:-3]
    return yaml.safe_load(body)


@pytest.mark.library
@pytest.mark.rendering
@pytest.mark.unit
class TestFrontMatterBasics:
    def test_required_layout_and_keys(self, content_generator, sample_library_entry):
        fm = _parse_front_matter(
            content_generator.generate_front_matter(sample_library_entry)
        )
        assert fm['layout'] == 'library-item'
        assert fm['title'] == 'Ocean Governance Beyond National Jurisdiction'
        assert fm['bibtex_key'] == 'wright2023ocean'
        assert fm['year'] == '2023'
        assert fm['date'] == '2023-06-01'
        assert fm['entry_type'] == 'Journal Article'
        assert fm['is_event'] is False

    def test_authors_tags_categories(self, content_generator, sample_library_entry):
        fm = _parse_front_matter(
            content_generator.generate_front_matter(sample_library_entry)
        )
        assert 'Glen Wright' in fm['authors']
        assert 'Jane Doe' in fm['authors']
        assert 'ocean' in fm['tags']
        assert 'publications' in fm['categories']
        assert 'ocean-governance' in fm['categories']
        assert 'biodiversity' in fm['categories']

    def test_venue_location_institution(self, content_generator, sample_library_entry):
        fm = _parse_front_matter(
            content_generator.generate_front_matter(sample_library_entry)
        )
        assert fm['venue'] == 'Marine Policy'
        assert fm['location'] == 'Paris, France'
        assert fm['institution'] == 'IDDRI'

    def test_legacy_link_fields(self, content_generator, sample_library_entry):
        fm = _parse_front_matter(
            content_generator.generate_front_matter(sample_library_entry)
        )
        assert fm['url'] == 'https://example.com/ocean-governance'
        assert fm['doi'] == 'https://doi.org/10.1000/mp.2023.001'
        assert fm['pdf'] == 'wright_2023_ocean_governance.pdf'

    def test_role_speakers_quotes_from_annote(
        self, content_generator, sample_library_entry
    ):
        fm = _parse_front_matter(
            content_generator.generate_front_matter(sample_library_entry)
        )
        assert fm['role'] == 'author'
        assert fm['speakers'] == ['Alice Expert']
        assert fm['quotes'] == ['Ocean governance matters']

    def test_unicode_title_preserved(self, content_generator):
        entry = {
            'ID': 'unicode2023',
            'type': 'article',
            'title': 'Biodiversité en haute mer — traité',
            'author': 'Dupont, François',
            'year': '2023',
            'month': '01',
        }
        fm = _parse_front_matter(content_generator.generate_front_matter(entry))
        assert 'Biodiversité' in fm['title']
        assert 'François' in fm['authors'][0] or 'Dupont' in fm['authors'][0]


@pytest.mark.library
@pytest.mark.rendering
@pytest.mark.unit
class TestEventDetection:
    def test_webinar_is_event(self, content_generator, sample_event_entry):
        fm = _parse_front_matter(
            content_generator.generate_front_matter(sample_event_entry)
        )
        assert fm['is_event'] is True
        assert fm['entry_type'].lower() in {'webinar', 'webinar'}

    def test_conference_paper_maps_to_event(self, content_generator):
        assert content_generator._compute_is_event('Conference Paper') is True
        assert content_generator._compute_is_event('Guest Lecture') is True
        assert content_generator._compute_is_event('Side Event') is True
        assert content_generator._compute_is_event('Journal Article') is False
        assert content_generator._compute_is_event('Report') is False

    def test_normalize_event_key_aliases(self, content_generator):
        assert content_generator._normalize_event_key('launch event') == 'event'
        assert content_generator._normalize_event_key('moderated') == 'panel'
        assert content_generator._normalize_event_key('organised') == 'event'
        assert content_generator._normalize_event_key('') is None


@pytest.mark.library
@pytest.mark.rendering
@pytest.mark.unit
class TestStandfirstAndDescription:
    def test_standfirst_from_description_field(self, content_generator):
        entry = {
            'ID': 'x',
            'type': 'article',
            'title': 'Title',
            'year': '2023',
            'month': '1',
            'description': (
                'A standfirst long enough to qualify as a real description '
                'for the page hero.'
            ),
        }
        fm = _parse_front_matter(content_generator.generate_front_matter(entry))
        assert 'standfirst long enough' in fm['standfirst']

    def test_standfirst_from_first_abstract_paragraph(self, content_generator):
        entry = {
            'ID': 'x',
            'type': 'article',
            'title': 'Title',
            'year': '2023',
            'month': '1',
            'abstract': (
                'First paragraph is long enough to become standfirst text here.\n\n'
                'Second paragraph should not appear in standfirst.'
            ),
        }
        fm = _parse_front_matter(content_generator.generate_front_matter(entry))
        assert 'First paragraph' in fm['standfirst']
        assert 'Second paragraph' not in fm['standfirst']

    def test_standfirst_capped_at_sentence_boundary(self, content_generator):
        long = ('Sentence one is short. ' * 5) + ('Word ' * 80)
        capped = content_generator._cap_standfirst(long)
        assert len(capped) <= content_generator.STANDFIRST_MAX_CHARS + 5
        assert capped.endswith('.') or capped.endswith('…')

    def test_plain_text_strips_html_and_markdown(self, content_generator):
        plain = content_generator._plain_text(
            '<p>Hello <b>world</b></p> with *emphasis* and {braces}'
        )
        assert '<' not in plain
        assert 'Hello' in plain
        assert 'world' in plain
        assert '*' not in plain


@pytest.mark.library
@pytest.mark.rendering
@pytest.mark.unit
class TestResources:
    def test_landing_and_video_resources_without_local_files(
        self, content_generator, sample_event_entry, tmp_path
    ):
        with patch.object(content_generator.config, 'PDF_DIR', str(tmp_path)):
            fm = _parse_front_matter(
                content_generator.generate_front_matter(sample_event_entry)
            )
        kinds = {r['kind'] for r in fm.get('resources', [])}
        assert 'landing' in kinds
        assert 'video' in kinds
        # Missing local PDF should be omitted with warning, not crash
        assert 'pdf' not in kinds

    def test_local_pdf_included_when_file_exists(
        self, content_generator, sample_library_entry, tmp_path
    ):
        pdf_dir = tmp_path / 'pdf'
        pdf_dir.mkdir()
        pdf_name = sample_library_entry['pdf']
        (pdf_dir / pdf_name).write_bytes(b'%PDF-1.4 fake')

        with patch.object(content_generator.config, 'PDF_DIR', str(pdf_dir)):
            fm = _parse_front_matter(
                content_generator.generate_front_matter(sample_library_entry)
            )

        pdf_resources = [r for r in fm['resources'] if r['kind'] == 'pdf']
        assert len(pdf_resources) == 1
        assert pdf_resources[0]['primary'] is True
        assert pdf_resources[0]['local'] is True
        assert pdf_resources[0]['url'] == f'/assets/pdf/{pdf_name}'
        assert pdf_resources[0]['label'] == 'View primary document'

    def test_report_pdf_label(self, content_generator):
        assert content_generator._pdf_action_label('Report') == 'View report PDF'
        assert content_generator._pdf_action_label('Journal Article') == 'View primary document'

    def test_landing_labels(self, content_generator):
        assert 'IDDRI' in content_generator._landing_label('IDDRI', False)
        assert content_generator._landing_label(None, True) == 'Visit event website'
        assert content_generator._landing_label(None, False) == 'Visit publication page'

    def test_dedupe_resources_prefers_more_specific_kind(self, content_generator):
        candidates = [
            {
                'kind': 'landing',
                'url': 'https://example.com/doc',
                'title': 'Landing',
                'label': 'Visit',
            },
            {
                'kind': 'agenda',
                'url': 'https://example.com/doc',
                'title': 'Agenda',
                'label': 'Agenda',
            },
        ]
        result = content_generator._dedupe_resources(candidates)
        assert len(result) == 1
        assert result[0]['kind'] == 'agenda'

    def test_dedupe_keeps_primary_when_upgrading_kind(self, content_generator):
        candidates = [
            {
                'kind': 'pdf',
                'url': 'https://example.com/same',
                'title': 'PDF',
                'label': 'PDF',
                'primary': True,
            },
            {
                'kind': 'agenda',
                'url': 'https://example.com/same',
                'title': 'Agenda',
                'label': 'Agenda',
            },
        ]
        result = content_generator._dedupe_resources(candidates)
        assert len(result) == 1
        assert result[0]['kind'] == 'agenda'
        assert result[0].get('primary') is True

    def test_format_from_filename(self, content_generator):
        assert content_generator._format_from_filename('a.pdf') == 'PDF'
        assert content_generator._format_from_filename('a.pptx') == 'PPTX'
        assert content_generator._format_from_filename('a.zip') == 'ZIP'
        assert content_generator._format_from_filename('a.unknown') == 'UNKNOWN'

    def test_zip_resource_with_metadata(self, content_generator, tmp_path):
        zip_dir = tmp_path / 'zips'
        zip_dir.mkdir()
        (zip_dir / 'bundle.zip').write_bytes(b'PK')
        entry = {
            'ID': 'z',
            'type': 'article',
            'title': 'T',
            'year': '2023',
            'month': '1',
            'zip_archive': 'bundle.zip',
            'zip_file_count': '3',
            'zip_file_size_mb': '12.5',
        }
        with patch.object(content_generator.config, 'ZIP_DIR', str(zip_dir)), \
             patch.object(content_generator.config, 'PDF_DIR', str(tmp_path)):
            fm = _parse_front_matter(content_generator.generate_front_matter(entry))
        assert fm['zip_archive'] == 'bundle.zip'
        zip_res = [r for r in fm['resources'] if r['kind'] == 'zip']
        assert len(zip_res) == 1
        assert '3 files' in zip_res[0]['subtitle']
        assert '12.5 MB' in zip_res[0]['subtitle']

    def test_missing_local_file_emits_warning(self, content_generator, capsys):
        entry = {
            'ID': 'missingpdf',
            'type': 'article',
            'title': 'Missing PDF Paper',
            'year': '2023',
            'month': '1',
            'pdf': 'does-not-exist.pdf',
        }
        with patch.object(content_generator.config, 'PDF_DIR', '/tmp/nonexistent-pdf-dir'):
            content_generator.generate_front_matter(entry)
        assert any('Missing local pdf' in w for w in content_generator.warnings)


@pytest.mark.library
@pytest.mark.rendering
@pytest.mark.unit
class TestCategoriesAndDates:
    def test_categories_by_entry_type(self, content_generator):
        assert 'publications' in content_generator._determine_categories(
            {'type': 'article'}, []
        )
        assert 'conferences' in content_generator._determine_categories(
            {'type': 'inproceedings'}, []
        )
        assert 'theses' in content_generator._determine_categories(
            {'type': 'phdthesis'}, []
        )
        assert 'reports' in content_generator._determine_categories(
            {'type': 'techreport'}, []
        )
        assert 'events' in content_generator._determine_categories(
            {'type': 'misc'}, ['blog']
        )
        assert 'other' in content_generator._determine_categories(
            {'type': 'misc'}, ['random']
        )

    def test_topic_keywords_add_categories(self, content_generator):
        cats = content_generator._determine_categories(
            {'type': 'article'}, ['climate change', 'renewable', 'marine policy']
        )
        assert 'climate-change' in cats
        assert 'renewable-energy' in cats
        assert 'marine-policy' in cats

    def test_topic_keyword_energy_maps_before_renewable_substring(
        self, content_generator
    ):
        # First matching topic wins per keyword (energy before renewable in dict order)
        cats = content_generator._determine_categories(
            {'type': 'article'}, ['renewable energy']
        )
        assert 'energy-policy' in cats
        assert 'publications' in cats

    def test_build_date_str_month_names(self, content_generator):
        assert content_generator._build_date_str('2024', 'mar') == '2024-03-01'
        assert content_generator._build_date_str('2024', 'September') == '2024-09-01'
        assert content_generator._build_date_str('2024', '9') == '2024-09-01'

    def test_build_date_str_invalid_falls_back(self, content_generator):
        assert content_generator._build_date_str('bad', 'xx') == 'bad-01-01'


@pytest.mark.library
@pytest.mark.rendering
@pytest.mark.unit
class TestPreviewAndGallery:
    def test_resolve_preview_from_existing_file(
        self, content_generator, tmp_path
    ):
        preview_dir = tmp_path / 'previews'
        preview_dir.mkdir()
        (preview_dir / 'cover.jpeg').write_bytes(b'fake')
        entry = {'preview': 'cover.jpeg', 'ID': 'x'}
        with patch.object(content_generator.config, 'PREVIEW_DIR', str(preview_dir)):
            result = content_generator._resolve_preview(entry, [])
        assert result == 'cover'

    def test_resolve_preview_falls_back_to_gallery(self, content_generator, tmp_path):
        with patch.object(content_generator.config, 'PREVIEW_DIR', str(tmp_path)):
            result = content_generator._resolve_preview({}, ['gallery_photo_1'])
        assert result == 'gallery_photo_1'

    def test_gallery_excludes_thumbnails(self, content_generator, tmp_path):
        entry = {
            'ID': 'g',
            'type': 'article',
            'title': 'G',
            'year': '2023',
            'month': '1',
            'author': 'Wright, Glen',
        }
        with patch.object(
            content_generator, '_find_processed_images',
            return_value=['img_photo_1', 'img_thumbnail_x', 'img_figure_2']
        ), patch.object(content_generator.config, 'PDF_DIR', str(tmp_path)), \
           patch.object(content_generator.config, 'PREVIEW_DIR', str(tmp_path)), \
           patch.object(content_generator.config, 'IMAGES_DIR', str(tmp_path)):
            fm = _parse_front_matter(content_generator.generate_front_matter(entry))
        assert 'gallery' in fm
        assert 'img_photo_1' in fm['gallery']
        assert 'img_figure_2' in fm['gallery']
        assert all('thumbnail' not in g.lower() for g in fm['gallery'])

    def test_hero_preview_src_appends_jpeg_when_extension_missing(
        self, content_generator
    ):
        """Regression: stem-only preview must become a .jpeg URL for the hero img.

        Without this, the browser requests a path with no file and paints the alt
        text ("Cover image for …") as visible page content.
        """
        src = ContentGenerator.resolve_hero_preview_src(
            '2026_european_society_ecological_economics_16th_annual_conference'
        )
        assert src == (
            '/assets/img/publication_preview/'
            '2026_european_society_ecological_economics_16th_annual_conference.jpeg'
        )

    def test_hero_preview_src_preserves_existing_extension(self, content_generator):
        assert ContentGenerator.resolve_hero_preview_src('cover.jpg') == (
            '/assets/img/publication_preview/cover.jpg'
        )
        assert ContentGenerator.resolve_hero_preview_src('cover.png') == (
            '/assets/img/publication_preview/cover.png'
        )

    def test_hero_preview_src_keeps_remote_urls(self, content_generator):
        url = 'https://cdn.example.com/covers/item.jpeg'
        assert ContentGenerator.resolve_hero_preview_src(url) == url

    def test_hero_preview_src_empty_returns_none(self, content_generator):
        assert ContentGenerator.resolve_hero_preview_src(None) is None
        assert ContentGenerator.resolve_hero_preview_src('') is None
        assert ContentGenerator.resolve_hero_preview_src('   ') is None

    def test_stem_preview_resolves_to_existing_jpeg_on_disk(
        self, content_generator, tmp_path
    ):
        """End-to-end contract: generator stem + hero URL resolution → real file."""
        preview_dir = tmp_path / 'publication_preview'
        preview_dir.mkdir()
        stem = '2026_le_traite_sur_la_protection'
        (preview_dir / f'{stem}.jpeg').write_bytes(b'\xff\xd8\xff fake jpeg')

        entry = {
            'ID': 'traite2026',
            'type': 'article',
            'title': 'Le traite',
            'year': '2026',
            'month': '1',
            'preview': f'{stem}.jpeg',
        }
        with patch.object(content_generator.config, 'PREVIEW_DIR', str(preview_dir)), \
             patch.object(content_generator.config, 'PDF_DIR', str(tmp_path)), \
             patch.object(content_generator.config, 'IMAGES_DIR', str(tmp_path)):
            fm = _parse_front_matter(content_generator.generate_front_matter(entry))

        # Generator still emits the stem (legacy front-matter shape)
        assert fm['preview'] == stem

        # Naive path without extension must NOT exist (the original bug)
        naive = preview_dir / stem
        assert not naive.is_file()

        # Hero resolution must produce a path that exists on disk
        hero_src = ContentGenerator.resolve_hero_preview_src(fm['preview'])
        assert hero_src.endswith('.jpeg')
        assert ContentGenerator.preview_src_resolves_on_disk(
            fm['preview'], str(preview_dir)
        )

    def test_hero_liquid_still_appends_jpeg_for_extensionless_preview(self):
        """Guard the Liquid template so the Python helper and hero stay in sync."""
        hero = Path('_includes/library/hero.liquid').read_text(encoding='utf-8')
        assert "append: '.jpeg'" in hero or 'append: ".jpeg"' in hero
        assert 'preview_src' in hero
        assert 'Cover image for' in hero


@pytest.mark.library
@pytest.mark.rendering
@pytest.mark.unit
class TestBodyContent:
    def test_notes_section_emitted(self, content_generator):
        content = content_generator.generate_content({
            'note': 'Important observation.\nhttps://example.com/skip\nAnother line.',
        })
        assert '## Notes' in content
        assert 'Important observation.' in content
        assert 'Another line.' in content
        assert 'https://' not in content

    def test_empty_note_yields_empty_body(self, content_generator):
        assert content_generator.generate_content({}) == ''
        assert content_generator.generate_content({'note': 'https://only.url'}) == ''

    def test_helpers_strip_and_dedupe(self, content_generator):
        assert content_generator._strip_str('  hi  ') == 'hi'
        assert content_generator._strip_str('') is None
        assert content_generator._strip_str(None) is None
        assert content_generator._strip_str(['a']) is None
        assert content_generator._dedupe_list(['A', 'a', 'B']) == ['A', 'B']
