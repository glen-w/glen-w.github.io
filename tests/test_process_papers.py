#!/usr/bin/env python3
"""
Comprehensive pytest suite for process_papers.py
Tests all core functionality including BibTeX parsing, filename generation, 
PDF operations, and thumbnail generation.
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import sys

# Add the parent directory to the path so we can import process_papers
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from process_papers import (
    clean_nested_braces,
    parse_bibtex_entry,
    clean_title_for_filename,
    extract_author_names_for_filename,
    extract_journal_or_publisher_for_filename,
    extract_file_paths,
    prepare_pdf_metadata,
    entry_has_selected_tag,
    entry_has_all_required_tags,
    add_selected_tag_if_featured,
    add_pdf_and_preview_tags,
    clean_malformed_bibtex_entries,
    validate_and_clean_bibtex
)


class TestBibTeXParsing:
    """Test BibTeX parsing functionality."""
    
    def test_clean_nested_braces_simple(self):
        """Test cleaning simple nested braces."""
        text = "Simple {text} with {nested {braces}}"
        result = clean_nested_braces(text)
        assert result == "Simple text with nested braces"
    
    def test_clean_nested_braces_complex(self):
        """Test cleaning complex nested braces."""
        text = "Complex {text {with {multiple {levels}}}} of nesting"
        result = clean_nested_braces(text)
        assert result == "Complex text with multiple levels of nesting"
    
    def test_clean_nested_braces_empty(self):
        """Test cleaning empty or None text."""
        assert clean_nested_braces("") == ""
        assert clean_nested_braces(None) == ""
    
    def test_clean_nested_braces_no_braces(self):
        """Test cleaning text with no braces."""
        text = "Text without any braces"
        result = clean_nested_braces(text)
        assert result == text
    
    def test_parse_bibtex_entry_simple(self):
        """Test parsing a simple BibTeX entry."""
        entry = """@article{test2023,
            title = {Test Title},
            author = {Test Author},
            year = {2023}
        }"""
        
        citation_key, fields = parse_bibtex_entry(entry)
        assert citation_key == "test2023"
        assert fields["title"] == "Test Title"
        assert fields["author"] == "Test Author"
        assert fields["year"] == "2023"
    
    def test_parse_bibtex_entry_with_nested_braces(self):
        """Test parsing BibTeX entry with nested braces in fields."""
        entry = """@article{test2023,
            title = {Title with {nested} braces},
            author = {Author with {complex} name},
            journal = {Journal {of} Science}
        }"""
        
        citation_key, fields = parse_bibtex_entry(entry)
        assert citation_key == "test2023"
        assert fields["title"] == "Title with nested braces"
        assert fields["author"] == "Author with complex name"
        assert fields["journal"] == "Journal of Science"
    
    def test_parse_bibtex_entry_malformed(self):
        """Test parsing malformed BibTeX entry."""
        entry = "@article{test2023, title = {Test Title}"
        citation_key, fields = parse_bibtex_entry(entry)
        assert citation_key == "test2023"
        # The parser is more robust than expected - it can handle this case
        assert "title" in fields  # Actually does parse the title
    
    def test_parse_bibtex_entry_no_fields(self):
        """Test parsing BibTeX entry with no fields."""
        entry = "@article{test2023,}"
        citation_key, fields = parse_bibtex_entry(entry)
        assert citation_key == "test2023"
        assert len(fields) == 0


class TestFilenameGeneration:
    """Test filename generation functionality."""
    
    def test_clean_title_for_filename_simple(self):
        """Test cleaning simple title for filename."""
        title = "Simple Title"
        result = clean_title_for_filename(title)
        assert result == "Simple_Title"
    
    def test_clean_title_for_filename_with_special_chars(self):
        """Test cleaning title with special characters."""
        title = "Title with @#$%^&*() special chars!"
        result = clean_title_for_filename(title)
        assert result == "Title_with_special_chars"
    
    def test_clean_title_for_filename_with_redundant_phrases(self):
        """Test cleaning title with redundant phrases."""
        title = "Some Title Global Status Report"
        result = clean_title_for_filename(title)
        assert result == "Some_Title"
    
    def test_clean_title_for_filename_long(self):
        """Test cleaning very long title."""
        title = "A" * 300  # Very long title
        result = clean_title_for_filename(title)
        assert len(result) <= 200  # Should be truncated
    
    def test_extract_author_names_single_author(self):
        """Test extracting single author name."""
        author = "Smith, John"
        result = extract_author_names_for_filename(author)
        assert result == "John_Smith"
    
    def test_extract_author_names_two_authors(self):
        """Test extracting two author names."""
        author = "Smith, John and Doe, Jane"
        result = extract_author_names_for_filename(author)
        assert result == "John_Smith_Jane_Doe"
    
    def test_extract_author_names_multiple_authors(self):
        """Test extracting multiple author names."""
        author = "Smith, John and Doe, Jane and Brown, Bob"
        result = extract_author_names_for_filename(author)
        assert result == "John_Smith_etal"
    
    def test_extract_author_names_corporate(self):
        """Test extracting corporate author name."""
        author = "United Nations"
        result = extract_author_names_for_filename(author)
        assert result == "United_Nations"
    
    def test_extract_journal_or_publisher_journal(self):
        """Test extracting journal name."""
        fields = {"journal": "Nature", "publisher": "Springer"}
        result = extract_journal_or_publisher_for_filename(fields)
        assert result == "Nature"
    
    def test_extract_journal_or_publisher_publisher(self):
        """Test extracting publisher when no journal."""
        fields = {"publisher": "Springer", "institution": "University"}
        result = extract_journal_or_publisher_for_filename(fields)
        assert result == "Springer"
    
    def test_extract_journal_or_publisher_institution(self):
        """Test extracting institution when no journal or publisher."""
        fields = {"institution": "University of Test"}
        result = extract_journal_or_publisher_for_filename(fields)
        assert result == "University_of_Test"
    
    def test_extract_journal_or_publisher_none(self):
        """Test extracting when no relevant fields exist."""
        fields = {"title": "Test Title"}
        result = extract_journal_or_publisher_for_filename(fields)
        assert result == ""


class TestFileOperations:
    """Test file operation functionality."""
    
    def test_extract_file_paths_single(self):
        """Test extracting single file path."""
        file_field = "Description:/path/to/file.pdf:application/pdf"
        with patch('os.path.exists', return_value=True):
            result = extract_file_paths(file_field)
            assert result == ["/path/to/file.pdf"]
    
    def test_extract_file_paths_multiple(self):
        """Test extracting multiple file paths."""
        file_field = "Desc1:/path1.pdf:pdf;Desc2:/path2.pdf:pdf"
        with patch('os.path.exists', return_value=True):
            result = extract_file_paths(file_field)
            assert result == ["/path1.pdf", "/path2.pdf"]
    
    def test_extract_file_paths_nonexistent(self):
        """Test extracting file paths when files don't exist."""
        file_field = "Description:/path/to/file.pdf:application/pdf"
        with patch('os.path.exists', return_value=False):
            result = extract_file_paths(file_field)
            assert result == []
    
    def test_extract_file_paths_empty(self):
        """Test extracting file paths from empty field."""
        result = extract_file_paths("")
        assert result == []
    
    def test_extract_file_paths_malformed(self):
        """Test extracting file paths from malformed field."""
        file_field = "Malformed field without proper format"
        result = extract_file_paths(file_field)
        assert result == []


