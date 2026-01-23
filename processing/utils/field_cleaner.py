#!/usr/bin/env python3
"""
FieldCleaner module for process_papers.py
Handles cleaning and removal of processed fields from BibTeX entries.
"""

import re
from typing import Dict, List, Optional, Tuple

from processing.config import Configuration


class FieldCleaner:
    """Handles cleaning and removal of processed fields from BibTeX entries."""
    
    def __init__(self, config: Configuration = None):
        """Initialize with configuration."""
        self.config = config or Configuration()
    
    def clean_file_field_from_images(self, file_field: str, processed_images: List[str] = None) -> str:
        """
        Remove image entries from the file field, keeping only PDFs, thumbnails, and other non-image files.
        
        Args:
            file_field: The file field content to clean
            processed_images: List of processed image filenames to remove
            
        Returns:
            Cleaned file field content
        """
        if not file_field:
            return file_field
        
        # Split by semicolon and filter out image entries (but keep thumbnails)
        file_parts = file_field.split(';')
        cleaned_parts = []
        
        for part in file_parts:
            part = part.strip()
            if not part:
                continue
            
            # Check if this is a thumbnail file
            is_thumbnail = self._is_thumbnail_file(part)
            
            # Check if this is an image file (but not thumbnail)
            is_image = self._is_image_file(part) and not is_thumbnail
            
            # Check if this is a processed image that should be removed
            is_processed_image = False
            if processed_images:
                for processed_image in processed_images:
                    if self._file_matches_processed(part, processed_image):
                        is_processed_image = True
                        break
            
            # Keep the part if it's not an image OR if it's a thumbnail OR if it's not a processed image
            if not is_image or is_thumbnail or not is_processed_image:
                cleaned_parts.append(part)
        
        # Return the cleaned file field
        if cleaned_parts:
            return '; '.join(cleaned_parts)
        else:
            return ''
    
    def clean_file_field_after_processing(self, file_field: str, fields: Dict) -> str:
        """
        Remove all processed files from the file field, keeping only unprocessed files.
        
        Args:
            file_field: The file field content to clean
            fields: The entry fields containing processed file information
            
        Returns:
            Cleaned file field content
        """
        if not file_field:
            return file_field
        
        # Get lists of processed files
        processed_files = self._get_processed_files(fields)
        
        # Keep only unprocessed files
        remaining_parts = []
        for part in file_field.split(';'):
            part = part.strip()
            if not part:
                continue
            
            # Check if this file was processed
            was_processed = self._was_file_processed(part, processed_files)
            
            # Keep the part if it wasn't processed
            if not was_processed:
                remaining_parts.append(part)
        
        # Return the cleaned file field
        if remaining_parts:
            return '; '.join(remaining_parts)
        else:
            return ''
    
    def remove_field_from_content(self, content: str, field_name: str) -> str:
        """
        Remove a specific field from BibTeX entry content while maintaining multi-line format.
        
        Args:
            content: The BibTeX entry content
            field_name: The name of the field to remove
            
        Returns:
            Content with the field removed
        """
        # More robust pattern that handles complex field values with proper brace matching
        pattern = rf'{re.escape(field_name)}\s*=\s*\{{'
        
        # Find the start of the field
        match = re.search(pattern, content, re.MULTILINE)
        if not match:
            return content
        
        start_pos = match.end() - 1  # Position of opening brace
        brace_count = 0
        end_pos = start_pos
        
        # Find matching closing brace
        for i in range(start_pos, len(content)):
            if content[i] == '{':
                brace_count += 1
            elif content[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_pos = i
                    break
        
        if brace_count == 0:  # Found matching closing brace
            # Remove the field and its value
            before_field = content[:match.start()]
            after_field = content[end_pos + 1:]
            
            # Clean up any trailing comma from the field
            after_field = re.sub(r'^\s*,?\s*', '', after_field)
            
            # Clean up any double commas that might be left
            cleaned_content = before_field + after_field
            cleaned_content = re.sub(r',\s*,', ',', cleaned_content)
            
            # Clean up trailing commas before closing brace
            cleaned_content = re.sub(r',\s*\n\s*}', '\n}', cleaned_content)
            
            return cleaned_content
        
        return content
    
    def remove_multiple_fields_from_content(self, content: str, field_names: List[str]) -> str:
        """
        Remove multiple fields from BibTeX entry content.
        
        Args:
            content: The BibTeX entry content
            field_names: List of field names to remove
            
        Returns:
            Content with the fields removed
        """
        cleaned_content = content
        for field_name in field_names:
            cleaned_content = self.remove_field_from_content(cleaned_content, field_name)
        return cleaned_content
    
    def _is_thumbnail_file(self, file_part: str) -> bool:
        """Check if a file part is a thumbnail file."""
        if ':' in file_part:
            # Format: description:path:mime
            parts = file_part.split(':')
            if len(parts) >= 2:
                description = parts[0].strip().lower()
                return 'thumbnail' in description
        else:
            # Format: path or filename
            return 'thumbnail' in file_part.lower()
        return False
    
    def _is_image_file(self, file_part: str) -> bool:
        """Check if a file part is an image file."""
        return any(f':image/{ext}' in file_part for ext in ['jpeg', 'jpg', 'png', 'gif'])
    
    def _file_matches_processed(self, file_part: str, processed_image: str) -> bool:
        """Check if a file part matches a processed image."""
        if ':' in file_part:
            # Format: description:path:mime
            parts = file_part.split(':')
            if len(parts) >= 2:
                path_part = parts[1].strip()
                return processed_image in path_part or path_part in processed_image
        else:
            # Format: path or filename
            return processed_image in file_part or file_part in processed_image
        return False
    
    def _get_processed_files(self, fields: Dict) -> Dict[str, List[str]]:
        """Get all processed files from fields."""
        processed_files = {
            'pdfs': [],
            'images': [],
            'thumbnails': []
        }
        
        # Get PDFs
        if 'pdf' in fields and fields['pdf']:
            processed_files['pdfs'].append(fields['pdf'])
        if 'slides' in fields and fields['slides']:
            processed_files['pdfs'].append(fields['slides'])
        
        # Get images
        if 'photos' in fields and fields['photos']:
            processed_files['images'].extend(fields['photos'].split(', '))
        if 'figures' in fields and fields['figures']:
            processed_files['images'].extend(fields['figures'].split(', '))
        
        # Get thumbnails
        if 'preview' in fields and fields['preview']:
            processed_files['thumbnails'].append(fields['preview'])
        
        return processed_files
    
    def _was_file_processed(self, file_part: str, processed_files: Dict[str, List[str]]) -> bool:
        """Check if a file part was processed."""
        # Check if it's a PDF that was processed
        if 'application/pdf' in file_part or file_part.endswith('.pdf'):
            for processed_pdf in processed_files['pdfs']:
                if self._file_matches_processed(file_part, processed_pdf):
                    return True
        
        # Check if it's an image that was processed
        if self._is_image_file(file_part):
            for processed_image in processed_files['images']:
                if self._file_matches_processed(file_part, processed_image):
                    return True
        
        # Check if it's a thumbnail that was processed
        if self._is_thumbnail_file(file_part):
            for processed_thumbnail in processed_files['thumbnails']:
                if self._file_matches_processed(file_part, processed_thumbnail):
                    return True
        
        return False


def main():
    """Command-line interface for field cleaning."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Clean BibTeX fields')
    parser.add_argument('--remove-field', help='Remove a specific field from content')
    parser.add_argument('--remove-fields', nargs='+', help='Remove multiple fields from content')
    parser.add_argument('--clean-file-field', help='Clean file field from images')
    parser.add_argument('--content', help='BibTeX content to process')
    
    args = parser.parse_args()
    
    cleaner = FieldCleaner()
    
    if args.remove_field and args.content:
        result = cleaner.remove_field_from_content(args.content, args.remove_field)
        print(result)
    elif args.remove_fields and args.content:
        result = cleaner.remove_multiple_fields_from_content(args.content, args.remove_fields)
        print(result)
    elif args.clean_file_field:
        result = cleaner.clean_file_field_from_images(args.clean_file_field)
        print(result)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
