#!/usr/bin/env python3
"""
FileManager class for process_papers.py
Handles all file operations including copying, directory creation, and file management.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Optional

from processing.config import Configuration


class FileManager:
    """Handles all file operations and management."""
    
    def __init__(self, config: Configuration = None):
        """Initialize with configuration."""
        self.config = config or Configuration()
    
    def ensure_directories_exist(self) -> None:
        """Ensure all required directories exist."""
        self.config.ensure_directories_exist()
    
    def copy_file(self, source_path: str, destination_path: str, force: bool = False) -> bool:
        """Copy a file from source to destination."""
        try:
            # Create destination directory if it doesn't exist
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            
            # Copy the file if it doesn't exist or if forced
            if not os.path.exists(destination_path) or force:
                shutil.copy2(source_path, destination_path)
                print(f"  ✅ Copied: {os.path.basename(source_path)} -> {os.path.basename(destination_path)}")
                return True
            else:
                print(f"  ⏭️  File already exists: {os.path.basename(destination_path)}")
                return True
                
        except Exception as e:
            print(f"  ❌ Error copying {source_path}: {e}")
            return False
    
    def generate_pdf_thumbnail(self, pdf_path: str, output_path: str, size: str = None) -> bool:
        """Generate a thumbnail image of the first page of a PDF using ImageMagick."""
        if size is None:
            size = self.config.DEFAULT_THUMBNAIL_SIZE
        
        try:
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Use modern ImageMagick 7 'magick' command
            cmd = [
                'magick', 
                '-density', self.config.THUMBNAIL_DENSITY,
                f'{pdf_path}[0]',
                '-background', 'white',
                '-alpha', 'remove',
                '-resize', size,
                '-quality', self.config.THUMBNAIL_QUALITY,
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Verify the generated file is not empty or corrupted
                if os.path.exists(output_path) and os.path.getsize(output_path) > self.config.MIN_THUMBNAIL_SIZE:
                    print(f"  ✅ Generated thumbnail: {os.path.basename(output_path)}")
                    return True
                else:
                    print(f"  ❌ Generated thumbnail is too small or corrupted")
                    self._cleanup_file(output_path)
                    return False
            else:
                # Try fallback with legacy convert command
                print("  🔄 Trying fallback with legacy convert command...")
                return self._generate_thumbnail_fallback(pdf_path, output_path, size)
                
        except Exception as e:
            print(f"  ❌ Error generating thumbnail: {e}")
            self._cleanup_file(output_path)
            return False
    
    def _generate_thumbnail_fallback(self, pdf_path: str, output_path: str, size: str) -> bool:
        """Fallback thumbnail generation using legacy convert command."""
        try:
            fallback_cmd = [
                'convert',
                '-density', self.config.THUMBNAIL_DENSITY,
                f'{pdf_path}[0]',
                '-background', 'white',
                '-alpha', 'remove',
                '-resize', size,
                '-quality', self.config.THUMBNAIL_QUALITY,
                output_path
            ]
            
            fallback_result = subprocess.run(fallback_cmd, capture_output=True, text=True)
            if fallback_result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > self.config.MIN_THUMBNAIL_SIZE:
                print(f"  ✅ Generated thumbnail with fallback: {os.path.basename(output_path)}")
                return True
            else:
                print(f"  ❌ Fallback also failed")
                self._cleanup_file(output_path)
                return False
                
        except Exception as e:
            print(f"  ❌ Fallback thumbnail generation failed: {e}")
            self._cleanup_file(output_path)
            return False
    
    def generate_svg_thumbnail(self, svg_path: str, output_path: str, size: str = None) -> bool:
        """Generate a thumbnail image from an SVG file using ImageMagick."""
        if size is None:
            size = self.config.DEFAULT_THUMBNAIL_SIZE
        
        try:
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Use modern ImageMagick 7 'magick' command to convert SVG to JPEG
            cmd = [
                'magick', 
                '-background', 'white',
                '-density', '300',  # High DPI for crisp SVG rendering
                svg_path,
                '-resize', size,
                '-quality', self.config.THUMBNAIL_QUALITY,
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Verify the generated file is not empty or corrupted
                if os.path.exists(output_path) and os.path.getsize(output_path) > self.config.MIN_THUMBNAIL_SIZE:
                    print(f"  ✅ Generated SVG thumbnail: {os.path.basename(output_path)}")
                    return True
                else:
                    print(f"  ❌ Generated SVG thumbnail is too small or corrupted")
                    self._cleanup_file(output_path)
                    return False
            else:
                # Try fallback with legacy convert command
                print("  🔄 Trying fallback with legacy convert command for SVG...")
                return self._generate_svg_thumbnail_fallback(svg_path, output_path, size)
                
        except Exception as e:
            print(f"  ❌ Error generating SVG thumbnail: {e}")
            self._cleanup_file(output_path)
            return False
    
    def _generate_svg_thumbnail_fallback(self, svg_path: str, output_path: str, size: str) -> bool:
        """Fallback SVG thumbnail generation using legacy convert command."""
        try:
            fallback_cmd = [
                'convert',
                '-background', 'white',
                '-density', '300',
                svg_path,
                '-resize', size,
                '-quality', self.config.THUMBNAIL_QUALITY,
                output_path
            ]
            
            fallback_result = subprocess.run(fallback_cmd, capture_output=True, text=True)
            if fallback_result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > self.config.MIN_THUMBNAIL_SIZE:
                print(f"  ✅ Generated SVG thumbnail with fallback: {os.path.basename(output_path)}")
                return True
            else:
                print(f"  ❌ SVG fallback also failed")
                self._cleanup_file(output_path)
                return False
                
        except Exception as e:
            print(f"  ❌ Fallback SVG thumbnail generation failed: {e}")
            self._cleanup_file(output_path)
            return False

    def _cleanup_file(self, file_path: str) -> None:
        """Clean up a file if it exists."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except (OSError, PermissionError):
            # Ignore permission errors when cleaning up
            pass
    
    def process_images_for_entry(self, citation_key: str, fields: Dict[str, str], output_dir: str, force: bool = False, regenerate: bool = False, verbose: bool = False) -> Dict[str, List[str]]:
        """Process images for a BibTeX entry, copying and renaming them."""
        if 'file' not in fields or not fields['file']:
            return {}
        
        # Parse file field to find images, keeping track of both entry and path
        file_entries = fields['file'].split(';')
        image_data = []  # List of (file_entry, file_path) tuples
        
        for file_entry in file_entries:
            if any(f'image/{ext}' in file_entry for ext in ['jpeg', 'jpg', 'png', 'gif']):
                # Extract the file path from the file entry
                parts = file_entry.split(':')
                if len(parts) >= 2:
                    file_path = parts[1].strip()
                    if os.path.exists(file_path):
                        image_data.append((file_entry.strip(), file_path))
        
        if not image_data:
            return {}
        
        # Generate base filename components
        from core.text_processor import TextProcessor
        text_processor = TextProcessor(self.config)
        
        author_filename = text_processor.extract_author_names_for_filename(fields.get('author', ''))
        title = fields.get('title', '')
        condensed_title = text_processor.remove_filler_words(title)
        # Use slugify_title with underscores for filenames (consistent with PDF filename conventions)
        clean_filename = text_processor.slugify_title(condensed_title, max_length=190, separator='_')
        year = fields.get('year', '')
        
        # Create base filename
        if author_filename and year:
            base_filename = f"{author_filename}_{year}_{clean_filename}"
        elif author_filename:
            base_filename = f"{author_filename}_{clean_filename}"
        else:
            base_filename = clean_filename
        
        # Clean up base filename
        base_filename = text_processor.clean_filename(base_filename)
        
        # Initialize image classifier
        # Enable image content analysis when regenerating (slower but more accurate)
        from utils.image_classifier import ImageClassifier
        enable_analysis = regenerate or self.config.ENABLE_IMAGE_CONTENT_ANALYSIS
        classifier_verbose = verbose or self.config.IMAGE_CLASSIFICATION_VERBOSE
        classifier = ImageClassifier(enable_image_analysis=enable_analysis, verbose=classifier_verbose)
        
        # Process each image
        processed_images = {}
        figure_count = 1
        photo_count = 1
        
        for file_entry, image_path in image_data:
            original_filename = os.path.basename(image_path)
            file_extension = os.path.splitext(original_filename)[1].lower()
            
            # Use classifier to determine if it's a figure or photo
            image_type = classifier.classify_image(file_entry, image_path)
            
            # Generate new filename based on classification
            if image_type == 'figure':
                new_filename = f"{base_filename}_figure_{figure_count:02d}{file_extension}".lower()
                figure_count += 1
            else:  # 'photo'
                new_filename = f"{base_filename}_photo_{photo_count:02d}{file_extension}".lower()
                photo_count += 1
            
            # Create destination path
            dest_path = os.path.join(self.config.IMAGES_DIR, new_filename)
            
            # Copy file if it doesn't exist or if forced
            if self.copy_file(image_path, dest_path, force):
                # Store the processed image info
                if image_type not in processed_images:
                    processed_images[image_type] = []
                processed_images[image_type].append(new_filename)
                if verbose:
                    print(f"  📸 Classified and processed {image_type}: {new_filename}")
        
        return processed_images
    
    def clean_file_field_from_images(self, entry_content: str) -> str:
        """Remove image entries from the file field, keeping only PDFs and other non-image files."""
        import re
        
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
            if part and not any(f':image/{ext}' in part for ext in ['jpeg', 'jpg', 'png', 'gif']):
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
    
    def cleanup_existing_files(self, regenerate: bool = False) -> None:
        """Clean up existing PDF files and thumbnails if regenerate flag is set."""
        if not regenerate:
            return
        
        print("🧹 Regenerate mode: Cleaning up existing files...")
        
        # Clean up PDF directory
        if os.path.exists(self.config.PDF_DIR):
            for file in os.listdir(self.config.PDF_DIR):
                if file.endswith('.pdf'):
                    file_path = os.path.join(self.config.PDF_DIR, file)
                    try:
                        os.remove(file_path)
                        print(f"  🗑️  Deleted: {file}")
                    except Exception as e:
                        print(f"  ⚠️  Could not delete {file}: {e}")
        
        # Clean up preview directory
        if os.path.exists(self.config.PREVIEW_DIR):
            for file in os.listdir(self.config.PREVIEW_DIR):
                if file.endswith(tuple(self.config.PREVIEW_EXTENSIONS)):
                    file_path = os.path.join(self.config.PREVIEW_DIR, file)
                    try:
                        os.remove(file_path)
                        print(f"  🗑️  Deleted: {file}")
                    except Exception as e:
                        print(f"  ⚠️  Could not delete {file}: {e}")
        
        print("  ✅ Cleanup complete")
    
    def create_backup(self, file_path: str) -> Optional[str]:
        """Create a backup of a file."""
        try:
            backup_path = self.config.get_backup_filename(file_path)
            shutil.copy2(file_path, backup_path)
            print(f"  💾 Created backup: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"  ⚠️  Warning: Could not create backup: {e}")
            return None
    
    def file_exists(self, file_path: str) -> bool:
        """Check if a file exists."""
        return os.path.exists(file_path)
    
    def get_file_size(self, file_path: str) -> int:
        """Get the size of a file in bytes."""
        try:
            return os.path.getsize(file_path)
        except OSError:
            return 0
    
    def list_files_in_directory(self, directory: str, extensions: List[str] = None) -> List[str]:
        """List files in a directory with optional extension filtering."""
        if not os.path.exists(directory):
            return []
        
        files = []
        for file in os.listdir(directory):
            if extensions is None or any(file.endswith(ext) for ext in extensions):
                files.append(file)
        
        return files
    
    def copy_thumbnail_file(self, source_path: str, destination_path: str, force: bool = False) -> bool:
        """Copy a thumbnail file from source to destination."""
        try:
            # Create destination directory if it doesn't exist
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            
            # Copy the file if it doesn't exist or if forced
            if not os.path.exists(destination_path) or force:
                shutil.copy2(source_path, destination_path)
                print(f"  ✅ Copied thumbnail: {os.path.basename(source_path)} -> {os.path.basename(destination_path)}")
                return True
            else:
                print(f"  ⏭️  Thumbnail already exists: {os.path.basename(destination_path)}")
                return True
                
        except Exception as e:
            print(f"  ❌ Error copying thumbnail {source_path}: {e}")
            return False
