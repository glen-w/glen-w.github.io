#!/usr/bin/env python3
"""
EntryProcessor - Processes individual BibTeX entries

Handles processing of individual BibTeX entries including file processing,
thumbnail generation, and metadata updates.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

from processing.config import Configuration
from processing.utils.file_field_manager import FileFieldManager
from processing.utils.file_field_parser import FileFieldParser
from processing.utils.file_manager import FileManager
from processing.core.bibtex_processor import BibTeXProcessor
from processing.core.pdf_processor import PDFProcessor
from processing.core.text_processor import TextProcessor
from processing.core.zip_archive_generator import ZipArchiveGenerator


class EntryProcessor:
    """Processes individual BibTeX entries."""
    
    def __init__(self, config: Configuration, file_manager: FileManager,
                 pdf_processor: PDFProcessor, bibtex_processor: BibTeXProcessor,
                 text_processor: TextProcessor, zip_archive_generator: ZipArchiveGenerator,
                 file_field_manager: FileFieldManager):
        """Initialize with all required processors."""
        self.config = config
        self.file_manager = file_manager
        self.pdf_processor = pdf_processor
        self.bibtex_processor = bibtex_processor
        self.text_processor = text_processor
        self.zip_archive_generator = zip_archive_generator
        self.file_field_manager = file_field_manager
        self.file_field_parser = file_field_manager.parser
    
    def _output_files_exist(self, fields: Dict) -> bool:
        """Check that all pipeline output files referenced in fields exist on disk. Used in incremental mode."""
        field_to_dir = [
            ('preview', self.config.PREVIEW_DIR),
            ('pdf', self.config.PDF_DIR),
            ('slides', self.config.PDF_DIR),
            ('agenda', self.config.PDF_DIR),
            ('zip_archive', self.config.ZIP_DIR),
        ]
        for fname, dir_path in field_to_dir:
            val = fields.get(fname, '').strip()
            if not val:
                continue
            if '://' in val or val.startswith('http'):
                continue
            base = os.path.basename(val.strip().lstrip('/').replace('\\', '/'))
            if not base:
                continue
            if not os.path.exists(os.path.join(dir_path, base)):
                return False
        for bundle in ('figures', 'photos'):
            val = fields.get(bundle, '').strip()
            if not val:
                continue
            for part in val.split(','):
                fn = part.strip().lstrip('/').replace('\\', '/')
                fn = os.path.basename(fn) if fn else ''
                if not fn or '://' in fn:
                    continue
                if not os.path.exists(os.path.join(self.config.IMAGES_DIR, fn)):
                    return False
        return True

    def is_entry_processed(self, fields: Dict, incremental: bool = False) -> bool:
        """Check if entry already has required tags. When incremental=True, also require referenced output files exist on disk."""
        has_preview = 'preview' in fields and fields.get('preview', '').strip()
        has_doc = bool(fields.get('pdf', '').strip() or fields.get('slides', '').strip() or fields.get('agenda', '').strip())
        has_basic_processing = has_preview and has_doc
        if not has_basic_processing:
            return False
        file_field = fields.get('file', '')
        has_unprocessed_images = any(f':image/{ext}' in file_field for ext in ['jpeg', 'jpg', 'png', 'gif'])
        if has_unprocessed_images:
            return False
        if incremental:
            return self._output_files_exist(fields)
        return True

    def process_entry(self, entry: Dict, regenerate: bool, force: bool, incremental: bool,
                     update_metadata: bool, thumbnail_size: str, verbose: bool,
                     force_refetch_metadata: bool, rename_only: bool,
                     update_pdf_metadata: bool = False) -> bool:
        """
        Process a single BibTeX entry.
        
        Args:
            entry: Dictionary with 'citation_key' and 'fields' keys
            regenerate: Whether to regenerate existing files
            force: Whether to force reprocessing
            update_metadata: Whether to update metadata
            thumbnail_size: Size for thumbnail generation
            verbose: Whether to print verbose output
            force_refetch_metadata: Whether to force refetch metadata
            rename_only: Whether to only rename URLs
            update_pdf_metadata: Whether to update PDF metadata
        
        Returns:
            True if processing succeeded, False otherwise
        """
        citation_key = entry.get('citation_key', '')
        fields = entry.get('fields', {})
        
        if not citation_key or not fields:
            return False
        
        print(f"\n📄 Processing: {citation_key}")

        # Skip if already processed (unless force mode)
        if not force and self.is_entry_processed(fields, incremental=incremental):
            if incremental and entry.get('_original_content'):
                entry['_skipped'] = True
            print(f"  ⏭️  Already processed, skipping")
            return True
        
        # Process files and generate thumbnails
        if not self.process_entry_files(citation_key, fields, regenerate, force, incremental,
                                       thumbnail_size, verbose, update_pdf_metadata):
            return False
        
        # Update metadata if requested
        if update_metadata and not rename_only:
            self._update_entry_metadata(citation_key, fields, force_refetch_metadata, verbose)
        
        return True
    
    def process_entry_files(self, citation_key: str, fields: Dict, regenerate: bool,
                           force: bool, incremental: bool, thumbnail_size: str, verbose: bool,
                           update_pdf_metadata: bool = False) -> bool:
        """
        Process files for an entry (PDFs, images, thumbnails).
        
        Args:
            citation_key: The citation key for the entry
            fields: Dictionary of BibTeX fields
            regenerate: Whether to regenerate existing files
            force: Whether to force reprocessing
            thumbnail_size: Size for thumbnail generation
            verbose: Whether to print verbose output
            update_pdf_metadata: Whether to update PDF metadata
        
        Returns:
            True if all file processing succeeded, False otherwise
        """
        if 'file' not in fields or not fields['file']:
            print(f"  ⚠️  No file field found")
            return True
        
        # Extract file paths - separate agenda and slides PDFs from regular PDFs
        all_pdf_paths = self.bibtex_processor.extract_pdf_files(fields['file'])
        agenda_paths = self.bibtex_processor.extract_agenda_pdfs(fields['file'])
        slides_paths = self.bibtex_processor.extract_slides_pdfs(fields['file'])
        image_paths = self.bibtex_processor.extract_image_files(fields['file'])
        audio_paths = self.bibtex_processor.extract_audio_files(fields['file'])
        
        # Remove agenda and slides PDFs from regular PDF list to avoid double processing
        regular_pdf_paths = [p for p in all_pdf_paths if p not in agenda_paths and p not in slides_paths]
        
        # Process regular PDFs
        pdf_success = self._process_pdfs(citation_key, fields, regular_pdf_paths, regenerate, force, verbose, update_pdf_metadata)
        
        # Process agenda PDFs separately (creates agenda field, not pdf field)
        agenda_success = self._process_agenda_pdfs(citation_key, fields, agenda_paths, regenerate, force, verbose)
        
        # Process slides PDFs separately if found by name (creates slides field)
        # Note: Slides may also be created from keyword detection elsewhere
        slides_success = True
        if slides_paths:
            slides_success = self._process_slides_pdfs(citation_key, fields, slides_paths, regenerate, force, verbose)
        
        # Process images
        image_success = self._process_images(citation_key, fields, image_paths, regenerate, force, verbose)
        
        # Clean file field to remove image entries if images were processed
        if image_success and image_paths and ('photos' in fields or 'figures' in fields):
            fields['file'] = self.file_field_manager.remove_images(fields['file'])
        
        # Process audio files
        audio_success = self._process_audio_files(citation_key, fields, audio_paths, regenerate, force, verbose)
        
        # Clean file field to remove audio entries if audio files were processed
        if audio_success and audio_paths:
            fields['file'] = self.file_field_manager.remove_audio(fields['file'])
        
        # Process thumbnails with priority logic
        thumbnail_success = self._process_thumbnails_with_priority(citation_key, fields,
                                                                  regenerate, force, thumbnail_size, verbose)
        
        # Clean file field to remove all processed files (PDFs, images, thumbnails, audio)
        # Only keep the file field if there are unprocessed files
        if pdf_success or agenda_success or slides_success or image_success or audio_success or thumbnail_success:
            fields['file'] = self.file_field_manager.replace_with_processed(fields['file'], fields)
        
        # Create zip archive if entry has been successfully processed
        # Only create zip if there are files to archive (pdf/slides and/or images)
        has_files = (pdf_success and ('pdf' in fields or 'slides' in fields)) or image_success or audio_success
        if has_files:
            zip_metadata = self.zip_archive_generator.create_archive(citation_key, fields, skip_if_exists=incremental)
            if zip_metadata:
                # Add zip filename and metadata to fields
                fields['zip_archive'] = zip_metadata['filename']
                fields['zip_file_count'] = zip_metadata['file_count']
                fields['zip_file_size_mb'] = zip_metadata['file_size_mb']
        
        return pdf_success and agenda_success and slides_success and image_success and audio_success and thumbnail_success
    
    def _process_pdfs(self, citation_key: str, fields: Dict, pdf_paths: List[str],
                     regenerate: bool, force: bool, verbose: bool,
                     update_pdf_metadata: bool = False) -> bool:
        """Process PDF files for an entry."""
        if not pdf_paths:
            return True
        
        # Track filenames being generated for this entry to handle multiple PDFs
        # that would generate the same base filename (only add suffixes for same-entry collisions)
        session_filenames = set()
        
        success = True
        for pdf_path in pdf_paths:
            if not self._process_single_pdf(citation_key, fields, pdf_path, regenerate, force, verbose, update_pdf_metadata, session_filenames):
                success = False
        
        return success
    
    def _process_single_pdf(self, citation_key: str, fields: Dict, pdf_path: str,
                          regenerate: bool, force: bool, verbose: bool,
                          update_pdf_metadata: bool = False, session_filenames: set = None) -> bool:
        """Process a single PDF file."""
        import os
        
        if not os.path.exists(pdf_path):
            print(f"  ❌ PDF not found: {pdf_path}")
            return False
        
        # Use session_filenames to track filenames for this entry only
        # Only add suffixes when multiple PDFs for the SAME entry would generate the same filename
        if session_filenames is None:
            session_filenames = set()
        
        # Generate filename (only check for collisions within current entry's session)
        # Don't check directory - only add suffixes for same-entry duplicates
        filename = self.text_processor.generate_filename(citation_key, fields, 'pdf',
                                                         existing_filenames=session_filenames)
        if not filename:
            print(f"  ❌ Could not generate filename for PDF")
            return False
        
        # Add to session tracking
        session_filenames.add(filename)
        
        # Copy PDF
        dest_path = os.path.join(self.config.PDF_DIR, filename)
        if not os.path.exists(dest_path) or force:
            if not self.file_manager.copy_file(pdf_path, dest_path, force):
                return False
        
        # Update PDF metadata only in regenerate mode (if enabled)
        if update_pdf_metadata and regenerate:
            # Prepare metadata from BibTeX fields
            metadata = self.pdf_processor.prepare_pdf_metadata(fields)
            
            # Update metadata on destination PDF (not source)
            # Failures are logged but don't stop processing
            if not self.pdf_processor.update_pdf_metadata(dest_path, metadata, backup=False):
                if verbose:
                    print(f"  ⚠️  PDF metadata update failed for {filename}, continuing...")
            # Note: We don't return False here - metadata update failure shouldn't stop processing
        
        # Add tags to fields
        fields['pdf'] = filename
        
        return True
    
    def _process_agenda_pdfs(self, citation_key: str, fields: Dict, agenda_paths: List[str],
                            regenerate: bool, force: bool, verbose: bool) -> bool:
        """Process agenda PDF files for an entry."""
        import os
        
        if not agenda_paths:
            return True
        
        # Process the first agenda PDF (typically only one)
        agenda_path = agenda_paths[0]
        if not os.path.exists(agenda_path):
            print(f"  ❌ Agenda PDF not found: {agenda_path}")
            return False
        
        # Generate filename
        filename = self.text_processor.generate_filename(citation_key, fields, 'pdf',
                                                         check_directory=self.config.PDF_DIR)
        if not filename:
            print(f"  ❌ Could not generate filename for agenda PDF")
            return False
        
        # Modify filename to indicate it's an agenda
        base_name = filename.replace('.pdf', '')
        agenda_filename = f"{base_name}_agenda.pdf"
        
        # Copy agenda PDF
        dest_path = os.path.join(self.config.PDF_DIR, agenda_filename)
        if not os.path.exists(dest_path) or force:
            if not self.file_manager.copy_file(agenda_path, dest_path, force):
                return False
        
        # Add agenda field (do NOT add pdf or preview fields)
        fields['agenda'] = agenda_filename
        
        return True
    
    def _process_slides_pdfs(self, citation_key: str, fields: Dict, slides_paths: List[str],
                            regenerate: bool, force: bool, verbose: bool) -> bool:
        """Process slides PDF files for an entry."""
        import os
        
        if not slides_paths:
            return True
        
        # Process the first slides PDF (typically only one)
        slides_path = slides_paths[0]
        if not os.path.exists(slides_path):
            print(f"  ❌ Slides PDF not found: {slides_path}")
            return False
        
        # Generate filename
        filename = self.text_processor.generate_filename(citation_key, fields, 'pdf',
                                                         check_directory=self.config.PDF_DIR)
        if not filename:
            print(f"  ❌ Could not generate filename for slides PDF")
            return False
        
        # Modify filename to indicate it's slides (or use as-is if already descriptive)
        base_name = filename.replace('.pdf', '')
        slides_filename = f"{base_name}_slides.pdf"
        
        # Copy slides PDF
        dest_path = os.path.join(self.config.PDF_DIR, slides_filename)
        if not os.path.exists(dest_path) or force:
            if not self.file_manager.copy_file(slides_path, dest_path, force):
                return False
        
        # Add slides field
        fields['slides'] = slides_filename
        
        return True
    
    def _process_images(self, citation_key: str, fields: Dict, image_paths: List[str],
                      regenerate: bool, force: bool, verbose: bool) -> bool:
        """Process image files for an entry."""
        if not image_paths:
            return True
        
        # Use the existing image processing logic
        processed_images = self.file_manager.process_images_for_entry(
            citation_key, fields, self.config.IMAGES_DIR, force, regenerate, verbose
        )
        
        # Store processed images in fields for file field replacement logic
        for image_type, files in processed_images.items():
            if files:
                # Convert singular to plural for BibTeX fields
                field_name = f"{image_type}s" if image_type in ['photo', 'figure'] else image_type
                fields[field_name] = ', '.join(files)
        
        return True
    
    def _process_audio_files(self, citation_key: str, fields: Dict, audio_paths: List[str],
                           regenerate: bool, force: bool, verbose: bool) -> bool:
        """Process audio files for an entry."""
        import os
        
        if not audio_paths:
            return True
        
        # Ensure audio directory exists
        os.makedirs(self.config.AUDIO_DIR, exist_ok=True)
        
        processed_audio_paths = []
        
        for audio_path in audio_paths:
            if not os.path.exists(audio_path):
                if verbose:
                    print(f"  ⚠️  Audio file not found: {audio_path}")
                continue
            
            # Get the original filename
            original_filename = os.path.basename(audio_path)
            # Keep original filename (or could use naming convention if needed)
            audio_filename = original_filename
            
            # Copy audio file to assets/audio/
            dest_path = os.path.join(self.config.AUDIO_DIR, audio_filename)
            
            if not os.path.exists(dest_path) or force:
                if not self.file_manager.copy_file(audio_path, dest_path, force):
                    if verbose:
                        print(f"  ❌ Failed to copy audio file: {audio_path}")
                    continue
            
            # Store relative path for annote field (relative to site root)
            relative_path = f"assets/audio/{audio_filename}"
            processed_audio_paths.append(relative_path)
            
            if verbose:
                print(f"  ✅ Processed audio: {audio_filename}")
        
        # Add audio paths to annote field in [audio] format
        if processed_audio_paths:
            self._add_audio_to_annote(fields, processed_audio_paths)
        
        return True
    
    def _add_audio_to_annote(self, fields: Dict, audio_paths: List[str]) -> None:
        """Add audio file paths to annote field in [audio] format."""
        import re
        
        # Create the audio section content
        audio_section = '\n'.join(audio_paths)
        
        # Check if annote field exists
        if 'annote' in fields and fields['annote']:
            annote_content = fields['annote'].strip()
            
            # Check if [audio] section already exists
            if '[audio]' in annote_content:
                # Replace existing [audio] section
                # Split by [audio] tag, keep everything before it, add new audio section
                parts = annote_content.split('[audio]')
                before_audio = parts[0].strip()
                # Remove everything after [audio] until next [tag] or end
                if len(parts) > 1:
                    after_audio = parts[1]
                    # Find next [tag] or end of string
                    next_tag_match = re.search(r'\[', after_audio)
                    if next_tag_match:
                        after_audio = after_audio[next_tag_match.start():]
                    else:
                        after_audio = ''
                else:
                    after_audio = ''
                
                # Reconstruct annote with new audio section
                if before_audio:
                    fields['annote'] = f"{before_audio}\n\n[audio]\n{audio_section}"
                else:
                    fields['annote'] = f"[audio]\n{audio_section}"
                
                if after_audio:
                    fields['annote'] += f"\n\n{after_audio}"
            else:
                # Append [audio] section to existing annote
                fields['annote'] = f"{annote_content}\n\n[audio]\n{audio_section}"
        else:
            # Create new annote field with [audio] section
            fields['annote'] = f"[audio]\n{audio_section}"
    
    def _process_thumbnails_with_priority(self, citation_key: str, fields: Dict,
                                        regenerate: bool, force: bool, thumbnail_size: str, verbose: bool) -> bool:
        """Process thumbnails using priority logic: thumbnail file > slides PDF > agenda PDF > most recent PDF."""
        import os
        
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
                priority_names = {1: "thumbnail file", 2: "slides PDF", 3: "agenda PDF", 4: "most recent PDF"}
                print(f"  🔍 Trying {priority_names[priority]}: {os.path.basename(file_path)}")
            
            if self._process_single_thumbnail_file(citation_key, fields, file_path, file_type,
                                                regenerate, force, thumbnail_size, verbose):
                return True
            else:
                if verbose:
                    priority_names = {1: "thumbnail file", 2: "slides PDF", 3: "agenda PDF", 4: "most recent PDF"}
                    print(f"  ❌ Failed to generate thumbnail from {priority_names[priority]}")
        
        print(f"  ❌ All thumbnail generation attempts failed")
        return False
    
    def _process_single_thumbnail_file(self, citation_key: str, fields: Dict, file_path: str,
                                     file_type: str, regenerate: bool, force: bool,
                                     thumbnail_size: str, verbose: bool) -> bool:
        """Process a single thumbnail file based on its type."""
        import os
        
        if not os.path.exists(file_path):
            if verbose:
                print(f"  ❌ File not found: {file_path}")
            return False
        
        # Generate filename for thumbnail (only check for collisions within same entry)
        filename = self.text_processor.generate_filename(citation_key, fields, 'jpeg')
        if not filename:
            if verbose:
                print(f"  ❌ Could not generate filename for thumbnail")
            return False
        
        preview_path = os.path.join(self.config.PREVIEW_DIR, filename)
        
        # Skip if already exists and not forcing or regenerating
        if os.path.exists(preview_path) and not (force or regenerate):
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
    
    def _copy_image_as_thumbnail(self, source_path: str, dest_path: str) -> bool:
        """Copy an image file to the thumbnail directory."""
        import os
        import shutil
        
        try:
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(source_path, dest_path)
            print(f"  ✅ Copied image thumbnail: {os.path.basename(dest_path)}")
            return True
        except Exception as e:
            print(f"  ❌ Error copying image thumbnail: {e}")
            return False
    
    def _should_add_preview_field(self, fields: Dict) -> bool:
        """Check if a preview field should be added based on available content."""
        # Always add preview field if we have successfully processed a thumbnail
        # The preview field represents the thumbnail/preview image regardless of source
        return True
    
    def _update_entry_metadata(self, citation_key: str, fields: Dict,
                             force_refetch_metadata: bool, verbose: bool) -> None:
        """Update entry metadata using external APIs."""
        # This would integrate with the metadata fetcher
        # For now, just a placeholder
        pass
