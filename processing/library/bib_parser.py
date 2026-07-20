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
        
        # Direct URL fields (pipeline renames url → website)
        url_value = entry.get('url') or entry.get('website')
        if url_value:
            links['url'] = str(url_value).strip()
        if entry.get('doi'):
            doi = str(entry['doi']).strip()
            if doi.startswith('http'):
                links['doi'] = doi
            else:
                links['doi'] = f"https://doi.org/{doi}"
        if entry.get('arxiv'):
            links['arxiv'] = f"https://arxiv.org/abs/{entry['arxiv']}"
        
        # PDF and media files
        if entry.get('pdf'):
            links['pdf'] = str(entry['pdf']).strip()
        if entry.get('preview'):
            links['preview'] = str(entry['preview']).strip()
        if entry.get('video'):
            links['video'] = str(entry['video']).strip()
        if entry.get('slides'):
            links['slides'] = str(entry['slides']).strip()
        if entry.get('agenda'):
            links['agenda'] = str(entry['agenda']).strip()
        if entry.get('poster'):
            links['poster'] = str(entry['poster']).strip()
        
        # Extract PDF from file field if pdf field is not already set
        if not links.get('pdf') and entry.get('file'):
            pdf_filename = self._extract_pdf_from_file_field(entry['file'])
            if pdf_filename:
                links['pdf'] = pdf_filename
        
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
    
    def _extract_pdf_from_file_field(self, file_field: str) -> Optional[str]:
        """Extract PDF filename from a BibTeX file field.
        
        Returns the PDF filename if found, or None if no PDF is found.
        Note: This extracts the original filename from the file field. If the PDF
        has been processed, the processed filename (in the 'pdf' field) should be
        used instead. This method is a fallback when the 'pdf' field is missing.
        """
        if not file_field:
            return None
        
        import os
        
        # Split by semicolon and process each part
        # Note: BibTeX file fields use semicolons to separate multiple files
        for part in file_field.split(';'):
            part = part.strip()
            if not part:
                continue
            
            # Handle format: Description:path:mime or path:mime
            # The MIME type is always the last part after the last colon
            if ':' in part:
                # Find the last colon to separate path from mime type
                last_colon_idx = part.rfind(':')
                if last_colon_idx > 0:
                    mime_part = part[last_colon_idx + 1:].strip().lower()
                    
                    # Check if the MIME type indicates PDF
                    if 'application/pdf' in mime_part:
                        # Extract the path part (everything before the last colon)
                        path_part = part[:last_colon_idx].strip()
                        
                        # If there's a description prefix (like "PDF:"), remove it
                        # Format: Description:path, so find the first colon after the description
                        if ':' in path_part:
                            # There's a description, get the path after the first colon
                            first_colon_idx = path_part.find(':')
                            path_part = path_part[first_colon_idx + 1:].strip()
                        
                        if path_part:
                            # Handle escaped semicolons in filenames (BibTeX escaping)
                            path_part = path_part.replace('\\;', ';')
                            # Extract just the filename from the path
                            filename = os.path.basename(path_part)
                            
                            # Return the filename (may need to be matched to processed filename)
                            return filename
            else:
                # Simple case: just a filename ending with .pdf
                if part.lower().endswith('.pdf'):
                    # Handle escaped semicolons
                    part = part.replace('\\;', ';')
                    filename = os.path.basename(part.strip())
                    return filename
        
        return None
    
    def extract_images(self, entry: Dict[str, Any]) -> List[str]:
        """Extract image files from entry."""
        images = []
        
        # Invalid image names to filter out
        invalid_names = {'pdf', 'thumbnail', 'thumb', 'preview', 'image', 'photo', 'figure'}
        
        def is_valid_image_name(img_name: str) -> bool:
            """Check if an image name is valid."""
            if not img_name or not img_name.strip():
                return False
            
            img_lower = img_name.lower().strip()
            
            # Filter out invalid generic names
            if img_lower in invalid_names:
                return False
            
            # Must contain at least one character that's not just generic text
            # Valid image names typically have alphanumeric characters, underscores, hyphens
            # and should not be just generic words
            if len(img_lower) < 3:
                return False
            
            return True
        
        def clean_image_filename(filename: str) -> str:
            """Clean and normalize image filename by removing extension."""
            if not filename:
                return ''
            
            # Remove file extension if present (layout template adds paths)
            # Common image extensions
            extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
            filename_lower = filename.lower()
            for ext in extensions:
                if filename_lower.endswith(ext):
                    # Remove extension
                    return filename[:-len(ext)]
            
            return filename.strip()
        
        # Direct image fields
        if entry.get('preview'):
            preview = clean_image_filename(entry['preview'])
            if is_valid_image_name(preview):
                images.append(preview)
        
        if entry.get('photos'):
            photos = entry['photos'].split(',')
            for photo in photos:
                photo = clean_image_filename(photo.strip())
                if is_valid_image_name(photo):
                    images.append(photo)
        
        # Extract from file field
        file_field = entry.get('file', '')
        if file_field:
            file_parts = file_field.split(';')
            for part in file_parts:
                part = part.strip()
                if any(ext in part.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                    # Extract filename from path
                    filename = part.split(':')[0] if ':' in part else part
                    filename = clean_image_filename(filename)
                    if is_valid_image_name(filename):
                        images.append(filename)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_images = []
        for img in images:
            if img and img not in seen:
                seen.add(img)
                unique_images.append(img)
        
        return unique_images
    
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
