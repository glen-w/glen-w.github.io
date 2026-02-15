#!/usr/bin/env python3
"""
Unit tests for PaperProcessor class.
Tests orchestration logic and workflow coordination.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

from processing.core.paper_processor import PaperProcessor
from processing.config import Configuration


@pytest.mark.unit
class TestPaperProcessor:
    """Unit tests for PaperProcessor class."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return Configuration()
    
    @pytest.fixture
    def processor(self, config):
        """Create PaperProcessor instance for testing."""
        return PaperProcessor(config)
    
    def test_initialization(self, processor):
        """Test that PaperProcessor initializes correctly."""
        assert processor.config is not None
        assert processor.text_processor is not None
        assert processor.file_manager is not None
        assert processor.pdf_processor is not None
        assert processor.bibtex_processor is not None
        assert processor.entry_processor is not None
        assert processor.file_field_parser is not None
        assert processor.file_field_manager is not None
    
    def test_check_dependencies_all_present(self, processor):
        """Test check_dependencies when all dependencies are available."""
        with patch('processing.core.paper_processor.PyPDF2'), \
             patch('processing.core.paper_processor.bibtexparser'), \
             patch('processing.core.paper_processor.requests'), \
             patch('processing.core.paper_processor.PIL'):
            result = processor.check_dependencies()
            assert result is True
    
    def test_check_dependencies_missing(self, processor):
        """Test check_dependencies when dependencies are missing."""
        with patch('builtins.__import__', side_effect=ImportError("No module named 'PyPDF2'")):
            result = processor.check_dependencies()
            assert result is False
    
    @patch('shutil.copy2')
    def test_copy_source_to_working_success(self, mock_copy, processor):
        """Test copying source file to working file."""
        mock_copy.return_value = None
        
        result = processor._copy_source_to_working("source.bib", "working.bib")
        
        assert result is True
        mock_copy.assert_called_once_with("source.bib", "working.bib")
    
    @patch('shutil.copy2')
    def test_copy_source_to_working_failure(self, mock_copy, processor):
        """Test copying source file when copy fails."""
        mock_copy.side_effect = Exception("Permission denied")
        
        result = processor._copy_source_to_working("source.bib", "working.bib")
        
        assert result is False
    
    @patch('builtins.open', new_callable=mock_open, read_data="@article{test, title = {Test}}")
    def test_read_bibtex_file_success(self, mock_file, processor):
        """Test reading BibTeX file successfully."""
        result = processor._read_bibtex_file("test.bib")
        
        assert result == "@article{test, title = {Test}}"
        mock_file.assert_called_once_with("test.bib", 'r', encoding='utf-8')
    
    @patch('builtins.open', side_effect=FileNotFoundError("File not found"))
    def test_read_bibtex_file_not_found(self, mock_file, processor):
        """Test reading BibTeX file when file doesn't exist."""
        result = processor._read_bibtex_file("nonexistent.bib")
        
        assert result is None
    
    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('os.remove')
    def test_cleanup_existing_files(self, mock_remove, mock_listdir, mock_exists, processor):
        """Test cleanup of existing files in regenerate mode."""
        mock_exists.return_value = True
        mock_listdir.side_effect = [
            ['file1.pdf', 'file2.pdf'],  # PDF_DIR
            ['thumb1.jpg', 'thumb2.jpg']  # PREVIEW_DIR
        ]
        
        processor._cleanup_existing_files()
        
        assert mock_remove.call_count == 4  # 2 PDFs + 2 thumbnails
    
    @patch.object(PaperProcessor, '_read_bibtex_file')
    @patch.object(PaperProcessor, '_process_entries')
    @patch('builtins.open', new_callable=mock_open)
    @patch('shutil.copy2')
    def test_process_papers_basic_flow(self, mock_copy, mock_file, mock_process, mock_read, processor):
        """Test basic process_papers workflow."""
        mock_read.return_value = "@article{test, title = {Test}}"
        mock_copy.return_value = None
        
        processor.process_papers(
            source_bibtex_file="source.bib",
            test_mode=True,
            test_count=1
        )
        
        mock_read.assert_called_once()
        mock_process.assert_called_once()
    
    @patch.object(PaperProcessor, '_read_bibtex_file')
    def test_process_papers_read_failure(self, mock_read, processor):
        """Test process_papers when file read fails."""
        mock_read.return_value = None
        
        processor.process_papers(source_bibtex_file="source.bib")
        
        # Should return early without processing
    
    @patch.object(PaperProcessor, 'entry_processor')
    @patch.object(PaperProcessor, 'bibtex_processor')
    def test_process_entries_delegates_to_entry_processor(self, mock_bibtex, mock_entry, processor):
        """Test that _process_entries delegates to entry_processor."""
        mock_bibtex.parse_bibtex_entries.return_value = [
            {'citation_key': 'test2023', 'fields': {'title': 'Test'}, 'content': '@article{test2023, title = {Test}}'}
        ]
        mock_entry.process_entry.return_value = True
        
        processor._process_entries(
            working_file="test.bib",
            regenerate=False,
            force=False,
            incremental=False,
            update_metadata=True,
            thumbnail_size='600x',
            test_mode=True,
            test_count=1,
            verbose=False,
            force_refetch_metadata=False,
            rename_urls=True,
            rename_only=False,
            update_pdf_metadata=False,
            content="@article{test2023, title = {Test}}",
        )
        
        mock_entry.process_entry.assert_called_once()
    
    @patch.object(PaperProcessor, 'file_field_manager')
    def test_clean_file_field_in_content(self, mock_manager, processor):
        """Test cleaning file field in BibTeX content."""
        mock_manager.replace_with_processed.return_value = "PDF:/assets/pdf/file.pdf:application/pdf"
        
        content = "@article{test, file = {PDF:/old/path.pdf:application/pdf}, title = {Test}}"
        result = processor._clean_file_field_in_content(content, {'pdf': 'file.pdf'})
        
        assert "PDF:/assets/pdf/file.pdf:application/pdf" in result
        mock_manager.replace_with_processed.assert_called_once()
    
    @patch.object(PaperProcessor, 'bibtex_processor')
    @patch.object(PaperProcessor, 'formatter')
    @patch('builtins.open', new_callable=mock_open)
    def test_write_updated_bibtex_from_entries(self, mock_file, mock_formatter, mock_bibtex, processor):
        """Test writing updated BibTeX from entries."""
        entries = [
            {
                'citation_key': 'test2023',
                'fields': {'title': 'Test', 'pdf': 'test.pdf'},
                'content': '@article{test2023, title = {Test}}'
            }
        ]
        mock_bibtex.rename_url_fields.return_value = ("@article{test2023, title = {Test}}", 0)
        mock_formatter.format_entry_from_content.return_value = "@article{test2023, title = {Test}}"
        
        processor._write_updated_bibtex_from_entries(entries, "test.bib", rename_urls=True)
        
        mock_file.assert_called()
        mock_bibtex.rename_url_fields.assert_called_once()
    
    def test_update_entry_content_adds_new_fields(self, processor):
        """Test that _update_entry_content adds new fields."""
        entry_content = "@article{test2023,\n\ttitle = {Test}\n}"
        fields = {'pdf': 'test.pdf', 'preview': 'preview.jpg'}
        
        result = processor._update_entry_content(entry_content, fields)
        
        assert 'pdf = {test.pdf}' in result
        assert 'preview = {preview.jpg}' in result
    
    def test_update_entry_content_updates_annote(self, processor):
        """Test that _update_entry_content updates annote field."""
        entry_content = "@article{test2023,\n\ttitle = {Test},\n\tannote = {old}\n}"
        fields = {'annote': '[audio]\nassets/audio/file.mp3'}
        
        result = processor._update_entry_content(entry_content, fields)
        
        assert '[audio]' in result
        assert 'assets/audio/file.mp3' in result
    
    def test_update_entry_content_handles_missing_closing_brace(self, processor):
        """Test that _update_entry_content handles missing closing brace."""
        entry_content = "@article{test2023,\n\ttitle = {Test}"
        fields = {'pdf': 'test.pdf'}
        
        result = processor._update_entry_content(entry_content, fields)
        
        # Should return original content unchanged
        assert result == entry_content

    def test_incremental_write_preserves_skipped_block_exactly(self, processor):
        """Incremental: entry with _skipped and _original_content (weird spacing) is emitted exact bytes."""
        raw_block = "@article{key99,\n  title = {  Spaced  },\n  preview = {x.jpg}\n}\n"
        entries = [
            {
                'citation_key': 'key99',
                'fields': {'title': 'Spaced', 'preview': 'x.jpg'},
                'content': '@article{key99, title = {Spaced}}',
                '_skipped': True,
                '_original_content': raw_block.rstrip(),
            }
        ]
        with patch('builtins.open', new_callable=mock_open) as mopen:
            processor._write_updated_bibtex_from_entries(entries, "out.bib", rename_urls=False, incremental=True)
        written = mopen().write.call_args[0][0]
        assert raw_block.rstrip() in written
        assert written.endswith('\n')
        assert written.strip() == raw_block.rstrip()

    def test_merge_keeps_processed_fields_from_existing(self, processor):
        """Merge: export lacks preview, existing has preview -> merged entry has preview from existing."""
        export_content = "@article{key1,\n\ttitle = {New Title}\n}\n"
        working_content = "@article{key1,\n\ttitle = {Old},\n\tpreview = {existing_preview.jpg}\n}\n"
        merged = processor._merge_export_with_existing(export_content, working_content)
        assert len(merged) == 1
        assert merged[0]['fields'].get('preview') == 'existing_preview.jpg'
        assert merged[0]['_original_content'].rstrip() == working_content.rstrip()
