#!/usr/bin/env python3
"""
Add AcademiaObscura tag to all posts that have category:
- Academic Humour
- Adjuncts (or Adjuncts (guest posts))
"""

import re
from pathlib import Path

TARGET_CATEGORIES = ['Academic Humour', 'Adjuncts']

def has_target_category(frontmatter_text):
    """Check if frontmatter has any of the target categories."""
    for category in TARGET_CATEGORIES:
        # Check for exact match with quotes
        if f'"{category}"' in frontmatter_text or f"'{category}'" in frontmatter_text:
            return True
        # Also check for "Adjuncts (guest posts)"
        if category == 'Adjuncts' and 'Adjuncts' in frontmatter_text:
            return True
    return False

def has_academia_obscura_tag(frontmatter_text):
    """Check if frontmatter already has AcademiaObscura tag."""
    tags_match = re.search(r'^tags:\s*(.*?)$', frontmatter_text, re.MULTILINE)
    if tags_match:
        tags_value = tags_match.group(1).strip()
        if 'AcademiaObscura' in tags_value:
            return True
    return False

def add_academia_obscura_tag(content):
    """Add AcademiaObscura tag to frontmatter."""
    # Match YAML frontmatter
    frontmatter_match = re.match(r'^(---\n)(.*?)(\n---)', content, re.DOTALL)
    if not frontmatter_match:
        return content
    
    prefix = frontmatter_match.group(1)
    frontmatter_text = frontmatter_match.group(2)
    suffix = frontmatter_match.group(3)
    body = content[len(frontmatter_match.group(0)):]
    
    # Check if tags line exists
    tags_match = re.search(r'^tags:\s*(.*?)$', frontmatter_text, re.MULTILINE)
    
    if tags_match:
        # Tags line exists - add to existing tags
        tags_line = tags_match.group(0)
        tags_value = tags_match.group(1).strip()
        
        # Check if it's a list
        if tags_value.startswith('[') and tags_value.endswith(']'):
            # It's a list - add AcademiaObscura if not present
            if 'AcademiaObscura' not in tags_value:
                # Add to list
                if tags_value == '[]':
                    new_tags = '["AcademiaObscura"]'
                else:
                    # Insert before closing bracket
                    new_tags = tags_value[:-1] + ', "AcademiaObscura"]'
                frontmatter_text = frontmatter_text.replace(tags_line, f'tags: {new_tags}')
        elif tags_value:
            # Single tag value - convert to list
            frontmatter_text = frontmatter_text.replace(
                tags_line, 
                f'tags: ["{tags_value}", "AcademiaObscura"]'
            )
        else:
            # Empty tags - add as list
            frontmatter_text = frontmatter_text.replace(
                tags_line,
                'tags: ["AcademiaObscura"]'
            )
    else:
        # No tags line - add one before categories or at end
        categories_match = re.search(r'^categories:', frontmatter_text, re.MULTILINE)
        if categories_match:
            # Insert before categories
            insert_pos = categories_match.start()
            frontmatter_text = (
                frontmatter_text[:insert_pos].rstrip() + '\n' +
                'tags: ["AcademiaObscura"]\n' +
                frontmatter_text[insert_pos:]
            )
        else:
            # Add at end of frontmatter
            frontmatter_text = frontmatter_text.rstrip() + '\ntags: ["AcademiaObscura"]'
    
    return prefix + frontmatter_text + suffix + body

def process_file(file_path):
    """Process a single markdown file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        return False, "No frontmatter found"
    
    frontmatter_text = frontmatter_match.group(1)
    
    # Check if it has any target category
    if not has_target_category(frontmatter_text):
        return False, "Does not have target category"
    
    # Check if tag already exists
    if has_academia_obscura_tag(frontmatter_text):
        return False, "Already has AcademiaObscura tag"
    
    # Add the tag
    new_content = add_academia_obscura_tag(content)
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True, "Tag added successfully"

def main():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    posts_dir = project_root / '_posts'
    
    if not posts_dir.exists():
        print(f"Error: _posts directory not found at {posts_dir}")
        return
    
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    print(f"Looking for posts with categories: {', '.join(TARGET_CATEGORIES)}")
    print("=" * 60)
    
    # Process all markdown files
    for post_file in sorted(posts_dir.glob('*.md')):
        success, message = process_file(post_file)
        if success:
            print(f"✓ {post_file.name}: {message}")
            updated_count += 1
        elif "Already has" in message:
            print(f"- {post_file.name}: {message}")
            skipped_count += 1
        elif "Does not have" in message:
            # Don't print these - too many
            pass
        else:
            print(f"✗ {post_file.name}: {message}")
            error_count += 1
    
    print("\n" + "=" * 60)
    print(f"Summary:")
    print(f"  Updated: {updated_count} files")
    print(f"  Skipped (already has tag): {skipped_count} files")
    print(f"  Errors: {error_count} files")
    print("=" * 60)

if __name__ == '__main__':
    main()
