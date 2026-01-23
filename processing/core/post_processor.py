#!/usr/bin/env python3
"""
PostProcessor module for process_papers.py
Handles post-processing cleanup and field removal after main processing is complete.
"""

import os
import re
from typing import Dict, List, Optional

from processing.config import Configuration
from processing.utils.field_cleaner import FieldCleaner
from processing.core.bibtex_processor import BibTeXProcessor
from processing.core.bibtex_formatter import BibTeXFormatter


class PostProcessor:
    """Handles post-processing cleanup and field removal."""
    
    def __init__(self, config: Configuration = None):
        """Initialize with configuration and dependencies."""
        self.config = config or Configuration()
        self.field_cleaner = FieldCleaner(config)
        self.bibtex_processor = BibTeXProcessor(config)
        self.formatter = BibTeXFormatter()
    
    def clean_processed_entries(self, bibtex_file: str, remove_file_field: bool = True) -> bool:
        """
        Clean processed entries by removing processed fields from file field.
        
        Args:
            bibtex_file: Path to the BibTeX file to clean
            remove_file_field: Whether to remove the file field entirely after processing
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Read the BibTeX file
            with open(bibtex_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse entries
            entries = self.bibtex_processor.parse_bibtex_entries(content)
            
            # Track if any changes were made
            changes_made = False
            
            # Process each entry
            for entry in entries:
                citation_key = entry['citation_key']
                fields = entry['fields']
                entry_content = entry['content']
                
                # Check if this entry has been processed
                if self._is_entry_processed(fields):
                    print(f"  🧹 Cleaning processed entry: {citation_key}")
                    
                    # Clean the file field
                    if 'file' in fields and fields['file']:
                        original_file_field = fields['file']
                        
                        if remove_file_field:
                            # Remove the file field entirely
                            cleaned_content = self.field_cleaner.remove_field_from_content(
                                entry_content, 'file'
                            )
                            # Remove from fields dict
                            del fields['file']
                        else:
                            # Clean the file field to remove processed files
                            cleaned_file_field = self.field_cleaner.clean_file_field_after_processing(
                                fields['file'], fields
                            )
                            
                            if cleaned_file_field != original_file_field:
                                # Update the content
                                cleaned_content = self._update_field_in_content(
                                    entry_content, 'file', cleaned_file_field
                                )
                                # Update the fields dict
                                fields['file'] = cleaned_file_field
                            else:
                                cleaned_content = entry_content
                        
                        # Update the entry content
                        entry['content'] = cleaned_content
                        changes_made = True
                        print(f"    ✅ Cleaned file field for {citation_key}")
            
            # Write the cleaned content back to file
            if changes_made:
                self._write_cleaned_content(entries, bibtex_file)
                print(f"✅ Successfully cleaned {bibtex_file}")
                return True
            else:
                print("ℹ️  No entries needed cleaning")
                return True
                
        except Exception as e:
            print(f"❌ Error cleaning entries: {e}")
            return False
    
    def remove_specific_fields(self, bibtex_file: str, field_names: List[str]) -> bool:
        """
        Remove specific fields from all entries in a BibTeX file.
        
        Args:
            bibtex_file: Path to the BibTeX file to process
            field_names: List of field names to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Read the BibTeX file
            with open(bibtex_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse entries
            entries = self.bibtex_processor.parse_bibtex_entries(content)
            
            # Track if any changes were made
            changes_made = False
            
            # Process each entry
            for entry in entries:
                citation_key = entry['citation_key']
                fields = entry['fields']
                entry_content = entry['content']
                
                # Check if any of the fields exist
                fields_to_remove = [field for field in field_names if field in fields]
                
                if fields_to_remove:
                    print(f"  🗑️  Removing fields from {citation_key}: {', '.join(fields_to_remove)}")
                    
                    # Remove fields from content
                    cleaned_content = self.field_cleaner.remove_multiple_fields_from_content(
                        entry_content, fields_to_remove
                    )
                    
                    # Remove fields from fields dict
                    for field in fields_to_remove:
                        del fields[field]
                    
                    # Update the entry content
                    entry['content'] = cleaned_content
                    changes_made = True
            
            # Write the cleaned content back to file
            if changes_made:
                self._write_cleaned_content(entries, bibtex_file)
                print(f"✅ Successfully removed fields from {bibtex_file}")
                return True
            else:
                print("ℹ️  No fields to remove")
                return True
                
        except Exception as e:
            print(f"❌ Error removing fields: {e}")
            return False
    
    def clean_file_field_only(self, bibtex_file: str) -> bool:
        """
        Clean only the file field from processed entries, removing processed files.
        
        Args:
            bibtex_file: Path to the BibTeX file to process
            
        Returns:
            True if successful, False otherwise
        """
        return self.clean_processed_entries(bibtex_file, remove_file_field=True)
    
    def remove_file_field_entirely(self, bibtex_file: str) -> bool:
        """
        Remove the file field entirely from processed entries.
        
        Args:
            bibtex_file: Path to the BibTeX file to process
            
        Returns:
            True if successful, False otherwise
        """
        return self.clean_processed_entries(bibtex_file, remove_file_field=True)
    
    def _is_entry_processed(self, fields: Dict) -> bool:
        """Check if an entry has been processed (has preview, pdf, or image fields)."""
        return any(field in fields for field in ['preview', 'pdf', 'slides', 'photos', 'figures'])
    
    def _update_field_in_content(self, content: str, field_name: str, field_value: str) -> str:
        """Update a field value in BibTeX content."""
        # Pattern to match the field and its value
        pattern = rf'({re.escape(field_name)})\s*=\s*\{{[^{{}}]*(?:\{{[^{{}}]*\}}[^{{}}]*)*\}}'
        
        # Handle field values that already contain curly braces
        if field_value.startswith('{') and field_value.endswith('}'):
            # Field value already has braces, use as-is
            replacement = f"{field_name} = {field_value}"
        else:
            # Field value needs braces, add them
            replacement = f"{field_name} = {{{field_value}}}"
        
        # Replace the field
        updated_content = re.sub(pattern, replacement, content)
        
        return updated_content
    
    def _write_cleaned_content(self, entries: List[Dict], bibtex_file: str) -> None:
        """Write cleaned content back to the BibTeX file with proper formatting."""
        # Format each entry properly
        formatted_entries = []
        for entry in entries:
            formatted_entry = self.formatter.format_entry_from_content(entry['content'])
            formatted_entries.append(formatted_entry)
        
        # Join entries with blank lines
        cleaned_content = '\n\n'.join(formatted_entries)
        
        # Write to file
        with open(bibtex_file, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)


def main():
    """Command-line interface for post-processing."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Post-process BibTeX files')
    parser.add_argument('bibtex_file', help='Path to BibTeX file to process')
    parser.add_argument('--clean-file-field', action='store_true',
                       help='Clean file field from processed files')
    parser.add_argument('--remove-file-field', action='store_true',
                       help='Remove file field entirely from processed entries')
    parser.add_argument('--remove-fields', nargs='+',
                       help='Remove specific fields from all entries')
    
    args = parser.parse_args()
    
    processor = PostProcessor()
    
    if args.clean_file_field:
        success = processor.clean_file_field_only(args.bibtex_file)
    elif args.remove_file_field:
        success = processor.remove_file_field_entirely(args.bibtex_file)
    elif args.remove_fields:
        success = processor.remove_specific_fields(args.bibtex_file, args.remove_fields)
    else:
        parser.print_help()
        return
    
    if success:
        print("✅ Post-processing completed successfully")
    else:
        print("❌ Post-processing failed")
        exit(1)


if __name__ == "__main__":
    main()
