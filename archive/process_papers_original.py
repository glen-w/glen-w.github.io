#!/usr/bin/env python3
"""
Script to process papers from Zotero export:
1. Copy _bibliography/Exported Items.bib to _bibliography/papers.bib
2. Parse BibTeX entries with proper nested brace handling
3. Copy PDF files to assets/pdf with renamed filenames
4. Generate thumbnail previews for each PDF
5. Add pdf/slides and preview tags to BibTeX entries (slides for presentations, pdf for papers)
6. Add dimensions=true and altmetric=true tags to entries with DOI for citation tracking
7. Update PDF metadata with BibTeX information
8. Support regenerate mode to clean existing files and start fresh
"""

import os
import re
import shutil
import sys
import subprocess
import argparse
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import requests
import json
from typing import Dict, List, Optional, Tuple

# Global cache for metadata to avoid redundant API calls
METADATA_CACHE = {}
CACHE_FILE = "_metadata_cache.json"

def load_metadata_cache():
    """Load metadata cache from file if it exists."""
    global METADATA_CACHE
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                METADATA_CACHE = json.load(f)
            print(f"  📚 Loaded metadata cache with {len(METADATA_CACHE)} entries")
        except Exception as e:
            print(f"  ⚠️  Could not load metadata cache: {e}")
            METADATA_CACHE = {}
    else:
        METADATA_CACHE = {}

def save_metadata_cache():
    """Save metadata cache to file."""
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(METADATA_CACHE, f, indent=2, ensure_ascii=False)
        print(f"  💾 Saved metadata cache with {len(METADATA_CACHE)} entries")
    except Exception as e:
        print(f"  ⚠️  Could not save metadata cache: {e}")

def generate_cache_key(title: str, author: str) -> str:
    """Generate a cache key for a paper based on title and author."""
    # Normalize title and author for consistent caching
    clean_title = re.sub(r'[^\w\s]', '', title.lower().strip())
    clean_author = re.sub(r'[^\w\s]', '', author.lower().strip())
    
    # Create a hash of the normalized title and author
    cache_string = f"{clean_title}|{clean_author}"
    return hashlib.md5(cache_string.encode('utf-8')).hexdigest()

def is_metadata_complete(fields: Dict[str, str]) -> bool:
    """Check if metadata is complete enough to skip API calls."""
    # Define required fields for completeness
    required_fields = ['doi', 'abstract', 'keywords', 'journal']
    
    # Count how many required fields are present and non-empty
    present_fields = 0
    for field in required_fields:
        if field in fields and fields[field] and fields[field].strip():
            present_fields += 1
    
    # Consider metadata complete if at least 3 out of 4 required fields are present
    # This allows for some flexibility while still ensuring good coverage
    return present_fields >= 3

def should_fetch_metadata(fields: Dict[str, str], force_refetch: bool = False, verbose: bool = False) -> bool:
    """Determine if metadata should be fetched from external APIs."""
    if force_refetch:
        if verbose:
            print(f"    🔄 Force refetch enabled - will fetch metadata")
        return True
    
    # Check if metadata is already complete
    if is_metadata_complete(fields):
        if verbose:
            print(f"    ✅ Metadata already complete - skipping API calls")
        return False
    
    # Check if we have the most critical fields (DOI and abstract)
    has_doi = fields.get('doi') and fields['doi'].strip()
    has_abstract = fields.get('abstract') and fields['abstract'].strip()
    
    if has_doi and has_abstract:
        if verbose:
            print(f"    ✅ Has DOI and abstract - skipping API calls")
        return False
    
    if verbose:
        missing_fields = []
        if not has_doi:
            missing_fields.append('DOI')
        if not has_abstract:
            missing_fields.append('abstract')
        if not fields.get('keywords'):
            missing_fields.append('keywords')
        if not fields.get('journal'):
            missing_fields.append('journal')
        print(f"    📡 Missing fields: {', '.join(missing_fields)} - will fetch metadata")
    
    return True

