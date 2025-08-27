#!/usr/bin/env python3
"""
Tests using the real papers.bib file to ensure our script works with actual data.
"""

import pytest
import os
import tempfile
import shutil
import sys

# Add the parent directory to the path so we can import process_papers
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import bibtexparser
    from bibtexparser.bparser import BibTexParser
    BIBTEXPARSER_AVAILABLE = True
except ImportError:
    BIBTEXPARSER_AVAILABLE = True
    BIBTEXPARSER_AVAILABLE = False

from process_papers import (
    parse_bibtex_entry,
    clean_nested_braces,
    extract_file_paths,
    prepare_pdf_metadata
)


@pytest.mark.skipif(not BIBTEXPARSER_AVAILABLE, reason="bibtexparser not available")
class TestRealBibTeXFile:
    """Test our script with the actual papers.bib file."""
    
    @pytest.fixture
    def papers_bib_path(self):
        """Get the path to the real papers.bib file."""
        bib_path = "_bibliography/papers.bib"
        if not os.path.exists(bib_path):
            pytest.skip(f"Real papers.bib file not found at {bib_path}")
        return bib_path
    
    @pytest.fixture
    def papers_bib_content(self, papers_bib_path):
        """Read the content of the real papers.bib file."""
        with open(papers_bib_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def test_real_bibtex_file_parsing(self, papers_bib_content):
        """Test that we can parse the real papers.bib file."""
        # Split into individual entries
        entries = [entry.strip() for entry in papers_bib_content.split('\n@') if entry.strip()]
        
        # Skip the first entry if it doesn't start with @
        if entries and not entries[0].startswith('@'):
            entries[0] = '@' + entries[0]
        
        # Test parsing each entry
        for i, entry in enumerate(entries):
            if not entry.startswith('@'):
                continue
                
            try:
                citation_key, fields = parse_bibtex_entry(entry)
                
                # Basic validation
                assert citation_key is not None, f"Entry {i} has no citation key"
                assert len(fields) > 0, f"Entry {i} has no fields"
                
                # Check for common required fields
                if 'title' in fields:
                    assert isinstance(fields['title'], str), f"Entry {i} title is not string"
                    assert len(fields['title']) > 0, f"Entry {i} title is empty"
                
                if 'author' in fields:
                    assert isinstance(fields['author'], str), f"Entry {i} author is not string"
                    assert len(fields['author']) > 0, f"Entry {i} author is empty"
                
                if 'year' in fields:
                    assert isinstance(fields['year'], str), f"Entry {i} year is not string"
                    assert len(fields['year']) > 0, f"Entry {i} year is empty"
                
            except Exception as e:
                pytest.fail(f"Failed to parse entry {i}: {e}\nEntry: {entry[:200]}...")
    
    def test_real_bibtex_file_bibtexparser_compatibility(self, papers_bib_content):
        """Test that our parsed entries are compatible with bibtexparser."""
        parser = BibTexParser(common_strings=True)
        parser.ignore_nonstandard_types = False
        parser.homogenize_fields = False
        
        # Parse with bibtexparser first
        bibtexparser_parsed = parser.parse(papers_bib_content)
        
        # Split into individual entries for our parser
        entries = [entry.strip() for entry in papers_bib_content.split('\n@') if entry.strip()]
        if entries and not entries[0].startswith('@'):
            entries[0] = '@' + entries[0]
        
        # Compare a few entries
        test_count = min(5, len(entries))  # Test first 5 entries
        
        for i in range(test_count):
            entry = entries[i]
            if not entry.startswith('@'):
                continue
                
            try:
                # Parse with our function
                our_citation_key, our_fields = parse_bibtex_entry(entry)
                
                # Find corresponding entry in bibtexparser output
                bibtexparser_entry = None
                for parsed_entry in bibtexparser_parsed.entries:
                    if parsed_entry['ID'] == our_citation_key:
                        bibtexparser_entry = parsed_entry
                        break
                
                if bibtexparser_entry:
                    # Compare key fields
                    for field_name in ['title', 'author', 'year']:
                        if field_name in our_fields and field_name in bibtexparser_entry:
                            our_value = our_fields[field_name]
                            their_value = bibtexparser_entry[field_name]
                            
                            # Clean both values for comparison (remove extra whitespace)
                            our_clean = ' '.join(our_value.split())
                            their_clean = ' '.join(their_value.split())
                            
                            # Values should be similar (our parser removes braces)
                            assert our_clean in their_clean or their_clean in our_clean, \
                                f"Field {field_name} mismatch in entry {i}: '{our_clean}' vs '{their_clean}'"
                
            except Exception as e:
                pytest.fail(f"Failed to compare entry {i}: {e}")
    
    def test_real_bibtex_file_field_extraction(self, papers_bib_content):
        """Test field extraction from real BibTeX entries."""
        entries = [entry.strip() for entry in papers_bib_content.split('\n@') if entry.strip()]
        if entries and not entries[0].startswith('@'):
            entries[0] = '@' + entries[0]
        
        # Test a few entries
        test_count = min(3, len(entries))
        
        for i in range(test_count):
            entry = entries[i]
            if not entry.startswith('@'):
                continue
                
            try:
                citation_key, fields = parse_bibtex_entry(entry)
                
                # Test title cleaning
                if 'title' in fields:
                    clean_title = clean_nested_braces(fields['title'])
                    assert '{' not in clean_title, f"Entry {i} title still has braces after cleaning"
                    assert '}' not in clean_title, f"Entry {i} title still has braces after cleaning"
                
                # Test author name extraction
                if 'author' in fields:
                    author = fields['author']
                    # Check that author field is reasonable
                    assert len(author) > 0, f"Entry {i} has empty author field"
                    assert ',' in author or ' and ' in author, f"Entry {i} author format unexpected: {author}"
                
                # Test file field extraction if present
                if 'file' in fields:
                    file_paths = extract_file_paths(fields['file'])
                    # File paths should be a list
                    assert isinstance(file_paths, list), f"Entry {i} file_paths is not a list"
                
            except Exception as e:
                pytest.fail(f"Failed to test field extraction for entry {i}: {e}")
    
    def test_real_bibtex_file_metadata_preparation(self, papers_bib_content):
        """Test metadata preparation from real BibTeX entries."""
        entries = [entry.strip() for entry in papers_bib_content.split('\n@') if entry.strip()]
        if entries and not entries[0].startswith('@'):
            entries[0] = '@' + entries[0]
        
        # Test a few entries
        test_count = min(3, len(entries))
        
        for i in range(test_count):
            entry = entries[i]
            if not entry.startswith('@'):
                continue
                
            try:
                citation_key, fields = parse_bibtex_entry(entry)
                
                # Prepare metadata
                metadata = prepare_pdf_metadata(fields)
                
                # Basic validation
                assert isinstance(metadata, dict), f"Entry {i} metadata is not a dict"
                
                # Check that metadata contains expected fields when available
                if 'title' in fields:
                    assert 'title' in metadata, f"Entry {i} missing title in metadata"
                    assert metadata['title'] == fields['title'], f"Entry {i} title mismatch in metadata"
                
                if 'author' in fields:
                    assert 'author' in metadata, f"Entry {i} missing author in metadata"
                
                # Check that producer is always set
                assert 'producer' in metadata, f"Entry {i} missing producer in metadata"
                assert metadata['producer'] == "glen-w's Al-folio Helper"
                
            except Exception as e:
                pytest.fail(f"Failed to test metadata preparation for entry {i}: {e}")
    
    def test_real_bibtex_file_special_characters(self, papers_bib_content):
        """Test handling of special characters in real BibTeX entries."""
        entries = [entry.strip() for entry in papers_bib_content.split('\n@') if entry.strip()]
        if entries and not entries[0].startswith('@'):
            entries[0] = '@' + entries[0]
        
        # Look for entries with special characters
        special_char_entries = []
        for entry in entries:
            if any(char in entry for char in ['@', '#', '$', '%', '^', '&', '*', '(', ')', '!']):
                special_char_entries.append(entry)
        
        # Test a few entries with special characters
        test_count = min(2, len(special_char_entries))
        
        successful_parses = 0
        for i in range(test_count):
            entry = special_char_entries[i]
            try:
                citation_key, fields = parse_bibtex_entry(entry)
                
                # Should parse successfully despite special characters
                if citation_key is not None and len(fields) > 0:
                    successful_parses += 1
                    
                    # Test title cleaning with special characters
                    if 'title' in fields:
                        clean_title = clean_nested_braces(fields['title'])
                        assert '{' not in clean_title
                        assert '}' not in clean_title
                
            except Exception as e:
                # Some entries may not parse due to complex BibTeX syntax
                # This is expected with real BibTeX files
                print(f"    Note: Entry {i} could not be parsed: {e}")
                continue
        
        # At least some entries should parse successfully
        assert successful_parses > 0, "No entries with special characters could be parsed"


if __name__ == "__main__":
    pytest.main([__file__])
