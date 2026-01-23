#!/usr/bin/env python3
"""
Fix malformed tags in blog posts that were incorrectly added.
"""

import re
from pathlib import Path

def fix_file(file_path):
    """Fix malformed tags in a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for malformed tags that include "categories:" in them
    if re.search(r'tags:.*categories:', content):
        # Extract frontmatter
        frontmatter_match = re.match(r'^(---\n)(.*?)(\n---)', content, re.DOTALL)
        if not frontmatter_match:
            return False
        
        prefix = frontmatter_match.group(1)
        frontmatter_text = frontmatter_match.group(2)
        suffix = frontmatter_match.group(3)
        body = content[len(frontmatter_match.group(0)):]
        
        # Find and fix the malformed tags line
        # Remove the malformed tags line
        frontmatter_text = re.sub(r'^tags:.*?categories:.*?$', '', frontmatter_text, flags=re.MULTILINE)
        
        # Now add tags correctly before categories
        categories_match = re.search(r'^categories:', frontmatter_text, re.MULTILINE)
        if categories_match:
            insert_pos = categories_match.start()
            frontmatter_text = (
                frontmatter_text[:insert_pos].rstrip() + '\n' +
                'tags: ["AcademiaObscura"]\n' +
                frontmatter_text[insert_pos:]
            )
        
        new_content = prefix + frontmatter_text + suffix + body
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True
    
    return False

def main():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    posts_dir = project_root / '_posts'
    
    fixed_count = 0
    
    for post_file in sorted(posts_dir.glob('*.md')):
        if fix_file(post_file):
            print(f"Fixed: {post_file.name}")
            fixed_count += 1
    
    print(f"\nFixed {fixed_count} files")

if __name__ == '__main__':
    main()
