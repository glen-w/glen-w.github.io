#!/usr/bin/env python3
"""
Final BibTeX Fixer for process_papers.py
Fixes all remaining issues comprehensively.
"""

import re
import os
from typing import Dict, List, Optional
from config import Configuration
from text_processor import TextProcessor


class FinalBibTeXFixer:
    """Final comprehensive fixer for all BibTeX issues."""
    
    def __init__(self, config: Configuration = None):
        """Initialize with configuration."""
        self.config = config or Configuration()
        self.text_processor = TextProcessor(config)
    
    def fix_all_issues(self, bibtex_file: str) -> bool:
        """Fix all remaining issues."""
        try:
            # Read the file
            with open(bibtex_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"🔧 Fixing all remaining issues in {bibtex_file}...")
            
            # Step 1: Fix trailing commas
            content = self._fix_trailing_commas(content)
            
            # Step 2: Fix remaining internal braces
            content = self._fix_remaining_internal_braces(content)
            
            # Step 3: Fix uncleared file tags
            content = self._fix_uncleared_file_tags(content)
            
            # Write the fixed content back
            with open(bibtex_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Successfully fixed all issues in {bibtex_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error fixing {bibtex_file}: {e}")
            return False
    
    def _fix_trailing_commas(self, content: str) -> str:
        """Fix trailing commas before closing braces."""
        print("  🔧 Fixing trailing commas...")
        
        # Remove trailing comma before closing brace
        content = re.sub(r',\s*\n\s*}', '\n}', content)
        
        return content
    
    def _fix_remaining_internal_braces(self, content: str) -> str:
        """Fix remaining internal braces in titles."""
        print("  🔧 Fixing remaining internal braces...")
        
        # More aggressive pattern for titles with internal braces
        pattern = r'(\btitle\s*=\s*)\{([^{}]*\{[^{}]*\}[^{}]*)\}'
        
        def clean_title(match):
            field_decl = match.group(1)
            field_value = match.group(2)
            
            # Clean all internal braces
            cleaned = self.text_processor.clean_nested_braces(field_value)
            
            return f'{field_decl}{{{cleaned}}}'
        
        # Apply multiple times to handle nested braces
        old_content = ""
        while old_content != content:
            old_content = content
            content = re.sub(pattern, clean_title, content)
        
        return content
    
    def _fix_uncleared_file_tags(self, content: str) -> str:
        """Fix uncleared file tags."""
        print("  🔧 Fixing uncleared file tags...")
        
        # Pattern to match file field with image entries
        pattern = r'(\bfile\s*=\s*\{[^}]*)([^;]*\.jpg:[^;]*)([^}]*\})'
        
        def clean_file_field(match):
            before = match.group(1)
            image_entry = match.group(2)
            after = match.group(3)
            
            # Check if this is a thumbnail (keep thumbnails)
            if 'thumbnail' in image_entry.lower():
                return match.group(0)  # Keep as is
            
            # Remove the image entry
            return before + after
        
        content = re.sub(pattern, clean_file_field, content)
        
        return content


def main():
    """Command-line interface for final fixing."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Final BibTeX fixing')
    parser.add_argument('bibtex_file', help='Path to BibTeX file to fix')
    
    args = parser.parse_args()
    
    fixer = FinalBibTeXFixer()
    success = fixer.fix_all_issues(args.bibtex_file)
    
    if not success:
        exit(1)


if __name__ == "__main__":
    main()
