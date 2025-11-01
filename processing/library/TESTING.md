# Testing Guide for Library Generator

This document describes the comprehensive test suite for the library page generator system.

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Pytest fixtures and configuration
├── test_bib_parser.py          # Unit tests for BibParser class
├── test_content_generator.py   # Unit tests for ContentGenerator class
├── test_library_page_generator.py  # Unit tests for LibraryPageGenerator class
└── test_integration.py         # Integration tests for complete system
```

## Test Categories

### Unit Tests
- **BibParser Tests**: Test individual parsing functions
- **ContentGenerator Tests**: Test markdown and YAML generation
- **LibraryPageGenerator Tests**: Test main generation logic

### Integration Tests
- **End-to-End Tests**: Complete generation workflow
- **Error Handling Tests**: Robustness and error recovery
- **Performance Tests**: Large bibliography handling
- **Unicode Tests**: International character support

## Running Tests

### Prerequisites
```bash
pip install -r requirements-test.txt
```

### Basic Test Execution
```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_bib_parser.py

# Run specific test class
python -m pytest tests/test_bib_parser.py::TestBibParser

# Run specific test method
python -m pytest tests/test_bib_parser.py::TestBibParser::test_clean_title
```

### Using the Test Runner Script
```bash
# Run all tests
python run_tests.py

# Run only unit tests
python run_tests.py --unit

# Run only integration tests
python run_tests.py --integration

# Run with coverage
python run_tests.py --coverage

# Generate HTML report
python run_tests.py --html

# Run in parallel
python run_tests.py --parallel

# Run specific test file
python run_tests.py --file test_bib_parser.py
```

### Advanced Test Options
```bash
# Run with coverage and HTML report
python run_tests.py --coverage --html

# Run tests in parallel with verbose output
python run_tests.py --parallel --verbose

# Run only fast tests (exclude slow ones)
python -m pytest -m "not slow"
```

## Test Coverage

The test suite aims for comprehensive coverage of:

### BibParser Class (100% coverage target)
- ✅ Title cleaning and normalization
- ✅ Author parsing and formatting
- ✅ Entry type detection and display
- ✅ Date extraction (year, month)
- ✅ Venue formatting
- ✅ Keyword extraction and cleaning
- ✅ Link extraction (URLs, DOIs, PDFs, etc.)
- ✅ Image extraction from various fields
- ✅ Abstract and description generation

### ContentGenerator Class (100% coverage target)
- ✅ YAML front matter generation
- ✅ Markdown content generation
- ✅ Category determination logic
- ✅ Different entry types (article, conference, report, etc.)
- ✅ Edge cases and error handling

### LibraryPageGenerator Class (100% coverage target)
- ✅ Initialization and configuration
- ✅ Bibliography loading
- ✅ Entry filtering (test mode vs normal mode)
- ✅ Filename generation
- ✅ Page generation
- ✅ Error handling and recovery
- ✅ Output directory management

### Integration Tests (95% coverage target)
- ✅ End-to-end generation workflow
- ✅ Test mode vs normal mode comparison
- ✅ Generated file consistency and validation
- ✅ Filename generation consistency
- ✅ Error handling robustness
- ✅ Large bibliography handling
- ✅ Unicode character support

## Test Data

### Sample BibTeX Content
The test suite uses comprehensive sample data including:
- Various entry types (article, conference, report, misc, blog)
- Different author formats (single, multiple, first-last, last-first)
- Various date formats (year only, year-month, full date)
- Different keyword formats (comma-separated, semicolon-separated)
- Various link types (URLs, DOIs, PDFs, videos, slides)
- Unicode characters and special cases
- Edge cases (empty fields, malformed data)

### Fixtures
- `sample_bib_content`: Complete BibTeX test data
- `sample_bib_file`: Temporary BibTeX file
- `generator`: LibraryPageGenerator instance
- `test_generator`: LibraryPageGenerator in test mode
- `bib_parser`: BibParser instance
- `content_generator`: ContentGenerator instance
- `sample_entry`: Individual BibTeX entry for testing

## Test Scenarios

### Happy Path Tests
- ✅ Normal bibliography processing
- ✅ Test mode functionality
- ✅ File generation and content validation
- ✅ YAML front matter structure
- ✅ Markdown content generation

### Edge Case Tests
- ✅ Empty or missing fields
- ✅ Special characters in titles
- ✅ Very long titles and abstracts
- ✅ Malformed BibTeX data
- ✅ Unicode characters and emojis
- ✅ Different date formats

### Error Handling Tests
- ✅ Non-existent BibTeX files
- ✅ Malformed BibTeX syntax
- ✅ Permission errors
- ✅ Invalid entry data
- ✅ Large bibliography processing

### Performance Tests
- ✅ Processing 50+ entries
- ✅ Memory usage optimization
- ✅ File I/O efficiency
- ✅ Parallel processing capabilities

## Continuous Integration

### GitHub Actions (Recommended)
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    - name: Run tests
      run: python run_tests.py --coverage --html
```

