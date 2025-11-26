# Book CSV to Markdown Generator - Final Implementation Plan

## Overview
Generate book markdown files from CSV spreadsheet (`_books/books.csv`) with Open Library API integration for ISBNs, covers, genres, and publication year. Update book layouts to support all CSV statuses including the new "half-read" status.

## CSV Structure

The CSV has exactly 4 columns (in order):
- `title` - Book title
- `author` - Book author
- `status` - Reading status (read, reread, paused, abandoned, half-read, queued)
- `rating` - Personal rating (decimal number like 3.75, can be empty)

## Status Mapping

CSV Status → Valid Status:
- `read` → `finished`
- `reread` → `reread`
- `paused` → `paused`
- `abandoned` → `abandoned`
- `half-read` → `half-read` (NEW - needs to be added to layouts)
- `queued` → `queued`
- Invalid/missing → `uncategorized`

## Implementation Steps

### 1. Update Book Layout Files

#### 1.1 Update `_layouts/book-shelf.liquid`
- **File**: `_layouts/book-shelf.liquid`
- **Line**: 32
- **Change**: Add `half-read` to valid statuses list
- **From**: `'abandoned,finished,interested,paused,queued,reading,reread'`
- **To**: `'abandoned,finished,half-read,interested,paused,queued,reading,reread'`

#### 1.2 Update `_sass/_base.scss`
- **File**: `_sass/_base.scss`
- **Location**: After line 1748 (after `figcaption.reread` style)
- **Add**: CSS styling for `figcaption.half-read` status
- **Color**: `#f0ad4e` (amber) to indicate partial completion
- **Code**:
```scss
figcaption.half-read {
  font-family: monospace;
  color: #23212d;
  text-transform: uppercase;
  background-color: #f0ad4e;
}
```

### 2. Create Book Processing Script

#### 2.1 Create `processing/books/__init__.py`
- Empty file to make `books` a Python package

#### 2.2 Create `processing/books/generate_books.py`

**Script Structure:**

**Imports:**
```python
import csv
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Dict, Optional, List
import requests
```

**Configuration Constants:**
```python
BOOKS_DIR = Path(__file__).parent.parent / "_books"
CACHE_FILE = Path(__file__).parent.parent / "_books_cache.json"
API_TIMEOUT = 10
API_DELAY = 0.5  # Rate limiting between API calls
VALID_STATUSES = ['abandoned', 'finished', 'half-read', 'interested', 'paused', 'queued', 'reading', 'reread']
STATUS_MAPPING = {'read': 'finished'}
```

**BookMetadataFetcher Class:**

- `__init__()`: Initialize with cache file path
- `load_cache()`: Load JSON cache from file if exists
- `save_cache()`: Save cache to JSON file
- `generate_cache_key(title, author)`: Create cache key from normalized title and author
- `fetch_book_metadata(title, author, year=None)`:
  - Check cache first, return cached result if available
  - Query Open Library API: `https://openlibrary.org/search.json`
  - Parameters: `title`, `author`, `limit=5`, optionally `first_publish_year`
  - Find best match (prefer exact or close title match)
  - Extract from API response:
    - `title` → metadata['title']
    - `author_name[0]` → metadata['author']
    - `first_publish_year` → metadata['year']
    - `isbn` (prefer longest, usually ISBN-13) → metadata['isbn']
    - `cover_edition_key` or `edition_key[0]` → metadata['olid']
    - `cover_i` → metadata['cover_id']
    - `subject` → metadata['genres'] (array of genre strings)
  - Cache result (even if None to avoid repeated failed requests)
  - Return metadata dict or None
  - Add delay between API calls for rate limiting

**Helper Functions:**

- `normalize_status(status)`:
  - Map CSV statuses to valid statuses
  - `read` → `finished`
  - `half-read` → `half-read`
  - Others pass through if in VALID_STATUSES, else return `uncategorized`

- `slugify_title(title)`:
  - Convert title to filename-friendly slug
  - Remove special characters, replace spaces with hyphens
  - Limit to 100 characters
  - Return lowercase slug

