#!/usr/bin/env python3
"""
Targeted Brace Fixer for process_papers.py
Specifically targets the complex internal braces in titles.
"""

import re
import os
from typing import Dict, List, Optional
from config import Configuration
from text_processor import TextProcessor


class TargetedBraceFixer:
    """Targeted fixer for specific brace issues."""
    
    def __init__(self, config: Configuration = None):
        """Initialize with configuration."""
        self.config = config or Configuration()
        self.text_processor = TextProcessor(config)
    
    def fix_complex_internal_braces(self, bibtex_file: str) -> bool:
        """Fix complex internal braces in titles."""
        try:
            # Read the file
            with open(bibtex_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"🔧 Fixing complex internal braces in {bibtex_file}...")
            
            # Fix the specific patterns we see
            content = self._fix_specific_patterns(content)
            
            # Write the fixed content back
            with open(bibtex_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Successfully fixed complex internal braces in {bibtex_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error fixing {bibtex_file}: {e}")
            return False
    
    def _fix_specific_patterns(self, content: str) -> str:
        """Fix specific patterns we've identified."""
        
        # Pattern 1: {"{The} ship has reached the shore": ...}
        pattern1 = r'(\btitle\s*=\s*)\{\"\{([^}]+)\}\s*([^}]+)\}'
        def fix_pattern1(match):
            field_decl = match.group(1)
            first_part = match.group(2)
            rest = match.group(3)
            return f'{field_decl}{{{first_part} {rest}}}'
        
        content = re.sub(pattern1, fix_pattern1, content)
        
        # Pattern 2: {30x30 target: {Implementation} challenges...}
        pattern2 = r'(\btitle\s*=\s*)\{([^{}]*)\{([^}]+)\}([^{}]*)\}'
        def fix_pattern2(match):
            field_decl = match.group(1)
            before = match.group(2)
            middle = match.group(3)
            after = match.group(4)
            return f'{field_decl}{{{before}{middle}{after}}}'
        
        content = re.sub(pattern2, fix_pattern2, content)
        
        # Pattern 3: {Renewables 2025 {Global} {Status} {Report}: {Global} {Overview}}
        pattern3 = r'(\btitle\s*=\s*)\{([^{}]*)\{([^}]+)\}([^{}]*)\{([^}]+)\}([^{}]*)\{([^}]+)\}([^{}]*)\{([^}]+)\}([^{}]*)\{([^}]+)\}([^{}]*)\}'
        def fix_pattern3(match):
            field_decl = match.group(1)
            parts = [match.group(i) for i in range(2, len(match.groups()) + 1)]
            # Reconstruct without internal braces
            result = parts[0]  # before first brace
            for i in range(1, len(parts), 2):
                if i + 1 < len(parts):
                    result += parts[i] + parts[i + 1]  # content + after
            return f'{field_decl}{{{result}}}'
        
        content = re.sub(pattern3, fix_pattern3, content)
        
        # More general pattern for any remaining internal braces
        pattern4 = r'(\btitle\s*=\s*)\{([^{}]*\{[^{}]*\}[^{}]*)\}'
        def fix_pattern4(match):
            field_decl = match.group(1)
            field_value = match.group(2)
            cleaned = self.text_processor.clean_nested_braces(field_value)
            return f'{field_decl}{{{cleaned}}}'
        
        content = re.sub(pattern4, fix_pattern4, content)
        
        return content


def main():
    """Command-line interface for targeted fixing."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Targeted BibTeX fixing')
    parser.add_argument('bibtex_file', help='Path to BibTeX file to fix')
    
    args = parser.parse_args()
    
    fixer = TargetedBraceFixer()
    success = fixer.fix_complex_internal_braces(args.bibtex_file)
    
    if not success:
        exit(1)


if __name__ == "__main__":
    main()