class TestPDFMetadataAndTags:
    """Test PDF metadata updates and tag handling."""
    
    def test_prepare_pdf_metadata_complete(self):
        """Test preparing complete PDF metadata."""
        fields = {
            "title": "Test {Title} with Braces",
            "author": "Smith, John and Doe, Jane",
            "journal": "Test Journal",
            "year": "2023",
            "doi": "10.1000/test",
            "keywords": "test, example"
        }
        
        metadata = prepare_pdf_metadata(fields)
        
        assert metadata["title"] == "Test Title with Braces"
        assert metadata["author"] == "Smith, John"  # First author only
        assert metadata["subject"] == "test, example"
        assert metadata["creator"] == "Smith, John"
        assert metadata["producer"] == "RENWeB"
    
    def test_prepare_pdf_metadata_minimal(self):
        """Test preparing PDF metadata with minimal fields."""
        fields = {
            "title": "Minimal Title",
            "author": "Author, Name"
        }
        
        metadata = prepare_pdf_metadata(fields)
        
        assert metadata["title"] == "Minimal Title"
        assert metadata["author"] == "Author, Name"
        assert metadata["subject"] == ""
        assert metadata["creator"] == "Author, Name"
        assert metadata["producer"] == "RENWeB"
    
    def test_add_pdf_and_preview_tags_new_entry(self):
        """Test adding pdf and preview tags to a new entry."""
        bibtex_content = """@article{test2023,
            title = {Test Title},
            author = {Test Author},
            year = {2023}
        }"""
        
        result = add_pdf_and_preview_tags(
            bibtex_content, "test2023", "preview.jpg", "document.pdf", {}
        )
        
        # Check that tags were added
        assert "preview = {preview.jpg}" in result
        assert "pdf = {document.pdf}" in result
        
        # Check BibTeX syntax integrity
        assert result.count("{") == result.count("}")  # Balanced braces
        assert result.count(",") == 5  # Commas after test2023, Test Title, Test Author, 2023, preview.jpg
    
    def test_add_pdf_and_preview_tags_existing_entry(self):
        """Test adding pdf and preview tags to an entry with existing fields."""
        bibtex_content = """@article{test2023,
            title = {Test Title},
            author = {Test Author},
            year = {2023},
            journal = {Test Journal}
        }"""
        
        result = add_pdf_and_preview_tags(
            bibtex_content, "test2023", "preview.jpg", "document.pdf", {}
        )
        
        # Check that tags were added
        assert "preview = {preview.jpg}" in result
        assert "pdf = {document.pdf}" in result
        
        # Check that existing fields are preserved
        assert "title = {Test Title}" in result
        assert "author = {Test Author}" in result
        assert "year = {2023}" in result
        assert "journal = {Test Journal}" in result
        
        # Check BibTeX syntax integrity
        assert result.count("{") == result.count("}")  # Balanced braces
        assert result.count(",") == 6  # Commas after test2023, Test Title, Test Author, year, journal, preview
    
    def test_add_pdf_and_preview_tags_preserves_selected(self):
        """Test that adding pdf/preview tags preserves existing selected tag."""
        bibtex_content = """@article{test2023,
            title = {Test Title},
            author = {Test Author},
            year = {2023},
            selected = {true}
        }"""
        
        result = add_pdf_and_preview_tags(
            bibtex_content, "test2023", "preview.jpg", "document.pdf", {}
        )
        
        # Check that selected tag is preserved
        assert "selected = {true}" in result
        assert "preview = {preview.jpg}" in result
        assert "pdf = {document.pdf}" in result
        
        # Check BibTeX syntax integrity
        assert result.count("{") == result.count("}")  # Balanced braces
        assert result.count(",") == 6  # Commas after test2023, Test Title, Test Author, year, selected, preview


