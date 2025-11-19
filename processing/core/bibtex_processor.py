#!/usr/bin/env python3
"""
BibTeXProcessor class for process_papers.py
Handles all BibTeX parsing, manipulation, and entry processing.
"""

import os
import re
import sys
from typing import Dict, List, Tuple, Optional

# Add the processing directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Configuration
from core.text_processor import TextProcessor
from core.notes_processor import NotesProcessor


class BibTeXProcessor:
    """Handles all BibTeX parsing and manipulation operations."""
    
    def __init__(self, config: Configuration = None, text_processor: TextProcessor = None):
        """Initialize with configuration and text processor."""
        self.config = config or Configuration()
        self.text_processor = text_processor or TextProcessor(config)
        self.notes_processor = NotesProcessor()
    
    def parse_bibtex_entry(self, content: str) -> Tuple[Optional[str], Dict[str, str]]:
        """Parse a single BibTeX entry and return the citation key and fields."""
        # First, try to fix malformed entries with duplicated entry types
        content = self._fix_duplicated_entry_types(content)
        
        # Extract citation key (e.g., @article{KEY,)
        key_match = re.search(r'@\w+\{([^,]+),', content)
        if not key_match:
            return None, {}
        
        citation_key = key_match.group(1).strip()
        # Clean the citation key to remove invalid characters
        citation_key = self.text_processor.clean_citation_key(citation_key)
        
        # Find the entry boundaries to limit field parsing to this entry only
        entry_start = key_match.start()
        entry_end = self._find_entry_end(content, entry_start)
        if entry_end == -1:
            return None, {}
        
        # Extract only the content of this entry
        entry_content = content[entry_start:entry_end]
        
        # Extract all fields with proper brace handling
        fields = {}
        
        # First, find all fields with braces (handle nested braces properly)
        pos = 0
        while True:
            # Find the next field start
            field_start_match = re.search(r'(\w+)\s*=\s*\{', entry_content[pos:])
            if not field_start_match:
                break
                
            field_name = field_start_match.group(1).strip()
            field_start = pos + field_start_match.end() - 1  # Position of the opening brace
            
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
            
            if brace_count == 0:  # Found matching closing brace
                field_value = entry_content[field_start + 1:field_end].strip()
                fields[field_name] = field_value
                pos = field_end + 1
            else:
                # Unmatched braces, skip this field
                pos = pos + field_start_match.end()
        
        # Then, find fields without braces (but not already processed)
        for match in re.finditer(r'(\w+)\s*=\s*([^{,\n][^,\n]*?)(?=,\s*\w+\s*=|$)', entry_content):
            field_name = match.group(1).strip()
            field_value = match.group(2).strip()
            
            # Only add if we don't already have this field, value is not empty, and doesn't start with {
            if field_name not in fields and field_value and not field_value.startswith('{'):
                fields[field_name] = field_value
        
        return citation_key, fields
    
    def _find_entry_end(self, content: str, start_pos: int) -> int:
        """Find the end position of a BibTeX entry starting at start_pos."""
        # Find the opening brace after the entry type
        brace_start = content.find('{', start_pos)
        if brace_start == -1:
            return -1
        
        # Count braces to find the matching closing brace
        brace_count = 1
        for i in range(brace_start + 1, len(content)):
            if content[i] == '{':
                brace_count += 1
            elif content[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    return i + 1
        
        return -1
    
    def parse_bibtex_entries(self, content: str) -> List[Dict]:
        """Parse all BibTeX entries from content and return list of entry dictionaries."""
        import re
        
        entries = []
        # Split content by entries (each entry starts with @)
        # Use a more robust splitting approach that handles blank lines
        entry_blocks = re.split(r'(?=\n\s*@\w+\{)', content)
        
        
        for block in entry_blocks:
            if not block.strip():
                continue
                
            # Clean up the block
            block = block.strip()
            
            # Skip if it doesn't start with @
            if not block.startswith('@'):
                continue
            
            citation_key, fields = self.parse_bibtex_entry(block)
            if citation_key and fields:
                entries.append({
                    'citation_key': citation_key,
                    'fields': fields,
                    'content': block
                })
        
        return entries
    
    def find_entry_bounds(self, content: str, citation_key: str) -> Tuple[int, int]:
        """Find the start and end positions of a BibTeX entry."""
        # Find the entry start
        entry_start_pattern = r'@\w+\{\s*' + re.escape(citation_key) + r'\s*,'
        start_match = re.search(entry_start_pattern, content)
        if not start_match:
            return -1, -1
        
        start_pos = start_match.start()
        
        # Find the closing brace of this entry by counting braces
        brace_start = content.find('{', start_pos)
        if brace_start == -1:
            return -1, -1
        
        brace_count = 1
        end_pos = brace_start + 1
        
        for i, char in enumerate(content[brace_start + 1:], brace_start + 1):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_pos = i + 1
                    break
        
        return start_pos, end_pos
    
    def add_tag_to_entry(self, content: str, citation_key: str, tag_name: str, tag_value: str) -> str:
        """Add a tag to a BibTeX entry."""
        start_pos, end_pos = self.find_entry_bounds(content, citation_key)
        if start_pos == -1:
            return content
        
        # Extract the entry content
        entry_content = content[start_pos:end_pos]
        
        # Check if tag already exists
        if f'{tag_name} =' in entry_content:
            return content
        
        # Find the last field before the closing brace
        last_field_match = None
        for match in re.finditer(r'\w+\s*=\s*(?:\{[^}]*\}|[^,\n]+)', entry_content):
            last_field_match = match
        
        if not last_field_match:
            return content
        
        # Check if the last field ends with a comma
        last_field_text = last_field_match.group(0)
        needs_comma = not last_field_text.rstrip().endswith(',')
        
        # Prepare tag to add
        if needs_comma:
            tag_to_add = f",\n\t{tag_name} = {{{tag_value}}}"
        else:
            tag_to_add = f"\n\t{tag_name} = {{{tag_value}}}"
        
        # Insert tag after the last field
        last_field_end = last_field_match.end()
        modified_entry = entry_content[:last_field_end] + tag_to_add + entry_content[last_field_end:]
        
        # Replace the entry in the content
        return content[:start_pos] + modified_entry + content[end_pos:]
    
    def add_multiple_tags(self, content: str, citation_key: str, tags: Dict[str, str]) -> str:
        """Add multiple tags to a BibTeX entry."""
        start_pos, end_pos = self.find_entry_bounds(content, citation_key)
        if start_pos == -1:
            return content
        
        # Extract the entry content
        entry_content = content[start_pos:end_pos]
        
        # Check which tags already exist
        existing_tags = set()
        for tag_name in tags.keys():
            if f'{tag_name} =' in entry_content:
                existing_tags.add(tag_name)
        
        # Filter out existing tags
        new_tags = {k: v for k, v in tags.items() if k not in existing_tags}
        if not new_tags:
            return content
        
        # Find the last field before the closing brace
        last_field_match = None
        for match in re.finditer(r'\w+\s*=\s*(?:\{[^}]*\}|[^,\n]+)', entry_content):
            last_field_match = match
        
        if not last_field_match:
            return content
        
        # Check if the last field ends with a comma
        last_field_text = last_field_match.group(0)
        needs_comma = not last_field_text.rstrip().endswith(',')
        
        # Prepare tags to add
        tags_to_add = ""
        for i, (tag_name, tag_value) in enumerate(new_tags.items()):
            if i == 0 and needs_comma:
                tags_to_add += f",\n\t{tag_name} = {{{tag_value}}}"
            else:
                tags_to_add += f",\n\t{tag_name} = {{{tag_value}}}"
        
        # Insert tags after the last field
        last_field_end = last_field_match.end()
        modified_entry = entry_content[:last_field_end] + tags_to_add + entry_content[last_field_end:]
        
        # Replace the entry in the content
        return content[:start_pos] + modified_entry + content[end_pos:]
    
    def clean_malformed_entries(self, content: str) -> str:
        """Clean up common malformed BibTeX entries."""
        print("🧹 Cleaning up malformed BibTeX entries...")
        
        # Split into entries
        entries = re.split(r'\n(?=@)', content)
        cleaned_entries = []
        
        for entry in entries:
            if not entry.strip():
                cleaned_entries.append(entry)
                continue
            
            # Clean braces from text fields
            cleaned_entry = self._clean_braces_from_fields(entry)
            
            # Apply individual entry cleaning
            cleaned_entry = self._clean_individual_entry(cleaned_entry)
            
            # Additional cleaning for common issues
            cleaned_entry = self._clean_additional_issues(cleaned_entry)
            
            if cleaned_entry:
                cleaned_entries.append(cleaned_entry)
        
        return '\n'.join(cleaned_entries)
    
    def _clean_braces_from_fields(self, entry: str) -> str:
        """Clean braces from text fields in an entry."""
        for field in self.config.TEXT_FIELDS_TO_CLEAN:
            pattern = rf'({field})\s*=\s*\{{'
            match = re.search(pattern, entry)
            if match:
                # Find the matching closing brace
                start_pos = match.end() - 1
                brace_count = 0
                end_pos = start_pos
                
                for i in range(start_pos, len(entry)):
                    if entry[i] == '{':
                        brace_count += 1
                    elif entry[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end_pos = i
                            break
                
                if brace_count == 0:
                    field_value = entry[start_pos + 1:end_pos]
                    cleaned_value = self.text_processor.clean_braces_in_field_value(field_value)
                    entry = entry[:start_pos + 1] + cleaned_value + entry[end_pos:]
        
        return entry
    
    def _clean_individual_entry(self, entry: str) -> str:
        """Clean an individual BibTeX entry."""
        if not entry.strip():
            return entry
        
        # Fix missing closing braces with better logic
        open_braces = entry.count('{')
        close_braces = entry.count('}')
        if open_braces > close_braces:
            missing_braces = open_braces - close_braces
            # Add missing braces at the end, but be smarter about it
            entry = entry.rstrip()
            # Remove any trailing commas before adding braces
            entry = re.sub(r',\s*$', '', entry)
            entry = entry + '\n' + '}' * missing_braces
            print(f"  🔧 Fixed {missing_braces} missing closing braces")
        elif close_braces > open_braces:
            # Too many closing braces - remove excess
            excess_braces = close_braces - open_braces
            # Remove excess closing braces from the end
            entry = entry.rstrip()
            for _ in range(excess_braces):
                if entry.endswith('}'):
                    entry = entry[:-1].rstrip()
            print(f"  🔧 Removed {excess_braces} excess closing braces")
        
        # Additional brace validation and fixing
        entry = self._fix_brace_issues(entry)
        
        # Fix malformed entry structure
        if not re.match(r'@\w+\{', entry.strip()):
            # Try to fix missing opening brace
            type_match = re.search(r'@(\w+)\s+([^,]+),', entry)
            if type_match:
                entry_type = type_match.group(1)
                entry_key = type_match.group(2)
                content_after_type = entry[type_match.end():]
                entry = f"@{entry_type}{{{entry_key},\n{content_after_type}"
            else:
                # If we can't fix it, try to preserve what we can
                type_match = re.search(r'@(\w+)\s+([^,\n]+)', entry)
                if type_match:
                    entry_type = type_match.group(1)
                    entry_key = type_match.group(2)
                    content_after_type = entry[type_match.end():]
                    entry = f"@{entry_type}{{{entry_key},\n{content_after_type}"
                else:
                    return entry  # Return original if we can't fix it
        
        # Fix missing commas between fields
        while True:
            new_entry = re.sub(
                r'(\w+\s*=\s*\{[^}]*\})\s*\n\s*(\w+\s*=\s*\{[^}]*\})',
                r'\1,\n\t\2',
                entry
            )
            if new_entry == entry:
                break
            entry = new_entry
        
        # Fix trailing and stray commas
        entry = self._fix_comma_issues(entry)
        
        # Fix improper escaping
        entry = self.fix_improper_escaping(entry)
        
        # Fix other common issues
        entry = re.sub(r'^\s*[a-zA-Z],\s*$', '', entry, flags=re.MULTILINE)
        entry = re.sub(r',\s*\n\s*}', '\n}', entry)
        
        return entry
    
    def _fix_brace_issues(self, entry: str) -> str:
        """Fix brace-related issues in BibTeX entries."""
        if not entry.strip():
            return entry
        
        # First, try to fix the entry by parsing it more carefully
        entry = self._fix_brace_issues_advanced(entry)
        
        # Then do the simple line-by-line fix as backup
        lines = entry.split('\n')
        fixed_lines = []
        brace_count = 0
        
        for line in lines:
            # Count braces in this line
            line_open = line.count('{')
            line_close = line.count('}')
            brace_count += line_open - line_close
            
            # If we have negative brace count, it means we have too many closing braces
            if brace_count < 0:
                # Remove excess closing braces from this line
                excess_close = abs(brace_count)
                for _ in range(excess_close):
                    if line.rstrip().endswith('}'):
                        line = line.rstrip()[:-1].rstrip()
                brace_count = 0
            
            fixed_lines.append(line)
        
        # If we still have unmatched braces at the end, add missing closing braces
        if brace_count > 0:
            fixed_lines.append('}' * brace_count)
        
        return '\n'.join(fixed_lines)
    
    def _fix_brace_issues_advanced(self, entry: str) -> str:
        """Advanced brace fixing by parsing the entry structure."""
        if not entry.strip():
            return entry
        
        # Find the entry type and citation key
        type_match = re.match(r'@(\w+)\s*\{\s*([^,]+)\s*,', entry)
        if not type_match:
            return entry
        
        entry_type = type_match.group(1)
        citation_key = type_match.group(2).strip()
        
        # Find the start of fields (after the comma)
        start_pos = type_match.end()
        
        # Find the matching closing brace for the entire entry
        brace_count = 1  # We already have one opening brace
        end_pos = start_pos
        
        for i in range(start_pos, len(entry)):
            if entry[i] == '{':
                brace_count += 1
            elif entry[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_pos = i + 1
                    break
        
        if brace_count != 0:
            # Unmatched braces - try to fix by adding missing closing braces
            if brace_count > 0:
                entry = entry.rstrip() + '\n' + '}' * brace_count
            else:
                # Too many closing braces - remove excess
                excess = abs(brace_count)
                entry = entry.rstrip()
                for _ in range(excess):
                    if entry.endswith('}'):
                        entry = entry[:-1].rstrip()
        
        return entry
    
    def _fix_comma_issues(self, entry: str) -> str:
        """Fix various comma-related issues in BibTeX entries."""
        # Remove double commas
        entry = re.sub(r',\s*,+', ',', entry)
        
        # Remove trailing comma before closing brace
        entry = re.sub(r',\s*\n\s*}', '\n}', entry)
        
        # Fix comma at start of line (move to end of previous line)
        entry = re.sub(r'\n\s*,\s*(\w+\s*=)', r',\n\t\1', entry)
        
        # Remove multiple consecutive commas
        entry = re.sub(r',{2,}', ',', entry)
        
        # Fix comma spacing
        entry = re.sub(r',\s*', ', ', entry)
        
        return entry
    
    def validate_bibtex(self, content: str) -> List[str]:
        """Validate BibTeX content and return list of issues."""
        issues = []
        
        # Check for unmatched braces
        brace_count = 0
        for char in content:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
        
        if brace_count != 0:
            issues.append(f"Unmatched braces: {brace_count} more {'{' if brace_count > 0 else '}'}")
        
        # Check for common syntax issues
        if re.search(r'}\s*\n\s*[a-zA-Z]', content):
            issues.append("Missing commas between fields")
        
        if re.search(r'pdf\s*=\s*\{[^}]*\}\s*\n\s*pdf\s*=\s*\{', content):
            issues.append("Duplicate pdf fields detected")
        
        return issues
    
    def rename_url_fields(self, content: str) -> Tuple[str, int]:
        """Rename 'url' fields to 'website' fields for Jekyll compatibility."""
        # Count existing url fields
        url_count = len(re.findall(r'\burl\s*=\s*\{', content))
        
        if url_count == 0:
            return content, 0
        
        # Replace 'url = {' with 'website = {'
        modified_content = re.sub(r'\burl\s*=\s*\{', 'website = {', content)
        
        # Also handle 'urldate' fields
        urldate_count = len(re.findall(r'\burldate\s*=\s*\{', modified_content))
        if urldate_count > 0:
            modified_content = re.sub(r'\burldate\s*=\s*\{', 'website_date = {', modified_content)
        
        return modified_content, url_count
    
    def extract_file_paths(self, file_field: str) -> List[str]:
        """Extract file paths from a BibTeX file field."""
        if not file_field:
            return []
        
        paths = []
        # Split by semicolon and process each part
        for part in file_field.split(';'):
            part = part.strip()
            if not part:  # Skip empty parts
                continue
                
            # Handle different formats: Description:path:mime or path:mime or just path
            if ':' in part:
                # Split by colon and take the middle part (path)
                parts = part.split(':')
                if len(parts) >= 2:
                    # Take the second part (index 1) as the path
                    path_part = parts[1].strip()
                    if path_part and self._is_valid_path(path_part):
                        paths.append(path_part)
                elif len(parts) == 1:
                    # Single part, might be just a path
                    if self._is_valid_path(parts[0]):
                        paths.append(parts[0].strip())
            else:
                # No colons, might be just a path
                if self._is_valid_path(part):
                    paths.append(part)
        
        return paths
    
    def extract_thumbnail_files(self, file_field: str) -> List[str]:
        """Extract thumbnail file paths from a BibTeX file field."""
        if not file_field:
            return []
        
        thumbnail_paths = []
        # Split by semicolon and process each part
        for part in file_field.split(';'):
            part = part.strip()
            if not part:  # Skip empty parts
                continue
                
            # Handle different formats: Description:path:mime or path:mime or just path
            if ':' in part:
                # Split by colon and check if it's a thumbnail file
                parts = part.split(':')
                if len(parts) >= 2:
                    # Check if the description contains "thumbnail" (case insensitive)
                    description = parts[0].strip().lower()
                    if 'thumbnail' in description:
                        path_part = parts[1].strip()
                        if path_part and self._is_valid_path(path_part):
                            thumbnail_paths.append(path_part)
            else:
                # Check if the filename itself contains "thumbnail"
                if 'thumbnail' in part.lower() and self._is_valid_path(part):
                    thumbnail_paths.append(part.strip())
        
        return thumbnail_paths
    
    def extract_pdf_files(self, file_field: str) -> List[str]:
        """Extract PDF file paths from a BibTeX file field."""
        if not file_field:
            return []
        
        pdf_paths = []
        # Split by semicolon and process each part
        for part in file_field.split(';'):
            part = part.strip()
            if not part:  # Skip empty parts
                continue
                
            # Handle different formats: Description:path:mime or path:mime or just path
            if ':' in part:
                # Split by colon and check if it's a PDF file
                parts = part.split(':')
                if len(parts) >= 2:
                    # Check if the MIME type indicates PDF
                    mime_type = parts[-1].strip().lower()
                    if 'application/pdf' in mime_type:
                        path_part = parts[1].strip()
                        if path_part and self._is_valid_path(path_part):
                            pdf_paths.append(path_part)
            else:
                # Check if the filename ends with .pdf
                if part.lower().endswith('.pdf') and self._is_valid_path(part):
                    pdf_paths.append(part.strip())
        
        return pdf_paths
    
    def extract_image_files(self, file_field: str) -> List[str]:
        """Extract image file paths from a BibTeX file field, excluding thumbnail files."""
        if not file_field:
            return []
        
        image_paths = []
        # Split by semicolon and process each part
        for part in file_field.split(';'):
            part = part.strip()
            if not part:  # Skip empty parts
                continue
            
            # Check if this is a thumbnail file (description contains 'thumbnail' or filename contains 'thumbnail')
            is_thumbnail = False
            if ':' in part:
                # Format: description:path:mime
                parts = part.split(':')
                if len(parts) >= 2:
                    description = parts[0].strip().lower()
                    if 'thumbnail' in description:
                        is_thumbnail = True
            else:
                # Format: path or filename
                if 'thumbnail' in part.lower():
                    is_thumbnail = True
            
            # Skip thumbnail files - they should be processed separately
            if is_thumbnail:
                continue
                
            # Handle different formats: Description:path:mime or path:mime or just path
            if ':' in part:
                # Split by colon and check if it's an image file
                parts = part.split(':')
                if len(parts) >= 2:
                    # Check if the MIME type indicates an image
                    mime_type = parts[-1].strip().lower()
                    if any(img_type in mime_type for img_type in ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']):
                        path_part = parts[1].strip()
                        if path_part and self._is_valid_path(path_part):
                            image_paths.append(path_part)
            else:
                # Check if the filename has an image extension
                if any(part.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']) and self._is_valid_path(part):
                    image_paths.append(part.strip())
        
        return image_paths
    
    def extract_agenda_pdfs(self, file_field: str) -> List[str]:
        """Extract PDF files with 'agenda' in the filename."""
        if not file_field:
            return []
        
        agenda_paths = []
        # Split by semicolon and process each part
        for part in file_field.split(';'):
            part = part.strip()
            if not part:  # Skip empty parts
                continue
                
            # Handle different formats: Description:path:mime or path:mime or just path
            if ':' in part:
                # Split by colon and check if it's an agenda PDF
                parts = part.split(':')
                if len(parts) >= 2:
                    # Check if the description contains "agenda" and MIME type indicates PDF
                    description = parts[0].strip().lower()
                    mime_type = parts[-1].strip().lower()
                    if 'agenda' in description and 'application/pdf' in mime_type:
                        path_part = parts[1].strip()
                        if path_part and self._is_valid_path(path_part):
                            agenda_paths.append(path_part)
            else:
                # Check if the filename contains "agenda" and ends with .pdf
                if 'agenda' in part.lower() and part.lower().endswith('.pdf') and self._is_valid_path(part):
                    agenda_paths.append(part.strip())
        
        return agenda_paths
    
    def extract_slides_pdfs(self, file_field: str) -> List[str]:
        """Extract PDF files with 'slides' in filename or description."""
        if not file_field:
            return []
        
        slides_paths = []
        # Split by semicolon and process each part
        for part in file_field.split(';'):
            part = part.strip()
            if not part:  # Skip empty parts
                continue
                
            # Handle different formats: Description:path:mime or path:mime or just path
            if ':' in part:
                # Split by colon and check if it's a slides PDF
                parts = part.split(':')
                if len(parts) >= 2:
                    # Check if the description contains "slides" and MIME type indicates PDF
                    description = parts[0].strip().lower()
                    mime_type = parts[-1].strip().lower()
                    if 'slides' in description and 'application/pdf' in mime_type:
                        path_part = parts[1].strip()
                        if path_part and self._is_valid_path(path_part):
                            slides_paths.append(path_part)
            else:
                # Check if the filename contains "slides" and ends with .pdf
                if 'slides' in part.lower() and part.lower().endswith('.pdf') and self._is_valid_path(part):
                    slides_paths.append(part.strip())
        
        return slides_paths
    
    def extract_most_recent_pdf(self, file_field: str) -> Optional[str]:
        """Extract the most recent PDF file based on modification time."""
        if not file_field:
            return None
        
        pdf_files = self.extract_pdf_files(file_field)
        if not pdf_files:
            return None
        
        # Find the most recently modified PDF
        most_recent = None
        most_recent_time = 0
        
        for pdf_path in pdf_files:
            try:
                if os.path.exists(pdf_path):
                    mod_time = os.path.getmtime(pdf_path)
                    if mod_time > most_recent_time:
                        most_recent_time = mod_time
                        most_recent = pdf_path
            except (OSError, FileNotFoundError):
                continue
        
        return most_recent
    
    def get_thumbnail_priority_files(self, file_field: str) -> List[Dict[str, str]]:
        """Get files for thumbnail generation in priority order.
        
        Returns list of dicts with 'path', 'type', and 'priority' keys.
        Priority: 1=thumbnail file, 2=agenda PDF, 3=most recent PDF
        """
        if not file_field:
            return []
        
        priority_files = []
        
        # Priority 1: Thumbnail files (SVG, PNG, etc.)
        thumbnail_paths = self.extract_thumbnail_files(file_field)
        for path in thumbnail_paths:
            if os.path.exists(path):
                file_ext = os.path.splitext(path)[1].lower()
                if file_ext == '.svg':
                    priority_files.append({'path': path, 'type': 'svg', 'priority': 1})
                elif file_ext in ['.png', '.jpg', '.jpeg']:
                    priority_files.append({'path': path, 'type': 'image', 'priority': 1})
        
        # Priority 2: Agenda PDFs
        agenda_paths = self.extract_agenda_pdfs(file_field)
        for path in agenda_paths:
            if os.path.exists(path):
                priority_files.append({'path': path, 'type': 'pdf', 'priority': 2})
        
        # Priority 3: Most recent PDF
        most_recent_pdf = self.extract_most_recent_pdf(file_field)
        if most_recent_pdf and most_recent_pdf not in [f['path'] for f in priority_files]:
            priority_files.append({'path': most_recent_pdf, 'type': 'pdf', 'priority': 3})
        
        # Sort by priority (lower number = higher priority)
        priority_files.sort(key=lambda x: x['priority'])
        return priority_files
    
    def _is_valid_path(self, path: str) -> bool:
        """Check if a string looks like a valid file path."""
        if not path or len(path.strip()) == 0:
            return False
        
        # Basic validation: should contain at least one character and not be just colons
        path = path.strip()
        if path in [':', '::', ':::', '::::']:
            return False
            
        # Should not be just special characters
        if re.match(r'^[^a-zA-Z0-9/\\\.\-_]+$', path):
            return False
        
        # Should look like a file path (contain at least one dot or slash)
        if not ('.' in path or '/' in path or '\\' in path):
            return False
            
        # Should not contain multiple slashes in a row (likely malformed)
        if re.search(r'[/\\]{2,}', path):
            return False
        
        # Should start with / or contain a proper file extension
        if not (path.startswith('/') or path.startswith('./') or '.' in path.split('/')[-1]):
            return False
            
        return True
    
    def fix_improper_escaping(self, content: str) -> str:
        """Fix common LaTeX escaping issues in BibTeX content."""
        # Fix double backslashes that should be single
        # Common patterns: \\& -> \&, \\$ -> \$, \\% -> \%, etc.
        common_escapes = ['&', '$', '%', '#', '^', '_', '{', '}']
        
        for char in common_escapes:
            # Fix \\char to \char
            pattern = rf'\\\\{re.escape(char)}'
            replacement = rf'\\{char}'
            content = re.sub(pattern, replacement, content)
        
        return content
    
    
    def process_notes_from_zotero(self, content: str) -> str:
        """
        Process Zotero notes and extract information into BibTeX fields.
        
        This method looks for entries that have notes with [type], [role], etc. sections
        and extracts that information into the appropriate BibTeX fields.
        
        Args:
            content: The BibTeX content
            
        Returns:
            Updated BibTeX content with extracted information
        """
        # Parse all entries
        entries = self._parse_all_entries(content)
        modified_entries = []
        
        for entry in entries:
            # Filter out snapshot attachments from file field
            if 'file' in entry and entry['file']:
                entry['file'] = self._filter_snapshot_attachments(entry['file'])
            
            # Check if this entry has notes with structured information
            # Only check 'annote' field (Zotero Notes field exports to 'annote')
            # Custom tags should only come from Zotero Notes field
            note_content = None
            if 'annote' in entry:
                note_content = entry['annote']
            
            # Always process notes to add BibTeX type fallback if needed
            entry = self.notes_processor.process_notes_for_entry(entry, note_content or '')
            
            # Convert back to BibTeX format
            formatted_entry = self._format_entry_to_bibtex(entry)
            modified_entries.append(formatted_entry)
        
        return '\n\n'.join(modified_entries)
    
    def _filter_snapshot_attachments(self, file_field: str) -> str:
        """
        Filter out snapshot attachments from the file field.
        
        Zotero creates snapshot attachments for web pages that we want to exclude
        from the processed bibliography.
        
        Args:
            file_field: The file field content
            
        Returns:
            File field content with snapshot attachments removed
        """
        if not file_field:
            return file_field
        
        # Split by semicolon and filter out snapshot entries
        file_parts = file_field.split(';')
        filtered_parts = []
        
        for part in file_parts:
            part = part.strip()
            if not part:
                continue
            
            # Check if this is a snapshot attachment
            # Snapshot attachments typically have "Snapshot:" or "text/html" in them
            is_snapshot = (
                'Snapshot:' in part or 
                'text/html' in part or
                'snapshot' in part.lower()
            )
            
            if not is_snapshot:
                filtered_parts.append(part)
        
        # Return the filtered file field
        if filtered_parts:
            return '; '.join(filtered_parts)
        else:
            return ''
    
    def _parse_all_entries(self, content: str) -> List[Dict[str, str]]:
        """Parse all BibTeX entries from content."""
        entries = []
        
        # Find all @type{key, ... } entries
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
        
        return entries
    
    def _parse_entry_fields(self, entry_content: str) -> Dict[str, str]:
        """Parse fields from a single BibTeX entry."""
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
    
    def _format_entry_to_bibtex(self, entry: Dict[str, str]) -> str:
        """Format an entry dictionary back to BibTeX format."""
        entry_type = entry.get('ENTRYTYPE', 'misc')
        citation_key = entry.get('ID', 'unknown')
        
        lines = [f"@{entry_type}{{{citation_key},"]
        
        # Add all fields except ENTRYTYPE and ID
        field_names = [k for k in entry.keys() if k not in ['ENTRYTYPE', 'ID']]
        for i, field_name in enumerate(field_names):
            field_value = entry[field_name]
            if i == len(field_names) - 1:
                lines.append(f"\t{field_name} = {{{field_value}}}")
            else:
                lines.append(f"\t{field_name} = {{{field_value}}},")
        
        lines.append("}")
        
        return '\n'.join(lines)
    
    def _fix_duplicated_entry_types(self, content: str) -> str:
        """Fix malformed entries with duplicated entry types like @news{article{..."""
        # Pattern to match duplicated entry types: @type1{type2{key, (with optional spaces)
        pattern = r'@(\w+)\s*\{\s*(\w+)\s*\{\s*([^,]+),'
        
        def fix_duplicate(match):
            type1 = match.group(1)
            type2 = match.group(2)
            key = match.group(3)
            # Use the second type (usually the correct one) and fix the structure
            # But preserve the original multi-word type in a comment for later processing
            return f"@{type2}{{{key}, % ORIGINAL_TYPE: {type1} {type2}"
        
        # Apply the fix
        fixed_content = re.sub(pattern, fix_duplicate, content)
        
        # If we made a change, log it
        if fixed_content != content:
            print(f"  🔧 Fixed duplicated entry type: {content[:50]}...")
        
        return fixed_content
    
    def _clean_additional_issues(self, entry: str) -> str:
        """Clean additional common issues in BibTeX entries."""
        if not entry.strip():
            return entry
        
        # Fix comma at start of line (move to end of previous line)
        entry = re.sub(r'\n\s*,\s*(\w+\s*=)', r',\n\t\1', entry)
        
        # Fix missing commas between fields
        entry = re.sub(r'}\s*\n\s*(\w+\s*=)', r'},\n\t\1', entry)
        
        # Fix double commas
        entry = re.sub(r',\s*,+', ',', entry)
        
        # Fix trailing comma before closing brace
        entry = re.sub(r',\s*\n\s*}', '\n}', entry)
        
        # Fix multiple consecutive commas
        entry = re.sub(r',{2,}', ',', entry)
        
        # Fix comma spacing
        entry = re.sub(r',\s*', ', ', entry)
        
        # Fix empty field values
        entry = re.sub(r'=\s*\{\s*\}\s*,?', '= {},\n', entry)
        
        # Fix invalid characters in citation keys
        # This is a more complex fix that would need to be handled carefully
        
        return entry
    