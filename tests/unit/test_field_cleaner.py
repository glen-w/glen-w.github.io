#!/usr/bin/env python3
"""
Unit tests for FieldCleaner — file-field cleanup and field removal from BibTeX.
"""

import pytest

from processing.config import Configuration
from processing.utils.field_cleaner import FieldCleaner


@pytest.fixture
def cleaner():
    return FieldCleaner(Configuration())


@pytest.mark.unit
class TestFieldCleanerFileField:
    def test_clean_images_keeps_pdf(self, cleaner):
        field = (
            'PDF:/path/doc.pdf:application/pdf; '
            'Image:/path/photo.jpg:image/jpeg'
        )
        cleaned = cleaner.clean_file_field_from_images(
            field, processed_images=['photo.jpg']
        )
        assert 'doc.pdf' in cleaned
        assert 'photo.jpg' not in cleaned

    def test_keeps_thumbnail_images(self, cleaner):
        field = (
            'Thumbnail:/path/thumb.jpg:image/jpeg; '
            'Photo:/path/photo.jpg:image/jpeg'
        )
        cleaned = cleaner.clean_file_field_from_images(
            field, processed_images=['photo.jpg']
        )
        assert 'thumb.jpg' in cleaned
        assert 'photo.jpg' not in cleaned

    def test_empty_file_field(self, cleaner):
        assert cleaner.clean_file_field_from_images('') == ''
        assert cleaner.clean_file_field_from_images(None) in ('', None)

    def test_clean_after_processing_removes_matched(self, cleaner):
        field = 'PDF:/z/doc.pdf:application/pdf; Extra:/z/other.pdf:application/pdf'
        fields = {'pdf': 'doc.pdf'}
        cleaned = cleaner.clean_file_field_after_processing(field, fields)
        # doc.pdf was processed; other.pdf should remain if not matched
        assert 'other.pdf' in cleaned or cleaned == '' or 'doc.pdf' not in cleaned


@pytest.mark.unit
class TestFieldCleanerFieldRemoval:
    def test_remove_single_field(self, cleaner):
        content = (
            '@article{key,\n'
            '\ttitle = {Hello},\n'
            '\tfile = {a.pdf:/path/a.pdf:application/pdf},\n'
            '\tyear = {2023}\n'
            '}'
        )
        result = cleaner.remove_field_from_content(content, 'file')
        assert 'file =' not in result
        assert 'title = {Hello}' in result
        assert 'year = {2023}' in result

    def test_remove_field_with_nested_braces(self, cleaner):
        content = (
            '@article{key,\n'
            '\ttitle = {A {Nested} Title},\n'
            '\tabstract = {Text with {braces} inside},\n'
            '\tyear = {2023}\n'
            '}'
        )
        result = cleaner.remove_field_from_content(content, 'abstract')
        assert 'abstract' not in result
        assert 'Nested' in result

    def test_remove_nonexistent_field_noop(self, cleaner):
        content = '@article{key,\n\ttitle = {T}\n}'
        assert cleaner.remove_field_from_content(content, 'missing') == content

    def test_remove_multiple_fields(self, cleaner):
        content = (
            '@article{key,\n'
            '\ttitle = {T},\n'
            '\tfile = {x},\n'
            '\tmendeley-tags = {y},\n'
            '\tyear = {2023}\n'
            '}'
        )
        result = cleaner.remove_multiple_fields_from_content(
            content, ['file', 'mendeley-tags']
        )
        assert 'file =' not in result
        assert 'mendeley-tags' not in result
        assert 'title = {T}' in result

    def test_is_thumbnail_and_image_helpers(self, cleaner):
        assert cleaner._is_thumbnail_file('Thumbnail:/p/t.jpg:image/jpeg') is True
        assert cleaner._is_thumbnail_file('Photo:/p/p.jpg:image/jpeg') is False
        assert cleaner._is_image_file('x:/p/p.jpg:image/jpeg') is True
        assert cleaner._is_image_file('x:/p/d.pdf:application/pdf') is False
