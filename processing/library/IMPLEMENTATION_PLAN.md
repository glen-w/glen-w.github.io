# Library Page Generator - Implementation Plan

## Overview
This system automatically generates individual markdown pages for each bibliography item with rich features including share buttons, social posting, PDF embedding, and image galleries.

## Folder Structure
```
_library/                          # Generated markdown pages
processing/library/                # Python generation scripts
├── generate_library_pages.py     # Main generation script
├── bib_parser.py                 # BibTeX parsing utilities
├── content_generator.py          # Markdown content generation
├── social_posts.py               # Social media post generation
└── IMPLEMENTATION_PLAN.md        # This file

_layouts/
└── library-item.liquid           # Jekyll layout for library pages

assets/
├── js/library/                   # JavaScript for library features
│   ├── sharing.js                # Share panel functionality
│   ├── pdf-viewer.js             # PDF embedding
│   ├── gallery.js                # Image gallery
│   └── social-posting.js         # Social media posting
└── css/library/                  # Styles for library pages
    ├── library-pages.scss        # Main styles
    ├── sharing.scss              # Share panel styles
    ├── pdf-viewer.scss           # PDF viewer styles
    └── gallery.scss               # Gallery styles
```

## Implementation Phases

### Phase 1: Basic Scaffolding (Current)
**Goal**: Create working generator with test mode and basic page layout

#### Tasks:
1. ✅ Create folder structure
2. ✅ Set up basic Python script with --test flag
3. ✅ Create Jekyll layout stub
4. ✅ Implement basic BibTeX parsing
5. ✅ Generate simple markdown pages
6. ✅ Test with 5 latest items with location

#### Files to Create:
- `generate_library_pages.py` - Main script with --test flag
- `bib_parser.py` - BibTeX parsing utilities
- `library-item.liquid` - Basic Jekyll layout
- `requirements.txt` - Python dependencies

#### Test Mode Features:
- Find 5 most recent entries by year in papers.bib
- Generate basic markdown pages
- Validate file creation and content

### Phase 2: Enhanced Content Generation
**Goal**: Rich content with abstracts, metadata, and basic features

#### Tasks:
1. Extract and format abstracts
2. Generate proper front matter
3. Add author formatting
4. Include publication details
5. Add basic styling

#### Files to Update:
- `content_generator.py` - Enhanced markdown generation
- `library-item.liquid` - Improved layout
- `library-pages.scss` - Basic styling

### Phase 3: PDF and Media Integration
**Goal**: PDF embedding and image gallery functionality

#### Tasks:
1. Implement PDF embedding with PDF.js
2. Create image gallery system
3. Handle multiple file types
4. Add responsive design

#### Files to Create:
- `pdf-viewer.js` - PDF embedding functionality
- `gallery.js` - Image gallery with lightbox
- `pdf-viewer.scss` - PDF viewer styles
- `gallery.scss` - Gallery styles

### Phase 4: Social Features
**Goal**: Share buttons and social media posting

#### Tasks:
1. Add share panel with social buttons
2. Implement social media post generation
3. Add copy link functionality
4. Create pre-formatted posts

#### Files to Create:
- `sharing.js` - Share panel functionality
- `social-posts.py` - Social media post generation
- `social-posting.js` - Social posting interface
- `sharing.scss` - Share panel styles

### Phase 5: Advanced Features
**Goal**: Search, filtering, and automation

#### Tasks:
1. Add search and filtering
2. Implement related content suggestions
3. Add analytics tracking
4. Create automation scripts

#### Files to Create:
- `search.js` - Search functionality
- `analytics.js` - Analytics tracking
- `automation.py` - Watch mode and CI integration

### Phase 6: Polish and Optimization
**Goal**: Performance, SEO, and user experience

#### Tasks:
1. Optimize page load times
2. Add SEO meta tags
3. Implement structured data
4. Add accessibility features
5. Create documentation

## Current Phase: Phase 1 - Basic Scaffolding

### Immediate Next Steps:
1. Create `generate_library_pages.py` with --test flag
2. Implement basic BibTeX parsing
3. Create `library-item.liquid` layout
4. Test with 5 latest items with location
5. Validate generated pages

### Success Criteria for Phase 1:
- [ ] Script runs with --test flag
- [ ] Finds 5 most recent entries by year
- [ ] Generates valid markdown files
- [ ] Pages render correctly in Jekyll
- [ ] Basic layout displays content properly

### Dependencies:
- `bibtexparser` - BibTeX parsing
- `python-dateutil` - Date handling
- `slugify` - URL-friendly slugs
- `pyyaml` - YAML front matter generation

## Testing Strategy

### Unit Tests:
- BibTeX parsing accuracy
- Date extraction and formatting
- Slug generation
- Content generation

### Integration Tests:
- Jekyll build process
- Layout rendering
- Asset loading
- Responsive design

### Manual Tests:
- Test mode with sample data
- Full generation with all items
- Cross-browser compatibility
- Mobile responsiveness

## Configuration

### Jekyll Configuration Updates:
```yaml
collections:
  library:
    output: true
    permalink: /library/:name/
```

### Python Configuration:
- Source bibliography file path
- Output directory path
- Asset paths
- Social media settings

## Future Enhancements

### Potential Features:
- AI-generated summaries
- Automatic tagging
- Citation network visualization
- Export to various formats
- Integration with reference managers
- Collaborative features
- Version control for changes

### Performance Optimizations:
- Lazy loading for images
- Caching for generated content
- CDN integration
- Progressive web app features
