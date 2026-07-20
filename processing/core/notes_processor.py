#!/usr/bin/env python3
"""
Notes Processor for Zotero Notes Integration

This module handles importing and processing Zotero notes into BibTeX entries.
It extracts structured information from Zotero notes and adds them as annote fields
to BibTeX entries for use in the library display system.
"""

import re
from typing import Dict, List, Optional, Tuple
from processing.core.tag_extractor import TagExtractor


class NotesProcessor:
    """Handles processing of Zotero notes into BibTeX annote fields."""
    
    def __init__(self):
        """Initialize the notes processor."""
        self.tag_extractor = TagExtractor(preserve_case=False)
    
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
        
        # Add the structured notes to annote field (Zotero Notes export standard)
        # Custom tags should only come from Zotero Notes field, which exports to annote
        entry['annote'] = structured_notes
        
        # Extract and populate BibTeX fields from notes
        entry = self._extract_and_populate_fields(entry, structured_notes)
        
        return entry
    
    def _add_bibtex_type_fallback(self, entry: Dict[str, any]) -> Dict[str, any]:
        """
        Add BibTeX type fallback to entries that don't have custom types in notes.
        
        Only adds fallback if [type] section doesn't already exist in annote.
        
        Args:
            entry: The BibTeX entry dictionary
            
        Returns:
            Updated entry dictionary with type fallback
        """
        # Check if [type] already exists in annote - if so, don't add fallback
        annote = entry.get('annote', '')
        if annote and '[type]' in annote:
            return entry
        
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
            
            # Add the type to the annote field for the template to use
            # Escape @ symbols to prevent BibTeX parsing conflicts
            escaped_type = display_type.replace('@', '@@')
            if 'annote' in entry and entry['annote']:
                # Add to existing annote
                entry['annote'] += f'\n\n[type]\n{escaped_type}'
            else:
                # Create new annote field
                entry['annote'] = f'[type]\n{escaped_type}'
        
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
                # Escape @ for BibTeX, but do not re-escape already-escaped @@
                placeholder = '\x00AT\x00'
                line = line.replace('@@', placeholder)
                line = line.replace('@', '@@')
                line = line.replace(placeholder, '@@')
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
        
        # Use unified tag extractor for consistent extraction
        # Create temporary entry dict with annote for extraction
        temp_entry = entry.copy()
        temp_entry['annote'] = notes
        
        # Extract type information from notes
        entry_type = self.tag_extractor.extract_type(temp_entry)
        if not entry_type:
            # If no custom type found in notes, add BibTeX type fallback to notes
            entry = self._add_bibtex_type_fallback(entry)
        
        # Note: Tags are stored in annote field only (Zotero Notes export), not in keywords field
        # This ensures single source of truth and preserves Zotero format
        
        # Extract selected tag from notes
        is_selected = self.tag_extractor.extract_selected(temp_entry)
        if is_selected:
            entry['selected'] = 'true'
        
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
    
    @staticmethod
    def _strip_trailing_url_punctuation(url: str) -> str:
        """Remove trailing punctuation commonly stuck to URLs in prose."""
        return url.rstrip('.,);')

    def _extract_video_links(self, notes: str) -> List[str]:
        """Extract video links from notes (any http(s) URL in the [video] section)."""
        if not notes or '[video]' not in notes:
            return []
        
        video_section = notes.split('[video]')[-1].split('[')[0].strip()
        video_lines = video_section.split('\n')
        
        video_links = []
        for line in video_lines:
            clean_line = self._strip_trailing_url_punctuation(line.strip())
            if clean_line and re.match(r'https?://', clean_line, re.IGNORECASE):
                video_links.append(clean_line)
        
        return video_links
    
    def _extract_other_links(self, notes: str) -> List[str]:
        """Extract non-video links from notes."""
        if not notes:
            return []
        
        video_links = set(self._extract_video_links(notes))
        
        # Find all URLs in the notes
        url_pattern = r'https?://[^\s]+'
        all_urls = re.findall(url_pattern, notes)
        
        # Filter out video URLs (including those listed under [video])
        other_links = []
        for url in all_urls:
            clean_url = self._strip_trailing_url_punctuation(url)
            if clean_url in video_links:
                continue
            if 'youtube' in clean_url or 'youtu.be' in clean_url:
                continue
            other_links.append(clean_url)
        
        return other_links
    
    
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
            Updated entries with annote fields added
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
    test_entry = {
        'ENTRYTYPE': 'misc',
        'annote': """supplementary

[role]
moderator
speaker

[type]
webinar

[video]
https://www.youtube.com/watch?v=iMmbqMbH8go"""
    }
    
    processed = processor.process_notes_for_entry(test_entry, test_entry['annote'])
    print(f"Processed entry: {processed}")
    
    # Test tag extraction using unified extractor
    tags = processor.tag_extractor.extract_all_tags(processed)
    print(f"Extracted tags: {tags}")


if __name__ == "__main__":
    main()
