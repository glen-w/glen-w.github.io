#!/usr/bin/env python3
"""
Integration tests for end-to-end paper processing workflow.
Uses the current PaperProcessor API (no removed private methods).
"""

import pytest
from unittest.mock import patch, MagicMock

from processing.main import run_main_processing, run_validation, run_post_processing
from processing.config import Configuration


def _args(**kwargs):
    defaults = {
        'bibtex_file': 'source.bib',
        'regenerate': False,
        'force': False,
        'incremental': False,
        'update_metadata': True,
        'thumbnail_size': '600x',
        'test': True,
        'test_count': 2,
        'verbose': False,
        'force_refetch_metadata': False,
        'rename_urls': True,
        'rename_only': False,
        'update_pdf_metadata': False,
        'no_pdf_metadata': True,
        'simple_validate': False,
        'validate': True,
        'no_validate': False,
        'clean_file_field': True,
        'remove_file_field': False,
        'remove_fields': None,
        'keep_file_field': False,
    }
    defaults.update(kwargs)
    return type('Args', (), defaults)()


@pytest.mark.integration
class TestEndToEndProcessing:
    """Integration tests for complete processing workflow."""

    @pytest.fixture
    def config(self):
        return Configuration()

    def test_complete_processing_workflow(self, config, temp_dir, sample_bibtex_content):
        """Test complete processing workflow with valid input."""
        source_bibtex = temp_dir / "source.bib"
        source_bibtex.write_text(sample_bibtex_content)

        with patch('processing.core.paper_processor.PaperProcessor.check_dependencies', return_value=True), \
             patch('processing.core.paper_processor.PaperProcessor.process_papers') as mock_process:
            success = run_main_processing(config, _args(bibtex_file=str(source_bibtex)))
            assert success is True
            mock_process.assert_called_once()

    def test_processing_with_validation(self, config, temp_dir, sample_bibtex_content):
        """Test processing with validation step."""
        source_bibtex = temp_dir / "source.bib"
        source_bibtex.write_text(sample_bibtex_content)

        with patch('processing.core.paper_processor.PaperProcessor.check_dependencies', return_value=True), \
             patch('processing.core.paper_processor.PaperProcessor.process_papers'), \
             patch('processing.main.os.path.exists', return_value=True), \
             patch('processing.main.EnhancedValidator') as mock_val_cls:
            mock_val = MagicMock()
            mock_val.validate_bibtex_file.return_value = {
                'all_passed': True, 'total_entries': 2, 'failed_entries': 0
            }
            mock_val.get_validation_summary.return_value = {'all_passed': True}
            mock_val_cls.return_value = mock_val

            success = run_main_processing(config, _args(bibtex_file=str(source_bibtex)))
            assert success is True

            validation_success = run_validation(config, _args())
            assert validation_success is True

    def test_processing_with_post_processing(self, config, temp_dir, sample_bibtex_content):
        """Test processing with post-processing cleanup."""
        source_bibtex = temp_dir / "source.bib"
        source_bibtex.write_text(sample_bibtex_content)

        with patch('processing.core.paper_processor.PaperProcessor.check_dependencies', return_value=True), \
             patch('processing.core.paper_processor.PaperProcessor.process_papers'), \
             patch('processing.main.os.path.exists', return_value=True), \
             patch('processing.main.PostProcessor') as mock_post_cls:
            mock_post = MagicMock()
            mock_post.clean_file_field_only.return_value = True
            mock_post.remove_file_field_entirely.return_value = True
            mock_post_cls.return_value = mock_post

            success = run_main_processing(config, _args(bibtex_file=str(source_bibtex)))
            assert success is True

            post_success = run_post_processing(config, _args(clean_file_field=True, remove_file_field=False))
            assert post_success is True
            mock_post.clean_file_field_only.assert_called()

    def test_processing_with_malformed_input(self, config, temp_dir, malformed_bibtex_content):
        """Test processing with malformed input — process_papers is invoked."""
        source_bibtex = temp_dir / "source.bib"
        source_bibtex.write_text(malformed_bibtex_content)

        with patch('processing.core.paper_processor.PaperProcessor.check_dependencies', return_value=True), \
             patch('processing.core.paper_processor.PaperProcessor.process_papers') as mock_process:
            success = run_main_processing(config, _args(bibtex_file=str(source_bibtex)))
            assert success is True
            mock_process.assert_called_once()

    def test_processing_error_handling(self, config, temp_dir, sample_bibtex_content):
        """Test that exceptions in process_papers return False."""
        source_bibtex = temp_dir / "source.bib"
        source_bibtex.write_text(sample_bibtex_content)

        with patch('processing.core.paper_processor.PaperProcessor.check_dependencies', return_value=True), \
             patch('processing.core.paper_processor.PaperProcessor.process_papers',
                   side_effect=RuntimeError('boom')):
            success = run_main_processing(config, _args(bibtex_file=str(source_bibtex)))
            assert success is False
