#!/usr/bin/env python3
"""
Comprehensive unit tests for BibParser — title/author/type/links/images helpers
used by library page generation.
"""

import pytest

from processing.library.bib_parser import BibParser


@pytest.mark.library
@pytest.mark.unit
class TestBibParserTitles:
    def test_clean_title_strips_braces(self, bib_parser):
        assert bib_parser.clean_title('{Ocean} Governance') == 'Ocean Governance'

    def test_clean_title_strips_quotes(self, bib_parser):
        assert bib_parser.clean_title('"Quoted Title"') == 'Quoted Title'
        assert bib_parser.clean_title("'Quoted Title'") == 'Quoted Title'

    def test_clean_title_empty_returns_untitled(self, bib_parser):
        assert bib_parser.clean_title('') == 'Untitled'
        assert bib_parser.clean_title(None) == 'Untitled'

    def test_clean_title_nested_braces(self, bib_parser):
        # Single-pass brace strip: outer braces first leaves inner remnant braces
        cleaned = bib_parser.clean_title('{A {Nested} Title}')
        assert 'Nested' in cleaned
        assert cleaned != '{A {Nested} Title}'


@pytest.mark.library
@pytest.mark.unit
class TestBibParserAuthors:
    def test_format_authors_last_first(self, bib_parser):
        authors = bib_parser.format_authors({'author': 'Wright, Glen and Doe, Jane'})
        assert len(authors) == 2
        assert authors[0]['last'] == 'Wright'
        assert authors[0]['first'] == 'Glen'
        assert authors[1]['last'] == 'Doe'

    def test_format_authors_first_last(self, bib_parser):
        authors = bib_parser.format_authors({'author': 'Glen Wright'})
        assert authors[0]['first'] == 'Glen'
        assert authors[0]['last'] == 'Wright'

    def test_format_authors_single_name(self, bib_parser):
        authors = bib_parser.format_authors({'author': 'UNESCO'})
        assert authors[0]['first'] == 'UNESCO'
        assert authors[0]['last'] == ''

    def test_format_authors_empty(self, bib_parser):
        assert bib_parser.format_authors({}) == []
        assert bib_parser.format_authors({'author': ''}) == []

    def test_format_authors_field_alias(self, bib_parser):
        authors = bib_parser.format_authors({'authors': 'Smith, Alice'})
        assert len(authors) == 1
        assert authors[0]['last'] == 'Smith'


@pytest.mark.library
@pytest.mark.unit
class TestBibParserEntryTypes:
    def test_standard_article_type(self, bib_parser):
        assert bib_parser.get_entry_type_display({'type': 'article'}) == 'Journal Article'

    def test_conference_type(self, bib_parser):
        assert bib_parser.get_entry_type_display({'type': 'inproceedings'}) == 'Conference Paper'

    def test_custom_type_from_annote(self, bib_parser):
        entry = {'type': 'misc', 'annote': '[type]\nPolicy Brief\n[role]\nauthor'}
        assert bib_parser.get_entry_type_display(entry) == 'Policy brief'

    def test_custom_type_from_keywords(self, bib_parser):
        entry = {'type': 'misc', 'keywords': 'custom_type: briefing note, ocean'}
        assert bib_parser.get_entry_type_display(entry) == 'Briefing Note'

    def test_keyword_role_overrides(self, bib_parser):
        assert bib_parser.get_entry_type_display(
            {'type': 'misc', 'keywords': 'moderator, event'}
        ) == 'moderated'
        assert bib_parser.get_entry_type_display(
            {'type': 'misc', 'keywords': 'organiser'}
        ) == 'organized'
        assert bib_parser.get_entry_type_display(
            {'type': 'misc', 'keywords': 'panellist'}
        ) == 'panel'
        assert bib_parser.get_entry_type_display(
            {'type': 'misc', 'keywords': 'workshop'}
        ) == 'workshop'
        assert bib_parser.get_entry_type_display(
            {'type': 'misc', 'keywords': 'side event'}
        ) == 'Side Event'
        assert bib_parser.get_entry_type_display(
            {'type': 'misc', 'keywords': 'policy brief'}
        ) == 'Policy Brief'
        assert bib_parser.get_entry_type_display(
            {'type': 'misc', 'keywords': 'attendee'}
        ) == 'attendance'

    def test_unknown_type_title_cased(self, bib_parser):
        assert bib_parser.get_entry_type_display({'type': 'dataset'}) == 'Dataset'

    def test_missing_type_defaults_to_other(self, bib_parser):
        assert bib_parser.get_entry_type_display({}) == 'Other'


