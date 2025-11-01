#!/usr/bin/env python3
"""
Unit tests for BibTeXProcessor class.
Tests all methods and functionality of the BibTeX processor module.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from processing.core.bibtex_processor import BibTeXProcessor
from processing.core.text_processor import TextProcessor
from processing.config import Configuration


@pytest.mark.unit
class TestBibTeXProcessor:
    """Unit tests for BibTeXProcessor class."""
    
    @pytest.fixture
    def bibtex_processor(self, config):
        """Create BibTeX processor for testing."""
        text_processor = TextProcessor(config)
        return BibTeXProcessor(config, text_processor)
    
    def test_parse_bibtex_entry_basic(self, bibtex_processor):
        """Test basic BibTeX entry parsing."""
        content = """@article{test2023,
            title = {Test Title},
            author = {Test Author},
            year = {2023}
        }"""
        
        citation_key, fields = bibtex_processor.parse_bibtex_entry(content)
        
        assert citation_key == "test2023"
        assert fields["title"] == "Test Title"
        assert fields["author"] == "Test Author"
        assert fields["year"] == "2023"
    
    def test_parse_bibtex_entry_with_nested_braces(self, bibtex_processor):
        """Test parsing entries with nested braces."""
        content = """@article{test2023,
            title = {Title with {nested} braces},
            author = {Author with {complex} name},
            year = {2023}
        }"""
        
        citation_key, fields = bibtex_processor.parse_bibtex_entry(content)
        
        assert citation_key == "test2023"
        assert fields["title"] == "Title with {nested} braces"
        assert fields["author"] == "Author with {complex} name"
        assert fields["year"] == "2023"
    
    def test_parse_bibtex_entry_malformed(self, bibtex_processor):
        """Test parsing malformed entries."""
        content = """@article{test2023,
            title = {Test Title}
            author = {Test Author}
            year = {2023}
        }"""
        
        citation_key, fields = bibtex_processor.parse_bibtex_entry(content)
        
        # Should still parse despite missing commas
        assert citation_key == "test2023"
        assert len(fields) > 0
    
    def test_parse_bibtex_entries_multiple(self, bibtex_processor):
        """Test parsing multiple BibTeX entries."""
        content = """@article{test2023a,
            title = {First Title},
            author = {First Author},
            year = {2023}
        }

        @book{test2023b,
            title = {Second Title},
            author = {Second Author},
            year = {2023}
        }"""
        
        entries = bibtex_processor.parse_bibtex_entries(content)
        
        assert len(entries) == 2
        assert entries[0]["citation_key"] == "test2023a"
        assert entries[1]["citation_key"] == "test2023b"
        assert entries[0]["fields"]["title"] == "First Title"
        assert entries[1]["fields"]["title"] == "Second Title"
    
    def test_find_entry_bounds(self, bibtex_processor):
        """Test finding entry bounds in content."""
        content = """@article{test2023,
            title = {Test Title},
            author = {Test Author},
            year = {2023}
        }"""
        
        start, end = bibtex_processor.find_entry_bounds(content, "test2023")
        
        assert start != -1
        assert end != -1
        assert content[start:end].startswith("@article{test2023")
        assert content[start:end].endswith("}")
    
    def test_find_entry_bounds_not_found(self, bibtex_processor):
        """Test finding entry bounds when entry doesn't exist."""
        content = """@article{test2023,
            title = {Test Title},
            author = {Test Author},
            year = {2023}
        }"""
        
        start, end = bibtex_processor.find_entry_bounds(content, "nonexistent")
        
        assert start == -1
        assert end == -1
    
    def test_add_tag_to_entry(self, bibtex_processor):
        """Test adding a single tag to an entry."""
        content = """@article{test2023,
            title = {Test Title},
            author = {Test Author},
            year = {2023}
        }"""
        
        modified = bibtex_processor.add_tag_to_entry(content, "test2023", "pdf", "test.pdf")
        
        assert "pdf = {test.pdf}" in modified
        assert "title = {Test Title}" in modified  # Original content preserved
    
    def test_add_tag_to_entry_existing_tag(self, bibtex_processor):
        """Test adding tag when tag already exists."""
        content = """@article{test2023,
            title = {Test Title},
            author = {Test Author},
            year = {2023},
            pdf = {existing.pdf}
        }"""
        
        modified = bibtex_processor.add_tag_to_entry(content, "test2023", "pdf", "new.pdf")
        
        # Should not add duplicate tag
        assert modified == content
    
    def test_add_multiple_tags(self, bibtex_processor):
        """Test adding multiple tags to an entry."""
        content = """@article{test2023,
            title = {Test Title},
            author = {Test Author},
            year = {2023}
        }"""
        
        tags = {
            "pdf": "test.pdf",
            "preview": "test.jpg",
            "selected": "true"
        }
        
        modified = bibtex_processor.add_multiple_tags(content, "test2023", tags)
        
        assert "pdf = {test.pdf}" in modified
        assert "preview = {test.jpg}" in modified
        assert "selected = {true}" in modified
        assert "title = {Test Title}" in modified  # Original content preserved
    
    def test_clean_malformed_entries(self, bibtex_processor):
        """Test cleaning malformed entries."""
        content = """@article{test2023,
            title = {Test Title}
            author = {Test Author},,
            year = {2023},
        }"""
        
        cleaned = bibtex_processor.clean_malformed_entries(content)
        
        # Should be parseable after cleaning
        citation_key, fields = bibtex_processor.parse_bibtex_entry(cleaned)
        assert citation_key == "test2023"
        assert len(fields) > 0
    
    def test_clean_malformed_entries_empty(self, bibtex_processor):
        """Test cleaning empty content."""
        content = ""
        
        cleaned = bibtex_processor.clean_malformed_entries(content)
        
        assert cleaned == ""
    
    def test_clean_malformed_entries_whitespace_only(self, bibtex_processor):
        """Test cleaning whitespace-only content."""
        content = "   \n  \t  \n  "
        
        cleaned = bibtex_processor.clean_malformed_entries(content)
        
        # Should handle whitespace gracefully
        assert isinstance(cleaned, str)
    
    def test_validate_bibtex(self, bibtex_processor):
        """Test BibTeX validation."""
        # Valid content
        valid_content = """@article{test2023,
            title = {Test Title},
            author = {Test Author},
            year = {2023}
        }"""
        
        issues = bibtex_processor.validate_bibtex(valid_content)
        assert len(issues) == 0
        
        # Invalid content
        invalid_content = """@article{test2023,
            title = {Test Title}
            author = {Test Author},
            year = {2023}
        }"""
        
        issues = bibtex_processor.validate_bibtex(invalid_content)
        assert len(issues) > 0
        assert any("Missing commas" in issue for issue in issues)
    
    def test_rename_url_fields(self, bibtex_processor):
        """Test renaming URL fields."""
        content = """@article{test2023,
            title = {Test Title},
            author = {Test Author},
            year = {2023},
            url = {https://example.com},
            urldate = {2023-01-01}
        }"""
        
        modified, count = bibtex_processor.rename_url_fields(content)
        
        assert count == 1
        assert "website = {https://example.com}" in modified
        assert "website_date = {2023-01-01}" in modified
        assert "url = {" not in modified
        assert "urldate = {" not in modified
    
    def test_rename_url_fields_no_urls(self, bibtex_processor):
        """Test renaming when no URL fields exist."""
        content = """@article{test2023,
            title = {Test Title},
            author = {Test Author},
            year = {2023}
        }"""
        
        modified, count = bibtex_processor.rename_url_fields(content)
        
        assert count == 0
        assert modified == content
    
    def test_extract_file_paths(self, bibtex_processor):
        """Test extracting file paths from file field."""
        file_field = "test.pdf:/path/to/test.pdf:application/pdf; image.jpg:/path/to/image.jpg:image/jpeg"
        
        paths = bibtex_processor.extract_file_paths(file_field)
        
        assert "/path/to/test.pdf" in paths
        assert "/path/to/image.jpg" in paths
    
    def test_extract_file_paths_empty(self, bibtex_processor):
        """Test extracting file paths from empty file field."""
        file_field = ""
        
        paths = bibtex_processor.extract_file_paths(file_field)
        
        assert len(paths) == 0
    
    def test_extract_thumbnail_files(self, bibtex_processor):
        """Test extracting thumbnail files from file field."""
        file_field = "test.pdf:/path/to/test.pdf:application/pdf; thumbnail.png:/path/to/thumbnail.png:image/png; image.jpg:/path/to/image.jpg:image/jpeg"
        
        thumbnails = bibtex_processor.extract_thumbnail_files(file_field)
        
        assert "/path/to/thumbnail.png" in thumbnails
        assert "/path/to/image.jpg" not in thumbnails  # Not a thumbnail
        assert "/path/to/test.pdf" not in thumbnails  # Not an image
    
    def test_extract_pdf_files(self, bibtex_processor):
        """Test extracting PDF files from file field."""
        file_field = "test.pdf:/path/to/test.pdf:application/pdf; image.jpg:/path/to/image.jpg:image/jpeg; doc.pdf:/path/to/doc.pdf:application/pdf"
        
        pdfs = bibtex_processor.extract_pdf_files(file_field)
        
        assert "/path/to/test.pdf" in pdfs
        assert "/path/to/doc.pdf" in pdfs
        assert "/path/to/image.jpg" not in pdfs  # Not a PDF
    
    def test_extract_image_files(self, bibtex_processor):
        """Test extracting image files from file field."""
        file_field = "test.pdf:/path/to/test.pdf:application/pdf; image.jpg:/path/to/image.jpg:image/jpeg; thumbnail.png:/path/to/thumbnail.png:image/png; figure.gif:/path/to/figure.gif:image/gif"
        
        images = bibtex_processor.extract_image_files(file_field)
        
        assert "/path/to/image.jpg" in images
        assert "/path/to/figure.gif" in images
        assert "/path/to/thumbnail.png" not in images  # Thumbnails excluded
        assert "/path/to/test.pdf" not in images  # Not an image
    
    def test_extract_agenda_pdfs(self, bibtex_processor):
        """Test extracting agenda PDF files from file field."""
        file_field = "test.pdf:/path/to/test.pdf:application/pdf; agenda.pdf:/path/to/agenda.pdf:application/pdf; meeting.pdf:/path/to/meeting.pdf:application/pdf"
        
        agendas = bibtex_processor.extract_agenda_pdfs(file_field)
        
        assert "/path/to/agenda.pdf" in agendas
        assert "/path/to/test.pdf" not in agendas  # No "agenda" in description
        assert "/path/to/meeting.pdf" not in agendas  # No "agenda" in description
    
    @patch('os.path.exists')
    @patch('os.path.getmtime')
    def test_extract_most_recent_pdf(self, mock_getmtime, mock_exists, bibtex_processor):
        """Test extracting most recent PDF file."""
        file_field = "old.pdf:/path/to/old.pdf:application/pdf; new.pdf:/path/to/new.pdf:application/pdf"
        
        # Mock file existence and modification times
        mock_exists.return_value = True
        mock_getmtime.side_effect = [1000, 2000]  # new.pdf is more recent
        
        most_recent = bibtex_processor.extract_most_recent_pdf(file_field)
        
        assert most_recent == "/path/to/new.pdf"
    
    def test_get_thumbnail_priority_files(self, bibtex_processor):
        """Test getting thumbnail priority files."""
        file_field = "test.pdf:/path/to/test.pdf:application/pdf; thumbnail.png:/path/to/thumbnail.png:image/png; agenda.pdf:/path/to/agenda.pdf:application/pdf"
        
        with patch('os.path.exists', return_value=True):
            priority_files = bibtex_processor.get_thumbnail_priority_files(file_field)
        
        assert len(priority_files) > 0
        # Should be sorted by priority
        priorities = [f['priority'] for f in priority_files]
        assert priorities == sorted(priorities)
    
    def test_is_valid_path(self, bibtex_processor):
        """Test path validation."""
        # Valid paths
        assert bibtex_processor._is_valid_path("/path/to/file.pdf")
        assert bibtex_processor._is_valid_path("file.pdf")
        assert bibtex_processor._is_valid_path("./relative/path.pdf")
        
        # Invalid paths
        assert not bibtex_processor._is_valid_path("")
        assert not bibtex_processor._is_valid_path(":")
        assert not bibtex_processor._is_valid_path(":::")
        assert not bibtex_processor._is_valid_path("invalid")
        assert not bibtex_processor._is_valid_path("//invalid")
    
    def test_fix_improper_escaping(self, bibtex_processor):
        """Test fixing improper LaTeX escaping."""
        content = "Title with \\\\& and \\\\$ and \\\\% characters"
        
        fixed = bibtex_processor.fix_improper_escaping(content)
        
        assert "\\&" in fixed
        assert "\\$" in fixed
        assert "\\%" in fixed
        assert "\\\\&" not in fixed
        assert "\\\\$" not in fixed
        assert "\\\\%" not in fixed
    
    def test_process_ignore_tags(self, bibtex_processor):
        """Test processing ignore tags in keywords."""
        content = """@article{test2023,
            title = {Test Title},
            author = {Test Author},
            year = {2023},
            keywords = {test, ignore:book, other}
        }"""
        
        processed = bibtex_processor.process_ignore_tags(content)
        
        assert "@book{test2023" in processed
        assert "ignore:book" not in processed
        assert "keywords = {test, other}" in processed
    
    def test_fix_duplicated_entry_types(self, bibtex_processor):
        """Test fixing duplicated entry types."""
        content = "@newspaper{article{test2023, title = {Test}}}"
        
        fixed = bibtex_processor._fix_duplicated_entry_types(content)
        
        assert "@article{test2023" in fixed
        assert "@newspaper{article{test2023" not in fixed
    
    def test_clean_additional_issues(self, bibtex_processor):
        """Test cleaning additional common issues."""
        content = """@article{test2023,
            title = {Test Title}
            author = {Test Author},,
            year = {2023},
        }"""
        
        cleaned = bibtex_processor._clean_additional_issues(content)
        
        # Should fix comma issues
        assert ",," not in cleaned
        assert not cleaned.strip().endswith(",")
    
    def test_clean_braces_from_fields(self, bibtex_processor):
        """Test cleaning braces from text fields."""
        content = """@article{test2023,
            title = {Title with {nested} braces},
            author = {Test Author},
            year = {2023}
        }"""
        
        cleaned = bibtex_processor._clean_braces_from_fields(content)
        
        # Should clean braces from title field
        assert "Title with nested braces" in cleaned
        assert "Title with {nested} braces" not in cleaned
    
    def test_clean_individual_entry(self, bibtex_processor):
        """Test cleaning individual entry."""
        content = """@article{test2023,
            title = {Test Title}
            author = {Test Author}
            year = {2023}
        }"""
        
        cleaned = bibtex_processor._clean_individual_entry(content)
        
        # Should be parseable after cleaning
        citation_key, fields = bibtex_processor.parse_bibtex_entry(cleaned)
        assert citation_key == "test2023"
        assert len(fields) > 0
    
    def test_fix_brace_issues(self, bibtex_processor):
        """Test fixing brace issues."""
        content = """@article{test2023,
            title = {Test Title},
            author = {Test Author},
            year = {2023}"""
        
        fixed = bibtex_processor._fix_brace_issues(content)
        
        # Should add missing closing brace
        assert fixed.count('{') == fixed.count('}')
    
    def test_fix_comma_issues(self, bibtex_processor):
        """Test fixing comma issues."""
        content = """@article{test2023,
            title = {Test Title},,
            author = {Test Author},
            year = {2023},
        }"""
        
        fixed = bibtex_processor._fix_comma_issues(content)
        
        # Should fix double commas and trailing commas
        assert ",," not in fixed
        assert not fixed.strip().endswith(",")
