#!/usr/bin/env python3
"""
BibTeXFormatter module for process_papers.py
Handles proper formatting of BibTeX entries with multi-line fields.
"""

import re
import sys
import os
from typing import Dict, List

# Add the processing directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.text_processor import TextProcessor


class BibTeXFormatter:
    """Handles proper formatting of BibTeX entries with multi-line fields."""
    
    def __init__(self):
        """Initialize the formatter."""
        self.text_processor = TextProcessor()
    
    def format_entry(self, entry_type: str, citation_key: str, fields: Dict[str, str]) -> str:
        """
        Format a BibTeX entry with proper multi-line structure.
        
        Args:
            entry_type: The BibTeX entry type (e.g., 'article', 'book')
            citation_key: The citation key
            fields: Dictionary of field names and values
            
        Returns:
            Formatted BibTeX entry string
        """
        # Start with the entry declaration
        lines = [f"@{entry_type}{{{citation_key},"]
        
        # Add each field on its own line with proper indentation
        field_names = list(fields.keys())
        for i, (field_name, field_value) in enumerate(fields.items()):
            # Determine if this is the last field
            is_last = (i == len(field_names) - 1)
            
            # Clean internal braces for certain fields
            if field_name in ['title', 'shorttitle', 'abstract', 'author', 'booktitle', 'journal', 'publisher', 'type']:
                cleaned_value = self.text_processor.clean_braces_in_field_value(field_value)
            else:
                cleaned_value = field_value
            
            # Format the field value
            if cleaned_value.startswith('{') and cleaned_value.endswith('}'):
                # Field value already has braces
                formatted_value = cleaned_value
            else:
                # Add braces around the field value
                formatted_value = f"{{{cleaned_value}}}"
            
            # Add the field line
            if is_last:
                # Last field doesn't need a comma
                lines.append(f"\t{field_name} = {formatted_value}")
            else:
                # Non-last field needs a comma
                lines.append(f"\t{field_name} = {formatted_value},")
        
        # Close the entry
        lines.append("}")
        
        return '\n'.join(lines)
    
    def format_entry_from_content(self, content: str) -> str:
        """
        Format a BibTeX entry from existing content, ensuring proper multi-line structure.
        
        Args:
            content: The existing BibTeX entry content
            
        Returns:
            Formatted BibTeX entry string
        """
        # Parse the entry
        entry_info = self._parse_entry_content(content)
        if not entry_info:
            return content
        
        # Format it properly
        return self.format_entry(
            entry_info['type'],
            entry_info['citation_key'],
            entry_info['fields']
        )
    
    def _parse_entry_content(self, content: str) -> Dict:
        """Parse BibTeX entry content to extract type, key, and fields."""
        # Find the entry type and citation key
        type_match = re.match(r'@(\w+)\s*\{\s*([^,]+)\s*,', content)
        if not type_match:
            return None
        
        entry_type = type_match.group(1)
        citation_key = type_match.group(2).strip()
        
        # Find the start of the fields (after the comma)
        start_pos = type_match.end()
        
        # Find the matching closing brace
        brace_count = 1  # We already have one opening brace
        end_pos = start_pos
        
        for i in range(start_pos, len(content)):
            if content[i] == '{':
                brace_count += 1
            elif content[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_pos = i
                    break
        
        if brace_count != 0:  # No matching closing brace found
            return None
        
        # Extract fields content
        fields_content = content[start_pos:end_pos]
        
        # Clean up the fields content to remove any stray commas at the beginning
        fields_content = fields_content.strip()
        if fields_content.startswith(','):
            fields_content = fields_content[1:].strip()
        
        # Parse fields
        fields = self._parse_fields(fields_content)
        
        return {
            'type': entry_type,
            'citation_key': citation_key,
            'fields': fields
        }
    
    def _parse_fields(self, fields_content: str) -> Dict[str, str]:
        """Parse fields from BibTeX entry content."""
        fields = {}
        
        # Handle both single-line and multi-line field formats
        # First, try to split by field patterns
        field_pattern = r'(\w+)\s*=\s*\{'
        
        # Find all field matches
        matches = list(re.finditer(field_pattern, fields_content))
        
        for i, match in enumerate(matches):
            field_name = match.group(1)
            start_pos = match.end() - 1  # Position of opening brace
            
            # Find the end position of this field by looking for the closing brace
            brace_count = 0
            end_pos = start_pos
            for j in range(start_pos, len(fields_content)):
                if fields_content[j] == '{':
                    brace_count += 1
                elif fields_content[j] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_pos = j
                        break
            
            # Extract the field value
            field_value = fields_content[start_pos + 1:end_pos]
            
            # Clean up the field value
            field_value = field_value.strip()
            
            # Remove trailing comma if present
            if field_value.endswith(','):
                field_value = field_value[:-1].strip()
            
            # Remove any trailing closing braces
            while field_value.endswith('}'):
                field_value = field_value[:-1].strip()
            
            # Remove any trailing commas that might be left
            if field_value.endswith(','):
                field_value = field_value[:-1].strip()
            
            fields[field_name] = field_value
        
        return fields
    
    def format_bibtex_file(self, input_file: str, output_file: str = None) -> bool:
        """
        Format an entire BibTeX file with proper multi-line structure.
        
        Args:
            input_file: Path to input BibTeX file
            output_file: Path to output file (if None, overwrites input)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Read the input file
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split into entries
            entries = self._split_into_entries(content)
            
            # Format each entry
            formatted_entries = []
            for entry in entries:
                if entry.strip():
                    formatted_entry = self.format_entry_from_content(entry)
                    formatted_entries.append(formatted_entry)
            
            # Join entries with blank lines
            formatted_content = '\n\n'.join(formatted_entries)
            
            # Write to output file
            output_path = output_file or input_file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(formatted_content)
            
            return True
            
        except Exception as e:
            print(f"Error formatting BibTeX file: {e}")
            return False
    
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
    """Command-line interface for BibTeX formatting."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Format BibTeX file with proper multi-line structure')
    parser.add_argument('input_file', help='Path to input BibTeX file')
    parser.add_argument('--output', '-o', help='Path to output file (default: overwrite input)')
    
    args = parser.parse_args()
    
    formatter = BibTeXFormatter()
    success = formatter.format_bibtex_file(args.input_file, args.output)
    
    if success:
        print("✅ BibTeX file formatted successfully")
    else:
        print("❌ Failed to format BibTeX file")
        exit(1)


if __name__ == "__main__":
    main()
