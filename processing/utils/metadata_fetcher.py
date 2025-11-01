#!/usr/bin/env python3
"""
MetadataFetcher class for process_papers.py
Handles all external API calls for metadata enrichment.
"""

import json
import os
import requests
import sys
from typing import Dict, Optional

# Add the processing directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Configuration
from core.text_processor import TextProcessor


class MetadataFetcher:
    """Handles all external API calls for metadata enrichment."""
    
    def __init__(self, config: Configuration = None, text_processor: TextProcessor = None):
        """Initialize with configuration and text processor."""
        self.config = config or Configuration()
        self.text_processor = text_processor or TextProcessor(config)
        self.cache = {}
        self.cache_file = self.config.CACHE_FILE
    
    def load_cache(self) -> None:
        """Load metadata cache from file if it exists."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
                print(f"  📚 Loaded metadata cache with {len(self.cache)} entries")
            except Exception as e:
                print(f"  ⚠️  Could not load metadata cache: {e}")
                self.cache = {}
        else:
            self.cache = {}
    
    def save_cache(self) -> None:
        """Save metadata cache to file."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
            print(f"  💾 Saved metadata cache with {len(self.cache)} entries")
        except Exception as e:
            print(f"  ⚠️  Could not save metadata cache: {e}")
    
    def is_metadata_complete(self, fields: Dict[str, str]) -> bool:
        """Check if metadata is complete enough to skip API calls."""
        present_fields = 0
        for field in self.config.REQUIRED_METADATA_FIELDS:
            if field in fields and fields[field] and fields[field].strip():
                present_fields += 1
        
        return present_fields >= self.config.MIN_REQUIRED_FIELDS
    
    def should_fetch_metadata(self, fields: Dict[str, str], force_refetch: bool = False, verbose: bool = False) -> bool:
        """Determine if metadata should be fetched from external APIs."""
        if force_refetch:
            if verbose:
                print(f"    🔄 Force refetch enabled - will fetch metadata")
            return True
        
        # Check if metadata is already complete
        if self.is_metadata_complete(fields):
            if verbose:
                print(f"    ✅ Metadata already complete - skipping API calls")
            return False
        
        # Check if we have the most critical fields (DOI and abstract)
        has_doi = fields.get('doi') and fields['doi'].strip()
        has_abstract = fields.get('abstract') and fields['abstract'].strip()
        
        if has_doi and has_abstract:
            if verbose:
                print(f"    ✅ Has DOI and abstract - skipping API calls")
            return False
        
        if verbose:
            missing_fields = []
            if not has_doi:
                missing_fields.append('DOI')
            if not has_abstract:
                missing_fields.append('abstract')
            if not fields.get('keywords'):
                missing_fields.append('keywords')
            if not fields.get('journal'):
                missing_fields.append('journal')
            print(f"    📡 Missing fields: {', '.join(missing_fields)} - will fetch metadata")
        
        return True
    
    def fetch_metadata_from_semantic_scholar(self, title: str, author: str, verbose: bool = False) -> Optional[Dict[str, str]]:
        """Fetch metadata from Semantic Scholar API with caching."""
        # Check cache first
        cache_key = self.text_processor.generate_cache_key(title, author)
        if cache_key in self.cache:
            if verbose:
                print(f"    💾 Using cached metadata for Semantic Scholar")
            return self.cache[cache_key].get('semantic_scholar')
        
        try:
            # Search query
            query = f"{title} {author}"
            
            if verbose:
                print(f"    🔍 Searching Semantic Scholar for: {query[:60]}...")
            
            # Semantic Scholar API endpoint
            url = self.config.SEMANTIC_SCHOLAR_URL
            params = {
                "query": query,
                "limit": 1,
                "fields": "paperId,title,abstract,doi,isbn,keywords,venue,year,authors"
            }
            
            response = requests.get(url, params=params, timeout=self.config.API_TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                if data.get("data") and len(data["data"]) > 0:
                    paper = data["data"][0]
                    
                    metadata = {}
                    
                    # Extract DOI
                    if paper.get("doi"):
                        metadata["doi"] = paper["doi"]
                    
                    # Extract ISBN
                    if paper.get("isbn"):
                        metadata["isbn"] = paper["isbn"]
                    
                    # Extract abstract
                    if paper.get("abstract"):
                        metadata["abstract"] = paper["abstract"]
                    
                    # Extract keywords
                    if paper.get("keywords"):
                        metadata["keywords"] = ", ".join(paper["keywords"])
                    
                    # Extract venue/journal
                    if paper.get("venue"):
                        metadata["journal"] = paper["venue"]
                    
                    # Extract year
                    if paper.get("year"):
                        metadata["year"] = str(paper["year"])
                    
                    # Extract authors
                    if paper.get("authors"):
                        authors = [f"{author.get('name', '')}" for author in paper["authors"]]
                        metadata["author"] = " and ".join(authors)
                    
                    if metadata:
                        # Cache the result
                        if cache_key not in self.cache:
                            self.cache[cache_key] = {}
                        self.cache[cache_key]['semantic_scholar'] = metadata
                        
                        print(f"    📚 Fetched metadata from Semantic Scholar")
                        return metadata
            
            # Cache empty result to avoid repeated failed requests
            if cache_key not in self.cache:
                self.cache[cache_key] = {}
            self.cache[cache_key]['semantic_scholar'] = None
            
            return None
            
        except Exception as e:
            print(f"    ⚠️  Error fetching from Semantic Scholar: {e}")
            # Cache empty result to avoid repeated failed requests
            if cache_key not in self.cache:
                self.cache[cache_key] = {}
            self.cache[cache_key]['semantic_scholar'] = None
            return None
    
    def fetch_metadata_from_crossref(self, title: str, author: str, verbose: bool = False) -> Optional[Dict[str, str]]:
        """Fetch metadata from Crossref API as fallback with caching."""
        # Check cache first
        cache_key = self.text_processor.generate_cache_key(title, author)
        if cache_key in self.cache:
            if verbose:
                print(f"    💾 Using cached metadata for Crossref")
            return self.cache[cache_key].get('crossref')
        
        try:
            if verbose:
                print(f"    🔍 Searching Crossref for: {title[:40]}...")
            
            # Crossref API endpoint
            url = self.config.CROSSREF_URL
            params = {
                "query": f"{title} {author}",
                "rows": 1,
                "select": "DOI,ISBN,abstract,subject,container-title,created,author"
            }
            
            response = requests.get(url, params=params, timeout=self.config.API_TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                if data.get("message", {}).get("items") and len(data["message"]["items"]) > 0:
                    item = data["message"]["items"][0]
                    
                    metadata = {}
                    
                    # Extract DOI
                    if item.get("DOI"):
                        metadata["doi"] = item["DOI"]
                    
                    # Extract ISBN
                    if item.get("ISBN"):
                        isbn_list = item["ISBN"]
                        if isinstance(isbn_list, list) and len(isbn_list) > 0:
                            metadata["isbn"] = isbn_list[0]
                        elif isinstance(isbn_list, str):
                            metadata["isbn"] = isbn_list
                    
                    # Extract abstract
                    if item.get("abstract"):
                        metadata["abstract"] = item["abstract"]
                    
                    # Extract subjects/keywords
                    if item.get("subject"):
                        metadata["keywords"] = ", ".join(item["subject"])
                    
                    # Extract journal/container title
                    if item.get("container-title"):
                        container_titles = item["container-title"]
                        if isinstance(container_titles, list) and len(container_titles) > 0:
                            metadata["journal"] = container_titles[0]
                        elif isinstance(container_titles, str):
                            metadata["journal"] = container_titles
                    
                    # Extract year
                    if item.get("created", {}).get("date-parts"):
                        date_parts = item["created"]["date-parts"][0]
                        if len(date_parts) > 0:
                            metadata["year"] = str(date_parts[0])
                    
                    # Extract authors
                    if item.get("author"):
                        authors = []
                        for author_info in item["author"]:
                            if author_info.get("given") and author_info.get("family"):
                                authors.append(f"{author_info['family']}, {author_info['given']}")
                            elif author_info.get("name"):
                                authors.append(author_info["name"])
                        if authors:
                            metadata["author"] = " and ".join(authors)
                    
                    if metadata:
                        # Cache the result
                        if cache_key not in self.cache:
                            self.cache[cache_key] = {}
                        self.cache[cache_key]['crossref'] = metadata
                        
                        print(f"    📚 Fetched metadata from Crossref")
                        return metadata
            
            # Cache empty result to avoid repeated failed requests
            if cache_key not in self.cache:
                self.cache[cache_key] = {}
            self.cache[cache_key]['crossref'] = None
            
            return None
            
        except Exception as e:
            print(f"    ⚠️  Error fetching from Crossref: {e}")
            # Cache empty result to avoid repeated failed requests
            if cache_key not in self.cache:
                self.cache[cache_key] = {}
            self.cache[cache_key]['crossref'] = None
            return None
    
    def enrich_bibtex_entry_with_metadata(self, fields: Dict[str, str], force_refetch: bool = False, verbose: bool = False) -> Dict[str, str]:
        """Enrich BibTeX entry with metadata from external sources."""
        enriched_fields = fields.copy()
        
        # Check if we should fetch metadata
        if self.should_fetch_metadata(enriched_fields, force_refetch, verbose):
            title = enriched_fields.get("title", "")
            author = enriched_fields.get("author", "")
            
            if title and author:
                # Try Semantic Scholar first
                metadata = self.fetch_metadata_from_semantic_scholar(title, author, verbose)
                
                # Fallback to Crossref if Semantic Scholar fails
                if not metadata:
                    metadata = self.fetch_metadata_from_crossref(title, author, verbose)
                
                # Merge fetched metadata with existing fields
                if metadata:
                    for key, value in metadata.items():
                        if key not in enriched_fields or not enriched_fields[key]:
                            enriched_fields[key] = value
                            if verbose:
                                print(f"    ➕ Added {key}: {str(value)[:50]}...")
        else:
            if verbose:
                print(f"    ⏭️  Skipping metadata fetch - already complete or not needed")
        
        return enriched_fields
    
    def clear_cache(self) -> None:
        """Clear the metadata cache."""
        self.cache = {}
        if os.path.exists(self.cache_file):
            try:
                os.remove(self.cache_file)
                print(f"🗑️  Cleared metadata cache: {self.cache_file}")
            except Exception as e:
                print(f"⚠️  Could not clear cache: {e}")
        else:
            print("ℹ️  No cache file found to clear")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get statistics about the cache."""
        total_entries = len(self.cache)
        semantic_scholar_entries = sum(1 for entry in self.cache.values() if entry.get('semantic_scholar'))
        crossref_entries = sum(1 for entry in self.cache.values() if entry.get('crossref'))
        
        return {
            'total_entries': total_entries,
            'semantic_scholar_entries': semantic_scholar_entries,
            'crossref_entries': crossref_entries
        }
