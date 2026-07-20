#!/usr/bin/env python3
"""
SimpleValidator module for process_papers.py
Provides focused validation without tight coupling to processing logic.
"""

import os
import re
from typing import Dict, List, Optional
from processing.config import Configuration


class SimpleValidator:
    """Provides focused validation without tight coupling to processing logic."""
    
    def __init__(self, config: Configuration = None):
        """Initialize with configuration."""
        self.config = config or Configuration()
    
    def validate_bibtex_file(self, bibtex_file: str) -> Dict:
        """
        Validate a BibTeX file for basic issues.
        
        Args:
            bibtex_file: Path to the BibTeX file to validate
            
        Returns:
            Dictionary with validation results
        """
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'total_entries': 0,
            'failed_entries': 0
        }
        
        try:
            with open(bibtex_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            results['valid'] = False
            results['errors'].append(f"Failed to read file: {e}")
            return results
        
        # Parse entries using simple regex
        entries = self._parse_entries_simple(content)
        results['total_entries'] = len(entries)
        
        # Validate each entry
        for entry in entries:
            entry_errors = self._validate_entry_simple(entry)
            if entry_errors:
                results['failed_entries'] += 1
                results['errors'].extend(entry_errors)
        
        # Overall validation status
        results['valid'] = len(results['errors']) == 0
        
        return results
    
    def validate_after_processing(self, bibtex_file: str) -> Dict:
        """
        Validate a BibTeX file after processing to check for common issues.
        
        Args:
            bibtex_file: Path to the BibTeX file to validate
            
        Returns:
            Dictionary with validation results
        """
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'total_entries': 0,
            'failed_entries': 0
        }
        
        try:
            with open(bibtex_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            results['valid'] = False
            results['errors'].append(f"Failed to read file: {e}")
            return results
        
        # Parse entries
        entries = self._parse_entries_simple(content)
        results['total_entries'] = len(entries)
        
        # Validate each entry
        for entry in entries:
            entry_errors = self._validate_processed_entry(entry)
            if entry_errors:
                results['failed_entries'] += 1
                results['errors'].extend(entry_errors)
        
        # Overall validation status
        results['valid'] = len(results['errors']) == 0
        
        return results
    
    def _parse_entries_simple(self, content: str) -> List[Dict]:
        """Parse BibTeX entries using simple regex."""
        entries = []
        
        # Find all @type{key, ... } entries with proper brace matching
        pattern = r'@(\w+)\s*\{\s*([^,]+)\s*,'
        
        # Find all matches
        matches = list(re.finditer(pattern, content))
        
        for i, match in enumerate(matches):
            entry_type = match.group(1)
            citation_key = match.group(2).strip()
            
            # Find the start of the fields (after the comma)
            start_pos = match.end()
            
            # Find the matching closing brace
            brace_count = 1  # We already have one opening brace
            end_pos = start_pos
            
            for j in range(start_pos, len(content)):
                if content[j] == '{':
                    brace_count += 1
                elif content[j] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_pos = j
                        break
            
            if brace_count == 0:  # Found matching closing brace
                # Extract the full entry content
                full_content = content[match.start():end_pos + 1]
                
                # Extract fields content (everything between the comma and the closing brace)
                fields_content = content[start_pos:end_pos]
                
                # Parse fields
                fields = self._parse_fields_simple(fields_content)
                
                entries.append({
                    'type': entry_type,
                    'citation_key': citation_key,
                    'fields': fields,
                    'content': full_content
                })
        
        return entries
    
    def _parse_fields_simple(self, fields_content: str) -> Dict:
        """Parse fields from BibTeX entry content."""
        fields = {}
        
        # Simple field parsing - look for field = value patterns
        field_pattern = r'(\w+)\s*=\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
        matches = re.findall(field_pattern, fields_content)
        
        for field_name, field_value in matches:
            fields[field_name] = field_value.strip()
        
        return fields
    
    def _validate_entry_simple(self, entry: Dict) -> List[str]:
        """Validate a single entry for basic issues."""
        errors = []
        citation_key = entry['citation_key']
        fields = entry['fields']
        
        # Check for trailing commas
        content = entry['content']
        if re.search(r',\s*\n\s*}', content):
            errors.append(f"{citation_key}: Trailing comma before closing brace")
        
        # Check for double commas
        if re.search(r',\s*,', content):
            errors.append(f"{citation_key}: Double comma found")
        
        # Check for unmatched braces
        open_braces = content.count('{')
        close_braces = content.count('}')
        if open_braces != close_braces:
            errors.append(f"{citation_key}: Unmatched braces: {open_braces} open, {close_braces} close")
        
        return errors
    
    def _validate_processed_entry(self, entry: Dict) -> List[str]:
        """Validate a processed entry for common issues."""
        errors = []
        citation_key = entry['citation_key']
        fields = entry['fields']
        
        # Check for basic syntax issues
        basic_errors = self._validate_entry_simple(entry)
        errors.extend(basic_errors)
        
        # Check for file field issues
        file_field = fields.get('file', '')
        if file_field:
            # Check if file field contains properly formatted image entries
            for part in file_field.split(';'):
                part = part.strip()
                if part and any(f':image/{ext}' in part for ext in ['jpeg', 'jpg', 'png', 'gif']):
                    # Check if this is properly formatted with descriptive filename
                    if ':' in part:
                        parts = part.split(':')
                        if len(parts) >= 2:
                            path_part = parts[1].strip()
                            if '/Users/' in path_part or '/Documents/' in path_part:
                                # Still using original storage path - should be updated
                                errors.append(f"{citation_key}: File field contains unprocessed image with original path: {part}")
                            elif '/assets/' not in path_part:
                                # Not using assets path - should be updated
                                errors.append(f"{citation_key}: File field contains image without proper assets path: {part}")
                    else:
                        # No colon format - should be updated to descriptive format
                        errors.append(f"{citation_key}: File field contains image without proper format: {part}")
        
        return errors
    
    def print_validation_summary(self, results: Dict) -> None:
        """Print validation summary."""
        total = results['total_entries']
        failed = results['failed_entries']
        errors = len(results['errors'])
        warnings = len(results['warnings'])
        
        print(f"\n📊 Validation Summary:")
        print(f"  Total entries: {total}")
        print(f"  Failed entries: {failed}")
        print(f"  Errors: {errors}")
        print(f"  Warnings: {warnings}")
        
        if errors > 0:
            print(f"\n❌ Errors:")
            for error in results['errors'][:10]:  # Show first 10
                print(f"    {error}")
            if errors > 10:
                print(f"    ... and {errors - 10} more errors")
        
        if warnings > 0:
            print(f"\n⚠️  Warnings:")
            for warning in results['warnings'][:10]:  # Show first 10
                print(f"    {warning}")
            if warnings > 10:
                print(f"    ... and {warnings - 10} more warnings")
        
        if results['valid']:
            print(f"\n✅ All validation checks passed!")
        else:
            print(f"\n❌ Validation failed with {failed} failed entries")


def main():
    """Command-line interface for simple validation."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple BibTeX validation')
    parser.add_argument('bibtex_file', help='Path to BibTeX file to validate')
    parser.add_argument('--after-processing', action='store_true',
                       help='Validate after processing (check for common issues)')
    
    args = parser.parse_args()
    
    validator = SimpleValidator()
    
    if args.after_processing:
        results = validator.validate_after_processing(args.bibtex_file)
    else:
        results = validator.validate_bibtex_file(args.bibtex_file)
    
    validator.print_validation_summary(results)
    
    if not results['valid']:
        exit(1)


if __name__ == "__main__":
    main()
