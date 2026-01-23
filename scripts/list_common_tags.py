#!/usr/bin/env python3
"""
One-off script to list the most common tags from blog posts.
Scans all posts in _posts/ directory and counts tag/category frequency.
"""

import os
import re
from collections import Counter
from pathlib import Path

def extract_frontmatter(file_path):
    """Extract YAML frontmatter from a markdown file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Match YAML frontmatter between --- markers
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        return {}
    
    frontmatter_text = frontmatter_match.group(1)
    frontmatter = {}
    
    # Simple YAML parser for tags and categories
    for line in frontmatter_text.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        # Match key: value patterns
        match = re.match(r'^(\w+):\s*(.*)$', line)
        if match:
            key = match.group(1)
            value = match.group(2).strip()
            
            # Handle list values (tags: ["tag1", "tag2"] or tags: ['tag1', 'tag2'] or tags: [tag1, tag2])
            if value.startswith('[') and value.endswith(']'):
                # Extract items from list, handling both single and double quotes
                if value == '[]':
                    # Empty list
                    frontmatter[key] = []
                else:
                    # Extract items, handling quotes and commas
                    items = re.findall(r'["\']([^"\']+)["\']', value)
                    if not items:
                        # Try without quotes - split by comma and clean up
                        items = [item.strip() for item in value[1:-1].split(',') if item.strip() and item.strip() != ',']
                    # Filter out empty strings and commas
                    frontmatter[key] = [item.strip() for item in items if item.strip() and item.strip() != ',']
            elif value:
                frontmatter[key] = value
            else:
                # Empty value (like "tags:" with nothing after)
                frontmatter[key] = None
    
    return frontmatter

def main():
    # Get the script directory and project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    posts_dir = project_root / '_posts'
    
    if not posts_dir.exists():
        print(f"Error: _posts directory not found at {posts_dir}")
        return
    
    tag_counter = Counter()
    category_counter = Counter()
    total_posts = 0
    posts_with_tags = 0
    posts_with_categories = 0
    
    # Process all markdown files in _posts
    for post_file in sorted(posts_dir.glob('*.md')):
        total_posts += 1
        frontmatter = extract_frontmatter(post_file)
        
        # Extract tags
        if 'tags' in frontmatter:
            tags = frontmatter['tags']
            if isinstance(tags, list) and tags:
                posts_with_tags += 1
                for tag in tags:
                    if tag and tag.strip() and tag.strip() != ',':  # Skip empty strings and commas
                        tag_counter[tag.strip()] += 1
            elif isinstance(tags, str) and tags.strip() and tags.strip() != ',':
                posts_with_tags += 1
                tag_counter[tags.strip()] += 1
        
        # Extract categories
        if 'categories' in frontmatter:
            categories = frontmatter['categories']
            if isinstance(categories, list) and categories:
                posts_with_categories += 1
                for category in categories:
                    if category and category.strip() and category.strip() != ',':  # Skip empty strings and commas
                        category_counter[category.strip()] += 1
            elif isinstance(categories, str) and categories.strip() and categories.strip() != ',':
                posts_with_categories += 1
                category_counter[categories.strip()] += 1
    
    # Display results
    print("=" * 60)
    print("BLOG POST TAG ANALYSIS")
    print("=" * 60)
    print(f"\nTotal posts scanned: {total_posts}")
    print(f"Posts with tags: {posts_with_tags}")
    print(f"Posts with categories: {posts_with_categories}")
    
    print("\n" + "=" * 60)
    print("MOST COMMON TAGS (sorted by frequency)")
    print("=" * 60)
    if tag_counter:
        for tag, count in tag_counter.most_common():
            print(f"  {tag:30s} : {count:3d} posts")
    else:
        print("  No tags found")
    
    print("\n" + "=" * 60)
    print("MOST COMMON CATEGORIES (sorted by frequency)")
    print("=" * 60)
    if category_counter:
        for category, count in category_counter.most_common():
            print(f"  {category:30s} : {count:3d} posts")
    else:
        print("  No categories found")
    
    # Combined view (tags + categories)
    print("\n" + "=" * 60)
    print("COMBINED TAGS + CATEGORIES (sorted by frequency)")
    print("=" * 60)
    combined = tag_counter + category_counter
    if combined:
        for item, count in combined.most_common():
            print(f"  {item:30s} : {count:3d} posts")
    else:
        print("  No tags or categories found")

if __name__ == '__main__':
    main()
