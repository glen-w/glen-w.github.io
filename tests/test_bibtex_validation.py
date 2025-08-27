#!/usr/bin/env python3
"""
Tests for BibTeX syntax validation using bibtexparser library.
Ensures that all generated BibTeX output is syntactically correct.
"""

import pytest
import tempfile
import os
import sys

# Add the parent directory to the path so we can import process_papers
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import bibtexparser
    from bibtexparser.bparser import BibTexParser
    from bibtexparser.bwriter import BibTexWriter
    BIBTEXPARSER_AVAILABLE = True
except ImportError:
    BIBTEXPARSER_AVAILABLE = True  # We'll skip tests if not available
    BIBTEXPARSER_AVAILABLE = False

from process_papers import (
    add_pdf_and_preview_tags,
    parse_bibtex_entry,
    clean_nested_braces
)


@pytest.mark.skipif(not BIBTEXPARSER_AVAILABLE, reason="bibtexparser not available")
class TestBibTeXSyntaxValidation:
    """Test that generated BibTeX syntax is valid using bibtexparser."""
    
    def test_parse_bibtex_entry_output_validity(self):
        """Test that parse_bibtex_entry produces valid BibTeX syntax."""
        # Test various BibTeX entry formats
        test_entries = [
            # Simple entry
            """@article{test2023,
                title = {Simple Title},
                author = {Test Author},
                year = {2023}
            }""",
            
            # Entry with nested braces
            """@article{test2023,
                title = {Title with {nested} braces},
                author = {Author with {complex} name},
                journal = {Journal {of} Science}
            }""",
            
            # Entry with special characters
            """@article{test2023,
                title = {Title with @#$%^&*() special chars!},
                author = {Author, Test and Another, Author},
                year = {2023},
                doi = {10.1000/123.456}
            }""",
            
            # Entry with multiple authors
            """@article{test2023,
                title = {Multi-author paper},
                author = {Smith, John and Doe, Jane and Brown, Bob},
                year = {2023},
                journal = {Test Journal}
            }""",
            
            # Entry with URLs and DOIs
            """@article{test2023,
                title = {Paper with metadata},
                author = {Author, Test},
                year = {2023},
                doi = {10.1000/123.456},
                url = {https://example.com/paper}
            }"""
        ]
        
        for i, entry in enumerate(test_entries):
            # Create a fresh parser for each entry to avoid accumulation
            parser = BibTexParser(common_strings=True)
            parser.ignore_nonstandard_types = False
            parser.homogenize_fields = False
            
            # Parse with our function
            citation_key, fields = parse_bibtex_entry(entry)
            assert citation_key is not None, f"Entry {i}: No citation key found"
            assert len(fields) > 0, f"Entry {i}: No fields found"
            
            # Validate that the parsed entry can be reconstructed and parsed again
            reconstructed_entry = self._reconstruct_entry(citation_key, fields)
            
            # Parse the reconstructed entry with bibtexparser
            parsed = parser.parse(reconstructed_entry)
            assert len(parsed.entries) == 1, f"Entry {i}: Expected 1 entry, got {len(parsed.entries)}"
            assert parsed.entries[0]['ID'] == citation_key
            
            # Check that all fields are preserved
            for field_name, field_value in fields.items():
                assert parsed.entries[0].get(field_name) == field_value, f"Entry {i}: Field {field_name} mismatch"
    
    def test_add_pdf_and_preview_tags_syntax_validity(self):
        """Test that add_pdf_and_preview_tags produces valid BibTeX syntax."""
        # Test adding tags to various entry types
        test_cases = [
            # Simple entry
            ("""@article{test2023,
                title = {Test Title},
                author = {Test Author}
            }""", "test.jpeg", "test.pdf", None),
            
            # Entry with existing fields
            ("""@article{test2023,
                title = {Test Title},
                author = {Test Author},
                year = {2023},
                journal = {Test Journal}
            }""", "test.jpeg", "test.pdf", None),
            
            # Entry with DOI (should get dimensions tag)
            ("""@article{test2023,
                title = {Test Title with DOI},
                author = {Test Author},
                doi = {10.1000/123.456}
            }""", "test.jpeg", "test.pdf", {
                'title': 'Test Title with DOI',
                'author': 'Test Author',
                'doi': '10.1000/123.456'
            })
        ]
        
        for i, (bibtex_content, preview_filename, pdf_filename, fields) in enumerate(test_cases):
            # Create a fresh parser for each test case to avoid accumulation
            test_parser = BibTexParser(common_strings=True)
            test_parser.ignore_nonstandard_types = False
            test_parser.homogenize_fields = False
            
            # Add tags
            modified_content = add_pdf_and_preview_tags(
                bibtex_content, "test2023", preview_filename, pdf_filename, fields
            )
            
            # Validate that the modified content is valid BibTeX
            try:
                parsed = test_parser.parse(modified_content)
                assert len(parsed.entries) == 1, f"Test case {i}: Expected 1 entry, got {len(parsed.entries)}"
                
                entry = parsed.entries[0]
                assert entry['ID'] == "test2023"
                assert entry.get('preview') == preview_filename
                assert entry.get('pdf') == pdf_filename
                
                # Check that original fields are preserved
                assert entry.get('title') is not None
                assert entry.get('author') is not None
                
                # Check dimensions tag if DOI is present
                if fields and 'doi' in fields and fields['doi'].strip():
                    assert entry.get('dimensions') == 'true'
                else:
                    assert entry.get('dimensions') is None
                
            except Exception as e:
                pytest.fail(f"Test case {i} failed: Generated BibTeX is invalid: {e}\nContent: {modified_content}")
    
    def test_clean_nested_braces_preserves_syntax(self):
        """Test that clean_nested_braces preserves valid BibTeX syntax."""
        test_cases = [
            "Simple text",
            "Text with {single} braces",
            "Text with {nested {braces}}",
            "Complex {text {with {multiple {levels}}}} of nesting",
            "Text with @#$%^&*() special chars!",
            "Text with {braces} and @#$%^&*() chars!"
        ]
        
        for text in test_cases:
            cleaned = clean_nested_braces(text)
            
            # Check that no braces remain
            assert '{' not in cleaned
            assert '}' not in cleaned
            
            # Check that content is preserved (minus braces)
            # Remove braces from original for comparison
            original_no_braces = text.replace('{', '').replace('}', '')
            assert cleaned == original_no_braces
    
    def test_full_bibtex_file_validation(self):
        """Test that a complete BibTeX file with our modifications is valid."""
        # Create a complete BibTeX file with multiple entries
        bibtex_content = """@article{test2023a,
            title = {First Test Title},
            author = {Author, First},
            year = {2023},
            journal = {Test Journal}
        }

        @article{test2023b,
            title = {Second Test Title with {nested} braces},
            author = {Author, Second and Another, Author},
            year = {2023},
            doi = {10.1000/123.456}
        }

        @book{testbook2023,
            title = {Test Book Title},
            author = {Book, Author},
            year = {2023},
            publisher = {Test Publisher}
        }"""
        
        # Add tags to each entry
        modified_content = bibtex_content
        entries = [
            ("test2023a", "first.jpeg", "first.pdf"),
            ("test2023b", "second.jpeg", "second.pdf"),
            ("testbook2023", "book.jpeg", "book.pdf")
        ]
        
        for citation_key, preview_filename, pdf_filename in entries:
            # Create fields dict for the entry to check for DOI
            fields = {}
            if citation_key == "test2023b":  # This entry has a DOI
                fields = {
                    'title': 'Second Test Title with {nested} braces',
                    'author': 'Author, Second and Another, Author',
                    'year': '2023',
                    'doi': '10.1000/123.456'
                }
            
            modified_content = add_pdf_and_preview_tags(
                modified_content, citation_key, preview_filename, pdf_filename, fields
            )
        
        # Validate the complete file
        parser = BibTexParser(common_strings=True)
        parser.ignore_nonstandard_types = False
        parser.homogenize_fields = False
        
        try:
            parsed = parser.parse(modified_content)
            assert len(parsed.entries) == 3
            
            # Check that all entries have the required tags
            for entry in parsed.entries:
                assert 'preview' in entry
                assert 'pdf' in entry
                assert entry['title'] is not None
                assert entry['author'] is not None
                
                # Check dimensions tag for entry with DOI
                if entry['ID'] == 'test2023b':
                    assert entry.get('dimensions') == 'true'
                else:
                    assert entry.get('dimensions') is None
                
        except Exception as e:
            pytest.fail(f"Complete BibTeX file is invalid: {e}\nContent: {modified_content}")
    
    def test_bibtex_writer_compatibility(self):
        """Test that our modified BibTeX can be written and parsed again."""
        # Create a test entry with DOI
        original_entry = """@article{test2023,
            title = {Test Title},
            author = {Test Author},
            year = {2023},
            doi = {10.1000/123.456}
        }"""
        
        # Create fields dict to pass to the function
        fields = {
            'title': 'Test Title',
            'author': 'Test Author',
            'year': '2023',
            'doi': '10.1000/123.456'
        }
        
        # Add tags
        modified_content = add_pdf_and_preview_tags(
            original_entry, "test2023", "test.jpeg", "test.pdf", fields
        )
        
        # Parse with bibtexparser
        parser = BibTexParser(common_strings=True)
        parsed = parser.parse(modified_content)
        
        # Write back using bibtexparser
        writer = BibTexWriter()
        writer.indent = '    '
        writer.comma_first = False
        
        written_content = writer.write(parsed)
        
        # Parse the written content again
        reparsed_parser = BibTexParser(common_strings=True)
        reparsed = reparsed_parser.parse(written_content)
        
        # Verify the content is preserved
        assert len(reparsed.entries) == 1
        entry = reparsed.entries[0]
        assert entry['ID'] == "test2023"
        assert entry.get('title') == "Test Title"
        assert entry.get('author') == "Test Author"
        assert entry.get('year') == "2023"
        assert entry.get('doi') == "10.1000/123.456"
        assert entry.get('preview') == "test.jpeg"
        assert entry.get('pdf') == "test.pdf"
        assert entry.get('dimensions') == "true"  # Should have dimensions tag due to DOI
    
    def _reconstruct_entry(self, citation_key, fields):
        """Helper method to reconstruct a BibTeX entry from parsed fields."""
        entry_lines = [f"@article{{{citation_key},"]
        
        for field_name, field_value in fields.items():
            entry_lines.append(f"    {field_name} = {{{field_value}}},")
        
        # Remove trailing comma from last field
        if entry_lines:
            entry_lines[-1] = entry_lines[-1].rstrip(',')
        
        entry_lines.append("}")
        return "\n".join(entry_lines)