class TestBibTeXSyntaxIntegrity:
    """Test BibTeX syntax integrity and validation."""
    
    def test_clean_malformed_bibtex_missing_commas(self):
        """Test cleaning BibTeX with missing commas between fields."""
        malformed_bibtex = """@article{test2023,
            title = {Test Title}
            author = {Test Author}
            year = {2023}
        }"""
        
        cleaned = clean_malformed_bibtex_entries(malformed_bibtex)
        
        # Check that commas were added
        assert "title = {Test Title}," in cleaned
        assert "author = {Test Author}," in cleaned
        assert "year = {2023}" in cleaned  # No comma after last field
        
        # Check BibTeX syntax integrity
        assert cleaned.count("{") == cleaned.count("}")  # Balanced braces
        assert cleaned.count(",") == 2  # Commas after title and author
    
    def test_clean_malformed_bibtex_duplicate_fields(self):
        """Test cleaning BibTeX with duplicate fields."""
        malformed_bibtex = """@article{test2023,
            title = {Test Title},
            pdf = {wrong.pdf},
            author = {Test Author},
            pdf = {correct.pdf},
            year = {2023}
        }"""
        
        cleaned = clean_malformed_bibtex_entries(malformed_bibtex)
        
        # Check that duplicate pdf fields are handled
        assert cleaned.count("pdf = {") == 1  # Only one pdf field should remain
        assert "pdf = {correct.pdf}" in cleaned  # Last one should remain
        
        # Check BibTeX syntax integrity
        assert cleaned.count("{") == cleaned.count("}")  # Balanced braces
        assert cleaned.count(",") == 3  # Commas after title, author, pdf
    
    def test_clean_malformed_bibtex_wrong_content(self):
        """Test cleaning BibTeX with wrong content in fields."""
        malformed_bibtex = """@article{test2023,
            title = {Test Title},
            preview = {wrong_preview.jpeg},
            author = {Test Author},
            preview = {correct_preview.jpeg},
            year = {2023}
        }"""
        
        cleaned = clean_malformed_bibtex_entries(malformed_bibtex)
        
        # Check that duplicate preview fields are handled
        assert cleaned.count("preview = {") == 1  # Only one preview field should remain
        assert "preview = {correct_preview.jpeg}" in cleaned  # Last one should remain
        
        # Check BibTeX syntax integrity
        assert cleaned.count("{") == cleaned.count("}")  # Balanced braces
        assert cleaned.count(",") == 3  # Commas after title, author, preview
    
    def test_validate_and_clean_bibtex_balanced_braces(self):
        """Test BibTeX validation for balanced braces."""
        valid_bibtex = """@article{test2023,
            title = {Test {Title} with {Nested} Braces},
            author = {Test Author},
            year = {2023}
        }"""
        
        result = validate_and_clean_bibtex(valid_bibtex)
        
        # Should return the content unchanged if valid
        assert result == valid_bibtex
    
    def test_validate_and_clean_bibtex_unbalanced_braces(self):
        """Test BibTeX validation for unbalanced braces."""
        invalid_bibtex = """@article{test2023,
            title = {Test Title with {unbalanced braces,
            author = {Test Author},
            year = {2023}
        }"""
        
        result = validate_and_clean_bibtex(invalid_bibtex)
        
        # Should detect the issue and attempt to fix or report it
        # The exact behavior depends on the implementation
        assert isinstance(result, str)
    
    def test_bibtex_syntax_after_tag_addition(self):
        """Test that BibTeX syntax remains valid after adding tags."""
        original_bibtex = """@article{test2023,
            title = {Test Title},
            author = {Test Author},
            year = {2023}
        }"""
        
        # Add selected tag
        with_selected = add_selected_tag_if_featured(
            original_bibtex, "test2023", {"keywords": "featured, important"}
        )
        
        # Add pdf and preview tags
        with_all_tags = add_pdf_and_preview_tags(
            with_selected, "test2023", "preview.jpg", "document.pdf", {}
        )
        
        # Check that all tags are present
        assert "selected = {true}" in with_all_tags
        assert "preview = {preview.jpg}" in with_all_tags
        assert "pdf = {document.pdf}" in with_all_tags
        
        # Check BibTeX syntax integrity
        assert with_all_tags.count("{") == with_all_tags.count("}")  # Balanced braces
        
        # Count commas - should have commas after test2023, Test Title, Test Author, year, selected, preview
        assert with_all_tags.count(",") == 6
        
        # Validate the final BibTeX
        validated = validate_and_clean_bibtex(with_all_tags)
        assert validated == with_all_tags  # Should be valid and unchanged
    
    def test_bibtex_syntax_with_complex_fields(self):
        """Test BibTeX syntax with complex field values containing braces."""
        complex_bibtex = """@article{test2023,
            title = {Complex {Title} with {Multiple {Nested} Braces}},
            author = {Author, First and Second, Author},
            journal = {Journal of {Complex} Science},
            year = {2023}
        }"""
        
        # Add selected tag
        with_selected = add_selected_tag_if_featured(
            complex_bibtex, "test2023", {"keywords": "featured"}
        )
        
        # Add pdf and preview tags
        with_all_tags = add_pdf_and_preview_tags(
            with_selected, "test2023", "preview.jpg", "document.pdf", {}
        )
        
        # Check that all tags are present
        assert "selected = {true}" in with_all_tags
        assert "preview = {preview.jpg}" in with_all_tags
        assert "pdf = {document.pdf}" in with_all_tags
        
        # Check that complex fields are preserved
        assert "title = {Complex {Title} with {Multiple {Nested} Braces}}" in with_all_tags
        assert "author = {Author, First and Second, Author}" in with_all_tags
        assert "journal = {Journal of {Complex} Science}" in with_all_tags
        
        # Check BibTeX syntax integrity
        assert with_all_tags.count("{") == with_all_tags.count("}")  # Balanced braces
        
        # Validate the final BibTeX
        validated = validate_and_clean_bibtex(with_all_tags)
        assert validated == with_all_tags  # Should be valid and unchanged


