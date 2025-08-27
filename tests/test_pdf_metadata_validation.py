#!/usr/bin/env python3
"""
Comprehensive tests for PDF metadata validation.
Ensures that metadata is actually written to PDF files and can be read back correctly.
"""

import pytest
import os
import tempfile
import shutil
import sys
from unittest.mock import patch, MagicMock, mock_open

# Add the parent directory to the path so we can import process_papers
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

from process_papers import (
    prepare_pdf_metadata,
    update_pdf_metadata
)


class TestPDFMetadataValidation:
    """Test that PDF metadata is correctly written and can be read back."""
    
    def test_prepare_pdf_metadata_comprehensive(self):
        """Test comprehensive metadata preparation with all possible fields."""
        # Test with complete fields
        fields = {
            'title': 'Test Paper Title with {braces}',
            'author': 'Smith, John and Doe, Jane',
            'year': '2023',
            'journal': 'Test Journal',
            'abstract': 'This is a test abstract with some content.',
            'keywords': 'test, metadata, pdf',
            'doi': '10.1000/123.456',
            'url': 'https://example.com/paper'
        }
        
        metadata = prepare_pdf_metadata(fields)
        
        # Check required fields
        assert metadata['title'] == 'Test Paper Title with {braces}'
        assert metadata['author'] == 'Smith, John'  # Only first author
        assert metadata['producer'] == "glen-w's Al-folio Helper"
        
        # Check that abstract is not included (PyPDF2 doesn't support it well)
        assert 'abstract' not in metadata
        
        # Check that DOI is not included (PyPDF2 doesn't support it well)
        assert 'doi' not in metadata
    
    def test_prepare_pdf_metadata_edge_cases(self):
        """Test metadata preparation with edge cases and special characters."""
        # Test with special characters
        fields = {
            'title': 'Title with @#$%^&*() special chars!',
            'author': 'Author with "quotes" and \'apostrophes\'',
            'year': '2023',
            'journal': 'Journal with {braces} and [brackets]'
        }
        
        metadata = prepare_pdf_metadata(fields)
        
        # Special characters should be preserved
        assert '@#$%^&*()' in metadata['title']
        assert '"quotes"' in metadata['author']
        # Note: The function only includes first author, so check what's actually included
        assert 'Author with "quotes"' in metadata['author']
        # Note: clean_nested_braces removes braces, so check the cleaned version
        # The title in this test case doesn't have braces, so just check it's preserved
        assert metadata['title'] == 'Title with @#$%^&*() special chars!'
    
    @pytest.mark.skipif(not PYPDF2_AVAILABLE, reason="PyPDF2 not available")
    def test_pdf_metadata_round_trip(self):
        """Test that metadata can be written to PDF and read back correctly."""
        # Create a simple test PDF
        from PyPDF2 import PdfWriter, PdfReader
        
        # Create a minimal PDF
        writer = PdfWriter()
        page = writer.add_blank_page(width=612, height=792)
        writer.add_metadata({
            'Title': 'Original Title',
            'Author': 'Original Author',
            'Subject': 'Original Subject'
        })
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            temp_pdf = f.name
        
        try:
            with open(temp_pdf, 'wb') as f:
                writer.write(f)
            
            # Prepare new metadata
            fields = {
                'title': 'Updated Test Title',
                'author': 'Updated Test Author',
                'year': '2023',
                'journal': 'Test Journal'
            }
            
            metadata = prepare_pdf_metadata(fields)
            
            # Update the PDF metadata
            success = update_pdf_metadata(temp_pdf, metadata)
            assert success, "PDF metadata update should succeed"
            
            # Read back the PDF and verify metadata
            with open(temp_pdf, 'rb') as f:
                reader = PdfReader(f)
                info = reader.metadata
            
            # Check that metadata was updated
            assert info.get('/Title') == 'Updated Test Title'
            assert info.get('/Author') == 'Updated Test Author'
            assert info.get('/Producer') == "glen-w's Al-folio Helper"
            
            # Check that original metadata was overwritten
            assert info.get('/Subject') != 'Original Subject'
            
        finally:
            # Clean up
            if os.path.exists(temp_pdf):
                os.unlink(temp_pdf)
    
    @pytest.mark.skipif(not PYPDF2_AVAILABLE, reason="PyPDF2 not available")
    def test_pdf_metadata_field_persistence(self):
        """Test that all metadata fields persist correctly."""
        from PyPDF2 import PdfWriter, PdfReader
        
        # Create test PDF
        writer = PdfWriter()
        page = writer.add_blank_page(width=612, height=792)
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            temp_pdf = f.name
        
        try:
            with open(temp_pdf, 'wb') as f:
                writer.write(f)
            
            # Test with comprehensive metadata
            fields = {
                'title': 'Comprehensive Test Title',
                'author': 'Comprehensive Test Author',
                'year': '2023',
                'journal': 'Comprehensive Test Journal',
                'abstract': 'This is a comprehensive test abstract.',
                'keywords': 'comprehensive, test, metadata'
            }
            
            metadata = prepare_pdf_metadata(fields)
            
            # Update PDF metadata
            success = update_pdf_metadata(temp_pdf, metadata)
            assert success
            
            # Read back and verify all fields
            with open(temp_pdf, 'rb') as f:
                reader = PdfReader(f)
                info = reader.metadata
            
            # Verify all expected fields
            assert info.get('/Title') == 'Comprehensive Test Title'
            assert info.get('/Author') == 'Comprehensive Test Author'
            assert info.get('/Producer') == "glen-w's Al-folio Helper"
            
            # Verify field types
            assert isinstance(info.get('/Title'), str)
            assert isinstance(info.get('/Author'), str)
            assert isinstance(info.get('/Producer'), str)
            
        finally:
            if os.path.exists(temp_pdf):
                os.unlink(temp_pdf)
    
    @pytest.mark.skipif(not PYPDF2_AVAILABLE, reason="PyPDF2 not available")
    def test_pdf_metadata_error_handling(self):
        """Test metadata update error handling."""
        from PyPDF2 import PdfWriter, PdfReader
        
        # Test with non-existent file
        non_existent_file = '/non/existent/file.pdf'
        metadata = {'title': 'Test', 'author': 'Test Author'}
        
        success = update_pdf_metadata(non_existent_file, metadata)
        assert not success, "Should fail for non-existent file"
        
        # Test with read-only file (if possible)
        writer = PdfWriter()
        page = writer.add_blank_page(width=612, height=792)
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            temp_pdf = f.name
        
        try:
            with open(temp_pdf, 'wb') as f:
                writer.write(f)
            
            # Make file read-only
            os.chmod(temp_pdf, 0o444)
            
            # Try to update metadata
            success = update_pdf_metadata(temp_pdf, metadata)
            # This might succeed or fail depending on the system, but shouldn't crash
            
        finally:
            # Restore permissions and clean up
            if os.path.exists(temp_pdf):
                os.chmod(temp_pdf, 0o666)
                os.unlink(temp_pdf)
    
    def test_metadata_field_validation(self):
        """Test that metadata fields are properly validated and cleaned."""
        # Test with empty fields
        fields = {
            'title': '',
            'author': '',
            'year': '',
            'journal': ''
        }
        
        metadata = prepare_pdf_metadata(fields)
        
        # Empty fields should NOT be included (function filters them out)
        assert 'title' not in metadata
        assert 'author' not in metadata
        assert metadata['producer'] == "glen-w's Al-folio Helper"
        
        # Test with None fields
        fields = {
            'title': None,
            'author': None,
            'year': None
        }
        
        metadata = prepare_pdf_metadata(fields)
        
        # None fields should NOT be included (function filters them out)
        assert 'title' not in metadata
        assert 'author' not in metadata
        assert metadata['producer'] == "glen-w's Al-folio Helper"
    
    @pytest.mark.skipif(not PYPDF2_AVAILABLE, reason="PyPDF2 not available")
    def test_real_bibtex_metadata_integration(self):
        """Test metadata integration with real BibTeX data."""
        from PyPDF2 import PdfWriter, PdfReader
        
        # Use real BibTeX data
        real_fields = {
            'title': 'Conceptualising and combating transnational environmental crime',
            'author': 'Wright, Glen',
            'year': '2011',
            'journal': 'Trends in Organized Crime',
            'doi': '10.1007/s12117-011-9130-4',
            'abstract': 'To date, transnational environmental crime has been poorly attended to by the transnational organised crime and transnational policing discourse...'
        }
        
        # Create test PDF
        writer = PdfWriter()
        page = writer.add_blank_page(width=612, height=792)
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            temp_pdf = f.name
        
        try:
            with open(temp_pdf, 'wb') as f:
                writer.write(f)
            
            # Prepare and apply metadata
            metadata = prepare_pdf_metadata(real_fields)
            success = update_pdf_metadata(temp_pdf, metadata)
            assert success
            
            # Read back and verify
            with open(temp_pdf, 'rb') as f:
                reader = PdfReader(f)
                info = reader.metadata
            
            # Verify real data was preserved
            assert info.get('/Title') == real_fields['title']
            assert info.get('/Author') == real_fields['author']
            assert info.get('/Producer') == "glen-w's Al-folio Helper"
            
            # Check that long titles are handled correctly
            assert len(info.get('/Title', '')) > 50
            
            # Check that special characters in real data are preserved
            assert 'transnational' in info.get('/Title', '')
            assert 'environmental' in info.get('/Title', '')
            
        finally:
            if os.path.exists(temp_pdf):
                os.unlink(temp_pdf)
    
    def test_metadata_consistency_across_entries(self):
        """Test that metadata is consistent across different BibTeX entry types."""
        # Test different entry types
        test_cases = [
            {
                'title': 'Simple Title',
                'author': 'Simple Author',
                'year': '2023'
            },
            {
                'title': 'Complex Title with {Braces} and Special @#$%^&*() Chars!',
                'author': 'Author with "Quotes" and \'Apostrophes\'',
                'year': '2023',
                'journal': 'Complex Journal'
            },
            {
                'title': 'Very Long Title That Might Exceed Normal Length Limits and Contain Many Words',
                'author': 'Author, First and Author, Second and Author, Third',
                'year': '2023',
                'abstract': 'This is a very long abstract that contains many sentences and should be handled properly by the metadata preparation function.'
            }
        ]
        
        for i, fields in enumerate(test_cases):
            metadata = prepare_pdf_metadata(fields)
            
            # All entries should have producer
            assert metadata['producer'] == "glen-w's Al-folio Helper"
            
            # All entries should have title if provided and non-empty
            if fields.get('title') and fields['title'].strip():
                assert metadata['title'] == fields['title']
            
            # All entries should have author if provided and non-empty
            if fields.get('author') and fields['author'].strip():
                # prepare_pdf_metadata only takes the first author when multiple authors are separated by " and "
                if ' and ' in fields['author']:
                    first_author = fields['author'].split(' and ')[0]
                    assert metadata['author'] == first_author
                else:
                    # clean_nested_braces only removes braces, not quotes, so author should be preserved
                    assert metadata['author'] == fields['author']
            
            # Check that metadata is a dict
            assert isinstance(metadata, dict)
            
            print(f"    ✅ Test case {i+1}: Metadata prepared successfully")


if __name__ == "__main__":
    pytest.main([__file__])
