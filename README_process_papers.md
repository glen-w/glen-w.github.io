# Process Papers Pipeline Documentation

## Overview

The `process_papers.py` script is a comprehensive pipeline for processing academic papers and presentations from Zotero exports. It automatically generates thumbnails, renames files, adds appropriate tags to BibTeX entries, and prepares everything for display on a Jekyll-based academic website.

## Current Workflow

### 1. Input Processing
- **Source**: `_bibliography/Exported Items.bib` (Zotero export)
- **Target**: `_bibliography/papers.bib` (processed file)
- **Backup**: Creates timestamped backup before processing

### 2. File Processing Pipeline

#### A. PDF Files
- **Source**: Files referenced in `file` field with `:application/pdf` MIME type
- **Destination**: `assets/pdf/`
- **Naming Convention**: `{author}_{year}_{title}_{journal}.pdf`
- **Processing**:
  - Copy PDF to assets directory
  - Generate thumbnail (default: 600x pixels)
  - Update PDF metadata with BibTeX information
  - Add `pdf` or `slides` tag based on content type

#### B. Image Files
- **Source**: Files referenced in `file` field with image MIME types
- **Supported Types**: `:image/jpeg`, `:image/jpg`, `:image/png`, `:image/gif`
- **Destination**: `assets/img/publications/`
- **Naming Convention**: `{author}_{year}_{title}_{journal}_{type}_{number}.{ext}`

#### C. Image Classification
- **Figures**: Files starting with "figure" → `{base}_figure_{01,02,03...}.{ext}`
- **Photos**: All other images → `{base}_photo_{01,02,03...}.{ext}`
- **Tags Added**: `figures = {file1, file2, ...}` or `photos = {file1, file2, ...}`

### 3. Content Type Detection

#### Presentations (Slides)
- **Keywords**: `presenter`, `speaker`, `prezi`, `miro`
- **Tags Added**: `preview = {thumbnail}`, `slides = {pdf_file}`
- **Button Type**: Slides button with appropriate icon

#### Papers (PDFs)
- **Default**: All other entries
- **Tags Added**: `preview = {thumbnail}`, `pdf = {pdf_file}`
- **Button Type**: PDF button

### 4. File Naming System

#### Base Filename Components
1. **Author**: First author's last name + first name initial
2. **Year**: Publication year
3. **Title**: Cleaned title (removes special characters)
4. **Journal/Publisher**: Institution, journal, or publisher name

#### Example Naming
```
Input:  "Wright, Glen" + "2023" + "Ocean Governance" + "Nature"
Output: "wright_g_2023_ocean_governance_nature.pdf"
```

### 5. Thumbnail Generation
- **Tool**: ImageMagick
- **Default Size**: 600x pixels (auto height)
- **Format**: JPEG
- **Destination**: `assets/img/publication_preview/`
- **Naming**: Same as PDF but with `.jpeg` extension

## Current Tags and Fields

### BibTeX Tags Added by Script

#### Document Access
- `pdf = {filename}` - For academic papers
- `slides = {filename}` - For presentations
- `preview = {thumbnail}` - Thumbnail image for all entries

#### Media Galleries
- `figures = {file1, file2, ...}` - Figure images
- `photos = {file1, file2, ...}` - Photo images

#### Jekyll Compatibility
- `website = {url}` - Renamed from `url` field
- `website_date = {date}` - Renamed from `urldate` field

### Jekyll Template Fields Used

#### Document Links
- `entry.pdf` - PDF download button
- `entry.slides` - Slides download button (with Prezi/Miro detection)
- `entry.preview` - Thumbnail display
- `entry.website` - External website button (with YouTube/Amazon detection)

#### Media Galleries
- `entry.figures` - Figure gallery (multiple images)
- `entry.photos` - Photo gallery (multiple images)
- `entry.file` - Legacy file field gallery (being phased out)

#### External Links
- `entry.doi` - DOI link button
- `entry.arxiv` - arXiv link button
- `entry.html` - HTML version button

## Command Line Options

### Basic Usage
```bash
python process_papers.py [options]
```

### Available Options

#### Processing Control
- `--force` - Force reprocessing of all entries
- `--regenerate` - Delete existing files and regenerate everything
- `--test` - Test mode (process only first 5 entries)
- `--test-count N` - Process N entries in test mode

#### File Processing
- `--thumbnail-size WIDTHxHEIGHT` - Set thumbnail dimensions (default: 600x)
- `--bibtex-file PATH` - Specify source BibTeX file
- `--no-metadata` - Skip PDF metadata updates
- `--force-refetch-metadata` - Force re-fetching external metadata

#### Output Control
- `--verbose` - Enable detailed output
- `--clear-cache` - Clear metadata cache before processing
- `--no-rename-urls` - Skip URL field renaming

