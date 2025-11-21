#!/usr/bin/env python3
"""
Migrate poems from source directory to _creative/ using poem template.

Reads markdown poem files, extracts content, and generates new files
in _creative/ directory using the poem template structure.
"""

import re
from pathlib import Path


# Configuration
SOURCE_DIR = Path("/Users/89298/Documents/projects/poems")
TEMPLATE_PATH = Path(__file__).parent.parent / "templates" / "poem template.md"
OUTPUT_DIR = Path(__file__).parent.parent / "_creative"


def normalize_filename(filename):
    """
    Normalize filename: lowercase, spaces to underscores, remove special chars.
    Returns filename WITHOUT extension.
    """
    # Split filename and extension
    base_name = Path(filename).stem
    
    # Convert to lowercase
    normalized = base_name.lower()
    
    # Replace spaces with underscores
    normalized = normalized.replace(' ', '_')
    
    # Remove special characters, keep alphanumeric, underscores, and hyphens
    normalized = re.sub(r'[^a-z0-9_-]', '', normalized)
    
    # Remove multiple consecutive underscores
    normalized = re.sub(r'_+', '_', normalized)
    
    # Remove leading/trailing underscores
    normalized = normalized.strip('_')
    
    return normalized


def extract_poem_content(content):
    """
    Extract poem content by removing the # title heading.
    Returns the remaining content as-is.
    """
    lines = content.split('\n')
    
    # Remove the first line if it starts with # (markdown heading)
    if lines and lines[0].strip().startswith('#'):
        # Remove the heading line
        lines = lines[1:]
        # Remove any empty line immediately after heading
        if lines and not lines[0].strip():
            lines = lines[1:]
    
    return '\n'.join(lines).strip()


def get_source_filename_title(filename):
    """
    Get the title from the source filename (without extension).
    Returns the original filename as-is for the title field.
    """
    return Path(filename).stem


def process_poems():
    """
    Main function to process all poem files and generate output files.
    """
    # Read template
    if not TEMPLATE_PATH.exists():
        print(f"Error: Template not found at {TEMPLATE_PATH}")
        return
    
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Check if source directory exists
    if not SOURCE_DIR.exists():
        print(f"Error: Source directory not found at {SOURCE_DIR}")
        return
    
    # Find the split point between frontmatter/liquid template and poem content
    # The template has YAML frontmatter, then liquid template, then poem content
    template_lines = template.split('\n')
    
    # Find where the liquid template block ends
    # The liquid template is between {% if page.img %} and {% endif %}
    liquid_end_idx = -1
    in_liquid_block = False
    
    for i, line in enumerate(template_lines):
        if '{% if page.img %}' in line:
            in_liquid_block = True
        if in_liquid_block and '{% endif %}' in line:
            liquid_end_idx = i
            break
    
    # Content starts after the liquid template block
    # Include the empty line after {% endif %} if present
    if liquid_end_idx >= 0:
        content_start_idx = liquid_end_idx + 1
        # Include the empty line after {% endif %} if it exists
        if content_start_idx < len(template_lines) and not template_lines[content_start_idx].strip():
            content_start_idx += 1
    else:
        # Fallback: find where frontmatter ends (after second ---)
        frontmatter_end = -1
        for i, line in enumerate(template_lines):
            if line.strip() == '---' and i > 0:  # Second ---
                frontmatter_end = i
                break
        if frontmatter_end >= 0:
            content_start_idx = frontmatter_end + 1
            # Skip liquid template lines and empty line
            while content_start_idx < len(template_lines):
                line = template_lines[content_start_idx]
                if line.strip() and not line.strip().startswith('{%'):
                    break
                content_start_idx += 1
        else:
            content_start_idx = 0
    
    # Split template into header (frontmatter + liquid + empty line) and placeholder content
    template_header = '\n'.join(template_lines[:content_start_idx])
    if content_start_idx <= len(template_lines):
        template_header += '\n'  # Add newline before content
    
    # Process each markdown file in source directory
    processed_count = 0
    skipped_count = 0
    
    for poem_file in sorted(SOURCE_DIR.glob('*.md')):
        if not poem_file.is_file():
            continue
        
        print(f"\nProcessing: {poem_file.name}")
        
        # Read source poem content
        try:
            with open(poem_file, 'r', encoding='utf-8') as f:
                source_content = f.read()
        except Exception as e:
            print(f"  Error reading {poem_file.name}: {e}")
            skipped_count += 1
            continue
        
        # Extract poem content (remove # title heading)
        poem_content = extract_poem_content(source_content)
        
        if not poem_content:
            print(f"  Warning: No content found in {poem_file.name}")
            skipped_count += 1
            continue
        
        # Normalize filename
        normalized_name = normalize_filename(poem_file.name)
        
        if not normalized_name:
            print(f"  Warning: Could not normalize filename: {poem_file.name}")
            skipped_count += 1
            continue
        
        # Get title from source filename
        source_title = get_source_filename_title(poem_file.name)
        
        # Generate MD file content
        # Start with template header
        md_content = template_header
        
        # Replace title in frontmatter
        md_content = re.sub(
            r'title: "[^"]*"',
            f'title: "{source_title}"',
            md_content
        )
        
        # Add poem content
        md_content += poem_content
        
        # Write MD file
        md_file_path = OUTPUT_DIR / f"{normalized_name}.md"
        
        # Check if file already exists - skip without overwriting
        if md_file_path.exists():
            print(f"  Skipped (already exists): {md_file_path.name}")
            skipped_count += 1
            continue
        
        try:
            with open(md_file_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            print(f"  Created: {md_file_path.name}")
            processed_count += 1
        except Exception as e:
            print(f"  Error creating {md_file_path.name}: {e}")
            skipped_count += 1
    
    print(f"\n{'='*60}")
    print(f"Processing complete!")
    print(f"  Processed: {processed_count} poems")
    print(f"  Skipped: {skipped_count} files")
    print(f"{'='*60}")


if __name__ == "__main__":
    process_poems()