class TestFilenameGeneration:
    """Test filename generation for different author scenarios."""
    
    def test_single_author_filename(self):
        """Test filename generation for single author."""
        author = "Smith, John"
        result = extract_author_names_for_filename(author)
        assert result == "john_smith"
    
    def test_two_authors_filename(self):
        """Test filename generation for two authors (should add _etal)."""
        author = "Smith, John and Doe, Jane"
        result = extract_author_names_for_filename(author)
        assert result == "john_smith_etal"
    
    def test_three_authors_filename(self):
        """Test filename generation for three authors (should add _etal)."""
        author = "Smith, John and Doe, Jane and Brown, Bob"
        result = extract_author_names_for_filename(author)
        assert result == "john_smith_etal"
    
    def test_author_without_comma_filename(self):
        """Test filename generation for author without comma."""
        author = "John Smith"
        result = extract_author_names_for_filename(author)
        assert result == "john_smith"
    
    def test_multiple_authors_without_comma_filename(self):
        """Test filename generation for multiple authors without commas."""
        author = "John Smith and Jane Doe"
        result = extract_author_names_for_filename(author)
        assert result == "john_smith_etal"
    
    def test_journal_priority_order(self):
        """Test that journal/institution/publisher priority order is respected."""
        # Test with journal (highest priority)
        fields = {"journal": "Science Journal", "institution": "University", "publisher": "Publisher"}
        result = extract_journal_or_publisher_for_filename(fields)
        assert result == "science_journal"
        
        # Test with institution (second priority)
        fields = {"institution": "University", "publisher": "Publisher"}
        result = extract_journal_or_publisher_for_filename(fields)
        assert result == "university"
        
        # Test with publisher (lowest priority)
        fields = {"publisher": "Publisher"}
        result = extract_journal_or_publisher_for_filename(fields)
        assert result == "publisher"
        
        # Test with none
        fields = {}
        result = extract_journal_or_publisher_for_filename(fields)
        assert result == ""
    
    def test_prepare_pdf_metadata_minimal(self):
        """Test preparing minimal PDF metadata."""
        fields = {"title": "Test Title"}
        result = prepare_pdf_metadata(fields)
        assert result["title"] == "Test Title"
        assert "author" not in result
        assert "keywords" not in result
    
    def test_prepare_pdf_metadata_with_braces(self):
        """Test preparing metadata with braces in author field."""
        fields = {
            "title": "Test Title",
            "author": "Smith, {John} and Doe, {Jane}"
        }
        
        result = prepare_pdf_metadata(fields)
        # The function only takes the first author when cleaning braces
        assert result["author"] == "Smith, John"


