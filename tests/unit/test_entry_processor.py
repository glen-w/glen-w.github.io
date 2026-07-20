#!/usr/bin/env python3
"""
Unit tests for EntryProcessor class.
Tests entry processing workflow and file processing coordination.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from processing.core.entry_processor import EntryProcessor
from processing.config import Configuration
from processing.core.text_processor import TextProcessor
from processing.utils.file_manager import FileManager
from processing.core.pdf_processor import PDFProcessor
from processing.core.bibtex_processor import BibTeXProcessor
from processing.core.zip_archive_generator import ZipArchiveGenerator
from processing.utils.file_field_manager import FileFieldManager
from processing.utils.file_field_parser import FileFieldParser


@pytest.mark.unit
class TestEntryProcessor:
    """Unit tests for EntryProcessor class."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return Configuration()
    
    @pytest.fixture
    def text_processor(self, config):
        """Create TextProcessor instance."""
        return TextProcessor(config)
    
    @pytest.fixture
    def file_manager(self, config):
        """Create FileManager instance."""
        return FileManager(config)
    
    @pytest.fixture
    def pdf_processor(self, config, text_processor):
        """Create PDFProcessor instance."""
        return PDFProcessor(config, text_processor)
    
    @pytest.fixture
    def bibtex_processor(self, config, text_processor):
        """Create BibTeXProcessor instance."""
        return BibTeXProcessor(config, text_processor)
    
    @pytest.fixture
    def zip_generator(self, config, text_processor):
        """Create ZipArchiveGenerator instance."""
        return ZipArchiveGenerator(config, text_processor)
    
    @pytest.fixture
    def file_field_manager(self):
        """Create FileFieldManager instance."""
        parser = FileFieldParser()
        return FileFieldManager(parser)
    
    @pytest.fixture
    def entry_processor(self, config, file_manager, pdf_processor, bibtex_processor,
                       text_processor, zip_generator, file_field_manager):
        """Create EntryProcessor instance for testing."""
        return EntryProcessor(
            config=config,
            file_manager=file_manager,
            pdf_processor=pdf_processor,
            bibtex_processor=bibtex_processor,
            text_processor=text_processor,
            zip_archive_generator=zip_generator,
            file_field_manager=file_field_manager
        )
    
    def test_initialization(self, entry_processor):
        """Test that EntryProcessor initializes correctly."""
        assert entry_processor.config is not None
        assert entry_processor.file_manager is not None
        assert entry_processor.pdf_processor is not None
        assert entry_processor.bibtex_processor is not None
        assert entry_processor.file_field_manager is not None
    
    def test_is_entry_processed_basic_processing_complete(self, entry_processor):
        """Test is_entry_processed when basic processing is complete."""
        fields = {'preview': 'preview.jpg', 'pdf': 'file.pdf'}
        
        result = entry_processor.is_entry_processed(fields)
        
        assert result is True
    
    def test_is_entry_processed_with_slides(self, entry_processor):
        """Test is_entry_processed when slides are present."""
        fields = {'preview': 'preview.jpg', 'slides': 'slides.pdf'}
        
        result = entry_processor.is_entry_processed(fields)
        
        assert result is True
    
    def test_is_entry_processed_incomplete(self, entry_processor):
        """Test is_entry_processed when processing is incomplete."""
        fields = {'preview': 'preview.jpg'}  # Missing pdf or slides
        
        result = entry_processor.is_entry_processed(fields)
        
        assert result is False
    
    def test_is_entry_processed_with_unprocessed_images(self, entry_processor):
        """Test is_entry_processed when unprocessed images exist."""
        fields = {
            'preview': 'preview.jpg',
            'pdf': 'file.pdf',
            'file': 'image:/path/to/image.jpg:image/jpeg'  # Unprocessed image
        }
        
        result = entry_processor.is_entry_processed(fields)
        
        assert result is False

    @patch('os.path.exists')
    def test_is_entry_processed_incremental_false_when_preview_file_missing(self, mock_exists, entry_processor):
        """When incremental=True, is_entry_processed returns False if referenced preview file does not exist."""
        mock_exists.return_value = False
        fields = {'preview': 'foo.jpg', 'pdf': 'file.pdf'}
        result = entry_processor.is_entry_processed(fields, incremental=True)
        assert result is False

    @patch('os.path.exists')
    def test_is_entry_processed_incremental_true_when_files_exist(self, mock_exists, entry_processor):
        """When incremental=True and all referenced files exist on disk, is_entry_processed returns True."""
        mock_exists.return_value = True
        fields = {'preview': 'foo.jpg', 'pdf': 'file.pdf'}
        result = entry_processor.is_entry_processed(fields, incremental=True)
        assert result is True

    @patch.object(EntryProcessor, 'process_entry_files')
    def test_process_entry_success(self, mock_process_files, entry_processor):
        """Test processing a single entry successfully."""
        mock_process_files.return_value = True
        entry = {
            'citation_key': 'test2023',
            'fields': {'title': 'Test'}
        }
        
        result = entry_processor.process_entry(
            entry, regenerate=False, force=False, incremental=False, update_metadata=True,
            thumbnail_size='600x', verbose=False, force_refetch_metadata=False,
            rename_only=False, update_pdf_metadata=False
        )
        
        assert result is True
        mock_process_files.assert_called_once()
    
    @patch.object(EntryProcessor, 'is_entry_processed')
    def test_process_entry_already_processed(self, mock_is_processed, entry_processor):
        """Test processing entry that's already processed."""
        mock_is_processed.return_value = True
        entry = {
            'citation_key': 'test2023',
            'fields': {'preview': 'preview.jpg', 'pdf': 'file.pdf'}
        }
        
        result = entry_processor.process_entry(
            entry, regenerate=False, force=False, incremental=False, update_metadata=True,
            thumbnail_size='600x', verbose=False, force_refetch_metadata=False,
            rename_only=False, update_pdf_metadata=False
        )
        
        assert result is True
    
    def test_process_entry_missing_citation_key(self, entry_processor):
        """Test processing entry with missing citation key."""
        entry = {
            'fields': {'title': 'Test'}
        }
        
        result = entry_processor.process_entry(
            entry, regenerate=False, force=False, incremental=False, update_metadata=True,
            thumbnail_size='600x', verbose=False, force_refetch_metadata=False,
            rename_only=False, update_pdf_metadata=False
        )
        
        assert result is False
    
    def test_process_entry_files_no_file_field(self, entry_processor):
        """Test process_entry_files when no file field exists."""
        fields = {'title': 'Test'}
        
        with patch.object(entry_processor, '_process_pdfs') as mock_pdfs:
            result = entry_processor.process_entry_files(
                'test2023', fields, regenerate=False, force=False, incremental=False,
                thumbnail_size='600x', verbose=False, update_pdf_metadata=False
            )
            
            assert result is True
            mock_pdfs.assert_not_called()
    
    def test_process_entry_files_success(self, entry_processor):
        """Test process_entry_files successfully."""
        with patch.object(entry_processor, 'bibtex_processor') as mock_bibtex, \
             patch.object(entry_processor, '_process_pdfs') as mock_pdfs, \
             patch.object(entry_processor, '_process_agenda_pdfs', return_value=True), \
             patch.object(entry_processor, '_process_slides_pdfs', return_value=True), \
             patch.object(entry_processor, '_process_images') as mock_images, \
             patch.object(entry_processor, '_process_audio_files', return_value=True), \
             patch.object(entry_processor, '_process_thumbnails_with_priority') as mock_thumbnails, \
             patch.object(entry_processor, 'file_field_manager') as mock_manager, \
             patch.object(entry_processor, 'zip_archive_generator') as mock_zip:
            mock_bibtex.extract_pdf_files.return_value = ['/path/to/file.pdf']
            mock_bibtex.extract_image_files.return_value = []
            mock_bibtex.extract_agenda_pdfs.return_value = []
            mock_bibtex.extract_slides_pdfs.return_value = []
            mock_bibtex.extract_audio_files.return_value = []
            mock_pdfs.return_value = True
            mock_images.return_value = True
            mock_thumbnails.return_value = True
            mock_manager.replace_with_processed.return_value = "PDF:/assets/pdf/file.pdf:application/pdf"
            mock_zip.create_archive.return_value = None
            
            fields = {'file': 'PDF:/path/to/file.pdf:application/pdf'}
            
            result = entry_processor.process_entry_files(
                'test2023', fields, regenerate=False, force=False, incremental=False,
                thumbnail_size='600x', verbose=False, update_pdf_metadata=False
            )
            
            assert result is True
            mock_pdfs.assert_called_once()
    
    def test_process_single_pdf_success(self, entry_processor):
        """Test processing a single PDF file."""
        with patch('os.path.exists', return_value=True), \
             patch.object(entry_processor, 'file_manager') as mock_file, \
             patch.object(entry_processor, 'text_processor') as mock_text:
            mock_text.generate_filename.return_value = 'test.pdf'
            mock_file.copy_file.return_value = True
            
            fields = {}
            result = entry_processor._process_single_pdf(
                'test2023', fields, '/path/to/file.pdf',
                regenerate=False, force=False, verbose=False,
                update_pdf_metadata=False, session_filenames=set()
            )
            
            assert result is True
            assert fields['pdf'] == 'test.pdf'
    
    @patch('os.path.exists')
    def test_process_single_pdf_not_found(self, mock_exists, entry_processor):
        """Test processing PDF when file doesn't exist."""
        mock_exists.return_value = False
        
        fields = {}
        result = entry_processor._process_single_pdf(
            'test2023', fields, '/path/to/nonexistent.pdf',
            regenerate=False, force=False, verbose=False,
            update_pdf_metadata=False, session_filenames=set()
        )
        
        assert result is False
    
    def test_process_images_success(self, entry_processor):
        """Test processing images successfully."""
        with patch.object(entry_processor, 'file_manager') as mock_file:
            mock_file.process_images_for_entry.return_value = {
                'photo': ['photo1.jpg', 'photo2.jpg']
            }
            
            fields = {}
            result = entry_processor._process_images(
                'test2023', fields, ['/path/to/image1.jpg', '/path/to/image2.jpg'],
                regenerate=False, force=False, verbose=False
            )
            
            assert result is True
            assert fields['photos'] == 'photo1.jpg, photo2.jpg'
    
    def test_process_images_no_paths(self, entry_processor):
        """Test processing images when no paths provided."""
        fields = {}
        result = entry_processor._process_images(
            'test2023', fields, [],
            regenerate=False, force=False, verbose=False
        )
        
        assert result is True
    
    def test_process_thumbnails_with_priority(self, entry_processor):
        """Test processing thumbnails with priority logic."""
        with patch.object(entry_processor, 'bibtex_processor') as mock_bibtex, \
             patch.object(entry_processor, '_process_single_thumbnail_file') as mock_single:
            mock_bibtex.get_thumbnail_priority_files.return_value = [
                {'path': '/path/to/thumb.svg', 'type': 'svg', 'priority': 1}
            ]
            mock_single.return_value = True
            
            fields = {'file': 'thumbnail:/path/to/thumb.svg:image/svg+xml'}
            result = entry_processor._process_thumbnails_with_priority(
                'test2023', fields, regenerate=False, force=False,
                thumbnail_size='600x', verbose=False
            )
            
            assert result is True
            mock_single.assert_called_once()
    
    def test_process_single_thumbnail_file_pdf(self, entry_processor):
        """Test processing single thumbnail file from PDF."""
        with patch('os.path.exists', return_value=False) as mock_exists, \
             patch.object(entry_processor, 'file_manager') as mock_file, \
             patch.object(entry_processor, 'text_processor') as mock_text:
            # Source exists; preview path does not (so we generate)
            def exists_side_effect(path):
                return path == '/path/to/file.pdf'
            mock_exists.side_effect = exists_side_effect
            mock_text.generate_filename.return_value = 'preview.jpg'
            mock_file.generate_pdf_thumbnail.return_value = True
            
            fields = {'pdf': 'file.pdf'}
            result = entry_processor._process_single_thumbnail_file(
                'test2023', fields, '/path/to/file.pdf', 'pdf',
                regenerate=False, force=False, thumbnail_size='600x', verbose=False
            )
            
            assert result is True
            assert fields['preview'] == 'preview.jpg'
    
    def test_should_add_preview_field(self, entry_processor):
        """Test should_add_preview_field method."""
        fields = {}
        result = entry_processor._should_add_preview_field(fields)
        
        assert result is True
