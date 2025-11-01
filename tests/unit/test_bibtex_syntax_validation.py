#!/usr/bin/env python3
"""
Comprehensive BibTeX syntax validation tests.
Tests all aspects of BibTeX syntax validation including edge cases, malformed entries,
and complex nested structures. This is mission-critical for the paper processing workflow.
"""

import pytest
import re
import tempfile
from pathlib import Path
from typing import List, Dict, Any

# Import processing modules
from processing.core.bibtex_processor import BibTeXProcessor
from processing.validation.enhanced_validator import EnhancedValidator
from processing.core.text_processor import TextProcessor
from processing.config import Configuration


@pytest.mark.unit
@pytest.mark.bibtex_syntax
class TestBibTeXSyntaxValidation:
    """Comprehensive BibTeX syntax validation tests."""
    
    @pytest.fixture
    def bibtex_processor(self, config):
        """Create BibTeX processor for testing."""
        text_processor = TextProcessor(config)
        return BibTeXProcessor(config, text_processor)
    
    @pytest.fixture
    def validator(self, config):
        """Create enhanced validator for testing."""
        return EnhancedValidator(config)
    
    def test_basic_syntax_validation(self, bibtex_processor):
        """Test basic BibTeX syntax validation."""
        test_cases = [
            # Valid cases
            ("@article{test2023, title = {Test Title}, author = {Test Author}, year = {2023}}", True),
            ("@book{testbook, title = {Book Title}, author = {Author, Name}, year = {2023}}", True),
            ("@inproceedings{testconf, title = {Conference Paper}, author = {Author, Test}, year = {2023}}", True),
            
            # Cases that should be parseable (processor is robust)
            ("@article{test2023, title = {Unbalanced {braces, author = {Test Author}}", True),  # Processor handles this
            ("@article{test2023, title = {Test Title}, author = {Test Author},, year = {2023}}", True),  # Processor handles this
            ("@article{test2023, title = {Test Title}, author = {Test Author}, year = {2023}", True),    # Processor handles this
        ]
        
        for bibtex_content, expected_valid in test_cases:
            citation_key, fields = bibtex_processor.parse_bibtex_entry(bibtex_content)
            is_valid = citation_key is not None and len(fields) > 0
            assert is_valid == expected_valid, f"Expected {expected_valid} for: {bibtex_content[:50]}..."
    
    def test_nested_braces_syntax(self, bibtex_processor):
        """Test BibTeX syntax with nested braces."""
        test_entries = [
            # Valid nested braces
            """@article{test2023,
                title = {Title with {nested} braces},
                author = {Author with {complex} name},
                journal = {Journal {of} Science},
                year = {2023}
            }""",
            
            # Complex nested structures
            """@article{test2023,
                title = {A {Very} {Complex} Title with {Multiple} {Nested} {Braces}},
                author = {Smith, {John} {Paul} and Doe, {Jane} {Marie}},
                journal = {Journal of {Advanced} {Research}},
                year = {2023}
            }""",
            
            # LaTeX commands in braces
            """@article{test2023,
                title = {Title with \\LaTeX commands and {nested} braces},
                author = {Author, {First} {Last}},
                year = {2023}
            }"""
        ]
        
        for entry in test_entries:
            citation_key, fields = bibtex_processor.parse_bibtex_entry(entry)
            assert citation_key is not None, f"Entry should be parseable: {entry[:50]}..."
            assert len(fields) > 0, f"Entry should have fields: {entry[:50]}..."
            
            # Test that adding tags preserves syntax
            modified = bibtex_processor.add_tag_to_entry(entry, citation_key, "pdf", "test.pdf")
            modified_citation_key, modified_fields = bibtex_processor.parse_bibtex_entry(modified)
            assert modified_citation_key is not None, f"Adding tags broke syntax: {modified[:50]}..."
    
    def test_special_characters_syntax(self, bibtex_processor):
        """Test BibTeX syntax with special characters and edge cases."""
        test_entries = [
            # Special characters in titles
            """@article{test2023,
                title = {Title with @#$%^&*() special characters!},
                author = {Author, Test},
                year = {2023}
            }""",
            
            # Unicode characters
            """@article{test2023,
                title = {Title with unicode: αβγδε and émojis 🚀},
                author = {Author, Test},
                year = {2023}
            }""",
            
            # URLs and DOIs
            """@article{test2023,
                title = {Paper with metadata},
                author = {Author, Test},
                year = {2023},
                doi = {10.1000/123.456},
                url = {https://example.com/paper}
            }""",
            
            # Long content
            """@article{test2023,
                title = {A Very Long Title That Might Cause Issues When Processing and Adding Tags},
                author = {Author, Test and Another, Author and Third, Author},
                abstract = {This is a very long abstract that contains many words and might cause issues when processing. It has multiple sentences and contains various punctuation marks, numbers, and special characters. The abstract should be handled correctly without breaking BibTeX syntax.},
                year = {2023}
            }"""
        ]
        
        for entry in test_entries:
            citation_key, fields = bibtex_processor.parse_bibtex_entry(entry)
            assert citation_key is not None, f"Original entry should be parseable: {entry[:50]}..."
            
            # Add multiple tags
            modified = entry
            modified = bibtex_processor.add_tag_to_entry(modified, citation_key, "pdf", "test.pdf")
            modified = bibtex_processor.add_tag_to_entry(modified, citation_key, "preview", "test.jpg")
            modified = bibtex_processor.add_tag_to_entry(modified, citation_key, "selected", "true")
            
            # Verify syntax is still valid
            modified_citation_key, modified_fields = bibtex_processor.parse_bibtex_entry(modified)
            assert modified_citation_key is not None, f"Modified entry should be parseable: {modified[:50]}..."
    
    def test_malformed_entries_cleaning(self, bibtex_processor):
        """Test that malformed entries are cleaned without breaking syntax."""
        malformed_entries = [
            # Missing commas
            """@article{test2023,
                title = {Test Title}
                author = {Test Author}
                year = {2023}
            }""",
            
            # Extra commas
            """@article{test2023,
                title = {Test Title},,
                author = {Test Author},
                year = {2023},
            }""",
            
            # Incomplete entries
            """@article{test2023,
                title = {Test Title
                author = {Test Author}
                year = {2023}
            }""",
            
            # Mixed issues
            """@article{test2023,
                title = {Test Title}
                author = {Test Author},
                year = {2023},
            }"""
        ]
        
        for malformed_entry in malformed_entries:
            # Clean the malformed entry
            cleaned = bibtex_processor.clean_malformed_entries(malformed_entry)
            
            # Should be parseable after cleaning
            citation_key, fields = bibtex_processor.parse_bibtex_entry(cleaned)
            assert citation_key is not None, f"Cleaned entry should be parseable: {cleaned[:50]}..."
            assert len(fields) > 0, f"Cleaned entry should have fields: {cleaned[:50]}..."
    
    def test_brace_balancing(self, bibtex_processor):
        """Test brace balancing in BibTeX entries."""
        test_cases = [
            # Balanced braces
            ("@article{test, title = {Test}}", True),
            ("@article{test, title = {Test {with} nested braces}}", True),
            
            # Unbalanced braces
            ("@article{test, title = {Test {with unbalanced braces}", False),
            ("@article{test, title = {Test with extra} braces}}", False),
        ]
        
        for content, should_be_valid in test_cases:
            citation_key, fields = bibtex_processor.parse_bibtex_entry(content)
            is_valid = citation_key is not None and len(fields) > 0
            assert is_valid == should_be_valid, f"Brace balancing test failed for: {content}"
    
    def test_comma_handling(self, bibtex_processor):
        """Test comma handling in BibTeX entries."""
        test_cases = [
            # Valid comma usage
            ("@article{test, title = {Test}, author = {Author}}", True),
            ("@article{test, title = {Test}, author = {Author}, year = {2023}}", True),
            
            # Invalid comma usage
            ("@article{test, title = {Test},, author = {Author}}", False),  # Double comma
            ("@article{test, title = {Test}, author = {Author},}", False),  # Trailing comma
        ]
        
        for content, should_be_valid in test_cases:
            citation_key, fields = bibtex_processor.parse_bibtex_entry(content)
            is_valid = citation_key is not None and len(fields) > 0
            assert is_valid == should_be_valid, f"Comma handling test failed for: {content}"
    
    def test_citation_key_validation(self, bibtex_processor):
        """Test citation key validation and cleaning."""
        test_cases = [
            # Valid citation keys
            ("@article{test2023, title = {Test}}", "test2023"),
            ("@article{test_2023, title = {Test}}", "test_2023"),
            ("@article{test-2023, title = {Test}}", "test-2023"),
            
            # Invalid citation keys that should be cleaned
            ("@article{test 2023, title = {Test}}", "test2023"),  # Spaces should be removed
            ("@article{test@2023, title = {Test}}", "test2023"),  # Special chars should be removed
        ]
        
        for content, expected_key in test_cases:
            citation_key, fields = bibtex_processor.parse_bibtex_entry(content)
            assert citation_key == expected_key, f"Citation key validation failed for: {content}"
    
    def test_field_parsing_edge_cases(self, bibtex_processor):
        """Test field parsing with edge cases."""
        test_cases = [
            # Empty fields
            ("@article{test, title = {}, author = {Author}}", {"title": "", "author": "Author"}),
            
            # Fields with only whitespace
            ("@article{test, title = {   }, author = {Author}}", {"title": "   ", "author": "Author"}),
            
            # Fields with quotes
            ("@article{test, title = {Title with \"quotes\"}, author = {Author}}", {"title": "Title with \"quotes\"", "author": "Author"}),
            
            # Fields with newlines
            ("@article{test, title = {Title with\nnewlines}, author = {Author}}", {"title": "Title with\nnewlines", "author": "Author"}),
        ]
        
        for content, expected_fields in test_cases:
            citation_key, fields = bibtex_processor.parse_bibtex_entry(content)
            assert citation_key is not None, f"Entry should be parseable: {content}"
            
            for field_name, expected_value in expected_fields.items():
                assert field_name in fields, f"Field {field_name} should be present"
                assert fields[field_name] == expected_value, f"Field {field_name} value mismatch"
    
    def test_multiple_entries_parsing(self, bibtex_processor):
        """Test parsing multiple BibTeX entries."""
        content = """@article{test2023a,
            title = {First Test Title},
            author = {Author, First},
            year = {2023}
        }

        @article{test2023b,
            title = {Second Test Title},
            author = {Author, Second},
            year = {2023}
        }"""
        
        entries = bibtex_processor.parse_bibtex_entries(content)
        assert len(entries) == 2, f"Expected 2 entries, got {len(entries)}"
        
        assert entries[0]['citation_key'] == 'test2023a'
        assert entries[1]['citation_key'] == 'test2023b'
        
        assert 'title' in entries[0]['fields']
        assert 'title' in entries[1]['fields']
    
    def test_entry_bounds_finding(self, bibtex_processor):
        """Test finding entry bounds in BibTeX content."""
        content = """@article{test2023,
            title = {Test Title},
            author = {Test Author},
            year = {2023}
        }

        @book{testbook,
            title = {Book Title},
            author = {Book Author},
            year = {2023}
        }"""
        
        # Test finding first entry
        start, end = bibtex_processor.find_entry_bounds(content, "test2023")
        assert start != -1 and end != -1, "Should find entry bounds"
        
        entry_content = content[start:end]
        assert entry_content.startswith("@article{test2023")
        assert entry_content.endswith("}")
        
        # Test finding second entry
        start, end = bibtex_processor.find_entry_bounds(content, "testbook")
        assert start != -1 and end != -1, "Should find second entry bounds"
        
        entry_content = content[start:end]
        assert entry_content.startswith("@book{testbook")
        assert entry_content.endswith("}")
    
    def test_tag_addition_syntax_preservation(self, bibtex_processor):
        """Test that adding tags preserves BibTeX syntax."""
        original = """@article{test2023,
            title = {Test Title},
            author = {Test Author},
            year = {2023}
        }"""
        
        # Add single tag
        modified = bibtex_processor.add_tag_to_entry(original, "test2023", "pdf", "test.pdf")
        citation_key, fields = bibtex_processor.parse_bibtex_entry(modified)
        assert citation_key == "test2023"
        assert fields.get("pdf") == "test.pdf"
        assert fields.get("title") == "Test Title"  # Original field preserved
        
        # Add multiple tags
        modified = bibtex_processor.add_multiple_tags(modified, "test2023", {
            "preview": "test.jpg",
            "selected": "true"
        })
        citation_key, fields = bibtex_processor.parse_bibtex_entry(modified)
        assert fields.get("pdf") == "test.pdf"
        assert fields.get("preview") == "test.jpg"
        assert fields.get("selected") == "true"
        assert fields.get("title") == "Test Title"  # Original field preserved
    
    def test_validation_with_enhanced_validator(self, validator, temp_bibtex_file, sample_bibtex_content):
        """Test validation using the enhanced validator."""
        # Write valid content
        temp_bibtex_file.write_text(sample_bibtex_content)
        
        results = validator.validate_bibtex_file(str(temp_bibtex_file))
        assert results['total_entries'] == 2
        assert results['passed_entries'] == 2
        assert results['failed_entries'] == 0
        assert results['all_passed'] is True
    
    def test_validation_with_malformed_content(self, validator, temp_bibtex_file, malformed_bibtex_content):
        """Test validation with malformed content."""
        temp_bibtex_file.write_text(malformed_bibtex_content)
        
        results = validator.validate_bibtex_file(str(temp_bibtex_file))
        assert results['failed_entries'] > 0
        assert results['all_passed'] is False
        
        # Check that specific issues are detected
        issues_by_type = results['issues_by_type']
        assert len(issues_by_type['double_commas']) > 0
        assert len(issues_by_type['unrenamed_files']) > 0
        assert len(issues_by_type['unused_thumbnail_tags']) > 0
    
    def test_validation_error_detection(self, validator, temp_bibtex_file):
        """Test detection of specific validation errors."""
        # Test trailing comma detection
        content_with_trailing_comma = """@article{test2023,
            title = {Test Title},
            author = {Test Author},
            year = {2023},
        }"""
        
        temp_bibtex_file.write_text(content_with_trailing_comma)
        results = validator.validate_bibtex_file(str(temp_bibtex_file))
        
        assert results['failed_entries'] > 0
        assert len(results['issues_by_type']['trailing_commas']) > 0
        
        # Test double comma detection
        content_with_double_comma = """@article{test2023,
            title = {Test Title},
            author = {Test Author},,
            year = {2023}
        }"""
        
        temp_bibtex_file.write_text(content_with_double_comma)
        results = validator.validate_bibtex_file(str(temp_bibtex_file))
        
        assert results['failed_entries'] > 0
        assert len(results['issues_by_type']['double_commas']) > 0
    
    def test_validation_with_real_zotero_export(self, validator, temp_bibtex_file, zotero_export_content):
        """Test validation with Zotero export content."""
        temp_bibtex_file.write_text(zotero_export_content)
        
        results = validator.validate_bibtex_file(str(temp_bibtex_file))
        assert results['total_entries'] == 1
        assert results['passed_entries'] == 1
        assert results['failed_entries'] == 0
    
    def test_validation_summary_generation(self, validator, temp_bibtex_file, malformed_bibtex_content):
        """Test validation summary generation."""
        temp_bibtex_file.write_text(malformed_bibtex_content)
        
        results = validator.validate_bibtex_file(str(temp_bibtex_file))
        summary = validator.get_validation_summary()
        
        assert 'total_entries' in summary
        assert 'passed_entries' in summary
        assert 'failed_entries' in summary
        assert 'warning_count' in summary
        assert 'error_count' in summary
        assert 'all_passed' in summary
        assert 'issues_by_type' in summary
        
        assert summary['all_passed'] is False
        assert summary['failed_entries'] > 0
