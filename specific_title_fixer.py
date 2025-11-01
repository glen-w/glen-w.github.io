#!/usr/bin/env python3
"""
Specific Title Fixer for process_papers.py
Fixes the specific title patterns that still have internal braces.
"""

import re
import os
from typing import Dict, List, Optional
from config import Configuration
from text_processor import TextProcessor


class SpecificTitleFixer:
    """Fixes specific title patterns with internal braces."""
    
    def __init__(self, config: Configuration = None):
        """Initialize with configuration."""
        self.config = config or Configuration()
        self.text_processor = TextProcessor(config)
    
    def fix_specific_titles(self, bibtex_file: str) -> bool:
        """Fix the specific title patterns."""
        try:
            # Read the file
            with open(bibtex_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"🔧 Fixing specific title patterns in {bibtex_file}...")
            
            # Fix each specific pattern
            content = self._fix_specific_patterns(content)
            
            # Write the fixed content back
            with open(bibtex_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Successfully fixed specific title patterns in {bibtex_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error fixing {bibtex_file}: {e}")
            return False
    
    def _fix_specific_patterns(self, content: str) -> str:
        """Fix the specific patterns we identified."""
        
        # Pattern 1: {The ship has reached the shore": why the historic {Agreement} to protect the {High} {Seas} matters and what happens next}
        pattern1 = r'(\btitle\s*=\s*)\{The ship has reached the shore": why the historic \{Agreement\} to protect the \{High\} \{Seas\} matters and what happens next\}'
        replacement1 = r'\1{The ship has reached the shore: why the historic Agreement to protect the High Seas matters and what happens next}'
        content = re.sub(pattern1, replacement1, content)
        
        # Pattern 2: {Renewables 2024 {Global} {Status} {Report}: {Energy} {Systems} and {Infrastructure}}
        pattern2 = r'(\btitle\s*=\s*)\{Renewables 2024 \{Global\} \{Status\} \{Report\}: \{Energy\} \{Systems\} and \{Infrastructure\}\}'
        replacement2 = r'\1{Renewables 2024 Global Status Report: Energy Systems and Infrastructure}'
        content = re.sub(pattern2, replacement2, content)
        
        # Pattern 3: {Renewables 2024 {Global} {Status} {Report}: {Economic} and {Social} {Value} {Creation}}
        pattern3 = r'(\btitle\s*=\s*)\{Renewables 2024 \{Global\} \{Status\} \{Report\}: \{Economic\} and \{Social\} \{Value\} \{Creation\}\}'
        replacement3 = r'\1{Renewables 2024 Global Status Report: Economic and Social Value Creation}'
        content = re.sub(pattern3, replacement3, content)
        
        # Pattern 4: {The {Future} of {Energy}: {New} {Technologies} and {Human} {Development}}
        pattern4 = r'(\btitle\s*=\s*)\{The \{Future\} of \{Energy\}: \{New\} \{Technologies\} and \{Human\} \{Development\}\}'
        replacement4 = r'\1{The Future of Energy: New Technologies and Human Development}'
        content = re.sub(pattern4, replacement4, content)
        
        # Pattern 5: {Renewables for {Nature}: {Integrating} {Biodiversity} \& {Communities} in {Energy} {Policy}}
        pattern5 = r'(\btitle\s*=\s*)\{Renewables for \{Nature\}: \{Integrating\} \{Biodiversity\} \\& \{Communities\} in \{Energy\} \{Policy\}\}'
        replacement5 = r'\1{Renewables for Nature: Integrating Biodiversity & Communities in Energy Policy}'
        content = re.sub(pattern5, replacement5, content)
        
        # Pattern 6: {Post-2020 {Global} {Biodiversity} {Framework}: what's next for the {Ocean}?}
        pattern6 = r'(\btitle\s*=\s*)\{Post-2020 \{Global\} \{Biodiversity\} \{Framework\}: what\'s next for the \{Ocean\}\?\}'
        replacement6 = r'\1{Post-2020 Global Biodiversity Framework: what\'s next for the Ocean?}'
        content = re.sub(pattern6, replacement6, content)
        
        # Pattern 7: {Buildings and {Climate} {Global} {Forum}}
        pattern7 = r'(\btitle\s*=\s*)\{Buildings and \{Climate\} \{Global\} \{Forum\}\}'
        replacement7 = r'\1{Buildings and Climate Global Forum}'
        content = re.sub(pattern7, replacement7, content)
        
        # Pattern 8: {Global {Alliance} for {Buildings} and {Construction} ({GlobalABC}) {General} {Assembly}}
        pattern8 = r'(\btitle\s*=\s*)\{Global \{Alliance\} for \{Buildings\} and \{Construction\} \(\{GlobalABC\}\) \{General\} \{Assembly\}\}'
        replacement8 = r'\1{Global Alliance for Buildings and Construction (GlobalABC) General Assembly}'
        content = re.sub(pattern8, replacement8, content)
        
        return content


def main():
    """Command-line interface for specific title fixing."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix specific title patterns')
    parser.add_argument('bibtex_file', help='Path to BibTeX file to fix')
    
    args = parser.parse_args()
    
    fixer = SpecificTitleFixer()
    success = fixer.fix_specific_titles(args.bibtex_file)
    
    if not success:
        exit(1)


if __name__ == "__main__":
    main()
