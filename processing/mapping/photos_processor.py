#!/usr/bin/env python3
"""
Photo Locations Processor

Extracts location data from:
1. Photo folder names (e.g., "2024_05_UAE Abu Dhabi IRENA" -> "Abu Dhabi, United Arab Emirates")
2. GPS metadata in photos (clustered and deduplicated)

Outputs JSON compatible with map.html for display on the location map.
"""

import json
import re
import time
import requests
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

# Try to import PIL for GPS extraction
try:
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL/Pillow not available. GPS extraction will be skipped.")


# Country/region code mappings
COUNTRY_CODES = {
    # Standard codes
    'UK': 'United Kingdom',
    'US': 'United States',
    'USA': 'United States',
    'FR': 'France',
    'DE': 'Germany',
    'ES': 'Spain',
    'IT': 'Italy',
    'PT': 'Portugal',
    'NL': 'Netherlands',
    'SE': 'Sweden',
    'BE': 'Belgium',
    'PL': 'Poland',
    'AT': 'Austria',
    'CH': 'Switzerland',
    'IE': 'Ireland',
    'DK': 'Denmark',
    'NO': 'Norway',
    'FI': 'Finland',
    'GR': 'Greece',
    'CZ': 'Czech Republic',
    'HU': 'Hungary',
    'RO': 'Romania',
    'CN': 'China',
    'JP': 'Japan',
    'KR': 'South Korea',
    'TW': 'Taiwan',
    'SG': 'Singapore',
    'MY': 'Malaysia',
    'TH': 'Thailand',
    'VN': 'Vietnam',
    'ID': 'Indonesia',
    'PH': 'Philippines',
    'IN': 'India',
    'AE': 'United Arab Emirates',
    'UAE': 'United Arab Emirates',
    'SA': 'Saudi Arabia',
    'IL': 'Israel',
    'TR': 'Turkey',
    'EG': 'Egypt',
    'ZA': 'South Africa',
    'AU': 'Australia',
    'NZ': 'New Zealand',
    'CA': 'Canada',
    'MX': 'Mexico',
    'BR': 'Brazil',
    'AR': 'Argentina',
    'CL': 'Chile',
    'CO': 'Colombia',
    'PE': 'Peru',
    'LUX': 'Luxembourg',
    'JAM': 'Jamaica',
    'ITA': 'Italy',
    
    # Common abbreviations from folder names
    'Aus': 'Australia',
    'Ger': 'Germany',
    'Esp': 'Spain',
    'Ned': 'Netherlands',
    'SWE': 'Sweden',
    'NYC': 'United States',  # New York City
    'TX': 'United States',   # Texas
    'PA': 'United States',   # Pennsylvania
    'CA': 'United States',   # California (when context is US)
    'DC': 'United States',   # Washington DC
    'LA': 'United States',   # Louisiana
}

# US State codes (for better geocoding)
US_STATES = {
    'TX': 'Texas',
    'PA': 'Pennsylvania', 
    'CA': 'California',
    'NY': 'New York',
    'DC': 'Washington DC',
    'LA': 'Louisiana',
}

# Skip these folder names entirely (not real locations)
SKIP_FOLDERS = {
    '*inbox', '*misc', 'Whiteboards', 'misc', 'inbox',
    'Home', 'Uni', 'College', 'PhD', 'Xmas', 'Birthday',
}

# Skip these terms when parsing location (event names, not places)
SKIP_TERMS = {
    'IRENA', 'AOSIS', 'COP21', 'COP', 'IGC5', 'IGC', 'REN21', 'IDDRI',
    'workshop', 'retreat', 'wedding', 'birthday', 'visit', 'trip',
    'protest', 'rally', 'festival', 'camping', 'apartment',
    'Freshers Week', 'Bar Crawl', 'Fossil Fools', 'Climate Camp',
    'Download', 'Glastonbury', 'Best Kept Secret', 'Cropredy',
    'Mardi Gras', 'ACL',
}


