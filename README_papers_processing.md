# Enhanced Papers Processing Script

This enhanced script processes the `_bibliography/papers.bib` file to:

1. **Parse BibTeX entries** - Extract citation keys and file paths with improved nested brace handling
2. **Copy PDF files** - Copy PDFs to `assets/pdf/` with descriptive filenames (AUTHOR_YEAR_FULL_TITLE_JOURNAL.pdf)
3. **Add PDF and Preview tags** - Add both `pdf = {filename.pdf}` and `preview = {filename.jpeg}` to each BibTeX entry
4. **Generate thumbnails** - Create JPEG preview images for each PDF
5. **Support regenerate mode** - Clean existing files and start fresh when needed

## New Features

### 🧹 Regenerate Mode

The `--regenerate` flag deletes all existing PDFs and publication preview thumbnails before running, ensuring a clean slate:

```bash
# Delete all existing files and regenerate everything
python process_papers.py --regenerate
```

### 🔒 Improved Brace Handling

- **Nested braces are handled gracefully** - All `{text}` patterns are properly parsed and cleaned
- **No braces in filenames** - All braces are removed while preserving the content inside
- **Clean tags** - Both `pdf` and `preview` tags contain clean, brace-free filenames

### 📝 Full Title Preservation

- **Complete titles in filenames** - The full paper title is preserved in the filename for better descriptiveness
- **Smart truncation** - If titles are too long, they're intelligently truncated while keeping essential information
- **Meaningful filenames** - Files are named as: `Author_Year_FullTitle_Journal.pdf`

## Usage

### Prerequisites

- Python 3.6+
- Access to the PDF files referenced in the BibTeX entries
- ImageMagick installed for thumbnail generation

### Running the Script

```bash
# Process papers and copy PDFs (normal mode)
python process_papers.py

# Regenerate everything - delete existing files and start fresh
python process_papers.py --regenerate

# Regenerate thumbnails only (keep existing PDFs)
python process_papers.py --regenerate-thumbnails

# Force reprocessing of entries that already have tags
python process_papers.py --force

# Custom thumbnail size
python process_papers.py --thumbnail-size 800x600

# Process a different BibTeX file
python process_papers.py --bibtex-file path/to/other.bib
```

### Command Line Options

- `--regenerate` - Delete all existing PDFs and thumbnails, then regenerate everything
- `--regenerate-thumbnails` - Regenerate thumbnails for existing papers (without deleting PDFs)
- `--force` - Force reprocessing of entries even if they already have tags
- `--thumbnail-size` - Set thumbnail dimensions (default: 600x for auto height)
- `--bibtex-file` - Specify path to BibTeX file (default: \_bibliography/papers.bib)
- `--rename-urls` - Rename "url" fields to "website" for Jekyll compatibility
- `--add-altmetric` - Add altmetric: true for entries with DOI
- `--update-metadata` - Update PDF metadata with BibTeX information (default: True)
- `--no-metadata` - Skip PDF metadata updating
- `--skip-deps-check` - Skip dependency checking and installation

## What It Does

1. **Reads** `_bibliography/papers.bib`
2. **Cleans** all field values by removing nested braces while preserving content
3. **Parses** each BibTeX entry to extract:
   - Citation key (e.g., `Durussel2018`, `Iucn2018c`)
   - File paths from the `file` field
   - Title, author, year, and journal information
4. **Copies** PDF files to `assets/pdf/` with descriptive names like:
   - `/assets/pdf/Carole_Durussel_etal_2018_Strengthening_Regional_Ocean_Governance_for_the_High_Seas_STRONG_High_Seas.pdf`
   - `/assets/pdf/Sabrina_Guduff_etal_2018_Laying_the_Foundations_for_Management_of_a_Seamount_Beyond_National_Jurisdiction_IDDRI_IUCN_FFEM.pdf`
5. **Generates** thumbnail previews in `assets/img/publication_preview/`
6. **Updates PDF metadata** with BibTeX information (title, author, keywords, etc.)
7. **Updates** the BibTeX file by adding both `pdf` and `preview` tags:
   ```bibtex
   @techreport{Durussel2018,
       title = {Strengthening Regional Ocean Governance...},
       ...
       preview = {Carole_Durussel_etal_2018_Strengthening_Regional_Ocean_Governance_for_the_High_Seas_STRONG_High_Seas.jpeg},
       pdf = {Carole_Durussel_etal_2018_Strengthening_Regional_Ocean_Governance_for_the_High_Seas_STRONG_High_Seas.pdf}
   }
   ```

## Output

- **PDF files**: Copied to `/assets/pdf/` directory with descriptive names
- **Thumbnail images**: Generated in `/assets/img/publication_preview/` directory
- **Updated BibTeX**: `_bibliography/papers.bib` with new `pdf` and `preview` tags
- **Log output**: Shows progress with emojis and summary of processed entries

