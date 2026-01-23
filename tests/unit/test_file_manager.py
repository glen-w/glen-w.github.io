#!/usr/bin/env python3
"""
Unit tests for FileManager class.
Tests file operations including copying, directory creation, and thumbnail generation.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

from processing.utils.file_manager import FileManager
from processing.config import Configuration


@pytest.mark.unit
class TestFileManager:
    """Unit tests for FileManager class."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return Configuration()
    
    @pytest.fixture
    def file_manager(self, config):
        """Create FileManager instance for testing."""
        return FileManager(config)
    
    @patch('os.makedirs')
    @patch('shutil.copy2')
    @patch('os.path.exists')
    def test_copy_file_success(self, mock_exists, mock_copy, mock_makedirs, file_manager):
        """Test copying file successfully."""
        mock_exists.return_value = False
        mock_copy.return_value = None
        
        result = file_manager.copy_file("/source/file.pdf", "/dest/file.pdf", force=False)
        
        assert result is True
        mock_copy.assert_called_once_with("/source/file.pdf", "/dest/file.pdf")
    
    @patch('os.path.exists')
    def test_copy_file_already_exists(self, mock_exists, file_manager):
        """Test copying file when destination already exists."""
        mock_exists.return_value = True
        
        result = file_manager.copy_file("/source/file.pdf", "/dest/file.pdf", force=False)
        
        assert result is True  # Should return True even if file exists
    
    @patch('os.makedirs')
    @patch('shutil.copy2', side_effect=Exception("Permission denied"))
    @patch('os.path.exists')
    def test_copy_file_failure(self, mock_exists, mock_copy, mock_makedirs, file_manager):
        """Test copying file when copy operation fails."""
        mock_exists.return_value = False
        
        result = file_manager.copy_file("/source/file.pdf", "/dest/file.pdf", force=False)
        
        assert result is False
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    @patch('os.path.getsize')
    def test_generate_pdf_thumbnail_success(self, mock_getsize, mock_exists, mock_run, file_manager):
        """Test generating PDF thumbnail successfully."""
        mock_exists.return_value = True
        mock_getsize.return_value = 5000  # Larger than MIN_THUMBNAIL_SIZE
        mock_run.return_value = MagicMock(returncode=0)
        
        result = file_manager.generate_pdf_thumbnail("/path/to/file.pdf", "/path/to/thumb.jpg", "600x")
        
        assert result is True
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    @patch('os.path.getsize')
    def test_generate_pdf_thumbnail_too_small(self, mock_getsize, mock_exists, mock_run, file_manager):
        """Test generating PDF thumbnail when result is too small."""
        mock_exists.return_value = True
        mock_getsize.return_value = 100  # Smaller than MIN_THUMBNAIL_SIZE
        mock_run.return_value = MagicMock(returncode=0)
        
        result = file_manager.generate_pdf_thumbnail("/path/to/file.pdf", "/path/to/thumb.jpg", "600x")
        
        assert result is False
    
    @patch('subprocess.run')
    def test_generate_pdf_thumbnail_fallback(self, mock_run, file_manager):
        """Test PDF thumbnail generation with fallback to legacy convert command."""
        # First call fails (magick not found), second succeeds (convert works)
        mock_run.side_effect = [
            MagicMock(returncode=1),  # magick fails
            MagicMock(returncode=0)   # convert succeeds
        ]
        
        with patch('os.path.exists', return_value=True), \
             patch('os.path.getsize', return_value=5000):
            result = file_manager.generate_pdf_thumbnail("/path/to/file.pdf", "/path/to/thumb.jpg", "600x")
        
        assert result is True
        assert mock_run.call_count == 2  # Should try both commands
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    @patch('os.path.getsize')
    def test_generate_svg_thumbnail_success(self, mock_getsize, mock_exists, mock_run, file_manager):
        """Test generating SVG thumbnail successfully."""
        mock_exists.return_value = True
        mock_getsize.return_value = 5000
        mock_run.return_value = MagicMock(returncode=0)
        
        result = file_manager.generate_svg_thumbnail("/path/to/file.svg", "/path/to/thumb.jpg", "600x")
        
        assert result is True
        mock_run.assert_called_once()
    
    @patch('os.makedirs')
    def test_ensure_directories_exist(self, mock_makedirs, file_manager):
        """Test ensuring directories exist."""
        file_manager.ensure_directories_exist()
        
        # Should call makedirs for each directory
        assert mock_makedirs.call_count >= 1
    
    @patch('os.path.exists')
    @patch('os.remove')
    def test_cleanup_file(self, mock_remove, mock_exists, file_manager):
        """Test cleaning up a file."""
        mock_exists.return_value = True
        
        file_manager._cleanup_file("/path/to/file.pdf")
        
        mock_remove.assert_called_once_with("/path/to/file.pdf")
    
    @patch('os.path.exists')
    def test_cleanup_file_not_exists(self, mock_exists, file_manager):
        """Test cleaning up file that doesn't exist."""
        mock_exists.return_value = False
        
        # Should not raise exception
        file_manager._cleanup_file("/path/to/nonexistent.pdf")