class PhotosProcessor:
    """Processes photo folders and GPS metadata to extract locations."""
    
    def __init__(self, photos_dir: str, output_file: str = "assets/mapping/photos_locations.json",
                 skip_gps: bool = False, test_mode: bool = False):
        self.photos_dir = Path(photos_dir)
        self.output_file = Path(output_file)
        self.skip_gps = skip_gps
        self.test_mode = test_mode
        
        self.nominatim_url = "https://nominatim.openstreetmap.org/search"
        self.headers = {
            'User-Agent': 'PhotoLocationMapper/1.0 (Personal Photo Archive)'
        }
        
        # Ensure output directory exists
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        
    def process(self) -> bool:
        """Main processing method."""
        print("📸 Starting photo location processing...")
        
        # Step 1: Extract locations from folder names
        folder_locations = self._parse_folder_names()
        print(f"  Found {len(folder_locations)} unique locations from folder names")
        
        # Step 2: Extract GPS data from photos (optional)
        gps_locations = []
        if not self.skip_gps and PIL_AVAILABLE:
            gps_locations = self._extract_gps_locations()
            print(f"  Found {len(gps_locations)} locations with GPS data")
        
        # Step 3: Merge and deduplicate
        all_locations = self._merge_locations(folder_locations, gps_locations)
        print(f"  Total unique locations: {len(all_locations)}")
        
        # Step 4: Geocode locations without coordinates
        geocoded_locations = self._geocode_locations(all_locations)
        
        # Step 5: Output JSON
        self._write_output(geocoded_locations)
        
        success_count = sum(1 for loc in geocoded_locations if loc.get('geocoded'))
        print(f"✅ Complete: {success_count}/{len(geocoded_locations)} locations geocoded")
        return True
    
    def _parse_folder_names(self) -> List[Dict]:
        """Parse folder names to extract location information."""
        locations = []
        seen_locations = set()
        
        if not self.photos_dir.exists():
            print(f"Warning: Photos directory not found: {self.photos_dir}")
            return locations
        
        folders = sorted([f for f in self.photos_dir.iterdir() 
                         if f.is_dir() and not f.name.startswith('.')])
        
        for folder in folders:
            # Skip certain folders
            if folder.name in SKIP_FOLDERS or folder.name.startswith('*'):
                continue
            
            parsed = self._parse_folder_name(folder.name)
            if parsed and parsed['location']:
                # Create a unique key for deduplication
                location_key = parsed['location'].lower()
                if location_key not in seen_locations:
                    seen_locations.add(location_key)
                    locations.append({
                        'name': parsed['location'],
                        'country': parsed.get('country'),
                        'year': parsed.get('year'),
                        'source_folder': folder.name,
                        'coordinates': None,
                        'geocoded': False,
                    })
        
        return locations
    
    def _parse_folder_name(self, folder_name: str) -> Optional[Dict]:
        """Parse a single folder name to extract location and metadata.
        
        Examples:
            "2024_05_UAE Abu Dhabi IRENA" -> {"location": "Abu Dhabi", "country": "United Arab Emirates", "year": "2024"}
            "2013_01_Aus Kioloa" -> {"location": "Kioloa", "country": "Australia", "year": "2013"}
            "2017_09 Myanmar" -> {"location": "Myanmar", "country": None, "year": "2017"}
        """
        result = {'location': None, 'country': None, 'year': None}
        
        # Extract year
        year_match = re.match(r'^(\d{4})[-_]', folder_name)
        if year_match:
            result['year'] = year_match.group(1)
        
        # Remove date prefix (YYYY_MM_ or YYYY_)
        cleaned = re.sub(r'^\d{4}[-_]\d{0,2}[-_]?', '', folder_name)
        cleaned = re.sub(r'^\d{4}[-_]', '', cleaned)
        
        if not cleaned:
            return None
        
        # Check for country code at the start
        country_code = None
        location_part = cleaned
        
        # Try to match country code pattern at start
        code_match = re.match(r'^([A-Z]{2,3}|Aus|Ger|Esp|Ned)[-_\s](.+)$', cleaned, re.IGNORECASE)
        if code_match:
            potential_code = code_match.group(1)
            if potential_code.upper() in COUNTRY_CODES or potential_code in COUNTRY_CODES:
                country_code = potential_code
                location_part = code_match.group(2).strip()
                result['country'] = COUNTRY_CODES.get(potential_code.upper()) or COUNTRY_CODES.get(potential_code)
        
        # Handle special US state codes (TX, NYC, etc.)
        if country_code and country_code.upper() in US_STATES:
            # For US states, the location might be "Austin" from "TX_Austin"
            state = US_STATES[country_code.upper()]
            if location_part:
                # Extract city name, removing underscores
                city = location_part.replace('_', ' ').strip()
                # Remove event names
                for skip in SKIP_TERMS:
                    city = re.sub(rf'\b{re.escape(skip)}\b', '', city, flags=re.IGNORECASE).strip()
                city = re.sub(r'\s+', ' ', city).strip()
                city = re.sub(r'[,\s]+$', '', city).strip()
                
                if city:
                    result['location'] = f"{city}, {state}"
                    result['country'] = 'United States'
                else:
                    result['location'] = state
                    result['country'] = 'United States'
            return result
        
        # Clean up location part
        location = location_part.replace('_', ' ').strip()
        
        # Remove event names and descriptors
        for skip in SKIP_TERMS:
            location = re.sub(rf'\b{re.escape(skip)}\b', '', location, flags=re.IGNORECASE)
        
        # Clean up extra whitespace and trailing punctuation
        location = re.sub(r'\s+', ' ', location).strip()
        location = re.sub(r'[,\s]+$', '', location).strip()
        location = re.sub(r'^[,\s]+', '', location).strip()
        
        # Skip if location is now empty or too generic
        if not location or location.lower() in ('home', 'mom', 'dad', 'xmas', 'birthday'):
            return None
        
        result['location'] = location
        
        # If no country detected but location looks like a country, set it
        if not result['country'] and location in COUNTRY_CODES.values():
            result['country'] = location
            
        return result
    
    def _extract_gps_locations(self) -> List[Dict]:
        """Extract GPS coordinates from photos and cluster them."""
        if not PIL_AVAILABLE:
            return []
        
        print("  Scanning photos for GPS metadata...")
        
        # Collect all GPS points by folder
        folder_gps = defaultdict(list)
        
        # Get all image files
        extensions = ('*.jpg', '*.jpeg', '*.JPG', '*.JPEG')
        all_images = []
        for ext in extensions:
            all_images.extend(self.photos_dir.glob(f'**/{ext}'))
        
        # Limit for test mode
        if self.test_mode:
            all_images = all_images[:500]
        
        checked = 0
        for img_path in all_images:
            checked += 1
            if checked % 1000 == 0:
                print(f"    Checked {checked} photos...")
            
            coords = self._get_gps_coords(img_path)
            if coords:
                # Get the immediate parent folder name
                folder_name = img_path.parent.name
                folder_gps[folder_name].append({
                    'coords': coords,
                    'path': str(img_path),
                })
        
        print(f"    Found GPS data in {sum(len(v) for v in folder_gps.values())} photos across {len(folder_gps)} folders")
        
        # Cluster and select representative coordinates per folder
        locations = []
        for folder_name, gps_points in folder_gps.items():
            if not gps_points:
                continue
            
            # Use the first GPS point as representative (could cluster more sophisticatedly)
            representative = gps_points[0]['coords']
            
            # Parse folder name to get location name
            parsed = self._parse_folder_name(folder_name)
            name = parsed['location'] if parsed and parsed['location'] else folder_name
            
            locations.append({
                'name': name,
                'country': parsed.get('country') if parsed else None,
                'coordinates': {'lat': representative[0], 'lng': representative[1]},
                'geocoded': True,  # We have GPS coords
                'source_folder': folder_name,
                'gps_source': True,
            })
        
        return locations
    
    def _get_gps_coords(self, image_path: Path) -> Optional[Tuple[float, float]]:
        """Extract GPS coordinates from an image's EXIF data."""
        try:
            img = Image.open(image_path)
            exif = img._getexif()
            if not exif:
                return None
            
            for tag_id, value in exif.items():
                if TAGS.get(tag_id) == 'GPSInfo':
                    gps = {}
                    for gps_tag_id, gps_value in value.items():
                        gps[GPSTAGS.get(gps_tag_id, gps_tag_id)] = gps_value
                    
                    lat = gps.get('GPSLatitude')
                    lat_ref = gps.get('GPSLatitudeRef')
                    lng = gps.get('GPSLongitude')
                    lng_ref = gps.get('GPSLongitudeRef')
                    
                    if lat and lng:
                        lat_deg = float(lat[0]) + float(lat[1])/60 + float(lat[2])/3600
                        lng_deg = float(lng[0]) + float(lng[1])/60 + float(lng[2])/3600
                        if lat_ref == 'S': lat_deg = -lat_deg
                        if lng_ref == 'W': lng_deg = -lng_deg
                        
                        # Skip invalid 0,0 coordinates
                        if lat_deg != 0 or lng_deg != 0:
                            return (lat_deg, lng_deg)
            return None
        except Exception:
            return None
    
    def _merge_locations(self, folder_locs: List[Dict], gps_locs: List[Dict]) -> List[Dict]:
        """Merge folder-based and GPS-based locations, preferring GPS coords."""
        merged = {}
        
        # First, add all folder locations
        for loc in folder_locs:
            key = loc['name'].lower()
            merged[key] = loc.copy()
        
        # Then, update with GPS locations (they have coordinates)
        for loc in gps_locs:
            key = loc['name'].lower()
            if key in merged:
                # Update existing entry with GPS coordinates
                merged[key]['coordinates'] = loc['coordinates']
                merged[key]['geocoded'] = True
                merged[key]['gps_source'] = True
            else:
                merged[key] = loc.copy()
        
        return list(merged.values())
    
    def _geocode_locations(self, locations: List[Dict]) -> List[Dict]:
        """Geocode locations that don't have coordinates."""
        to_geocode = [loc for loc in locations if not loc.get('geocoded')]
        
        if not to_geocode:
            print("  All locations already have coordinates")
            return locations
        
        print(f"  Geocoding {len(to_geocode)} locations...")
        
        for i, loc in enumerate(to_geocode, 1):
            # Build geocoding query
            query = loc['name']
            if loc.get('country'):
                query = f"{loc['name']}, {loc['country']}"
            
            print(f"    [{i}/{len(to_geocode)}] {query}")
            
            coords = self._geocode_address(query)
            if coords:
                loc['coordinates'] = {'lat': coords[0], 'lng': coords[1]}
                loc['geocoded'] = True
                print(f"      ✓ {coords[0]:.4f}, {coords[1]:.4f}")
            else:
                print(f"      ✗ Failed")
            
            # Rate limiting
            if i % 5 == 0:
                time.sleep(1)
        
        return locations
    
    def _geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """Geocode an address using Nominatim API."""
        params = {
            'q': address,
            'format': 'json',
            'limit': 1,
        }
        
        try:
            response = requests.get(self.nominatim_url, params=params, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            if data and len(data) > 0:
                lat = float(data[0]['lat'])
                lng = float(data[0]['lon'])
                return (lat, lng)
            return None
        except Exception as e:
            print(f"      Error: {e}")
            return None
    
    def _write_output(self, locations: List[Dict]) -> None:
        """Write locations to output JSON file."""
        # Filter to only geocoded locations and clean up
        output_locations = []
        for loc in locations:
            if loc.get('geocoded') and loc.get('coordinates'):
                output_locations.append({
                    'name': loc['name'],
                    'coordinates': loc['coordinates'],
                    'geocoded': True,
                    'source': 'photos',
                })
        
        output_data = {
            'metadata': {
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_locations': len(output_locations),
                'source': 'photos',
            },
            'locations': output_locations
        }
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"  Output saved to: {self.output_file}")


def main():
    parser = argparse.ArgumentParser(description='Extract locations from photo folders and GPS metadata')
    parser.add_argument('--photos-dir', required=True, help='Path to photos directory')
    parser.add_argument('--output', default='assets/mapping/photos_locations.json',
                       help='Output JSON file path')
    parser.add_argument('--skip-gps', action='store_true',
                       help='Skip GPS metadata extraction (faster)')
    parser.add_argument('--test', action='store_true',
                       help='Test mode - limit GPS scanning')
    
    args = parser.parse_args()
    
    processor = PhotosProcessor(
        photos_dir=args.photos_dir,
        output_file=args.output,
        skip_gps=args.skip_gps,
        test_mode=args.test,
    )
    
    success = processor.process()
    return 0 if success else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())

