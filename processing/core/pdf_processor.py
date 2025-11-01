#!/usr/bin/env python3
"""
PDFProcessor class for process_papers.py
Handles all PDF-related operations including metadata updates and thumbnail generation.
"""

import os
import sys
from typing import Dict, Optional

# Add the processing directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Configuration
from core.text_processor import TextProcessor


class PDFProcessor:
    """Handles all PDF processing operations."""
    
    def __init__(self, config: Configuration = None, text_processor: TextProcessor = None):
        """Initialize with configuration and text processor."""
        self.config = config or Configuration()
        self.text_processor = text_processor or TextProcessor(config)
    
    def update_pdf_metadata(self, pdf_path: str, metadata: Dict[str, str]) -> bool:
        """Update PDF metadata using PyPDF2."""
        try:
            import PyPDF2
            
            # Read the PDF
            reader = PyPDF2.PdfReader(pdf_path)
            writer = PyPDF2.PdfWriter()
            
            # Copy all pages
            for page in reader.pages:
                writer.add_page(page)
            
            # Update metadata
            pdf_metadata = {}
            if metadata.get('title'):
                pdf_metadata['/Title'] = metadata['title']
            if metadata.get('author'):
                pdf_metadata['/Author'] = metadata['author']
            if metadata.get('subject'):
                pdf_metadata['/Subject'] = metadata['subject']
            if metadata.get('keywords'):
                pdf_metadata['/Keywords'] = metadata['keywords']
            if metadata.get('creator'):
                pdf_metadata['/Creator'] = metadata['creator']
            if metadata.get('producer'):
                pdf_metadata['/Producer'] = metadata['producer']
            if metadata.get('description'):
                pdf_metadata['/Description'] = metadata['description']
            
            # Add metadata to writer
            for key, value in pdf_metadata.items():
                writer.add_metadata({key: value})
            
            # Write the updated PDF
            with open(pdf_path, 'wb') as output_file:
                writer.write(output_file)
            
            print(f"  ✅ Updated PDF metadata: {os.path.basename(pdf_path)}")
            return True
            
        except Exception as e:
            print(f"  ❌ PDF metadata update failed: {e}")
            return False
    
    def prepare_pdf_metadata(self, fields: Dict[str, str]) -> Dict[str, str]:
        """Prepare PDF metadata from BibTeX fields."""
        metadata = {}
        
        # Title - clean braces from title
        if fields.get('title'):
            metadata['title'] = self.text_processor.clean_title_for_bibtex(fields['title'])
        
        # Author - first author's full name
        if fields.get('author'):
            author_field = fields['author']
            authors = [author.strip() for author in author_field.split(' and ')]
            if authors:
                first_author = authors[0]
                metadata['author'] = first_author
        
        # Subject - from keywords field
        if fields.get('keywords'):
            metadata['subject'] = fields['keywords']
        else:
            metadata['subject'] = ""
        
        # Creator - first author
        if fields.get('author'):
            author_field = fields['author']
            authors = [author.strip() for author in author_field.split(' and ')]
            if authors:
                first_author = authors[0]
                metadata['creator'] = first_author
        
        # Producer - tool used
        metadata['producer'] = self.config.PDF_PRODUCER
        
        # Description - abstract if available
        if fields.get('abstract'):
            abstract = fields['abstract']
            metadata['description'] = self.text_processor.truncate_abstract(abstract)
        
        return metadata
    
    def check_pdf_dependencies(self) -> bool:
        """Check if required PDF dependencies are available."""
        try:
            import PyPDF2
            return True
        except ImportError:
            print("  ❌ PyPDF2 not found - install with: pip install PyPDF2")
            return False
    
    def get_pdf_info(self, pdf_path: str) -> Optional[Dict[str, str]]:
        """Get basic information about a PDF file."""
        try:
            import PyPDF2
            
            reader = PyPDF2.PdfReader(pdf_path)
            info = reader.metadata
            
            if info:
                return {
                    'title': info.get('/Title', ''),
                    'author': info.get('/Author', ''),
                    'subject': info.get('/Subject', ''),
                    'keywords': info.get('/Keywords', ''),
                    'creator': info.get('/Creator', ''),
                    'producer': info.get('/Producer', ''),
                    'description': info.get('/Description', '')
                }
            else:
                return {}
                
        except Exception as e:
            print(f"  ⚠️  Could not read PDF info: {e}")
            return None
    
    def validate_pdf(self, pdf_path: str) -> bool:
        """Validate that a PDF file is readable and not corrupted."""
        try:
            import PyPDF2
            
            reader = PyPDF2.PdfReader(pdf_path)
            
            # Check if PDF has pages
            if len(reader.pages) == 0:
                print(f"  ⚠️  PDF has no pages: {os.path.basename(pdf_path)}")
                return False
            
            # Try to access the first page
            first_page = reader.pages[0]
            if first_page is None:
                print(f"  ⚠️  Could not access first page: {os.path.basename(pdf_path)}")
                return False
            
            return True
            
        except Exception as e:
            print(f"  ❌ PDF validation failed: {e}")
            return False
    
    def get_pdf_page_count(self, pdf_path: str) -> int:
        """Get the number of pages in a PDF."""
        try:
            import PyPDF2
            
            reader = PyPDF2.PdfReader(pdf_path)
            return len(reader.pages)
            
        except Exception as e:
            print(f"  ⚠️  Could not get page count: {e}")
            return 0
    
    def extract_text_from_page(self, pdf_path: str, page_number: int = 0) -> str:
        """Extract text from a specific page of a PDF."""
        try:
            import PyPDF2
            
            reader = PyPDF2.PdfReader(pdf_path)
            
            if page_number >= len(reader.pages):
                return ""
            
            page = reader.pages[page_number]
            return page.extract_text()
            
        except Exception as e:
            print(f"  ⚠️  Could not extract text from page {page_number}: {e}")
            return ""
    
    def is_pdf_file(self, file_path: str) -> bool:
        """Check if a file is a valid PDF."""
        if not os.path.exists(file_path):
            return False
        
        if not file_path.lower().endswith('.pdf'):
            return False
        
        return self.validate_pdf(file_path)
    
    def get_pdf_size(self, pdf_path: str) -> int:
        """Get the size of a PDF file in bytes."""
        try:
            return os.path.getsize(pdf_path)
        except OSError:
            return 0
    
    def create_pdf_summary(self, pdf_path: str) -> Dict[str, str]:
        """Create a summary of PDF information."""
        summary = {
            'file_path': pdf_path,
            'file_name': os.path.basename(pdf_path),
            'file_size': str(self.get_pdf_size(pdf_path)),
            'page_count': str(self.get_pdf_page_count(pdf_path)),
            'is_valid': str(self.validate_pdf(pdf_path))
        }
        
        # Add metadata if available
        metadata = self.get_pdf_info(pdf_path)
        if metadata:
            summary.update(metadata)
        
        return summary
