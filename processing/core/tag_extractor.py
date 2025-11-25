#!/usr/bin/env python3
"""
Unified Tag Extractor

Single source of truth for extracting tags from Zotero annote fields.
This module provides consistent tag extraction logic used across all processing modules.

Tags are extracted from structured notes using [type], [role], [language] markers.
The format matches Zotero export format exactly. Custom tags come only from annote field
(Zotero Notes field exports to annote).
"""

import re
from typing import Dict, List, Optional, Tuple


class TagExtractor:
    """Unified tag extraction from Zotero annote fields (Zotero Notes export)."""
    
    # Standard entry type mappings (BibTeX -> Display)
    ENTRY_TYPE_MAPPING = {
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
        'conference': 'Conference',
        'blog': 'Blog',
        'newspaper': 'Newspaper',
        'guest lecture': 'Guest Lecture',
        'briefing note': 'Briefing Note',
        'report section': 'Report Section',
    }
    
    # Valid language tags
    VALID_LANGUAGES = {'french', 'spanish', 'chinese'}
    
    def __init__(self, preserve_case: bool = False):
        """
        Initialize tag extractor.
        
        Args:
            preserve_case: If True, preserve original case. If False, normalize case.
                          Default False for consistency.
        """
        self.preserve_case = preserve_case
    
    def extract_type(self, entry: Dict[str, any]) -> Optional[str]:
        """
        Extract entry type from annote field (Zotero Notes export).
        
        Priority:
        1. [type] section in annote field
        2. BibTeX ENTRYTYPE with mapping
        
        Args:
            entry: BibTeX entry dictionary
            
        Returns:
            Entry type string, or None if not found
        """
        # Check annote field (Zotero Notes export standard)
        annote = entry.get('annote', '')
        if annote:
            annote_text = annote.strip()
            if '[type]' in annote_text:
                type_value = self._extract_section_value(annote_text, '[type]')
                if type_value:
                    return self._normalize_type(type_value)
        
        # Fallback to BibTeX ENTRYTYPE
        entry_type = entry.get('ENTRYTYPE', '').lower()
        if entry_type:
            return self.ENTRY_TYPE_MAPPING.get(entry_type, entry_type.capitalize())
        
        return None
    
    def extract_roles(self, entry: Dict[str, any]) -> List[str]:
        """
        Extract all role tags from annote field (Zotero Notes export).
        
        Args:
            entry: BibTeX entry dictionary
            
        Returns:
            List of role strings (lowercased), empty list if none found
        """
        roles = []
        
        # Check annote field (Zotero Notes export standard)
        annote = entry.get('annote', '')
        if annote:
            annote_text = annote.strip()
            if '[role]' in annote_text:
                role_values = self._extract_section_values(annote_text, '[role]')
                roles.extend(role_values)
        
        # Normalize: lowercase and remove duplicates
        normalized_roles = []
        seen = set()
        for role in roles:
            role_lower = role.lower().strip()
            if role_lower and role_lower not in seen:
                normalized_roles.append(role_lower)
                seen.add(role_lower)
        
        return normalized_roles
    
    def extract_languages(self, entry: Dict[str, any]) -> List[str]:
        """
        Extract language tags from annote field (Zotero Notes export).
        
        Only returns valid language tags (french, spanish, chinese).
        
        Args:
            entry: BibTeX entry dictionary
            
        Returns:
            List of language strings (lowercased), empty list if none found
        """
        languages = []
        
        # Check annote field (Zotero Notes export standard)
        annote = entry.get('annote', '')
        if annote:
            annote_text = annote.strip()
            if '[language]' in annote_text:
                language_values = self._extract_section_values(annote_text, '[language]')
                languages.extend(language_values)
        
        # Normalize: lowercase, validate, remove duplicates
        normalized_languages = []
        seen = set()
        for lang in languages:
            lang_lower = lang.lower().strip()
            if lang_lower in self.VALID_LANGUAGES and lang_lower not in seen:
                normalized_languages.append(lang_lower)
                seen.add(lang_lower)
        
        return normalized_languages
    
    def extract_selected(self, entry: Dict[str, any]) -> bool:
        """
        Extract selected tag from annote field (Zotero Notes export).
        
        Checks for [selected] marker (case-insensitive) anywhere in annote field.
        
        Args:
            entry: BibTeX entry dictionary
            
        Returns:
            Boolean indicating if entry should be marked as selected
        """
        # Check annote field (Zotero Notes export standard)
        annote = entry.get('annote', '')
        if annote:
            annote_text = annote.strip()
            # Check for [selected] marker (case-insensitive)
            if '[selected]' in annote_text.lower():
                return True
        
        return False
    
    def extract_all_tags(self, entry: Dict[str, any]) -> Dict[str, any]:
        """
        Extract all tags (type, roles, languages) from an entry.
        
        Args:
            entry: BibTeX entry dictionary
            
        Returns:
            Dictionary with keys: 'type', 'roles', 'languages'
        """
        return {
            'type': self.extract_type(entry),
            'roles': self.extract_roles(entry),
            'languages': self.extract_languages(entry)
        }
    
    def _extract_section_value(self, text: str, marker: str) -> Optional[str]:
        """
        Extract the first value from a structured section.
        
        Format: [marker]\nvalue
        
        Args:
            text: Text containing the section
            marker: Section marker (e.g., '[type]')
            
        Returns:
            First non-empty line after marker, or None
        """
        if marker not in text:
            return None
        
        # Split on marker, take last occurrence, then split on next [
        section = text.split(marker)[-1].split('[')[0].strip()
        
        # Get first non-empty line
        lines = section.split('\n')
        for line in lines:
            clean_line = line.strip()
            if clean_line:
                # Unescape @ symbols (BibTeX compatibility)
                return clean_line.replace('@@', '@')
        
        return None
    
    def _extract_section_values(self, text: str, marker: str) -> List[str]:
        """
        Extract all values from a structured section.
        
        Format: [marker]\nvalue1\nvalue2
        
        Args:
            text: Text containing the section
            marker: Section marker (e.g., '[role]')
            
        Returns:
            List of non-empty values after marker
        """
        if marker not in text:
            return []
        
        # Split on marker, take last occurrence, then split on next [
        section = text.split(marker)[-1].split('[')[0].strip()
        
        # Get all non-empty lines
        values = []
        lines = section.split('\n')
        for line in lines:
            clean_line = line.strip()
            if clean_line:
                # Unescape @ symbols (BibTeX compatibility)
                clean_line = clean_line.replace('@@', '@')
                values.append(clean_line)
        
        return values
    
    def _normalize_type(self, type_value: str) -> str:
        """
        Normalize entry type to standard format.
        
        Args:
            type_value: Raw type value from notes
            
        Returns:
            Normalized type string
        """
        # Unescape @ symbols
        type_value = type_value.replace('@@', '@')
        
        # Check if it's a known mapping
        type_lower = type_value.lower()
        if type_lower in self.ENTRY_TYPE_MAPPING:
            return self.ENTRY_TYPE_MAPPING[type_lower]
        
        # Apply case normalization
        if self.preserve_case:
            return type_value
        else:
            # Capitalize first letter of each word
            words = type_value.split()
            capitalized_words = [word.capitalize() for word in words]
            return ' '.join(capitalized_words)


def main():
    """Test the tag extractor."""
    extractor = TagExtractor()
    
    # Test entry
    test_entry = {
        'ENTRYTYPE': 'misc',
        'note': '',
        'annote': """[role]
moderator
speaker
[type]
webinar
[language]
french"""
    }
    
    print("Testing TagExtractor:")
    print(f"Type: {extractor.extract_type(test_entry)}")
    print(f"Roles: {extractor.extract_roles(test_entry)}")
    print(f"Languages: {extractor.extract_languages(test_entry)}")
    
    all_tags = extractor.extract_all_tags(test_entry)
    print(f"All tags: {all_tags}")


if __name__ == "__main__":
    main()

