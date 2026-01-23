#!/usr/bin/env python3
"""
ZipArchiveGenerator class for process_papers.py
Generates zip archives containing all attachments for each library item.
"""

import os
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Any

from processing.config import Configuration
from processing.core.text_processor import TextProcessor


class ZipArchiveGenerator:
    """Generates zip archives for library items with organized folder structure."""
    
    def __init__(self, config: Configuration = None, text_processor: TextProcessor = None):
        """Initialize with configuration and text processor."""
        self.config = config or Configuration()
        self.text_processor = text_processor or TextProcessor(self.config)
        
        # Ensure zip directory exists
        os.makedirs(self.config.ZIP_DIR, exist_ok=True)
    
    def create_archive(self, citation_key: str, fields: Dict) -> Optional[Dict[str, Any]]:
        """
        Create a zip archive containing all processed files for an entry.
        
        Args:
            citation_key: The BibTeX citation key
            fields: Dictionary of BibTeX fields containing processed file references
            
        Returns:
            Dictionary with 'filename', 'file_count', and 'file_size_mb' if archive was created, None otherwise
        """
        # Collect all files organized by folder
        file_map = self._collect_files(fields)
        
        # Check if there are any files to archive
        total_files = sum(len(files) for files in file_map.values())
        if total_files == 0:
            return None
        
        # Generate zip filename
        zip_filename = self._get_zip_filename(citation_key, fields)
        if not zip_filename:
            print(f"  ⚠️  Could not generate zip filename for {citation_key}")
            return None
        
        zip_path = os.path.join(self.config.ZIP_DIR, zip_filename)
        
        # Create zip archive
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add main PDF to root
                for filename in file_map.get('root', []):
                    source_path = os.path.join(self.config.PDF_DIR, filename)
                    if os.path.exists(source_path):
                        zipf.write(source_path, filename)
                        print(f"  ✅ Added to zip (root): {filename}")
                    else:
                        print(f"  ⚠️  File not found for zip: {source_path}")
                
                # Add documents to documents/ folder
                for filename in file_map.get('documents', []):
                    source_path = os.path.join(self.config.PDF_DIR, filename)
                    if os.path.exists(source_path):
                        zip_path_in_archive = os.path.join('documents', filename)
                        zipf.write(source_path, zip_path_in_archive)
                        print(f"  ✅ Added to zip (documents): {filename}")
                    else:
                        print(f"  ⚠️  File not found for zip: {source_path}")
                
                # Add photos to photos/ folder
                for filename in file_map.get('photos', []):
                    source_path = os.path.join(self.config.IMAGES_DIR, filename)
                    if os.path.exists(source_path):
                        zip_path_in_archive = os.path.join('photos', filename)
                        zipf.write(source_path, zip_path_in_archive)
                        print(f"  ✅ Added to zip (photos): {filename}")
                    else:
                        print(f"  ⚠️  File not found for zip: {source_path}")
                
                # Add figures to figures/ folder
                for filename in file_map.get('figures', []):
                    source_path = os.path.join(self.config.IMAGES_DIR, filename)
                    if os.path.exists(source_path):
                        zip_path_in_archive = os.path.join('figures', filename)
                        zipf.write(source_path, zip_path_in_archive)
                        print(f"  ✅ Added to zip (figures): {filename}")
                    else:
                        print(f"  ⚠️  File not found for zip: {source_path}")
                
                # Add audio files to audio/ folder
                for filename in file_map.get('audio', []):
                    source_path = os.path.join(self.config.AUDIO_DIR, filename)
                    if os.path.exists(source_path):
                        zip_path_in_archive = os.path.join('audio', filename)
                        zipf.write(source_path, zip_path_in_archive)
                        print(f"  ✅ Added to zip (audio): {filename}")
                    else:
                        print(f"  ⚠️  File not found for zip: {source_path}")
            
            # Validate zip file was created
            if os.path.exists(zip_path) and os.path.getsize(zip_path) > 0:
                print(f"  ✅ Created zip archive: {zip_filename}")
                
                # Calculate metadata: file count and size
                file_count = 0
                file_size_bytes = os.path.getsize(zip_path)
                file_size_mb = self._format_file_size(file_size_bytes)
                
                # Count files in zip (excluding directories)
                with zipfile.ZipFile(zip_path, 'r') as zipf:
                    for name in zipf.namelist():
                        # Only count actual files, not directories
                        if not name.endswith('/'):
                            file_count += 1
                
                return {
                    'filename': zip_filename,
                    'file_count': file_count,
                    'file_size_mb': file_size_mb
                }
            else:
                print(f"  ❌ Zip archive creation failed: {zip_filename}")
                return None
                
        except Exception as e:
            print(f"  ❌ Error creating zip archive: {e}")
            # Clean up partial zip file if it exists
            if os.path.exists(zip_path):
                try:
                    os.remove(zip_path)
                except:
                    pass
            return None
    
    def _format_file_size(self, size_bytes: int) -> str:
        """
        Convert file size from bytes to human-readable MB format.
        
        Args:
            size_bytes: File size in bytes
            
        Returns:
            Formatted string with 1 decimal place (e.g., "2.3")
        """
        size_mb = size_bytes / (1024 * 1024)
        return f"{size_mb:.1f}"
    
    def _collect_files(self, fields: Dict) -> Dict[str, List[str]]:
        """
        Collect all processed files from BibTeX fields and organize by folder.
        
        Args:
            fields: Dictionary of BibTeX fields
            
        Returns:
            Dictionary mapping folder names to lists of filenames:
            {
                'root': [main_pdf_filename],
                'documents': [agenda_filename, slides_filename, ...],
                'photos': [photo_filenames],
                'figures': [figure_filenames],
                'audio': [audio_filenames]
            }
        """
        file_map: Dict[str, List[str]] = {
            'root': [],
            'documents': [],
            'photos': [],
            'figures': [],
            'audio': []
        }
        
        # Main PDF goes in root
        if 'pdf' in fields and fields['pdf']:
            file_map['root'].append(fields['pdf'])
        
        # Agenda and slides go in documents folder
        if 'agenda' in fields and fields['agenda']:
            file_map['documents'].append(fields['agenda'])
        
        if 'slides' in fields and fields['slides']:
            file_map['documents'].append(fields['slides'])
        
        # Photos go in photos folder
        if 'photos' in fields and fields['photos']:
            # Photos field is comma-separated list
            photos = [p.strip() for p in fields['photos'].split(',')]
            file_map['photos'].extend(photos)
        
        # Figures go in figures folder
        if 'figures' in fields and fields['figures']:
            # Figures field is comma-separated list
            figures = [f.strip() for f in fields['figures'].split(',')]
            file_map['figures'].extend(figures)
        
        # Audio files - need to extract from annote field
        if 'annote' in fields and fields['annote']:
            audio_files = self._extract_audio_from_annote(fields['annote'])
            file_map['audio'].extend(audio_files)
        
        return file_map
    
    def _extract_audio_from_annote(self, annote: Optional[str]) -> List[str]:
        """
        Extract audio filenames from annote field.
        
        The annote field may contain audio references in format:
        [audio]
        assets/audio/filename1.mp3
        assets/audio/filename2.mp3
        
        Returns:
            List of audio filenames (just the filename, not the full path)
        """
        audio_files: List[str] = []
        
        if not annote:
            return audio_files
        
        # Look for [audio] section
        lines = annote.split('\n')
        in_audio_section = False
        
        for line in lines:
            line = line.strip()
            if line == '[audio]':
                in_audio_section = True
                continue
            
            if in_audio_section:
                # Check if line is empty or starts a new section
                if not line or (line.startswith('[') and line.endswith(']')):
                    break
                
                # Extract filename from path like "assets/audio/filename.mp3"
                if 'assets/audio/' in line:
                    filename = os.path.basename(line)
                    if filename:
                        audio_files.append(filename)
        
        return audio_files
    
    def _get_zip_filename(self, citation_key: str, fields: Dict) -> Optional[str]:
        """
        Generate zip filename using same naming convention as other files.
        
        Args:
            citation_key: The BibTeX citation key
            fields: Dictionary of BibTeX fields
            
        Returns:
            Zip filename with .zip extension, or None if generation fails
        """
        # Use the same filename generation logic as PDFs
        filename = self.text_processor.generate_filename(
            citation_key, fields, 'zip', check_directory=self.config.ZIP_DIR
        )
        
        if filename:
            # Ensure it has .zip extension
            if not filename.endswith('.zip'):
                filename = filename.replace('.zip', '') + '.zip'
            return filename
        
        return None
