#!/usr/bin/env python3
"""
Unit tests for TextProcessor class.
Tests text cleaning and processing functionality.
"""

import pytest
from processing.core.text_processor import TextProcessor
from processing.config import Configuration


@pytest.mark.unit
class TestTextProcessor:
    """Unit tests for TextProcessor class."""
    
    @pytest.fixture
    def text_processor(self, config):
        """Create text processor for testing."""
        return TextProcessor(config)
    
    def test_clean_citation_key(self, text_processor):
        """Test citation key cleaning."""
        # Test removing invalid characters
        assert text_processor.clean_citation_key("test@2023") == "test2023"
        assert text_processor.clean_citation_key("test 2023") == "test2023"
        assert text_processor.clean_citation_key("test-2023") == "test-2023"  # Valid
        assert text_processor.clean_citation_key("test_2023") == "test_2023"  # Valid
    
    def test_clean_braces_in_field_value(self, text_processor):
        """Test cleaning braces from field values."""
        # Test removing internal braces
        assert text_processor.clean_braces_in_field_value("Title with {nested} braces") == "Title with nested braces"
        assert text_processor.clean_braces_in_field_value("Simple title") == "Simple title"
        assert text_processor.clean_braces_in_field_value("{Title}") == "Title"
    
    def test_clean_nested_braces(self, text_processor):
        """Test cleaning nested braces."""
        # Test various nested brace patterns
        assert text_processor.clean_nested_braces("Simple text") == "Simple text"
        assert text_processor.clean_nested_braces("Text with {single} braces") == "Text with single braces"
        assert text_processor.clean_nested_braces("Text with {nested {braces}}") == "Text with nested braces"
        assert text_processor.clean_nested_braces("Complex {text {with {multiple {levels}}}} of nesting") == "Complex text with multiple levels of nesting"