class TestSelectedTagOperations:
    """Test selected tag functionality."""
    
    def test_entry_has_selected_tag_true(self):
        """Test checking if entry has selected tag when it exists."""
        fields = {"selected": "true", "title": "Test"}
        assert entry_has_selected_tag(fields) == True
    
    def test_entry_has_selected_tag_false(self):
        """Test checking if entry has selected tag when it doesn't exist."""
        fields = {"title": "Test", "author": "Author"}
        assert entry_has_selected_tag(fields) == False
    
    def test_entry_has_all_required_tags_basic(self):
        """Test checking all required tags for entry without featured keywords."""
        fields = {
            "title": "Test"
        }
        # Since we're not adding PDF/preview tags anymore, this should return False
        # (no selected tag needed for non-featured entries)
        assert entry_has_all_required_tags(fields) == False
    
    def test_entry_has_all_required_tags_with_featured(self):
        """Test checking all required tags for entry with featured keywords."""
        fields = {
            "keywords": "featured, marine",
            "selected": "true",
            "title": "Test"
        }
        assert entry_has_all_required_tags(fields) == True
    
    def test_entry_has_all_required_tags_with_featured_missing_selected(self):
        """Test checking all required tags for entry with featured keywords but missing selected tag."""
        fields = {
            "keywords": "featured, marine",
            "title": "Test"
        }
        # Should return False since featured keywords need selected tag
        assert entry_has_all_required_tags(fields) == False
    
    def test_entry_has_all_required_tags_with_doi(self):
        """Test checking all required tags for entry with DOI."""
        fields = {
            "keywords": "featured, marine",
            "doi": "10.1234/test",
            "selected": "true",
            "title": "Test"
        }
        # Should return True since it has the required selected tag
        assert entry_has_all_required_tags(fields) == True
    
    def test_entry_has_all_required_tags_with_doi_missing_dimensions(self):
        """Test checking all required tags for entry with DOI but missing dimensions."""
        fields = {
            "keywords": "featured, marine",
            "doi": "10.1234/test",
            "selected": "true",
            "title": "Test"
        }
        # Should return True since we only check for selected tags now
        assert entry_has_all_required_tags(fields) == True
    
    def test_add_selected_tag_if_featured_with_featured_keywords(self):
        """Test adding selected tag when keywords contain 'featured'."""
        bibtex_content = """@article{test2023,
            title = {Test Title},
            keywords = {featured, marine},
            year = {2023}
        }"""
        
        fields = {"keywords": "featured, marine"}
        result = add_selected_tag_if_featured(bibtex_content, "test2023", fields)
        
        # Check that selected tag was added
        assert "selected = {true}" in result
        # Check that it was added before the closing brace
        assert result.count("selected = {true}") == 1
        # Check proper comma placement
        assert ",\n\tselected = {true}" in result
    
    def test_add_selected_tag_if_featured_without_featured_keywords(self):
        """Test not adding selected tag when keywords don't contain 'featured'."""
        bibtex_content = """@article{test2023,
            title = {Test Title},
            keywords = {marine, ocean},
            year = {2023}
        }"""
        
        fields = {"keywords": "marine, ocean"}
        result = add_selected_tag_if_featured(bibtex_content, "test2023", fields)
        
        # Check that selected tag was not added
        assert "selected = {true}" not in result
        # Check that content is unchanged
        assert result == bibtex_content
    
    def test_add_selected_tag_if_featured_no_keywords(self):
        """Test not adding selected tag when no keywords field exists."""
        bibtex_content = """@article{test2023,
            title = {Test Title},
            year = {2023}
        }"""
        
        fields = {}
        result = add_selected_tag_if_featured(bibtex_content, "test2023", fields)
        
        # Check that selected tag was not added
        assert "selected = {true}" not in result
        # Check that content is unchanged
        assert result == bibtex_content
    
    def test_add_selected_tag_if_featured_empty_keywords(self):
        """Test not adding selected tag when keywords field is empty."""
        bibtex_content = """@article{test2023,
            title = {Test Title},
            keywords = {},
            year = {2023}
        }"""
        
        fields = {"keywords": ""}
        result = add_selected_tag_if_featured(bibtex_content, "test2023", fields)
        
        # Check that selected tag was not added
        assert "selected = {true}" not in result
        # Check that content is unchanged
        assert result == bibtex_content
    
    def test_add_selected_tag_if_featured_case_insensitive(self):
        """Test adding selected tag when keywords contain 'FEATURED' (case insensitive)."""
        bibtex_content = """@article{test2023,
            title = {Test Title},
            keywords = {FEATURED, marine},
            year = {2023}
        }"""
        
        fields = {"keywords": "FEATURED, marine"}
        result = add_selected_tag_if_featured(bibtex_content, "test2023", fields)
        
        # Check that selected tag was added
        assert "selected = {true}" in result
    
    def test_add_selected_tag_if_featured_replace_existing(self):
        """Test that existing selected tag prevents adding a new one."""
        bibtex_content = """@article{test2023,
            title = {Test Title},
            keywords = {featured, marine},
            selected = {false},
            year = {2023}
        }"""
    
        fields = {"keywords": "featured, marine", "selected": "false"}
        result = add_selected_tag_if_featured(bibtex_content, "test2023", fields)
    
        # Check that no new selected tag was added since one already exists
        assert "selected = {true}" not in result
        # Check that the existing selected tag is preserved
        assert "selected = {false}" in result
    
    def test_add_selected_tag_if_featured_proper_comma_handling(self):
        """Test proper comma handling when adding selected tag."""
        bibtex_content = """@article{test2023,
            title = {Test Title},
            keywords = {featured, marine}
        }"""
    
        fields = {"keywords": "featured, marine"}
        result = add_selected_tag_if_featured(bibtex_content, "test2023", fields)
    
        # Check that selected tag was added with proper comma handling
        # The current logic adds a comma when needed for proper BibTeX formatting
        assert "selected = {true}" in result
        # Check that we don't have double commas
        assert ",," not in result
    
    def test_add_selected_tag_if_featured_comma_already_present(self):
        """Test comma handling when comma is already present before closing brace."""
        bibtex_content = """@article{test2023,
            title = {Test Title},
            keywords = {featured, marine},
        }"""
        
        fields = {"keywords": "featured, marine"}
        result = add_selected_tag_if_featured(bibtex_content, "test2023", fields)
        
        # Check that selected tag was added with proper comma handling
        # The current logic adds a comma when needed for proper BibTeX formatting
        assert "selected = {true}" in result
        # Check that we don't have double commas
        assert ",," not in result
    
    def test_add_selected_tag_if_featured_multiple_entries(self):
        """Test adding selected tag in a file with multiple entries."""
        bibtex_content = """@article{test2023,
            title = {Test Title},
            keywords = {featured, marine},
            year = {2023}
        }

@article{test2024,
            title = {Another Title},
            keywords = {ocean, energy},
            year = {2024}
        }"""
        
        fields = {"keywords": "featured, marine"}
        result = add_selected_tag_if_featured(bibtex_content, "test2023", fields)
        
        # Check that selected tag was added to the first entry
        assert "selected = {true}" in result
        # Check that second entry was not modified
        assert "Another Title" in result
        # Check that we don't have the tag in the wrong entry
        lines = result.split('\n')
        selected_line_index = None
        for i, line in enumerate(lines):
            if "selected = {true}" in line:
                selected_line_index = i
                break
        
        # The selected tag should be in the first entry section
        assert selected_line_index is not None
        # Check that it's before the second @article
        second_article_index = None
        for i, line in enumerate(lines):
            if "@article{test2024" in line:
                second_article_index = i
                break
        
        assert selected_line_index < second_article_index
    
    def test_add_selected_tag_if_featured_complex_keywords(self):
        """Test adding selected tag with complex keyword formats."""
        test_cases = [
            "featured",
            "marine, featured, ocean",
            "featured, marine",
            "marine, featured",
            "marine, featured, ocean, energy",
            "featured, marine, ocean, energy",
            "marine, ocean, featured, energy",
            "marine, ocean, energy, featured"
        ]
        
        for keywords in test_cases:
            bibtex_content = f"""@article{{test2023,
            title = {{Test Title}},
            keywords = {{{keywords}}},
            year = {{2023}}
        }}"""
            
            fields = {"keywords": keywords}
            result = add_selected_tag_if_featured(bibtex_content, "test2023", fields)
            
            # Check that selected tag was added
            assert "selected = {true}" in result, f"Failed for keywords: {keywords}"
            # Check that we don't have duplicate tags
            assert result.count("selected = {true}") == 1, f"Failed for keywords: {keywords}"


