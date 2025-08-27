# Process Papers Script

A simplified Python script for processing academic papers in BibTeX format. The script handles PDF copying, thumbnail generation, and adds required tags to BibTeX entries.

## Features

- **BibTeX Parsing**: Robust parsing of BibTeX entries with proper nested brace handling
- **PDF Management**: Copy PDF files to organized directory structure with descriptive filenames
- **Thumbnail Generation**: Create preview images for each PDF using ImageMagick
- **Metadata Updates**: Update PDF metadata with BibTeX information using PyPDF2
- **Tag Management**: Automatically add `pdf`/`slides` and `preview` tags to BibTeX entries (slides for presentations, pdf for papers)
- **Test Mode**: Process only a subset of entries for quick testing
- **Regenerate Mode**: Clean existing files and start fresh
- **BibTeX Validation**: Comprehensive testing using bibtexparser library to ensure output syntax is correct

## Requirements

### Python Dependencies
```bash
pip install -r requirements.txt
```

Required packages:
- `PyPDF2>=3.0.0` - For PDF metadata updating

### System Dependencies
- **ImageMagick** - For generating PDF thumbnails
  - Install from: https://imagemagick.org/script/download.php
  - Supports both modern `magick` command and legacy `convert` command

## Usage

### Basic Usage
```bash
python process_papers.py
```

### Command Line Options
```bash
python process_papers.py [OPTIONS]

Options:
  --bibtex-file PATH        Path to papers.bib file (default: _bibliography/papers.bib)
  --thumbnail-size SIZE     Thumbnail size in format WIDTHxHEIGHT or WIDTHx for auto height (default: 600x)
  --regenerate              Delete all existing PDFs and thumbnails, then regenerate everything
  --force                   Force reprocessing of entries even if they already have tags
  --update-metadata         Update PDF metadata with BibTeX information (default: True)
  --no-metadata             Skip PDF metadata updating
  --verbose, -v             Enable verbose output for detailed processing information
  --test                    Test mode: process only first 5 entries for quick testing
  --test-count INT          Number of entries to process in test mode (default: 5)
  --help                    Show help message
```

### Examples

#### Process all papers
```bash
python process_papers.py
```

#### Test mode (process only 3 entries)
```bash
python process_papers.py --test --test-count 3
```

#### Regenerate everything
```bash
python process_papers.py --regenerate
```

#### Force reprocessing
```bash
python process_papers.py --force
```

#### Skip metadata updates
```bash
python process_papers.py --no-metadata
```

#### Verbose output
```bash
python process_papers.py --verbose
```

## How It Works

### 1. BibTeX Parsing
The script parses each BibTeX entry, handling nested braces properly:
```bibtex
@article{example2023,
    title = {Title with {nested} braces},
    author = {Smith, John and Doe, Jane},
    year = {2023},
    file = {Description:/path/to/paper.pdf:application/pdf}
}
```

### 2. Filename Generation
Creates descriptive filenames using the pattern:
```
authorfirstname_secondname_etal_year_FULL_TITLE_journal_or_publisher.pdf
```

Example: `John_Smith_Jane_Doe_2023_Climate_Change_Impacts_Nature.pdf`

### 3. File Operations
- Copies PDF files to `assets/pdf/` directory
- Generates thumbnails in `assets/img/publication_preview/` directory
- Updates PDF metadata with BibTeX information

### 4. BibTeX Updates
Adds `pdf`/`slides` and `preview` tags to each entry. The script checks if keywords contain "presenter" and sets `slides` tags for presentations, otherwise sets `pdf` tags for papers:

```bibtex
@article{example2023,
    title = {Title with nested braces},
    author = {Smith, John and Doe, Jane},
    year = {2023},
    keywords = {climate change, research},
    pdf = {John_Smith_Jane_Doe_2023_Climate_Change_Impacts_Nature.pdf},
    preview = {John_Smith_Jane_Doe_2023_Climate_Change_Impacts_Nature.jpeg}
}

@presentation{conference2023,
    title = {Conference Presentation},
    author = {Smith, John},
    year = {2023},
    keywords = {presenter, climate policy},
    slides = {John_Smith_2023_Conference_Presentation_Conference.pdf},
    preview = {John_Smith_2023_Conference_Presentation_Conference.jpeg}
}
```

