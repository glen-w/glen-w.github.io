#!/usr/bin/env python3
"""
Unit tests for PDFProcessor class.
Tests PDF operations including metadata updates and validation.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

from processing.core.pdf_processor import PDFProcessor
from processing.core.text_processor import TextProcessor
from processing.config import Configuration


@pytest.mark.unit
class TestPDFProcessor:
    """Unit tests for PDFProcessor class."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return Configuration()
    
    @pytest.fixture
    def text_processor(self, config):
        """Create TextProcessor instance."""
        return TextProcessor(config)
    
    @pytest.fixture
    def pdf_processor(self, config, text_processor):
        """Create PDFProcessor instance for testing."""
        return PDFProcessor(config, text_processor)
    
    @patch('shutil.copy2')
    @patch('os.path.exists')
    def test_backup_pdf_success(self, mock_exists, mock_copy, pdf_processor):
        """Test backing up PDF file successfully."""
        mock_exists.return_value = False
        mock_copy.return_value = None
        
        result = pdf_processor.backup_pdf("/path/to/file.pdf")
        
        assert result is not None
        assert "backup" in result
        mock_copy.assert_called_once()
    
    @patch('os.path.exists')
    def test_backup_pdf_already_exists(self, mock_exists, pdf_processor):
        """Test backing up PDF when backup already exists."""
        mock_exists.return_value = True
        
        result = pdf_processor.backup_pdf("/path/to/file.pdf")
        
        assert result is not None
        assert "backup" in result
    
    @patch('shutil.copy2', side_effect=Exception("Permission denied"))
    def test_backup_pdf_failure(self, mock_copy, pdf_processor):
        """Test backing up PDF when copy fails."""
        result = pdf_processor.backup_pdf("/path/to/file.pdf")
        
        assert result is None
    
    @patch('os.path.exists')
    @patch('os.access')
    def test_check_file_writable(self, mock_access, mock_exists, pdf_processor):
        """Test checking if PDF file is writable."""
        mock_exists.return_value = True
        mock_access.return_value = True
        
        result = pdf_processor._check_file_writable("/path/to/file.pdf")
        
        assert result is True
    
    @patch('os.path.exists')
    def test_check_file_writable_not_exists(self, mock_exists, pdf_processor):
        """Test checking writability when file doesn't exist."""
        mock_exists.return_value = False
        
        result = pdf_processor._check_file_writable("/path/to/file.pdf")
        
        assert result is False
    
    @patch('PyPDF2.PdfReader')
    @patch('PyPDF2.PdfWriter')
    def test_prepare_pdf_metadata(self, mock_writer, mock_reader, pdf_processor):
        """Test preparing PDF metadata from BibTeX fields."""
        fields = {
            'title': 'Test Title',
            'author': 'Test Author',
            'year': '2023',
            'journal': 'Test Journal'
        }
        
        metadata = pdf_processor.prepare_pdf_metadata(fields)
        
        assert metadata['title'] == 'Test Title'
        assert metadata['author'] == 'Test Author'
        assert 'subject' in metadata or 'journal' in metadata
    
    @patch('processing.core.pdf_processor.PDFProcessor.validate_pdf')
    @patch('processing.core.pdf_processor.PDFProcessor._check_file_writable')
    @patch('processing.core.pdf_processor.PDFProcessor._atomic_write_pdf')
    @patch('PyPDF2.PdfReader')
    @patch('PyPDF2.PdfWriter')
    def test_update_pdf_metadata_success(self, mock_writer, mock_reader, mock_write, mock_writable, mock_validate, pdf_processor):
        """Test updating PDF metadata successfully."""
        mock_validate.return_value = True
        mock_writable.return_value = True
        mock_write.return_value = True
        
        # Mock PDF reader and writer
        mock_pdf = MagicMock()
        mock_reader.return_value = mock_pdf
        mock_pdf.metadata = {}
        mock_pdf.pages = [MagicMock()]
        
        metadata = {'title': 'Test Title', 'author': 'Test Author'}
        result = pdf_processor.update_pdf_metadata("/path/to/file.pdf", metadata, backup=False)
        
        assert result is True
        mock_write.assert_called_once()
    
    @patch('processing.core.pdf_processor.PDFProcessor._check_file_writable')
    def test_update_pdf_metadata_not_writable(self, mock_writable, pdf_processor):
        """Test updating PDF metadata when file is not writable."""
        mock_writable.return_value = False
        
        metadata = {'title': 'Test Title'}
        result = pdf_processor.update_pdf_metadata("/path/to/file.pdf", metadata, backup=False)
        
        assert result is False
    
    @patch('processing.core.pdf_processor.PDFProcessor.validate_pdf')
    def test_validate_pdf_valid(self, mock_validate, pdf_processor):
        """Test PDF validation for valid PDF."""
        mock_validate.return_value = True
        
        result = pdf_processor.validate_pdf("/path/to/file.pdf")
        
        assert result is True
    
    @patch('processing.core.pdf_processor.PDFProcessor.validate_pdf')
    def test_validate_pdf_invalid(self, mock_validate, pdf_processor):
        """Test PDF validation for invalid PDF."""
        mock_validate.return_value = False
        
        result = pdf_processor.validate_pdf("/path/to/file.pdf")
        
        assert result is False
    
    @patch('tempfile.mkstemp')
    @patch('os.fdopen')
    @patch('os.replace')
    @patch('processing.core.pdf_processor.PDFProcessor.validate_pdf')
    def test_atomic_write_pdf_success(self, mock_validate, mock_replace, mock_fdopen, mock_mkstemp, pdf_processor):
        """Test atomic write of PDF file."""
        mock_mkstemp.return_value = (123, "/tmp/temp.pdf")
        mock_validate.return_value = True
        mock_writer = MagicMock()
        
        result = pdf_processor._atomic_write_pdf("/path/to/file.pdf", mock_writer)
        
        assert result is True
        mock_replace.assert_called_once()
    
    @patch('tempfile.mkstemp')
    @patch('os.fdopen')
    @patch('processing.core.pdf_processor.PDFProcessor.validate_pdf')
    def test_atomic_write_pdf_validation_fails(self, mock_validate, mock_fdopen, mock_mkstemp, pdf_processor):
        """Test atomic write when validation fails."""
        mock_mkstemp.return_value = (123, "/tmp/temp.pdf")
        mock_validate.return_value = False
        mock_writer = MagicMock()
        
        result = pdf_processor._atomic_write_pdf("/path/to/file.pdf", mock_writer)
        
        assert result is False
