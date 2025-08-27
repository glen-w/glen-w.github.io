#!/usr/bin/env python3
"""
Tests for main processing functions in process_papers.py
Uses mocking to test functionality without requiring actual files or external tools.
"""

import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock, mock_open
import sys

# Add the parent directory to the path so we can import process_papers
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from process_papers import (
    process_papers_bib,
    check_dependencies,
    generate_pdf_thumbnail,
    copy_pdf_file,
    update_pdf_metadata,
    cleanup_existing_files
)


class TestDependencyChecking:
    """Test dependency checking functionality."""
    
    @patch('subprocess.run')
    def test_check_dependencies_pypdf2_available(self, mock_run):
        """Test dependency check when PyPDF2 is available."""
        with patch.dict('sys.modules', {'PyPDF2': MagicMock()}):
            # Mock ImageMagick available
            mock_run.return_value.returncode = 0
            
            result = check_dependencies()
            assert result is True
    
    @patch('subprocess.run')
    def test_check_dependencies_pypdf2_missing(self, mock_run):
        """Test dependency check when PyPDF2 is missing."""
        with patch.dict('sys.modules', {}, clear=True):
            result = check_dependencies()
            assert result is False
    
    @patch('subprocess.run')
    def test_check_dependencies_imagemagick_missing(self, mock_run):
        """Test dependency check when ImageMagick is missing."""
        with patch.dict('sys.modules', {'PyPDF2': MagicMock()}):
            # Mock ImageMagick not available
            mock_run.side_effect = FileNotFoundError()
            
            result = check_dependencies()
            assert result is False


class TestFileOperations:
    """Test file operation functions."""
    
    @patch('subprocess.run')
    def test_generate_pdf_thumbnail_success(self, mock_run):
        """Test successful thumbnail generation."""
        mock_run.return_value.returncode = 0
        
        with patch('os.path.exists', return_value=True), \
             patch('os.path.getsize', return_value=5000):
            
            result = generate_pdf_thumbnail("/fake/path.pdf", "/fake/output.jpeg")
            assert result is True
    
    @patch('subprocess.run')
    def test_generate_pdf_thumbnail_fallback_success(self, mock_run):
        """Test thumbnail generation with fallback to convert command."""
        # First call fails (magick), second succeeds (convert)
        mock_run.side_effect = [
            MagicMock(returncode=1, stderr="magick failed"),
            MagicMock(returncode=0)
        ]
        
        with patch('os.path.exists', return_value=True), \
             patch('os.path.getsize', return_value=5000):
            
            result = generate_pdf_thumbnail("/fake/path.pdf", "/fake/output.jpeg")
            assert result is True
    
    @patch('subprocess.run')
    def test_generate_pdf_thumbnail_failure(self, mock_run):
        """Test thumbnail generation failure."""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Failed to generate thumbnail"
        
        with patch('os.path.exists', return_value=False):
            result = generate_pdf_thumbnail("/fake/path.pdf", "/fake/output.jpeg")
            assert result is False
    
    def test_copy_pdf_file_success(self):
        """Test successful PDF file copying."""
        with patch('os.makedirs'), \
             patch('shutil.copy2'):
            
            result = copy_pdf_file("/fake/source.pdf", "/fake/dest.pdf")
            assert result is True
    
    def test_copy_pdf_file_failure(self):
        """Test PDF file copying failure."""
        with patch('os.makedirs'), \
             patch('shutil.copy2', side_effect=Exception("Copy failed")):
            
            result = copy_pdf_file("/fake/source.pdf", "/fake/dest.pdf")
            assert result is False


class TestPDFMetadata:
    """Test PDF metadata functionality."""
    
    @patch('PyPDF2.PdfReader')
    @patch('PyPDF2.PdfWriter')
    def test_update_pdf_metadata_success(self, mock_writer_class, mock_reader_class):
        """Test successful PDF metadata update."""
        mock_reader = MagicMock()
        mock_writer = MagicMock()
        mock_reader_class.return_value = mock_reader
        mock_writer_class.return_value = mock_writer
        
        mock_reader.pages = [MagicMock()]
        
        with patch('builtins.open', mock_open()):
            result = update_pdf_metadata("/fake/path.pdf", {"title": "Test Title"})
            assert result is True
    
    def test_update_pdf_metadata_pypdf2_missing(self):
        """Test PDF metadata update when PyPDF2 is not available."""
        with patch.dict('sys.modules', {}, clear=True):
            result = update_pdf_metadata("/fake/path.pdf", {"title": "Test Title"})
            assert result is False


class TestCleanupFunctions:
    """Test cleanup functionality."""
    
    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('os.remove')
    def test_cleanup_existing_files_regenerate_true(self, mock_remove, mock_listdir, mock_exists):
        """Test cleanup when regenerate is True."""
        mock_exists.return_value = True
        mock_listdir.side_effect = [
            ["file1.pdf", "file2.pdf"],  # PDF directory
            ["thumb1.jpeg", "thumb2.jpeg"]  # Preview directory
        ]
        
        cleanup_existing_files(regenerate=True)
        
        # Should call remove for each file
        assert mock_remove.call_count == 4
    
    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('os.remove')
    def test_cleanup_existing_files_regenerate_false(self, mock_remove, mock_listdir, mock_exists):
        """Test cleanup when regenerate is False."""
        cleanup_existing_files(regenerate=False)
        
        # Should not call remove
        mock_remove.assert_not_called()


