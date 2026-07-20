#!/usr/bin/env python3
"""
PaperProcessor class for process_papers.py
Main processor that coordinates all paper processing operations.
"""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from processing.config import Configuration
from processing.core.bibtex_processor import BibTeXProcessor
from processing.core.entry_processor import EntryProcessor
from processing.utils.file_field_manager import FileFieldManager
from processing.utils.file_field_parser import FileFieldParser
from processing.utils.file_manager import FileManager
from processing.core.pdf_processor import PDFProcessor
from processing.core.text_processor import TextProcessor
from processing.utils.metadata_fetcher import MetadataFetcher
from processing.core.bibtex_formatter import BibTeXFormatter
from processing.core.zip_archive_generator import ZipArchiveGenerator


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
        self.zip_archive_generator = ZipArchiveGenerator(self.config, self.text_processor)
        self.file_field_parser = FileFieldParser()
        self.file_field_manager = FileFieldManager(self.file_field_parser)
        
        # Initialize entry processor with all required dependencies
        self.entry_processor = EntryProcessor(
            config=self.config,
            file_manager=self.file_manager,
            pdf_processor=self.pdf_processor,
            bibtex_processor=self.bibtex_processor,
            text_processor=self.text_processor,
            zip_archive_generator=self.zip_archive_generator,
            file_field_manager=self.file_field_manager
        )
    
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
                      force: bool = False, incremental: bool = False, update_metadata: bool = True,
                      thumbnail_size: str = '600x', test_mode: bool = False,
                      test_count: int = 5, verbose: bool = False,
                      force_refetch_metadata: bool = False, rename_urls: bool = True,
                      rename_only: bool = False, update_pdf_metadata: bool = False) -> None:
        """Main function to process papers from Zotero export."""
        source_file = source_bibtex_file or self.config.SOURCE_BIBTEX_FILE
        working_file = self.config.WORKING_BIBTEX_FILE

        print(f"📚 Processing {source_file}...")

        # Enable image content analysis when regenerating
        if regenerate:
            self.config.ENABLE_IMAGE_CONTENT_ANALYSIS = True
            self._cleanup_existing_files()

        if incremental and os.path.exists(working_file):
            # Incremental: merge export with existing papers.bib; do not overwrite working file yet
            source_content = self._read_bibtex_file(source_file)
            if not source_content:
                return
            working_content = self._read_bibtex_file(working_file)
            if not working_content:
                return
            # Clean/notes on export content only (new entries get same cleaning as today)
            cleaned_export = self.bibtex_processor.clean_malformed_entries(source_content)
            cleaned_export = self.bibtex_processor.process_notes_from_zotero(cleaned_export)
            entries = self._merge_export_with_existing(cleaned_export, working_content)
            if test_mode:
                entries = entries[:test_count]
                print(f"  🧪 Test mode: Processing only {len(entries)} entries")
            stats = self._process_entries(
                entries=entries,
                working_file=working_file,
                regenerate=regenerate,
                force=force,
                incremental=incremental,
                update_metadata=update_metadata,
                thumbnail_size=thumbnail_size,
                test_mode=test_mode,
                test_count=test_count,
                verbose=verbose,
                force_refetch_metadata=force_refetch_metadata,
                rename_urls=rename_urls,
                rename_only=rename_only,
                update_pdf_metadata=update_pdf_metadata,
            )
            self._write_updated_bibtex_from_entries(entries, working_file, rename_urls, incremental=True)
            if stats is not None:
                self._print_incremental_summary(stats, len(entries))
        else:
            # Non-incremental or first run (no papers.bib): copy source to working, then process as before
            if not self._copy_source_to_working(source_file, working_file):
                return
            content = self._read_bibtex_file(working_file)
            if not content:
                return
            content = self.bibtex_processor.clean_malformed_entries(content)
            content = self.bibtex_processor.process_notes_from_zotero(content)
            with open(working_file, 'w', encoding='utf-8') as f:
                f.write(content)
            self._process_entries(
                working_file=working_file,
                regenerate=regenerate,
                force=force,
                incremental=False,
                update_metadata=update_metadata,
                thumbnail_size=thumbnail_size,
                test_mode=test_mode,
                test_count=test_count,
                verbose=verbose,
                force_refetch_metadata=force_refetch_metadata,
                rename_urls=rename_urls,
                rename_only=rename_only,
                update_pdf_metadata=update_pdf_metadata,
                content=content,
            )

        print(f"\n✅ Processing completed successfully!")
    
    def _cleanup_existing_files(self) -> None:
        """Clean up existing files if regenerate mode is enabled."""
        print("  🧹 Cleaning up existing files...")
        
        deleted_counts = {}
        
        # Clean up PDFs
        if os.path.exists(self.config.PDF_DIR):
            count = 0
            for file in os.listdir(self.config.PDF_DIR):
                if file.endswith('.pdf'):
                    try:
                        os.remove(os.path.join(self.config.PDF_DIR, file))
                        count += 1
                    except Exception as e:
                        print(f"  ⚠️  Could not delete PDF {file}: {e}")
            deleted_counts['PDFs'] = count
            if count > 0:
                print(f"  🗑️  Deleted {count} PDFs from {self.config.PDF_DIR}")
        
        # Clean up preview thumbnails
        if os.path.exists(self.config.PREVIEW_DIR):
            count = 0
            for file in os.listdir(self.config.PREVIEW_DIR):
                if file.endswith(('.jpeg', '.jpg')):
                    try:
                        os.remove(os.path.join(self.config.PREVIEW_DIR, file))
                        count += 1
                    except Exception as e:
                        print(f"  ⚠️  Could not delete thumbnail {file}: {e}")
            deleted_counts['thumbnails'] = count
            if count > 0:
                print(f"  🗑️  Deleted {count} thumbnails from {self.config.PREVIEW_DIR}")
        
        # Clean up zip archives
        if os.path.exists(self.config.ZIP_DIR):
            count = 0
            for file in os.listdir(self.config.ZIP_DIR):
                if file.endswith('.zip'):
                    try:
                        os.remove(os.path.join(self.config.ZIP_DIR, file))
                        count += 1
                    except Exception as e:
                        print(f"  ⚠️  Could not delete zip {file}: {e}")
            deleted_counts['zips'] = count
            if count > 0:
                print(f"  🗑️  Deleted {count} zip archives from {self.config.ZIP_DIR}")
        
        # Clean up images (photos and figures)
        if os.path.exists(self.config.IMAGES_DIR):
            count = 0
            for file in os.listdir(self.config.IMAGES_DIR):
                if any(file.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                    try:
                        os.remove(os.path.join(self.config.IMAGES_DIR, file))
                        count += 1
                    except Exception as e:
                        print(f"  ⚠️  Could not delete image {file}: {e}")
            deleted_counts['images'] = count
            if count > 0:
                print(f"  🗑️  Deleted {count} images from {self.config.IMAGES_DIR}")
        
        # Clean up audio files
        if os.path.exists(self.config.AUDIO_DIR):
            count = 0
            for file in os.listdir(self.config.AUDIO_DIR):
                if any(file.lower().endswith(ext) for ext in ['.mp3', '.wav', '.ogg', '.m4a', '.aac']):
                    try:
                        os.remove(os.path.join(self.config.AUDIO_DIR, file))
                        count += 1
                    except Exception as e:
                        print(f"  ⚠️  Could not delete audio {file}: {e}")
            deleted_counts['audio'] = count
            if count > 0:
                print(f"  🗑️  Deleted {count} audio files from {self.config.AUDIO_DIR}")
        
        total_deleted = sum(deleted_counts.values())
        if total_deleted > 0:
            print(f"  ✅ Cleanup complete: Deleted {total_deleted} files total")
        else:
            print(f"  ℹ️  No existing files to clean up")
    
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

    def _merge_export_with_existing(self, source_content: str, working_content: str) -> List[Dict]:
        """Merge export content with existing papers.bib; export is source of truth, preserve pipeline output fields from existing."""
        existing_list = self.bibtex_processor.parse_bibtex_entries(working_content)
        existing_by_key = {e['citation_key']: e for e in existing_list}
        export_entries = self.bibtex_processor.parse_bibtex_entries(source_content)
        pipeline_fields = getattr(self.config, 'PIPELINE_OUTPUT_FIELDS', ())

        merged = []
        for export_entry in export_entries:
            key = export_entry.get('citation_key', '')
            fields = dict(export_entry.get('fields', {}))
            content = export_entry.get('content', '')
            if key in existing_by_key:
                existing = existing_by_key[key]
                for fname in pipeline_fields:
                    if fname in existing.get('fields', {}) and existing['fields'][fname]:
                        fields[fname] = existing['fields'][fname]
                merged.append({
                    'citation_key': key,
                    'fields': fields,
                    'content': content,
                    '_original_content': existing['content'].rstrip(),
                })
            else:
                merged.append({
                    'citation_key': key,
                    'fields': fields,
                    'content': content,
                })
        return merged

    def _process_entries(self, working_file: str, regenerate: bool, force: bool,
                        incremental: bool, update_metadata: bool, thumbnail_size: str,
                        test_mode: bool, test_count: int, verbose: bool,
                        force_refetch_metadata: bool, rename_urls: bool,
                        rename_only: bool, update_pdf_metadata: bool = False,
                        content: Optional[str] = None, entries: Optional[List[Dict]] = None) -> Optional[Dict]:
        """Process all BibTeX entries. Pass either content (parse and optionally slice) or pre-built entries (e.g. merged)."""
        if entries is None:
            if content is None:
                return None
            entries = self.bibtex_processor.parse_bibtex_entries(content)
            if test_mode:
                entries = entries[:test_count]
                print(f"  🧪 Test mode: Processing only {len(entries)} entries")

        processed_count = 0
        skipped_count = 0
        skipped_but_missing_count = 0
        merged_hits = sum(1 for e in entries if e.get('_original_content'))

        for entry in entries:
            ok = self.entry_processor.process_entry(
                entry, regenerate, force, incremental, update_metadata,
                thumbnail_size, verbose, force_refetch_metadata,
                rename_only, update_pdf_metadata,
            )
            if ok:
                if entry.get('_skipped'):
                    skipped_count += 1
                else:
                    processed_count += 1
                    if entry.get('_original_content'):
                        skipped_but_missing_count += 1

        print(f"  📊 Processed {processed_count} entries" + (f", skipped {skipped_count}" if incremental else ""))

        if not incremental:
            self._write_updated_bibtex_from_entries(entries, working_file, rename_urls, incremental=False)
            return None
        return {
            'total_in_export': len(entries),
            'merged_existing_hits': merged_hits,
            'processed_count': processed_count,
            'skipped_count': skipped_count,
            'skipped_but_missing_files': skipped_but_missing_count,
        }

    def _print_incremental_summary(self, stats: Dict, total_entries: int) -> None:
        """Print run summary in incremental mode."""
        print(f"\n  📋 Incremental summary: {stats['total_in_export']} in export, "
              f"{stats['merged_existing_hits']} merged from existing, "
              f"{stats['processed_count']} processed, {stats['skipped_count']} skipped"
              + (f", {stats['skipped_but_missing_files']} reprocessed (missing files)" if stats['skipped_but_missing_files'] else ""))

    def _clean_file_field_in_content(self, content: str, fields: Dict) -> str:
        """Clean the file field in the content to remove processed files."""
        # Find the file field in the content
        file_field_pattern = r'file\s*=\s*\{([^}]+)\}'
        match = re.search(file_field_pattern, content)
        if not match:
            return content
        
        file_field = match.group(1)
        cleaned_file_field = self.file_field_manager.replace_with_processed(file_field, fields)
        
        # Replace the file field in the content
        if cleaned_file_field:
            new_file_field = f"file = {{{cleaned_file_field}}}"
        else:
            new_file_field = ""  # Remove the file field entirely if empty
        
        return content.replace(match.group(0), new_file_field)
    
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
    
    def _write_updated_bibtex_from_entries(self, entries: List[Dict], working_file: str, rename_urls: bool = True, incremental: bool = False) -> None:
        """Write updated BibTeX content back to file using modified entries."""
        try:
            if incremental:
                blocks = []
                url_renames = 0
                for entry in entries:
                    # Skipped entries keep their exact original block (idempotent incremental).
                    if entry.get('_skipped') and entry.get('_original_content'):
                        updated = entry['_original_content']
                    else:
                        # Rebuild from export content and re-apply pipeline output fields.
                        updated = self._update_entry_content(entry['content'], entry['fields'])
                        if rename_urls:
                            updated, url_count = self.bibtex_processor.rename_url_fields(updated)
                            url_renames += url_count
                    blocks.append(updated.rstrip())
                if url_renames > 0:
                    print(f"  🔄 Renamed {url_renames} URL field(s) in updated blocks")
                final_content = '\n\n'.join(blocks) + '\n'
                with open(working_file, 'w', encoding='utf-8') as f:
                    f.write(final_content)
                print(f"  ✅ Updated {working_file}")
                return
            # Non-incremental: rebuild all entries, global rename_urls, then format
            updated_content = []
            for entry in entries:
                citation_key = entry['citation_key']
                fields = entry['fields']
                entry_content = entry['content']
                updated_entry = self._update_entry_content(entry_content, fields)
                updated_content.append(updated_entry)
            final_content = '\n\n'.join(updated_content)
            if rename_urls:
                final_content, url_count = self.bibtex_processor.rename_url_fields(final_content)
                if url_count > 0:
                    print(f"  🔄 Renamed {url_count} URL fields to website fields")
            try:
                formatted_entries = []
                for entry_content in final_content.split('\n\n'):
                    if entry_content.strip():
                        formatted_entry = self.formatter.format_entry_from_content(entry_content)
                        formatted_entries.append(formatted_entry)
                final_content = '\n\n'.join(formatted_entries)
            except Exception as e:
                print(f"  ⚠️  Warning: Could not apply formatting: {e}")
            with open(working_file, 'w', encoding='utf-8') as f:
                f.write(final_content + '\n')
            print(f"  ✅ Updated {working_file}")
        except Exception as e:
            print(f"  ❌ Error writing {working_file}: {e}")
    
    def _find_entry_closing_brace(self, entry_content: str) -> int:
        """Return index of the entry-level closing brace, or -1 if missing/unbalanced.

        Walks braces starting at the opening `{` after `@type{key` so field-value
        braces are not mistaken for the entry terminator.
        """
        brace_start = entry_content.find('{')
        if brace_start == -1:
            return -1
        depth = 0
        for i in range(brace_start, len(entry_content)):
            ch = entry_content[i]
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    return i
        return -1

    def _update_entry_content(self, entry_content: str, fields: Dict) -> str:
        """Update an entry's content with new fields."""
        last_brace = self._find_entry_closing_brace(entry_content)
        if last_brace == -1:
            # No entry-level closing brace found, return original content unchanged
            return entry_content
        
        # Extract the part before the closing brace
        before_brace = entry_content[:last_brace]
        after_brace = entry_content[last_brace:]
        
        # Update the file field to replace processed files with descriptive filenames
        if 'preview' in fields or 'pdf' in fields or 'photos' in fields or 'figures' in fields:
            before_brace = self._clean_file_field_in_content(before_brace, fields)
        
        # Update annote field if it was modified (e.g., by audio processing)
        if 'annote' in fields and fields['annote']:
            # Replace existing annote field or add new one
            annote_pattern = r'annote\s*=\s*\{[^}]*\}'
            new_annote = fields['annote']
            # Format annote with proper braces
            if not new_annote.startswith('{'):
                new_annote = '{' + new_annote + '}'
            
            if re.search(annote_pattern, before_brace):
                # Replace existing annote field
                before_brace = re.sub(annote_pattern, f'annote = {new_annote}', before_brace)
            else:
                # Add new annote field (will be added to new_fields below)
                pass
        
        # Persist pipeline output fields (must match Configuration.PIPELINE_OUTPUT_FIELDS + annote).
        # Without this, photos/figures/zip_* are lost every run → entries reprocess and zips proliferate (_a, _b, ...).
        persistable_fields = (
            'preview', 'pdf', 'slides', 'agenda', 'annote',
            'photos', 'figures',
            'zip_archive', 'zip_file_count', 'zip_file_size_mb',
        )
        new_fields = []
        for field_name, field_value in fields.items():
            if field_name not in persistable_fields:
                continue
            # Skip empty or None values
            if not field_value or (isinstance(field_value, str) and field_value.strip() == ''):
                continue

            # Check if field already exists in the content
            if f"{field_name} =" not in before_brace:
                # Handle field values that already contain curly braces
                if isinstance(field_value, str) and field_value.startswith('{') and field_value.endswith('}'):
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
