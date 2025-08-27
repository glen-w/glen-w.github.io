#!/usr/bin/env python3
"""
Script to process papers from Zotero export:
1. Copy _bibliography/Exported Items.bib to _bibliography/papers.bib
2. Parse BibTeX entries with proper nested brace handling
3. Copy PDF files to assets/pdf with renamed filenames
4. Generate thumbnail previews for each PDF
5. Add pdf/slides and preview tags to BibTeX entries (slides for presentations, pdf for papers)
6. Add dimensions=true tag to entries with DOI for citation tracking
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
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import requests
import json
import time
from typing import Dict, List, Optional, Tuple

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
    
    # Find all field patterns: field_name = { ... }
    field_start_pattern = r'(\w+)\s*=\s*\{'
    
    pos = 0
    while True:
        # Find the next field start
        match = re.search(field_start_pattern, content[pos:])
        if not match:
            break
            
        field_name = match.group(1).strip()
        field_start = pos + match.end() - 1  # Position of the opening brace
        
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
            # Clean the field value by removing nested braces
            field_value = clean_nested_braces(field_value)
            fields[field_name] = field_value
            pos = field_end + 1
        else:
            # Unmatched braces, skip this field
            pos = pos + match.end()
    
    return citation_key, fields

def clean_title_for_filename(title: str) -> str:
    """Clean a title for use in filenames."""
    if not title:
        return ""
    
    # Remove LaTeX commands and braces
    title = re.sub(r'\\[a-zA-Z]+', '', title)
    title = re.sub(r'\{([^}]*)\}', r'\1', title)
    
    # Remove special characters and replace with underscores
    title = re.sub(r'[^\w\s\-]', '_', title)
    title = re.sub(r'\s+', '_', title)
    title = re.sub(r'_+', '_', title)
    title = re.sub(r'^_|_$', '', title)
    
    # Limit length
    if len(title) > 50:
        title = title[:50]
    
    return title

def extract_author_names_for_filename(author: str) -> str:
    """Extract author names for use in filenames in format FIRSTNAME_SECONDNAME_etal."""
    if not author:
        return ""
    
    # Split by 'and' to get individual authors
    authors = [a.strip() for a in author.split(' and ')]
    
    if len(authors) == 1:
        # Single author: FIRSTNAME_SECONDNAME
        author = authors[0]
        if ',' in author:
            # Format: "Last, First" -> "First_Second"
            last_name = author.split(',')[0].strip()
            first_name = author.split(',')[1].strip()
            # Clean names for filename
            first_name = re.sub(r'[^\w]', '', first_name).lower()
            last_name = re.sub(r'[^\w]', '', last_name).lower()
            return f"{first_name}_{last_name}"
        else:
            # Format: "First Last" -> "first_second"
            parts = author.split()
            if len(parts) >= 2:
                first_name = re.sub(r'[^\w]', '', parts[0]).lower()
                last_name = re.sub(r'[^\w]', '', parts[-1]).lower()
                return f"{first_name}_{last_name}"
            else:
                return re.sub(r'[^\w]', '', author).lower()
    
    else:
        # Multiple authors (2 or more): FIRSTNAME_SECONDNAME_etal
        first_author = authors[0]
        if ',' in first_author:
            # Format: "Last, First" -> "First_Last"
            last_name = first_author.split(',')[0].strip()
            first_name = first_author.split(',')[1].strip()
            first_name = re.sub(r'[^\w]', '', first_name).lower()
            last_name = re.sub(r'[^\w]', '', last_name).lower()
            return f"{first_name}_{last_name}_etal"
        else:
            # Format: "First Last" -> "first_last"
            parts = first_author.split()
            if len(parts) >= 2:
                first_name = re.sub(r'[^\w]', '', parts[0]).lower()
                last_name = re.sub(r'[^\w]', '', parts[-1]).lower()
                return f"{first_name}_{last_name}_etal"
            else:
                return re.sub(r'[^\w]', '', first_author).lower() + "_etal"

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
                if os.path.exists(output_path):
                    os.remove(output_path)
                return False
            
    except Exception as e:
        print(f"  ❌ Error generating thumbnail: {e}")
        if os.path.exists(output_path):
            os.remove(output_path)
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
        metadata['title'] = clean_nested_braces(fields['title'])
    
    # Author - first author's full name
    if fields.get('author'):
        author_field = fields['author']
        authors = [author.strip() for author in author_field.split(' and ')]
        if authors:
            first_author = authors[0]
            first_author = clean_nested_braces(first_author)
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
            first_author = clean_nested_braces(first_author)
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

def clean_malformed_bibtex_entries(bibtex_content: str) -> str:
    """Clean up common malformed BibTeX entries that cause parsing errors."""
    print("🧹 Cleaning up malformed BibTeX entries...")
    
    # Process each entry separately to avoid cross-entry conflicts
    entries = re.split(r'\n(?=@)', bibtex_content)
    cleaned_entries = []
    
    for entry in entries:
        if not entry.strip():
            cleaned_entries.append(entry)
            continue
        
        # Fix missing commas between fields
        # Pattern: field = {...} followed immediately by field = {...} without comma
        entry = re.sub(
            r'(\w+\s*=\s*\{[^}]*\})\s*\n\s*(\w+\s*=\s*\{[^}]*\})',
            r'\1,\n\t\2',
            entry
        )
        
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
        
        cleaned_entries.append(entry)
    
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



def add_pdf_and_preview_tags(bibtex_content: str, citation_key: str, preview_filename: str, pdf_filename: str, fields: Dict[str, str]) -> str:
    """Add pdf/slides and preview tags to a BibTeX entry."""
    # Check if entry already has these tags
    if ('pdf' in fields or 'slides' in fields) and 'preview' in fields:
        return bibtex_content
    
    # Check if keywords contain "presenter" to determine if this should be slides instead of pdf
    is_presentation = False
    if 'keywords' in fields and fields['keywords']:
        keywords = fields['keywords'].lower()
        is_presentation = 'presenter' in keywords
    
    # Find the entry start
    entry_start_pattern = r'@\w+\{' + re.escape(citation_key) + r','
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
    # Find all fields in the entry
    field_pattern = r'(\w+\s*=\s*\{[^}]*\})'
    fields_matches = list(re.finditer(field_pattern, entry_content))
    
    if not fields_matches:
        print(f"    ❌ Could not find any fields for {citation_key}")
        return bibtex_content
    
    # Get the last field
    last_field_match = fields_matches[-1]
    last_field = last_field_match.group(1)
    
    # Check if the last field ends with a comma
    needs_comma = not last_field.endswith(',')
    
    # Prepare tags to add - use slides for presentations, pdf for papers
    if is_presentation:
        if needs_comma:
            tags_to_add = f",\n\tpreview = {{{preview_filename}}},\n\tslides = {{{pdf_filename}}}"
        else:
            tags_to_add = f"\n\tpreview = {{{preview_filename}}},\n\tslides = {{{pdf_filename}}}"
        print(f"    ✅ Added preview and slides tags (keywords contain 'presenter')")
    else:
        if needs_comma:
            tags_to_add = f",\n\tpreview = {{{preview_filename}}},\n\tpdf = {{{pdf_filename}}}"
        else:
            tags_to_add = f"\n\tpreview = {{{preview_filename}}},\n\tpdf = {{{pdf_filename}}}"
        print(f"    ✅ Added preview and pdf tags")
    
    # Insert tags after the last field, before the closing brace
    # Find the position of the last field
    last_field_pos = last_field_match.end()
    
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
    # For now, we only check for selected tags since we're focusing on that functionality
    # PDF/preview tags are added during processing, not checked for existence
    has_selected = entry_has_selected_tag(fields)
    return has_selected

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

def fetch_metadata_from_semantic_scholar(title: str, author: str) -> Optional[Dict[str, str]]:
    """Fetch metadata from Semantic Scholar API."""
    try:
        # Clean the title and author for search
        clean_title = clean_nested_braces(title)
        clean_author = clean_nested_braces(author)
        
        # Search query
        query = f"{clean_title} {clean_author}"
        
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
                    print(f"    📚 Fetched metadata from Semantic Scholar")
                    return metadata
        
        return None
        
    except Exception as e:
        print(f"    ⚠️  Error fetching from Semantic Scholar: {e}")
        return None

def fetch_metadata_from_crossref(title: str, author: str) -> Optional[Dict[str, str]]:
    """Fetch metadata from Crossref API as fallback."""
    try:
        # Clean the title and author for search
        clean_title = clean_nested_braces(title)
        clean_author = clean_nested_braces(author)
        
        # Crossref API endpoint
        url = "https://api.crossref.org/works"
        params = {
            "query": f"{clean_title} {clean_author}",
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
                    print(f"    📚 Fetched metadata from Crossref")
                    return metadata
        
        return None
        
    except Exception as e:
        print(f"    ⚠️  Error fetching from Crossref: {e}")
        return None

def enrich_bibtex_entry_with_metadata(fields: Dict[str, str]) -> Dict[str, str]:
    """Enrich BibTeX entry with metadata from external sources."""
    enriched_fields = fields.copy()
    
    # Only fetch if we don't already have key metadata
    if not enriched_fields.get("doi") and not enriched_fields.get("abstract"):
        title = enriched_fields.get("title", "")
        author = enriched_fields.get("author", "")
        
        if title and author:
            # Try Semantic Scholar first
            metadata = fetch_metadata_from_semantic_scholar(title, author)
            
            # Fallback to Crossref if Semantic Scholar fails
            if not metadata:
                metadata = fetch_metadata_from_crossref(title, author)
            
            # Merge fetched metadata with existing fields
            if metadata:
                for key, value in metadata.items():
                    if key not in enriched_fields or not enriched_fields[key]:
                        enriched_fields[key] = value
    
    return enriched_fields

def add_dimensions_tag_if_doi(bibtex_content: str, citation_key: str, fields: Dict[str, str]) -> str:
    """Add dimensions=true tag to BibTeX entry if DOI is present."""
    # Check if entry already has DOI and dimensions tag
    if not fields.get('doi') or 'dimensions' in fields:
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
    
    # Check if we need a comma before the dimensions tag
    content_before_brace = entry_content[:brace_pos].rstrip()
    needs_comma = not content_before_brace.endswith(',')
    
    # Prepare dimensions tag to add
    if needs_comma:
        tag_to_add = f",\n\tdimensions = {{true}}"
    else:
        tag_to_add = f"\n\tdimensions = {{true}}"
    
    # Insert tag before the closing brace
    modified_entry = entry_content[:brace_pos] + tag_to_add + entry_content[brace_pos:]
    
    # Replace the entry in the content
    modified_content = (
        bibtex_content[:start_pos] + 
        modified_entry + 
        bibtex_content[end_pos:]
    )
    
    return modified_content

def process_bibtex_file(bibtex_file: str, output_dir: str, regenerate: bool = False, 
                       force: bool = False, update_metadata: bool = True, 
                       thumbnail_size: str = '600x', test_mode: bool = False, 
                       test_count: int = 5, verbose: bool = False) -> None:
    """Main function to process the papers.bib file."""
    print(f"📚 Processing {bibtex_file}...")
    
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
        enriched_fields = enrich_bibtex_entry_with_metadata(fields)
        
        # Add selected=true tag if keywords contain 'featured' (do this before PDF processing to avoid conflicts)
        has_featured_keywords = 'keywords' in enriched_fields and enriched_fields['keywords'] and 'featured' in enriched_fields['keywords'].lower()
        if has_featured_keywords:
            modified_content = add_selected_tag_if_featured(modified_content, citation_key, enriched_fields)
        
        # Add dimensions=true tag if DOI is present
        if enriched_fields.get('doi'):
            modified_content = add_dimensions_tag_if_doi(modified_content, citation_key, enriched_fields)
        
        if not file_paths:
            print(f"  ❌ No PDF files found for {citation_key}")
            continue
        
        # Use the first PDF file found
        source_path = file_paths[0]
        
        # Extract filename from path
        filename = os.path.basename(source_path)
        
        # Clean filename for use in BibTeX
        clean_filename = clean_title_for_filename(fields.get('title', ''))
        author_filename = extract_author_names_for_filename(fields.get('author', ''))
        journal_filename = extract_journal_or_publisher_for_filename(fields)
        year = fields.get('year', '')
        
        # Create new filename in format: FIRSTNAME_SECONDNAME_etal_YEAR_TITLE_JOURNAL/INSTITUTION/PUBLISHER.pdf
        if author_filename and year and journal_filename:
            new_filename = f"{author_filename}_{year}_{clean_filename}_{journal_filename}.pdf"
        elif author_filename and year:
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
        modified_content = add_pdf_and_preview_tags(modified_content, citation_key, preview_filename, new_filename, fields)
                
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
    
    # Write the modified BibTeX content back to the file
    try:
        with open(bibtex_file, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        print(f"\n✅ Updated {bibtex_file} with pdf/slides, preview, and dimensions tags")
    except Exception as e:
        print(f"❌ Error writing to {bibtex_file}: {e}")
        return
    
    print(f"\n📊 Summary:")
    print(f"  Processed entries: {processed_count}")
    print(f"  Copied PDF files: {copied_count}")
    print(f"  Skipped entries: {skipped_count}")
    print(f"  Output directory: {output_dir}")

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
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Exiting due to missing dependencies.")
        sys.exit(1)

    if args.test:
        # Test mode: process only a small sample for quick testing
        print(f"🧪 Test mode: Will process only first {args.test_count} entries for quick testing")
        process_bibtex_file(working_bibtex_file, output_dir, False, args.force, 
                          update_metadata, args.thumbnail_size, True, args.test_count, args.verbose)
    elif args.regenerate:
        # Full regenerate mode: delete all files and reprocess everything
        print("🧹 Full regenerate mode: Will delete all existing files and reprocess everything")
        process_bibtex_file(working_bibtex_file, output_dir, True, args.force, 
                          update_metadata, args.thumbnail_size, False, 0, args.verbose)
    else:
        # Process new papers and generate thumbnails
        process_bibtex_file(working_bibtex_file, output_dir, False, args.force, 
                          update_metadata, args.thumbnail_size, False, 0, args.verbose)
    
    print(f"\n✅ Processing completed successfully!")

if __name__ == "__main__":
    main()

