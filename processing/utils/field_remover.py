#!/usr/bin/env python3
"""
FieldRemover utility for process_papers.py
Simple utility to remove specific fields from BibTeX entries.
"""

import re
import sys
from typing import List


def remove_fields_from_bibtex(bibtex_file: str, field_names: List[str], dry_run: bool = False) -> bool:
    """
    Remove specific fields from all entries in a BibTeX file.
    
    Args:
        bibtex_file: Path to the BibTeX file to process
        field_names: List of field names to remove
        dry_run: If True, only show what would be removed without making changes
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Read the file
        with open(bibtex_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = False
        
        # Remove each field
        for field_name in field_names:
            # More robust pattern that handles complex field values with proper brace matching
            pattern = rf'{re.escape(field_name)}\s*=\s*\{{'
            
            # Find all matches
            matches = list(re.finditer(pattern, content))
            
            if matches:
                if dry_run:
                    print(f"Would remove {len(matches)} instances of field '{field_name}'")
                else:
                    # Remove fields in reverse order to maintain positions
                    for match in reversed(matches):
                        # Find the start of the field
                        start_pos = match.start()
                        
                        # Find the opening brace
                        brace_start = match.end() - 1
                        brace_count = 0
                        end_pos = brace_start
                        
                        # Find matching closing brace
                        for i in range(brace_start, len(content)):
                            if content[i] == '{':
                                brace_count += 1
                            elif content[i] == '}':
                                brace_count -= 1
                                if brace_count == 0:
                                    end_pos = i
                                    break
                        
                        if brace_count == 0:  # Found matching closing brace
                            # Remove the field and its value
                            before_field = content[:start_pos]
                            after_field = content[end_pos + 1:]
                            
                            # Clean up any trailing comma from the field
                            after_field = re.sub(r'^\s*,?\s*', '', after_field)
                            
                            content = before_field + after_field
                            changes_made = True
                    
                    print(f"Removed {len(matches)} instances of field '{field_name}'")
            else:
                print(f"No instances of field '{field_name}' found")
        
        # Clean up any double commas that might be left
        if changes_made:
            content = re.sub(r',\s*,', ',', content)
            
            # Clean up trailing commas before closing brace
            content = re.sub(r',\s*\n\s*}', '\n}', content)
        
        # Write the cleaned content back to file
        if changes_made and not dry_run:
            with open(bibtex_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Successfully updated {bibtex_file}")
            return True
        elif dry_run:
            print("ℹ️  Dry run completed - no changes made")
            return True
        else:
            print("ℹ️  No changes needed")
            return True
            
    except Exception as e:
        print(f"❌ Error processing file: {e}")
        return False


def main():
    """Command-line interface for field removal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Remove fields from BibTeX file')
    parser.add_argument('bibtex_file', help='Path to BibTeX file to process')
    parser.add_argument('--fields', nargs='+', required=True,
                       help='Field names to remove')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be removed without making changes')
    
    args = parser.parse_args()
    
    success = remove_fields_from_bibtex(args.bibtex_file, args.fields, args.dry_run)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
