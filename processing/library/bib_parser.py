"""
BibTeX Parser Utilities

Helper functions for parsing and processing BibTeX entries.
"""

import re
from datetime import datetime
from typing import Dict, List, Optional, Any


class BibParser:
    """Utility class for parsing BibTeX entries."""
    
    def __init__(self):
        """Initialize the parser."""
        pass
    
    def clean_title(self, title: str) -> str:
        """Clean and format a title."""
        if not title:
            return "Untitled"
        
        # Remove braces and their contents, but preserve the content
        title = re.sub(r'\{([^}]*)\}', r'\1', title)
        # Remove extra quotes
        title = re.sub(r'^["\']+', '', title)
        title = re.sub(r'["\']+$', '', title)
        
        return title.strip()
    
    def format_authors(self, entry: Dict[str, Any]) -> List[Dict[str, str]]:
        """Format authors from BibTeX entry."""
        authors = []
        
        # Try different author fields
        author_field = entry.get('author') or entry.get('authors', '')
        if not author_field:
            return authors
        
        # Split by 'and' and clean up
        author_list = re.split(r'\s+and\s+', author_field, flags=re.IGNORECASE)
        
        for author in author_list:
            author = author.strip()
            if not author:
                continue
            
            # Parse name (simple approach)
            name_parts = author.split(',')
            if len(name_parts) >= 2:
                # Last, First format
                last_name = name_parts[0].strip()
                first_name = name_parts[1].strip()
            else:
                # First Last format
                name_parts = author.split()
                if len(name_parts) >= 2:
                    first_name = name_parts[0]
                    last_name = ' '.join(name_parts[1:])
                else:
                    first_name = author
                    last_name = ""
            
            authors.append({
                'first': first_name,
                'last': last_name,
                'full': author
            })
        
        return authors
    
    def get_entry_type_display(self, entry: Dict[str, Any]) -> str:
        """Get human-readable entry type."""
        # First check for custom_type field (from ignore tags)
        keywords = entry.get('keywords', '')
        custom_type_match = re.search(r'custom_type:\s*([^,]+)', keywords)
        if custom_type_match:
            return custom_type_match.group(1).strip().title()
        
        # Check for custom type in annote field [type] section
        annote = entry.get('annote', '')
        if annote:
            annote_text = annote.strip()
            if '[type]' in annote_text:
                type_section = annote_text.split('[type]')[-1].split('[')[0].strip()
                type_lines = type_section.split('\n')
                for line in type_lines:
                    clean_line = line.strip()
                    if clean_line != '':
                        # Use the custom type with proper capitalization
                        return clean_line.replace('@@', '@').capitalize()
        
        # Fall back to standard type mapping
        entry_type = entry.get('type', '').lower()
        
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
            'patent': 'Patent',
            'blog': 'Blog Post',
            'roundtable': 'Roundtable',
            'webinar': 'Webinar',
            'conference': 'Conference',
        }
        
        # Check for keyword overrides - handle specific multiword custom types
        keywords_lower = keywords.lower()
        if 'moderator' in keywords_lower:
            return 'moderated'
        elif 'organiser' in keywords_lower or 'organizer' in keywords_lower:
            return 'organized'
        elif 'panellist' in keywords_lower or 'panelist' in keywords_lower:
            return 'panel'
        elif 'workshop' in keywords_lower:
            return 'workshop'
        elif 'webinar' in keywords_lower:
            return 'webinar'
        elif 'launch event' in keywords_lower:
            return 'launch'
        elif 'side event' in keywords_lower:
            return 'Side Event'
        elif 'brown bag' in keywords_lower:
            return 'Brown Bag'
        elif 'background paper' in keywords_lower:
            return 'Background Paper'
        elif 'briefing note' in keywords_lower:
            return 'Briefing Note'
        elif 'discussion paper' in keywords_lower:
            return 'Discussion Paper'
        elif 'guest lecture' in keywords_lower:
            return 'Guest Lecture'
        elif 'issue brief' in keywords_lower:
            return 'Issue Brief'
        elif 'policy brief' in keywords_lower:
            return 'Policy Brief'
        elif 'report section' in keywords_lower:
            return 'Report Section'
        elif 'attendee' in keywords_lower:
            return 'attendance'
        
        return type_mapping.get(entry_type, entry_type.title() if entry_type else 'Other')
    
    def extract_year(self, entry: Dict[str, Any]) -> str:
        """Extract year from entry."""
        year = entry.get('year', '')
        if year:
            return str(year)
        
        # Try to extract from date field
        date = entry.get('date', '')
        if date:
            year_match = re.search(r'\b(19|20)\d{2}\b', date)
            if year_match:
                return year_match.group(0)
        
        return '2025'  # Default year
    
    def extract_month(self, entry: Dict[str, Any]) -> str:
        """Extract month from entry."""
        month = entry.get('month', '')
        if month:
            return str(month)
        
        # Try to extract from date field
        date = entry.get('date', '')
        if date:
            month_match = re.search(r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b', date, re.IGNORECASE)
            if month_match:
                return month_match.group(0)
        
        return '01'  # Default month
    
    def format_venue(self, entry: Dict[str, Any]) -> str:
        """Format venue information."""
        entry_type = entry.get('type', '').lower()
        
        if entry_type == 'article':
            return entry.get('journal', '')
        elif entry_type in ['inproceedings', 'incollection']:
            return entry.get('booktitle', '')
        elif entry_type in ['phdthesis', 'mastersthesis', 'thesis']:
            return entry.get('school', '')
        elif entry_type == 'techreport':
            return entry.get('institution', '')
        else:
            return entry.get('booktitle', '') or entry.get('journal', '') or entry.get('institution', '')
    
    def extract_keywords(self, entry: Dict[str, Any]) -> List[str]:
        """Extract and clean keywords."""
        keywords_str = entry.get('keywords', '')
        if not keywords_str:
            return []
        
        # Split by common delimiters
        keywords = re.split(r'[,;]', keywords_str)
        
        # Clean and filter
        cleaned_keywords = []
        for keyword in keywords:
            keyword = keyword.strip().lower()
            if keyword and not keyword.startswith('ignore'):
                cleaned_keywords.append(keyword)
        
        return cleaned_keywords
    
    def extract_links(self, entry: Dict[str, Any]) -> Dict[str, str]:
        """Extract various links from entry."""
        links = {}
        
        # Direct URL fields
        if entry.get('url'):
            links['url'] = entry['url']
        if entry.get('doi'):
            links['doi'] = f"https://doi.org/{entry['doi']}"
        if entry.get('arxiv'):
            links['arxiv'] = f"https://arxiv.org/abs/{entry['arxiv']}"
        
        # PDF and media files
        if entry.get('pdf'):
            links['pdf'] = entry['pdf']
        if entry.get('preview'):
            links['preview'] = entry['preview']
        if entry.get('video'):
            links['video'] = entry['video']
        if entry.get('slides'):
            links['slides'] = entry['slides']
        if entry.get('poster'):
            links['poster'] = entry['poster']
        
        # Extract URLs from note field
        note = entry.get('note', '')
        if note and 'http' in note:
            url_matches = re.findall(r'https?://[^\s]+', note)
            for i, url in enumerate(url_matches):
                if 'youtube' in url:
                    links['youtube'] = url
                elif 'amazon' in url:
                    links['amazon'] = url
                else:
                    links[f'link_{i+1}'] = url
        
        return links
    
    def extract_images(self, entry: Dict[str, Any]) -> List[str]:
        """Extract image files from entry."""
        images = []
        
        # Direct image fields
        if entry.get('preview'):
            images.append(entry['preview'])
        if entry.get('photos'):
            photos = entry['photos'].split(',')
            images.extend([photo.strip() for photo in photos if photo.strip()])
        
        # Extract from file field
        file_field = entry.get('file', '')
        if file_field:
            file_parts = file_field.split(';')
            for part in file_parts:
                part = part.strip()
                if any(ext in part.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                    # Extract filename from path
                    filename = part.split(':')[0] if ':' in part else part
                    images.append(filename)
        
        return [img for img in images if img]
    
    def get_abstract(self, entry: Dict[str, Any]) -> str:
        """Get abstract from entry."""
        abstract = entry.get('abstract', '')
        if abstract:
            # Preserve line breaks in abstract - only normalize multiple spaces to single spaces
            # but keep newlines intact
            abstract = re.sub(r'[ \t]+', ' ', abstract)  # Normalize spaces and tabs but preserve newlines
            return abstract.strip()
        return ''
    
    def get_description(self, entry: Dict[str, Any]) -> str:
        """Generate a description for the entry."""
        abstract = self.get_abstract(entry)
        if abstract:
            # Truncate abstract to reasonable length
            if len(abstract) > 200:
                return abstract[:200] + "..."
            return abstract
        
        # Fall back to title if no abstract
        title = self.clean_title(entry.get('title', ''))
        if len(title) > 100:
            return title[:100] + "..."
        return title
