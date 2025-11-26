#!/usr/bin/env python3
"""
Script to generate book markdown files from a spreadsheet.
Fetches ISBNs, covers, genres, and publication year from Open Library API.
"""

import csv
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Dict, Optional, List
import requests

# Configuration
BOOKS_DIR = Path(__file__).parent.parent.parent / "_books"
COVERS_DIR = Path(__file__).parent.parent.parent / "assets/img/book_covers"
CACHE_FILE = Path(__file__).parent.parent.parent / "_books_cache.json"
API_TIMEOUT = 10
API_DELAY = 0.5  # Delay between API calls to be respectful

# Valid statuses - formalized set
VALID_STATUSES = ['read', 'queued', 'stalled', 'skimmed', 'abandoned', 're-read']

# Status mapping - normalize variations to canonical forms
STATUS_MAPPING = {
    'reread': 're-read',    # Normalize reread to re-read
    'unread': 'queued',     # Unread means queued to read
}


class BookMetadataFetcher:
    """Fetches book metadata from Open Library API."""
    
    def __init__(self):
        self.cache = {}
        self.load_cache()
    
    def load_cache(self) -> None:
        """Load metadata cache from file if it exists."""
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
                print(f"  📚 Loaded book cache with {len(self.cache)} entries")
            except Exception as e:
                print(f"  ⚠️  Could not load book cache: {e}")
                self.cache = {}
        else:
            self.cache = {}
    
    def save_cache(self) -> None:
        """Save metadata cache to file."""
        try:
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
            print(f"  💾 Saved book cache with {len(self.cache)} entries")
        except Exception as e:
            print(f"  ⚠️  Could not save book cache: {e}")
    
    def generate_cache_key(self, title: str, author: str) -> str:
        """Generate a cache key from title and author."""
        key = f"{title.lower().strip()}|{author.lower().strip()}"
        return re.sub(r'[^\w|]', '', key)
    
    def _extract_metadata_from_result(self, best_match: Dict) -> Dict:
        """Extract metadata from an Open Library API result."""
        metadata = {}
        
        # Extract title
        if best_match.get('title'):
            metadata['title'] = best_match['title']
        
        # Extract author
        if best_match.get('author_name'):
            authors = best_match['author_name']
            if isinstance(authors, list):
                metadata['author'] = authors[0]
            else:
                metadata['author'] = authors
        
        # Extract ISBN (prefer ISBN-13, fallback to ISBN-10)
        isbn = None
        if best_match.get('isbn'):
            isbns = best_match['isbn']
            if isinstance(isbns, list):
                # Prefer longer ISBNs (usually ISBN-13)
                isbn = max(isbns, key=len) if isbns else None
            else:
                isbn = isbns
        
        # Extract OLID (Open Library ID)
        olid = None
        if best_match.get('cover_edition_key'):
            olid = best_match['cover_edition_key']
        elif best_match.get('edition_key'):
            editions = best_match['edition_key']
            if isinstance(editions, list) and editions:
                olid = editions[0]
            else:
                olid = editions
        
        # Extract year
        if best_match.get('first_publish_year'):
            metadata['year'] = str(best_match['first_publish_year'])
        
        # Extract cover ID
        cover_id = best_match.get('cover_i')
        
        # Extract genres from subject field
        genres = []
        if best_match.get('subject'):
            subjects = best_match['subject']
            if isinstance(subjects, list):
                genres = [s.strip() for s in subjects if s.strip()]
            elif isinstance(subjects, str):
                genres = [subjects.strip()] if subjects.strip() else []
        
        metadata['isbn'] = isbn
        metadata['olid'] = olid
        metadata['cover_id'] = cover_id
        metadata['genres'] = genres
        
        return metadata
    
    def _search_open_library(self, title: str, author: Optional[str] = None, year: Optional[str] = None, use_query: bool = False) -> Optional[Dict]:
        """Search Open Library API with given parameters."""
        url = "https://openlibrary.org/search.json"
        
        if use_query:
            # Use general query search (more flexible)
            query_parts = [title]
            if author:
                query_parts.append(author)
            params = {
                "q": " ".join(query_parts),
                "limit": 10
            }
        else:
            # Use structured search
            params = {
                "title": title,
                "limit": 10  # Get more results for better matching
            }
            
            if author:
                params["author"] = author
        
        if year and not use_query:
            try:
                params["first_publish_year"] = int(year)
            except ValueError:
                pass  # Skip invalid year
        
        try:
            response = requests.get(url, params=params, timeout=API_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('docs') and len(data['docs']) > 0:
                    # Find best match using flexible title matching
                    best_match = None
                    title_lower = title.lower()
                    title_words = set(title_lower.split())
                    
                    best_score = 0
                    for doc in data['docs']:
                        doc_title = doc.get('title', '').lower()
                        doc_title_words = set(doc_title.split())
                        
                        # Calculate match score
                        score = 0
                        # Exact title match gets highest score
                        if title_lower == doc_title:
                            score = 100
                        # Title contains or is contained in doc title
                        elif title_lower in doc_title or doc_title in title_lower:
                            score = 80
                        # Word overlap
                        elif title_words & doc_title_words:
                            common_words = len(title_words & doc_title_words)
                            total_words = len(title_words | doc_title_words)
                            score = int((common_words / total_words) * 60) if total_words > 0 else 0
                        
                        # Prefer results with covers
                        if doc.get('cover_i') or doc.get('cover_edition_key'):
                            score += 10
                        
                        if score > best_score:
                            best_score = score
                            best_match = doc
                    
                    if best_match and best_score >= 30:  # Minimum threshold
                        return self._extract_metadata_from_result(best_match)
            
            return None
        except Exception as e:
            print(f"    ⚠️  API error: {e}")
            return None
    
    def fetch_book_metadata(self, title: str, author: str, year: Optional[str] = None) -> Optional[Dict]:
        """Fetch book metadata from Open Library API with multiple search strategies."""
        cache_key = self.generate_cache_key(title, author)
        
        # Check cache first
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            if cached is not None:
                print(f"    💾 Using cached data for: {title}")
                return cached
            else:
                # Cached as "not found" - skip API call
                return None
        
        print(f"    🔍 Searching Open Library for: {title} by {author}")
        
        # Strategy 1: Search with title and full author
        metadata = self._search_open_library(title, author, year)
        if metadata and (metadata.get('olid') or metadata.get('isbn')):
            self.cache[cache_key] = metadata
            print(f"    ✅ Found: {metadata.get('title', title)}")
            if metadata.get('isbn'):
                print(f"       ISBN: {metadata['isbn']}")
            if metadata.get('olid'):
                print(f"       OLID: {metadata['olid']}")
            if metadata.get('genres'):
                print(f"       Genres: {', '.join(metadata['genres'][:3])}{'...' if len(metadata['genres']) > 3 else ''}")
            time.sleep(API_DELAY)
            return metadata
        
        # Strategy 2: If author has comma, try first author only
        if ',' in author:
            first_author = author.split(',')[0].strip()
            print(f"    🔍 Trying with first author only: {first_author}")
            metadata = self._search_open_library(title, first_author, year)
            if metadata and (metadata.get('olid') or metadata.get('isbn')):
                self.cache[cache_key] = metadata
                print(f"    ✅ Found: {metadata.get('title', title)}")
                if metadata.get('isbn'):
                    print(f"       ISBN: {metadata['isbn']}")
                if metadata.get('olid'):
                    print(f"       OLID: {metadata['olid']}")
                time.sleep(API_DELAY)
                return metadata
            time.sleep(API_DELAY)
        
        # Strategy 3: Search by title only (more flexible)
        print(f"    🔍 Trying title-only search")
        metadata = self._search_open_library(title, None, year)
        if metadata and (metadata.get('olid') or metadata.get('isbn')):
            self.cache[cache_key] = metadata
            print(f"    ✅ Found: {metadata.get('title', title)}")
            if metadata.get('isbn'):
                print(f"       ISBN: {metadata['isbn']}")
            if metadata.get('olid'):
                print(f"       OLID: {metadata['olid']}")
            time.sleep(API_DELAY)
            return metadata
        time.sleep(API_DELAY)
        
        # Strategy 4: Try general query search (most flexible)
        print(f"    🔍 Trying general query search")
        metadata = self._search_open_library(title, author, year, use_query=True)
        if metadata and (metadata.get('olid') or metadata.get('isbn')):
            self.cache[cache_key] = metadata
            print(f"    ✅ Found: {metadata.get('title', title)}")
            if metadata.get('isbn'):
                print(f"       ISBN: {metadata['isbn']}")
            if metadata.get('olid'):
                print(f"       OLID: {metadata['olid']}")
            time.sleep(API_DELAY)
            return metadata
        
        # No results found
        self.cache[cache_key] = None
        print(f"    ⚠️  No results found for: {title}")
        time.sleep(API_DELAY)
        return None


def normalize_status(status: str) -> str:
    """Normalize status to valid status."""
    if not status:
        return 'uncategorized'
    
    status_lower = status.lower().strip()
    
    # Check mapping first (for variations like reread -> re-read)
    if status_lower in STATUS_MAPPING:
        return STATUS_MAPPING[status_lower]
    
    # Check if already valid
    if status_lower in VALID_STATUSES:
        return status_lower
    
    return 'uncategorized'


def slugify_title(title: str) -> str:
    """Convert title to a filename-friendly slug."""
    # Remove special characters, keep spaces and hyphens
    slug = re.sub(r'[^\w\s-]', '', title)
    # Replace spaces and multiple hyphens with single hyphen
    slug = re.sub(r'[-\s]+', '-', slug)
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    # Limit length
    if len(slug) > 100:
        slug = slug[:100]
    return slug.lower()


def download_cover(cover_id: Optional[str], olid: Optional[str], isbn: Optional[str], slug: str, force: bool = False) -> Optional[str]:
    """
    Download cover from Open Library. Returns relative path if successful.
    
    Tries sources in order of quality:
    1. cover_id (direct cover ID, best quality)
    2. olid (Open Library ID)
    3. isbn (ISBN)
    """
    cover_path = COVERS_DIR / f"{slug}.jpg"
    relative_path = f"assets/img/book_covers/{slug}.jpg"
    
    # Skip if cover already exists (unless force)
    if cover_path.exists() and not force:
        print(f"    📷 Cover exists: {slug}.jpg")
        return relative_path
    
    # Build list of URLs to try in priority order
    urls_to_try = []
    if cover_id:
        urls_to_try.append(f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg")
    if olid:
        urls_to_try.append(f"https://covers.openlibrary.org/b/olid/{olid}-L.jpg")
    if isbn:
        urls_to_try.append(f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg")
    
    if not urls_to_try:
        return None
    
    for url in urls_to_try:
        try:
            response = requests.get(url, timeout=API_TIMEOUT)
            
            if response.status_code == 200:
                # Check if we got an actual image (not a placeholder or error)
                content_type = response.headers.get('content-type', '')
                if 'image' in content_type and len(response.content) > 1000:
                    # Save the cover
                    with open(cover_path, 'wb') as f:
                        f.write(response.content)
                    print(f"    📷 Downloaded cover: {slug}.jpg")
                    time.sleep(API_DELAY)
                    return relative_path
            
            time.sleep(API_DELAY)
        except Exception as e:
            print(f"    ⚠️  Cover download error: {e}")
            time.sleep(API_DELAY)
    
    print(f"    ⚠️  No cover found for: {slug}")
    return None


def generate_book_markdown(book_data: Dict, metadata: Optional[Dict] = None, cover_path: Optional[str] = None) -> str:
    """Generate markdown content for a book."""
    # Start with front matter
    front_matter = {
        'layout': 'book-review',
        'title': f'"{book_data.get("title", "").strip()}"',
        'author': book_data.get('author', '').strip(),
    }
    
    # Add local cover path if downloaded
    if cover_path:
        front_matter['cover'] = cover_path
    
    # Add year/released from API
    if metadata and metadata.get('year'):
        front_matter['released'] = metadata['year']
    
    # Add status (include uncategorized to ensure it shows in the right section)
    status = normalize_status(book_data.get('status', ''))
    front_matter['status'] = status
    
    # Add rating (stars) if provided
    rating = book_data.get('rating', '').strip()
    if rating:
        try:
            # Convert to float to validate, then keep as string for YAML
            float(rating)
            front_matter['stars'] = rating
        except ValueError:
            pass  # Skip invalid ratings
    
    # Add tags from API genres
    if metadata and metadata.get('genres'):
        front_matter['tags'] = metadata['genres']
    
    # Generate YAML front matter
    lines = ['---']
    for key, value in front_matter.items():
        if value:
            if isinstance(value, list):
                lines.append(f"{key}:")
                for item in value:
                    # Escape special characters in YAML strings
                    item_str = str(item).replace('"', '\\"')
                    lines.append(f"  - {item_str}")
            else:
                lines.append(f"{key}: {value}")
    lines.append('---')
    lines.append('')  # Empty line after front matter
    
    return '\n'.join(lines)


def read_spreadsheet(filepath: str) -> List[Dict]:
    """Read book data from CSV with fixed columns: title, author, read, rating."""
    books = []
    
    with open(filepath, 'r', encoding='utf-8-sig') as f:  # utf-8-sig handles BOM
        reader = csv.DictReader(f)
        
        for row in reader:
            # Handle BOM in column names (strip BOM from first column if present)
            title_key = 'title'
            if '\ufefftitle' in row:
                title_key = '\ufefftitle'
            
            book_data = {
                'title': row.get(title_key, row.get('title', '')).strip(),
                'author': row.get('author', '').strip(),
                'status': row.get('status', '').strip(),
                'rating': row.get('rating', '').strip(),
            }
            
            # Only add if we have at least title and author
            if book_data['title'] and book_data['author']:
                books.append(book_data)
            else:
                print(f"  ⚠️  Skipping row: missing title or author")
    
    return books


def main():
    """Main function to process spreadsheet and generate book files."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate book markdown files from spreadsheet'
    )
    default_csv = Path(__file__).parent / 'books.csv'
    parser.add_argument(
        'spreadsheet',
        nargs='?',
        default=str(default_csv),
        help=f'Path to CSV spreadsheet with books (columns: title, author, status, rating). Default: {default_csv}'
    )
    parser.add_argument(
        '--skip-api',
        action='store_true',
        help='Skip API calls and only generate files from spreadsheet data'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Overwrite existing book files'
    )
    
    args = parser.parse_args()
    
    # Ensure directories exist
    BOOKS_DIR.mkdir(parents=True, exist_ok=True)
    COVERS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Read spreadsheet
    print(f"📖 Reading spreadsheet: {args.spreadsheet}")
    books = read_spreadsheet(args.spreadsheet)
    print(f"   Found {len(books)} books")
    
    # Initialize metadata fetcher
    fetcher = BookMetadataFetcher()
    
    # Process each book
    created = 0
    skipped = 0
    errors = 0
    
    for i, book_data in enumerate(books, 1):
        title = book_data['title']
        author = book_data['author']
        print(f"\n[{i}/{len(books)}] Processing: {title} by {author}")
        
        # Generate slug for filename and cover
        slug = slugify_title(title)
        filename = slug + '.md'
        filepath = BOOKS_DIR / filename
        
        # Check if file exists
        if filepath.exists() and not args.force:
            print(f"    ⏭️  File exists: {filename} (use --force to overwrite)")
            skipped += 1
            continue
        
        # Fetch metadata if not skipping API
        metadata = None
        if not args.skip_api:
            metadata = fetcher.fetch_book_metadata(
                title, 
                author
            )
        
        # Download cover if metadata available
        cover_path = None
        if metadata and not args.skip_api:
            cover_path = download_cover(
                cover_id=metadata.get('cover_id'),
                olid=metadata.get('olid'),
                isbn=metadata.get('isbn'),
                slug=slug,
                force=args.force
            )
        
        # If no cover found, mark as uncategorized
        if not cover_path:
            print(f"    ⚠️  No cover - marking as uncategorized")
            book_data['status'] = 'uncategorized'
        
        # Generate markdown
        try:
            content = generate_book_markdown(book_data, metadata, cover_path)
            
            # Write file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"    ✅ Created: {filename}")
            created += 1
            
        except Exception as e:
            print(f"    ❌ Error creating {filename}: {e}")
            errors += 1
    
    # Save cache
    fetcher.save_cache()
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  ✅ Created: {created}")
    print(f"  ⏭️  Skipped: {skipped}")
    print(f"  ❌ Errors: {errors}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()

