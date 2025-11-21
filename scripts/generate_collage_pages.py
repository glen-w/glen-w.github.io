#!/usr/bin/env python3
"""
Generate MD pages for collage images from template.

Scans subfolders in the collage directory, copies images to assets,
and generates MD pages with proper metadata.
"""

import argparse
import re
import shutil
from pathlib import Path


# Configuration
SOURCE_DIR = Path("/Users/89298/Documents/projects/collage/glen/")
TEMPLATE_PATH = Path(__file__).parent.parent / "templates" / "collage_template.md"
OUTPUT_MD_DIR = Path(__file__).parent.parent / "_creative"
OUTPUT_IMG_DIR = Path(__file__).parent.parent / "assets" / "img" / "collage"
BACKUP_DIR = Path(__file__).parent.parent / "backups" / "collage_md"

# Supported image extensions
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}


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


def get_title_from_filename(filename):
    """
    Convert filename (without extension) to title format.
    Replaces underscores with spaces and strips whitespace.
    """
    base_name = Path(filename).stem
    title = base_name.replace('_', ' ')
    return title.strip()


def backup_existing_md_files():
    """
    Backup all existing MD files in _creative directory before processing.
    Only keeps one copy (overwrites previous backup).
    """
    # Ensure backup directory exists
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    # Find all existing MD files in _creative
    existing_md_files = list(OUTPUT_MD_DIR.glob("*.md"))
    
    if not existing_md_files:
        print("No existing MD files to backup.")
        return 0
    
    backed_up = 0
    for md_file in existing_md_files:
        try:
            backup_path = BACKUP_DIR / md_file.name
            shutil.copy2(md_file, backup_path)
            backed_up += 1
        except Exception as e:
            print(f"  Warning: Failed to backup {md_file.name}: {e}")
    
    if backed_up > 0:
        print(f"Backed up {backed_up} existing MD file(s) to {BACKUP_DIR}")
    
    return backed_up


def file_exists(normalized_name, extension):
    """
    Check if both the image and MD file already exist.
    Returns True if both exist, False otherwise.
    """
    image_path = OUTPUT_IMG_DIR / f"{normalized_name}{extension}"
    md_path = OUTPUT_MD_DIR / f"{normalized_name}.md"
    return image_path.exists() and md_path.exists()


def process_collage_images(regenerate=False):
    """
    Main function to process all collage images and generate MD pages.
    
    Args:
        regenerate: If True, overwrite all existing files. If False, skip existing files.
    """
    # Read template
    if not TEMPLATE_PATH.exists():
        print(f"Error: Template not found at {TEMPLATE_PATH}")
        return
    
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Ensure output directories exist
    OUTPUT_MD_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_IMG_DIR.mkdir(parents=True, exist_ok=True)
    
    # Backup existing MD files before processing (only in regenerate mode)
    if regenerate:
        print("Regenerate mode: Backing up existing MD files...")
        backup_existing_md_files()
        print()
    else:
        print("Incremental mode: Skipping existing files, only processing new ones.")
        print()
    
    # Check if source directory exists
    if not SOURCE_DIR.exists():
        print(f"Error: Source directory not found at {SOURCE_DIR}")
        return
    
    # Process each subfolder
    processed_count = 0
    skipped_count = 0
    existing_count = 0
    
    for subfolder in SOURCE_DIR.iterdir():
        if not subfolder.is_dir():
            continue
        
        series_name = subfolder.name
        print(f"\nProcessing series: {series_name}")
        
        # Process each image in the subfolder
        for image_file in subfolder.iterdir():
            if not image_file.is_file():
                continue
            
            # Check if it's an image file
            if image_file.suffix.lower() not in IMAGE_EXTENSIONS:
                print(f"  Skipping non-image file: {image_file.name}")
                skipped_count += 1
                continue
            
            # Normalize filename (without extension)
            normalized_name = normalize_filename(image_file.name)
            original_extension = image_file.suffix.lower()
            
            if not normalized_name:
                print(f"  Warning: Could not normalize filename: {image_file.name}")
                skipped_count += 1
                continue
            
            # Check if file already exists (skip if not in regenerate mode)
            if not regenerate and file_exists(normalized_name, original_extension):
                print(f"  Skipping existing: {image_file.name} (already processed)")
                existing_count += 1
                continue
            
            # Copy image to assets directory
            dest_image_path = OUTPUT_IMG_DIR / f"{normalized_name}{original_extension}"
            image_existed = dest_image_path.exists()
            try:
                shutil.copy2(image_file, dest_image_path)
                action = "Overwritten" if regenerate and image_existed else "Copied"
                print(f"  {action}: {image_file.name} -> {dest_image_path.name}")
            except Exception as e:
                print(f"  Error copying {image_file.name}: {e}")
                skipped_count += 1
                continue
            
            # Generate MD file
            md_file_path = OUTPUT_MD_DIR / f"{normalized_name}.md"
            md_existed = md_file_path.exists()
            
            # Prepare replacements
            title = get_title_from_filename(image_file.name)
            img_path = f"assets/img/collage/{normalized_name}{original_extension}"
            
            # Start with a fresh copy of the template
            md_content = template
            
            # Replace template placeholders using regex for flexible matching
            # Replace title (match any quoted value and optional comment)
            md_content = re.sub(
                r'title: "[^"]*"(?:\s+#.*)?',
                f'title: "{title}"',
                md_content
            )
            # Replace img path (match any value and optional comment)
            md_content = re.sub(
                r'img: assets/img/collage/[^\s#]*(?:\s+#.*)?',
                f'img: {img_path}',
                md_content
            )
            # Replace series (match any value including comment, but only to end of line)
            md_content = re.sub(
                r'series:.*$',
                f'series: {series_name}',
                md_content,
                flags=re.MULTILINE
            )
            
            # Write MD file
            try:
                with open(md_file_path, 'w', encoding='utf-8') as f:
                    f.write(md_content)
                action = "Overwritten" if regenerate and md_existed else "Created"
                print(f"  {action}: {md_file_path.name}")
                processed_count += 1
            except Exception as e:
                print(f"  Error creating {md_file_path.name}: {e}")
                skipped_count += 1
    
    print(f"\n{'='*60}")
    print(f"Processing complete!")
    print(f"  Processed: {processed_count} images")
    if not regenerate:
        print(f"  Skipped (existing): {existing_count} files")
    print(f"  Skipped (errors): {skipped_count} files")
    print(f"{'='*60}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate MD pages for collage images from template.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Process only new images (skip existing)
  %(prog)s --regenerate       # Overwrite all existing files
        """
    )
    parser.add_argument(
        '--regenerate',
        action='store_true',
        help='Regenerate all files, overwriting existing ones'
    )
    
    args = parser.parse_args()
    process_collage_images(regenerate=args.regenerate)

