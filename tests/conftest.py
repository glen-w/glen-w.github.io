#!/usr/bin/env python3
"""
Global pytest configuration and fixtures for the paper processing test suite.
Provides shared fixtures and configuration for all test modules.
"""

import pytest
import tempfile
import os
import sys
import shutil
from pathlib import Path
from typing import Dict, Any, Generator

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "processing"))

from processing.config import Configuration


@pytest.fixture(scope="session")
def project_root_path():
    """Get the project root path."""
    return project_root


@pytest.fixture(scope="session")
def processing_path():
    """Get the processing directory path."""
    return project_root / "processing"


@pytest.fixture
def temp_dir(tmp_path) -> Path:
    """Create a temporary directory for testing."""
    return tmp_path


@pytest.fixture
def temp_bibtex_file(temp_dir) -> Path:
    """Create a temporary BibTeX file for testing."""
    bibtex_file = temp_dir / "test.bib"
    bibtex_file.write_text("")
    return bibtex_file


@pytest.fixture
def sample_bibtex_content() -> str:
    """Sample BibTeX content for testing."""
    return """@article{test2023,
    title = {Test Title},
    author = {Test Author},
    year = {2023},
    journal = {Test Journal}
}

@book{testbook2023,
    title = {Test Book},
    author = {Book Author},
    year = {2023},
    publisher = {Test Publisher}
}"""


@pytest.fixture
def complex_bibtex_content() -> str:
    """Complex BibTeX content with various edge cases."""
    return """@article{complex2023,
    title = {Complex Title with {nested} braces and special chars @#$%^&*()},
    author = {Author, First and Author, Second},
    year = {2023},
    journal = {Journal of {Complex} Science},
    doi = {10.1000/complex123},
    url = {https://example.com/complex},
    abstract = {This is a very long abstract with multiple sentences. It contains various punctuation marks and might cause issues when processing. The abstract should be handled correctly without breaking BibTeX syntax.},
    keywords = {complex, testing, validation}
}

@inproceedings{conf2023,
    title = {Conference Paper with {Multiple} {Nested} {Braces}},
    author = {Smith, John and Doe, Jane and Brown, Bob},
    booktitle = {Proceedings of the {International} {Conference} on {Testing}},
    year = {2023},
    pages = {123--456},
    publisher = {Test Publisher}
}"""


@pytest.fixture
def malformed_bibtex_content() -> str:
    """Malformed BibTeX content for testing error handling."""
    return """@article{malformed2023,
    title = {Malformed Title
    author = {Test Author},,
    year = {2023},
    file = {test.pdf:/path/to/test.pdf:application/pdf; image.jpg:/path/to/image.jpg:image/jpeg},
    pdf = {54439519274_cf052b44d1_k.pdf},
    preview = {nonexistent.jpg}
}"""


@pytest.fixture
def zotero_export_content() -> str:
    """Sample Zotero export content with file fields."""
    return """@article{zotero2023,
    title = {Zotero Export Test},
    author = {Zotero, Test},
    year = {2023},
    file = {test.pdf:/path/to/test.pdf:application/pdf; thumbnail.png:/path/to/thumbnail.png:image/png; image.jpg:/path/to/image.jpg:image/jpeg},
    keywords = {zotero, export, test}
}"""


@pytest.fixture
def config() -> Configuration:
    """Create a test configuration instance."""
    return Configuration()


@pytest.fixture
def bibtex_processor(config):
    """Create BibTeX processor for testing."""
    from processing.core.text_processor import TextProcessor
    text_processor = TextProcessor(config)
    from processing.core.bibtex_processor import BibTeXProcessor
    return BibTeXProcessor(config, text_processor)


@pytest.fixture
def validator(config):
    """Create enhanced validator for testing."""
    from processing.validation.enhanced_validator import EnhancedValidator
    return EnhancedValidator(config)


@pytest.fixture
def test_config_dict() -> Dict[str, Any]:
    """Test configuration dictionary."""
    return {
        'BIBTEX_FILE': '_bibliography/papers.bib',
        'SOURCE_BIBTEX_FILE': '_bibliography/Exported Items.bib',
        'PREVIEW_DIR': 'assets/previews',
        'PDF_DIR': 'assets/pdfs',
        'PHOTOS_DIR': 'assets/photos',
        'FIGURES_DIR': 'assets/figures',
        'TEXT_FIELDS_TO_CLEAN': ['title', 'shorttitle', 'booktitle', 'journal', 'publisher'],
        'THUMBNAIL_SIZE': '600x',
        'TEST_MODE': True
    }


@pytest.fixture
def mock_file_system(temp_dir, test_config_dict):
    """Create a mock file system structure for testing."""
    # Create directory structure
    dirs = [
        'assets/previews',
        'assets/pdfs', 
        'assets/photos',
        'assets/figures',
        '_bibliography',
        '_library'
    ]
    
    for dir_path in dirs:
        (temp_dir / dir_path).mkdir(parents=True, exist_ok=True)
    
    # Create some test files
    test_files = {
        'assets/previews/test.jpg': b'fake image data',
        'assets/pdfs/test.pdf': b'fake pdf data',
        'assets/photos/photo1.jpg': b'fake photo data',
        'assets/figures/figure1.png': b'fake figure data',
        '_bibliography/papers.bib': b'@article{test, title = {Test}}',
        '_bibliography/Exported Items.bib': b'@article{export, title = {Export}}'
    }
    
    for file_path, content in test_files.items():
        (temp_dir / file_path).write_bytes(content)
    
    return temp_dir


@pytest.fixture
def sample_pdf_metadata() -> Dict[str, Any]:
    """Sample PDF metadata for testing."""
    return {
        'title': 'Test PDF Title',
        'author': 'Test PDF Author',
        'subject': 'Test Subject',
        'creator': 'Test Creator',
        'producer': 'Test Producer',
        'creation_date': '2023-01-01T00:00:00Z',
        'modification_date': '2023-01-01T00:00:00Z',
        'pages': 10
    }


@pytest.fixture
def sample_image_metadata() -> Dict[str, Any]:
    """Sample image metadata for testing."""
    return {
        'width': 1920,
        'height': 1080,
        'format': 'JPEG',
        'mode': 'RGB',
        'size': (1920, 1080)
    }


@pytest.fixture(autouse=True)
def cleanup_temp_files():
    """Clean up temporary files after each test."""
    yield
    # Cleanup is handled by pytest's tmp_path fixture


@pytest.fixture
def mock_bibtexparser():
    """Mock bibtexparser for testing when library is not available."""
    class MockBibTexParser:
        def __init__(self, *args, **kwargs):
            pass
        
        def parse(self, content):
            class MockEntries:
                def __init__(self, entries):
                    self.entries = entries
            
            # Simple mock parsing
            entries = []
            if '@article' in content:
                entries.append({'ID': 'test', 'ENTRYTYPE': 'article', 'title': 'Test'})
            return MockEntries(entries)
    
    return MockBibTexParser


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "bibtex_syntax: mark test as BibTeX syntax validation test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "requires_bibtexparser: mark test as requiring bibtexparser library"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on file location."""
    for item in items:
        # Add markers based on file location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
        
        # Add bibtex_syntax marker for syntax validation tests
        if "syntax" in str(item.fspath) or "bibtex" in str(item.fspath):
            item.add_marker(pytest.mark.bibtex_syntax)