- `generate_book_markdown(book_data, metadata=None)`:
  - Generate YAML front matter and markdown content
  - Front matter fields:
    - `layout: book-review`
    - `title`: from CSV (quoted string)
    - `author`: from CSV
    - `released`: from API metadata['year'] only
    - `status`: normalized from CSV
    - `stars`: from CSV rating (if provided and not empty)
    - `olid`: from API metadata (if available)
    - `isbn`: from API metadata (if no olid)
    - `tags`: from API metadata['genres'] (YAML array format, if available)
  - Return complete markdown string

- `read_spreadsheet(filepath)`:
  - Read CSV with fixed column names: title, author, status, rating
  - Use csv.DictReader
  - Extract exactly 4 fields: title, author, status, rating
  - Strip whitespace from all fields
  - Skip rows missing title or author
  - Return list of book dictionaries

**Main Function:**
- Argument parser:
  - Required: `spreadsheet` (CSV file path)
  - Optional: `--skip-api` (skip API calls, use only CSV data)
  - Optional: `--force` (overwrite existing files)
- Ensure `_books/` directory exists
- Read spreadsheet
- Initialize `BookMetadataFetcher`
- Process each book:
  - Fetch metadata from API (unless `--skip-api`)
  - Generate filename using `slugify_title()`
  - Check if file exists (skip unless `--force`)
  - Generate markdown content
  - Write to file
  - Track statistics (created, skipped, errors)
- Save cache
- Print summary statistics

### 3. Field Mapping

**From CSV to Front Matter:**
- `title` → `title` (quoted string in YAML)
- `author` → `author`
- `status` → `status` (normalized: read→finished, half-read→half-read)
- `rating` → `stars` (decimal number, only if provided and not empty)

**From API to Front Matter:**
- `first_publish_year` → `released`
- `subject` array → `tags` (YAML array format)
- `isbn` → `isbn`
- `cover_edition_key` → `olid`

### 4. Genre Handling from API

- Extract `subject` field from Open Library API response
- Normalize: trim whitespace, handle empty arrays
- Format as YAML array in front matter:
  ```yaml
  tags:
    - Fiction
    - Novels
    - Literature
  ```
- If no genres from API: don't add `tags` field
- Handle special characters in genre names

### 5. Error Handling

- API failures: cache None result, continue processing, log warning
- Missing fields: use defaults or skip field
- File write errors: log and continue with next book
- Invalid CSV: skip problematic rows with warning
- Special characters: handle in filenames and YAML (escape as needed)
- Empty rating: don't add `stars` field

### 6. Files to Create/Modify

**New Files:**
- `processing/books/__init__.py`
- `processing/books/generate_books.py`

**Modified Files:**
- `_layouts/book-shelf.liquid` (line 32: update statuses list)
- `_sass/_base.scss` (after line 1748: add half-read CSS)

**Generated Files:**
- `_books/{slugified-title}.md` (one per book from CSV)
- `_books_cache.json` (API response cache)

### 7. Status Color Scheme

- `abandoned`: #ee5f5b (red)
- `finished`: #62c462 (green)
- `half-read`: #f0ad4e (amber) - NEW
- `interested`: #7691db (blue)
- `paused`: #bdac7e (tan)
- `queued`: #9e76b5 (purple)
- `reading`: #f89406 (orange)
- `reread`: #a6517d (pink)
- `uncategorized`: #b0abb3 (gray)

### 8. Testing Considerations

- Test with `_books/books.csv` (6 books with various statuses)
- Verify all statuses display correctly with proper colors
- Test API caching (second run should use cache, no API calls)
- Test edge cases: missing fields, API failures, special characters in titles
- Verify genre extraction from API (subject field)
- Check filename generation (no conflicts, valid slugs, handles special chars)
- Test status normalization (read→finished, half-read→half-read)
- Verify empty rating handling (no stars field if empty)

## Usage

```bash
# Generate books from CSV with API calls
python processing/books/generate_books.py _books/books.csv

# Skip API calls (use only CSV data)
python processing/books/generate_books.py _books/books.csv --skip-api

# Overwrite existing files
python processing/books/generate_books.py _books/books.csv --force
```

