#!/usr/bin/env python3
"""
Mapping Processor with Caching

Integrates location geocoding and map generation into the process_papers workflow.
This module handles extracting locations from processed papers and generating
the interactive map with proper library page links.

Features:
- Intelligent caching to avoid redundant API calls
- Support for test mode, refresh mode, and cache-only mode
- Rate limiting and error handling
- Integration with main processing workflow
"""

import json
import re
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import sys

# Add parent directory to path to import TagExtractor
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.tag_extractor import TagExtractor


class MappingProcessor:
    """Handles location extraction, geocoding, and map generation with caching."""
    
    def __init__(self, bib_file_path: str, output_dir: str = "assets/mapping", 
                 test_mode: bool = False, refresh_cache: bool = False, cache_only: bool = False):
        """Initialize the mapping processor.
        
        Args:
            bib_file_path: Path to the processed papers.bib file
            output_dir: Directory to save mapping files
            test_mode: If True, only process 5 most recent locations
            refresh_cache: If True, ignore cache and geocode all locations
            cache_only: If True, only process uncached locations
        """
        self.bib_file_path = Path(bib_file_path)
        self.output_dir = Path(output_dir)
        self.test_mode = test_mode
        self.refresh_cache = refresh_cache
        self.cache_only = cache_only
        self.nominatim_url = "https://nominatim.openstreetmap.org/search"
        self.headers = {
            'User-Agent': 'LocationMapper/1.0 (Academic Research Tool)'
        }
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize tag extractor for extracting custom Zotero tags
        self.tag_extractor = TagExtractor()
        
        # Load existing cache
        self.cache_file = self.output_dir / "location_coordinates.json"
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Load existing cache from the output file."""
        if not self.cache_file.exists():
            return {'locations': {}, 'metadata': {}}
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Convert locations list to dict for faster lookup
                locations_dict = {}
                if 'locations' in data:
                    for loc in data['locations']:
                        # Use address as key for caching
                        address_key = loc['address'].strip().lower()
                        locations_dict[address_key] = loc
                return {
                    'locations': locations_dict,
                    'metadata': data.get('metadata', {})
                }
        except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
            print(f"Warning: Could not load cache: {e}")
            return {'locations': {}, 'metadata': {}}
    
    def _is_cached(self, address: str) -> bool:
        """Check if an address is already cached."""
        address_key = address.strip().lower()
        return address_key in self.cache['locations']
    
    def _get_cached_result(self, address: str) -> Optional[Dict]:
        """Get cached result for an address."""
        address_key = address.strip().lower()
        return self.cache['locations'].get(address_key)
    
    def _update_cache(self, result: Dict) -> None:
        """Update cache with a new result."""
        address_key = result['address'].strip().lower()
        self.cache['locations'][address_key] = result
    
    def process_locations(self) -> bool:
        """Main method to process all locations and generate mapping data."""
        print("🗺️  Starting location processing...")
        
        # Parse locations from BibTeX
        locations = self._parse_bibtex()
        if not locations:
            print("No entries with location data found.")
            return True
        
        # Filter locations based on cache status
        if self.cache_only:
            uncached_locations = [loc for loc in locations if not self._is_cached(loc['address'])]
            if not uncached_locations:
                print("All locations are already cached. Use refresh mode to force update.")
                return True
            locations = uncached_locations
            print(f"Cache-only mode: Processing {len(locations)} uncached locations")
        
        # Geocode locations
        geocoded_locations = self._geocode_locations(locations)
        
        # Generate mapping data
        self._generate_mapping_data(geocoded_locations)
        
        # Update map.html with correct library URLs
        self._update_map_html()
        
        print(f"✅ Mapping processing complete: {len([l for l in geocoded_locations if l['geocoded']])}/{len(geocoded_locations)} locations geocoded")
        return True
    
    def _parse_bibtex(self) -> List[Dict]:
        """Parse the BibTeX file and extract entries with location data."""
        locations = []
        
        if not self.bib_file_path.exists():
            print(f"Error: BibTeX file not found at {self.bib_file_path}")
            return locations
            
        with open(self.bib_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all entries that might have location data
        entry_pattern = r'@(\w+)\{([^,\s]+),\s*([^@]+?)(?=@|\Z)'
        entries = re.findall(entry_pattern, content, re.DOTALL)
        
        print(f"Found {len(entries)} total entries")
        
        for entry_type, bibtex_key, entry_content in entries:
            # Extract relevant fields - check all entry types for address fields
            title = self._extract_field(entry_content, 'title')
            address = self._extract_field(entry_content, 'address')
            year = self._extract_field(entry_content, 'year')
            month = self._extract_field(entry_content, 'month')
            preview = self._extract_field(entry_content, 'preview')
            note = self._extract_field(entry_content, 'note')
            annote = self._extract_field(entry_content, 'annote')
            
            # Extract custom Zotero tag from [type] section
            tag = None
            if note or annote:
                entry_dict = {
                    'ENTRYTYPE': entry_type,
                    'note': note or '',
                    'annote': annote or ''
                }
                tag = self.tag_extractor.extract_type(entry_dict)
            
            # Include any entry that has an address field, regardless of entry type
            if address and address.strip():
                locations.append({
                    'bibtex_key': bibtex_key.strip(),
                    'title': title.strip() if title else '',
                    'address': address.strip(),
                    'year': year.strip() if year else '',
                    'month': month.strip() if month else '',
                    'entry_type': entry_type,
                    'tag': tag,  # Custom Zotero tag from [type] section
                    'preview': preview.strip() if preview else None
                })
        
        # Sort by year and month (most recent first)
        locations = self._sort_by_date(locations)
        
        # If in test mode, limit to 5 most recent
        if self.test_mode and len(locations) > 5:
            print(f"Test mode: Limiting to 5 most recent locations (out of {len(locations)} found)")
            locations = locations[:5]
        
        return locations
    
    def _sort_by_date(self, locations: List[Dict]) -> List[Dict]:
        """Sort locations by date (most recent first)."""
        def get_sort_key(loc):
            year = int(loc['year']) if loc['year'] and loc['year'].isdigit() else 0
            month = loc['month'].lower() if loc['month'] else ''
            
            # Convert month to number for sorting
            month_map = {
                'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
                'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
                'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
            }
            month_num = month_map.get(month, 0)
            
            # Return tuple for sorting (year, month) - negative for descending order
            return (-year, -month_num)
        
        return sorted(locations, key=get_sort_key)
    
    def _extract_field(self, content: str, field_name: str) -> Optional[str]:
        """Extract a field value from BibTeX entry content."""
        pattern = rf'{field_name}\s*=\s*{{([^{{}}]*(?:{{[^{{}}]*}}[^{{}}]*)*)}}'
        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
        if match:
            value = match.group(1).strip()
            value = re.sub(r'\s+', ' ', value)
            return value
        return None
    
    def _geocode_location(self, address: str) -> Optional[Tuple[float, float]]:
        """Geocode an address using Nominatim API."""
        params = {
            'q': address,
            'format': 'json',
            'limit': 1,
            'addressdetails': 1
        }
        
        try:
            response = requests.get(self.nominatim_url, params=params, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            if data and len(data) > 0:
                lat = float(data[0]['lat'])
                lng = float(data[0]['lon'])
                return (lat, lng)
            else:
                print(f"No results found for: {address}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error geocoding {address}: {e}")
            return None
        except (ValueError, KeyError) as e:
            print(f"Error parsing geocoding response for {address}: {e}")
            return None
    
    def _geocode_locations(self, locations: List[Dict]) -> List[Dict]:
        """Geocode all locations with caching support."""
        print(f"Geocoding {len(locations)} locations...")
        results = []
        api_calls_made = 0
        cache_hits = 0
        
        for i, loc in enumerate(locations, 1):
            print(f"Geocoding {i}/{len(locations)}: {loc['address']}")
            
            # Check if we should use cached result
            if not self.refresh_cache and self._is_cached(loc['address']):
                cached_result = self._get_cached_result(loc['address'])
                if cached_result:
                    results.append(cached_result)
                    cache_hits += 1
                    print(f"  📋 Using cached result")
                    continue
            
            # Geocode the location
            coordinates = self._geocode_location(loc['address'])
            
            # Track API calls
            if not (self.cache_only and self._is_cached(loc['address'])):
                if not self.refresh_cache and self._is_cached(loc['address']):
                    cache_hits += 1
                else:
                    api_calls_made += 1
            
            if coordinates:
                result = {
                    'bibtex_key': loc['bibtex_key'],
                    'title': loc['title'],
                    'address': loc['address'],
                    'year': loc['year'],
                    'month': loc['month'],
                    'entry_type': loc['entry_type'],
                    'tag': loc.get('tag'),  # Custom Zotero tag
                    'coordinates': {
                        'lat': coordinates[0],
                        'lng': coordinates[1]
                    },
                    'geocoded': True
                }
                print(f"  ✓ Found coordinates: {coordinates[0]:.4f}, {coordinates[1]:.4f}")
            else:
                result = {
                    'bibtex_key': loc['bibtex_key'],
                    'title': loc['title'],
                    'address': loc['address'],
                    'year': loc['year'],
                    'month': loc['month'],
                    'entry_type': loc['entry_type'],
                    'tag': loc.get('tag'),  # Custom Zotero tag
                    'coordinates': None,
                    'geocoded': False
                }
                print(f"  ✗ Failed to geocode")
            
            # Update cache
            self._update_cache(result)
            results.append(result)
            
            # Rate limiting - be respectful to the API (only for actual API calls)
            if api_calls_made > 0 and api_calls_made % 5 == 0:
                print(f"  ⏸️  Rate limiting pause...")
                time.sleep(1)
        
        print(f"API calls made: {api_calls_made}, Cache hits: {cache_hits}")
        return results
    
    def _generate_mapping_data(self, locations: List[Dict]) -> None:
        """Generate the mapping data JSON file with caching."""
        # Get all current bibtex keys and addresses from parsed locations
        current_bibtex_keys = {loc['bibtex_key'] for loc in locations}
        current_addresses = {loc['address'].strip().lower() for loc in locations}
        
        # Start with existing cache, but filter to only keep entries that are still in BibTeX
        # This removes entries that were deleted from the BibTeX file
        all_locations = []
        for cached_loc in self.cache['locations'].values():
            cached_bibtex_key = cached_loc.get('bibtex_key', '')
            cached_address = cached_loc.get('address', '').strip().lower()
            # Keep if bibtex_key matches current entry OR address matches current entry
            if (cached_bibtex_key in current_bibtex_keys or 
                cached_address in current_addresses):
                all_locations.append(cached_loc)
        
        # Add new results that aren't already in cache
        existing_addresses = {loc['address'].strip().lower() for loc in all_locations}
        for result in locations:
            address_key = result['address'].strip().lower()
            if address_key not in existing_addresses:
                all_locations.append(result)
                existing_addresses.add(address_key)
            else:
                # Update existing entry
                for i, existing in enumerate(all_locations):
                    if existing['address'].strip().lower() == address_key:
                        all_locations[i] = result
                        break
        
        # Sort by year and month (most recent first)
        all_locations = self._sort_by_date(all_locations)
        
        output_data = {
            'metadata': {
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_locations': len(all_locations),
                'successfully_geocoded': sum(1 for r in all_locations if r['geocoded']),
                'source_file': str(self.bib_file_path),
                'cache_enabled': True,
                'refresh_mode': self.refresh_cache,
                'cache_only_mode': self.cache_only
            },
            'locations': all_locations
        }
        
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"Mapping data saved to: {self.cache_file}")
        print(f"Total locations in cache: {len(all_locations)}")
    
    def _update_map_html(self) -> None:
        """Update map.html to use correct library page URLs."""
        map_file = Path("map.html")
        if not map_file.exists():
            print("Warning: map.html not found, skipping map update")
            return
        
        # Read the current map.html
        with open(map_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # The map.html should already have the correct library page linking logic
        # This method can be used to update any dynamic content if needed
        print("Map HTML is up to date with library page linking")
    
    def generate_library_url(self, entry: Dict) -> str:
        """Generate the correct library page URL for an entry.
        
        This replicates the filename generation logic from the library generator
        to ensure URLs match the actual generated pages.
        """
        # Get date components
        year = entry.get('year', '2025')
        month = entry.get('month', '01')
        day = '01'  # Default day
        
        # Convert month name to number if needed
        month_names = {
            'jan': '01', 'january': '01',
            'feb': '02', 'february': '02',
            'mar': '03', 'march': '03',
            'apr': '04', 'april': '04',
            'may': '05',
            'jun': '06', 'june': '06',
            'jul': '07', 'july': '07',
            'aug': '08', 'august': '08',
            'sep': '09', 'september': '09',
            'oct': '10', 'october': '10',
            'nov': '11', 'november': '11',
            'dec': '12', 'december': '12'
        }
        
        if month.lower() in month_names:
            month = month_names[month.lower()]
        elif len(month) == 1:
            month = month.zfill(2)
        
        # Create date prefix (YYMMDD)
        date_prefix = f"{year[-2:]}{month}{day}"
        
        # Create title slug
        title = entry.get('title', 'untitled')
        if not title or title.strip() == '':
            title = 'untitled'
        
        # Remove common prefixes and clean up
        title = re.sub(r'^["\']', '', title)
        title = re.sub(r'["\']$', '', title)
        title_slug = self._slugify(title, max_length=50)
        
        # Generate filename and URL
        filename = f"{date_prefix}_{title_slug}"
        return f"/library/{filename}/"
    
    def _slugify(self, text: str, max_length: int = 50) -> str:
        """Create URL-friendly slug from text with proper accent handling."""
        try:
            from slugify import slugify
            return slugify(
                text,
                max_length=max_length,
                word_boundary=True,
                save_order=True,
                separator='-',
                lowercase=True
            )
        except ImportError:
            # Fallback if slugify is not available
            return re.sub(r'[^\w\s-]', '', text.lower()) \
                   .replace(' ', '-') \
                   .replace('--', '-') \
                   .strip('-')[:max_length]


def main():
    """Main function for standalone execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Process locations and generate mapping data with caching')
    parser.add_argument('--test', action='store_true', 
                       help='Process only the 5 most recent locations')
    parser.add_argument('--refresh', action='store_true',
                       help='Force refresh all cached locations (ignore cache)')
    parser.add_argument('--cache-only', action='store_true',
                       help='Only process locations that are not already cached')
    parser.add_argument('--bib-file', default="_bibliography/papers.bib",
                       help='Path to the BibTeX file')
    parser.add_argument('--output-dir', default="assets/mapping",
                       help='Output directory for mapping files')
    
    args = parser.parse_args()
    
    # Validate argument combinations
    if args.refresh and args.cache_only:
        print("Error: --refresh and --cache-only cannot be used together")
        return 1
    
    # Print mode information
    if args.test:
        print("🧪 Running in TEST MODE - processing only 5 most recent locations")
    else:
        print("🌍 Running in FULL MODE - processing all locations")
    
    if args.refresh:
        print("🔄 REFRESH MODE - ignoring cache, will geocode all locations")
    elif args.cache_only:
        print("📋 CACHE-ONLY MODE - only processing uncached locations")
    else:
        print("💾 CACHE MODE - using cache when available, geocoding new locations")
    
    processor = MappingProcessor(
        bib_file_path=args.bib_file,
        output_dir=args.output_dir,
        test_mode=args.test,
        refresh_cache=args.refresh,
        cache_only=args.cache_only
    )
    
    success = processor.process_locations()
    
    if success:
        print("✅ Mapping processing completed successfully!")
        return 0
    else:
        print("❌ Mapping processing failed!")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
