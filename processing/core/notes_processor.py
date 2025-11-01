#!/usr/bin/env python3
"""
Notes Processor for Zotero Notes Integration

This module handles importing and processing Zotero notes into BibTeX entries.
It extracts structured information from Zotero notes and adds them as note fields
to BibTeX entries for use in the library display system.
"""

import re
from typing import Dict, List, Optional, Tuple


class NotesProcessor:
    """Handles processing of Zotero notes into BibTeX note fields."""
    
    def __init__(self):
        """Initialize the notes processor."""
        pass
    
    def process_notes_for_entry(self, entry: Dict[str, any], zotero_notes: str) -> Dict[str, any]:
        """
        Process Zotero notes for a specific entry and extract information into BibTeX fields.
        
        Args:
            entry: The BibTeX entry dictionary
            zotero_notes: The raw notes from Zotero
            
        Returns:
            Updated entry dictionary with extracted information
        """
        if not zotero_notes or not zotero_notes.strip():
            # If no notes, still add BibTeX type fallback
            entry = self._add_bibtex_type_fallback(entry)
            return entry
        
        # Clean and structure the notes
        structured_notes = self._structure_notes(zotero_notes)
        
        # Add the structured notes as a note field
        # If the original was in 'annote', keep it there, otherwise use 'note'
        if 'annote' in entry and entry['annote'] == zotero_notes:
            entry['annote'] = structured_notes
        else:
            entry['note'] = structured_notes
        
        # Extract and populate BibTeX fields from notes
        entry = self._extract_and_populate_fields(entry, structured_notes)
        
        return entry
    
    def _add_bibtex_type_fallback(self, entry: Dict[str, any]) -> Dict[str, any]:
        """
        Add BibTeX type fallback to entries that don't have custom types in notes.
        
        Args:
            entry: The BibTeX entry dictionary
            
        Returns:
            Updated entry dictionary with type fallback
        """
        bibtex_type = entry.get('ENTRYTYPE', '').lower()
        if bibtex_type:
            # Map BibTeX types to proper multiword display types
            type_mapping = {
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
                'patent': 'Patent'
            }
            
            display_type = type_mapping.get(bibtex_type, bibtex_type)
            
            # Add the type to the notes field for the template to use
            # Escape @ symbols to prevent BibTeX parsing conflicts
            escaped_type = display_type.replace('@', '@@')
            if 'note' in entry and entry['note']:
                # Add to existing note
                entry['note'] += f'\n\n[type]\n{escaped_type}'
            elif 'annote' in entry and entry['annote']:
                # Add to existing annote
                entry['annote'] += f'\n\n[type]\n{escaped_type}'
            else:
                # Create new note field
                entry['note'] = f'[type]\n{escaped_type}'
        
        return entry
    
    def _structure_notes(self, raw_notes: str) -> str:
        """
        Structure raw Zotero notes into a consistent format.
        
        Args:
            raw_notes: Raw notes text from Zotero
            
        Returns:
            Structured notes text with @ symbols escaped for BibTeX compatibility
        """
        if not raw_notes:
            return ""
        
        # Split into lines and clean
        lines = raw_notes.strip().split('\n')
        structured_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Escape @ symbols to prevent BibTeX parsing conflicts
                line = line.replace('@', '@@')
                structured_lines.append(line)
        
        return '\n'.join(structured_lines)
    
    def _extract_and_populate_fields(self, entry: Dict[str, any], notes: str) -> Dict[str, any]:
        """
        Extract information from structured notes and populate BibTeX fields.
        
        Args:
            entry: The BibTeX entry dictionary
            notes: Structured notes text
            
        Returns:
            Updated entry dictionary with extracted fields
        """
        if not notes:
            return entry
        
        # Extract type information from notes
        entry_type = self.extract_type_from_notes(notes)
        if entry_type:
            # For multiword custom types, don't set as ENTRYTYPE (causes BibTeX parsing issues)
            # Instead, just add to keywords for backward compatibility
            if 'keywords' in entry:
                entry['keywords'] += f', {entry_type}'
            else:
                entry['keywords'] = entry_type
        else:
            # If no custom type found in notes, add BibTeX type fallback to notes
            entry = self._add_bibtex_type_fallback(entry)
        
        # Extract role information and add to keywords
        role = self.extract_role_from_notes(notes)
        if role:
            if 'keywords' in entry:
                entry['keywords'] += f', {role}'
            else:
                entry['keywords'] = role
        
        # Extract language information and add to keywords
        language = self.extract_language_from_notes(notes)
        if language:
            if 'keywords' in entry:
                entry['keywords'] += f', {language}'
            else:
                entry['keywords'] = language
        
        # Extract video links and add to appropriate fields
        video_links = self._extract_video_links(notes)
        if video_links:
            # Add the first video link as a video field
            entry['video'] = video_links[0]
        
        # Extract other links and add to appropriate fields
        other_links = self._extract_other_links(notes)
        if other_links:
            # Add links to a links field or URL field
            if 'url' not in entry:
                entry['url'] = other_links[0]
        
        return entry
    
    def _extract_video_links(self, notes: str) -> List[str]:
        """Extract video links from notes."""
        if not notes or '[video]' not in notes:
            return []
        
        video_section = notes.split('[video]')[-1].split('[')[0].strip()
        video_lines = video_section.split('\n')
        
        video_links = []
        for line in video_lines:
            clean_line = line.strip()
            if clean_line and ('youtube' in clean_line or 'youtu.be' in clean_line):
                video_links.append(clean_line)
        
        return video_links
    
    def _extract_other_links(self, notes: str) -> List[str]:
        """Extract non-video links from notes."""
        if not notes:
            return []
        
        # Find all URLs in the notes
        url_pattern = r'https?://[^\s]+'
        all_urls = re.findall(url_pattern, notes)
        
        # Filter out video URLs
        other_links = []
        for url in all_urls:
            if 'youtube' not in url and 'youtu.be' not in url:
                other_links.append(url)
        
        return other_links
    
    def extract_type_from_notes(self, notes: str) -> Optional[str]:
        """
        Extract type information from structured notes.
        
        Args:
            notes: Structured notes text
            
        Returns:
            Type string if found, None otherwise
        """
        if not notes or '[type]' not in notes:
            return None
        
        # Extract the type section
        type_section = notes.split('[type]')[-1].split('[')[0].strip()
        type_lines = type_section.split('\n')
        
        for line in type_lines:
            clean_line = line.strip()
            if clean_line:
                # Return the type as-is (preserve multiword custom types)
                return clean_line
        
        return None
    
    def extract_role_from_notes(self, notes: str) -> Optional[str]:
        """
        Extract role information from structured notes.
        
        Args:
            notes: Structured notes text
            
        Returns:
            Role string if found, None otherwise
        """
        if not notes or '[role]' not in notes:
            return None
        
        # Extract the role section
        role_section = notes.split('[role]')[-1].split('[')[0].strip()
        role_lines = role_section.split('\n')
        
        for line in role_lines:
            clean_line = line.strip()
            if clean_line:
                return clean_line.lower()
        
        return None
    
    def extract_language_from_notes(self, notes: str) -> Optional[str]:
        """
        Extract language information from structured notes.
        
        Args:
            notes: Structured notes text
            
        Returns:
            Language string if found, None otherwise
        """
        if not notes or '[language]' not in notes:
            return None
        
        # Extract the language section
        language_section = notes.split('[language]')[-1].split('[')[0].strip()
        language_lines = language_section.split('\n')
        
        for line in language_lines:
            clean_line = line.strip()
            if clean_line:
                return clean_line.lower()
        
        return None
    
    def extract_links_from_notes(self, notes: str) -> List[str]:
        """
        Extract links from structured notes.
        
        Args:
            notes: Structured notes text
            
        Returns:
            List of URLs found in notes
        """
        if not notes:
            return []
        
        # Find all URLs in the notes
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, notes)
        
        return urls
    
    def process_bibliography_notes(self, entries: List[Dict[str, any]], 
                                 zotero_notes_map: Dict[str, str]) -> List[Dict[str, any]]:
        """
        Process notes for all entries in a bibliography.
        
        Args:
            entries: List of BibTeX entries
            zotero_notes_map: Mapping of citation keys to Zotero notes
            
        Returns:
            Updated entries with note fields added
        """
        processed_entries = []
        
        for entry in entries:
            citation_key = entry.get('ID', '')
            if citation_key in zotero_notes_map:
                entry = self.process_notes_for_entry(entry, zotero_notes_map[citation_key])
            
            processed_entries.append(entry)
        
        return processed_entries