def check_dependencies():
    """Check if required dependencies are available."""
    print("🔍 Checking required dependencies...")
    
    # Check PyPDF2 for PDF metadata
    try:
        import PyPDF2
        print("  ✅ PyPDF2 is available")
        return True
    except ImportError:
        print("  ❌ PyPDF2 not found - install with: pip install PyPDF2")
        return False
    
    # Check if ImageMagick is available
    magick_available = False
    try:
        result = subprocess.run(['magick', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✅ ImageMagick (magick) is available")
            magick_available = True
        else:
            print("  ⚠️  ImageMagick (magick) command failed")
    except FileNotFoundError:
        print("  ⚠️  ImageMagick (magick) not found")
    
    # Check legacy convert command as fallback
    convert_available = False
    try:
        result = subprocess.run(['convert', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✅ ImageMagick (convert) is available")
            convert_available = True
        else:
            print("  ⚠️  ImageMagick (convert) command failed")
    except FileNotFoundError:
        print("  ⚠️  ImageMagick (convert) not found")
    
    if not magick_available and not convert_available:
        print("  ❌ ImageMagick not found - thumbnail generation will not work")
        print("     Install ImageMagick: https://imagemagick.org/script/download.php")
        return False
    
    return True

def clean_nested_braces(text: str) -> str:
    """Remove all nested braces from text, preserving the content inside."""
    if not text:
        return ""
    
    # Remove the innermost braces first, working outward
    while re.search(r'\{[^{}]*\}', text):
        text = re.sub(r'\{([^{}]*)\}', r'\1', text)
    
    # Remove any remaining unmatched braces
    text = re.sub(r'\{', '', text)
    text = re.sub(r'\}', '', text)
    
    return text.strip()

def parse_bibtex_entry(content: str) -> Tuple[str, Dict[str, str]]:
    """Parse a single BibTeX entry and return the citation key and fields."""
    # Extract citation key (e.g., @article{KEY,)
    key_match = re.search(r'@\w+\{([^,]+),', content)
    if not key_match:
        return None, {}
    
    citation_key = key_match.group(1).strip()
    
    # Extract all fields with proper brace handling
    fields = {}
    
    # First, find all fields with braces (handle nested braces properly)
    pos = 0
    while True:
        # Find the next field start
        field_start_match = re.search(r'(\w+)\s*=\s*\{', content[pos:])
        if not field_start_match:
            break
            
        field_name = field_start_match.group(1).strip()
        field_start = pos + field_start_match.end() - 1  # Position of the opening brace
        
        # Find the matching closing brace
        brace_count = 0
        field_end = field_start
        
        for i in range(field_start, len(content)):
            if content[i] == '{':
                brace_count += 1
            elif content[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    field_end = i
                    break
        
        if brace_count == 0:  # Found matching closing brace
            field_value = content[field_start + 1:field_end].strip()
            fields[field_name] = field_value
            pos = field_end + 1
        else:
            # Unmatched braces, skip this field
            pos = pos + field_start_match.end()
    
    # Then, find fields without braces (but not already processed)
    # Use a simpler regex to avoid catastrophic backtracking
    for match in re.finditer(r'(\w+)\s*=\s*([^{,\n][^,\n]*?)(?=,\s*\w+\s*=|$)', content):
        field_name = match.group(1).strip()
        field_value = match.group(2).strip()
        
        # Only add if we don't already have this field, value is not empty, and doesn't start with {
        if field_name not in fields and field_value and not field_value.startswith('{'):
            fields[field_name] = field_value
    
    return citation_key, fields

def clean_title_for_filename(title: str) -> str:
    """Clean a title for use in filenames."""
    if not title:
        return ""
    
    # Remove LaTeX commands and braces
    title = re.sub(r'\\[a-zA-Z]+', '', title)
    title = re.sub(r'\{([^}]*)\}', r'\1', title)
    
    # Remove special characters and replace with underscores (only allow ASCII alphanumeric, spaces, and hyphens)
    title = re.sub(r'[^a-zA-Z0-9\s\-]', '_', title)
    title = re.sub(r'\s+', '_', title)
    title = re.sub(r'_+', '_', title)
    title = re.sub(r'^_|_$', '', title)
    
    # Limit length
    if len(title) > 50:
        title = title[:50]
    
    return title

def clean_title_for_bibtex(title: str) -> str:
    """Clean a title for use in BibTeX entries (preserves special characters)."""
    if not title:
        return ""
    
    # Remove LaTeX commands
    title = re.sub(r'\\[a-zA-Z]+', '', title)
    
    # Remove curly braces but preserve their contents
    title = re.sub(r'\{([^}]*)\}', r'\1', title)
    
    # Normalize whitespace (multiple spaces to single space)
    title = re.sub(r'\s+', ' ', title)
    title = title.strip()
    
    return title

def remove_filler_words(title: str) -> str:
    """Remove common filler words from titles to make filenames more concise."""
    if not title:
        return ""
    
    # Common filler words to remove (case insensitive)
    filler_words = {
        'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below',
        'up', 'down', 'out', 'off', 'over', 'under', 'again', 'further', 'then', 'once',
        'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
        'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'shall'
    }
    
    # Split title into words
    words = title.split()
    
    # Filter out filler words (case insensitive)
    filtered_words = [word for word in words if word.lower() not in filler_words]
    
    # Join back together
    return ' '.join(filtered_words)

def extract_author_names_for_filename(author: str) -> str:
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
            # Single author: glen_wright
            return "glen_wright"
        else:
            # Multiple authors: glen_wright_etal
            return "glen_wright_etal"
    else:
        # Glen Wright is not first author: return empty string (will use title only)
        return ""

def extract_journal_or_publisher_for_filename(fields: Dict[str, str]) -> str:
    """Extract journal, institution, or publisher name for use in filenames in order of preference."""
    # Priority order: journal, institution, publisher
    for field_name in ['journal', 'institution', 'publisher']:
        if field_name in fields and fields[field_name]:
            value = fields[field_name]
            
            # Remove LaTeX commands and braces
            value = re.sub(r'\\[a-zA-Z]+', '', value)
            value = re.sub(r'\{([^}]*)\}', r'\1', value)
            
            # Remove special characters and replace with underscores
            value = re.sub(r'[^\w\s\-]', '_', value)
            value = re.sub(r'\s+', '_', value)
            value = re.sub(r'_+', '_', value)
            value = re.sub(r'^_|_$', '', value)
            
            # Limit length
            if len(value) > 30:
                value = value[:30]
            
            return value.lower()
    
    return ""

def extract_file_paths(file_field: str) -> List[str]:
    """Extract file paths from a BibTeX file field."""
    if not file_field:
        return []
    
    paths = []
    # Split by semicolon and extract the file paths
    for part in file_field.split(';'):
        if ':' in part:
            # Format: "description:path:type"
            path_part = part.split(':')[1] if len(part.split(':')) > 1 else part
            if os.path.exists(path_part.strip()):
                paths.append(path_part.strip())
    
    return paths

def generate_pdf_thumbnail(pdf_path: str, output_path: str, size: str = "400x600") -> bool:
    """Generate a thumbnail image of the first page of a PDF using ImageMagick."""
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Use modern ImageMagick 7 'magick' command
        cmd = [
            'magick', 
            '-density', '300',
            f'{pdf_path}[0]',
            '-background', 'white',
            '-alpha', 'remove',
            '-resize', size,
            '-quality', '95',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Verify the generated file is not empty or corrupted
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                print(f"  ✅ Generated thumbnail: {os.path.basename(output_path)}")
                return True
            else:
                print(f"  ❌ Generated thumbnail is too small or corrupted")
                if os.path.exists(output_path):
                    os.remove(output_path)
                return False
        else:
            # Try fallback with legacy convert command
            print("  🔄 Trying fallback with legacy convert command...")
            fallback_cmd = [
                'convert',
                '-density', '300',
                f'{pdf_path}[0]',
                '-background', 'white',
                '-alpha', 'remove',
                '-resize', size,
                '-quality', '95',
                output_path
            ]
            
            fallback_result = subprocess.run(fallback_cmd, capture_output=True, text=True)
            if fallback_result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                print(f"  ✅ Generated thumbnail with fallback: {os.path.basename(output_path)}")
                return True
            else:
                print(f"  ❌ Fallback also failed")
                try:
                    if os.path.exists(output_path):
                        os.remove(output_path)
                except (OSError, PermissionError):
                    # Ignore permission errors when cleaning up
                    pass
                return False
            
    except Exception as e:
        print(f"  ❌ Error generating thumbnail: {e}")
        try:
            if os.path.exists(output_path):
                os.remove(output_path)
        except (OSError, PermissionError):
            # Ignore permission errors when cleaning up
            pass
        return False

def copy_pdf_file(source_path: str, destination_path: str) -> bool:
    """Copy a PDF file from source to destination."""
    try:
        # Create destination directory if it doesn't exist
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        
        # Copy the file
        shutil.copy2(source_path, destination_path)
        print(f"  ✅ Copied: {os.path.basename(source_path)} -> {os.path.basename(destination_path)}")
        return True
    except Exception as e:
        print(f"  ❌ Error copying {source_path}: {e}")
        return False

def update_pdf_metadata(pdf_path: str, metadata: Dict[str, str]) -> bool:
    """Update PDF metadata using PyPDF2."""
    try:
        import PyPDF2
        
        # Read the PDF
        reader = PyPDF2.PdfReader(pdf_path)
        writer = PyPDF2.PdfWriter()
        
        # Copy all pages
        for page in reader.pages:
            writer.add_page(page)
        
        # Update metadata
        if metadata.get('title'):
            writer.add_metadata({'/Title': metadata['title']})
        if metadata.get('author'):
            writer.add_metadata({'/Author': metadata['author']})
        if metadata.get('subject'):
            writer.add_metadata({'/Subject': metadata['subject']})
        if metadata.get('keywords'):
            writer.add_metadata({'/Keywords': metadata['keywords']})
        if metadata.get('creator'):
            writer.add_metadata({'/Creator': metadata['creator']})
        if metadata.get('producer'):
            writer.add_metadata({'/Producer': metadata['producer']})
        if metadata.get('description'):
            writer.add_metadata({'/Description': metadata['description']})
        
        # Write the updated PDF
        with open(pdf_path, 'wb') as output_file:
            writer.write(output_file)
        
        print(f"  ✅ Updated PDF metadata: {os.path.basename(pdf_path)}")
        return True
        
    except Exception as e:
        print(f"  ❌ PDF metadata update failed: {e}")
        return False

def prepare_pdf_metadata(fields: Dict[str, str]) -> Dict[str, str]:
    """Prepare PDF metadata from BibTeX fields."""
    metadata = {}
    
    # Title - clean braces from title
    if fields.get('title'):
        metadata['title'] = fields['title']
    
    # Author - first author's full name
    if fields.get('author'):
        author_field = fields['author']
        authors = [author.strip() for author in author_field.split(' and ')]
        if authors:
            first_author = authors[0]
            metadata['author'] = first_author
    
    # Subject - from keywords field
    if fields.get('keywords'):
        metadata['subject'] = fields['keywords']
    else:
        metadata['subject'] = ""
    
    # Creator - first author
    if fields.get('author'):
        author_field = fields['author']
        authors = [author.strip() for author in author_field.split(' and ')]
        if authors:
            first_author = authors[0]
            metadata['creator'] = first_author
    
    # Producer - tool used
    metadata['producer'] = "RENWeB"
    
    # Description - abstract if available
    if fields.get('abstract'):
        abstract = fields['abstract']
        if len(abstract) > 500:
            abstract = abstract[:500] + "..."
        metadata['description'] = abstract
    
    return metadata

def clean_individual_entry(entry: str) -> str:
    """Clean an individual BibTeX entry."""
    if not entry.strip():
        return entry
    
    # Fix missing closing brace - add one if we have unbalanced braces
    open_braces = entry.count('{')
    close_braces = entry.count('}')
    if open_braces > close_braces:
        missing_braces = open_braces - close_braces
        entry = entry.rstrip() + '\n' + '}' * missing_braces
    
    # Fix entries that don't start with @type{ - this is a severe malformation
    if not re.match(r'@\w+\{', entry.strip()):
        # Try to find the @type{ line within the entry
        type_match = re.search(r'@(\w+)\{([^,]+),', entry)
        if type_match:
            entry_type = type_match.group(1)
            entry_key = type_match.group(2)
            # Extract the content after the @type{ line
            content_after_type = entry[type_match.end():]
            # Remove any stray content before the @type{ line
            content_before_type = entry[:type_match.start()]
            # Reconstruct the entry properly, removing stray content
            entry = f"@{entry_type}{{{entry_key},\n{content_after_type}"
            print(f"    🔧 Fixed malformed entry: {entry_key}")
        else:
            # This is a severely malformed entry that can't be fixed
            # It's likely a fragment that should be discarded
            print(f"    ⚠️  Discarding severely malformed entry fragment")
            # Return an empty string to indicate this entry should be skipped
            return ""
    
    return entry

def clean_malformed_bibtex_entries(bibtex_content: str) -> str:
    """Clean up common malformed BibTeX entries that cause parsing errors."""
    print("🧹 Cleaning up malformed BibTeX entries...")
    
    # First, clean up braces in all text fields globally to prevent parsing issues
    # This is more efficient than cleaning them individually later
    print("  🔧 Cleaning braces from text fields...")
    
    # Clean braces from common text fields that often have Zotero highlighting
    # Process each entry individually to handle nested braces properly
    entries = re.split(r'\n(?=@)', bibtex_content)
    cleaned_entries = []
    
    for entry in entries:
        if not entry.strip():
            cleaned_entries.append(entry)
            continue
        
        # Clean braces from text fields in this entry
        text_fields = ['title', 'author', 'journal', 'publisher', 'institution', 'abstract', 'keywords']
        for field in text_fields:
            # Find field = {value} and clean the value
            # Use a more sophisticated approach to handle nested braces
            def clean_field_value(match):
                field_name = match.group(1)
                field_value = match.group(2)
                cleaned_value = clean_nested_braces(field_value)
                return f'{field_name} = {{{cleaned_value}}}'
            
            # Use a pattern that matches the field and then finds the matching closing brace
            pattern = rf'({field})\s*=\s*\{{'
            match = re.search(pattern, entry)
            if match:
                # Find the matching closing brace
                start_pos = match.end() - 1  # Position of opening brace
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
                
                if brace_count == 0:  # Found matching closing brace
                    field_value = entry[start_pos + 1:end_pos]
                    cleaned_value = clean_nested_braces(field_value)
                    entry = entry[:start_pos + 1] + cleaned_value + entry[end_pos:]
        
        # Apply individual entry cleaning logic
        cleaned_entry = clean_individual_entry(entry)
        if cleaned_entry:  # Only add non-empty entries
            cleaned_entries.append(cleaned_entry)
    
    bibtex_content = '\n'.join(cleaned_entries)
    
    # Additional early cleaning steps for better processing
    print("  🔧 Normalizing whitespace and line endings...")
    # Normalize line endings and clean up excessive whitespace
    bibtex_content = re.sub(r'\r\n', '\n', bibtex_content)  # Normalize line endings
    bibtex_content = re.sub(r'\r', '\n', bibtex_content)    # Handle old Mac line endings
    bibtex_content = re.sub(r'\n\s*\n\s*\n', '\n\n', bibtex_content)  # Remove excessive blank lines
    bibtex_content = re.sub(r'[ \t]+', ' ', bibtex_content)  # Normalize spaces and tabs
    
    print("  🔧 Cleaning special characters from text fields...")
    # Clean special characters from text fields that will be used in filenames
    entries = re.split(r'\n(?=@)', bibtex_content)
    cleaned_entries = []
    
    for entry in entries:
        if not entry.strip():
            cleaned_entries.append(entry)
            continue
        
        # Clean special characters from fields that will be used in filenames
        filename_fields = ['title', 'author', 'journal', 'publisher', 'institution']
        for field in filename_fields:
            pattern = rf'({field})\s*=\s*\{{'
            match = re.search(pattern, entry)
            if match:
                # Find the matching closing brace
                start_pos = match.end() - 1  # Position of opening brace
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
                
                if brace_count == 0:  # Found matching closing brace
                    field_value = entry[start_pos + 1:end_pos]
                    # Apply cleaning logic appropriate for the field type
                    if field in ['title', 'journal', 'publisher', 'institution']:
                        cleaned_value = clean_title_for_bibtex(field_value)
                    else:
                        cleaned_value = clean_title_for_filename(field_value)
                    if cleaned_value != field_value:  # Only update if changed
                        entry = entry[:start_pos + 1] + cleaned_value + entry[end_pos:]
        
        cleaned_entries.append(entry)
    
    bibtex_content = '\n'.join(cleaned_entries)
    
    # Now process each entry separately for other malformed patterns
    entries = re.split(r'\n(?=@)', bibtex_content)
    cleaned_entries = []
    
    for entry in entries:
        if not entry.strip():
            cleaned_entries.append(entry)
            continue
        
        # Fix missing commas between fields
        # Pattern: field = {...} followed immediately by field = {...} without comma
        # Apply this multiple times to handle all missing commas
        while True:
            new_entry = re.sub(
                r'(\w+\s*=\s*\{[^}]*\})\s*\n\s*(\w+\s*=\s*\{[^}]*\})',
                r'\1,\n\t\2',
                entry
            )
            if new_entry == entry:
                break  # No more changes needed
            entry = new_entry
        
        # Fix stray characters like "p," that appear alone on lines
        entry = re.sub(r'^\s*[a-zA-Z],\s*$', '', entry, flags=re.MULTILINE)
        
        # Fix double commas
        entry = re.sub(r',\s*,', ',', entry)
        
        # Fix trailing comma before closing brace
        entry = re.sub(r',\s*\n\s*}', '\n}', entry)
        
        
        # Fix the specific pattern: "jpg}df = {" -> "jpg}, pdf = {"
        # This must come BEFORE the general pattern to avoid conflicts
        entry = re.sub(r'(\w+)\}df\s*=\s*\{', r'\1}, pdf = {', entry)
        
        # Fix malformed field names (like "}df = {" should be "pdf = {")
        entry = re.sub(r'\}\s*df\s*=\s*\{', 'pdf = {', entry)
        
        # Fix the specific pattern: "}df = {" (no space before df)
        entry = re.sub(r'\}df\s*=\s*\{', 'pdf = {', entry)
        
        # Fix stray characters and malformed field separators
        # Pattern: }field = { should be , field = { (remove extra } and add comma)
        entry = re.sub(r'\}\s*(\w+)\s*=\s*\{', r', \1 = {', entry)
        
        # Fix cases where we have "}fieldname = {" pattern (but not df which we already handled)
        entry = re.sub(r'\}\s*(?!df\s*=)([a-zA-Z]+)\s*=\s*\{', r'\1 = {', entry)
        
        # Fix missing field names before values (be more careful)
        # Pattern: }value} should be field = {value} but only at the end of entry
        # This is too aggressive, let's remove it for now
        # entry = re.sub(r'\}\s*([^=}]+)\}\s*$', r'field = {\1}', entry)
        
        # Handle duplicate pdf fields (keep the LAST one, not the first)
        pdf_fields = re.findall(r'pdf\s*=\s*\{[^}]*\}', entry)
        if len(pdf_fields) > 1:
            last_pdf = pdf_fields[-1]  # Keep the last one
            # Remove all pdf fields
            entry = re.sub(r'pdf\s*=\s*\{[^}]*\},?\s*', '', entry)
            # Add back only the last pdf field before the closing brace
            entry = re.sub(r'(\s*)\}(\s*)$', rf',\n\t{last_pdf}\1}}\2', entry)
            print(f"    🔧 Fixed duplicate pdf fields in entry")
        
        # Handle duplicate preview fields (keep the LAST one, not the first)
        preview_fields = re.findall(r'preview\s*=\s*\{[^}]*\}', entry)
        if len(preview_fields) > 1:
            last_preview = preview_fields[-1]  # Keep the last one
            # Remove all preview fields
            entry = re.sub(r'preview\s*=\s*\{[^}]*\},?\s*', '', entry)
            # Add back only the last preview field before the closing brace
            entry = re.sub(r'(\s*)\}(\s*)$', rf',\n\t{last_preview}\1}}\2', entry)
            print(f"    🔧 Fixed duplicate preview fields in entry")
        
        # Clean up any remaining malformed lines
        # Remove lines that are just stray characters or incomplete
        lines = entry.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            # Skip empty lines or lines with just stray characters
            if not line or re.match(r'^[a-zA-Z],?\s*$', line):
                continue
            # Skip lines that don't look like proper BibTeX fields
            # But be more permissive to avoid removing valid content
            if not re.match(r'^\s*(\w+\s*=\s*\{|@\w+\{|}|\s*$)', line):
                # Only skip if it's clearly not a valid field
                if not re.match(r'^\s*\w+', line):
                    continue
            cleaned_lines.append(line)
        
        if cleaned_lines:
            cleaned_entry = '\n'.join(cleaned_lines)
            cleaned_entries.append(cleaned_entry)
    
    cleaned_content = '\n'.join(cleaned_entries)
    
    print("  ✅ Malformed entries cleaned up")
    return cleaned_content

def add_selected_tag_if_featured(bibtex_content: str, citation_key: str, fields: Dict[str, str]) -> str:
    """Add selected=true tag to BibTeX entry if keywords contain 'featured'."""
    # Check if keywords contain "featured"
    if 'keywords' not in fields or not fields['keywords']:
        return bibtex_content
    
    keywords = fields['keywords'].lower()
    if 'featured' not in keywords:
        return bibtex_content
    
    # Check if entry already has selected tag
    if 'selected' in fields:
        return bibtex_content
    
    # Find the entry start - look for @type{citation_key,
    entry_start_pattern = r'@\w+\{' + re.escape(citation_key) + r','
    
    # Find the entry start
    start_match = re.search(entry_start_pattern, bibtex_content)
    if not start_match:
        print(f"    ❌ Could not find entry for {citation_key} when adding selected tag")
        return bibtex_content
    
    start_pos = start_match.start()
    
    # Find the closing brace of this entry by counting braces
    # Start from the opening brace after the citation key
    brace_start = bibtex_content.find('{', start_pos)
    if brace_start == -1:
        print(f"    ❌ Could not find opening brace for {citation_key}")
        return bibtex_content
    
    brace_count = 1  # Start with 1 for the opening brace we just found
    end_pos = brace_start + 1
    
    for i, char in enumerate(bibtex_content[brace_start + 1:], brace_start + 1):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                end_pos = i + 1
                break
    
    if end_pos == brace_start + 1:
        print(f"    ❌ Could not find closing brace for {citation_key} when adding selected tag")
        return bibtex_content
    
    # Extract the entry content
    entry_content = bibtex_content[start_pos:end_pos]
    
    # Find the closing brace position within the entry
    # Look for the last } that's not part of a field value
    brace_pos = -1
    brace_count = 0
    
    for i, char in enumerate(entry_content):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                brace_pos = i
                break
    
    if brace_pos == -1:
        print(f"    ❌ Could not find closing brace in entry for {citation_key}")
        return bibtex_content
    
    # Check if we need a comma before the selected tag
    # Look at the content before the closing brace
    content_before_brace = entry_content[:brace_pos].rstrip()
    
    # Simple check: if the last non-whitespace character is a comma, don't add another
    needs_comma = not content_before_brace.endswith(',')
    
    # Prepare selected tag to add
    if needs_comma:
        tag_to_add = f",\n\tselected = {{true}}"
    else:
        tag_to_add = f"\n\tselected = {{true}}"
    
    # Insert tag before the closing brace
    modified_entry = entry_content[:brace_pos] + tag_to_add + entry_content[brace_pos:]
    
    # Replace the entry in the content
    modified_content = (
        bibtex_content[:start_pos] + 
        modified_entry + 
        bibtex_content[end_pos:]
    )
    
    print(f"    ✅ Added selected=true tag (keywords contain 'featured')")
    return modified_content

def entry_has_selected_tag(fields: Dict[str, str]) -> bool:
    """Check if a BibTeX entry already has a selected tag."""
    return 'selected' in fields



def process_images_for_entry(citation_key: str, fields: Dict[str, str], output_dir: str, force: bool = False) -> Dict[str, str]:
    """Process images for a BibTeX entry, copying and renaming them."""
    if 'file' not in fields or not fields['file']:
        return {}
    
    # Parse file field to find images
    file_entries = fields['file'].split(';')
    images = []
    
    for file_entry in file_entries:
        if 'image/' in file_entry:
            # Extract the file path from the file entry
            parts = file_entry.split(':')
            if len(parts) >= 2:
                file_path = parts[1].strip()
                if os.path.exists(file_path):
                    images.append(file_path)
    
    if not images:
        return {}
    
    # Generate base filename components
    author_filename = extract_author_names_for_filename(fields.get('author', ''))
    title = fields.get('title', '')
    condensed_title = remove_filler_words(title)
    clean_filename = clean_title_for_filename(condensed_title)
    year = fields.get('year', '')
    
    # Create base filename (no journal/conference names)
    if author_filename and year:
        base_filename = f"{author_filename}_{year}_{clean_filename}"
    elif author_filename:
        base_filename = f"{author_filename}_{clean_filename}"
    else:
        base_filename = clean_filename
    
    # Clean up base filename
    base_filename = re.sub(r'[^\w\-_.]', '_', base_filename)
    base_filename = re.sub(r'_+', '_', base_filename)
    base_filename = re.sub(r'^_|_$', '', base_filename)
    
    # Process each image
    processed_images = {}
    figure_count = 1
    photo_count = 1
    
    for image_path in images:
        original_filename = os.path.basename(image_path)
        file_extension = os.path.splitext(original_filename)[1].lower()
        
        # Determine if it's a figure or photo based on filename
        if original_filename.lower().startswith('figure'):
            image_type = 'figure'
            new_filename = f"{base_filename}_figure_{figure_count:02d}{file_extension}"
            figure_count += 1
        else:
            # All other images are treated as photos
            image_type = 'photo'
            new_filename = f"{base_filename}_photo_{photo_count:02d}{file_extension}"
            photo_count += 1
        
        # Create destination path
        dest_path = os.path.join("assets/img/publications", new_filename)
        
        # Copy file if it doesn't exist or if forced
        if not os.path.exists(dest_path) or force:
            try:
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy2(image_path, dest_path)
                print(f"  ✅ Copied image: {new_filename}")
            except Exception as e:
                print(f"  ❌ Error copying image {original_filename}: {e}")
                continue
        else:
            print(f"  ⏭️  Image already exists: {new_filename}")
        
        # Store the processed image info
        if image_type not in processed_images:
            processed_images[image_type] = []
        processed_images[image_type].append(new_filename)
    
    return processed_images

def clean_file_field_from_images(entry_content: str) -> str:
    """Remove image entries from the file field, keeping only PDFs and other non-image files."""
    # Find the file field
    file_field_match = re.search(r'file\s*=\s*\{([^}]*)\}', entry_content)
    if not file_field_match:
        return entry_content
    
    file_content = file_field_match.group(1)
    
    # Split by semicolon and filter out image entries
    file_parts = file_content.split(';')
    non_image_parts = []
    
    for part in file_parts:
        part = part.strip()
        if part and not (':image/jpeg' in part or ':image/jpg' in part or ':image/png' in part or ':image/gif' in part):
            non_image_parts.append(part)
    
    # Reconstruct the file field
    if non_image_parts:
        new_file_content = '; '.join(non_image_parts)
        new_entry_content = entry_content.replace(file_field_match.group(0), f'file = {{{new_file_content}}}')
    else:
        # Remove the entire file field if no non-image files remain
        new_entry_content = entry_content.replace(file_field_match.group(0), '')
        # Clean up any trailing comma
        new_entry_content = re.sub(r',\s*}', '}', new_entry_content)
    
    return new_entry_content

def add_image_tags(bibtex_content: str, citation_key: str, processed_images: Dict[str, list]) -> str:
    """Add image tags to a BibTeX entry and clean up the file field."""
    # Check if we have images to process (only if there are actual images)
    if not processed_images or (not processed_images.get('figure') and not processed_images.get('photo')):
        return bibtex_content
    
    # Find the entry start - be more specific to avoid matching wrong entries
    entry_start_pattern = r'@\w+\{\s*' + re.escape(citation_key) + r'\s*,'
    start_match = re.search(entry_start_pattern, bibtex_content)
    if not start_match:
        print(f"    ❌ Could not find entry for {citation_key} when adding image tags")
        return bibtex_content
    
    start_pos = start_match.start()
    
    # Find the closing brace of this entry by counting braces
    brace_start = bibtex_content.find('{', start_pos)
    if brace_start == -1:
        print(f"    ❌ Could not find opening brace for {citation_key}")
        return bibtex_content
    
    brace_count = 1
    end_pos = brace_start + 1
    
    for i, char in enumerate(bibtex_content[brace_start + 1:], brace_start + 1):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                end_pos = i + 1
                break
    
    if end_pos == brace_start + 1:
        print(f"    ❌ Could not find closing brace for {citation_key}")
        return bibtex_content
    
    # Get the entry content
    entry_content = bibtex_content[start_pos:end_pos]
    
    # Check if the entry already has photos or figures tags
    if 'photos' in entry_content or 'figures' in entry_content:
        print(f"    ⏭️  Entry {citation_key} already has image tags")
        return bibtex_content
    
    # Note: We allow image processing even if preview/pdf tags exist, as they serve different purposes
    
    # Clean the file field to remove image entries
    cleaned_entry_content = clean_file_field_from_images(entry_content)
    
    # Prepare image tags to add (only if there are actual images)
    tags_to_add = ""
    if 'figure' in processed_images and processed_images['figure']:
        figures_list = ', '.join(processed_images['figure'])
        tags_to_add += f",\n\tfigures = {{{figures_list}}}"
    
    if 'photo' in processed_images and processed_images['photo']:
        photos_list = ', '.join(processed_images['photo'])
        if tags_to_add:
            tags_to_add += f",\n\tphotos = {{{photos_list}}}"
        else:
            tags_to_add += f",\n\tphotos = {{{photos_list}}}"
    
    if tags_to_add:
        # Find the last field in the cleaned entry content to determine where to insert tags
        # Handle both fields with braces {value} and fields without braces (like month = jul)
        last_field_match = None
        for match in re.finditer(r'\w+\s*=\s*(?:\{[^}]*\}|[^,\n]+)', cleaned_entry_content):
            last_field_match = match
        
        if not last_field_match:
            print(f"    ⚠️  Could not find last field in entry {citation_key}")
            return bibtex_content
        
        # Check if the last field ends with a comma to avoid double commas
        last_field_text = last_field_match.group(0)
        last_field_ends_with_comma = last_field_text.rstrip().endswith(',')
        
        # Adjust tags_to_add based on whether we need a comma
        if last_field_ends_with_comma:
            # If the last field already has a comma, remove the leading comma from tags_to_add
            adjusted_tags = tags_to_add[1:]  # Remove the leading comma
        else:
            # If the last field doesn't have a comma, keep the leading comma in tags_to_add
            adjusted_tags = tags_to_add
        
        # Don't add a comma at the end - the final cleanup will handle trailing commas
        
        # Insert tags after the last field in the cleaned content
        last_field_end = last_field_match.end()
        modified_entry = cleaned_entry_content[:last_field_end] + adjusted_tags + cleaned_entry_content[last_field_end:]
        
        # Replace the entire entry in the original content
        modified_content = (
            bibtex_content[:start_pos] + 
            modified_entry + 
            bibtex_content[end_pos:]
        )
        
        print(f"    ✅ Added image tags: {len(processed_images.get('figure', []))} figures, {len(processed_images.get('photo', []))} photos")
        return modified_content
    
    return bibtex_content

def add_pdf_and_preview_tags(bibtex_content: str, citation_key: str, preview_filename: str, pdf_filename: str, fields: Dict[str, str], verbose: bool = False) -> str:
    """Add pdf/slides and preview tags to a BibTeX entry."""
    # Check if entry already has these tags
    if ('pdf' in fields or 'slides' in fields) and 'preview' in fields:
        return bibtex_content
    
    # Additional check: make sure the entry doesn't already have these tags in the content
    # This prevents duplicate additions when the content is modified multiple times
    entry_start_pattern = r'@\w+\{\s*' + re.escape(citation_key) + r'\s*,'
    start_match = re.search(entry_start_pattern, bibtex_content)
    if start_match:
        # Find the entry content to check for existing tags
        start_pos = start_match.start()
        brace_start = bibtex_content.find('{', start_pos)
        if brace_start != -1:
            brace_count = 1
            end_pos = brace_start + 1
            for i, char in enumerate(bibtex_content[brace_start + 1:], brace_start + 1):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_pos = i + 1
                        break
            
            if end_pos > brace_start + 1:
                entry_content = bibtex_content[start_pos:end_pos]
                # Check if preview and pdf/slides tags already exist in this specific entry
                has_preview = 'preview' in entry_content
                has_pdf_or_slides = 'pdf' in entry_content or 'slides' in entry_content
                if has_preview and has_pdf_or_slides:
                    return bibtex_content
                
                # Also check if the entry already has image tags to avoid conflicts
                if 'photos' in entry_content or 'figures' in entry_content:
                    print(f"    ⏭️  Entry {citation_key} already has image tags, skipping pdf/preview processing to avoid conflicts")
                    return bibtex_content
    
    # Check if keywords contain "presenter", "speaker", "prezi", or "miro" to determine if this should be slides instead of pdf
    is_presentation = False
    if 'keywords' in fields and fields['keywords']:
        keywords = fields['keywords'].lower()
        is_presentation = 'presenter' in keywords or 'speaker' in keywords or 'prezi' in keywords or 'miro' in keywords
    
    # Find the entry start - be more specific to avoid matching wrong entries
    # Look for the exact pattern: @type{citation_key,
    entry_start_pattern = r'@\w+\{\s*' + re.escape(citation_key) + r'\s*,'
    start_match = re.search(entry_start_pattern, bibtex_content)
    if not start_match:
        print(f"    ❌ Could not find entry for {citation_key} when adding pdf/slides/preview tags")
        return bibtex_content
    
    start_pos = start_match.start()
    
    # Find the closing brace of this entry by counting braces from the start
    brace_start = bibtex_content.find('{', start_pos)
    if brace_start == -1:
        print(f"    ❌ Could not find opening brace for {citation_key}")
        return bibtex_content
    
    brace_count = 1
    end_pos = brace_start + 1
    
    for i, char in enumerate(bibtex_content[brace_start + 1:], brace_start + 1):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                end_pos = i + 1
                break
    
    if end_pos == brace_start + 1:
        print(f"    ❌ Could not find closing brace for {citation_key}")
        return bibtex_content
    
    # Find the position to insert tags - look for the last field before the closing brace
    # We'll insert before the closing brace, after the last field
    entry_content = bibtex_content[start_pos:end_pos]
    
    # Find the last field before the closing brace
    # Look for the last field pattern: field = {value}
    # This pattern needs to handle whitespace and newlines
    # Find all fields in the entry - handle nested braces properly by parsing manually
    fields_matches = []
    i = 0
    while i < len(entry_content):
        # Look for field pattern: word = {
        field_start = re.search(r'\w+\s*=\s*\{', entry_content[i:])
        if not field_start:
            break
        
        field_start_pos = i + field_start.start()
        field_name_end = i + field_start.end() - 1  # Position of opening brace
        
        # Count braces to find the matching closing brace
        brace_count = 1
        j = field_name_end + 1
        while j < len(entry_content) and brace_count > 0:
            if entry_content[j] == '{':
                brace_count += 1
            elif entry_content[j] == '}':
                brace_count -= 1
            j += 1
        
        if brace_count == 0:
            # Found complete field
            field_end = j
            field_text = entry_content[field_start_pos:field_end]
            fields_matches.append((field_start_pos, field_end, field_text))
            i = field_end
        else:
            break
    
    # Debug: print the fields found
    if verbose:
        print(f"    🔍 Found {len(fields_matches)} fields in entry {citation_key}")
        for i, (start, end, field) in enumerate(fields_matches):
            print(f"      Field {i+1}: {field[:50]}...")
    
    if not fields_matches:
        print(f"    ❌ Could not find any fields for {citation_key}")
        return bibtex_content
    
    # Get the last field
    last_field_start, last_field_end, last_field = fields_matches[-1]
    
    # Check if the last field ends with a comma (accounting for whitespace)
    needs_comma = not last_field.rstrip().endswith(',')
    
    # Prepare tags to add - use slides for presentations, pdf for papers
    if is_presentation:
        if needs_comma:
            tags_to_add = f",\n\tpreview = {{{preview_filename}}},\n\tslides = {{{pdf_filename}}}"
        else:
            tags_to_add = f"\n\tpreview = {{{preview_filename}}},\n\tslides = {{{pdf_filename}}}"
        print(f"    ✅ Added preview and slides tags (keywords contain 'presenter', 'speaker', 'prezi', or 'miro')")
    else:
        if needs_comma:
            tags_to_add = f",\n\tpreview = {{{preview_filename}}},\n\tpdf = {{{pdf_filename}}}"
        else:
            tags_to_add = f"\n\tpreview = {{{preview_filename}}},\n\tpdf = {{{pdf_filename}}}"
        print(f"    ✅ Added preview and pdf tags")
    
    # Insert tags after the last field, before the closing brace
    # Find the position of the last field
    last_field_pos = last_field_end
    
    # Insert tags at this position
    modified_entry = entry_content[:last_field_pos] + tags_to_add + entry_content[last_field_pos:]
    
    # Replace the entry in the content
    modified_content = (
        bibtex_content[:start_pos] + 
        modified_entry + 
        bibtex_content[end_pos:]
    )
    
    return modified_content

def entry_has_pdf_and_preview_tags(fields: Dict[str, str]) -> bool:
    """Check if a BibTeX entry already has pdf/slides and preview tags."""
    return ('pdf' in fields or 'slides' in fields) and 'preview' in fields

def entry_has_all_required_tags(fields: Dict[str, str]) -> bool:
    """Check if a BibTeX entry already has all required tags."""
    # Check for selected tags
    has_selected = entry_has_selected_tag(fields)
    
    # Check for DOI-based tags if DOI is present
    has_doi_based_tags = True
    if fields.get('doi'):
        has_altmetric = 'altmetric' in fields
        has_dimensions = 'dimensions' in fields
        has_doi_based_tags = has_altmetric and has_dimensions
    
    return has_selected and has_doi_based_tags

def cleanup_existing_files(regenerate: bool = False) -> None:
    """Clean up existing PDF files and thumbnails if regenerate flag is set."""
    if not regenerate:
        return
    
    print("🧹 Regenerate mode: Cleaning up existing files...")
    
    # Clean up PDF directory
    pdf_dir = "assets/pdf"
    if os.path.exists(pdf_dir):
        for file in os.listdir(pdf_dir):
            if file.endswith('.pdf'):
                file_path = os.path.join(pdf_dir, file)
                try:
                    os.remove(file_path)
                    print(f"  🗑️  Deleted: {file}")
                except Exception as e:
                    print(f"  ⚠️  Could not delete {file}: {e}")
    
    # Clean up preview directory
    preview_dir = "assets/img/publication_preview"
    if os.path.exists(preview_dir):
        for file in os.listdir(preview_dir):
            if file.endswith(('.jpeg', '.jpg')):
                file_path = os.path.join(preview_dir, file)
                try:
                    os.remove(file_path)
                    print(f"  🗑️  Deleted: {file}")
                except Exception as e:
                    print(f"  ⚠️  Could not delete {file}: {e}")
    
    print("  ✅ Cleanup complete")

def validate_and_clean_bibtex(bibtex_content: str) -> str:
    """Validate and clean corrupted BibTeX content."""
    print("🔍 Validating BibTeX content...")
    
    # Check for basic BibTeX structure issues
    issues_found = []
    
    # Check for unmatched braces
    brace_count = 0
    for char in bibtex_content:
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
    
    if brace_count != 0:
        issues_found.append(f"Unmatched braces: {brace_count} more {'{' if brace_count > 0 else '}'}")
    
    # Check for common syntax issues
    if re.search(r'[a-zA-Z]\s*\n\s*[a-zA-Z]', bibtex_content):
        issues_found.append("Missing commas between fields")
    
    if re.search(r'pdf\s*=\s*\{[^}]*\}\s*\n\s*pdf\s*=\s*\{', bibtex_content):
        issues_found.append("Duplicate pdf fields detected")
    
    if issues_found:
        print(f"  ⚠️  Found {len(issues_found)} potential issues:")
        for issue in issues_found:
            print(f"    - {issue}")
        print("  🔧 Will attempt to fix these issues...")
    else:
        print("  ✅ No obvious BibTeX syntax issues found")
    
    return bibtex_content

def fetch_metadata_from_semantic_scholar(title: str, author: str, verbose: bool = False) -> Optional[Dict[str, str]]:
    """Fetch metadata from Semantic Scholar API with caching."""
    # Check cache first
    cache_key = generate_cache_key(title, author)
    if cache_key in METADATA_CACHE:
        if verbose:
            print(f"    💾 Using cached metadata for Semantic Scholar")
        return METADATA_CACHE[cache_key].get('semantic_scholar')
    
    try:
        # Title and author are already cleaned in early processing
        # Search query
        query = f"{title} {author}"
        
        if verbose:
            print(f"    🔍 Searching Semantic Scholar for: {query[:60]}...")
        
        # Semantic Scholar API endpoint
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            "query": query,
            "limit": 1,
            "fields": "paperId,title,abstract,doi,isbn,keywords,venue,year,authors"
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("data") and len(data["data"]) > 0:
                paper = data["data"][0]
                
                metadata = {}
                
                # Extract DOI
                if paper.get("doi"):
                    metadata["doi"] = paper["doi"]
                
                # Extract ISBN
                if paper.get("isbn"):
                    metadata["isbn"] = paper["isbn"]
                
                # Extract abstract
                if paper.get("abstract"):
                    metadata["abstract"] = paper["abstract"]
                
                # Extract keywords
                if paper.get("keywords"):
                    metadata["keywords"] = ", ".join(paper["keywords"])
                
                # Extract venue/journal
                if paper.get("venue"):
                    metadata["journal"] = paper["venue"]
                
                # Extract year
                if paper.get("year"):
                    metadata["year"] = str(paper["year"])
                
                # Extract authors
                if paper.get("authors"):
                    authors = [f"{author.get('name', '')}" for author in paper["authors"]]
                    metadata["author"] = " and ".join(authors)
                
                if metadata:
                    # Cache the result
                    if cache_key not in METADATA_CACHE:
                        METADATA_CACHE[cache_key] = {}
                    METADATA_CACHE[cache_key]['semantic_scholar'] = metadata
                    
                    print(f"    📚 Fetched metadata from Semantic Scholar")
                    return metadata
        
        # Cache empty result to avoid repeated failed requests
        if cache_key not in METADATA_CACHE:
            METADATA_CACHE[cache_key] = {}
        METADATA_CACHE[cache_key]['semantic_scholar'] = None
        
        return None
        
    except Exception as e:
        print(f"    ⚠️  Error fetching from Semantic Scholar: {e}")
        # Cache empty result to avoid repeated failed requests
        if cache_key not in METADATA_CACHE:
            METADATA_CACHE[cache_key] = {}
        METADATA_CACHE[cache_key]['semantic_scholar'] = None
        return None

def fetch_metadata_from_crossref(title: str, author: str, verbose: bool = False) -> Optional[Dict[str, str]]:
    """Fetch metadata from Crossref API as fallback with caching."""
    # Check cache first
    cache_key = generate_cache_key(title, author)
    if cache_key in METADATA_CACHE:
        if verbose:
            print(f"    💾 Using cached metadata for Crossref")
        return METADATA_CACHE[cache_key].get('crossref')
    
    try:
        # Title and author are already cleaned in early processing
        if verbose:
            print(f"    🔍 Searching Crossref for: {title[:40]}...")
        
        # Crossref API endpoint
        url = "https://api.crossref.org/works"
        params = {
            "query": f"{title} {author}",
            "rows": 1,
            "select": "DOI,ISBN,abstract,subject,container-title,created,author"
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("message", {}).get("items") and len(data["message"]["items"]) > 0:
                item = data["message"]["items"][0]
                
                metadata = {}
                
                # Extract DOI
                if item.get("DOI"):
                    metadata["doi"] = item["DOI"]
                
                # Extract ISBN
                if item.get("ISBN"):
                    isbn_list = item["ISBN"]
                    if isinstance(isbn_list, list) and len(isbn_list) > 0:
                        metadata["isbn"] = isbn_list[0]
                    elif isinstance(isbn_list, str):
                        metadata["isbn"] = isbn_list
                
                # Extract abstract
                if item.get("abstract"):
                    metadata["abstract"] = item["abstract"]
                
                # Extract subjects/keywords
                if item.get("subject"):
                    metadata["keywords"] = ", ".join(item["subject"])
                
                # Extract journal/container title
                if item.get("container-title"):
                    container_titles = item["container-title"]
                    if isinstance(container_titles, list) and len(container_titles) > 0:
                        metadata["journal"] = container_titles[0]
                    elif isinstance(container_titles, str):
                        metadata["journal"] = container_titles
                
                # Extract year
                if item.get("created", {}).get("date-parts"):
                    date_parts = item["created"]["date-parts"][0]
                    if len(date_parts) > 0:
                        metadata["year"] = str(date_parts[0])
                
                # Extract authors
                if item.get("author"):
                    authors = []
                    for author_info in item["author"]:
                        if author_info.get("given") and author_info.get("family"):
                            authors.append(f"{author_info['family']}, {author_info['given']}")
                        elif author_info.get("name"):
                            authors.append(author_info["name"])
                    if authors:
                        metadata["author"] = " and ".join(authors)
                
                if metadata:
                    # Cache the result
                    if cache_key not in METADATA_CACHE:
                        METADATA_CACHE[cache_key] = {}
                    METADATA_CACHE[cache_key]['crossref'] = metadata
                    
                    print(f"    📚 Fetched metadata from Crossref")
                    return metadata
        
        # Cache empty result to avoid repeated failed requests
        if cache_key not in METADATA_CACHE:
            METADATA_CACHE[cache_key] = {}
        METADATA_CACHE[cache_key]['crossref'] = None
        
        return None
        
    except Exception as e:
        print(f"    ⚠️  Error fetching from Crossref: {e}")
        # Cache empty result to avoid repeated failed requests
        if cache_key not in METADATA_CACHE:
            METADATA_CACHE[cache_key] = {}
        METADATA_CACHE[cache_key]['crossref'] = None
        return None

def enrich_bibtex_entry_with_metadata(fields: Dict[str, str], force_refetch: bool = False, verbose: bool = False) -> Dict[str, str]:
    """Enrich BibTeX entry with metadata from external sources."""
    enriched_fields = fields.copy()
    
    # Check if we should fetch metadata
    if should_fetch_metadata(enriched_fields, force_refetch, verbose):
        title = enriched_fields.get("title", "")
        author = enriched_fields.get("author", "")
        
        if title and author:
            # Try Semantic Scholar first
            metadata = fetch_metadata_from_semantic_scholar(title, author, verbose)
            
            # Fallback to Crossref if Semantic Scholar fails
            if not metadata:
                metadata = fetch_metadata_from_crossref(title, author, verbose)
            
            # Merge fetched metadata with existing fields
            if metadata:
                for key, value in metadata.items():
                    if key not in enriched_fields or not enriched_fields[key]:
                        enriched_fields[key] = value
                        if verbose:
                            print(f"    ➕ Added {key}: {str(value)[:50]}...")
    else:
        if verbose:
            print(f"    ⏭️  Skipping metadata fetch - already complete or not needed")
    
    return enriched_fields


def add_altmetric_tag_if_doi(bibtex_content: str, citation_key: str, fields: Dict[str, str]) -> str:
    """Add altmetric=true tag to BibTeX entry if DOI is present."""
    # Check if entry already has DOI and altmetric tag
    if not fields.get('doi') or 'altmetric' in fields:
        return bibtex_content
    
    # Find the entry start
    entry_start_pattern = r'@\w+\{' + re.escape(citation_key) + r','
    start_match = re.search(entry_start_pattern, bibtex_content)
    if not start_match:
        return bibtex_content
    
    start_pos = start_match.start()
    
    # Find the closing brace of this entry
    brace_start = bibtex_content.find('{', start_pos)
    if brace_start == -1:
        return bibtex_content
    
    brace_count = 1
    end_pos = brace_start + 1
    
    for i, char in enumerate(bibtex_content[brace_start + 1:], brace_start + 1):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                end_pos = i + 1
                break
    
    if end_pos == brace_start + 1:
        return bibtex_content
    
    # Extract the entry content
    entry_content = bibtex_content[start_pos:end_pos]
    
    # Find the closing brace position within the entry
    brace_pos = -1
    brace_count = 0
    
    for i, char in enumerate(entry_content):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                brace_pos = i
                break
    
    if brace_pos == -1:
        return bibtex_content
    
    # Check if we need a comma before the altmetric tag
    content_before_brace = entry_content[:brace_pos].rstrip()
    needs_comma = not content_before_brace.endswith(',')
    
    # Prepare altmetric tag to add
    if needs_comma:
        tag_to_add = f",\n\taltmetric = {{true}}"
    else:
        tag_to_add = f"\n\taltmetric = {{true}}"
    
    # Insert tag before the closing brace
    modified_entry = entry_content[:brace_pos] + tag_to_add + entry_content[brace_pos:]
    
    # Replace the entry in the content
    modified_content = (
        bibtex_content[:start_pos] + 
        modified_entry + 
        bibtex_content[end_pos:]
    )
    
    return modified_content

def rename_url_to_website_fields(bibtex_content: str) -> Tuple[str, int]:
    """Rename all 'url' fields to 'website' fields for Jekyll compatibility."""
    print("🔄 Renaming 'url' fields to 'website' fields for Jekyll compatibility...")
    
    # Count existing url fields
    url_count = len(re.findall(r'\burl\s*=\s*\{', bibtex_content))
    
    if url_count == 0:
        print("  ℹ️  No 'url' fields found to rename")
        return bibtex_content, 0
    
    # Replace 'url = {' with 'website = {' (case sensitive to avoid false matches)
    modified_content = re.sub(r'\burl\s*=\s*\{', 'website = {', bibtex_content)
    
    # Also handle 'urldate' fields - rename to 'website_date' for consistency
    urldate_count = len(re.findall(r'\burldate\s*=\s*\{', modified_content))
    if urldate_count > 0:
        modified_content = re.sub(r'\burldate\s*=\s*\{', 'website_date = {', modified_content)
        print(f"  ✅ Renamed {urldate_count} 'urldate' fields to 'website_date'")
    
    print(f"  ✅ Renamed {url_count} 'url' fields to 'website' fields")
    return modified_content, url_count

def process_bibtex_file(bibtex_file: str, output_dir: str, regenerate: bool = False, 
                       force: bool = False, update_metadata: bool = True, 
                       thumbnail_size: str = '600x', test_mode: bool = False, 
                       test_count: int = 5, verbose: bool = False, 
                       force_refetch_metadata: bool = False, rename_urls: bool = True) -> None:
    """Main function to process the papers.bib file."""
    print(f"📚 Processing {bibtex_file}...")
    
    # Load metadata cache
    load_metadata_cache()
    
    # Create backup of the original BibTeX file
    backup_file = bibtex_file.replace('.bib', f'_backup_{int(time.time())}.bib')
    try:
        shutil.copy2(bibtex_file, backup_file)
        print(f"  💾 Created backup: {backup_file}")
    except Exception as e:
        print(f"  ⚠️  Warning: Could not create backup: {e}")
        print(f"     Continuing without backup...")
    
    # Clean up existing files if regenerate mode
    cleanup_existing_files(regenerate)
    
    # Read and parse the BibTeX file
    try:
        with open(bibtex_file, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"  ✅ Read {bibtex_file}")
    except Exception as e:
        print(f"❌ Error reading {bibtex_file}: {e}")
        return
    
    # Validate and clean the BibTeX content first
    content = validate_and_clean_bibtex(content)
    
    # Clean up malformed entries
    content = clean_malformed_bibtex_entries(content)
    
    # Rename url fields to website fields for Jekyll compatibility
    url_rename_count = 0
    if rename_urls:
        content, url_rename_count = rename_url_to_website_fields(content)
    
    # Parse BibTeX entries
    entries = re.split(r'\n(?=@)', content)
    
    # Process each entry
    processed_count = 0
    copied_count = 0
    skipped_count = 0
    modified_content = content
    
    for entry in entries:
        if not entry.strip():
            continue
            
        citation_key, fields = parse_bibtex_entry(entry)
        if not citation_key:
            continue
        
        # Skip if already processed and not forced/regenerated
        # But always process entries with featured keywords to add selected tags
        has_featured_keywords = 'keywords' in fields and fields['keywords'] and 'featured' in fields['keywords'].lower()
        if entry_has_all_required_tags(fields) and not force and not regenerate and not has_featured_keywords:
            print(f"  ⏭️  Skipping already processed entry: {citation_key}")
            skipped_count += 1
            continue

        processed_count += 1
        
        # Test mode: limit processing to specified number of entries
        if test_mode and processed_count > test_count:
            print(f"  🧪 Test mode: Reached limit of {test_count} entries, stopping processing")
            break
            
        if verbose:
            print(f"\n📄 Processing entry: {citation_key}")
            print(f"  Title: {fields.get('title', 'N/A')[:80]}...")
            print(f"  Author: {fields.get('author', 'N/A')[:60]}...")
            print(f"  Year: {fields.get('year', 'N/A')}")
        else:
            print(f"\n📄 Processing entry: {citation_key}")
        
        # Extract file paths
        file_field = fields.get('file', '')
        file_paths = extract_file_paths(file_field)
        
        # Enrich entry with metadata from external sources (DOI, abstract, keywords, etc.)
        enriched_fields = enrich_bibtex_entry_with_metadata(fields, force_refetch_metadata, verbose)
        
        # Add selected=true tag if keywords contain 'featured' (do this before PDF processing to avoid conflicts)
        has_featured_keywords = 'keywords' in enriched_fields and enriched_fields['keywords'] and 'featured' in enriched_fields['keywords'].lower()
        if has_featured_keywords:
            modified_content = add_selected_tag_if_featured(modified_content, citation_key, enriched_fields)
        
        
        # Add altmetric=true tag if DOI is present
        if enriched_fields.get('doi'):
            modified_content = add_altmetric_tag_if_doi(modified_content, citation_key, enriched_fields)
        
        if not file_paths:
            print(f"  ❌ No PDF files found for {citation_key}")
            continue
        
        # Use the first PDF file found
        source_path = file_paths[0]
        
        # Extract filename from path
        filename = os.path.basename(source_path)
        
        # Clean and condense filename for use in BibTeX
        title = fields.get('title', '')
        condensed_title = remove_filler_words(title)
        clean_filename = clean_title_for_filename(condensed_title)
        author_filename = extract_author_names_for_filename(fields.get('author', ''))
        year = fields.get('year', '')
        
        # Create new filename in format: AUTHOR_YEAR_TITLE.pdf (no journal/conference names)
        if author_filename and year:
            new_filename = f"{author_filename}_{year}_{clean_filename}.pdf"
        elif author_filename:
            new_filename = f"{author_filename}_{clean_filename}.pdf"
        else:
            new_filename = f"{clean_filename}.pdf"
        
        # Clean up filename
        new_filename = re.sub(r'[^\w\-_.]', '_', new_filename)
        new_filename = re.sub(r'_+', '_', new_filename)
        new_filename = re.sub(r'^_|_$', '', new_filename)
        
        # Create destination path
        dest_path = os.path.join(output_dir, new_filename)
        
        # Copy file if it doesn't exist or if forced
        if not os.path.exists(dest_path) or force:
            try:
                shutil.copy2(source_path, dest_path)
                copied_count += 1
                print(f"  ✅ Copied PDF: {new_filename}")
            except Exception as e:
                print(f"  ❌ Error copying PDF: {e}")
                continue
        else:
            print(f"  ⏭️  PDF already exists: {new_filename}")
        
        # Generate thumbnail preview
        preview_filename = new_filename.replace('.pdf', '.jpeg')
        preview_path = os.path.join("assets/img/publication_preview", preview_filename)
        
        if not os.path.exists(preview_path) or force:
            try:
                if generate_pdf_thumbnail(dest_path, preview_path, thumbnail_size):
                    print(f"  ✅ Generated thumbnail: {preview_filename}")
                else:
                    print(f"  ❌ Failed to generate thumbnail: {preview_filename}")
                    continue
            except Exception as e:
                print(f"  ❌ Error generating thumbnail: {e}")
                continue
        else:
            print(f"  ⏭️  Thumbnail already exists: {preview_filename}")
        
        # Add pdf and preview tags to BibTeX
        modified_content = add_pdf_and_preview_tags(modified_content, citation_key, preview_filename, new_filename, fields, verbose)
        
        # Process images for this entry (always process, even if PDF tags exist)
        processed_images = process_images_for_entry(citation_key, fields, output_dir, force)
        if processed_images:
            # Add image tags to BibTeX
            modified_content = add_image_tags(modified_content, citation_key, processed_images)
                
        # Update PDF metadata if enabled
        if update_metadata:
            try:
                metadata = prepare_pdf_metadata(enriched_fields)
                update_pdf_metadata(dest_path, metadata)
                print(f"  ✅ Updated PDF metadata: {new_filename}")
            except Exception as e:
                print(f"  ❌ Error updating PDF metadata: {e}")
        else:
            print(f"  ℹ️  PDF metadata updating disabled")

        # Selected tag processing is now done earlier to avoid conflicts
    
    # Final cleanup of any trailing commas that may have been introduced
    modified_content = clean_malformed_bibtex_entries(modified_content)
    
    # Write the modified BibTeX content back to the file
    try:
        with open(bibtex_file, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        print(f"\n✅ Updated {bibtex_file} with pdf/slides, preview, dimensions, and altmetric tags")
    except Exception as e:
        print(f"❌ Error writing to {bibtex_file}: {e}")
        return
    
    # Save metadata cache
    save_metadata_cache()
    
    print(f"\n📊 Summary:")
    print(f"  Processed entries: {processed_count}")
    print(f"  Copied PDF files: {copied_count}")
    print(f"  Skipped entries: {skipped_count}")
    if rename_urls and url_rename_count > 0:
        print(f"  Renamed URL fields: {url_rename_count}")
    print(f"  Output directory: {output_dir}")
    print(f"  Metadata cache entries: {len(METADATA_CACHE)}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Process papers.bib, generate PDF thumbnails, and add tags')
    parser.add_argument('--thumbnail-size', default='600x', 
                       help='Thumbnail size in format WIDTHxHEIGHT or WIDTHx for auto height (default: 600x)')
    parser.add_argument('--bibtex-file', default='_bibliography/Exported Items.bib',
                       help='Path to source BibTeX file from Zotero (default: _bibliography/Exported Items.bib)')
    parser.add_argument('--regenerate', action='store_true',
                       help='Delete all existing PDFs and thumbnails, then regenerate everything')
    parser.add_argument('--force', action='store_true',
                       help='Force reprocessing of entries even if they already have tags')
    parser.add_argument('--update-metadata', action='store_true', default=True,
                       help='Update PDF metadata with BibTeX information (default: True)')
    parser.add_argument('--no-metadata', action='store_true',
                       help='Skip PDF metadata updating')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output for detailed processing information')
    parser.add_argument('--test', action='store_true',
                       help='Test mode: process only first 5 entries for quick testing')
    parser.add_argument('--test-count', type=int, default=5,
                       help='Number of entries to process in test mode (default: 5)')
    parser.add_argument('--force-refetch-metadata', action='store_true',
                       help='Force re-fetching of metadata from external APIs, ignoring cache and existing fields')
    parser.add_argument('--clear-cache', action='store_true',
                       help='Clear the metadata cache before processing')
    parser.add_argument('--rename-urls', action='store_true', default=True,
                       help='Rename "url" fields to "website" fields for Jekyll compatibility (default: True)')
    parser.add_argument('--no-rename-urls', action='store_true',
                       help='Skip renaming "url" fields to "website" fields')
    
    args = parser.parse_args()
    
    source_bibtex_file = args.bibtex_file
    working_bibtex_file = '_bibliography/papers.bib'
    
    # Check if source file exists
    if not os.path.exists(source_bibtex_file):
        print(f"❌ Error: Source file {source_bibtex_file} not found!")
        print(f"   This should be the file exported from Zotero.")
        sys.exit(1)
    
    # Copy source file to working file
    try:
        shutil.copy2(source_bibtex_file, working_bibtex_file)
        print(f"📋 Copied {source_bibtex_file} to {working_bibtex_file}")
    except Exception as e:
        print(f"❌ Error copying {source_bibtex_file} to {working_bibtex_file}: {e}")
        sys.exit(1)
    
    # Create output directories if they don't exist
    output_dir = "assets/pdf"
    preview_dir = "assets/img/publication_preview"
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(preview_dir, exist_ok=True)
    
    # Handle metadata updating preference
    update_metadata = args.update_metadata and not args.no_metadata
    
    # Handle URL renaming preference
    rename_urls = args.rename_urls and not args.no_rename_urls
    
    # Clear cache if requested
    if args.clear_cache:
        if os.path.exists(CACHE_FILE):
            try:
                os.remove(CACHE_FILE)
                print(f"🗑️  Cleared metadata cache: {CACHE_FILE}")
            except Exception as e:
                print(f"⚠️  Could not clear cache: {e}")
        else:
            print("ℹ️  No cache file found to clear")
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Exiting due to missing dependencies.")
        sys.exit(1)

    if args.test:
        # Test mode: process only a small sample for quick testing
        print(f"🧪 Test mode: Will process only first {args.test_count} entries for quick testing")
        process_bibtex_file(working_bibtex_file, output_dir, False, args.force, 
                          update_metadata, args.thumbnail_size, True, args.test_count, args.verbose, 
                          args.force_refetch_metadata, rename_urls)
    elif args.regenerate:
        # Full regenerate mode: delete all files and reprocess everything
        print("🧹 Full regenerate mode: Will delete all existing files and reprocess everything")
        process_bibtex_file(working_bibtex_file, output_dir, True, args.force, 
                          update_metadata, args.thumbnail_size, False, 0, args.verbose, 
                          args.force_refetch_metadata, rename_urls)
    else:
        # Process new papers and generate thumbnails
        process_bibtex_file(working_bibtex_file, output_dir, False, args.force, 
                          update_metadata, args.thumbnail_size, False, 0, args.verbose, 
                          args.force_refetch_metadata, rename_urls)
    
    print(f"\n✅ Processing completed successfully!")

if __name__ == "__main__":
    main()

