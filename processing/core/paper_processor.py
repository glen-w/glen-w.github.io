#!/usr/bin/env python3
"""
PaperProcessor class for process_papers.py
Main processor that coordinates all paper processing operations.
"""

import os
import re
import shutil
import time
import sys
from typing import Dict, List, Optional

# Add the processing directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Configuration
from core.bibtex_processor import BibTeXProcessor
from utils.file_manager import FileManager
from core.pdf_processor import PDFProcessor
from core.text_processor import TextProcessor
from utils.metadata_fetcher import MetadataFetcher
from core.bibtex_formatter import BibTeXFormatter


class PaperProcessor:
    """Main processor that coordinates all paper processing operations."""
    
    def __init__(self, config: Configuration = None):
        """Initialize with configuration and all required processors."""
        self.config = config or Configuration()
        self.text_processor = TextProcessor(self.config)
        self.file_manager = FileManager(self.config)
        self.pdf_processor = PDFProcessor(self.config, self.text_processor)
        self.bibtex_processor = BibTeXProcessor(self.config, self.text_processor)
        self.metadata_fetcher = MetadataFetcher(self.config)
        self.formatter = BibTeXFormatter()
    
    def check_dependencies(self) -> bool:
        """Check if all required dependencies are available."""
        try:
            # Check for required Python packages
            import PyPDF2
            import bibtexparser
            import requests
            import PIL
            return True
        except ImportError as e:
            print(f"❌ Missing dependency: {e}")
            return False
    
    def process_papers(self, source_bibtex_file: str = None, regenerate: bool = False, 
                      force: bool = False, update_metadata: bool = True, 
                      thumbnail_size: str = '600x', test_mode: bool = False, 
                      test_count: int = 5, verbose: bool = False, 
                      force_refetch_metadata: bool = False, rename_urls: bool = True,
                      rename_only: bool = False) -> None:
        """Main function to process papers from Zotero export."""
        source_file = source_bibtex_file or self.config.SOURCE_BIBTEX_FILE
        working_file = self.config.WORKING_BIBTEX_FILE
        
        print(f"📚 Processing {source_file}...")
        
        # Create backup of the original BibTeX file
        self._create_backup(source_file)
        
        # Clean up existing files if regenerate mode
        if regenerate:
            self._cleanup_existing_files()
        
        # Copy source to working file
        if not self._copy_source_to_working(source_file, working_file):
            return
        
        # Read and parse the BibTeX file
        content = self._read_bibtex_file(working_file)
        if not content:
            return
        
        # First clean malformed entries and remove curly braces from text fields
        content = self.bibtex_processor.clean_malformed_entries(content)
        
        # Process Zotero notes to extract information into BibTeX fields
        content = self.bibtex_processor.process_notes_from_zotero(content)
        
        # Write the updated content back to the working file
        with open(working_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Process entries
        self._process_entries(content, working_file, regenerate, force, update_metadata, 
                            thumbnail_size, test_mode, test_count, verbose, 
                            force_refetch_metadata, rename_urls, rename_only)
        
        print(f"\n✅ Processing completed successfully!")
    
    def _create_backup(self, source_file: str) -> None:
        """Create backup of the source BibTeX file."""
        backup_file = source_file.replace('.bib', f'_backup_{int(time.time())}.bib')
        try:
            shutil.copy2(source_file, backup_file)
            print(f"  💾 Created backup: {backup_file}")
        except Exception as e:
            print(f"  ⚠️  Warning: Could not create backup: {e}")
    
    def _cleanup_existing_files(self) -> None:
        """Clean up existing files if regenerate mode is enabled."""
        print("  🧹 Cleaning up existing files...")
        
        # Clean up PDFs
        if os.path.exists(self.config.PDF_DIR):
            for file in os.listdir(self.config.PDF_DIR):
                if file.endswith('.pdf'):
                    os.remove(os.path.join(self.config.PDF_DIR, file))
            print(f"  🗑️  Cleaned up PDFs in {self.config.PDF_DIR}")
        
        # Clean up preview thumbnails
        if os.path.exists(self.config.PREVIEW_DIR):
            for file in os.listdir(self.config.PREVIEW_DIR):
                if file.endswith(('.jpeg', '.jpg')):
                    os.remove(os.path.join(self.config.PREVIEW_DIR, file))
            print(f"  🗑️  Cleaned up thumbnails in {self.config.PREVIEW_DIR}")
    
    def _copy_source_to_working(self, source_file: str, working_file: str) -> bool:
        """Copy source BibTeX file to working file."""
        try:
            shutil.copy2(source_file, working_file)
            print(f"  ✅ Copied {source_file} to {working_file}")
            return True
        except Exception as e:
            print(f"  ❌ Error copying {source_file} to {working_file}: {e}")
            return False
    
    def _read_bibtex_file(self, file_path: str) -> Optional[str]:
        """Read and validate BibTeX file content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"  ✅ Read {file_path}")
            return content
        except Exception as e:
            print(f"  ❌ Error reading {file_path}: {e}")
            return None
    
    def _process_entries(self, content: str, working_file: str, regenerate: bool, 
                        force: bool, update_metadata: bool, thumbnail_size: str, 
                        test_mode: bool, test_count: int, verbose: bool, 
                        force_refetch_metadata: bool, rename_urls: bool, 
                        rename_only: bool) -> None:
        """Process all BibTeX entries."""
        # Parse entries
        entries = self.bibtex_processor.parse_bibtex_entries(content)
        
        if test_mode:
            entries = entries[:test_count]
            print(f"  🧪 Test mode: Processing only {len(entries)} entries")
        
        processed_count = 0
        for entry in entries:
            if self._process_single_entry(entry, regenerate, force, update_metadata, 
                                        thumbnail_size, verbose, force_refetch_metadata, 
                                        rename_urls, rename_only):
                processed_count += 1
        
        print(f"  📊 Processed {processed_count} entries")
        
        # Write updated content back to file using the modified entries
        self._write_updated_bibtex_from_entries(entries, working_file, rename_urls)
    
    def _process_single_entry(self, entry: Dict, regenerate: bool, force: bool, 
                            update_metadata: bool, thumbnail_size: str, verbose: bool, 
                            force_refetch_metadata: bool, rename_urls: bool, 
                            rename_only: bool) -> bool:
        """Process a single BibTeX entry."""
        citation_key = entry.get('citation_key', '')
        fields = entry.get('fields', {})
        
        if not citation_key or not fields:
            return False
        
        print(f"\n📄 Processing: {citation_key}")
        
        # Skip if already processed (unless force mode)
        if not force and self._is_entry_processed(fields):
            print(f"  ⏭️  Already processed, skipping")
            return True
        
        # Process files and generate thumbnails
        if not self._process_entry_files(citation_key, fields, regenerate, force, 
                                       thumbnail_size, verbose):
            return False
        
        # Update metadata if requested
        if update_metadata and not rename_only:
            self._update_entry_metadata(citation_key, fields, force_refetch_metadata, verbose)
        
        return True
    
    def _is_entry_processed(self, fields: Dict) -> bool:
        """Check if entry already has required tags."""
        # Check if basic processing is complete
        has_basic_processing = 'preview' in fields and ('pdf' in fields or 'slides' in fields)
        
        # If basic processing is complete, check if image processing is also complete
        if has_basic_processing:
            # Check if there are still images in the file field that need processing
            file_field = fields.get('file', '')
            has_unprocessed_images = any(f':image/{ext}' in file_field for ext in ['jpeg', 'jpg', 'png', 'gif'])
            
            # If there are unprocessed images, we need to reprocess
            if has_unprocessed_images:
                return False
            
            # Check if images were processed but file field wasn't updated
            # Images are now handled through the file field with descriptive filenames
            # No need to check for separate photos/figures fields
        
        return has_basic_processing
    
    def _process_entry_files(self, citation_key: str, fields: Dict, regenerate: bool, 
                           force: bool, thumbnail_size: str, verbose: bool) -> bool:
        """Process files for an entry (PDFs, images, thumbnails)."""
        if 'file' not in fields or not fields['file']:
            print(f"  ⚠️  No file field found")
            return True
        
        # Extract file paths
        pdf_paths = self.bibtex_processor.extract_pdf_files(fields['file'])
        image_paths = self.bibtex_processor.extract_image_files(fields['file'])
        
        # Process PDFs
        pdf_success = self._process_pdfs(citation_key, fields, pdf_paths, regenerate, force, verbose)
        
        # Process images
        image_success = self._process_images(citation_key, fields, image_paths, regenerate, force, verbose)
        
        # Clean file field to remove image entries if images were processed
        if image_success and image_paths and ('photos' in fields or 'figures' in fields):
            fields['file'] = self._clean_file_field_from_images(fields['file'])
        
        # Process thumbnails with priority logic
        thumbnail_success = self._process_thumbnails_with_priority(citation_key, fields, 
                                                                  regenerate, force, thumbnail_size, verbose)
        
        # Clean file field to remove all processed files (PDFs, images, thumbnails)
        # Only keep the file field if there are unprocessed files
        if pdf_success or image_success or thumbnail_success:
            fields['file'] = self._clean_file_field_after_processing(fields['file'], fields)
        
        return pdf_success and image_success and thumbnail_success
    
    def _clean_file_field_after_processing(self, file_field: str, fields: Dict) -> str:
        """Replace processed files in the file field with their new descriptive filenames."""
        if not file_field:
            return file_field
        
        # Get lists of processed files with their types
        processed_pdfs = []
        if 'pdf' in fields and fields['pdf']:
            processed_pdfs.append(fields['pdf'])
        if 'slides' in fields and fields['slides']:
            processed_pdfs.append(fields['slides'])
        
        processed_images = []
        if 'photos' in fields and fields['photos']:
            processed_images.extend(fields['photos'].split(', '))
        if 'figures' in fields and fields['figures']:
            processed_images.extend(fields['figures'].split(', '))
        
        # Get processed thumbnails (preview fields)
        processed_thumbnails = []
        if 'preview' in fields and fields['preview']:
            processed_thumbnails.append(fields['preview'])
        
        # If we have processed files, replace the entire file field with processed versions
        if processed_pdfs or processed_images or processed_thumbnails:
            updated_parts = []
            
            # Add processed PDFs
            for pdf in processed_pdfs:
                updated_parts.append(f"PDF:/assets/pdf/{pdf}:application/pdf")
            
            # Add processed images
            for image in processed_images:
                if 'photo' in image:
                    updated_parts.append(f"photo:/assets/img/publications/{image}:image/jpeg")
                elif 'figure' in image:
                    updated_parts.append(f"figure:/assets/img/publications/{image}:image/jpeg")
                else:
                    updated_parts.append(f"image:/assets/img/publications/{image}:image/jpeg")
            
            # Add processed thumbnails
            for thumbnail in processed_thumbnails:
                updated_parts.append(f"thumbnail:/assets/img/publication_preview/{thumbnail}:image/jpeg")
            
            return '; '.join(updated_parts)
        
        # If no processed files, return original field
        return file_field
    
    def _clean_file_field_from_images(self, file_field: str) -> str:
        """Remove image entries from the file field, keeping only PDFs, thumbnails, and other non-image files."""
        if not file_field:
            return file_field
        
        # Split by semicolon and filter out image entries (but keep thumbnails)
        file_parts = file_field.split(';')
        non_image_parts = []
        
        for part in file_parts:
            part = part.strip()
            if part:
                # Check if this is a thumbnail file (description contains 'thumbnail' or filename contains 'thumbnail')
                is_thumbnail = False
                if ':' in part:
                    # Format: description:path:mime
                    parts = part.split(':')
                    if len(parts) >= 2:
                        description = parts[0].strip().lower()
                        if 'thumbnail' in description:
                            is_thumbnail = True
                else:
                    # Format: path or filename
                    if 'thumbnail' in part.lower():
                        is_thumbnail = True
                
                # Keep the part if it's not an image OR if it's a thumbnail
                if not any(f':image/{ext}' in part for ext in ['jpeg', 'jpg', 'png', 'gif']) or is_thumbnail:
                    non_image_parts.append(part)
        
        # Reconstruct the file field
        if non_image_parts:
            return '; '.join(non_image_parts)
        else:
            return ''
    
    def _process_pdfs(self, citation_key: str, fields: Dict, pdf_paths: List[str], 
                     regenerate: bool, force: bool, verbose: bool) -> bool:
        """Process PDF files for an entry."""
        if not pdf_paths:
            return True
        
        success = True
        for pdf_path in pdf_paths:
            if not self._process_single_pdf(citation_key, fields, pdf_path, regenerate, force, verbose):
                success = False
        
        return success
    
    def _process_single_pdf(self, citation_key: str, fields: Dict, pdf_path: str, 
                          regenerate: bool, force: bool, verbose: bool) -> bool:
        """Process a single PDF file."""
        if not os.path.exists(pdf_path):
            print(f"  ❌ PDF not found: {pdf_path}")
            return False
        
        # Generate filename
        filename = self.text_processor.generate_filename(citation_key, fields, 'pdf')
        if not filename:
            print(f"  ❌ Could not generate filename for PDF")
            return False
        
        # Copy PDF
        dest_path = os.path.join(self.config.PDF_DIR, filename)
        if not os.path.exists(dest_path) or force:
            if not self.file_manager.copy_file(pdf_path, dest_path, force):
                return False
        
        # Generate thumbnail
        preview_filename = filename.replace('.pdf', '.jpeg')
        preview_path = os.path.join(self.config.PREVIEW_DIR, preview_filename)
        
        if not os.path.exists(preview_path) or force:
            if not self.file_manager.generate_pdf_thumbnail(dest_path, preview_path):
                return False
        
        # Add tags to fields
        fields['pdf'] = filename
        fields['preview'] = preview_filename
        
        return True
    
    def _process_images(self, citation_key: str, fields: Dict, image_paths: List[str], 
                      regenerate: bool, force: bool, verbose: bool) -> bool:
        """Process image files for an entry."""
        if not image_paths:
            return True
        
        # Use the existing image processing logic
        processed_images = self.file_manager.process_images_for_entry(
            citation_key, fields, self.config.IMAGES_DIR, force
        )
        
        # Store processed images in fields for file field replacement logic
        for image_type, files in processed_images.items():
            if files:
                # Convert singular to plural for BibTeX fields
                field_name = f"{image_type}s" if image_type in ['photo', 'figure'] else image_type
                fields[field_name] = ', '.join(files)
        
        return True
    
    def _process_thumbnails_with_priority(self, citation_key: str, fields: Dict, 
                                        regenerate: bool, force: bool, thumbnail_size: str, verbose: bool) -> bool:
        """Process thumbnails using priority logic: thumbnail file > agenda PDF > most recent PDF."""
        if 'file' not in fields or not fields['file']:
            return True
        
        # Get files in priority order
        priority_files = self.bibtex_processor.get_thumbnail_priority_files(fields['file'])
        
        if not priority_files:
            print(f"  ⚠️  No suitable files found for thumbnail generation")
            return True
        
        # Try each file in priority order until one succeeds
        for file_info in priority_files:
            file_path = file_info['path']
            file_type = file_info['type']
            priority = file_info['priority']
            
            if verbose:
                priority_names = {1: "thumbnail file", 2: "agenda PDF", 3: "most recent PDF"}
                print(f"  🔍 Trying {priority_names[priority]}: {os.path.basename(file_path)}")
            
            if self._process_single_thumbnail_file(citation_key, fields, file_path, file_type, 
                                                regenerate, force, thumbnail_size, verbose):
                return True
            else:
                if verbose:
                    print(f"  ❌ Failed to generate thumbnail from {priority_names[priority]}")
        
        print(f"  ❌ All thumbnail generation attempts failed")
        return False
    
    def _process_single_thumbnail_file(self, citation_key: str, fields: Dict, file_path: str, 
                                     file_type: str, regenerate: bool, force: bool, 
                                     thumbnail_size: str, verbose: bool) -> bool:
        """Process a single thumbnail file based on its type."""
        if not os.path.exists(file_path):
            if verbose:
                print(f"  ❌ File not found: {file_path}")
            return False
        
        # Generate filename for thumbnail
        filename = self.text_processor.generate_filename(citation_key, fields, 'jpeg')
        if not filename:
            if verbose:
                print(f"  ❌ Could not generate filename for thumbnail")
            return False
        
        preview_path = os.path.join(self.config.PREVIEW_DIR, filename)
        
        # Skip if already exists and not forcing
        if os.path.exists(preview_path) and not force:
            if verbose:
                print(f"  ⏭️  Thumbnail already exists: {filename}")
            # Only add the preview tag if there's something to preview
            if 'preview' not in fields and self._should_add_preview_field(fields):
                fields['preview'] = filename
            return True
        
        # Generate thumbnail based on file type
        success = False
        if file_type == 'svg':
            success = self.file_manager.generate_svg_thumbnail(file_path, preview_path, thumbnail_size)
        elif file_type == 'image':
            success = self._copy_image_as_thumbnail(file_path, preview_path)
        elif file_type == 'pdf':
            success = self.file_manager.generate_pdf_thumbnail(file_path, preview_path, thumbnail_size)
        
        if success:
            # Add preview tag to fields (only if not already set and there's something to preview)
            if 'preview' not in fields and self._should_add_preview_field(fields):
                fields['preview'] = filename
            return True
        
        return False
    
    def _should_add_preview_field(self, fields: Dict) -> bool:
        """Check if a preview field should be added based on available content."""
        # Always add preview field if we have successfully processed a thumbnail
        # The preview field represents the thumbnail/preview image regardless of source
        return True
    
    def _clean_file_field_in_content(self, content: str, fields: Dict) -> str:
        """Clean the file field in the content to remove processed files."""
        # Find the file field in the content
        file_field_pattern = r'file\s*=\s*\{([^}]+)\}'
        match = re.search(file_field_pattern, content)
        if not match:
            return content
        
        file_field = match.group(1)
        cleaned_file_field = self._clean_file_field_after_processing(file_field, fields)
        
        # Replace the file field in the content
        if cleaned_file_field:
            new_file_field = f"file = {{{cleaned_file_field}}}"
        else:
            new_file_field = ""  # Remove the file field entirely if empty
        
        return content.replace(match.group(0), new_file_field)
    
    def _copy_image_as_thumbnail(self, source_path: str, dest_path: str) -> bool:
        """Copy an image file to the thumbnail directory."""
        try:
            import shutil
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(source_path, dest_path)
            print(f"  ✅ Copied image thumbnail: {os.path.basename(dest_path)}")
            return True
        except Exception as e:
            print(f"  ❌ Error copying image thumbnail: {e}")
            return False
    
    def _update_entry_metadata(self, citation_key: str, fields: Dict, 
                             force_refetch_metadata: bool, verbose: bool) -> None:
        """Update entry metadata using external APIs."""
        # This would integrate with the metadata fetcher
        # For now, just a placeholder
        pass
    
    def _write_updated_bibtex(self, content: str, working_file: str) -> None:
        """Write updated BibTeX content back to file."""
        try:
            # Parse all entries to get updated content
            entries = self.bibtex_processor.parse_bibtex_entries(content)
            
            # Rebuild the content with updated entries
            updated_content = []
            for entry in entries:
                citation_key = entry['citation_key']
                fields = entry['fields']
                entry_content = entry['content']
                
                # Update the entry content with new fields
                updated_entry = self._update_entry_content(entry_content, fields)
                updated_content.append(updated_entry)
            
            # Join all entries
            final_content = '\n\n'.join(updated_content)
            
            with open(working_file, 'w', encoding='utf-8') as f:
                f.write(final_content)
            print(f"  ✅ Updated {working_file}")
        except Exception as e:
            print(f"  ❌ Error writing {working_file}: {e}")
    
    def _write_updated_bibtex_from_entries(self, entries: List[Dict], working_file: str, rename_urls: bool = True) -> None:
        """Write updated BibTeX content back to file using modified entries."""
        try:
            # Rebuild the content with updated entries
            updated_content = []
            for entry in entries:
                citation_key = entry['citation_key']
                fields = entry['fields']
                entry_content = entry['content']
                
                # Update the entry content with new fields
                updated_entry = self._update_entry_content(entry_content, fields)
                updated_content.append(updated_entry)
            
            # Join all entries
            final_content = '\n\n'.join(updated_content)
            
            # Rename URL fields if requested
            if rename_urls:
                final_content, url_count = self.bibtex_processor.rename_url_fields(final_content)
                if url_count > 0:
                    print(f"  🔄 Renamed {url_count} URL fields to website fields")
            
            # Apply BibTeX formatting to clean up internal braces and formatting
            try:
                # Parse entries and format them properly
                formatted_entries = []
                for entry_content in final_content.split('\n\n'):
                    if entry_content.strip():
                        formatted_entry = self.formatter.format_entry_from_content(entry_content)
                        formatted_entries.append(formatted_entry)
                
                # Join formatted entries
                final_content = '\n\n'.join(formatted_entries)
            except Exception as e:
                print(f"  ⚠️  Warning: Could not apply formatting: {e}")
            
            with open(working_file, 'w', encoding='utf-8') as f:
                f.write(final_content)
            print(f"  ✅ Updated {working_file}")
        except Exception as e:
            print(f"  ❌ Error writing {working_file}: {e}")
    
    def _update_entry_content(self, entry_content: str, fields: Dict) -> str:
        """Update an entry's content with new fields."""
        # Find the end of the entry (before the closing brace)
        last_brace = entry_content.rfind('}')
        if last_brace == -1:
            # No closing brace found, return original content unchanged
            return entry_content
        
        # Extract the part before the closing brace
        before_brace = entry_content[:last_brace]
        after_brace = entry_content[last_brace:]
        
        # Update the file field to replace processed files with descriptive filenames
        if 'preview' in fields or 'pdf' in fields or 'photos' in fields or 'figures' in fields:
            before_brace = self._clean_file_field_in_content(before_brace, fields)
        
        # Add new fields that don't already exist and have valid values
        new_fields = []
        for field_name, field_value in fields.items():
            if field_name in ['preview', 'pdf', 'slides']:
                # Skip empty or None values
                if not field_value or field_value.strip() == '':
                    continue
                
                # Preview field should always be added if it exists
                # It represents the thumbnail/preview image regardless of source
                
                # Check if field already exists in the content
                if f"{field_name} =" not in before_brace:
                    # Handle field values that already contain curly braces
                    if field_value.startswith('{') and field_value.endswith('}'):
                        # Field value already has braces, use as-is
                        new_fields.append(f"\t{field_name} = {field_value}")
                    else:
                        # Field value needs braces, add them
                        new_fields.append(f"\t{field_name} = {{{field_value}}}")
        
        # Combine everything
        if new_fields:
            # Clean up trailing commas and whitespace from before_brace
            before_brace = before_brace.rstrip()
            if before_brace.endswith(','):
                # Remove trailing comma
                before_brace = before_brace[:-1].rstrip()
            
            # Add new fields with proper comma handling
            updated_content = before_brace + ',\n' + ',\n'.join(new_fields) + '\n' + after_brace
        else:
            # Clean up trailing commas and whitespace from before_brace
            before_brace = before_brace.rstrip()
            if before_brace.endswith(','):
                # Remove trailing comma
                before_brace = before_brace[:-1].rstrip()
            updated_content = before_brace + after_brace
        
        return updated_content