### Local Development
```bash
# Quick test during development
python -m pytest tests/test_bib_parser.py -v

# Full test suite before commit
python run_tests.py --coverage

# Performance test
python -m pytest tests/test_integration.py::TestIntegration::test_large_bibliography_handling -v
```

## Debugging Tests

### Running Individual Tests
```bash
# Run specific test with maximum verbosity
python -m pytest tests/test_bib_parser.py::TestBibParser::test_clean_title -vvv

# Run with print statements visible
python -m pytest tests/test_bib_parser.py::TestBibParser::test_clean_title -s

# Run with debugger on failure
python -m pytest tests/test_bib_parser.py::TestBibParser::test_clean_title --pdb
```

### Test Output Analysis
```bash
# Show test durations
python -m pytest --durations=10

# Show slowest tests
python -m pytest --durations=0

# Show test coverage details
python -m pytest --cov=. --cov-report=term-missing
```

## Test Maintenance

### Adding New Tests
1. Create test methods following naming convention: `test_feature_name`
2. Use appropriate fixtures from `conftest.py`
3. Add docstrings explaining test purpose
4. Include both positive and negative test cases
5. Update this documentation if adding new test categories

### Updating Tests
1. Update test data when adding new features
2. Ensure backward compatibility
3. Update fixtures if changing test data structure
4. Verify all tests still pass after changes

### Test Data Management
- Keep test data minimal but comprehensive
- Use realistic but anonymized data
- Include edge cases and error conditions
- Document any special test data requirements

## Performance Benchmarks

### Current Performance Targets
- **Small bibliography (5 entries)**: < 1 second
- **Medium bibliography (50 entries)**: < 5 seconds
- **Large bibliography (500 entries)**: < 30 seconds
- **Memory usage**: < 100MB for 500 entries
- **Test execution**: < 10 seconds for full suite

### Monitoring Performance
```bash
# Run performance tests
python -m pytest tests/test_integration.py::TestIntegration::test_large_bibliography_handling -v

# Profile memory usage
python -m pytest tests/test_integration.py::TestIntegration::test_large_bibliography_handling --profile

# Time individual tests
python -m pytest --durations=0
```

## Troubleshooting

### Common Issues
1. **Import errors**: Ensure all dependencies are installed
2. **Permission errors**: Check file permissions for test directories
3. **Unicode errors**: Ensure proper encoding in test files
4. **Memory issues**: Reduce test data size or increase system memory

### Debug Commands
```bash
# Check test discovery
python -m pytest --collect-only

# Run with maximum verbosity
python -m pytest -vvv

# Show test environment
python -m pytest --show-capture=all

# Run specific test with debug output
python -m pytest tests/test_bib_parser.py::TestBibParser::test_clean_title -vvv -s
```

This comprehensive test suite ensures the library generator is robust, reliable, and maintainable.
