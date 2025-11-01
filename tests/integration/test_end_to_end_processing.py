#!/usr/bin/env python3
"""
Integration tests for end-to-end paper processing workflow.
Tests the complete processing pipeline from BibTeX input to final output.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from processing.main import run_main_processing, run_validation, run_post_processing
from processing.config import Configuration


@pytest.mark.integration
class TestEndToEndProcessing:
    """Integration tests for complete processing workflow."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return Configuration()
    
    def test_complete_processing_workflow(self, config, temp_dir, sample_bibtex_content):
        """Test complete processing workflow with valid input."""
        # Create test files
        source_bibtex = temp_dir / "source.bib"
        source_bibtex.write_text(sample_bibtex_content)
        
        # Mock external dependencies
        with patch('processing.core.paper_processor.PaperProcessor.check_dependencies', return_value=True), \
             patch('processing.core.paper_processor.PaperProcessor._process_pdf_files', return_value=(True, sample_bibtex_content)), \
             patch('processing.core.paper_processor.PaperProcessor._add_image_tags', return_value=sample_bibtex_content), \
             patch('processing.core.paper_processor.PaperProcessor._update_pdf_metadata'):
            
            # Run main processing
            success = run_main_processing(config, type('Args', (), {
                'bibtex_file': str(source_bibtex),
                'regenerate': False,
                'force': False,
                'update_metadata': True,
                'thumbnail_size': '600x',
                'test_mode': True,
                'test_count': 2,
                'verbose': False,
                'force_refetch_metadata': False,
                'rename_urls': True,
                'rename_only': False
            })())
            
            assert success is True
    
    def test_processing_with_validation(self, config, temp_dir, sample_bibtex_content):
        """Test processing with validation step."""
        # Create test files
        source_bibtex = temp_dir / "source.bib"
        output_bibtex = temp_dir / "papers.bib"
        source_bibtex.write_text(sample_bibtex_content)
        output_bibtex.write_text(sample_bibtex_content)
        
        # Mock processing
        with patch('processing.core.paper_processor.PaperProcessor.check_dependencies', return_value=True), \
             patch('processing.core.paper_processor.PaperProcessor._process_pdf_files', return_value=(True, sample_bibtex_content)), \
             patch('processing.core.paper_processor.PaperProcessor._add_image_tags', return_value=sample_bibtex_content), \
             patch('processing.core.paper_processor.PaperProcessor._update_pdf_metadata'):
            
            # Run processing
            success = run_main_processing(config, type('Args', (), {
                'bibtex_file': str(source_bibtex),
                'regenerate': False,
                'force': False,
                'update_metadata': True,
                'thumbnail_size': '600x',
                'test_mode': True,
                'test_count': 2,
                'verbose': False,
                'force_refetch_metadata': False,
                'rename_urls': True,
                'rename_only': False
            })())
            
            assert success is True
            
            # Run validation
            validation_success = run_validation(config, type('Args', (), {
                'simple_validate': False,
                'validate': True,
                'no_validate': False
            })())
            
            assert validation_success is True
    
    def test_processing_with_post_processing(self, config, temp_dir, sample_bibtex_content):
        """Test processing with post-processing cleanup."""
        # Create test files
        source_bibtex = temp_dir / "source.bib"
        output_bibtex = temp_dir / "papers.bib"
        source_bibtex.write_text(sample_bibtex_content)
        output_bibtex.write_text(sample_bibtex_content)
        
        # Mock processing
        with patch('processing.core.paper_processor.PaperProcessor.check_dependencies', return_value=True), \
             patch('processing.core.paper_processor.PaperProcessor._process_pdf_files', return_value=(True, sample_bibtex_content)), \
             patch('processing.core.paper_processor.PaperProcessor._add_image_tags', return_value=sample_bibtex_content), \
             patch('processing.core.paper_processor.PaperProcessor._update_pdf_metadata'):
            
            # Run processing
            success = run_main_processing(config, type('Args', (), {
                'bibtex_file': str(source_bibtex),
                'regenerate': False,
                'force': False,
                'update_metadata': True,
                'thumbnail_size': '600x',
                'test_mode': True,
                'test_count': 2,
                'verbose': False,
                'force_refetch_metadata': False,
                'rename_urls': True,
                'rename_only': False
            })())
            
            assert success is True
            
            # Run post-processing
            post_success = run_post_processing(config, type('Args', (), {
                'clean_file_field': True,
                'remove_file_field': False,
                'remove_fields': None
            })())
            
            assert post_success is True
    
    def test_processing_with_malformed_input(self, config, temp_dir, malformed_bibtex_content):
        """Test processing with malformed input."""
        # Create test files
        source_bibtex = temp_dir / "source.bib"
        source_bibtex.write_text(malformed_bibtex_content)
        
        # Mock processing
        with patch('processing.core.paper_processor.PaperProcessor.check_dependencies', return_value=True), \
             patch('processing.core.paper_processor.PaperProcessor._process_pdf_files', return_value=(True, malformed_bibtex_content)), \
             patch('processing.core.paper_processor.PaperProcessor._add_image_tags', return_value=malformed_bibtex_content), \
             patch('processing.core.paper_processor.PaperProcessor._update_pdf_metadata'):
            
            # Run processing - should handle malformed input gracefully
            success = run_main_processing(config, type('Args', (), {
                'bibtex_file': str(source_bibtex),
                'regenerate': False,
                'force': False,
                'update_metadata': True,
                'thumbnail_size': '600x',
                'test_mode': True,
                'test_count': 1,
                'verbose': False,
                'force_refetch_metadata': False,
                'rename_urls': True,
                'rename_only': False
            })())
            
            # Should still succeed as malformed entries are cleaned
            assert success is True
    
    def test_processing_error_handling(self, config, temp_dir, sample_bibtex_content):
        """Test error handling during processing."""
        # Create test files
        source_bibtex = temp_dir / "source.bib"
        source_bibtex.write_text(sample_bibtex_content)
        
        # Mock processing to raise exception
        with patch('processing.core.paper_processor.PaperProcessor.check_dependencies', return_value=True), \
             patch('processing.core.paper_processor.PaperProcessor._process_pdf_files', side_effect=Exception("Processing error")):
            
            # Run processing - should handle error gracefully
            success = run_main_processing(config, type('Args', (), {
                'bibtex_file': str(source_bibtex),
                'regenerate': False,
                'force': False,
                'update_metadata': True,
                'thumbnail_size': '600x',
                'test_mode': True,
                'test_count': 2,
                'verbose': False,
                'force_refetch_metadata': False,
                'rename_urls': True,
                'rename_only': False
            })())
            
            # Should fail gracefully
            assert success is False
