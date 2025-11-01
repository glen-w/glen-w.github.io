#!/usr/bin/env python3
"""
Empty Sections Cleanup Script

This script helps clean up empty sections in BibTeX entries that come from Zotero.
It removes empty [video], [audio], [links], [quotes], [role], [speakers], [type] sections
that contain only whitespace, braces, or brackets.
"""

import re
import sys
from pathlib import Path


def clean_empty_sections(content):
    """
    Clean up empty sections in BibTeX content.
    
    Args:
        content (str): The BibTeX content to clean
        
    Returns:
        str: Cleaned content
    """
    # Define the sections to clean
    sections_to_clean = ['video', 'audio', 'links', 'quotes', 'role', 'speakers', 'type']
    
    for section in sections_to_clean:
        # Pattern to match [section] followed by optional whitespace and closing brace
        # This handles cases like [video]}, [video]\n}, [video] }, etc.
        pattern = rf'\[{section}\]\s*[}}\]]'
        
        # Replace with just the closing brace/bracket
        content = re.sub(pattern, '}', content)
        
        # Also handle cases where there might be newlines
        pattern_multiline = rf'\[{section}\]\s*\n\s*[}}\]]'
        content = re.sub(pattern_multiline, '}', content)
    
    return content


def process_bibtex_file(file_path):
    """
    Process a BibTeX file to clean up empty sections.
    
    Args:
        file_path (str): Path to the BibTeX file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Clean the content
        cleaned_content = clean_empty_sections(content)
        
        # Check if any changes were made
        if content != cleaned_content:
            # Create backup
            backup_path = f"{file_path}.backup"
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Created backup: {backup_path}")
            
            # Write cleaned content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            print(f"Cleaned empty sections in: {file_path}")
        else:
            print(f"No empty sections found in: {file_path}")
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python cleanup_empty_sections.py <bibtex_file>")
        print("Example: python cleanup_empty_sections.py ../_bibliography/papers.bib")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not Path(file_path).exists():
        print(f"Error: File {file_path} does not exist")
        sys.exit(1)
    
    process_bibtex_file(file_path)


if __name__ == "__main__":
    main()