## File Structure

### Input Files
```
_bibliography/
├── Exported Items.bib          # Zotero export (source)
├── papers.bib                  # Processed file (target)
└── papers_backup_*.bib         # Timestamped backups
```

### Output Directories
```
assets/
├── pdf/                        # PDF files
├── img/
│   ├── publication_preview/    # Thumbnails
│   └── publications/           # Figure/photo images
└── html/                       # HTML files (if any)
```

## Current Limitations

### Image Processing
- Only processes images from `file` field
- No support for agenda, slides, or other document types
- Limited to figure/photo classification
- No batch processing of multiple image types

### File Naming
- Fixed naming convention (author_year_title_journal)
- No custom naming patterns
- Limited special character handling

### Content Detection
- Only keyword-based presentation detection
- No automatic content type inference
- Limited support for different document types

## Future Enhancement Opportunities

### Proposed Improvements
1. **Multi-type Support**: Handle agenda, slides, handouts, etc.
2. **Flexible Naming**: Support custom naming patterns
3. **Smart Classification**: Auto-detect content types
4. **Batch Processing**: Process multiple file types simultaneously
5. **Custom Tags**: Support for additional metadata fields
6. **Template Integration**: Better Jekyll template integration

### Suggested Zotero Naming Convention
```
For images:
- "figure_01.jpg" → figures gallery
- "photo_01.jpg" → photos gallery
- "agenda_01.pdf" → agenda button
- "slides_01.pdf" → slides button
- "handout_01.pdf" → handout button
```

---

## Roadmap for Script Revision

### Phase 1: Enhanced File Type Detection and Processing
**Goal**: Support multiple document types with intelligent classification

#### 1.1 File Type Detection System
- **Current**: Only PDFs and images (figure/photo)
- **New**: Support for agenda, slides, handouts, posters, reports, etc.
- **Implementation**: 
  - Extend `process_images_for_entry()` to `process_files_for_entry()`
  - Add file type detection based on filename prefixes
  - Create mapping: `{prefix} → {bibtag} → {button_type}`

#### 1.2 Enhanced Naming Convention
- **Current**: Fixed `{author}_{year}_{title}_{journal}` pattern
- **New**: Flexible patterns based on file type
- **Implementation**:
  - Create `FileTypeConfig` class with naming rules
  - Support custom patterns per file type
  - Maintain backward compatibility

#### 1.3 File Type Configuration
```python
FILE_TYPE_CONFIG = {
    'figure': {'tag': 'figures', 'button': 'figures', 'pattern': '{base}_figure_{num:02d}'},
    'photo': {'tag': 'photos', 'button': 'photos', 'pattern': '{base}_photo_{num:02d}'},
    'agenda': {'tag': 'agenda', 'button': 'agenda', 'pattern': '{base}_agenda_{num:02d}'},
    'slides': {'tag': 'slides', 'button': 'slides', 'pattern': '{base}_slides_{num:02d}'},
    'handout': {'tag': 'handouts', 'button': 'handout', 'pattern': '{base}_handout_{num:02d}'},
    'poster': {'tag': 'posters', 'button': 'poster', 'pattern': '{base}_poster_{num:02d}'},
    'report': {'tag': 'reports', 'button': 'report', 'pattern': '{base}_report_{num:02d}'}
}
```

### Phase 2: Improved Content Classification
**Goal**: Smart detection of content types beyond keyword matching

#### 2.1 Multi-Factor Classification
- **Current**: Keywords only (`presenter`, `speaker`, `prezi`, `miro`)
- **New**: Combined approach using multiple signals
- **Signals**:
  - Filename patterns (`slides_`, `agenda_`, etc.)
  - Keywords in title/abstract
  - Entry type (`@misc`, `@inproceedings`, etc.)
  - File extensions and MIME types
  - Zotero item type tags

#### 2.2 Content Type Priority System
```python
CONTENT_TYPE_RULES = [
    {'type': 'slides', 'priority': 1, 'signals': ['slides_', 'presenter', 'speaker']},
    {'type': 'agenda', 'priority': 2, 'signals': ['agenda_', 'schedule']},
    {'type': 'handout', 'priority': 3, 'signals': ['handout_', 'materials']},
    {'type': 'poster', 'priority': 4, 'signals': ['poster_', 'conference_poster']},
    {'type': 'paper', 'priority': 5, 'signals': ['@article', '@inproceedings']}
]
```

### Phase 3: Enhanced Jekyll Integration
**Goal**: Better integration with Jekyll templates and improved UI

#### 3.1 Dynamic Button Generation
- **Current**: Hardcoded button types
- **New**: Dynamic button generation based on file types
- **Implementation**:
  - Generate button HTML in Liquid templates
  - Support custom icons per file type
  - Handle multiple buttons per entry

