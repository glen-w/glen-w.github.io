#!/usr/bin/env python3
"""
Unit tests for EnhancedValidator class.
Tests all validation methods and error detection functionality.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from processing.validation.enhanced_validator import EnhancedValidator
from processing.config import Configuration


@pytest.mark.unit
class TestEnhancedValidator:
    """Unit tests for EnhancedValidator class."""
    
    @pytest.fixture
    def validator(self, config):
        """Create enhanced validator for testing."""
        return EnhancedValidator(config)
    
    def test_initialization(self, validator):
        """Test validator initialization."""
        assert validator.validation_results['total_entries'] == 0
        assert validator.validation_results['passed_entries'] == 0
        assert validator.validation_results['failed_entries'] == 0
        assert len(validator.validation_results['warnings']) == 0
        assert len(validator.validation_results['errors']) == 0
        
        # Check issue types are initialized
        issue_types = validator.validation_results['issues_by_type']
        expected_types = [
            'trailing_commas', 'double_commas', 'internal_braces',
            'uncleared_file_tags', 'unused_thumbnail_tags', 'unrenamed_files',
            'bibtex_syntax', 'unmatched_braces', 'malformed_entries'
        ]
        for issue_type in expected_types:
            assert issue_type in issue_types
            assert isinstance(issue_types[issue_type], list)
    
    def test_validate_bibtex_file_success(self, validator, temp_bibtex_file, sample_bibtex_content):
        """Test successful validation of valid BibTeX file."""
        temp_bibtex_file.write_text(sample_bibtex_content)
        
        results = validator.validate_bibtex_file(str(temp_bibtex_file))
        
        assert results['total_entries'] == 2
        assert results['passed_entries'] == 2
        assert results['failed_entries'] == 0
        assert results['all_passed'] is True
        assert len(results['errors']) == 0
    
    def test_validate_bibtex_file_not_found(self, validator, temp_dir):
        """Test validation with non-existent file."""
        non_existent_file = temp_dir / "nonexistent.bib"
        
        results = validator.validate_bibtex_file(str(non_existent_file))
        
        assert len(results['errors']) > 0
        assert "Failed to read BibTeX file" in results['errors'][0]
    
    def test_check_trailing_commas(self, validator):
        """Test trailing comma detection."""
        # Content with trailing comma
        content_with_trailing = """@article{test2023,
            title = {Test Title},
            author = {Test Author},
            year = {2023},
        }"""
        
        issues = validator._check_trailing_commas("test2023", content_with_trailing)
        assert len(issues) > 0
        assert any("Trailing comma" in issue for issue in issues)
        
        # Content without trailing comma
        content_without_trailing = """@article{test2023,
            title = {Test Title},
            author = {Test Author},
            year = {2023}
        }"""
        
        issues = validator._check_trailing_commas("test2023", content_without_trailing)
        assert len(issues) == 0
    
    def test_check_double_commas(self, validator):
        """Test double comma detection."""
        # Content with double comma
        content_with_double = """@article{test2023,
            title = {Test Title},
            author = {Test Author},,
            year = {2023}
        }"""
        
        issues = validator._check_double_commas("test2023", content_with_double)
        assert len(issues) > 0
        assert any("Double comma" in issue for issue in issues)
        
        # Content with comma followed by comma on next line
        content_with_line_double = """@article{test2023,
            title = {Test Title},
            author = {Test Author},
            ,
            year = {2023}
        }"""
        
        issues = validator._check_double_commas("test2023", content_with_line_double)
        assert len(issues) > 0
        assert any("Comma followed by comma" in issue for issue in issues)
        
        # Content without double commas
        content_without_double = """@article{test2023,
            title = {Test Title},
            author = {Test Author},
            year = {2023}
        }"""
        
        issues = validator._check_double_commas("test2023", content_without_double)
        assert len(issues) == 0
    
    def test_check_internal_braces(self, validator):
        """Test internal braces detection."""
        # Fields with internal braces
        fields_with_braces = {
            'title': 'Title with {nested} braces',
            'booktitle': 'Book with {internal} braces',
            'journal': 'Journal of {Science}',
            'publisher': 'Publisher {Name}'
        }
        
        issues = validator._check_internal_braces("test2023", fields_with_braces)
        assert len(issues) > 0
        assert any("internal braces" in issue.lower() for issue in issues)
        
        # Fields without internal braces
        fields_without_braces = {
            'title': 'Simple Title',
            'booktitle': 'Simple Book',
            'journal': 'Simple Journal',
            'publisher': 'Simple Publisher'
        }
        
        issues = validator._check_internal_braces("test2023", fields_without_braces)
        assert len(issues) == 0
    
    def test_check_uncleared_file_tags(self, validator):
        """Test uncleared file tags detection (unprocessed image paths only)."""
        # File field with unprocessed images (absolute storage paths)
        fields_with_unprocessed = {
            'file': 'test.pdf:/path/to/test.pdf:application/pdf; image.jpg:/Users/me/Documents/image.jpg:image/jpeg',
            'pdf': 'test.pdf'
        }
        
        issues = validator._check_uncleared_file_tags("test2023", fields_with_unprocessed, "")
        assert len(issues) > 0
        assert any("unprocessed image" in issue.lower() or "original path" in issue.lower() for issue in issues)
        
        # PDF-only file field is not flagged by current image-focused checker
        fields_with_processed = {
            'file': 'test.pdf:/path/to/test.pdf:application/pdf',
            'pdf': 'test.pdf'
        }
        
        issues = validator._check_uncleared_file_tags("test2023", fields_with_processed, "")
        assert len(issues) == 0
        
        # Clean file field (no images)
        fields_clean = {
            'file': 'other.pdf:/path/to/other.pdf:application/pdf',
            'pdf': 'test.pdf'
        }
        
        issues = validator._check_uncleared_file_tags("test2023", fields_clean, "")
        assert len(issues) == 0
    
    @patch('os.path.exists')
    def test_check_unused_thumbnail_tags(self, mock_exists, validator):
        """Test unused thumbnail tags detection."""
        # Preview file not found
        mock_exists.return_value = False
        fields_with_missing = {
            'preview': 'nonexistent.jpg'
        }
        
        issues = validator._check_unused_thumbnail_tags("test2023", fields_with_missing)
        assert len(issues) > 0
        assert any("Preview file not found" in issue for issue in issues)
        
        # Preview file exists
        mock_exists.return_value = True
        fields_with_existing = {
            'preview': 'existing.jpg'
        }
        
        issues = validator._check_unused_thumbnail_tags("test2023", fields_with_existing)
        assert len(issues) == 0
    
    def test_check_unrenamed_files(self, validator):
        """Test unrenamed files detection."""
        # Files with original Zotero names
        fields_with_zotero = {
            'pdf': '54439519274_cf052b44d1_k.pdf',
            'photos': 'A1B2C3D4.jpeg',
            'preview': '12345678-1234-1234-1234-123456789012.jpg'
        }
        
        issues = validator._check_unrenamed_files("test2023", fields_with_zotero)
        assert len(issues) > 0
        assert any("not renamed" in issue.lower() for issue in issues)
        
        # Files with proper names
        fields_with_proper = {
            'pdf': 'test_paper_2023.pdf',
            'photos': 'figure1.jpg',
            'preview': 'thumbnail.png'
        }
        
        issues = validator._check_unrenamed_files("test2023", fields_with_proper)
        assert len(issues) == 0
    
    def test_check_bibtex_syntax(self, validator):
        """Test BibTeX syntax issues detection."""
        # Content with comma at start of line
        content_with_start_comma = """@article{test2023,
            title = {Test Title},
            ,author = {Test Author},
            year = {2023}
        }"""
        
        issues = validator._check_bibtex_syntax("test2023", content_with_start_comma)
        assert len(issues) > 0
        assert any("Comma at start of line" in issue for issue in issues)
        
        # Content with missing comma between fields
        content_missing_comma = """@article{test2023,
            title = {Test Title}
            author = {Test Author},
            year = {2023}
        }"""
        
        issues = validator._check_bibtex_syntax("test2023", content_missing_comma)
        assert len(issues) > 0
        assert any("Missing comma between fields" in issue for issue in issues)
        
        # Content with invalid citation key
        content_invalid_key = """@article{test@2023,
            title = {Test Title},
            author = {Test Author},
            year = {2023}
        }"""
        
        issues = validator._check_bibtex_syntax("test@2023", content_invalid_key)
        assert len(issues) > 0
        assert any("Invalid characters in citation key" in issue for issue in issues)
        
        # Empty field values are allowed by current syntax checker (not flagged)
        content_empty_field = """@article{test2023,
            title = {Test Title},
            author = {},
            year = {2023}
        }"""
        
        issues = validator._check_bibtex_syntax("test2023", content_empty_field)
        assert not any("Empty field value" in issue for issue in issues)
        
        # Valid content
        content_valid = """@article{test2023,
            title = {Test Title},
            author = {Test Author},
            year = {2023}
        }"""
        
        issues = validator._check_bibtex_syntax("test2023", content_valid)
        assert len(issues) == 0
    
    def test_check_unmatched_braces(self, validator):
        """Test unmatched braces detection."""
        # Content with unmatched braces
        content_unmatched = """@article{test2023,
            title = {Test Title},
            author = {Test Author},
            year = {2023}"""
        
        issues = validator._check_unmatched_braces("test2023", content_unmatched)
        assert len(issues) > 0
        assert any("Unmatched braces" in issue for issue in issues)
        
        # Content with extra closing braces
        content_extra = """@article{test2023,
            title = {Test Title},
            author = {Test Author},
            year = {2023}
        }}"""
        
        issues = validator._check_unmatched_braces("test2023", content_extra)
        assert len(issues) > 0
        assert any("Unmatched braces" in issue for issue in issues)
        
        # Content with balanced braces
        content_balanced = """@article{test2023,
            title = {Test Title},
            author = {Test Author},
            year = {2023}
        }"""
        
        issues = validator._check_unmatched_braces("test2023", content_balanced)
        assert len(issues) == 0
    
    def test_check_malformed_entries(self, validator):
        """Test malformed entries detection."""
        # Missing entry type
        content_no_type = """{test2023,
            title = {Test Title},
            author = {Test Author},
            year = {2023}
        }"""
        
        issues = validator._check_malformed_entries("test2023", content_no_type)
        assert len(issues) > 0
        assert any("Missing or invalid entry type" in issue for issue in issues)
        
        # Missing citation key
        content_no_key = """@article{
            title = {Test Title},
            author = {Test Author},
            year = {2023}
        }"""
        
        issues = validator._check_malformed_entries("", content_no_key)
        assert len(issues) > 0
        assert any("Missing citation key" in issue for issue in issues)
        
        # Missing opening brace
        content_no_brace = """@article test2023,
            title = {Test Title},
            author = {Test Author},
            year = {2023}
        }"""
        
        issues = validator._check_malformed_entries("test2023", content_no_brace)
        assert len(issues) > 0
        assert any("Missing opening brace" in issue for issue in issues)
        
        # Missing closing brace
        content_no_close = """@article{test2023,
            title = {Test Title},
            author = {Test Author},
            year = {2023}"""
        
        issues = validator._check_malformed_entries("test2023", content_no_close)
        assert len(issues) > 0
        assert any("Missing closing brace" in issue for issue in issues)
        
        # Valid entry
        content_valid = """@article{test2023,
            title = {Test Title},
            author = {Test Author},
            year = {2023}
        }"""
        
        issues = validator._check_malformed_entries("test2023", content_valid)
        assert len(issues) == 0
    
    def test_is_original_zotero_filename(self, validator):
        """Test Zotero filename detection."""
        # Zotero-style filenames
        zotero_filenames = [
            "54439519274_cf052b44d1_k",
            "12345678-1234-1234-1234-123456789012",
            "A1B2C3D4",
            "a1b2c3d4"
        ]
        
        for filename in zotero_filenames:
            assert validator._is_original_zotero_filename(filename), f"Should detect {filename} as Zotero filename"
        
        # Normal filenames
        normal_filenames = [
            "test.pdf",
            "my_document_2023.pdf",
            "paper_title_v2.pdf",
            "figure1.jpg"
        ]
        
        for filename in normal_filenames:
            assert not validator._is_original_zotero_filename(filename), f"Should not detect {filename} as Zotero filename"
    
    def test_validate_single_entry_enhanced(self, validator):
        """Test enhanced validation of single entry."""
        # Valid entry
        valid_entry = {
            'citation_key': 'test2023',
            'fields': {
                'title': 'Test Title',
                'author': 'Test Author',
                'year': '2023'
            },
            'content': """@article{test2023,
                title = {Test Title},
                author = {Test Author},
                year = {2023}
            }"""
        }
        
        validator._validate_single_entry_enhanced(valid_entry)
        
        assert validator.validation_results['passed_entries'] == 1
        assert validator.validation_results['failed_entries'] == 0
        assert len(validator.validation_results['errors']) == 0
        
        # Reset for next test
        validator.validation_results = {
            'total_entries': 0,
            'passed_entries': 0,
            'failed_entries': 0,
            'warnings': [],
            'errors': [],
            'issues_by_type': {
                'trailing_commas': [],
                'double_commas': [],
                'internal_braces': [],
                'uncleared_file_tags': [],
                'unused_thumbnail_tags': [],
                'unrenamed_files': [],
                'bibtex_syntax': [],
                'unmatched_braces': [],
                'malformed_entries': []
            }
        }
        
        # Invalid entry
        invalid_entry = {
            'citation_key': 'test2023',
            'fields': {
                'title': 'Test Title',
                'author': 'Test Author',
                'year': '2023'
            },
            'content': """@article{test2023,
                title = {Test Title},
                author = {Test Author},,
                year = {2023}
            }"""
        }
        
        validator._validate_single_entry_enhanced(invalid_entry)
        
        assert validator.validation_results['passed_entries'] == 0
        assert validator.validation_results['failed_entries'] == 1
        assert len(validator.validation_results['errors']) > 0
        assert len(validator.validation_results['issues_by_type']['double_commas']) > 0
    
    def test_get_validation_summary(self, validator):
        """Test validation summary generation."""
        # Set up some test data
        validator.validation_results = {
            'total_entries': 10,
            'passed_entries': 8,
            'failed_entries': 2,
            'warnings': ['Warning 1', 'Warning 2'],
            'errors': ['Error 1', 'Error 2', 'Error 3'],
            'issues_by_type': {
                'trailing_commas': ['Issue 1'],
                'double_commas': ['Issue 2'],
                'internal_braces': [],
                'uncleared_file_tags': [],
                'unused_thumbnail_tags': [],
                'unrenamed_files': [],
                'bibtex_syntax': [],
                'unmatched_braces': [],
                'malformed_entries': []
            }
        }
        
        summary = validator.get_validation_summary()
        
        assert summary['total_entries'] == 10
        assert summary['passed_entries'] == 8
        assert summary['failed_entries'] == 2
        assert summary['warning_count'] == 2
        assert summary['error_count'] == 3
        assert summary['all_passed'] is False
        assert 'issues_by_type' in summary
        assert len(summary['issues_by_type']['trailing_commas']) == 1
        assert len(summary['issues_by_type']['double_commas']) == 1
    
    def test_print_enhanced_validation_summary(self, validator, capsys):
        """Test validation summary printing."""
        # Set up test data
        validator.validation_results = {
            'total_entries': 5,
            'passed_entries': 3,
            'failed_entries': 2,
            'warnings': ['Warning 1'],
            'errors': ['Error 1', 'Error 2'],
            'issues_by_type': {
                'trailing_commas': ['Issue 1'],
                'double_commas': ['Issue 2'],
                'internal_braces': [],
                'uncleared_file_tags': [],
                'unused_thumbnail_tags': [],
                'unrenamed_files': [],
                'bibtex_syntax': [],
                'unmatched_braces': [],
                'malformed_entries': []
            }
        }
        
        validator._print_enhanced_validation_summary()
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert "Enhanced Validation Summary" in output
        assert "Total entries: 5" in output
        assert "Passed: 3" in output
        assert "Failed: 2" in output
        assert "Warnings: 1" in output
        assert "Errors: 2" in output
        assert "Trailing Commas: 1 issues" in output
        assert "Double Commas: 1 issues" in output
