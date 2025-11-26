# Location Mapping System

This system extracts locations from your `papers.bib` file, geocodes them using OpenStreetMap's Nominatim API, and displays them on an interactive map.

## Features

- **Automatic Location Extraction**: Parses BibTeX entries to find entries with address information
- **Smart Sorting**: Orders locations by date (most recent first)
- **Intelligent Caching**: Avoids redundant API calls by caching geocoded locations
- **Test Mode**: `--test` flag processes only the 5 most recent locations for quick testing
- **Geocoding**: Uses OpenStreetMap Nominatim API (free, no API key required)
- **Interactive Map**: Built with Leaflet.js showing locations with marker clustering
- **Full-Page Display**: Standalone full-screen map (100vh/100vw) for immersive viewing
- **Pins-Only View**: Clean map display with location pins only (no popups)
- **Home Navigation**: Small home icon in top corner to return to home page
- **Responsive Design**: Works on desktop and mobile devices

## Files

- `processor.py` - Unified Python script to extract and geocode locations (integrated with main processing)
- `location_coordinates.json` - JSON file storing coordinates and metadata
- `map.html` - Interactive map visualization
- `README.md` - This documentation

## Usage

### 1. Integrated with Main Processing

The mapping system is now integrated into the main processing workflow. When you run:

```bash
cd processing
python3 main.py
```

It will automatically:
- Parse `papers.bib` for entries with address data
- Check cache first to avoid redundant API calls
- Geocode only new/uncached locations
- Save results to `location_coordinates.json` with caching metadata

### 2. Standalone Usage

You can also run the mapping processor standalone:

**Full Mode (all locations):**
```bash
cd processing/mapping
python3 processor.py
```

**Test Mode (5 most recent locations):**
```bash
python3 processor.py --test
```

**Cache-only Mode (only process uncached locations):**
```bash
python3 processor.py --cache-only
```

**Refresh Mode (force refresh all cached locations):**
```bash
python3 processor.py --refresh
```

**Custom options:**
```bash
python3 processor.py --test --bib-file /path/to/your/papers.bib --output-dir custom_output
```

## Caching

The system now includes intelligent caching that:
- Loads existing geocoded locations from `location_coordinates.json`
- Only makes API calls for new/uncached locations
- Merges new results with existing cache
- Provides detailed statistics on API calls vs cache hits
- Supports refresh mode to force re-geocoding all locations

### 2. View the Map

Open `assets/mapping/map.html` in a web browser or navigate to `/map.html` on your site. The map will automatically:
- Load location data from `location_coordinates.json`
- Display pins for each geocoded location with marker clustering
- Fit the map bounds to show all locations
- Provide a home icon in the top-left corner to return to the home page

The map is a standalone full-page HTML file that displays locations visited, sourced from your `papers.bib` file. It uses the same map implementation as the library page but in a full-screen format with pins only (no popups).

## Data Format

The `location_coordinates.json` file contains:

```json
{
  "metadata": {
    "generated_at": "2025-01-27 10:30:00",
    "total_locations": 3,
    "successfully_geocoded": 3,
    "source_file": "/path/to/papers.bib"
  },
  "locations": [
    {
      "bibtex_key": "HowProtectOur2024",
      "title": "How to protect our ocean",
      "address": "Paris, France",
      "year": "2024",
      "month": "mar",
      "entry_type": "roundtable",
      "coordinates": {
        "lat": 48.8566,
        "lng": 2.3522
      },
      "geocoded": true
    }
  ]
}
```

## Supported BibTeX Entry Types

The script looks for these entry types with `address` fields:
- `@conference`
- `@roundtable` 
- `@workshop`
- `@misc` (if it has address data)

## Requirements

- Python 3.6+
- `requests` library for API calls
- Modern web browser with JavaScript enabled

## Rate Limiting

The script includes 1-second delays between geocoding requests to be respectful to the Nominatim API. For large datasets, consider running during off-peak hours.

## Error Handling

- Failed geocoding attempts are logged and stored with `geocoded: false`
- The map will still display successfully geocoded locations
- Error messages are shown in the web interface

## Customization

### Adding New Entry Types

Edit the `parse_bibtex()` method in `geocode_conferences.py` to include additional BibTeX entry types:

```python
if entry_type.lower() in ['conference', 'roundtable', 'workshop', 'misc', 'your_new_type']:
```

### Styling the Map

Modify the CSS in `map.html` to customize colors, fonts, and layout. The map uses the same clustering styles as the library page for consistency.

## Roadmap

### Multiple Data Sources
The map is currently structured to support future multiple data sources beyond `papers.bib`. The `loadLocationData()` function can be extended to:
- Merge location data from multiple JSON files
- Support different data formats that will be normalized during loading
- Allow filtering by data source

### Future Enhancements
- **Filtering Capabilities**: Add filtering by year, event type, or country
- **Optional Popup Toggle**: Add ability to enable/disable popups for detailed information
- **Export Functionality**: Export map as image or PDF
- **Additional Data Sources**: Support for other location data sources (travel logs, personal visits, etc.)
- **Interactive Features**: Time-based filtering, heat maps, or route visualization
