#!/usr/bin/env python3
"""
Unit tests for NotesProcessor — Zotero notes → annote / field population.
"""

import pytest

from processing.core.notes_processor import NotesProcessor


@pytest.fixture
def notes_processor():
    return NotesProcessor()


@pytest.mark.unit
class TestNotesProcessor:
    def test_empty_notes_adds_type_fallback(self, notes_processor):
        entry = {'ENTRYTYPE': 'article', 'ID': 'x'}
        result = notes_processor.process_notes_for_entry(entry, '')
        assert '[type]' in result['annote']
        assert 'Journal Article' in result['annote']

    def test_empty_notes_skips_fallback_if_type_exists(self, notes_processor):
        entry = {'ENTRYTYPE': 'article', 'annote': '[type]\nCustom'}
        result = notes_processor.process_notes_for_entry(entry, '')
        assert result['annote'].count('[type]') == 1
        assert 'Custom' in result['annote']

    def test_structure_notes_escapes_at(self, notes_processor):
        structured = notes_processor._structure_notes('@handle and text')
        assert '@@handle' in structured

    def test_process_notes_sets_annote(self, notes_processor):
        entry = {'ENTRYTYPE': 'misc', 'ID': 'w'}
        notes = '[type]\nwebinar\n[role]\nmoderator\n[selected]'
        result = notes_processor.process_notes_for_entry(entry, notes)
        assert '[type]' in result['annote']
        assert 'webinar' in result['annote'].lower() or 'Webinar' in result['annote']
        assert result.get('selected') == 'true'

    def test_extract_video_links(self, notes_processor):
        notes = '[video]\nhttps://youtube.com/watch?v=abc\nhttps://example.com/clip.mp4'
        videos = notes_processor._extract_video_links(notes)
        assert videos == [
            'https://youtube.com/watch?v=abc',
            'https://example.com/clip.mp4',
        ]

    def test_extract_video_links_empty(self, notes_processor):
        assert notes_processor._extract_video_links('no videos') == []
        assert notes_processor._extract_video_links('') == []

    def test_video_populated_on_entry(self, notes_processor):
        entry = {'ENTRYTYPE': 'misc'}
        notes = '[type]\nwebinar\n[video]\nhttps://youtu.be/xyz'
        result = notes_processor.process_notes_for_entry(entry, notes)
        assert result['video'] == 'https://youtu.be/xyz'

    def test_video_section_stops_at_next_section(self, notes_processor):
        notes = (
            '[video]\n'
            'https://vimeo.com/12345\n'
            '[role]\n'
            'moderator\n'
            'https://example.com/should-not-be-video'
        )
        videos = notes_processor._extract_video_links(notes)
        assert videos == ['https://vimeo.com/12345']
        assert not any('should-not-be-video' in v for v in videos)

    def test_non_youtube_video_urls_retained(self, notes_processor):
        notes = (
            '[video]\n'
            'https://vimeo.com/98765\n'
            'https://cdn.example.com/talk.mp4\n'
            'https://youtube.com/watch?v=abc'
        )
        videos = notes_processor._extract_video_links(notes)
        assert videos == [
            'https://vimeo.com/98765',
            'https://cdn.example.com/talk.mp4',
            'https://youtube.com/watch?v=abc',
        ]

    def test_trailing_punctuation_stripped_from_video_urls(self, notes_processor):
        notes = (
            '[video]\n'
            'https://youtu.be/xyz.\n'
            'https://vimeo.com/1),\n'
            'https://cdn.example.com/a.mp4;'
        )
        videos = notes_processor._extract_video_links(notes)
        assert videos == [
            'https://youtu.be/xyz',
            'https://vimeo.com/1',
            'https://cdn.example.com/a.mp4',
        ]

    def test_process_notes_twice_does_not_double_escape_at(self, notes_processor):
        entry = {'ENTRYTYPE': 'misc', 'ID': 'at'}
        notes = 'Contact @ocean_policy and already@@escaped'
        once = notes_processor.process_notes_for_entry(dict(entry), notes)
        twice = notes_processor.process_notes_for_entry(dict(entry), once['annote'])
        assert '@@@@' not in twice['annote']
        assert twice['annote'].count('@@ocean_policy') == 1
        assert '@@escaped' in twice['annote']

    def test_roles_speakers_quotes_survive(self, notes_processor):
        entry = {'ENTRYTYPE': 'misc', 'ID': 'event'}
        notes = (
            '[type]\nwebinar\n'
            '[role]\nmoderator\n'
            '[speakers]\nAlice Expert\nBob Host\n'
            '[quotes]\nOcean governance matters\n'
            '[video]\nhttps://youtu.be/abc'
        )
        result = notes_processor.process_notes_for_entry(entry, notes)
        annote = result['annote']
        assert '[role]' in annote
        assert 'moderator' in annote
        assert '[speakers]' in annote
        assert 'Alice Expert' in annote
        assert '[quotes]' in annote
        assert 'Ocean governance matters' in annote
        assert result.get('video') == 'https://youtu.be/abc'

    def test_add_audio_replace_preserves_following_sections(self):
        from processing.core.entry_processor import EntryProcessor

        ep = object.__new__(EntryProcessor)
        fields = {
            'annote': (
                '[type]\nwebinar\n\n'
                '[audio]\nold.mp3\n\n'
                '[role]\nspeaker\n\n'
                '[quotes]\nKeep me'
            )
        }
        ep._add_audio_to_annote(fields, ['new_a.mp3', 'new_b.mp3'])
        annote = fields['annote']
        assert '[audio]' in annote
        assert 'new_a.mp3' in annote
        assert 'new_b.mp3' in annote
        assert 'old.mp3' not in annote
        assert '[role]' in annote
        assert 'speaker' in annote
        assert '[quotes]' in annote
        assert 'Keep me' in annote
        assert annote.count('[audio]') == 1

    def test_add_audio_reprocess_does_not_duplicate_paths(self):
        from processing.core.entry_processor import EntryProcessor

        ep = object.__new__(EntryProcessor)
        fields = {'annote': '[type]\npanel'}
        ep._add_audio_to_annote(fields, ['clip.mp3'])
        ep._add_audio_to_annote(fields, ['clip.mp3'])
        assert fields['annote'].count('clip.mp3') == 1
        assert fields['annote'].count('[audio]') == 1

    def test_other_links_set_url_when_missing(self, notes_processor):
        entry = {'ENTRYTYPE': 'misc'}
        notes = '[type]\nother\nhttps://example.com/page'
        result = notes_processor.process_notes_for_entry(entry, notes)
        assert result.get('url') == 'https://example.com/page'

    def test_other_links_do_not_overwrite_url(self, notes_processor):
        entry = {'ENTRYTYPE': 'misc', 'url': 'https://original.com'}
        notes = 'See https://example.com/other'
        result = notes_processor.process_notes_for_entry(entry, notes)
        assert result['url'] == 'https://original.com'

    def test_whitespace_only_notes_treated_as_empty(self, notes_processor):
        entry = {'ENTRYTYPE': 'book'}
        result = notes_processor.process_notes_for_entry(entry, '   \n  ')
        assert 'Book' in result['annote']