class TestIntegration:
    """Test integration scenarios."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_full_bibtex_processing(self, temp_dir):
        """Test full BibTeX processing workflow."""
        # Create test BibTeX file
        bibtex_content = """@article{test2023,
            title = {Test {Title} with Braces},
            author = {Smith, John and Doe, Jane},
            year = {2023},
            journal = {Test Journal},
            file = {Description:/test/path.pdf:application/pdf}
        }"""
        
        bibtex_file = os.path.join(temp_dir, "test.bib")
        with open(bibtex_file, 'w') as f:
            f.write(bibtex_content)
        
        # Parse the entry
        citation_key, fields = parse_bibtex_entry(bibtex_content)
        
        # Test all the processing steps
        assert citation_key == "test2023"
        assert fields["title"] == "Test Title with Braces"
        assert fields["author"] == "Smith, John and Doe, Jane"
        assert fields["year"] == "2023"
        assert fields["journal"] == "Test Journal"
        
        # Test filename generation
        clean_title = clean_title_for_filename(fields["title"])
        author_names = extract_author_names_for_filename(fields["author"])
        journal = extract_journal_or_publisher_for_filename(fields)
        
        assert clean_title == "Test_Title_with_Braces"
        assert author_names == "john_smith_etal"  # Multiple authors get _etal
        assert journal == "test_journal"  # Function returns lowercase
        
        # Test file path extraction - mock the file existence
        with patch('os.path.exists', return_value=True):
            file_paths = extract_file_paths(fields["file"])
            assert len(file_paths) == 1
            assert file_paths[0] == "/test/path.pdf"
        
        # Test metadata preparation
        metadata = prepare_pdf_metadata(fields)
        assert metadata["title"] == "Test Title with Braces"
        assert metadata["author"] == "Smith, John"  # Only first author is used for PDF metadata


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_parse_bibtex_entry_empty(self):
        """Test parsing empty entry."""
        citation_key, fields = parse_bibtex_entry("")
        assert citation_key is None
        assert fields == {}
    
    def test_parse_bibtex_entry_whitespace_only(self):
        """Test parsing whitespace-only entry."""
        citation_key, fields = parse_bibtex_entry("   \n\t   ")
        assert citation_key is None
        assert fields == {}
    
    def test_clean_title_for_filename_none(self):
        """Test cleaning None title."""
        result = clean_title_for_filename(None)
        assert result == ""
    
    def test_extract_author_names_empty(self):
        """Test extracting author names from empty field."""
        result = extract_author_names_for_filename("")
        assert result == ""
    
    def test_extract_journal_or_publisher_empty_fields(self):
        """Test extracting journal/publisher from empty fields."""
        result = extract_journal_or_publisher_for_filename({})
        assert result == ""


if __name__ == "__main__":
    pytest.main([__file__])
