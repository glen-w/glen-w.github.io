#!/usr/bin/env python3
"""
Comprehensive BibTeX Fixer for process_papers.py
Fixes all common BibTeX issues with a more robust approach.
"""

import re
import os
from typing import Dict, List, Optional
from config import Configuration
from text_processor import TextProcessor


class ComprehensiveBibTeXFixer:
    """Comprehensive fixer for all BibTeX issues."""
    
    def __init__(self, config: Configuration = None):
        """Initialize with configuration."""
        self.config = config or Configuration()
        self.text_processor = TextProcessor(config)
    
    def fix_bibtex_file(self, bibtex_file: str) -> bool:
        """
        Fix all common issues in a BibTeX file.
        
        Args:
            bibtex_file: Path to the BibTeX file to fix
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Read the file
            with open(bibtex_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"🔧 Comprehensively fixing issues in {bibtex_file}...")
            
            # Step 1: Fix missing commas after citation keys
            content = self._fix_missing_commas_after_citation_keys(content)
            
            # Step 2: Fix internal braces in all fields
            content = self._fix_all_internal_braces(content)
            
            # Step 3: Fix unmatched braces
            content = self._fix_unmatched_braces(content)
            
            # Step 4: Fix trailing commas
            content = self._fix_trailing_commas(content)
            
            # Step 5: Fix double commas
            content = self._fix_double_commas(content)
            
            # Step 6: Fix other syntax issues
            content = self._fix_other_syntax_issues(content)
            
            # Write the fixed content back
            with open(bibtex_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Successfully fixed {bibtex_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error fixing {bibtex_file}: {e}")
            return False
    
    def _fix_missing_commas_after_citation_keys(self, content: str) -> str:
        """Fix missing commas after citation keys."""
        print("  🔧 Fixing missing commas after citation keys...")
        
        # Pattern to match @type{key without comma
        pattern = r'@(\w+)\{([^,\n]+)\s*\n'
        
        def add_comma(match):
            entry_type = match.group(1)
            citation_key = match.group(2).strip()
            return f"@{entry_type}{{{citation_key}}},\n"
        
        content = re.sub(pattern, add_comma, content)
        return content
    
    def _fix_all_internal_braces(self, content: str) -> str:
        """Fix internal braces in all fields comprehensively."""
        print("  🔧 Fixing all internal braces...")
        
        # Fields that should have internal braces cleaned
        fields_to_clean = ['title', 'shorttitle', 'booktitle', 'journal', 'publisher']
        
        for field_name in fields_to_clean:
            # More comprehensive pattern that handles multiple internal braces
            pattern = r'(' + re.escape(field_name) + r'\s*=\s*)\{([^{}]*\{[^{}]*\}[^{}]*)\}'
            
            def clean_field_value(match):
                field_declaration = match.group(1)
                field_value = match.group(2)
                
                # Clean internal braces from the value
                cleaned_value = self.text_processor.clean_nested_braces(field_value)
                
                return f"{field_declaration}{{{cleaned_value}}}"
            
            # Apply the fix multiple times to handle nested braces
            old_content = ""
            while old_content != content:
                old_content = content
                content = re.sub(pattern, clean_field_value, content)
        
        return content
    
    def _fix_unmatched_braces(self, content: str) -> str:
        """Fix unmatched braces in entries."""
        print("  🔧 Fixing unmatched braces...")
        
        # Split into entries and fix each one
        entries = self._split_into_entries(content)
        fixed_entries = []
        
        for entry in entries:
            if entry.strip():
                fixed_entry = self._fix_entry_braces(entry)
                fixed_entries.append(fixed_entry)
        
        return '\n\n'.join(fixed_entries)
    
    def _fix_entry_braces(self, entry: str) -> str:
        """Fix braces in a single entry."""
        # Count braces
        open_braces = entry.count('{')
        close_braces = entry.count('}')
        
        if open_braces == close_braces:
            return entry  # Already balanced
        
        if open_braces > close_braces:
            # Missing closing braces
            missing = open_braces - close_braces
            # Add missing closing braces at the end
            entry = entry.rstrip() + '}' * missing
        else:
            # Too many closing braces - this is less common but possible
            extra = close_braces - open_braces
            # Remove extra closing braces from the end
            for _ in range(extra):
                entry = entry.rstrip()
                if entry.endswith('}'):
                    entry = entry[:-1]
        
        return entry
    
    def _fix_trailing_commas(self, content: str) -> str:
        """Fix trailing commas before closing braces."""
        print("  🔧 Fixing trailing commas...")
        
        # Remove trailing comma before closing brace
        content = re.sub(r',\s*\n\s*}', '\n}', content)
        
        # Remove trailing comma at end of line before closing brace
        content = re.sub(r',\s*$', '', content, flags=re.MULTILINE)
        
        return content
    
    def _fix_double_commas(self, content: str) -> str:
        """Fix double commas."""
        print("  🔧 Fixing double commas...")
        
        # Fix double commas
        content = re.sub(r',\s*,', ',', content)
        
        # Fix comma followed by comma on next line
        content = re.sub(r',\s*\n\s*,', ',', content)
        
        return content
    
    def _fix_other_syntax_issues(self, content: str) -> str:
        """Fix other syntax issues."""
        print("  🔧 Fixing other syntax issues...")
        
        # Fix missing commas between fields
        content = re.sub(r'}\s*(\w+\s*=)', r'},\n\t\1', content)
        
        # Fix comma at start of line
        content = re.sub(r'\n\s*,\s*(\w)', r',\n\t\1', content)
        
        return content
    
    def _split_into_entries(self, content: str) -> List[str]:
        """Split BibTeX content into individual entries."""
        entries = []
        current_entry = []
        brace_count = 0
        in_entry = False
        
        for line in content.split('\n'):
            if line.strip().startswith('@'):
                # Start of new entry
                if current_entry and in_entry:
                    entries.append('\n'.join(current_entry))
                current_entry = [line]
                in_entry = True
                # Count braces in this line
                brace_count = line.count('{') - line.count('}')
            elif in_entry:
                current_entry.append(line)
                brace_count += line.count('{') - line.count('}')
                if brace_count == 0:
                    # Entry is complete
                    entries.append('\n'.join(current_entry))
                    current_entry = []
                    in_entry = False
        
        # Add the last entry if exists
        if current_entry and in_entry:
            entries.append('\n'.join(current_entry))
        
        return entries


def main():
    """Command-line interface for comprehensive BibTeX fixing."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Comprehensively fix BibTeX issues')
    parser.add_argument('bibtex_file', help='Path to BibTeX file to fix')
    
    args = parser.parse_args()
    
    fixer = ComprehensiveBibTeXFixer()
    success = fixer.fix_bibtex_file(args.bibtex_file)
    
    if not success:
        exit(1)


if __name__ == "__main__":
    main()
