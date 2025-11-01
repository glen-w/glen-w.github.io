#!/usr/bin/env python3
"""
TextProcessor class for process_papers.py
Handles all text cleaning, normalization, and processing operations.
"""

import re
import sys
import os
from typing import Dict, List, Optional

# Add the processing directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Configuration

# Import slugify for proper accent handling
try:
    from slugify import slugify
except ImportError:
    # Fallback if slugify is not available
    def slugify(text, **kwargs):
        """Fallback slugify function if python-slugify is not available."""
        return re.sub(r'[^\w\s-]', '', text.lower()) \
               .replace(' ', '-') \
               .replace('--', '-') \
               .strip('-')


class TextProcessor:
    """Handles all text processing and cleaning operations."""
    
    def __init__(self, config: Configuration = None):
        """Initialize with configuration."""
        self.config = config or Configuration()
    
    def clean_nested_braces(self, text: str) -> str:
        """Remove internal braces from text while preserving outer braces for BibTeX fields."""
        if not text:
            return ""
        
        # If the text is already wrapped in braces, preserve them and clean internal ones
        if text.startswith('{') and text.endswith('}'):
            # Extract content inside outer braces
            inner_content = text[1:-1]
            # Clean internal braces from the inner content
            cleaned_inner = self._clean_internal_braces_only(inner_content)
            return f"{{{cleaned_inner}}}"
        else:
            # If not wrapped in braces, clean all braces
            return self._clean_internal_braces_only(text)
    
    def clean_braces_in_field_value(self, field_value: str) -> str:
        """Clean braces in a field value, ensuring proper matching."""
        if not field_value:
            return ""
        
        # Normalize to ASCII first to avoid encoding issues
        field_value = self.normalize_to_ascii(field_value)
        
        # If the field value is wrapped in braces, remove the outer braces and clean internal ones
        if field_value.startswith('{') and field_value.endswith('}'):
            inner_content = field_value[1:-1]
            cleaned_inner = self._clean_internal_braces_only(inner_content)
            return cleaned_inner
        else:
            # If not wrapped in braces, just clean internal braces (don't add outer braces)
            cleaned = self._clean_internal_braces_only(field_value)
            return cleaned
    
    def _clean_internal_braces_only(self, text: str) -> str:
        """Remove internal braces from text, preserving the content inside."""
        if not text:
            return ""
        
        # Remove the innermost braces first, working outward
        while re.search(r'\{[^{}]*\}', text):
            text = re.sub(r'\{([^{}]*)\}', r'\1', text)
        
        # Remove any remaining unmatched braces
        text = re.sub(r'\{', '', text)
        text = re.sub(r'\}', '', text)
        
        return text.strip()
    
    def clean_title_for_filename(self, title: str) -> str:
        """Clean a title for use in filenames."""
        if not title:
            return ""
        
        # Remove LaTeX commands and braces
        title = re.sub(r'\\[a-zA-Z]+', '', title)
        title = self.clean_nested_braces(title)
        
        # Remove special characters and replace with underscores
        title = re.sub(r'[^a-zA-Z0-9\s\-]', '_', title)
        title = re.sub(r'\s+', '_', title)
        # Remove dashes and replace with underscores
        title = re.sub(r'-+', '_', title)
        title = re.sub(r'_+', '_', title)
        title = re.sub(r'^_|_$', '', title)
        
        # Apply length limit
        if len(title) > self.config.MAX_TITLE_LENGTH:
            title = self.truncate_at_word_boundary(title, self.config.MAX_TITLE_LENGTH)
        
        return title
    
    def slugify_title(self, title: str, max_length: int = 50) -> str:
        """Create URL-friendly slug from title with proper accent handling."""
        if not title:
            return ""
        
        # Remove LaTeX commands and braces first
        title = re.sub(r'\\[a-zA-Z]+', '', title)
        title = self.clean_nested_braces(title)
        
        # Use python-slugify for proper accent handling
        slug = slugify(
            title,
            max_length=max_length,
            word_boundary=True,
            save_order=True,
            separator='-',
            lowercase=True
        )
        
        return slug
    
    def clean_title_for_bibtex(self, title: str) -> str:
        """Clean a title for use in BibTeX entries (normalizes to ASCII)."""
        if not title:
            return ""
        
        # Normalize to ASCII first to avoid encoding issues
        title = self.normalize_to_ascii(title)
        
        # Remove LaTeX commands
        title = re.sub(r'\\[a-zA-Z]+', '', title)
        
        # Remove curly braces but preserve their contents
        title = re.sub(r'\{([^}]*)\}', r'\1', title)
        
        # Normalize whitespace
        title = re.sub(r'\s+', ' ', title)
        title = title.strip()
        
        return title
    
    def remove_filler_words(self, title: str) -> str:
        """Remove common filler words from titles to make filenames more concise."""
        if not title:
            return ""
        
        # Split title into words
        words = title.split()
        
        # Filter out filler words (case insensitive)
        filtered_words = [word for word in words if word.lower() not in self.config.FILLER_WORDS]
        
        # Join back together
        return ' '.join(filtered_words)
    
    def extract_author_names_for_filename(self, author: str) -> str:
        """Extract author names for use in filenames based on whether Glen Wright is first author."""
        if not author:
            return ""
        
        # Split by 'and' to get individual authors
        authors = [a.strip() for a in author.split(' and ')]
        
        # Check if Glen Wright is the first author
        first_author = authors[0].lower()
        is_glen_wright_first = 'wright' in first_author and 'glen' in first_author
        
        if is_glen_wright_first:
            if len(authors) == 1:
                return "glen_wright"
            else:
                return "glen_wright_etal"
        else:
            return ""
    
    def extract_journal_or_publisher_for_filename(self, fields: Dict[str, str]) -> str:
        """Extract journal, institution, or publisher name for use in filenames."""
        # Priority order: journal, institution, publisher
        for field_name in ['journal', 'institution', 'publisher']:
            if field_name in fields and fields[field_name]:
                value = fields[field_name]
                
                # Remove LaTeX commands and braces
                value = re.sub(r'\\[a-zA-Z]+', '', value)
                value = self.clean_nested_braces(value)
                
                # Remove special characters and replace with underscores
                value = re.sub(r'[^\w\s\-]', '_', value)
                value = re.sub(r'\s+', '_', value)
                # Remove dashes and replace with underscores
                value = re.sub(r'-+', '_', value)
                value = re.sub(r'_+', '_', value)
                value = re.sub(r'^_|_$', '', value)
                
                # Limit length
                if len(value) > self.config.MAX_JOURNAL_LENGTH:
                    value = value[:self.config.MAX_JOURNAL_LENGTH]
                
                return value.lower()
        
        return ""
    
    def clean_filename(self, filename: str) -> str:
        """Clean a filename by removing invalid characters."""
        if not filename:
            return ""
        
        # Remove braces and other special characters, replace with underscores
        filename = re.sub(r'[^\w\-_.]', '_', filename)
        # Remove dashes and replace with underscores
        filename = re.sub(r'-+', '_', filename)
        filename = re.sub(r'_+', '_', filename)
        filename = re.sub(r'^_|_$', '', filename)
        
        return filename.lower()
    
    def truncate_at_word_boundary(self, text: str, max_length: int) -> str:
        """Truncate text at word boundary to avoid cutting words in half."""
        if not text or len(text) <= max_length:
            return text
        
        # Find the last underscore before the max_length
        truncated = text[:max_length]
        last_underscore = truncated.rfind('_')
        
        # If we found an underscore and it's not at the very beginning
        if last_underscore > 0:
            # Truncate at the last complete word (before the underscore)
            return text[:last_underscore]
        else:
            # If no underscore found, just truncate at max_length
            return text[:max_length]
    
    def truncate_filename_at_word_boundary(self, filename: str, max_length: int) -> str:
        """Truncate filename at word boundary to avoid cutting words in half."""
        if not filename or len(filename) <= max_length:
            return filename
        
        # Find the last underscore before the max_length
        truncated = filename[:max_length]
        last_underscore = truncated.rfind('_')
        
        # If we found an underscore and it's not at the very beginning
        if last_underscore > 0:
            # Truncate at the last complete word (before the underscore)
            return filename[:last_underscore] + '.pdf'
        else:
            # If no underscore found, just truncate at max_length
            return filename[:max_length]
    
    def truncate_abstract(self, abstract: str) -> str:
        """Truncate abstract to maximum length."""
        if not abstract:
            return ""
        
        if len(abstract) > self.config.MAX_ABSTRACT_LENGTH:
            return abstract[:self.config.MAX_ABSTRACT_LENGTH] + "..."
        
        return abstract
    
    def normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace in text."""
        if not text:
            return ""
        
        # Normalize line endings
        text = re.sub(r'\r\n', '\n', text)
        text = re.sub(r'\r', '\n', text)
        
        # Remove excessive blank lines
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        
        # Normalize spaces and tabs
        text = re.sub(r'[ \t]+', ' ', text)
        
        return text.strip()
    
    def normalize_to_ascii(self, text: str) -> str:
        """Normalize text to ASCII by replacing common non-ASCII characters."""
        if not text:
            return ""
        
        # Character replacements for common non-ASCII characters
        replacements = {
            # Smart quotes
            '"': '"',  # Left double quotation mark
            '"': '"',  # Right double quotation mark
            ''': "'",  # Left single quotation mark
            ''': "'",  # Right single quotation mark
            '‚': ',',  # Single low-9 quotation mark
            '„': '"',  # Double low-9 quotation mark
            '‹': "'",  # Single left-pointing angle quotation mark
            '›': "'",  # Single right-pointing angle quotation mark
            '«': '"',  # Left-pointing double angle quotation mark
            '»': '"',  # Right-pointing double angle quotation mark
            
            # Dashes
            '–': '-',  # En dash
            '—': '-',  # Em dash
            '―': '-',  # Horizontal bar
            
            # Ellipsis
            '…': '...',  # Horizontal ellipsis
            
            # Accented characters
            'à': 'a', 'á': 'a', 'â': 'a', 'ã': 'a', 'ä': 'a', 'å': 'a', 'æ': 'ae',
            'À': 'A', 'Á': 'A', 'Â': 'A', 'Ã': 'A', 'Ä': 'A', 'Å': 'A', 'Æ': 'AE',
            'è': 'e', 'é': 'e', 'ê': 'e', 'ë': 'e',
            'È': 'E', 'É': 'E', 'Ê': 'E', 'Ë': 'E',
            'ì': 'i', 'í': 'i', 'î': 'i', 'ï': 'i',
            'Ì': 'I', 'Í': 'I', 'Î': 'I', 'Ï': 'I',
            'ò': 'o', 'ó': 'o', 'ô': 'o', 'õ': 'o', 'ö': 'o', 'ø': 'o', 'œ': 'oe',
            'Ò': 'O', 'Ó': 'O', 'Ô': 'O', 'Õ': 'O', 'Ö': 'O', 'Ø': 'O', 'Œ': 'OE',
            'ù': 'u', 'ú': 'u', 'û': 'u', 'ü': 'u',
            'Ù': 'U', 'Ú': 'U', 'Û': 'U', 'Ü': 'U',
            'ý': 'y', 'ÿ': 'y',
            'Ý': 'Y', 'Ÿ': 'Y',
            'ñ': 'n', 'Ñ': 'N',
            'ç': 'c', 'Ç': 'C',
            
            # Non-breaking space
            '\xa0': ' ',  # Non-breaking space
            
            # Other common characters
            '°': ' degrees',  # Degree sign
            '±': '+/-',  # Plus-minus sign
            '×': 'x',  # Multiplication sign
            '÷': '/',  # Division sign
            '©': '(c)',  # Copyright sign
            '®': '(R)',  # Registered trademark sign
            '™': '(TM)',  # Trademark sign
        }
        
        # Apply replacements
        for old_char, new_char in replacements.items():
            text = text.replace(old_char, new_char)
        
        return text
    
    def clean_text_field(self, field_value: str, field_type: str = 'general') -> str:
        """Clean a text field based on its type."""
        if not field_value:
            return ""
        
        # Apply basic cleaning
        cleaned = self.clean_nested_braces(field_value)
        
        # Apply type-specific cleaning
        if field_type == 'filename':
            cleaned = self.clean_title_for_filename(cleaned)
        elif field_type == 'bibtex':
            cleaned = self.clean_title_for_bibtex(cleaned)
        elif field_type == 'general':
            cleaned = self.clean_title_for_bibtex(cleaned)
        
        return cleaned
    
    def generate_cache_key(self, title: str, author: str) -> str:
        """Generate a cache key for a paper based on title and author."""
        import hashlib
        
        # Normalize title and author for consistent caching
        clean_title = re.sub(r'[^\w\s]', '', title.lower().strip())
        clean_author = re.sub(r'[^\w\s]', '', author.lower().strip())
        
        # Create a hash of the normalized title and author
        cache_string = f"{clean_title}|{clean_author}"
        return hashlib.md5(cache_string.encode('utf-8')).hexdigest()
    
    def generate_filename(self, citation_key: str, fields: Dict[str, str], file_type: str = 'pdf') -> Optional[str]:
        """Generate a filename for a file based on BibTeX entry fields."""
        try:
            # Extract basic information
            title = fields.get('title', '')
            author = fields.get('author', '')
            year = fields.get('year', '')
            
            if not title:
                print(f"  ⚠️  No title found for {citation_key}")
                return None
            
            # Clean and format components
            # First remove filler words to make title more concise
            condensed_title = self.remove_filler_words(title)
            clean_title = self.clean_title_for_filename(condensed_title)
            clean_author = self.clean_author_for_filename(author)
            
            # Generate filename components
            filename_parts = []
            
            # Add author (first author only) - omit if no author
            if clean_author:
                filename_parts.append(clean_author)
            
            # Add year - omit if no year
            if year:
                filename_parts.append(year)
            
            # Add title (truncated to 130 characters at word boundary)
            if len(clean_title) > 130:
                clean_title = self.truncate_at_word_boundary(clean_title, 130)
            filename_parts.append(clean_title)
            
            # Note: Journal title is intentionally excluded from filename
            
            # Join parts and add extension
            base_filename = '_'.join(filename_parts)
            
            # Clean the filename to remove any invalid characters
            base_filename = self.clean_filename(base_filename)
            
            # Add appropriate extension
            if file_type == 'pdf':
                return f"{base_filename}.pdf"
            elif file_type in ['jpeg', 'jpg']:
                return f"{base_filename}.jpeg"
            else:
                return f"{base_filename}.{file_type}"
                
        except Exception as e:
            print(f"  ❌ Error generating filename for {citation_key}: {e}")
            return None
    
    def clean_author_for_filename(self, author: str) -> str:
        """Clean author string for use in filenames."""
        if not author:
            return ''
        
        # Clean nested braces first
        author = self.clean_nested_braces(author)
        
        # Split by 'and' to get first author
        authors = [a.strip() for a in author.split(' and ')]
        first_author = authors[0] if authors else ''
        
        # Extract first name and last name
        name_parts = first_author.split(',')
        if len(name_parts) >= 2:
            last_name = name_parts[0].strip()
            first_name = name_parts[1].strip()
            return f"{first_name.lower()}_{last_name.lower()}"
        else:
            # If no comma, try to split by space
            name_parts = first_author.split()
            if len(name_parts) >= 2:
                first_name = name_parts[0].strip()
                last_name = name_parts[-1].strip()
                return f"{first_name.lower()}_{last_name.lower()}"
            else:
                return first_author.lower().replace(' ', '_')
    
    def clean_citation_key(self, citation_key: str) -> str:
        """Clean citation key to remove invalid characters."""
        if not citation_key:
            return ""
        
        # Remove braces and other invalid characters, keep only alphanumeric, underscores, colons, and hyphens
        cleaned = re.sub(r'[^a-zA-Z0-9_:-]', '', citation_key)
        
        # Remove multiple consecutive underscores
        cleaned = re.sub(r'_+', '_', cleaned)
        
        # Remove leading/trailing underscores
        cleaned = cleaned.strip('_')
        
        # Ensure it's not empty
        if not cleaned:
            cleaned = "unknown"
        
        return cleaned