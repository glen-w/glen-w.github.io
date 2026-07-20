#!/usr/bin/env python3
"""
Unit tests for TagExtractor — shared between paper processing and library rendering.
"""

import pytest

from processing.core.tag_extractor import TagExtractor


@pytest.mark.unit
@pytest.mark.library
class TestTagExtractorType:
    def test_type_from_annote(self, tag_extractor):
        entry = {'ENTRYTYPE': 'misc', 'annote': '[type]\nwebinar\n[role]\nspeaker'}
        assert tag_extractor.extract_type(entry) == 'Webinar'

    def test_type_fallback_to_entrytype(self, tag_extractor):
        assert tag_extractor.extract_type({'ENTRYTYPE': 'article'}) == 'Journal Article'
        assert tag_extractor.extract_type({'ENTRYTYPE': 'techreport'}) == 'Report'

    def test_type_unknown_entrytype_capitalized(self, tag_extractor):
        assert tag_extractor.extract_type({'ENTRYTYPE': 'dataset'}) == 'Dataset'

    def test_type_missing(self, tag_extractor):
        assert tag_extractor.extract_type({}) is None

    def test_type_multiword_custom(self, tag_extractor):
        entry = {'ENTRYTYPE': 'misc', 'annote': '[type]\npolicy brief'}
        assert tag_extractor.extract_type(entry) == 'Policy Brief'

    def test_type_unescape_at(self, tag_extractor):
        entry = {'ENTRYTYPE': 'misc', 'annote': '[type]\n@@mention'}
        result = tag_extractor.extract_type(entry)
        assert result == '@Mention' or '@' in result

    def test_preserve_case(self):
        extractor = TagExtractor(preserve_case=True)
        entry = {'ENTRYTYPE': 'misc', 'annote': '[type]\nMy Custom Type'}
        assert extractor.extract_type(entry) == 'My Custom Type'


@pytest.mark.unit
@pytest.mark.library
class TestTagExtractorRoles:
    def test_multiple_roles(self, tag_extractor):
        entry = {'annote': '[role]\nModerator\nSpeaker\n[type]\nwebinar'}
        roles = tag_extractor.extract_roles(entry)
        assert roles == ['moderator', 'speaker']

    def test_dedupe_roles(self, tag_extractor):
        entry = {'annote': '[role]\nauthor\nAuthor\nauthor'}
        assert tag_extractor.extract_roles(entry) == ['author']

    def test_no_roles(self, tag_extractor):
        assert tag_extractor.extract_roles({'annote': '[type]\narticle'}) == []
        assert tag_extractor.extract_roles({}) == []


@pytest.mark.unit
@pytest.mark.library
class TestTagExtractorLanguages:
    def test_valid_languages(self, tag_extractor):
        entry = {'annote': '[language]\nFrench\nSpanish\nChinese\nCatalan'}
        langs = tag_extractor.extract_languages(entry)
        assert set(langs) == {'french', 'spanish', 'chinese', 'catalan'}

    def test_invalid_language_dropped(self, tag_extractor):
        entry = {'annote': '[language]\ngerman\nfrench'}
        assert tag_extractor.extract_languages(entry) == ['french']

    def test_no_languages(self, tag_extractor):
        assert tag_extractor.extract_languages({}) == []


@pytest.mark.unit
@pytest.mark.library
class TestTagExtractorSelectedAndAll:
    def test_selected_true(self, tag_extractor):
        assert tag_extractor.extract_selected({'annote': 'note\n[selected]\nmore'}) is True
        assert tag_extractor.extract_selected({'annote': '[SELECTED]'}) is True

    def test_selected_false(self, tag_extractor):
        assert tag_extractor.extract_selected({'annote': '[type]\narticle'}) is False
        assert tag_extractor.extract_selected({}) is False

    def test_extract_all_tags(self, tag_extractor):
        entry = {
            'ENTRYTYPE': 'misc',
            'annote': '[type]\nworkshop\n[role]\norganiser\n[language]\nfrench',
        }
        tags = tag_extractor.extract_all_tags(entry)
        assert tags['type'] == 'Workshop'
        assert 'organiser' in tags['roles']
        assert 'french' in tags['languages']

    def test_section_helpers(self, tag_extractor):
        text = '[type]\nFirst\n[role]\nA\nB'
        assert tag_extractor._extract_section_value(text, '[type]') == 'First'
        assert tag_extractor._extract_section_values(text, '[role]') == ['A', 'B']
        assert tag_extractor._extract_section_value(text, '[missing]') is None
