#!/usr/bin/env python3
"""
KMZ Location Extractor

Extracts placemark locations from a KMZ file and generates a JSON file
compatible with the existing location_coordinates.json format.
"""

import json
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple


class KMZExtractor:
    """Extracts locations from KMZ files."""
    
    def __init__(self, kmz_file_path: str, output_file_path: str = "assets/mapping/kmz_locations.json"):
        """Initialize the KMZ extractor.
        
        Args:
            kmz_file_path: Path to the KMZ file
            output_file_path: Path to output JSON file
        """
        self.kmz_file_path = Path(kmz_file_path)
        self.output_file_path = Path(output_file_path)
        
        # Ensure output directory exists
        self.output_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # KML namespace
        self.ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    
    def extract_locations(self) -> bool:
        """Extract locations from KMZ file and generate JSON output."""
        print(f"🗺️  Extracting locations from {self.kmz_file_path}...")
        
        if not self.kmz_file_path.exists():
            print(f"Error: KMZ file not found at {self.kmz_file_path}")
            return False
        
        try:
            # Extract KML from KMZ
            with zipfile.ZipFile(self.kmz_file_path, 'r') as kmz:
                # Find the main KML file (usually doc.kml)
                kml_files = [f for f in kmz.namelist() if f.endswith('.kml')]
                if not kml_files:
                    print("Error: No KML file found in KMZ archive")
                    return False
                
                # Use the first KML file (usually doc.kml)
                kml_file = kml_files[0]
                kml_content = kmz.read(kml_file).decode('utf-8')
            
            # Parse KML
            root = ET.fromstring(kml_content)
            
            # Extract placemarks
            placemarks = root.findall('.//kml:Placemark', self.ns)
            print(f"Found {len(placemarks)} placemarks")
            
            locations = []
            for placemark in placemarks:
                location = self._extract_placemark(placemark)
                if location:
                    locations.append(location)
            
            print(f"Successfully extracted {len(locations)} locations with coordinates")
            
            # Generate output JSON
            output_data = {
                'metadata': {
                    'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'total_locations': len(locations),
                    'source_file': str(self.kmz_file_path)
                },
                'locations': locations
            }
            
            # Write to file
            with open(self.output_file_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Locations saved to: {self.output_file_path}")
            return True
            
        except zipfile.BadZipFile:
            print(f"Error: {self.kmz_file_path} is not a valid ZIP file")
            return False
        except ET.ParseError as e:
            print(f"Error parsing KML: {e}")
            return False
        except Exception as e:
            print(f"Error extracting locations: {e}")
            return False
    
    def _extract_placemark(self, placemark: ET.Element) -> Optional[Dict]:
        """Extract location data from a placemark element.
        
        Args:
            placemark: XML element representing a placemark
            
        Returns:
            Dictionary with location data or None if coordinates are missing
        """
        # Extract name
        name_elem = placemark.find('kml:name', self.ns)
        name = name_elem.text.strip() if name_elem is not None and name_elem.text else "Unnamed Location"
        
        # Extract coordinates from Point
        point = placemark.find('.//kml:Point', self.ns)
        if point is not None:
            coords_elem = point.find('kml:coordinates', self.ns)
            if coords_elem is not None and coords_elem.text:
                coords = self._parse_coordinates(coords_elem.text)
                if coords:
                    return {
                        'name': name,
                        'coordinates': {
                            'lat': coords[1],  # latitude
                            'lng': coords[0]   # longitude
                        },
                        'geocoded': True,
                        'source': 'kmz'
                    }
        
        # Try to extract from LineString or Polygon (use first coordinate)
        linestring = placemark.find('.//kml:LineString', self.ns)
        if linestring is not None:
            coords_elem = linestring.find('kml:coordinates', self.ns)
            if coords_elem is not None and coords_elem.text:
                coords = self._parse_coordinates(coords_elem.text.split()[0])  # First coordinate
                if coords:
                    return {
                        'name': name,
                        'coordinates': {
                            'lat': coords[1],
                            'lng': coords[0]
                        },
                        'geocoded': True,
                        'source': 'kmz'
                    }
        
        polygon = placemark.find('.//kml:Polygon', self.ns)
        if polygon is not None:
            outer_boundary = polygon.find('.//kml:outerBoundaryIs', self.ns)
            if outer_boundary is not None:
                linear_ring = outer_boundary.find('.//kml:LinearRing', self.ns)
                if linear_ring is not None:
                    coords_elem = linear_ring.find('kml:coordinates', self.ns)
                    if coords_elem is not None and coords_elem.text:
                        coords = self._parse_coordinates(coords_elem.text.split()[0])  # First coordinate
                        if coords:
                            return {
                                'name': name,
                                'coordinates': {
                                    'lat': coords[1],
                                    'lng': coords[0]
                                },
                                'geocoded': True,
                                'source': 'kmz'
                            }
        
        # No valid coordinates found
        return None
    
    def _parse_coordinates(self, coord_string: str) -> Optional[Tuple[float, float]]:
        """Parse coordinate string from KML format (lng,lat,altitude).
        
        Args:
            coord_string: Coordinate string in format "lng,lat,altitude" or "lng,lat"
            
        Returns:
            Tuple of (longitude, latitude) or None if parsing fails
        """
        try:
            parts = coord_string.strip().split(',')
            if len(parts) >= 2:
                lng = float(parts[0].strip())
                lat = float(parts[1].strip())
                return (lng, lat)
        except (ValueError, IndexError) as e:
            print(f"Warning: Could not parse coordinates '{coord_string}': {e}")
        return None


def main():
    """Main function for standalone execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract locations from KMZ file')
    parser.add_argument('--kmz-file', default='processing/My Places.kmz',
                       help='Path to the KMZ file')
    parser.add_argument('--output', default='assets/mapping/kmz_locations.json',
                       help='Output JSON file path')
    
    args = parser.parse_args()
    
    extractor = KMZExtractor(args.kmz_file, args.output)
    success = extractor.extract_locations()
    
    if success:
        print("✅ KMZ extraction completed successfully!")
        return 0
    else:
        print("❌ KMZ extraction failed!")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())