@pytest.mark.library
@pytest.mark.unit
class TestBibParserDates:
    def test_extract_year_direct(self, bib_parser):
        assert bib_parser.extract_year({'year': '2023'}) == '2023'

    def test_extract_year_from_date(self, bib_parser):
        assert bib_parser.extract_year({'date': '2021-06-15'}) == '2021'

    def test_extract_year_default(self, bib_parser):
        assert bib_parser.extract_year({}) == '2025'

    def test_extract_month_direct(self, bib_parser):
        assert bib_parser.extract_month({'month': 'jun'}) == 'jun'

    def test_extract_month_from_date(self, bib_parser):
        assert bib_parser.extract_month({'date': '15 mar 2020'}) == 'mar'

    def test_extract_month_default(self, bib_parser):
        assert bib_parser.extract_month({}) == '01'


@pytest.mark.library
@pytest.mark.unit
class TestBibParserVenue:
    def test_article_uses_journal(self, bib_parser):
        assert bib_parser.format_venue(
            {'type': 'article', 'journal': 'Marine Policy'}
        ) == 'Marine Policy'

    def test_inproceedings_uses_booktitle(self, bib_parser):
        assert bib_parser.format_venue(
            {'type': 'inproceedings', 'booktitle': 'IOC 2021'}
        ) == 'IOC 2021'

    def test_thesis_uses_school(self, bib_parser):
        assert bib_parser.format_venue(
            {'type': 'phdthesis', 'school': 'ANU'}
        ) == 'ANU'

    def test_techreport_uses_institution(self, bib_parser):
        assert bib_parser.format_venue(
            {'type': 'techreport', 'institution': 'IDDRI'}
        ) == 'IDDRI'

    def test_misc_falls_back_across_fields(self, bib_parser):
        assert bib_parser.format_venue(
            {'type': 'misc', 'institution': 'OECD'}
        ) == 'OECD'


@pytest.mark.library
@pytest.mark.unit
class TestBibParserKeywords:
    def test_extract_keywords_splits_and_lowercases(self, bib_parser):
        kws = bib_parser.extract_keywords({'keywords': 'Ocean, Governance; Marine'})
        assert kws == ['ocean', 'governance', 'marine']

    def test_extract_keywords_filters_ignore_prefix(self, bib_parser):
        kws = bib_parser.extract_keywords(
            {'keywords': 'ocean, ignore-this, governance'}
        )
        assert 'ignore-this' not in kws
        assert 'ocean' in kws

    def test_extract_keywords_empty(self, bib_parser):
        assert bib_parser.extract_keywords({}) == []


@pytest.mark.library
@pytest.mark.unit
class TestBibParserLinks:
    def test_extract_url_and_doi(self, bib_parser):
        links = bib_parser.extract_links({
            'url': 'https://example.com/paper',
            'doi': '10.1000/xyz',
        })
        assert links['url'] == 'https://example.com/paper'
        assert links['doi'] == 'https://doi.org/10.1000/xyz'

    def test_doi_already_url(self, bib_parser):
        links = bib_parser.extract_links({'doi': 'https://doi.org/10.1/abc'})
        assert links['doi'] == 'https://doi.org/10.1/abc'

    def test_website_alias_for_url(self, bib_parser):
        links = bib_parser.extract_links({'website': 'https://example.com/w'})
        assert links['url'] == 'https://example.com/w'

    def test_arxiv_and_media_fields(self, bib_parser):
        links = bib_parser.extract_links({
            'arxiv': '2301.00001',
            'pdf': 'paper.pdf',
            'preview': 'thumb.jpg',
            'video': 'https://youtube.com/x',
            'slides': 'slides.pdf',
            'agenda': 'agenda.pdf',
            'poster': 'poster.pdf',
        })
        assert links['arxiv'] == 'https://arxiv.org/abs/2301.00001'
        assert links['pdf'] == 'paper.pdf'
        assert links['slides'] == 'slides.pdf'
        assert links['agenda'] == 'agenda.pdf'
        assert links['poster'] == 'poster.pdf'

    def test_pdf_from_file_field_fallback(self, bib_parser):
        links = bib_parser.extract_links({
            'file': 'PDF:/zotero/storage/ABC/paper.pdf:application/pdf',
        })
        assert links['pdf'] == 'paper.pdf'

    def test_pdf_field_prefers_over_file_field(self, bib_parser):
        links = bib_parser.extract_links({
            'pdf': 'processed.pdf',
            'file': 'orig.pdf:/path/orig.pdf:application/pdf',
        })
        assert links['pdf'] == 'processed.pdf'

    def test_urls_from_note_field(self, bib_parser):
        links = bib_parser.extract_links({
            'note': 'Watch https://youtube.com/watch?v=1 and buy https://amazon.com/x',
        })
        assert links['youtube'] == 'https://youtube.com/watch?v=1'
        assert links['amazon'] == 'https://amazon.com/x'

    def test_extract_pdf_from_file_simple_filename(self, bib_parser):
        assert bib_parser._extract_pdf_from_file_field('report.pdf') == 'report.pdf'

    def test_extract_pdf_from_file_empty(self, bib_parser):
        assert bib_parser._extract_pdf_from_file_field('') is None
        assert bib_parser._extract_pdf_from_file_field(None) is None

    def test_extract_pdf_skips_non_pdf(self, bib_parser):
        result = bib_parser._extract_pdf_from_file_field(
            'thumb.png:/path/thumb.png:image/png'
        )
        assert result is None