@pytest.mark.skipif(not BIBTEXPARSER_AVAILABLE, reason="bibtexparser not available")
class TestBibTeXEdgeCases:
    """Test edge cases and potential syntax issues."""
    
    def test_empty_fields_handling(self):
        """Test handling of empty fields."""
        entry = """@article{test2023,
            title = {},
            author = {},
            year = {}
        }"""
        
        citation_key, fields = parse_bibtex_entry(entry)
        assert citation_key == "test2023"
        assert fields["title"] == ""
        assert fields["author"] == ""
        assert fields["year"] == ""
    
    def test_fields_with_only_braces(self):
        """Test fields that contain only braces."""
        entry = """@article{test2023,
            title = {{}},
            author = {{}},
            year = {2023}
        }"""
        
        citation_key, fields = parse_bibtex_entry(entry)
        assert citation_key == "test2023"
        assert fields["title"] == ""
        assert fields["author"] == ""
        assert fields["year"] == "2023"
    
    def test_fields_with_quotes(self):
        """Test fields that contain quotes."""
        entry = """@article{test2023,
            title = {Title with "quotes"},
            author = {Author with 'apostrophes'},
            year = {2023}
        }"""
        
        citation_key, fields = parse_bibtex_entry(entry)
        assert citation_key == "test2023"
        assert fields["title"] == 'Title with "quotes"'
        assert fields["author"] == "Author with 'apostrophes'"
        assert fields["year"] == "2023"
    
    def test_fields_with_newlines(self):
        """Test fields that contain newlines."""
        entry = """@article{test2023,
            title = {Title with
newlines},
            author = {Test Author},
            year = {2023}
        }"""
        
        citation_key, fields = parse_bibtex_entry(entry)
        assert citation_key == "test2023"
        assert "newlines" in fields["title"]
        assert fields["author"] == "Test Author"
        assert fields["year"] == "2023"


if __name__ == "__main__":
    pytest.main([__file__])
