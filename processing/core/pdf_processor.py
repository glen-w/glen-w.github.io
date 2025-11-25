#!/usr/bin/env python3
"""
PDFProcessor class for process_papers.py
Handles all PDF-related operations including metadata updates and thumbnail generation.
"""

import os
import sys
import shutil
import tempfile
import time
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
    
    def backup_pdf(self, pdf_path: str) -> Optional[str]:
        """Create a backup of a PDF file before modification."""
        try:
            # Ensure backup directory exists
            self.config.ensure_pdf_metadata_backup_dir_exists()
            
            # Generate backup filename with timestamp
            base_name = os.path.basename(pdf_path)
            name, ext = os.path.splitext(base_name)
            timestamp = int(time.time())
            backup_filename = f"{name}_backup_{timestamp}{ext}"
            backup_path = os.path.join(self.config.PDF_METADATA_BACKUP_DIR, backup_filename)
            
            # Only backup if file doesn't already exist (avoid duplicates)
            if not os.path.exists(backup_path):
                shutil.copy2(pdf_path, backup_path)
                print(f"  💾 Created PDF backup: {backup_filename}")
                return backup_path
            else:
                # Return existing backup path
                return backup_path
                
        except Exception as e:
            print(f"  ⚠️  Warning: Could not create PDF backup: {e}")
            return None
    
    def _atomic_write_pdf(self, pdf_path: str, writer) -> bool:
        """Write PDF using atomic operation (temp file + rename)."""
        try:
            # Create temp file in same directory
            temp_dir = os.path.dirname(pdf_path)
            temp_fd, temp_path = tempfile.mkstemp(suffix='.pdf', dir=temp_dir)
            
            try:
                # Write to temp file
                with os.fdopen(temp_fd, 'wb') as temp_file:
                    writer.write(temp_file)
                
                # Verify temp file is valid
                if not self.validate_pdf(temp_path):
                    os.remove(temp_path)
                    return False
                
                # Atomic rename
                os.replace(temp_path, pdf_path)
                return True
                
            except Exception as e:
                # Clean up temp file on error
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except:
                        pass
                raise e
                
        except Exception as e:
            print(f"  ❌ Atomic write failed: {e}")
            return False
    
    def _check_file_writable(self, pdf_path: str) -> bool:
        """Check if PDF file is writable."""
        if not os.path.exists(pdf_path):
            return False
        
        # Check if we can write to the file
        if not os.access(pdf_path, os.W_OK):
            print(f"  ⚠️  PDF file is not writable: {os.path.basename(pdf_path)}")
            return False
        
        return True
    
    def _validate_metadata_values(self, metadata: Dict[str, str]) -> Dict[str, str]:
        """Validate and sanitize metadata values for PDF format."""
        validated = {}
        
        # PDF metadata has some limitations - ensure values are strings and reasonable length
        for key, value in metadata.items():
            if value is None:
                continue
            
            # Convert to string
            str_value = str(value)
            
            # Truncate if too long (PDF metadata fields have practical limits)
            # Title, Author, Subject, Keywords typically limited to ~255 characters
            max_length = 255
            if len(str_value) > max_length:
                str_value = str_value[:max_length-3] + "..."
            
            # Remove null bytes and other problematic characters
            str_value = str_value.replace('\x00', '')
            
            validated[key] = str_value
        
        return validated
    
    def update_pdf_metadata(self, pdf_path: str, metadata: Dict[str, str], backup: bool = False) -> bool:
        """Update PDF metadata using PyPDF2 with enhanced error handling and atomic writes."""
        # Check dependency first
        if not self.check_pdf_dependencies():
            return False
        
        # Validate PDF is readable
        if not self.validate_pdf(pdf_path):
            print(f"  ⚠️  PDF validation failed, skipping metadata update: {os.path.basename(pdf_path)}")
            return False
        
        # Check file is writable
        if not self._check_file_writable(pdf_path):
            return False
        
        # Create backup before modification
        backup_path = None
        if backup:
            backup_path = self.backup_pdf(pdf_path)
            if backup_path is None:
                print(f"  ⚠️  Warning: Proceeding without backup for {os.path.basename(pdf_path)}")
        
        try:
            import PyPDF2
            # Try to import specific errors, fallback to generic Exception if not available
            try:
                from PyPDF2.errors import PdfReadError, PdfWriteError
            except ImportError:
                # Older versions of PyPDF2 don't have errors module
                PdfReadError = Exception
                PdfWriteError = Exception
            
            # Read the PDF
            try:
                reader = PyPDF2.PdfReader(pdf_path)
            except PdfReadError as e:
                print(f"  ❌ PDF read error: {e}")
                return False
            except Exception as e:
                print(f"  ❌ Error reading PDF: {e}")
                return False
            
            writer = PyPDF2.PdfWriter()
            
            # Copy all pages
            try:
                for page in reader.pages:
                    writer.add_page(page)
            except Exception as e:
                print(f"  ❌ Error copying PDF pages: {e}")
                return False
            
            # Validate and prepare metadata
            validated_metadata = self._validate_metadata_values(metadata)
            
            # Update metadata
            pdf_metadata = {}
            if validated_metadata.get('title'):
                pdf_metadata['/Title'] = validated_metadata['title']
            if validated_metadata.get('author'):
                pdf_metadata['/Author'] = validated_metadata['author']
            if validated_metadata.get('subject'):
                pdf_metadata['/Subject'] = validated_metadata['subject']
            if validated_metadata.get('keywords'):
                pdf_metadata['/Keywords'] = validated_metadata['keywords']
            if validated_metadata.get('creator'):
                pdf_metadata['/Creator'] = validated_metadata['creator']
            if validated_metadata.get('producer'):
                pdf_metadata['/Producer'] = validated_metadata['producer']
            if validated_metadata.get('description'):
                pdf_metadata['/Description'] = validated_metadata['description']
            
            # Add metadata to writer
            try:
                for key, value in pdf_metadata.items():
                    writer.add_metadata({key: value})
            except Exception as e:
                print(f"  ❌ Error adding metadata: {e}")
                return False
            
            # Atomic write
            if not self._atomic_write_pdf(pdf_path, writer):
                # Restore from backup if write failed
                if backup_path and os.path.exists(backup_path):
                    try:
                        shutil.copy2(backup_path, pdf_path)
                        print(f"  🔄 Restored PDF from backup after failed write")
                    except:
                        pass
                return False
            
            # Verify the written PDF is still valid
            if not self.validate_pdf(pdf_path):
                # Restore from backup if validation failed
                if backup_path and os.path.exists(backup_path):
                    try:
                        shutil.copy2(backup_path, pdf_path)
                        print(f"  🔄 Restored PDF from backup after validation failure")
                    except:
                        pass
                return False
            
            print(f"  ✅ Updated PDF metadata: {os.path.basename(pdf_path)}")
            return True
            
        except ImportError:
            print("  ❌ PyPDF2 not found - install with: pip install PyPDF2")
            return False
        except Exception as e:
            print(f"  ❌ PDF metadata update failed: {e}")
            # Restore from backup if available
            if backup_path and os.path.exists(backup_path):
                try:
                    shutil.copy2(backup_path, pdf_path)
                    print(f"  🔄 Restored PDF from backup after error")
                except:
                    pass
            return False
    
    def prepare_pdf_metadata(self, fields: Dict[str, str]) -> Dict[str, str]:
        """Prepare PDF metadata from BibTeX fields with validation."""
        metadata = {}
        
        # Title - clean braces from title
        if fields.get('title'):
            title = self.text_processor.clean_title_for_bibtex(fields['title'])
            if title:
                metadata['title'] = title
        
        # Author - first author's full name
        if fields.get('author'):
            author_field = fields['author']
            authors = [author.strip() for author in author_field.split(' and ')]
            if authors:
                first_author = authors[0]
                if first_author:
                    metadata['author'] = first_author
        
        # Subject - from keywords field or journal
        if fields.get('keywords'):
            metadata['subject'] = fields['keywords']
        elif fields.get('journal'):
            metadata['subject'] = fields['journal']
        elif fields.get('publisher'):
            metadata['subject'] = fields['publisher']
        elif fields.get('institution'):
            metadata['subject'] = fields['institution']
        else:
            metadata['subject'] = ""
        
        # Keywords - from keywords field if available
        if fields.get('keywords'):
            metadata['keywords'] = fields['keywords']
        
        # Creator - first author
        if fields.get('author'):
            author_field = fields['author']
            authors = [author.strip() for author in author_field.split(' and ')]
            if authors:
                first_author = authors[0]
                if first_author:
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
