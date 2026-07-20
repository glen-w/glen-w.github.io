#!/usr/bin/env python3
"""
EnhancedValidator class for process_papers.py
Comprehensive validation checks for common BibTeX issues and processing problems.
"""

import os
import re
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from processing.config import Configuration


class EnhancedValidator:
    """Comprehensive validation for BibTeX files with detailed error reporting."""
    
    def __init__(self, config: Configuration = None):
        """Initialize with configuration."""
        self.config = config or Configuration()
        self.validation_results = {
            'total_entries': 0,
            'passed_entries': 0,
            'failed_entries': 0,
            'warnings': [],
            'errors': [],
            'issues_by_type': {
                'trailing_commas': [],
                'double_commas': [],
                'internal_braces': [],
                'uncleared_file_tags': [],
                'unused_thumbnail_tags': [],
                'unrenamed_files': [],
                'bibtex_syntax': [],
                'unmatched_braces': [],
                'malformed_entries': []
            }
        }
    
    def validate_bibtex_file(self, bibtex_file: str) -> Dict:
        """
        Validate a BibTeX file for all common issues.
        
        Args:
            bibtex_file: Path to the BibTeX file to validate
            
        Returns:
            Dictionary with comprehensive validation results
        """
        print("\n🔍 Running enhanced validation checks...")
        
        # Reset results
        self.validation_results = {
            'total_entries': 0,
            'passed_entries': 0,
            'failed_entries': 0,
            'warnings': [],
            'errors': [],
            'issues_by_type': {
                'trailing_commas': [],
                'double_commas': [],
                'internal_braces': [],
                'uncleared_file_tags': [],
                'unused_thumbnail_tags': [],
                'unrenamed_files': [],
                'bibtex_syntax': [],
                'unmatched_braces': [],
                'malformed_entries': []
            }
        }
        
        # Read and parse the BibTeX file
        try:
            with open(bibtex_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.validation_results['errors'].append(f"Failed to read BibTeX file: {e}")
            return self.validation_results
        
        # Parse entries
        from processing.core.bibtex_processor import BibTeXProcessor
        processor = BibTeXProcessor(self.config)
        entries = processor.parse_bibtex_entries(content)

        self.validation_results['total_entries'] = len(entries)

        # Non-empty file that parses to zero entries is a hard failure
        if content.strip() and len(entries) == 0:
            msg = "Failed to parse any BibTeX entries from non-empty file"
            self.validation_results['errors'].append(msg)
            self.validation_results['issues_by_type']['malformed_entries'].append(msg)
            self.validation_results['failed_entries'] = 1
            self.validation_results['all_passed'] = False
            self._print_enhanced_validation_summary()
            return self.validation_results

        # Validate each entry
        for entry in entries:
            self._validate_single_entry_enhanced(entry)

        # Add all_passed key
        self.validation_results['all_passed'] = self.validation_results['failed_entries'] == 0
        
        # Print summary
        self._print_enhanced_validation_summary()
        
        return self.validation_results
    
    def _validate_single_entry_enhanced(self, entry: Dict) -> None:
        """Enhanced validation for a single BibTeX entry."""
        citation_key = entry.get('citation_key', 'unknown')
        fields = entry.get('fields', {})
        entry_content = entry.get('content', '')
        
        entry_passed = True
        entry_errors = []
        entry_warnings = []
        
        # Check 1: Trailing commas
        trailing_comma_issues = self._check_trailing_commas(citation_key, entry_content)
        if trailing_comma_issues:
            entry_passed = False
            entry_errors.extend(trailing_comma_issues)
            self.validation_results['issues_by_type']['trailing_commas'].extend(trailing_comma_issues)
        
        # Check 2: Double commas
        double_comma_issues = self._check_double_commas(citation_key, entry_content)
        if double_comma_issues:
            entry_passed = False
            entry_errors.extend(double_comma_issues)
            self.validation_results['issues_by_type']['double_commas'].extend(double_comma_issues)
        
        # Check 3: Internal braces in fields
        internal_brace_issues = self._check_internal_braces(citation_key, fields)
        if internal_brace_issues:
            entry_passed = False
            entry_errors.extend(internal_brace_issues)
            self.validation_results['issues_by_type']['internal_braces'].extend(internal_brace_issues)
        
        # Check 4: Uncleared file tags
        uncleared_file_issues = self._check_uncleared_file_tags(citation_key, fields, entry_content)
        if uncleared_file_issues:
            entry_passed = False
            entry_errors.extend(uncleared_file_issues)
            self.validation_results['issues_by_type']['uncleared_file_tags'].extend(uncleared_file_issues)
        
        # Check 5: Unused thumbnail tags
        unused_thumbnail_issues = self._check_unused_thumbnail_tags(citation_key, fields)
        if unused_thumbnail_issues:
            entry_passed = False
            entry_errors.extend(unused_thumbnail_issues)
            self.validation_results['issues_by_type']['unused_thumbnail_tags'].extend(unused_thumbnail_issues)
        
        # Check 6: Unrenamed files
        unrenamed_file_issues = self._check_unrenamed_files(citation_key, fields)
        if unrenamed_file_issues:
            entry_passed = False
            entry_errors.extend(unrenamed_file_issues)
            self.validation_results['issues_by_type']['unrenamed_files'].extend(unrenamed_file_issues)
        
        # Check 7: BibTeX syntax issues
        syntax_issues = self._check_bibtex_syntax(citation_key, entry_content)
        if syntax_issues:
            entry_passed = False
            entry_errors.extend(syntax_issues)
            self.validation_results['issues_by_type']['bibtex_syntax'].extend(syntax_issues)
        
        # Check 8: Unmatched braces
        unmatched_brace_issues = self._check_unmatched_braces(citation_key, entry_content)
        if unmatched_brace_issues:
            entry_passed = False
            entry_errors.extend(unmatched_brace_issues)
            self.validation_results['issues_by_type']['unmatched_braces'].extend(unmatched_brace_issues)
        
        # Check 9: Malformed entries
        malformed_issues = self._check_malformed_entries(citation_key, entry_content)
        if malformed_issues:
            entry_passed = False
            entry_errors.extend(malformed_issues)
            self.validation_results['issues_by_type']['malformed_entries'].extend(malformed_issues)
        
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
    
    def _check_trailing_commas(self, citation_key: str, content: str) -> List[str]:
        """Check for trailing commas before closing braces."""
        issues = []
        
        # Check for trailing comma before closing brace
        if re.search(r',\s*\n\s*}', content):
            issues.append("Trailing comma before closing brace")
        
        # Check for trailing comma at end of line before closing brace
        if re.search(r',\s*$', content.split('}')[0]):
            issues.append("Trailing comma at end of line before closing brace")
        
        return issues
    
    def _check_double_commas(self, citation_key: str, content: str) -> List[str]:
        """Check for double commas."""
        issues = []
        
        # Check for double commas
        if re.search(r',\s*,', content):
            issues.append("Double comma found")
        
        # Check for comma followed by comma with only whitespace
        if re.search(r',\s*\n\s*,', content):
            issues.append("Comma followed by comma on next line")
        
        return issues
    
    def _check_internal_braces(self, citation_key: str, fields: Dict) -> List[str]:
        """Check for internal braces in fields that should be cleaned."""
        issues = []
        
        # Fields that should not have internal braces
        fields_to_check = ['title', 'shorttitle', 'booktitle', 'journal', 'publisher']
        
        for field_name in fields_to_check:
            if field_name in fields:
                field_value = fields[field_name]
                # Check for internal braces (but not at the start/end)
                if re.search(r'\{[^{}]*\}', field_value):
                    # Check if it's not just the outer braces
                    inner_content = field_value[1:-1] if field_value.startswith('{') and field_value.endswith('}') else field_value
                    if re.search(r'\{[^{}]*\}', inner_content):
                        issues.append(f"Field '{field_name}' contains internal braces that should be cleaned")
        
        return issues
    
    def _check_uncleared_file_tags(self, citation_key: str, fields: Dict, content: str) -> List[str]:
        """Check for proper file field formatting with descriptive filenames."""
        issues = []
        
        # Check if file field contains properly formatted image entries
        file_field = fields.get('file', '')
        if file_field:
            for part in file_field.split(';'):
                part = part.strip()
                if part and any(f':image/{ext}' in part for ext in ['jpeg', 'jpg', 'png', 'gif']):
                    # Check if this is properly formatted with descriptive filename
                    if ':' in part:
                        parts = part.split(':')
                        if len(parts) >= 2:
                            description = parts[0].strip().lower()
                            path_part = parts[1].strip()
                            
                            # Check if the path contains descriptive filename (not just generic names)
                            if '/assets/' in path_part:
                                # This is properly formatted with assets path
                                continue
                            elif '/Users/' in path_part or '/Documents/' in path_part:
                                # This is still using original storage path - should be updated
                                issues.append(f"File field contains unprocessed image with original path: {part}")
                            else:
                                # Generic filename without proper path
                                issues.append(f"File field contains image with generic filename: {part}")
                    else:
                        # No colon format - should be updated to descriptive format
                        issues.append(f"File field contains image without proper format: {part}")
        
        return issues
    
    def _check_unused_thumbnail_tags(self, citation_key: str, fields: Dict) -> List[str]:
        """Check for unused thumbnail tags."""
        issues = []
        
        # Check if preview field exists but no corresponding file
        if 'preview' in fields:
            preview_filename = fields['preview']
            preview_path = os.path.join(self.config.PREVIEW_DIR, preview_filename)
            if not os.path.exists(preview_path):
                issues.append(f"Preview file not found: {preview_filename}")
        
        # Check if preview field exists but no PDF or image files to preview
        # Note: Preview fields can exist without PDFs when they come from thumbnail files
        # This is a valid case, so we don't flag it as an error
        
        return issues
    
    def _check_unrenamed_files(self, citation_key: str, fields: Dict) -> List[str]:
        """Check for unrenamed files that still have original Zotero names."""
        issues = []
        
        # Check PDF files
        if 'pdf' in fields:
            pdf_filename = fields['pdf']
            if self._is_original_zotero_filename(pdf_filename):
                issues.append(f"PDF file not renamed: {pdf_filename}")
        
        # Check image files
        for field_name in ['photos', 'figures']:
            if field_name in fields:
                files = fields[field_name].split(', ')
                for filename in files:
                    if self._is_original_zotero_filename(filename):
                        issues.append(f"{field_name} file not renamed: {filename}")
        
        # Check preview files
        if 'preview' in fields:
            preview_filename = fields['preview']
            if self._is_original_zotero_filename(preview_filename):
                issues.append(f"Preview file not renamed: {preview_filename}")
        
        return issues
    
    def _check_bibtex_syntax(self, citation_key: str, content: str) -> List[str]:
        """Check for BibTeX syntax issues."""
        issues = []
        
        # Check for comma at start of line (should be at end of previous line)
        if re.search(r'\n\s*,\s*\w', content):
            issues.append("Comma at start of line")
        
        # Check for missing comma between fields
        if re.search(r'}\s*\w+\s*=', content):
            issues.append("Missing comma between fields")
        
        # Check for invalid characters in citation key
        if not re.match(r'^[a-zA-Z0-9_:-]+$', citation_key):
            issues.append(f"Invalid characters in citation key: {citation_key}")
        
        return issues
    
    def _check_unmatched_braces(self, citation_key: str, content: str) -> List[str]:
        """Check for unmatched braces."""
        issues = []
        
        open_braces = content.count('{')
        close_braces = content.count('}')
        if open_braces != close_braces:
            issues.append(f"Unmatched braces: {open_braces} open, {close_braces} close")
        
        return issues
    
    def _check_malformed_entries(self, citation_key: str, content: str) -> List[str]:
        """Check for malformed entries."""
        issues = []
        
        # Check for missing entry type
        if not re.match(r'@\w+\s*\{', content):
            issues.append("Missing or invalid entry type")
        
        # Check for missing citation key
        if not re.search(r'@\w+\s*\{\s*[^,\s\n]+\s*,', content):
            issues.append("Missing citation key")
        
        # Check for missing opening brace
        if not re.search(r'@\w+\s*\{', content):
            issues.append("Missing opening brace")
        
        # Check for missing closing brace by counting braces
        open_braces = content.count('{')
        close_braces = content.count('}')
        if open_braces != close_braces:
            issues.append("Missing closing brace")
        
        return issues
    
    def _is_original_zotero_filename(self, filename: str) -> bool:
        """Check if filename appears to be an original Zotero filename."""
        # Remove file extension for pattern matching
        base_name = filename
        if '.' in filename:
            base_name = filename.rsplit('.', 1)[0]
        
        # Common patterns for original Zotero filenames
        zotero_patterns = [
            r'^\d+_[a-f0-9]+_[a-z]$',  # e.g., 54439519274_cf052b44d1_k
            r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$',  # UUIDs
            r'^[A-Z0-9]{8}$',  # 8-character alphanumeric codes
            r'^[a-f0-9]{8}$',  # 8-character hex codes
        ]
        
        for pattern in zotero_patterns:
            if re.match(pattern, base_name):
                return True
        
        return False
    
    def _print_enhanced_validation_summary(self) -> None:
        """Print enhanced validation summary with detailed issue breakdown."""
        total = self.validation_results['total_entries']
        passed = self.validation_results['passed_entries']
        failed = self.validation_results['failed_entries']
        warnings = len(self.validation_results['warnings'])
        errors = len(self.validation_results['errors'])
        
        print(f"\n📊 Enhanced Validation Summary:")
        print(f"  Total entries: {total}")
        print(f"  Passed: {passed}")
        print(f"  Failed: {failed}")
        print(f"  Warnings: {warnings}")
        print(f"  Errors: {errors}")
        
        # Print detailed issue breakdown
        issues_by_type = self.validation_results['issues_by_type']
        for issue_type, issues in issues_by_type.items():
            if issues:
                print(f"\n🔍 {issue_type.replace('_', ' ').title()}: {len(issues)} issues")
                for issue in issues[:5]:  # Show first 5
                    print(f"    {issue}")
                if len(issues) > 5:
                    print(f"    ... and {len(issues) - 5} more")
        
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
            'all_passed': self.validation_results['failed_entries'] == 0,
            'issues_by_type': self.validation_results['issues_by_type']
        }


def main():
    """Command-line interface for enhanced validation."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced BibTeX validation')
    parser.add_argument('bibtex_file', help='Path to BibTeX file to validate')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    validator = EnhancedValidator()
    results = validator.validate_bibtex_file(args.bibtex_file)
    
    summary = validator.get_validation_summary()
    if not summary['all_passed']:
        exit(1)


if __name__ == "__main__":
    main()