class TestMainProcessing:
    """Test main processing functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @patch('process_papers.check_dependencies')
    @patch('process_papers.generate_pdf_thumbnail')
    @patch('process_papers.copy_pdf_file')
    @patch('process_papers.update_pdf_metadata')
    def test_process_papers_bib_basic_workflow(self, mock_update_metadata, mock_copy_file, 
                                             mock_generate_thumbnail, mock_check_deps, temp_dir):
        """Test basic processing workflow."""
        # Mock dependencies available
        mock_check_deps.return_value = True
        
        # Mock successful file operations
        mock_copy_file.return_value = True
        mock_generate_thumbnail.return_value = True
        mock_update_metadata.return_value = True
        
        # Create test BibTeX file
        bibtex_content = """@article{test2023,
            title = {Test Title},
            author = {Smith, John},
            year = {2023},
            file = {Description:/fake/path.pdf:application/pdf}
        }"""
        
        bibtex_file = os.path.join(temp_dir, "test.bib")
        with open(bibtex_file, 'w') as f:
            f.write(bibtex_content)
        
        # Mock file existence
        with patch('os.path.exists', return_value=True):
            # Process the file
            process_papers_bib(bibtex_file, temp_dir, test_mode=True, test_count=1)
            
            # Verify the file was processed
            mock_copy_file.assert_called_once()
            mock_generate_thumbnail.assert_called_once()
            mock_update_metadata.assert_called_once()
    
    @patch('process_papers.check_dependencies')
    def test_process_papers_bib_dependencies_missing(self, mock_check_deps, temp_dir):
        """Test processing when dependencies are missing."""
        mock_check_deps.return_value = False
        
        bibtex_file = os.path.join(temp_dir, "test.bib")
        with open(bibtex_file, 'w') as f:
            f.write("@article{test2023, title = {Test}}")
        
        # Should not process when dependencies are missing
        with patch('os.path.exists', return_value=True):
            process_papers_bib(bibtex_file, temp_dir, test_mode=True, test_count=1)
            
            # Should not have processed any files
            assert not os.path.exists(os.path.join(temp_dir, "assets", "pdf"))
    
    @patch('process_papers.check_dependencies')
    @patch('process_papers.generate_pdf_thumbnail')
    @patch('process_papers.copy_pdf_file')
    def test_process_papers_bib_skip_processed_entries(self, mock_copy_file, 
                                                      mock_generate_thumbnail, mock_check_deps, temp_dir):
        """Test that already processed entries are skipped."""
        mock_check_deps.return_value = True
        mock_copy_file.return_value = True
        mock_generate_thumbnail.return_value = True
        
        # Create BibTeX file with already processed entry
        bibtex_content = """@article{test2023,
            title = {Test Title},
            author = {Smith, John},
            year = {2023},
            file = {Description:/fake/path.pdf:application/pdf},
            pdf = {already_processed.pdf},
            preview = {already_processed.jpeg}
        }"""
        
        bibtex_file = os.path.join(temp_dir, "test.bib")
        with open(bibtex_file, 'w') as f:
            f.write(bibtex_content)
        
        with patch('os.path.exists', return_value=True):
            process_papers_bib(bibtex_file, temp_dir, test_mode=True, test_count=1)
            
            # Should not copy or generate thumbnail for already processed entry
            mock_copy_file.assert_not_called()
            mock_generate_thumbnail.assert_not_called()
    
    @patch('process_papers.check_dependencies')
    @patch('process_papers.generate_pdf_thumbnail')
    @patch('process_papers.copy_pdf_file')
    def test_process_papers_bib_force_reprocess(self, mock_copy_file, 
                                               mock_generate_thumbnail, mock_check_deps, temp_dir):
        """Test that force flag reprocesses already processed entries."""
        mock_check_deps.return_value = True
        mock_copy_file.return_value = True
        mock_generate_thumbnail.return_value = True
        
        # Create BibTeX file with already processed entry
        bibtex_content = """@article{test2023,
            title = {Test Title},
            author = {Smith, John},
            year = {2023},
            file = {Description:/fake/path.pdf:application/pdf},
            pdf = {already_processed.pdf},
            preview = {already_processed.jpeg}
        }"""
        
        bibtex_file = os.path.join(temp_dir, "test.bib")
        with open(bibtex_file, 'w') as f:
            f.write(bibtex_content)
        
        with patch('os.path.exists', return_value=True):
            # Process with force flag
            process_papers_bib(bibtex_file, temp_dir, force=True, test_mode=True, test_count=1)
            
            # Should process even though entry was already processed
            mock_copy_file.assert_called_once()
            mock_generate_thumbnail.assert_called_once()


class TestErrorHandling:
    """Test error handling scenarios."""
    
    @patch('process_papers.check_dependencies')
    def test_process_papers_bib_file_not_found(self, mock_check_deps, temp_dir):
        """Test handling of missing BibTeX file."""
        mock_check_deps.return_value = True
        
        # Try to process non-existent file
        non_existent_file = os.path.join(temp_dir, "nonexistent.bib")
        
        # Should handle gracefully
        process_papers_bib(non_existent_file, temp_dir, test_mode=True, test_count=1)
    
    @patch('process_papers.check_dependencies')
    @patch('process_papers.copy_pdf_file')
    def test_process_papers_bib_copy_failure(self, mock_copy_file, mock_check_deps, temp_dir):
        """Test handling of PDF copy failure."""
        mock_check_deps.return_value = True
        mock_copy_file.return_value = False  # Copy fails
        
        bibtex_content = """@article{test2023,
            title = {Test Title},
            author = {Smith, John},
            year = {2023},
            file = {Description:/fake/path.pdf:application/pdf}
        }"""
        
        bibtex_file = os.path.join(temp_dir, "test.bib")
        with open(bibtex_file, 'w') as f:
            f.write(bibtex_content)
        
        with patch('os.path.exists', return_value=True):
            # Should handle copy failure gracefully
            process_papers_bib(bibtex_file, temp_dir, test_mode=True, test_count=1)


if __name__ == "__main__":
    pytest.main([__file__])

