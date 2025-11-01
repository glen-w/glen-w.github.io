# Library Page Generator

Automatically generates individual markdown pages for each bibliography item with rich features including share buttons, social posting, PDF embedding, and image galleries.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Test the Setup
```bash
python test_generator.py
```

### 3. Generate Pages (Test Mode)
```bash
python generate_library_pages.py --test
```

### 4. Generate All Pages
```bash
python generate_library_pages.py
```

## Usage

### Basic Usage
```bash
# Test mode (5 latest items with location)
python generate_library_pages.py --test

# Full generation
python generate_library_pages.py

# Custom BibTeX file
python generate_library_pages.py --bib-file _bibliography/Exported\ Items.bib

# Custom output directory
python generate_library_pages.py --output-dir _custom_library
```

### Command Line Options
- `--test`: Test mode - only process 5 most recent entries
- `--bib-file PATH`: Path to BibTeX file (default: _bibliography/papers.bib)
- `--output-dir PATH`: Output directory for generated pages (default: _library)

## Features

### Current Features (Phase 1)
- ✅ BibTeX parsing and processing
- ✅ Automatic filename generation with date prefix
- ✅ YAML front matter generation
- ✅ Basic markdown content generation
- ✅ Test mode for development
- ✅ Jekyll layout template

### Planned Features
- 🔄 Share panel with social media buttons
- 🔄 Social media post generation
- 🔄 PDF embedding with PDF.js
- 🔄 Image gallery with lightbox
- 🔄 Search and filtering
- 🔄 Related content suggestions

## File Structure

```
processing/library/
├── generate_library_pages.py    # Main generation script
├── bib_parser.py                # BibTeX parsing utilities
├── content_generator.py         # Markdown content generation
├── test_generator.py            # Test script
├── requirements.txt             # Python dependencies
├── README.md                    # This file
└── IMPLEMENTATION_PLAN.md       # Detailed implementation plan

_library/                        # Generated markdown pages
├── 250120_ship_has_reached_shore.md
├── 250120_30x30_target_implementation.md
└── ...

_layouts/
└── library-item.liquid          # Jekyll layout for library pages
```

## Generated Page Structure

Each generated page includes:

### Front Matter
```yaml
---
layout: library-item
title: "The ship has reached the shore"
date: 2023-03-04
description: "Why the historic Agreement to protect the High Seas matters"
tags: [ocean, governance, BBNJ]
categories: [publications]
entry_type: blog
authors: [Wright, Glen, Langlet, Arne, Tessnow-Von Wysocki, Ina]
venue: IDDRI
year: 2023
abstract: "On Saturday March 4, 2023..."
url: https://www.iddri.org/en/publications-and-events/blog-post/...
pdf: glen_wright_2023_The_ship_has_reached_the_shore.pdf
preview: glen_wright_2023_The_ship_has_reached_the_shore.jpeg
---
```

### Content Sections
- Abstract
- Publication Details
- Links and Resources
- Keywords
- Notes (if available)

## Jekyll Integration

### 1. Add Library Collection
Add to `_config.yml`:
```yaml
collections:
  library:
    output: true
    permalink: /library/:name/
```

### 2. Navigation
Add library section to your navigation menu.

### 3. Styling
The layout includes basic styling. Customize in `assets/css/library/`.

## Development

### Running Tests
```bash
python test_generator.py
```

### Adding New Features
1. Update the appropriate module (bib_parser.py, content_generator.py, etc.)
2. Test with `python test_generator.py`
3. Test with `python generate_library_pages.py --test`
4. Update documentation

### Debugging
- Use `--test` flag to limit processing to 5 items
- Check generated files in `_library/` directory
- Verify Jekyll build with `bundle exec jekyll serve`

## Troubleshooting

### Common Issues

1. **Missing dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **BibTeX file not found**
   - Check file path in `--bib-file` argument
   - Ensure file exists and is readable

3. **No entries found**
   - Test mode processes the 5 most recent entries by year
   - Use without `--test` flag to process all entries

4. **Jekyll build errors**
   - Check generated markdown files for syntax errors
   - Verify front matter YAML format
   - Check Jekyll logs for specific errors

### Getting Help
- Check the implementation plan in `IMPLEMENTATION_PLAN.md`
- Review generated files in `_library/` directory
- Test with a small subset using `--test` flag

## License

This project is part of the glen-w.github.io website and follows the same license terms.
