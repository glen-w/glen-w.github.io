# Location Mapping System

This system extracts locations from your `papers.bib` file, geocodes them using OpenStreetMap's Nominatim API, and displays them on an interactive map.

## Features

- **Automatic Location Extraction**: Parses BibTeX entries to find entries with address information
- **Smart Sorting**: Orders locations by date (most recent first)
- **Intelligent Caching**: Avoids redundant API calls by caching geocoded locations
- **Test Mode**: `--test` flag processes only the 5 most recent locations for quick testing
- **Geocoding**: Uses OpenStreetMap Nominatim API (free, no API key required)
- **Interactive Map**: Built with Leaflet.js showing locations
- **Rich Popups**: Display title, event type, date, location, and link to library page
- **Responsive Design**: Works on desktop and mobile devices
- **Statistics**: Shows total locations, mapped locations, and countries

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

Open `map.html` in a web browser. The map will automatically load the location data and display:
- Pins for each geocoded location
- Popups with location details
- Statistics about the data

### 3. Integration with Library Page

The popup links use anchor format `#BibTeXKey` (e.g., `#HowProtectOur2024`) that can be linked to your library page sections.

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

Modify the CSS in `map.html` to customize colors, fonts, and layout.

### Popup Content

Edit the `createPopupContent()` method in `map.html` to change what information is displayed in the popups.

## Future Enhancements

- Add clustering for many nearby conferences
- Include conference abstracts in popups
- Add filtering by year, type, or country
- Export map as image or PDF
- Integration with Jekyll site generation