#### 3.2 Gallery System Enhancement
- **Current**: Separate `figures` and `photos` galleries
- **New**: Unified gallery system with type filtering
- **Features**:
  - Mixed media galleries
  - Type-based filtering
  - Lazy loading for large galleries

#### 3.3 Template Field Mapping
```liquid
{% for file_type in entry.file_types %}
  {% case file_type %}
    {% when 'figures' %}
      <!-- Figure gallery -->
    {% when 'photos' %}
      <!-- Photo gallery -->
    {% when 'agenda' %}
      <!-- Agenda button -->
    {% when 'slides' %}
      <!-- Slides button -->
  {% endcase %}
{% endfor %}
```

### Phase 4: Advanced Processing Features
**Goal**: More sophisticated file processing and metadata handling

#### 4.1 Batch Processing
- **Current**: Sequential processing
- **New**: Parallel processing for better performance
- **Features**:
  - Multi-threaded file copying
  - Concurrent thumbnail generation
  - Progress tracking and reporting

#### 4.2 Metadata Enhancement
- **Current**: Basic PDF metadata updates
- **New**: Rich metadata for all file types
- **Features**:
  - EXIF data extraction for images
  - Document properties for PDFs
  - Custom metadata fields
  - Alt text generation for images

#### 4.3 Error Handling and Recovery
- **Current**: Basic error handling
- **New**: Robust error recovery system
- **Features**:
  - Detailed error logging
  - Partial processing recovery
  - Validation and verification
  - Rollback capabilities

### Phase 5: Configuration and Customization
**Goal**: Make the script highly configurable and extensible

#### 5.1 Configuration System
- **Current**: Hardcoded settings
- **New**: YAML/JSON configuration files
- **Features**:
  - User-defined file type mappings
  - Custom naming patterns
  - Template customization
  - Output directory configuration

#### 5.2 Plugin Architecture
- **Current**: Monolithic script
- **New**: Modular plugin system
- **Features**:
  - Custom file processors
  - Custom metadata extractors
  - Custom naming strategies
  - Custom template generators

### Phase 6: Testing and Documentation
**Goal**: Ensure reliability and maintainability

#### 6.1 Comprehensive Testing
- **Unit tests** for all functions
- **Integration tests** for full pipeline
- **Performance tests** for large datasets
- **Regression tests** for existing functionality

#### 6.2 Documentation Updates
- **API documentation** for all functions
- **Configuration guide** for users
- **Migration guide** from old to new system
- **Troubleshooting guide** for common issues

### Implementation Timeline

#### Week 1-2: Phase 1 (File Type Detection)
- Implement `FileTypeConfig` system
- Extend file processing functions
- Add support for new file types
- Update naming conventions

#### Week 3-4: Phase 2 (Content Classification)
- Implement multi-factor classification
- Add content type priority system
- Update BibTeX tag generation
- Test with existing data

#### Week 5-6: Phase 3 (Jekyll Integration)
- Update Liquid templates
- Implement dynamic button generation
- Enhance gallery system
- Test UI integration

#### Week 7-8: Phase 4 (Advanced Features)
- Implement batch processing
- Add metadata enhancement
- Improve error handling
- Performance optimization

#### Week 9-10: Phase 5 (Configuration)
- Implement configuration system
- Add plugin architecture
- Create user documentation
- Migration tools

#### Week 11-12: Phase 6 (Testing & Polish)
- Comprehensive testing
- Documentation updates
- Performance tuning
- Final integration testing

### Migration Strategy

#### Backward Compatibility
- Maintain existing functionality
- Gradual migration path
- Configuration flags for old vs new behavior
- Automatic detection of old vs new naming

#### Data Migration
- Script to convert existing entries
- Validation of migrated data
- Rollback capabilities
- User confirmation for changes

#### Testing Strategy
- Test with existing bibliography
- Validate all existing functionality
- Performance comparison
- User acceptance testing

## Error Handling

### Common Issues
- **Missing Dependencies**: ImageMagick, PyPDF2
- **File Permissions**: Write access to assets directories
- **Corrupted PDFs**: Metadata update failures
- **Malformed BibTeX**: Syntax errors in entries

### Recovery
- Automatic backup creation
- Graceful error handling
- Detailed error logging
- Test mode for debugging

## Dependencies

### Required
- Python 3.6+
- ImageMagick (for thumbnails)
- PyPDF2 (for PDF metadata)

### Optional
- External APIs for metadata fetching
- Additional image processing libraries

## Configuration

### Default Settings
- Thumbnail size: 600x pixels
- Output format: JPEG
- Backup retention: Manual cleanup
- Cache location: `_metadata_cache.json`

### Customization
- Modify filename patterns in functions
- Adjust thumbnail sizes
- Add new content type detection
- Extend tag generation logic