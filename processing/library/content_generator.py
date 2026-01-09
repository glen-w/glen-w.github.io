"""
Content Generator

Generates markdown content and front matter for library pages.
"""

import yaml
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

from processing.library.bib_parser import BibParser
from processing.core.text_processor import TextProcessor
from processing.config import Configuration


class ContentGenerator:
    """Generates markdown content for library pages."""
    
    def __init__(self):
        """Initialize the content generator."""
        self.bib_parser = BibParser()
        self.config = Configuration()
        self.text_processor = TextProcessor(self.config)
    
    def generate_front_matter(self, entry: Dict[str, Any]) -> str:
        """Generate YAML front matter for the page."""
        # Basic metadata
        title = self.bib_parser.clean_title(entry.get('title', 'Untitled'))
        year = self.bib_parser.extract_year(entry)
        month = self.bib_parser.extract_month(entry)
        
        # Create date
        try:
            # Convert month name to number if needed
            month_names = {
                'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
                'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
                'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
            }
            
            if month.lower() in month_names:
                month_num = month_names[month.lower()]
            else:
                month_num = int(month)
            
            date_obj = datetime(int(year), month_num, 1)
            date_str = date_obj.strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            date_str = f"{year}-{month.zfill(2)}-01"
        
        # Generate description
        description = self.bib_parser.get_description(entry)
        
        # Extract tags and categories
        keywords = self.bib_parser.extract_keywords(entry)
        tags = [kw for kw in keywords if not kw.startswith('ignore')]
        
        # Determine categories based on entry type and keywords
        categories = self._determine_categories(entry, keywords)
        
        # Extract authors
        authors = self.bib_parser.format_authors(entry)
        author_names = [f"{author['first']} {author['last']}" for author in authors]
        
        # Extract links and media
        links = self.bib_parser.extract_links(entry)
        
        # Find processed images (transformed filenames) instead of original ones
        processed_images = self._find_processed_images(entry)
        
        # Build front matter
        front_matter = {
            'layout': 'library-item',
            'title': title,
            'date': date_str,
            'description': description,
            'tags': tags,
            'categories': categories,
            'entry_type': self.bib_parser.get_entry_type_display(entry),
            'authors': author_names,
            'venue': self.bib_parser.format_venue(entry),
            'year': year,
            'abstract': self.bib_parser.get_abstract(entry),
            'bibtex_key': entry.get('ID', ''),
        }
        
        # Add optional fields
        if links.get('url'):
            front_matter['url'] = links['url']
        if links.get('doi'):
            front_matter['doi'] = links['doi']
        if links.get('pdf'):
            front_matter['pdf'] = links['pdf']
        
        # Priority: Use generated thumbnail filename if it exists, otherwise use processed images
        # Check for existing generated thumbnail first (most reliable)
        thumbnail_filename = self._check_for_existing_thumbnail(entry)
        if thumbnail_filename:
            front_matter['preview'] = thumbnail_filename
            # Add gallery from processed images if available
            if processed_images:
                front_matter['gallery'] = processed_images
        elif processed_images:
            # Use first processed image as preview
            front_matter['preview'] = processed_images[0]
            if len(processed_images) > 1:
                front_matter['gallery'] = processed_images
        
        # Add zip_archive field and metadata if present in BibTeX entry
        if entry.get('zip_archive'):
            front_matter['zip_archive'] = entry['zip_archive']
            if entry.get('zip_file_count'):
                front_matter['zip_file_count'] = entry['zip_file_count']
            if entry.get('zip_file_size_mb'):
                front_matter['zip_file_size_mb'] = entry['zip_file_size_mb']
        
        # Add location if available
        if entry.get('address'):
            front_matter['location'] = entry['address']
        
        # Add additional metadata
        if entry.get('institution'):
            front_matter['institution'] = entry['institution']
        if entry.get('publisher'):
            front_matter['publisher'] = entry['publisher']
        if entry.get('pages'):
            front_matter['pages'] = entry['pages']
        if entry.get('volume'):
            front_matter['volume'] = entry['volume']
        if entry.get('number'):
            front_matter['number'] = entry['number']
        
        # Convert to YAML
        yaml_str = yaml.dump(front_matter, default_flow_style=False, allow_unicode=True)
        return f"---\n{yaml_str}---"
    
    def _determine_categories(self, entry: Dict[str, Any], keywords: List[str]) -> List[str]:
        """Determine categories based on entry type and keywords."""
        categories = []
        
        # Base category from entry type
        entry_type = entry.get('type', '').lower()
        if entry_type == 'article':
            categories.append('publications')
        elif entry_type in ['inproceedings', 'incollection']:
            categories.append('conferences')
        elif entry_type in ['phdthesis', 'mastersthesis', 'thesis']:
            categories.append('theses')
        elif entry_type == 'techreport':
            categories.append('reports')
        elif entry_type == 'misc':
            if any(kw in keywords for kw in ['blog', 'webinar', 'workshop']):
                categories.append('events')
            else:
                categories.append('other')
        else:
            categories.append('other')
        
        # Add topic-based categories
        topic_keywords = {
            'ocean': 'ocean-governance',
            'energy': 'energy-policy',
            'renewable': 'renewable-energy',
            'climate': 'climate-change',
            'marine': 'marine-policy',
            'biodiversity': 'biodiversity',
            'sustainability': 'sustainability',
            'policy': 'policy',
            'governance': 'governance',
        }
        
        for keyword in keywords:
            for topic, category in topic_keywords.items():
                if topic in keyword.lower():
                    if category not in categories:
                        categories.append(category)
                    break
        
        return categories if categories else ['other']
    
    def _check_for_existing_thumbnail(self, entry: Dict[str, Any]) -> Optional[str]:
        """Check if a thumbnail exists for this entry's PDF.
        
        Args:
            entry: The BibTeX entry dictionary
            
        Returns:
            The thumbnail filename (without path) if found, None otherwise
        """
        citation_key = entry.get('ID', '')
        if not citation_key:
            return None
        
        # Generate the expected thumbnail filename
        try:
            thumbnail_filename = self.text_processor.generate_filename(
                citation_key, 
                entry, 
                'jpeg',
                check_directory=self.config.PREVIEW_DIR
            )
            
            if thumbnail_filename:
                # Check if the file actually exists
                thumbnail_path = os.path.join(self.config.PREVIEW_DIR, thumbnail_filename)
                if os.path.exists(thumbnail_path):
                    # Return filename without extension (layout adds paths)
                    return thumbnail_filename.replace('.jpeg', '').replace('.jpg', '')
        except Exception:
            # If anything goes wrong, just return None
            pass
        
        return None
    
    def _find_processed_images(self, entry: Dict[str, Any]) -> List[str]:
        """Find processed image filenames for this entry.
        
        Looks for images in the publications directory that match the entry's
        transformed filename pattern (based on author, year, and title).
        
        Args:
            entry: The BibTeX entry dictionary
            
        Returns:
            List of processed image filenames (without extensions) found
        """
        if not os.path.exists(self.config.IMAGES_DIR):
            return []
        
        # Generate base filename pattern (same logic as file_manager.process_images_for_entry)
        author_filename = self.text_processor.extract_author_names_for_filename(entry.get('author', ''))
        title = entry.get('title', '')
        condensed_title = self.text_processor.remove_filler_words(title)
        clean_filename = self.text_processor.slugify_title(condensed_title, max_length=190, separator='_')
        year = entry.get('year', '')
        
        # Create base filename
        if author_filename and year:
            base_filename = f"{author_filename}_{year}_{clean_filename}"
        elif author_filename:
            base_filename = f"{author_filename}_{clean_filename}"
        else:
            base_filename = clean_filename
        
        # Clean up base filename
        base_filename = self.text_processor.clean_filename(base_filename).lower()
        
        # Find all files in publications directory that match the pattern
        processed_images = []
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        
        try:
            for filename in os.listdir(self.config.IMAGES_DIR):
                filename_lower = filename.lower()
                # Check if filename starts with base pattern and contains _photo_ or _figure_
                if filename_lower.startswith(base_filename) and ('_photo_' in filename_lower or '_figure_' in filename_lower):
                    # Check if it's an image file
                    if any(filename_lower.endswith(ext) for ext in image_extensions):
                        # Return filename without extension (consistent with preview field format)
                        # Template will add extension back
                        for ext in image_extensions:
                            if filename_lower.endswith(ext):
                                processed_images.append(filename[:-len(ext)])
                                break
            
            # Sort to ensure consistent order (photos before figures, then by number)
            processed_images.sort()
            
        except Exception:
            # If anything goes wrong, return empty list
            pass
        
        return processed_images
    
    def generate_content(self, entry: Dict[str, Any]) -> str:
        """Generate the main content for the library page."""
        content_parts = []
        
        # Abstract section - only show if different from description
        abstract = self.bib_parser.get_abstract(entry)
        description = self.bib_parser.get_description(entry)
        if abstract:
            # Only show abstract if it's meaningfully different from description
            abstract_clean = abstract.strip()[:200]  # First 200 chars for comparison
            description_clean = (description or '').strip()[:200]
            if abstract_clean != description_clean and len(abstract.strip()) > 50:
                content_parts.append("## Abstract\n")
                content_parts.append(abstract)
                content_parts.append("")
        
        # Publication details - only show if there's additional info beyond what's in header
        pub_details = []
        
        # Authors (only include if not already shown prominently in header)
        authors = self.bib_parser.format_authors(entry)
        if authors:
            author_names = []
            for author in authors:
                if author['first'] and author['last']:
                    author_names.append(f"{author['first']} {author['last']}")
                else:
                    author_names.append(author['full'])
            
            pub_details.append(f"**Authors:** {', '.join(author_names)}")
        
        # Venue and publication info
        venue = self.bib_parser.format_venue(entry)
        if venue:
            pub_details.append(f"**Venue:** {venue}")
        
        # Don't include Year and Location in Publication Details if they're already in header
        # (They're shown in the page front matter)
        
        # Location (only if not already in header via address field)
        if entry.get('address') and not entry.get('location'):
            pub_details.append(f"**Location:** {entry['address']}")
        
        # Additional fields
        if entry.get('volume'):
            pub_details.append(f"**Volume:** {entry['volume']}")
        if entry.get('number'):
            pub_details.append(f"**Number:** {entry['number']}")
        if entry.get('pages'):
            pub_details.append(f"**Pages:** {entry['pages']}")
        if entry.get('institution'):
            pub_details.append(f"**Institution:** {entry['institution']}")
        if entry.get('publisher'):
            pub_details.append(f"**Publisher:** {entry['publisher']}")
        
        # Only add Publication Details section if there's content
        if pub_details:
            content_parts.append("## Publication Details\n")
            content_parts.append("\n".join(pub_details))
            content_parts.append("")
        
        # Links and resources - only show if there are actual links
        links = self.bib_parser.extract_links(entry)
        link_items = []
        
        if links:
            if links.get('url'):
                link_items.append(f"- [Original URL]({links['url']})")
            if links.get('doi'):
                link_items.append(f"- [DOI]({links['doi']})")
            if links.get('arxiv'):
                link_items.append(f"- [arXiv]({links['arxiv']})")
            if links.get('pdf'):
                link_items.append(f"- [PDF]({links['pdf']})")
            if links.get('video'):
                link_items.append(f"- [Video]({links['video']})")
            if links.get('slides'):
                link_items.append(f"- [Slides]({links['slides']})")
            if links.get('poster'):
                link_items.append(f"- [Poster]({links['poster']})")
            
            # Additional links - exclude image files
            for key, url in links.items():
                if key not in ['url', 'doi', 'arxiv', 'pdf', 'video', 'slides', 'poster', 'preview']:
                    # Skip image files
                    if not url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg')):
                        link_items.append(f"- [Additional Link]({url})")
        
        # Only add Links and Resources section if there are actual links
        if link_items:
            content_parts.append("## Links and Resources\n")
            content_parts.append("\n".join(link_items))
            content_parts.append("")
        
        # Keywords - don't show (tags are already in header)
        # Removed to avoid redundancy
        
        # Notes and additional information
        if entry.get('note'):
            note = entry['note']
            # Clean up note (remove URLs that are already in links)
            note_lines = note.split('\n')
            clean_lines = []
            for line in note_lines:
                line = line.strip()
                if line and not line.startswith('http'):
                    clean_lines.append(line)
            
            if clean_lines:
                content_parts.append("## Notes\n")
                content_parts.append('\n'.join(clean_lines))
                content_parts.append("")
        
        return '\n'.join(content_parts)
