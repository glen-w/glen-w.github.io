#!/usr/bin/env python3
"""
ValidationChecker class for process_papers.py
Performs comprehensive validation checks on processed BibTeX entries to ensure completeness.
"""

import os
import re
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from processing.config import Configuration


class ValidationChecker:
    """Handles comprehensive validation of processed BibTeX entries."""
    
    def __init__(self, config: Configuration = None):
        """Initialize with configuration."""
        self.config = config or Configuration()
        self.validation_results = {
            'total_entries': 0,
            'passed_entries': 0,
            'failed_entries': 0,
            'warnings': [],
            'errors': []
        }
    
    def validate_all_entries(self, bibtex_file: str) -> Dict:
        """Validate all entries in a BibTeX file."""
        print("\n🔍 Running comprehensive validation checks...")
        
        # Reset results
        self.validation_results = {
            'total_entries': 0,
            'passed_entries': 0,
            'failed_entries': 0,
            'warnings': [],
            'errors': []
        }
        
        # Read and parse the BibTeX file
        try:
            with open(bibtex_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.validation_results['errors'].append(f"Failed to read BibTeX file: {e}")
            return self.validation_results
        
        # Parse entries
        from core.bibtex_processor import BibTeXProcessor
        processor = BibTeXProcessor(self.config)
        entries = processor.parse_bibtex_entries(content)
        
        self.validation_results['total_entries'] = len(entries)
        
        # Validate each entry
        for entry in entries:
            self._validate_single_entry(entry)
        
        # Print summary
        self._print_validation_summary()
        
        return self.validation_results
    
    def validate_and_fix_entries(self, bibtex_file: str) -> Dict:
        """Validate all entries and automatically fix common issues."""
        print("\n🔍 Running comprehensive validation and fixing issues...")
        
        # Reset results
        self.validation_results = {
            'total_entries': 0,
            'passed_entries': 0,
            'failed_entries': 0,
            'warnings': [],
            'errors': []
        }
        
        # Read and parse the BibTeX file
        try:
            with open(bibtex_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.validation_results['errors'].append(f"Failed to read BibTeX file: {e}")
            return self.validation_results
        
        # Parse entries
        from core.bibtex_processor import BibTeXProcessor
        from core.text_processor import TextProcessor
        processor = BibTeXProcessor(self.config)
        text_processor = TextProcessor(self.config)
        entries = processor.parse_bibtex_entries(content)
        
        self.validation_results['total_entries'] = len(entries)
        
        # Track if any fixes were made
        fixes_made = False
        
        # Validate and fix each entry
        for entry in entries:
            original_content = entry['content']
            fixed_content = self._fix_entry_issues(entry, text_processor)
            
            if fixed_content != original_content:
                entry['content'] = fixed_content
                # Re-parse the entry to update the fields dictionary
                citation_key, fields = processor.parse_bibtex_entry(fixed_content)
                entry['fields'] = fields
                fixes_made = True
                print(f"  🔧 Fixed issues in {entry['citation_key']}")
            
            self._validate_single_entry(entry)
        
        # If fixes were made, write the corrected content back to file
        if fixes_made:
            print(f"\n🔧 Writing corrected content to {bibtex_file}")
            corrected_content = '\n\n'.join([entry['content'] for entry in entries])
            try:
                with open(bibtex_file, 'w', encoding='utf-8') as f:
                    f.write(corrected_content)
                print(f"✅ Successfully wrote corrected BibTeX file")
            except Exception as e:
                self.validation_results['errors'].append(f"Failed to write corrected file: {e}")
        
        # Print summary
        self._print_validation_summary()
        
        return self.validation_results
    
    def _validate_single_entry(self, entry: Dict) -> None:
        """Validate a single BibTeX entry."""
        citation_key = entry.get('citation_key', 'unknown')
        fields = entry.get('fields', {})
        entry_content = entry.get('content', '')
        
        entry_passed = True
        entry_warnings = []
        entry_errors = []
        
        # Check 1: Image processing validation
        image_validation = self._validate_image_processing(citation_key, fields, entry_content)
        if not image_validation['passed']:
            entry_passed = False
            entry_errors.extend(image_validation['errors'])
        entry_warnings.extend(image_validation['warnings'])
        
        # Check 2: File field validation
        file_validation = self._validate_file_field(citation_key, fields, entry_content)
        if not file_validation['passed']:
            entry_passed = False
            entry_errors.extend(file_validation['errors'])
        entry_warnings.extend(file_validation['warnings'])
        
        # Check 3: Preview/thumbnail validation
        preview_validation = self._validate_preview_field(citation_key, fields)
        if not preview_validation['passed']:
            entry_passed = False
            entry_errors.extend(preview_validation['errors'])
        entry_warnings.extend(preview_validation['warnings'])
        
        # Check 4: PDF processing validation
        pdf_validation = self._validate_pdf_processing(citation_key, fields)
        if not pdf_validation['passed']:
            entry_passed = False
            entry_errors.extend(pdf_validation['errors'])
        entry_warnings.extend(pdf_validation['warnings'])
        
        # Check 5: URL field validation
        url_validation = self._validate_url_fields(citation_key, fields)
        if not url_validation['passed']:
            entry_passed = False
            entry_errors.extend(url_validation['errors'])
        entry_warnings.extend(url_validation['warnings'])
        
        # Check 6: Ignore field validation
        ignore_validation = self._validate_ignore_fields(citation_key, fields, entry_content)
        if not ignore_validation['passed']:
            entry_passed = False
            entry_errors.extend(ignore_validation['errors'])
        entry_warnings.extend(ignore_validation['warnings'])
        
        # Check 7: File renaming validation
        renaming_validation = self._validate_file_renaming(citation_key, fields, entry_content)
        if not renaming_validation['passed']:
            entry_passed = False
            entry_errors.extend(renaming_validation['errors'])
        entry_warnings.extend(renaming_validation['warnings'])
        
        # Check 8: BibTeX syntax validation (trailing commas, malformed entries)
        syntax_validation = self._validate_bibtex_syntax(citation_key, entry_content)
        if not syntax_validation['passed']:
            entry_passed = False
            entry_errors.extend(syntax_validation['errors'])
        entry_warnings.extend(syntax_validation['warnings'])
        
        # Check 9: Title cleaning validation (curly braces)
        title_validation = self._validate_title_cleaning(citation_key, fields)
        if not title_validation['passed']:
            entry_passed = False
            entry_errors.extend(title_validation['errors'])
        entry_warnings.extend(title_validation['warnings'])
        
        # Update results
        if entry_passed:
            self.validation_results['passed_entries'] += 1
        else:
            self.validation_results['failed_entries'] += 1
        
        # Add warnings and errors
        for warning in entry_warnings:
            self.validation_results['warnings'].append(f"{citation_key}: {warning}")
        for error in entry_errors:
            self.validation_results['errors'].append(f"{citation_key}: {error}")
    
    def _validate_image_processing(self, citation_key: str, fields: Dict, entry_content: str) -> Dict:
        """Validate image processing completeness."""
        result = {'passed': True, 'warnings': [], 'errors': []}
        
        # Check if there are image files in the file field (excluding thumbnails)
        file_field = fields.get('file', '')
        has_non_thumbnail_image_files = False
        
        for part in file_field.split(';'):
            part = part.strip()
            if part and any(f'image/{ext}' in part for ext in ['jpeg', 'jpg', 'png', 'gif']):
                # Check if this is a thumbnail file
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
                
                if not is_thumbnail:
                    has_non_thumbnail_image_files = True
                    break
        
        if has_non_thumbnail_image_files:
            # If there are non-thumbnail image files, check if they've been processed
            has_photos_field = 'photos' in fields and fields['photos'].strip()
            has_figures_field = 'figures' in fields and fields['figures'].strip()
            
            if not has_photos_field and not has_figures_field:
                result['passed'] = False
                result['errors'].append("Image files found but no photos/figures fields added")
            
            # Check if file field still contains image entries (should be cleaned, except thumbnails)
            remaining_image_entries = []
            for part in file_field.split(';'):
                part = part.strip()
                if part and any(f'image/{ext}' in part for ext in ['jpeg', 'jpg', 'png', 'gif']):
                    # Check if this is a thumbnail file
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
                    
                    if not is_thumbnail:
                        remaining_image_entries.append(part)
            
            # Check if remaining image entries are properly formatted with descriptive filenames
            for entry in remaining_image_entries:
                if ':' in entry:
                    parts = entry.split(':')
                    if len(parts) >= 2:
                        path_part = parts[1].strip()
                        if '/Users/' in path_part or '/Documents/' in path_part:
                            # Still using original storage path - should be updated
                            result['passed'] = False
                            result['errors'].append(f"File field contains unprocessed image with original path: {entry}")
                        elif '/assets/' not in path_part:
                            # Not using assets path - should be updated
                            result['passed'] = False
                            result['errors'].append(f"File field contains image without proper assets path: {entry}")
                else:
                    # No colon format - should be updated to descriptive format
                    result['passed'] = False
                    result['errors'].append(f"File field contains image without proper format: {entry}")
        
        return result
    
    def _validate_file_field(self, citation_key: str, fields: Dict, entry_content: str) -> Dict:
        """Validate file field processing with descriptive filenames."""
        result = {'passed': True, 'warnings': [], 'errors': []}
        
        file_field = fields.get('file', '')
        if not file_field:
            return result
        
        # Check if file field contains properly formatted image entries
        file_parts = file_field.split(';')
        for part in file_parts:
            part = part.strip()
            if part and any(f'image/{ext}' in part for ext in ['jpeg', 'jpg', 'png', 'gif']):
                # Check if this is properly formatted with descriptive filename
                if ':' in part:
                    parts = part.split(':')
                    if len(parts) >= 2:
                        path_part = parts[1].strip()
                        if '/Users/' in path_part or '/Documents/' in path_part:
                            # Still using original storage path - should be updated
                            result['passed'] = False
                            result['errors'].append(f"File field contains unprocessed image with original path: {part}")
                        elif '/assets/' not in path_part:
                            # Not using assets path - should be updated
                            result['passed'] = False
                            result['errors'].append(f"File field contains image without proper assets path: {part}")
                else:
                    # No colon format - should be updated to descriptive format
                    result['passed'] = False
                    result['errors'].append(f"File field contains image without proper format: {part}")
        
        return result
    
    def _validate_preview_field(self, citation_key: str, fields: Dict) -> Dict:
        """Validate preview/thumbnail field."""
        result = {'passed': True, 'warnings': [], 'errors': []}
        
        # Check if entry has files that should have previews
        file_field = fields.get('file', '')
        has_pdf_files = any('application/pdf' in file_field or part.endswith('.pdf') 
                           for part in file_field.split(';') if part.strip())
        
        if has_pdf_files:
            preview_field = fields.get('preview', '')
            if not preview_field:
                result['passed'] = False
                result['errors'].append("PDF files found but no preview field added")
            else:
                # Check if preview file exists
                preview_path = os.path.join(self.config.PREVIEW_DIR, preview_field)
                if not os.path.exists(preview_path):
                    result['passed'] = False
                    result['errors'].append(f"Preview file not found: {preview_field}")
        
        return result
    
    def _validate_pdf_processing(self, citation_key: str, fields: Dict) -> Dict:
        """Validate PDF processing completeness."""
        result = {'passed': True, 'warnings': [], 'errors': []}
        
        # Check if entry has PDF files
        file_field = fields.get('file', '')
        has_pdf_files = any('application/pdf' in file_field or part.endswith('.pdf') 
                           for part in file_field.split(';') if part.strip())
        
        if has_pdf_files:
            # Check if PDF field was added
            pdf_field = fields.get('pdf', '')
            if not pdf_field:
                result['passed'] = False
                result['errors'].append("PDF files found but no pdf field added")
            else:
                # Check if PDF file exists
                pdf_path = os.path.join(self.config.PDF_DIR, pdf_field)
                if not os.path.exists(pdf_path):
                    result['passed'] = False
                    result['errors'].append(f"PDF file not found: {pdf_field}")
        
        return result
    
    def _validate_url_fields(self, citation_key: str, fields: Dict) -> Dict:
        """Validate URL field renaming."""
        result = {'passed': True, 'warnings': [], 'errors': []}
        
        # Check if url field was renamed to website
        if 'url' in fields:
            result['passed'] = False
            result['errors'].append("URL field not renamed to website")
        
        # Check if urldate field was renamed to website_date
        if 'urldate' in fields:
            result['passed'] = False
            result['errors'].append("urldate field not renamed to website_date")
        
        return result
    
    def _validate_ignore_fields(self, citation_key: str, fields: Dict, entry_content: str) -> Dict:
        """Validate ignore field processing."""
        result = {'passed': True, 'warnings': [], 'errors': []}
        
        # Check if ignore fields are properly processed
        ignore_fields = [key for key in fields.keys() if key.startswith('ignore:')]
        
        for ignore_field in ignore_fields:
            # Check if the field value is properly formatted
            value = fields[ignore_field]
            if not value or value.strip() == '':
                result['warnings'].append(f"Empty ignore field: {ignore_field}")
        
        return result
    
    def _validate_file_renaming(self, citation_key: str, fields: Dict, entry_content: str) -> Dict:
        """Validate file renaming completeness."""
        result = {'passed': True, 'warnings': [], 'errors': []}
        
        # Check if files have been renamed according to naming convention
        file_field = fields.get('file', '')
        if file_field:
            file_parts = file_field.split(';')
            for part in file_parts:
                part = part.strip()
                if ':' in part:
                    parts = part.split(':')
                    if len(parts) >= 2:
                        filename = parts[0].strip()
                        # Check if filename follows expected pattern (not original Zotero names)
                        if self._is_original_zotero_filename(filename):
                            result['warnings'].append(f"File may not be renamed: {filename}")
        
        return result
    
    def _is_original_zotero_filename(self, filename: str) -> bool:
        """Check if filename appears to be an original Zotero filename."""
        # Common patterns for original Zotero filenames
        zotero_patterns = [
            r'^\d+_[a-f0-9]+_[a-z]$',  # e.g., 54439519274_cf052b44d1_k
            r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$',  # UUIDs
            r'^[A-Z0-9]{8}$',  # 8-character alphanumeric codes
        ]
        
        for pattern in zotero_patterns:
            if re.match(pattern, filename):
                return True
        
        return False
    
    def _validate_bibtex_syntax(self, citation_key: str, entry_content: str) -> Dict:
        """Validate BibTeX syntax for common issues like trailing commas."""
        result = {'passed': True, 'warnings': [], 'errors': []}
        
        # Check for trailing commas before closing brace
        if re.search(r',\s*\n\s*}', entry_content):
            result['passed'] = False
            result['errors'].append("Trailing comma before closing brace")
        
        # Check for double commas
        if re.search(r',\s*,', entry_content):
            result['passed'] = False
            result['errors'].append("Double comma found")
        
        # Check for comma at start of line (should be at end of previous line)
        if re.search(r'\n\s*,\s*\w', entry_content):
            result['passed'] = False
            result['errors'].append("Comma at start of line")
        
        # Check for unmatched braces
        open_braces = entry_content.count('{')
        close_braces = entry_content.count('}')
        if open_braces != close_braces:
            result['passed'] = False
            result['errors'].append(f"Unmatched braces: {open_braces} open, {close_braces} close")
        
        return result
    
    def _validate_title_cleaning(self, citation_key: str, fields: Dict) -> Dict:
        """Validate that titles have been properly cleaned of curly braces."""
        result = {'passed': True, 'warnings': [], 'errors': []}
        
        # Check title field
        title = fields.get('title', '')
        if title and re.search(r'\{[^{}]*\}', title):
            result['passed'] = False
            result['errors'].append("Title contains curly braces that should be cleaned")
        
        # Check shorttitle field
        shorttitle = fields.get('shorttitle', '')
        if shorttitle and re.search(r'\{[^{}]*\}', shorttitle):
            result['passed'] = False
            result['errors'].append("Shorttitle contains curly braces that should be cleaned")
        
        # Check booktitle field
        booktitle = fields.get('booktitle', '')
        if booktitle and re.search(r'\{[^{}]*\}', booktitle):
            result['passed'] = False
            result['errors'].append("Booktitle contains curly braces that should be cleaned")
        
        return result
    
    def _fix_entry_issues(self, entry: Dict, text_processor) -> str:
        """Fix common issues in a BibTeX entry."""
        content = entry['content']
        fields = entry['fields']
        
        # Fix 1: Remove trailing commas before closing brace
        content = re.sub(r',\s*\n\s*}', '\n}', content)
        
        # Fix 2: Remove double commas
        content = re.sub(r',\s*,', ',', content)
        
        # Fix 3: Fix comma at start of line (move to end of previous line)
        content = re.sub(r'\n\s*,\s*(\w)', r',\n\t\1', content)
        
        # Fix 4: Clean curly braces from title fields using more robust pattern
        for field_name in ['title', 'shorttitle', 'booktitle']:
            if field_name in fields:
                field_value = fields[field_name]
                if field_value and re.search(r'\{[^{}]*\}', field_value):
                    # Clean the field value
                    cleaned_value = text_processor.clean_nested_braces(field_value)
                    
                    # Use a more robust pattern that handles nested braces properly
                    # Find the field and its value with proper brace matching
                    pattern = rf'({field_name})\s*=\s*\{{'
                    match = re.search(pattern, content)
                    if match:
                        start_pos = match.end() - 1  # Position of opening brace
                        brace_count = 0
                        end_pos = start_pos
                        
                        # Find matching closing brace
                        for i in range(start_pos, len(content)):
                            if content[i] == '{':
                                brace_count += 1
                            elif content[i] == '}':
                                brace_count -= 1
                                if brace_count == 0:
                                    end_pos = i
                                    break
                        
                        if brace_count == 0:  # Found matching closing brace
                            # Replace the field value
                            content = content[:start_pos + 1] + cleaned_value + content[end_pos:]
        
        return content
    
    def _print_validation_summary(self) -> None:
        """Print validation summary."""
        total = self.validation_results['total_entries']
        passed = self.validation_results['passed_entries']
        failed = self.validation_results['failed_entries']
        warnings = len(self.validation_results['warnings'])
        errors = len(self.validation_results['errors'])
        
        print(f"\n📊 Validation Summary:")
        print(f"  Total entries: {total}")
        print(f"  Passed: {passed}")
        print(f"  Failed: {failed}")
        print(f"  Warnings: {warnings}")
        print(f"  Errors: {errors}")
        
        if warnings > 0:
            print(f"\n⚠️  Warnings:")
            for warning in self.validation_results['warnings'][:10]:  # Show first 10
                print(f"    {warning}")
            if warnings > 10:
                print(f"    ... and {warnings - 10} more warnings")
        
        if errors > 0:
            print(f"\n❌ Errors:")
            for error in self.validation_results['errors'][:10]:  # Show first 10
                print(f"    {error}")
            if errors > 10:
                print(f"    ... and {errors - 10} more errors")
        
        if failed == 0:
            print(f"\n✅ All validation checks passed!")
        else:
            print(f"\n❌ {failed} entries failed validation")
    
    def get_validation_summary(self) -> Dict:
        """Get validation summary as dictionary."""
        return {
            'total_entries': self.validation_results['total_entries'],
            'passed_entries': self.validation_results['passed_entries'],
            'failed_entries': self.validation_results['failed_entries'],
            'warning_count': len(self.validation_results['warnings']),
            'error_count': len(self.validation_results['errors']),
            'all_passed': self.validation_results['failed_entries'] == 0
        }
