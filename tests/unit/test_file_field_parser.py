#!/usr/bin/env python3
"""
Unit tests for FileFieldParser class.
Tests file field parsing and extraction functionality.
"""

import pytest
from unittest.mock import patch, MagicMock

from processing.utils.file_field_parser import FileFieldParser, FileEntry


@pytest.mark.unit
class TestFileFieldParser:
    """Unit tests for FileFieldParser class."""
    
    @pytest.fixture
    def parser(self):
        """Create FileFieldParser instance for testing."""
        return FileFieldParser()
    
    def test_parse_empty_field(self, parser):
        """Test parsing empty file field."""
        result = parser.parse("")
        assert result == []
    
    def test_parse_single_entry_full_format(self, parser):
        """Test parsing single entry with description:path:mime format."""
        file_field = "PDF:/path/to/file.pdf:application/pdf"
        entries = parser.parse(file_field)
        
        assert len(entries) == 1
        assert entries[0].description == "PDF"
        assert entries[0].path == "/path/to/file.pdf"
        assert entries[0].mime_type == "application/pdf"
    
    def test_parse_single_entry_path_mime_format(self, parser):
        """Test parsing single entry with path:mime format."""
        file_field = "/path/to/file.pdf:application/pdf"
        entries = parser.parse(file_field)
        
        assert len(entries) == 1
        assert entries[0].description == ""
        assert entries[0].path == "/path/to/file.pdf"
        assert entries[0].mime_type == "application/pdf"
    
    def test_parse_single_entry_path_only(self, parser):
        """Test parsing single entry with just path."""
        file_field = "/path/to/file.pdf"
        entries = parser.parse(file_field)
        
        assert len(entries) == 1
        assert entries[0].path == "/path/to/file.pdf"
        assert entries[0].mime_type == "application/pdf"  # Inferred from extension
    
    def test_parse_multiple_entries(self, parser):
        """Test parsing multiple entries separated by semicolons."""
        file_field = "PDF:/path/to/file1.pdf:application/pdf; image:/path/to/image.jpg:image/jpeg"
        entries = parser.parse(file_field)
        
        assert len(entries) == 2
        assert entries[0].description == "PDF"
        assert entries[0].path == "/path/to/file1.pdf"
        assert entries[1].description == "image"
        assert entries[1].path == "/path/to/image.jpg"
    
    def test_parse_with_whitespace(self, parser):
        """Test parsing handles whitespace correctly."""
        file_field = " PDF : /path/to/file.pdf : application/pdf "
        entries = parser.parse(file_field)
        
        assert len(entries) == 1
        assert entries[0].description == "PDF"
        assert entries[0].path == "/path/to/file.pdf"
        assert entries[0].mime_type == "application/pdf"
    
    def test_file_entry_is_pdf(self, parser):
        """Test FileEntry.is_pdf() method."""
        entry1 = FileEntry("PDF", "/path/to/file.pdf", "application/pdf")
        entry2 = FileEntry("", "/path/to/file.pdf", "")
        entry3 = FileEntry("", "/path/to/image.jpg", "image/jpeg")
        
        assert entry1.is_pdf() is True
        assert entry2.is_pdf() is True  # Inferred from extension
        assert entry3.is_pdf() is False
    
    def test_file_entry_is_image(self, parser):
        """Test FileEntry.is_image() method."""
        entry1 = FileEntry("", "/path/to/image.jpg", "image/jpeg")
        entry2 = FileEntry("", "/path/to/image.png", "image/png")
        entry3 = FileEntry("", "/path/to/file.pdf", "application/pdf")
        
        assert entry1.is_image() is True
        assert entry2.is_image() is True
        assert entry3.is_image() is False
    
    def test_file_entry_is_audio(self, parser):
        """Test FileEntry.is_audio() method."""
        entry1 = FileEntry("", "/path/to/audio.mp3", "audio/mpeg")
        entry2 = FileEntry("", "/path/to/audio.wav", "audio/wav")
        entry3 = FileEntry("", "/path/to/file.pdf", "application/pdf")
        
        assert entry1.is_audio() is True
        assert entry2.is_audio() is True
        assert entry3.is_audio() is False
    
    def test_file_entry_is_thumbnail(self, parser):
        """Test FileEntry.is_thumbnail() method."""
        entry1 = FileEntry("thumbnail", "/path/to/thumb.jpg", "image/jpeg")
        entry2 = FileEntry("", "/path/to/thumbnail.png", "image/png")
        entry3 = FileEntry("", "/path/to/image.jpg", "image/jpeg")
        
        assert entry1.is_thumbnail() is True
        assert entry2.is_thumbnail() is True
        assert entry3.is_thumbnail() is False
    
    def test_file_entry_is_agenda(self, parser):
        """Test FileEntry.is_agenda() method."""
        entry1 = FileEntry("agenda", "/path/to/agenda.pdf", "application/pdf")
        entry2 = FileEntry("", "/path/to/agenda_file.pdf", "application/pdf")
        entry3 = FileEntry("", "/path/to/file.pdf", "application/pdf")
        
        assert entry1.is_agenda() is True
        assert entry2.is_agenda() is True
        assert entry3.is_agenda() is False
    
    def test_file_entry_is_slides(self, parser):
        """Test FileEntry.is_slides() method."""
        entry1 = FileEntry("slides", "/path/to/slides.pdf", "application/pdf")
        entry2 = FileEntry("", "/path/to/slides_file.pdf", "application/pdf")
        entry3 = FileEntry("", "/path/to/file.pdf", "application/pdf")
        
        assert entry1.is_slides() is True
        assert entry2.is_slides() is True
        assert entry3.is_slides() is False
    
    def test_extract_pdfs(self, parser):
        """Test extracting PDF files from file field."""
        file_field = "PDF:/path/to/file1.pdf:application/pdf; image:/path/to/image.jpg:image/jpeg; PDF:/path/to/file2.pdf:application/pdf"
        pdfs = parser.extract_pdfs(file_field)
        
        assert len(pdfs) == 2
        assert "/path/to/file1.pdf" in pdfs
        assert "/path/to/file2.pdf" in pdfs
    
    def test_extract_pdfs_excludes_agenda_and_slides(self, parser):
        """Test that extract_pdfs excludes agenda and slides PDFs."""
        file_field = "PDF:/path/to/file.pdf:application/pdf; agenda:/path/to/agenda.pdf:application/pdf; slides:/path/to/slides.pdf:application/pdf"
        pdfs = parser.extract_pdfs(file_field)
        
        assert len(pdfs) == 1
        assert "/path/to/file.pdf" in pdfs
        assert "/path/to/agenda.pdf" not in pdfs
        assert "/path/to/slides.pdf" not in pdfs
    
    def test_extract_images(self, parser):
        """Test extracting image files from file field."""
        file_field = "image:/path/to/image1.jpg:image/jpeg; PDF:/path/to/file.pdf:application/pdf; image:/path/to/image2.png:image/png"
        images = parser.extract_images(file_field)
        
        assert len(images) == 2
        assert "/path/to/image1.jpg" in images
        assert "/path/to/image2.png" in images
    
    def test_extract_images_excludes_thumbnails(self, parser):
        """Test that extract_images excludes thumbnails by default."""
        file_field = "image:/path/to/image.jpg:image/jpeg; thumbnail:/path/to/thumb.jpg:image/jpeg"
        images = parser.extract_images(file_field, exclude_thumbnails=True)
        
        assert len(images) == 1
        assert "/path/to/image.jpg" in images
        assert "/path/to/thumb.jpg" not in images
    
    def test_extract_images_includes_thumbnails_when_requested(self, parser):
        """Test that extract_images can include thumbnails when requested."""
        file_field = "image:/path/to/image.jpg:image/jpeg; thumbnail:/path/to/thumb.jpg:image/jpeg"
        images = parser.extract_images(file_field, exclude_thumbnails=False)
        
        assert len(images) == 2
    
    def test_extract_audio(self, parser):
        """Test extracting audio files from file field."""
        file_field = "audio:/path/to/audio1.mp3:audio/mpeg; PDF:/path/to/file.pdf:application/pdf; audio:/path/to/audio2.wav:audio/wav"
        audio = parser.extract_audio(file_field)
        
        assert len(audio) == 2
        assert "/path/to/audio1.mp3" in audio
        assert "/path/to/audio2.wav" in audio
    
    def test_extract_agenda_pdfs(self, parser):
        """Test extracting agenda PDF files."""
        file_field = "PDF:/path/to/file.pdf:application/pdf; agenda:/path/to/agenda.pdf:application/pdf; slides:/path/to/slides.pdf:application/pdf"
        agendas = parser.extract_agenda_pdfs(file_field)
        
        assert len(agendas) == 1
        assert "/path/to/agenda.pdf" in agendas
    
    def test_extract_slides_pdfs(self, parser):
        """Test extracting slides PDF files."""
        file_field = "PDF:/path/to/file.pdf:application/pdf; slides:/path/to/slides.pdf:application/pdf; agenda:/path/to/agenda.pdf:application/pdf"
        slides = parser.extract_slides_pdfs(file_field)
        
        assert len(slides) == 1
        assert "/path/to/slides.pdf" in slides
    
    def test_extract_thumbnails(self, parser):
        """Test extracting thumbnail files."""
        file_field = "thumbnail:/path/to/thumb1.jpg:image/jpeg; image:/path/to/image.jpg:image/jpeg; thumbnail:/path/to/thumb2.png:image/png"
        thumbnails = parser.extract_thumbnails(file_field)
        
        assert len(thumbnails) == 2
        assert "/path/to/thumb1.jpg" in thumbnails
        assert "/path/to/thumb2.png" in thumbnails
    
    @patch('os.path.exists')
    @patch('os.path.getmtime')
    def test_extract_most_recent_pdf(self, mock_getmtime, mock_exists, parser):
        """Test extracting most recent PDF based on modification time."""
        mock_exists.return_value = True
        mock_getmtime.side_effect = [1000, 2000, 1500]  # Second file is most recent
        
        file_field = "PDF:/path/to/file1.pdf:application/pdf; PDF:/path/to/file2.pdf:application/pdf; PDF:/path/to/file3.pdf:application/pdf"
        most_recent = parser.extract_most_recent_pdf(file_field)
        
        assert most_recent == "/path/to/file2.pdf"
    
    @patch('os.path.exists')
    def test_extract_most_recent_pdf_none_exist(self, mock_exists, parser):
        """Test extract_most_recent_pdf when no files exist."""
        mock_exists.return_value = False
        
        file_field = "PDF:/path/to/file1.pdf:application/pdf"
        most_recent = parser.extract_most_recent_pdf(file_field)
        
        assert most_recent is None
    
    @patch('os.path.exists')
    @patch('os.path.getmtime')
    def test_get_thumbnail_priority_files(self, mock_getmtime, mock_exists, parser):
        """Test getting files in priority order for thumbnail generation."""
        mock_exists.return_value = True
        mock_getmtime.return_value = 1000
        
        file_field = "thumbnail:/path/to/thumb.svg:image/svg+xml; slides:/path/to/slides.pdf:application/pdf; agenda:/path/to/agenda.pdf:application/pdf; PDF:/path/to/file.pdf:application/pdf"
        priority_files = parser.get_thumbnail_priority_files(file_field)
        
        assert len(priority_files) >= 1
        # First should be thumbnail (priority 1)
        assert priority_files[0]['priority'] == 1
        assert priority_files[0]['type'] == 'svg'
    
    def test_extract_file_paths(self, parser):
        """Test extracting all file paths regardless of type."""
        file_field = "PDF:/path/to/file1.pdf:application/pdf; image:/path/to/image.jpg:image/jpeg; audio:/path/to/audio.mp3:audio/mpeg"
        paths = parser.extract_file_paths(file_field)
        
        assert len(paths) == 3
        assert "/path/to/file1.pdf" in paths
        assert "/path/to/image.jpg" in paths
        assert "/path/to/audio.mp3" in paths
    
    def test_parse_infers_mime_type_from_extension(self, parser):
        """Test that parser infers MIME type from file extension when not provided."""
        file_field = "/path/to/file.pdf"
        entries = parser.parse(file_field)
        
        assert len(entries) == 1
        assert entries[0].mime_type == "application/pdf"
    
    def test_parse_handles_empty_parts(self, parser):
        """Test that parser handles empty parts in file field."""
        file_field = "PDF:/path/to/file.pdf:application/pdf;; image:/path/to/image.jpg:image/jpeg"
        entries = parser.parse(file_field)
        
        assert len(entries) == 2  # Empty part should be skipped
    
    def test_parse_handles_malformed_entries(self, parser):
        """Test that parser handles malformed entries gracefully."""
        file_field = ":::; PDF:/path/to/file.pdf:application/pdf"
        entries = parser.parse(file_field)
        
        # Should skip invalid entries
        assert len(entries) == 1
        assert entries[0].path == "/path/to/file.pdf"