def main():
    """Test the notes processor."""
    processor = NotesProcessor()
    
    # Test notes processing
    test_notes = """supplementary

[audio]

[links]

[quotes]

[role]

moderator

[speakers]

José Elias Cabrera, Policy Officer, DG ENER (European Commission)

Louise Combret, Renewable Energy Policy Associate, The Nature Conservancy

Anne Georgelin, Deputy Head of the Office for Hydraulic and Marine Renewable Energies at the French Directorate-General for Energy and Climate (DGEC).

Ross Glover, Senior Nature Strategy Manager, SSE Renewables

Zoë Ledwith, Policy Advisor, REScoop

Dr Boze Hancock, Senior Marine Habitat Restoration Scientist, The Nature Conservancy

Andrea Wainer, Sustainability Lead, REN21

[type]

webinar

[video]

[https://www.youtube.com/watch?v=iMmbqMbH8go](https://www.youtube.com/watch?v=iMmbqMbH8go)"""
    
    # Test type extraction
    entry_type = processor.extract_type_from_notes(test_notes)
    print(f"Extracted type: {entry_type}")
    
    # Test role extraction
    role = processor.extract_role_from_notes(test_notes)
    print(f"Extracted role: {role}")
    
    # Test links extraction
    links = processor.extract_links_from_notes(test_notes)
    print(f"Extracted links: {links}")


if __name__ == "__main__":
    main()
