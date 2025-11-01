#!/usr/bin/env python3
"""
Dynamic Filters Generator

Generates dynamic filter data for the library page from bibliography entries.
This includes entry types, role tags, and language tags.
"""

import os
import re
import yaml
from typing import List, Dict, Any


class DynamicFiltersGenerator:
    """Generates dynamic filters data from bibliography entries."""
    
    def __init__(self, output_dir: str):
        """Initialize the generator.
        
        Args:
            output_dir (str): Output directory for the _data folder
        """
        self.output_dir = output_dir
    
    def generate_filters(self, entries: List[Dict[str, Any]]) -> None:
        """Generate dynamic filters data from bibliography entries.
        
        Args:
            entries: List of bibliography entries
        """
        print("Generating dynamic filters data...")
        
        # Initialize sets for collecting filter data
        entry_types = set()
        role_tags = set()
        language_tags = set()
        
        # Process the entries that were passed to this method
        # These entries have already been loaded and parsed by the calling code
        print("Processing entries for dynamic filters...")
        
        # Entry type mapping - standard BibTeX types use proper multiword names
        entry_type_mapping = {
            'article': 'Journal Article',
            'inproceedings': 'Conference Paper',
            'incollection': 'Book Chapter',
            'book': 'Book',
            'phdthesis': 'PhD Thesis',
            'mastersthesis': "Master's Thesis",
            'thesis': 'Thesis',
            'techreport': 'Report',
            'misc': 'Other',
            'unpublished': 'Unpublished',
            'inbook': 'Book Section',
            'proceedings': 'Proceedings',
            'manual': 'Manual',
            'patent': 'Patent',
            'webinar': 'Webinar',
            'roundtable': 'Roundtable',
            'workshop': 'Workshop',
            'panel': 'Panel',
            'conference': 'Conference'
        }
        
        # Process each entry
        for entry in entries:
            # Extract entry type - bibtexparser stores it in ENTRYTYPE field
            entry_type = entry.get('ENTRYTYPE', '').lower()
            display_name = ''
            
            # First check for type override from notes or annote field [type] section
            note = entry.get('note', '')
            annote = entry.get('annote', '')
            
            # Check note field first
            if note:
                note_text = note.strip()
                if '[type]' in note_text:
                    type_section = note_text.split('[type]')[-1].split('[')[0].strip()
                    type_lines = type_section.split('\n')
                    for line in type_lines:
                        clean_line = line.strip()
                        if clean_line != '':
                            # Use the custom type with proper capitalization
                            # Unescape @ symbols that were escaped for BibTeX compatibility
                            display_name = clean_line.replace('@@', '@').capitalize()
                            break
            
            # If no type from note field, check annote field
            if not display_name and annote:
                annote_text = annote.strip()
                if '[type]' in annote_text:
                    type_section = annote_text.split('[type]')[-1].split('[')[0].strip()
                    type_lines = type_section.split('\n')
                    for line in type_lines:
                        clean_line = line.strip()
                        if clean_line != '':
                            # Use the custom type with proper capitalization
                            # Unescape @ symbols that were escaped for BibTeX compatibility
                            display_name = clean_line.replace('@@', '@').capitalize()
                            break
            
            # If no type from notes, use original entry type
            if not display_name and entry_type:
                # Use mapping if available, otherwise capitalize the entry type
                display_name = entry_type_mapping.get(entry_type, entry_type.capitalize())
            
            if display_name:
                entry_types.add(display_name)
            
            # Extract role from notes or annote field [role] section
            if note:
                note_text = note.strip()
                if '[role]' in note_text:
                    role_section = note_text.split('[role]')[-1].split('[')[0].strip()
                    role_lines = role_section.split('\n')
                    for line in role_lines:
                        clean_line = line.strip()
                        if clean_line:
                            role_tags.add(clean_line.lower())
                
                # Extract language from notes field [language] section
                if '[language]' in note_text:
                    language_section = note_text.split('[language]')[-1].split('[')[0].strip()
                    language_lines = language_section.split('\n')
                    for line in language_lines:
                        clean_line = line.strip()
                        if clean_line:
                            language = clean_line.replace('@@', '@').lower()
                            if language in ['french', 'spanish', 'chinese']:
                                language_tags.add(language)
            
            # Also check annote field for role and language
            if annote:
                annote_text = annote.strip()
                if '[role]' in annote_text:
                    role_section = annote_text.split('[role]')[-1].split('[')[0].strip()
                    role_lines = role_section.split('\n')
                    for line in role_lines:
                        clean_line = line.strip()
                        if clean_line:
                            role_tags.add(clean_line.lower())
                
                # Extract language from annote field [language] section
                if '[language]' in annote_text:
                    language_section = annote_text.split('[language]')[-1].split('[')[0].strip()
                    language_lines = language_section.split('\n')
                    for line in language_lines:
                        clean_line = line.strip()
                        if clean_line:
                            language = clean_line.replace('@@', '@').lower()
                            if language in ['french', 'spanish', 'chinese']:
                                language_tags.add(language)
            
            # Extract keywords for role tags and language tags
            keywords = entry.get('keywords', '')
            if keywords:
                keyword_list = [k.strip() for k in keywords.split(',')]
                for keyword in keyword_list:
                    keyword_lower = keyword.lower()
                    
                    # Check for language indicators
                    if re.search(r'🇫🇷|french|français', keyword_lower):
                        language_tags.add('french')
                    elif re.search(r'🇪🇸|spanish|español', keyword_lower):
                        language_tags.add('spanish')
                    elif re.search(r'🇨🇳|chinese|中文', keyword_lower):
                        language_tags.add('chinese')
                    else:
                        # Only add actual role keywords to role_tags
                        actual_roles = {
                            'attendee', 'contributor', 'coordinator', 'delegate', 'editor',
                            'facilitator', 'featured', 'interview', 'lead author', 'moderator',
                            'organiser', 'organizer', 'panellist', 'panelist', 'participant',
                            'presenter', 'quoted', 'speaker'
                        }
                        if keyword_lower in actual_roles:
                            role_tags.add(keyword_lower)
        
        # All entry types are now dynamically discovered from the actual bibliography entries
        # This includes both standard BibTeX types and custom types from ignore tags
        
        # Convert to sorted lists
        display_entry_types = sorted(list(entry_types))
        role_tags_list = sorted(list(role_tags))
        language_tags_list = sorted(list(language_tags))
        
        
        # Create the data structure
        filter_data = {
            'entry_types': display_entry_types,
            'role_tags': role_tags_list,
            'language_tags': language_tags_list
        }
        
        # Write to YAML file
        data_dir = os.path.join(self.output_dir, '_data')
        os.makedirs(data_dir, exist_ok=True)
        
        output_file = os.path.join(data_dir, 'dynamic_filters.yml')
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(filter_data, f, default_flow_style=False, sort_keys=False)
        
        print(f"Generated dynamic filters: {len(display_entry_types)} entry types, {len(role_tags_list)} role tags, {len(language_tags_list)} language tags")
        print(f"Saved to: {output_file}")
    
    def _load_entries_from_file(self) -> List[Dict[str, Any]]:
        """Load entries from the processed BibTeX file using custom parsing."""
        import os
        import re
        
        processed_file = os.path.join(self.output_dir, '_bibliography', 'papers.bib')
        if not os.path.exists(processed_file):
            print(f"Processed file not found: {processed_file}")
            return []
        
        with open(processed_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        entries = []
        
        # Find all @type{key, ... } entries (including custom types like @webinar)
        pattern = r'@(\w+)\s*\{\s*([^,]+)\s*,'
        matches = list(re.finditer(pattern, content))
        
        for match in matches:
            entry_type = match.group(1)
            citation_key = match.group(2).strip()
            
            # Find the entry boundaries
            start_pos = match.start()
            end_pos = self._find_entry_end(content, start_pos)
            
            if end_pos != -1:
                entry_content = content[start_pos:end_pos]
                fields = self._parse_entry_fields(entry_content)
                fields['ENTRYTYPE'] = entry_type
                fields['ID'] = citation_key
                entries.append(fields)
        
        print(f"Loaded {len(entries)} entries from processed file")
        return entries
    
    def _find_entry_end(self, content: str, start_pos: int) -> int:
        """Find the end position of a BibTeX entry starting at start_pos."""
        # Find the opening brace after @type{
        brace_start = content.find('{', start_pos)
        if brace_start == -1:
            return -1
        
        brace_count = 1  # We have one opening brace
        end_pos = brace_start
        
        for i in range(brace_start + 1, len(content)):
            if content[i] == '{':
                brace_count += 1
            elif content[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_pos = i
                    break
        
        return end_pos if brace_count == 0 else -1
    
    def _parse_entry_fields(self, entry_content: str) -> Dict[str, str]:
        """Parse fields from a single BibTeX entry."""
        import re
        
        fields = {}
        
        # Find all fields with braces
        pos = 0
        while True:
            field_match = re.search(r'(\w+)\s*=\s*\{', entry_content[pos:])
            if not field_match:
                break
            
            field_name = field_match.group(1).strip()
            field_start = pos + field_match.end() - 1
            
            # Find the matching closing brace
            brace_count = 0
            field_end = field_start
            
            for i in range(field_start, len(entry_content)):
                if entry_content[i] == '{':
                    brace_count += 1
                elif entry_content[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        field_end = i
                        break
            
            if brace_count == 0:
                field_value = entry_content[field_start + 1:field_end].strip()
                fields[field_name] = field_value
                pos = field_end + 1
            else:
                pos = pos + field_match.end()
        
        return fields


def main():
    """Main entry point for standalone execution."""
    import argparse
    import sys
    from pathlib import Path
    
    # Add the processing directory to the Python path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from library.bib_parser import BibParser
    import bibtexparser
    from bibtexparser.bparser import BibTexParser
    from bibtexparser.customization import convert_to_unicode
    
    parser = argparse.ArgumentParser(description="Generate dynamic filters from BibTeX file")
    parser.add_argument('--bib-file', type=str, default='../_bibliography/papers.bib',
                       help='Path to BibTeX file')
    parser.add_argument('--output-dir', type=str, default='..',
                       help='Output directory (project root)')
    parser.add_argument('--test', action='store_true',
                       help='Test mode: only process 5 most recent entries')
    
    args = parser.parse_args()
    
    # Load bibliography
    try:
        with open(args.bib_file, 'r', encoding='utf-8') as bibtex_file:
            parser = BibTexParser(common_strings=True)
            parser.customization = convert_to_unicode
            bib_database = bibtexparser.load(bibtex_file, parser=parser)
        
        entries = bib_database.entries
        print(f"Loaded {len(entries)} entries from {args.bib_file}")
        
        # Filter for test mode if needed
        if args.test:
            # Sort by year and take the 5 most recent
            entries_with_year = []
            for entry in entries:
                year = entry.get('year', '0000')
                try:
                    year_int = int(year)
                except (ValueError, TypeError):
                    year_int = 0
                entries_with_year.append((year_int, entry))
            
            entries_with_year.sort(key=lambda x: x[0], reverse=True)
            entries = [entry for year, entry in entries_with_year[:5]]
            print(f"Test mode: Processing {len(entries)} most recent entries")
        
        # Generate filters
        generator = DynamicFiltersGenerator(args.output_dir)
        generator.generate_filters(entries)
        
    except FileNotFoundError:
        print(f"Error: BibTeX file not found: {args.bib_file}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
