"""
Content Generator

Generates markdown content and front matter for library pages.
"""

import yaml
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# Add the processing directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from library.bib_parser import BibParser


class ContentGenerator:
    """Generates markdown content for library pages."""
    
    def __init__(self):
        """Initialize the content generator."""
        self.bib_parser = BibParser()
    
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
        images = self.bib_parser.extract_images(entry)
        
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
        if images:
            front_matter['preview'] = images[0]
            if len(images) > 1:
                front_matter['gallery'] = images
        
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
    
    def generate_content(self, entry: Dict[str, Any]) -> str:
        """Generate the main content for the library page."""
        content_parts = []
        
        # Abstract section
        abstract = self.bib_parser.get_abstract(entry)
        if abstract:
            content_parts.append("## Abstract\n")
            content_parts.append(abstract)
            content_parts.append("")
        
        # Publication details
        content_parts.append("## Publication Details\n")
        
        # Authors
        authors = self.bib_parser.format_authors(entry)
        if authors:
            author_names = []
            for author in authors:
                if author['first'] and author['last']:
                    author_names.append(f"{author['first']} {author['last']}")
                else:
                    author_names.append(author['full'])
            
            content_parts.append(f"**Authors:** {', '.join(author_names)}")
            content_parts.append("")
        
        # Venue and publication info
        venue = self.bib_parser.format_venue(entry)
        if venue:
            content_parts.append(f"**Venue:** {venue}")
        
        # Year
        year = self.bib_parser.extract_year(entry)
        content_parts.append(f"**Year:** {year}")
        
        # Location
        if entry.get('address'):
            content_parts.append(f"**Location:** {entry['address']}")
        
        # Additional fields
        if entry.get('volume'):
            content_parts.append(f"**Volume:** {entry['volume']}")
        if entry.get('number'):
            content_parts.append(f"**Number:** {entry['number']}")
        if entry.get('pages'):
            content_parts.append(f"**Pages:** {entry['pages']}")
        if entry.get('institution'):
            content_parts.append(f"**Institution:** {entry['institution']}")
        if entry.get('publisher'):
            content_parts.append(f"**Publisher:** {entry['publisher']}")
        
        content_parts.append("")
        
        # Links and resources
        links = self.bib_parser.extract_links(entry)
        if links:
            content_parts.append("## Links and Resources\n")
            
            if links.get('url'):
                content_parts.append(f"- [Original URL]({links['url']})")
            if links.get('doi'):
                content_parts.append(f"- [DOI]({links['doi']})")
            if links.get('arxiv'):
                content_parts.append(f"- [arXiv]({links['arxiv']})")
            if links.get('pdf'):
                content_parts.append(f"- [PDF]({links['pdf']})")
            if links.get('video'):
                content_parts.append(f"- [Video]({links['video']})")
            if links.get('slides'):
                content_parts.append(f"- [Slides]({links['slides']})")
            if links.get('poster'):
                content_parts.append(f"- [Poster]({links['poster']})")
            
            # Additional links
            for key, url in links.items():
                if key not in ['url', 'doi', 'arxiv', 'pdf', 'video', 'slides', 'poster']:
                    content_parts.append(f"- [Additional Link]({url})")
            
            content_parts.append("")
        
        # Keywords
        keywords = self.bib_parser.extract_keywords(entry)
        if keywords:
            content_parts.append("## Keywords\n")
            content_parts.append(", ".join(keywords))
            content_parts.append("")
        
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