### Example Output

```
📚 Processing _bibliography/papers.bib...
  ✅ Renamed 45 'url' fields to 'website' for Jekyll compatibility
  ✅ Added altmetric: true for 23 entries with DOI

📄 Processing entry: Durussel2018
✓ Copied: /path/to/source.pdf -> assets/pdf/Carole_Durussel_etal_2018_Strengthening_Regional_Ocean_Governance_for_the_High_Seas_STRONG_High_Seas.pdf
✅ Generated thumbnail: Carole_Durussel_etal_2018_Strengthening_Regional_Ocean_Governance_for_the_High_Seas_STRONG_High_Seas.jpeg
✅ Added pdf and preview tags: Carole_Durussel_etal_2018_Strengthening_Regional_Ocean_Governance_for_the_High_Seas_STRONG_High_Seas.jpeg

✅ Updated _bibliography/papers.bib with pdf and preview tags

📊 Summary:
  Processed entries: 161
  Copied PDF files: 137
  Skipped entries: 0
  Renamed URLs: 45
  Added Altmetric: 23
  Output directory: assets/pdf
```

## Regenerate Mode Example

```bash
python process_papers.py --regenerate
```

Output:

```
🧹 Regenerate mode: Cleaning up existing files...
  🗑️  Deleted: Carole_Durussel_etal_2018_Strengthening_Regional_Ocean_Governance_for_the_High_Seas_STRONG_High_Seas.pdf
  🗑️  Deleted: Sabrina_Guduff_etal_2018_Laying_the_Foundations_for_Management_of_a_Seamount_Beyond_National_Jurisdiction_IDDRI_IUCN_FFEM.pdf
  🗑️  Deleted: Carole_Durussel_etal_2018_Strengthening_Regional_Ocean_Governance_for_the_High_Seas_STRONG_High_Seas.jpeg
  🗑️  Deleted: Sabrina_Guduff_etal_2018_Laying_the_Foundations_for_Management_of_a_Seamount_Beyond_National_Jurisdiction_IDDRI_IUCN_FFEM.jpeg
  ✅ Cleanup complete

📚 Processing _bibliography/papers.bib...
# ... continues with normal processing
```

## Notes

- **Full title preservation**: The complete paper title is included in filenames for maximum descriptiveness
- **Smart filename length management**: If titles are too long, they're intelligently truncated while preserving essential information
- **No braces in output**: All nested braces are properly handled and removed from both filenames and tags
- **Clean slate option**: Regenerate mode ensures no conflicts with existing files
- **Enhanced error handling**: Better validation and error reporting throughout the process

## Error Handling

- Missing PDF files are logged but don't stop processing
- File copy errors are logged with details
- Thumbnail generation failures are reported but don't prevent PDF processing
- The script continues processing other entries even if some fail
- Brace parsing errors are handled gracefully

## Backup

The script modifies the original `papers.bib` file. Consider backing it up before running:

```bash
cp _bibliography/papers.bib _bibliography/papers.bib.backup
```

## Technical Details

### Brace Handling Algorithm

The script uses a recursive approach to handle nested braces:

1. Find the innermost braces `{text}` and extract `text`
2. Repeat until no more braces remain
3. Clean up any unmatched braces
4. Preserve all content while ensuring no braces remain in output

### Filename Generation

Filenames are constructed as:
`AuthorNames_Year_FullTitle_Journal.pdf`

Where:

- **AuthorNames**: First author's first and last name, or "etal" for multiple authors
- **Year**: Publication year
- **FullTitle**: Complete paper title (cleaned of special characters)
- **Journal**: Journal name, publisher, or institution

### Thumbnail Generation

Uses ImageMagick to create high-quality JPEG previews:

- 150 DPI for crisp images
- White background to handle transparency issues
- 85% JPEG quality for good file size balance
- Default size: 600px width with auto height (maintains aspect ratio)
- Fallback to legacy `convert` command if `magick` fails

### PDF Metadata Updating

Automatically updates PDF metadata with BibTeX information:

- **Title**: Full paper title from BibTeX
- **Author**: First author's full name
- **Subject**: Journal/conference/institution name
- **Keywords**: Keywords from BibTeX entry
- **Creator**: Your name or institution
- **Producer**: Tool identification
- **Description**: Abstract (truncated if too long)

**Requirements**: Install `PyPDF2` or `pikepdf` for metadata updating

**Automatic Installation**: The script automatically checks for and installs missing Python dependencies:

```bash
# Dependencies are checked and installed automatically
python process_papers.py

# Skip dependency checking if needed
python process_papers.py --skip-deps-check
```

**Manual Installation** (if auto-install fails):

```bash
pip install PyPDF2
# or
pip install pikepdf
```