## Testing

### Running Tests
```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_process_papers.py -v

# Run with coverage
python -m pytest tests/ --cov=process_papers --cov-report=term-missing

# Use the test runner script
python run_tests.py
```

### Test Coverage
The test suite covers:
- **BibTeX Parsing**: Entry parsing, field extraction, brace handling
- **Filename Generation**: Title cleaning, author name extraction, journal/publisher handling
- **File Operations**: PDF copying, thumbnail generation, metadata updates
- **Error Handling**: Missing dependencies, file failures, malformed input
- **Integration**: Full workflow testing with mocked dependencies
- **BibTeX Validation**: Syntax validation using bibtexparser library
- **Real Data Testing**: Validation against actual papers.bib file

### BibTeX Validation Testing
The test suite includes comprehensive BibTeX syntax validation using the `bibtexparser` library:

- **Syntax Validation**: Ensures all generated BibTeX can be parsed by standard libraries
- **Round-trip Testing**: Validates that modified entries can be written and parsed again
- **Compatibility Testing**: Compares our parser output with bibtexparser results
- **Real Data Testing**: Tests against the actual papers.bib file to ensure compatibility
- **Edge Case Handling**: Tests special characters, nested braces, and malformed entries

### Test Structure
```
tests/
├── __init__.py
├── test_process_papers.py          # Core functionality tests
├── test_main_functions.py          # Main processing tests with mocking
├── test_bibtex_validation.py      # BibTeX syntax validation tests
└── test_real_bibtex.py            # Tests using real papers.bib file
```

## File Structure

```
project/
├── process_papers.py               # Main script
├── requirements.txt                # Python dependencies
├── requirements-test.txt           # Test dependencies
├── pytest.ini                     # Pytest configuration
├── run_tests.py                   # Test runner script
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── test_process_papers.py
│   ├── test_main_functions.py
│   ├── test_bibtex_validation.py
│   └── test_real_bibtex.py
├── assets/
│   ├── pdf/                       # Copied PDF files
│   └── img/
│       └── publication_preview/   # Generated thumbnails
└── _bibliography/
    └── papers.bib                 # Input BibTeX file
```

## Error Handling

The script handles various error conditions gracefully:
- **Missing Dependencies**: Checks for PyPDF2 and ImageMagick before processing
- **File Failures**: Continues processing other entries if individual files fail
- **Malformed BibTeX**: Skips entries that can't be parsed
- **Missing Files**: Logs warnings for referenced files that don't exist

## Backup and Safety

- **Automatic Backups**: Creates timestamped backups before processing
- **Safe Operations**: Only modifies files when operations succeed
- **Test Mode**: Process small subsets for validation before full runs

## Troubleshooting

### Common Issues

1. **ImageMagick not found**
   - Install ImageMagick from the official website
   - Ensure `magick` or `convert` command is available in PATH

2. **PyPDF2 import error**
   - Install with: `pip install PyPDF2>=3.0.0`

3. **Permission errors**
   - Ensure write permissions to output directories
   - Check file permissions for source PDFs

4. **Thumbnail generation fails**
   - Verify ImageMagick installation
   - Check PDF file integrity
   - Ensure sufficient disk space

5. **BibTeX parsing errors**
   - Check for malformed entries in papers.bib
   - Verify entry syntax and brace matching
   - Run tests to identify specific issues

### Debug Mode
Use `--verbose` flag for detailed processing information:
```bash
python process_papers.py --verbose
```

## Contributing

When modifying the script:
1. Add tests for new functionality
2. Ensure all tests pass: `python -m pytest tests/ -v`
3. Update documentation for new features
4. Test with sample data before production use
5. Validate BibTeX output syntax using the validation tests

## License

This script is part of the website project and follows the same licensing terms.
