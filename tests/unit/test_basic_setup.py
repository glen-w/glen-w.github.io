#!/usr/bin/env python3
"""
Basic setup tests to verify the test environment is working correctly.
"""

import pytest
from processing.config import Configuration
from processing.core.bibtex_processor import BibTeXProcessor
from processing.core.text_processor import TextProcessor
from processing.validation.enhanced_validator import EnhancedValidator


@pytest.mark.unit
class TestBasicSetup:
    """Basic setup tests to verify test environment."""
    
    def test_imports_work(self):
        """Test that all main modules can be imported."""
        # This test will fail if there are import issues
        assert True
    
    def test_config_creation(self, config):
        """Test that configuration can be created."""
        assert config is not None
        assert hasattr(config, 'WORKING_BIBTEX_FILE')
    
    def test_bibtex_processor_creation(self, config):
        """Test that BibTeX processor can be created."""
        text_processor = TextProcessor(config)
        bibtex_processor = BibTeXProcessor(config, text_processor)
        assert bibtex_processor is not None
    
    def test_validator_creation(self, config):
        """Test that validator can be created."""
        validator = EnhancedValidator(config)
        assert validator is not None
    
    def test_basic_bibtex_parsing(self, bibtex_processor, sample_bibtex_content):
        """Test basic BibTeX parsing functionality."""
        citation_key, fields = bibtex_processor.parse_bibtex_entry(sample_bibtex_content)
        assert citation_key is not None
        assert len(fields) > 0
    
    def test_basic_validation(self, validator, temp_bibtex_file, sample_bibtex_content):
        """Test basic validation functionality."""
        temp_bibtex_file.write_text(sample_bibtex_content)
        results = validator.validate_bibtex_file(str(temp_bibtex_file))
        assert results['total_entries'] > 0
