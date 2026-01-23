#!/usr/bin/env python3
"""
Unit tests for FileFieldManager class.
Tests file field cleaning and manipulation functionality.
"""

import pytest
from unittest.mock import MagicMock

from processing.utils.file_field_manager import FileFieldManager
from processing.utils.file_field_parser import FileFieldParser


@pytest.mark.unit
class TestFileFieldManager:
    """Unit tests for FileFieldManager class."""
    
    @pytest.fixture
    def manager(self):
        """Create FileFieldManager instance for testing."""
        parser = FileFieldParser()
        return FileFieldManager(parser)
    
    def test_remove_images_empty_field(self, manager):
        """Test removing images from empty field."""
        result = manager.remove_images("")
        assert result == ""
    
    def test_remove_images_keeps_pdfs(self, manager):
        """Test that remove_images keeps PDF files."""
        file_field = "PDF:/path/to/file.pdf:application/pdf; image:/path/to/image.jpg:image/jpeg"
        result = manager.remove_images(file_field)
        
        assert "PDF:/path/to/file.pdf:application/pdf" in result
        assert "image:/path/to/image.jpg:image/jpeg" not in result
    
    def test_remove_images_keeps_thumbnails(self, manager):
        """Test that remove_images keeps thumbnail files."""
        file_field = "thumbnail:/path/to/thumb.jpg:image/jpeg; image:/path/to/image.jpg:image/jpeg"
        result = manager.remove_images(file_field)
        
        assert "thumbnail:/path/to/thumb.jpg:image/jpeg" in result
        assert "image:/path/to/image.jpg:image/jpeg" not in result
    
    def test_remove_images_removes_all_images(self, manager):
        """Test that remove_images removes all image files."""
        file_field = "image:/path/to/image1.jpg:image/jpeg; image:/path/to/image2.png:image/png; PDF:/path/to/file.pdf:application/pdf"
        result = manager.remove_images(file_field)
        
        assert "image:/path/to/image1.jpg:image/jpeg" not in result
        assert "image:/path/to/image2.png:image/png" not in result
        assert "PDF:/path/to/file.pdf:application/pdf" in result
    
    def test_remove_audio_empty_field(self, manager):
        """Test removing audio from empty field."""
        result = manager.remove_audio("")
        assert result == ""
    
    def test_remove_audio_keeps_other_files(self, manager):
        """Test that remove_audio keeps non-audio files."""
        file_field = "PDF:/path/to/file.pdf:application/pdf; audio:/path/to/audio.mp3:audio/mpeg; image:/path/to/image.jpg:image/jpeg"
        result = manager.remove_audio(file_field)
        
        assert "PDF:/path/to/file.pdf:application/pdf" in result
        assert "image:/path/to/image.jpg:image/jpeg" in result
        assert "audio:/path/to/audio.mp3:audio/mpeg" not in result
    
    def test_remove_audio_removes_all_audio(self, manager):
        """Test that remove_audio removes all audio files."""
        file_field = "audio:/path/to/audio1.mp3:audio/mpeg; audio:/path/to/audio2.wav:audio/wav; PDF:/path/to/file.pdf:application/pdf"
        result = manager.remove_audio(file_field)
        
        assert "audio:/path/to/audio1.mp3:audio/mpeg" not in result
        assert "audio:/path/to/audio2.wav:audio/wav" not in result
        assert "PDF:/path/to/file.pdf:application/pdf" in result
    
    def test_replace_with_processed_no_processed_files(self, manager):
        """Test replace_with_processed when no files have been processed."""
        file_field = "PDF:/path/to/file.pdf:application/pdf"
        fields = {}
        result = manager.replace_with_processed(file_field, fields)
        
        assert result == file_field  # Should return original
    
    def test_replace_with_processed_with_pdf(self, manager):
        """Test replace_with_processed with processed PDF."""
        file_field = "PDF:/path/to/file.pdf:application/pdf"
        fields = {'pdf': 'processed_file.pdf'}
        result = manager.replace_with_processed(file_field, fields)
        
        assert "PDF:/assets/pdf/processed_file.pdf:application/pdf" in result
    
    def test_replace_with_processed_with_slides(self, manager):
        """Test replace_with_processed with processed slides."""
        file_field = "slides:/path/to/slides.pdf:application/pdf"
        fields = {'slides': 'processed_slides.pdf'}
        result = manager.replace_with_processed(file_field, fields)
        
        assert "PDF:/assets/pdf/processed_slides.pdf:application/pdf" in result
    
    def test_replace_with_processed_with_agenda(self, manager):
        """Test replace_with_processed with processed agenda."""
        file_field = "agenda:/path/to/agenda.pdf:application/pdf"
        fields = {'agenda': 'processed_agenda.pdf'}
        result = manager.replace_with_processed(file_field, fields)
        
        assert "PDF:/assets/pdf/processed_agenda.pdf:application/pdf" in result
    
    def test_replace_with_processed_with_photos(self, manager):
        """Test replace_with_processed with processed photos."""
        file_field = "image:/path/to/image.jpg:image/jpeg"
        fields = {'photos': 'photo1.jpg, photo2.jpg'}
        result = manager.replace_with_processed(file_field, fields)
        
        assert "photo:/assets/img/publications/photo1.jpg:image/jpeg" in result
        assert "photo:/assets/img/publications/photo2.jpg:image/jpeg" in result
    
    def test_replace_with_processed_with_figures(self, manager):
        """Test replace_with_processed with processed figures."""
        file_field = "image:/path/to/image.jpg:image/jpeg"
        fields = {'figures': 'figure1.jpg, figure2.jpg'}
        result = manager.replace_with_processed(file_field, fields)
        
        assert "figure:/assets/img/publications/figure1.jpg:image/jpeg" in result
        assert "figure:/assets/img/publications/figure2.jpg:image/jpeg" in result
    
    def test_replace_with_processed_with_preview(self, manager):
        """Test replace_with_processed with processed preview."""
        file_field = "thumbnail:/path/to/thumb.jpg:image/jpeg"
        fields = {'preview': 'preview.jpg'}
        result = manager.replace_with_processed(file_field, fields)
        
        assert "thumbnail:/assets/img/publication_preview/preview.jpg:image/jpeg" in result
    
    def test_replace_with_processed_multiple_types(self, manager):
        """Test replace_with_processed with multiple file types."""
        file_field = "PDF:/path/to/file.pdf:application/pdf; image:/path/to/image.jpg:image/jpeg"
        fields = {
            'pdf': 'processed.pdf',
            'photos': 'photo1.jpg, photo2.jpg',
            'preview': 'preview.jpg'
        }
        result = manager.replace_with_processed(file_field, fields)
        
        assert "PDF:/assets/pdf/processed.pdf:application/pdf" in result
        assert "photo:/assets/img/publications/photo1.jpg:image/jpeg" in result
        assert "photo:/assets/img/publications/photo2.jpg:image/jpeg" in result
        assert "thumbnail:/assets/img/publication_preview/preview.jpg:image/jpeg" in result
    
    def test_clean_after_processing_alias(self, manager):
        """Test that clean_after_processing is an alias for replace_with_processed."""
        file_field = "PDF:/path/to/file.pdf:application/pdf"
        fields = {'pdf': 'processed.pdf'}
        
        result1 = manager.replace_with_processed(file_field, fields)
        result2 = manager.clean_after_processing(file_field, fields)
        
        assert result1 == result2
    
    def test_remove_images_returns_empty_when_all_removed(self, manager):
        """Test that remove_images returns empty string when all entries are images."""
        file_field = "image:/path/to/image1.jpg:image/jpeg; image:/path/to/image2.png:image/png"
        result = manager.remove_images(file_field)
        
        assert result == ""
    
    def test_remove_audio_returns_empty_when_all_removed(self, manager):
        """Test that remove_audio returns empty string when all entries are audio."""
        file_field = "audio:/path/to/audio1.mp3:audio/mpeg; audio:/path/to/audio2.wav:audio/wav"
        result = manager.remove_audio(file_field)
        
        assert result == ""
