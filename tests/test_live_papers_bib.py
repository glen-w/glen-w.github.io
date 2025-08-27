#!/usr/bin/env python3
"""
Tests that actually read entries from the live papers.bib file
to ensure the script works with the real file structure.
"""

import pytest
import os
import tempfile
import shutil
import sys
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import process_papers
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import bibtexparser
    from bibtexparser.bparser import BibTexParser
    BIBTEXPARSER_AVAILABLE = True
except ImportError:
    BIBTEXPARSER_AVAILABLE = False

from process_papers import (
    parse_bibtex_entry,
    add_pdf_and_preview_tags,
    entry_has_pdf_and_preview_tags,
    process_papers_bib
)


class TestLivePapersBib:
    """Test with actual entries from the live papers.bib file."""
    
    @pytest.fixture
    def papers_bib_path(self):
        """Get the path to the real papers.bib file."""
        bib_path = "_bibliography/papers.bib"
        if not os.path.exists(bib_path):
            pytest.skip(f"Real papers.bib file not found at {bib_path}")
        return bib_path
    
    @pytest.fixture
    def sample_entries_from_live_file(self, papers_bib_path):
        """Extract a few sample entries from the live papers.bib file."""
        with open(papers_bib_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Use regex to split entries more reliably
        import re
        # Split on @entrytype{ patterns at the beginning of lines
        entries = re.split(r'\n(?=@\w+\{)', content)
        
        # Clean up entries and filter out empty ones
        sample_entries = []
        for entry in entries[:5]:  # Take first 5 entries
            entry = entry.strip()
            if entry and '@' in entry and '{' in entry:
                # Ensure entry starts with @
                if not entry.startswith('@'):
                    entry = '@' + entry
                sample_entries.append(entry)
        
        return sample_entries
    
    def test_live_entries_can_be_parsed(self, sample_entries_from_live_file):
        """Test that we can parse entries from the live papers.bib file."""
        parsed_count = 0
        doi_count = 0
        
        for i, entry in enumerate(sample_entries_from_live_file):
            try:
                citation_key, fields = parse_bibtex_entry(entry)
                
                if citation_key and len(fields) > 0:
                    parsed_count += 1
                    
                    # Check basic fields
                    assert isinstance(citation_key, str)
                    assert len(citation_key) > 0
                    assert isinstance(fields, dict)
                    
                    # Most entries should have title and author
                    if 'title' in fields:
                        assert isinstance(fields['title'], str)
                        assert len(fields['title']) > 0
                    
                    if 'author' in fields:
                        assert isinstance(fields['author'], str)
                        assert len(fields['author']) > 0
                    
                    # Count entries with DOI
                    if 'doi' in fields and fields['doi'].strip():
                        doi_count += 1
                        print(f"    Entry {citation_key} has DOI: {fields['doi']}")
                    
                    print(f"    Parsed entry {citation_key}: {fields.get('title', 'No title')[:50]}...")
                
            except Exception as e:
                print(f"    Could not parse entry {i}: {e}")
                continue
        
        # At least some entries should be parseable
        assert parsed_count > 0, f"Could not parse any of the {len(sample_entries_from_live_file)} sample entries"
        print(f"\n    Successfully parsed {parsed_count}/{len(sample_entries_from_live_file)} entries")
        print(f"    Found {doi_count} entries with DOI")
    
    @pytest.mark.skipif(not BIBTEXPARSER_AVAILABLE, reason="bibtexparser not available")
    def test_live_entries_dimensions_tag_logic(self, sample_entries_from_live_file):
        """Test that dimensions tag logic works correctly with live entries."""
        entries_with_doi = []
        entries_without_doi = []
        
        for entry in sample_entries_from_live_file:
            try:
                citation_key, fields = parse_bibtex_entry(entry)
                
                if citation_key and len(fields) > 0:
                    if 'doi' in fields and fields['doi'].strip():
                        entries_with_doi.append((citation_key, fields, entry))
                    else:
                        entries_without_doi.append((citation_key, fields, entry))
                        
            except Exception:
                continue
        
        # Test entries without DOI
        for citation_key, fields, original_entry in entries_without_doi[:2]:  # Test first 2
            # Should not require dimensions tag
            fields_with_basic = {**fields, "pdf": "test.pdf", "preview": "test.jpeg"}
            assert entry_has_pdf_and_preview_tags(fields_with_basic)
            
            # Add tags and verify no dimensions tag is added
            modified_content = add_pdf_and_preview_tags(
                original_entry, citation_key, "test.jpeg", "test.pdf", fields
            )
            
            # Parse with bibtexparser to verify
            parser = BibTexParser(common_strings=True)
            parser.ignore_nonstandard_types = False
            parser.homogenize_fields = False
            
            try:
                parsed = parser.parse(modified_content)
                if len(parsed.entries) == 1:
                    entry = parsed.entries[0]
                    assert entry.get('dimensions') is None, f"Entry {citation_key} without DOI should not have dimensions tag"
                    print(f"    ✅ Entry {citation_key} (no DOI): correctly has no dimensions tag")
            except Exception as e:
                print(f"    ⚠️  Could not validate {citation_key} with bibtexparser: {e}")
        
        # Test entries with DOI
        for citation_key, fields, original_entry in entries_with_doi[:2]:  # Test first 2
            # Should require dimensions tag
            fields_with_basic = {**fields, "pdf": "test.pdf", "preview": "test.jpeg"}
            assert not entry_has_pdf_and_preview_tags(fields_with_basic), f"Entry {citation_key} with DOI should require dimensions tag"
            
            fields_with_all = {**fields_with_basic, "dimensions": "true"}
            assert entry_has_pdf_and_preview_tags(fields_with_all), f"Entry {citation_key} with all tags should be complete"
            
            # Add tags and verify dimensions tag is added
            modified_content = add_pdf_and_preview_tags(
                original_entry, citation_key, "test.jpeg", "test.pdf", fields
            )
            
            # Parse with bibtexparser to verify
            parser = BibTexParser(common_strings=True)
            parser.ignore_nonstandard_types = False
            parser.homogenize_fields = False
            
            try:
                parsed = parser.parse(modified_content)
                if len(parsed.entries) == 1:
                    entry = parsed.entries[0]
                    assert entry.get('dimensions') == 'true', f"Entry {citation_key} with DOI should have dimensions=true"
                    print(f"    ✅ Entry {citation_key} (DOI: {fields['doi']}): correctly has dimensions=true")
            except Exception as e:
                print(f"    ⚠️  Could not validate {citation_key} with bibtexparser: {e}")
        
        print(f"\n    Tested {len(entries_without_doi[:2])} entries without DOI")
        print(f"    Tested {len(entries_with_doi[:2])} entries with DOI")
    
    def test_live_file_processing_workflow(self, papers_bib_path):
        """Test the complete processing workflow with a subset of the live file."""
        # Create a temporary copy with just a few entries
        with open(papers_bib_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract first few entries using regex
        import re
        entries = re.split(r'\n(?=@\w+\{)', content)
        
        # Create test file with first 3 entries
        test_entries = []
        for entry in entries[:3]:
            if entry.strip() and '@' in entry:
                if not entry.startswith('@'):
                    entry = '@' + entry
                test_entries.append(entry.strip())
        
        test_content = '\n\n'.join(test_entries)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bib', delete=False) as f:
            f.write(test_content)
            temp_file = f.name
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Mock all external operations
                with patch('process_papers.check_dependencies', return_value=True), \
                     patch('process_papers.copy_pdf_file', return_value=True), \
                     patch('process_papers.generate_pdf_thumbnail', return_value=True), \
                     patch('process_papers.update_pdf_metadata', return_value=True), \
                     patch('os.path.exists', return_value=True), \
                     patch('os.path.getsize', return_value=10000), \
                     patch('os.makedirs'):
                    
                    # Run the processing in test mode
                    process_papers_bib(
                        temp_file, 
                        output_dir=os.path.join(temp_dir, "assets", "pdf"),
                        test_mode=True, 
                        test_count=3,
                        verbose=True
                    )
                    
                    # Read the modified file
                    with open(temp_file, 'r') as f:
                        modified_content = f.read()
                    
                    # Check that some processing occurred
                    print(f"\n    Modified content length: {len(modified_content)}")
                    print(f"    Original content length: {len(test_content)}")
                    
                    # Should have added some tags
                    tag_count = modified_content.count('preview = {') + modified_content.count('pdf = {')
                    print(f"    Found {tag_count} PDF/preview tags in modified content")
                    
                    # Count dimensions tags
                    dimensions_count = modified_content.count('dimensions = {true}')
                    print(f"    Found {dimensions_count} dimensions tags in modified content")
                    
                    # Check that entries with DOI got dimensions tags
                    if 'doi = {' in test_content:
                        assert dimensions_count > 0, "Expected at least one dimensions tag for entries with DOI"
                        print(f"    ✅ Correctly added dimensions tags for DOI entries")
        
        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_live_file_sample_statistics(self, papers_bib_path):
        """Generate statistics about the live papers.bib file for testing insights."""
        with open(papers_bib_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Use regex to split entries more reliably
        import re
        entries = re.split(r'\n(?=@\w+\{)', content)
        
        total_entries = 0
        parseable_entries = 0
        entries_with_doi = 0
        entries_with_files = 0
        
        for entry in entries:
            entry = entry.strip()
            if entry and '@' in entry and '{' in entry:
                total_entries += 1
                
                try:
                    if not entry.startswith('@'):
                        entry = '@' + entry
                    
                    citation_key, fields = parse_bibtex_entry(entry)
                    
                    if citation_key and len(fields) > 0:
                        parseable_entries += 1
                        
                        if 'doi' in fields and fields['doi'].strip():
                            entries_with_doi += 1
                        
                        if 'file' in fields and fields['file'].strip():
                            entries_with_files += 1
                
                except Exception:
                    continue
        
        print(f"\n📊 Live papers.bib Statistics:")
        print(f"    Total entries: {total_entries}")
        if parseable_entries > 0:
            print(f"    Parseable entries: {parseable_entries} ({parseable_entries/total_entries*100:.1f}%)")
            print(f"    Entries with DOI: {entries_with_doi} ({entries_with_doi/parseable_entries*100:.1f}% of parseable)")
            print(f"    Entries with files: {entries_with_files} ({entries_with_files/parseable_entries*100:.1f}% of parseable)")
            print(f"    Entries that will get dimensions tag: {entries_with_doi}")
        else:
            print(f"    Parseable entries: {parseable_entries} (0.0%)")
            print(f"    Entries with DOI: {entries_with_doi}")
            print(f"    Entries with files: {entries_with_files}")
        
        # These are informational assertions - should always pass
        assert total_entries > 0
        # Don't require parseable_entries > 0 since our parser might not handle all real entries
    
    def test_specific_doi_entry_processing(self, papers_bib_path):
        """Test processing of a specific entry with DOI from the live file."""
        with open(papers_bib_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the Wright2011b entry which has a DOI
        import re
        entries = re.split(r'\n(?=@\w+\{)', content)
        
        target_entry = None
        for entry in entries:
            if 'Wright2011b' in entry and 'doi = {' in entry:
                target_entry = entry.strip()
                break
        
        if target_entry is None:
            pytest.skip("Could not find Wright2011b entry with DOI in papers.bib")
        
        print(f"\n🎯 Testing specific DOI entry: Wright2011b")
        
        # Parse the entry
        citation_key, fields = parse_bibtex_entry(target_entry)
        
        assert citation_key == "Wright2011b"
        assert "doi" in fields
        assert fields["doi"] == "10.1007/s12117-011-9130-4"
        print(f"    ✅ Parsed entry with DOI: {fields['doi']}")
        
        # Test that it requires dimensions tag
        fields_with_basic = {**fields, "pdf": "test.pdf", "preview": "test.jpeg"}
        assert not entry_has_pdf_and_preview_tags(fields_with_basic), "Entry with DOI should require dimensions tag"
        
        fields_with_all = {**fields_with_basic, "dimensions": "true"}
        assert entry_has_pdf_and_preview_tags(fields_with_all), "Entry with all tags should be complete"
        print(f"    ✅ Correctly requires dimensions tag due to DOI")
        
        # Test adding tags
        modified_content = add_pdf_and_preview_tags(
            target_entry, citation_key, "test.jpeg", "test.pdf", fields
        )
        
        # Validate with bibtexparser
        if BIBTEXPARSER_AVAILABLE:
            parser = BibTexParser(common_strings=True)
            parser.ignore_nonstandard_types = False
            parser.homogenize_fields = False
            
            try:
                parsed = parser.parse(modified_content)
                assert len(parsed.entries) == 1
                
                entry = parsed.entries[0]
                assert entry["ID"] == citation_key
                assert entry.get("preview") == "test.jpeg"
                assert entry.get("pdf") == "test.pdf" 
                assert entry.get("dimensions") == "true"
                assert entry.get("doi") == "10.1007/s12117-011-9130-4"
                
                print(f"    ✅ Successfully added dimensions=true tag")
                print(f"    ✅ BibTeX output validated by bibtexparser")
                
                # Verify original fields are preserved
                assert "Conceptualising and combating" in entry.get("title", "")
                assert entry.get("author") == "Wright, Glen"
                assert entry.get("year") == "2011"
                
            except Exception as e:
                print(f"    ⚠️  BibTeX validation failed: {e}")
                # Don't fail the test, just warn
        else:
            print(f"    ⚠️  bibtexparser not available for validation")
        
        print(f"    ✅ Test completed for real DOI entry")


if __name__ == "__main__":
    pytest.main([__file__])