@pytest.mark.library
@pytest.mark.unit
class TestBibParserImages:
    def test_preview_and_photos(self, bib_parser):
        images = bib_parser.extract_images({
            'preview': 'cover.jpg',
            'photos': 'photo1.png, photo2.jpeg',
        })
        assert 'cover' in images
        assert 'photo1' in images
        assert 'photo2' in images

    def test_filters_generic_invalid_names(self, bib_parser):
        images = bib_parser.extract_images({
            'preview': 'thumbnail',
            'photos': 'pdf, image, real_photo.jpg',
        })
        assert 'thumbnail' not in images
        assert 'pdf' not in images
        assert 'image' not in images
        assert 'real_photo' in images

    def test_images_from_file_field(self, bib_parser):
        images = bib_parser.extract_images({
            'file': 'gallery.jpg:/path/gallery.jpg:image/jpeg; doc.pdf:/path/doc.pdf:application/pdf',
        })
        assert 'gallery' in images

    def test_deduplicates_images(self, bib_parser):
        images = bib_parser.extract_images({
            'preview': 'same.jpg',
            'photos': 'same.jpg, same.png',
        })
        assert images.count('same') == 1


@pytest.mark.library
@pytest.mark.unit
class TestBibParserDedupeByKey:
    def test_dedupe_keeps_richer_true_duplicate(self, bib_parser, capsys):
        entries = [
            {'ID': 'Wright2011', 'title': 'Marine Energy', 'year': '2011'},
            {
                'ID': 'Wright2011',
                'title': 'Marine Energy',
                'author': 'Wright, Glen',
                'year': '2011',
                'booktitle': 'All-Energy Australia',
                'pdf': 'a.pdf',
            },
            {'ID': 'Other', 'title': 'Unique'},
        ]
        result = bib_parser.dedupe_entries_by_key(entries)
        assert [e['ID'] for e in result] == ['Wright2011', 'Other']
        assert result[0]['pdf'] == 'a.pdf'
        assert 'Duplicate entry Wright2011' in capsys.readouterr().out

    def test_dedupe_keeps_key_collision_with_different_titles(self, bib_parser, capsys):
        entries = [
            {'ID': 'Wright2014', 'title': 'Regulating marine renewable energy'},
            {'ID': 'Wright2014', 'title': 'The Scores at Half Time'},
        ]
        result = bib_parser.dedupe_entries_by_key(entries)
        assert len(result) == 2
        out = capsys.readouterr().out
        assert 'Citation key collision Wright2014' in out

    def test_dedupe_preserves_order_and_skips_empty_keys(self, bib_parser):
        entries = [
            {'ID': 'A', 'title': 'First'},
            {'title': 'No key'},
            {'ID': 'B', 'title': 'Second'},
            {'ID': 'A', 'title': 'First'},
        ]
        result = bib_parser.dedupe_entries_by_key(entries, warn=False)
        assert [e.get('ID') for e in result] == ['A', None, 'B']
        assert result[0]['title'] == 'First'


@pytest.mark.library
@pytest.mark.unit
class TestBibParserAbstractDescription:
    def test_get_abstract_normalizes_spaces_keeps_newlines(self, bib_parser):
        abstract = bib_parser.get_abstract({
            'abstract': 'Line one.  \t  Extra spaces.\n\nLine two.',
        })
        assert 'Extra spaces' in abstract
        assert '\n\n' in abstract

    def test_get_abstract_empty(self, bib_parser):
        assert bib_parser.get_abstract({}) == ''

    def test_get_description_from_abstract(self, bib_parser):
        desc = bib_parser.get_description({
            'abstract': 'A' * 250,
        })
        assert desc.endswith('...')
        assert len(desc) == 203

    def test_get_description_falls_back_to_title(self, bib_parser):
        desc = bib_parser.get_description({'title': 'Short Title'})
        assert desc == 'Short Title'

    def test_get_description_truncates_long_title(self, bib_parser):
        desc = bib_parser.get_description({'title': 'T' * 150})
        assert desc.endswith('...')
        assert len(desc) == 103
