#!/usr/bin/env python3
"""
Step-by-step BibTeX Fixer for process_papers.py
Fixes issues one at a time with careful validation.
"""

import re
import os
from typing import Dict, List, Optional
from config import Configuration
from text_processor import TextProcessor


class StepByStepFixer:
    """Step-by-step fixer for BibTeX issues."""
    
    def __init__(self, config: Configuration = None):
        """Initialize with configuration."""
        self.config = config or Configuration()
        self.text_processor = TextProcessor(config)
    
    def fix_internal_braces_only(self, bibtex_file: str) -> bool:
        """Fix only internal braces issues."""
        try:
            # Read the file
            with open(bibtex_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"🔧 Fixing internal braces in {bibtex_file}...")
            
            # Fix internal braces in title fields
            content = self._fix_title_internal_braces(content)
            
            # Write the fixed content back
            with open(bibtex_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Successfully fixed internal braces in {bibtex_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error fixing {bibtex_file}: {e}")
            return False
    
    def _fix_title_internal_braces(self, content: str) -> str:
        """Fix internal braces in title fields specifically."""
        # Fields that should have internal braces cleaned
        fields_to_clean = ['title', 'shorttitle', 'booktitle', 'journal', 'publisher']
        
        for field_name in fields_to_clean:
            print(f"    🔧 Cleaning internal braces in {field_name} fields...")
            
            # Find all field declarations
            pattern = r'(' + re.escape(field_name) + r'\s*=\s*)\{([^{}]*\{[^{}]*\}[^{}]*)\}'
            
            def clean_field_value(match):
                field_declaration = match.group(1)
                field_value = match.group(2)
                
                # Clean internal braces from the value
                cleaned_value = self.text_processor.clean_nested_braces(field_value)
                
                return f"{field_declaration}{{{cleaned_value}}}"
            
            # Apply the fix
            content = re.sub(pattern, clean_field_value, content)
        
        return content
    
    def fix_missing_commas_only(self, bibtex_file: str) -> bool:
        """Fix only missing commas after citation keys."""
        try:
            # Read the file
            with open(bibtex_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"🔧 Fixing missing commas in {bibtex_file}...")
            
            # Fix missing commas after citation keys
            content = self._fix_missing_commas_after_citation_keys(content)
            
            # Write the fixed content back
            with open(bibtex_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Successfully fixed missing commas in {bibtex_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error fixing {bibtex_file}: {e}")
            return False
    
    def _fix_missing_commas_after_citation_keys(self, content: str) -> str:
        """Fix missing commas after citation keys."""
        # Pattern to match @type{key without comma followed by newline and field
        pattern = r'@(\w+)\{([^,\n]+)\s*\n\s*(\w+\s*=)'
        
        def add_comma(match):
            entry_type = match.group(1)
            citation_key = match.group(2).strip()
            first_field = match.group(3)
            return f"@{entry_type}{{{citation_key}}},\n\t{first_field}"
        
        content = re.sub(pattern, add_comma, content)
        return content


def main():
    """Command-line interface for step-by-step fixing."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Step-by-step BibTeX fixing')
    parser.add_argument('bibtex_file', help='Path to BibTeX file to fix')
    parser.add_argument('--fix', choices=['internal_braces', 'missing_commas'], 
                       required=True, help='What to fix')
    
    args = parser.parse_args()
    
    fixer = StepByStepFixer()
    
    if args.fix == 'internal_braces':
        success = fixer.fix_internal_braces_only(args.bibtex_file)
    elif args.fix == 'missing_commas':
        success = fixer.fix_missing_commas_only(args.bibtex_file)
    
    if not success:
        exit(1)


if __name__ == "__main__":
    main()
