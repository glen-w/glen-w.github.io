#!/usr/bin/env python3
"""
FileManager class for process_papers.py
Handles all file operations including copying, directory creation, and file management.
"""

import os
import re
import shutil
import subprocess
import tempfile
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
        size = self._normalize_thumbnail_geometry(size or self.config.DEFAULT_THUMBNAIL_SIZE)

        try:
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
            prefix = [
                '-density', self.config.THUMBNAIL_DENSITY,
                f'{pdf_path}[0]',
                '-background', 'white',
                '-alpha', 'remove',
                '-strip',
            ]
            suffix = self._preview_fit_args(size, 'white') + [
                '-quality', self.config.THUMBNAIL_QUALITY,
                output_path,
            ]
            if self._run_magick(['magick'] + prefix + suffix, output_path):
                print(f"  ✅ Generated thumbnail: {os.path.basename(output_path)}")
                return True
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
                '-strip',
            ] + self._preview_fit_args(size, 'white') + [
                '-quality', self.config.THUMBNAIL_QUALITY,
                output_path,
            ]

            if self._run_magick(fallback_cmd, output_path):
                print(f"  ✅ Generated thumbnail with fallback: {os.path.basename(output_path)}")
                return True
            print(f"  ❌ Fallback also failed")
            self._cleanup_file(output_path)
            return False

        except Exception as e:
            print(f"  ❌ Fallback thumbnail generation failed: {e}")
            self._cleanup_file(output_path)
            return False
    
    def generate_svg_thumbnail(self, svg_path: str, output_path: str, size: str = None) -> bool:
        """Generate a thumbnail image from an SVG file using ImageMagick."""
        size = self._normalize_thumbnail_geometry(size or self.config.DEFAULT_THUMBNAIL_SIZE)

        try:
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
            prefix = [
                '-background', 'white',
                '-density', '150',
                svg_path,
                '-strip',
            ]
            suffix = self._preview_fit_args(size, 'white') + [
                '-quality', self.config.THUMBNAIL_QUALITY,
                output_path,
            ]
            if self._run_magick(['magick'] + prefix + suffix, output_path):
                print(f"  ✅ Generated SVG thumbnail: {os.path.basename(output_path)}")
                return True
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
                '-density', '150',
                svg_path,
                '-strip',
            ] + self._preview_fit_args(size, 'white') + [
                '-quality', self.config.THUMBNAIL_QUALITY,
                output_path,
            ]

            if self._run_magick(fallback_cmd, output_path):
                print(f"  ✅ Generated SVG thumbnail with fallback: {os.path.basename(output_path)}")
                return True
            print(f"  ❌ SVG fallback also failed")
            self._cleanup_file(output_path)
            return False

        except Exception as e:
            print(f"  ❌ Fallback SVG thumbnail generation failed: {e}")
            self._cleanup_file(output_path)
            return False

    @staticmethod
    def _normalize_thumbnail_geometry(size: str) -> str:
        """Append '>' so ImageMagick only shrinks images larger than the target box."""
        if not size:
            return size
        if size.endswith(('>', '<', '!', '^')):
            return size
        return f'{size}>'

    def _canvas_from_size(self, size: str) -> str:
        """WxH canvas for -extent; prefer the resize box, else PREVIEW_CANVAS."""
        raw = (size or '').rstrip('><!^')
        if re.fullmatch(r'\d+x\d+', raw):
            return raw
        return getattr(self.config, 'PREVIEW_CANVAS', '480x640')

    def _preview_fit_args(self, size: str, background: str) -> List[str]:
        """Fit inside the canvas, then pad so every preview is the same 3:4 frame."""
        return [
            '-resize', size,
            '-gravity', 'center',
            '-background', background,
            '-extent', self._canvas_from_size(size),
        ]

    def _flatten_alpha_args(self, background: str) -> List[str]:
        """Drop transparency onto a solid fill so logos do not sample as black."""
        return ['-background', background, '-alpha', 'remove', '-alpha', 'off']

    def _has_alpha(self, source_path: str) -> bool:
        """True when the source has a usable alpha channel (transparent logos)."""
        try:
            result = subprocess.run(
                ['magick', 'identify', '-quiet', '-format', '%A', source_path],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return (result.stdout or '').strip().lower() in {'true', 'blend'}
        except Exception:
            return False

    def _flatten_stddev(self, source_path: str, background: str) -> float:
        """How much detail remains after flattening onto a solid background."""
        try:
            result = subprocess.run(
                [
                    'magick',
                    source_path,
                    '-resize', '64x64>',
                    '-background', background,
                    '-alpha', 'remove',
                    '-format', '%[fx:standard_deviation]',
                    'info:',
                ],
                capture_output=True,
                text=True,
                timeout=15,
            )
            return float((result.stdout or '').strip())
        except (TypeError, ValueError, subprocess.SubprocessError):
            return 0.0

    def _hex_luminance(self, hex_color: str) -> float:
        digits = hex_color.lstrip('#')
        if not re.fullmatch(r'[0-9A-Fa-f]{6}', digits):
            return 1.0
        r = int(digits[0:2], 16)
        g = int(digits[2:4], 16)
        b = int(digits[4:6], 16)
        return (0.299 * r + 0.587 * g + 0.114 * b) / 255.0

    def _sample_pad_color(self, source_path: str) -> str:
        """Choose a mat that keeps the artwork visible, then match photos."""
        fallback_light = getattr(self.config, 'PREVIEW_PAD_FALLBACK', '#f0f0f0')
        fallback_dark = getattr(self.config, 'PREVIEW_PAD_DARK', '#1a1a1a')
        if self._has_alpha(source_path):
            white_sd = self._flatten_stddev(source_path, 'white')
            black_sd = self._flatten_stddev(source_path, 'black')
            if black_sd > white_sd * 1.2:
                return fallback_dark
            if white_sd > black_sd * 1.2:
                return fallback_light

        try:
            result = subprocess.run(
                [
                    'magick',
                    source_path,
                    *self._flatten_alpha_args('white'),
                    '-resize', '1x1!',
                    '-format', '%[hex:u.p{0,0}]',
                    'info:',
                ],
                capture_output=True,
                text=True,
                timeout=15,
            )
            hex_color = (result.stdout or '').strip().lstrip('#')
            if result.returncode == 0 and re.fullmatch(r'[0-9A-Fa-f]{6,8}', hex_color):
                sampled = f'#{hex_color[:6]}'
                if self._hex_luminance(sampled) < 0.22:
                    return fallback_light
                return sampled
        except Exception:
            pass
        return fallback_light

    def _run_magick(self, cmd: List[str], output_path: str) -> bool:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > self.config.MIN_THUMBNAIL_SIZE:
            return True
        if result.stderr and result.returncode != 0:
            print(f"     {result.stderr.strip()}")
        return False

    def optimize_preview_image(self, source_path: str, output_path: str, size: str = None) -> bool:
        """Resize/compress an image into a library preview thumbnail.

        Used for Zotero thumbnail attachments and other image sources so reprocessing
        does not reintroduce multi-megabyte preview files. Fits the source inside the
        canonical 3:4 canvas and pads with a sampled fill.
        """
        size = self._normalize_thumbnail_geometry(size or self.config.DEFAULT_THUMBNAIL_SIZE)
        pad = self._sample_pad_color(source_path)

        try:
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
            body = [
                source_path,
                '-auto-orient',
                '-strip',
            ] + self._flatten_alpha_args(pad) + self._preview_fit_args(size, pad) + [
                '-quality', self.config.THUMBNAIL_QUALITY,
                output_path,
            ]
            if self._run_magick(['magick'] + body, output_path):
                print(f"  ✅ Optimized preview thumbnail: {os.path.basename(output_path)}")
                return True

            print("  🔄 Trying fallback with legacy convert command for preview image...")
            if self._run_magick(['convert'] + body, output_path):
                print(f"  ✅ Optimized preview thumbnail: {os.path.basename(output_path)}")
                return True

            print(f"  ❌ Failed to optimize preview image: {os.path.basename(source_path)}")
            self._cleanup_file(output_path)
            return False

        except Exception as e:
            print(f"  ❌ Error optimizing preview image: {e}")
            self._cleanup_file(output_path)
            return False

    def normalize_preview_image(self, path: str, size: str = None) -> bool:
        """Fit an existing preview JPEG onto the canonical 3:4 canvas in place."""
        if not os.path.exists(path):
            print(f"  ❌ Preview not found: {path}")
            return False

        size = self._normalize_thumbnail_geometry(size or self.config.DEFAULT_THUMBNAIL_SIZE)
        pad = self._sample_pad_color(path)
        directory = os.path.dirname(path) or '.'
        fd, tmp_path = tempfile.mkstemp(suffix='.jpeg', dir=directory)
        os.close(fd)
        try:
            cmd = [
                'magick',
                path,
                '-auto-orient',
                '-strip',
            ] + self._flatten_alpha_args(pad) + self._preview_fit_args(size, pad) + [
                '-quality', self.config.THUMBNAIL_QUALITY,
                tmp_path,
            ]
            if self._run_magick(cmd, tmp_path):
                os.replace(tmp_path, path)
                print(f"  ✅ Normalized preview: {os.path.basename(path)}")
                return True
            print("  🔄 Trying fallback with legacy convert command for normalize...")
            fallback = ['convert'] + cmd[1:]
            if self._run_magick(fallback, tmp_path):
                os.replace(tmp_path, path)
                print(f"  ✅ Normalized preview: {os.path.basename(path)}")
                return True
            print(f"  ❌ Failed to normalize preview: {os.path.basename(path)}")
            return False
        except Exception as e:
            print(f"  ❌ Error normalizing preview {path}: {e}")
            return False
        finally:
            self._cleanup_file(tmp_path)

    def normalize_preview_directory(self, directory: str = None, size: str = None, verbose: bool = False) -> Dict[str, int]:
        """Rewrite every JPEG in the preview directory onto the 3:4 canvas."""
        directory = directory or self.config.PREVIEW_DIR
        stats = {'normalized': 0, 'skipped': 0, 'failed': 0}
        if not os.path.isdir(directory):
            print(f"❌ Preview directory not found: {directory}")
            return stats

        extensions = tuple(self.config.PREVIEW_EXTENSIONS)
        names = sorted(
            name for name in os.listdir(directory)
            if name.lower().endswith(extensions) and os.path.isfile(os.path.join(directory, name))
        )
        print(f"🖼️  Normalizing {len(names)} preview image(s) in {directory}")
        for name in names:
            path = os.path.join(directory, name)
            if self.normalize_preview_image(path, size):
                stats['normalized'] += 1
            else:
                stats['failed'] += 1
                if verbose:
                    print(f"  ⚠️  Skipped/failed: {name}")
        print(
            f"  ✅ Preview normalize complete: {stats['normalized']} updated, "
            f"{stats['failed']} failed"
        )
        return stats

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
    
    def copy_thumbnail_file(self, source_path: str, destination_path: str, force: bool = False, size: str = None) -> bool:
        """Write a resized/compressed preview thumbnail from an image source."""
        try:
            if os.path.exists(destination_path) and not force:
                print(f"  ⏭️  Thumbnail already exists: {os.path.basename(destination_path)}")
                return True
            return self.optimize_preview_image(source_path, destination_path, size)
        except Exception as e:
            print(f"  ❌ Error copying thumbnail {source_path}: {e}")
            return False
