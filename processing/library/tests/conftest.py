"""
Pytest configuration and fixtures for library generator tests.
"""

import pytest
import tempfile
import os
import shutil
from pathlib import Path

from processing.library.generator import LibraryPageGenerator
from processing.library.bib_parser import BibParser
from processing.library.content_generator import ContentGenerator


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_bib_content():
    """Sample BibTeX content for testing."""
    return """
@article{testArticle2023,
    title = {Test Article Title},
    author = {Smith, John and Doe, Jane},
    journal = {Test Journal},
    year = {2023},
    month = {jan},
    abstract = {This is a test abstract for the article.},
    keywords = {test, example, research},
    doi = {10.1000/test123},
    url = {https://example.com/test-article}
}

@inproceedings{testConference2024,
    title = {Test Conference Paper},
    author = {Johnson, Bob},
    booktitle = {International Conference on Testing},
    year = {2024},
    month = {mar},
    address = {Test City, Test Country},
    abstract = {This is a test abstract for the conference paper.},
    keywords = {conference, testing, example}
}

@techreport{testReport2025,
    title = {Test Technical Report},
    author = {Wilson, Alice},
    institution = {Test Institute},
    year = {2025},
    month = {apr},
    abstract = {This is a test abstract for the technical report.},
    keywords = {report, technical, example},
    pdf = {test-report-2025.pdf}
}

@misc{testMisc2022,
    title = {Test Miscellaneous Item},
    author = {Brown, Charlie},
    year = {2022},
    month = {dec},
    note = {This is a test note with additional information.},
    keywords = {misc, example, test}
}

@misc{testBlog2023,
    title = {Test Blog Post},
    author = {Davis, Emma},
    year = {2023},
    month = {jun},
    url = {https://example.com/blog/test-post},
    abstract = {This is a test blog post abstract.},
    keywords = {blog, example, test}
}
"""


@pytest.fixture
def sample_bib_file(temp_dir, sample_bib_content):
    """Create a sample BibTeX file for testing."""
    bib_file = os.path.join(temp_dir, "test.bib")
    with open(bib_file, 'w', encoding='utf-8') as f:
        f.write(sample_bib_content)
    return bib_file


@pytest.fixture
def generator(temp_dir, sample_bib_file):
    """Create a LibraryPageGenerator instance for testing."""
    return LibraryPageGenerator(
        bib_file=sample_bib_file,
        output_dir=os.path.join(temp_dir, "_library"),
        test_mode=False
    )


@pytest.fixture
def test_generator(temp_dir, sample_bib_file):
    """Create a LibraryPageGenerator instance in test mode."""
    return LibraryPageGenerator(
        bib_file=sample_bib_file,
        output_dir=os.path.join(temp_dir, "_library"),
        test_mode=True
    )


@pytest.fixture
def bib_parser():
    """Create a BibParser instance for testing."""
    return BibParser()


@pytest.fixture
def content_generator():
    """Create a ContentGenerator instance for testing."""
    return ContentGenerator()


@pytest.fixture
def sample_entry():
    """Sample BibTeX entry for testing."""
    return {
        'ID': 'testArticle2023',
        'type': 'article',
        'title': 'Test Article Title',
        'author': 'Smith, John and Doe, Jane',
        'journal': 'Test Journal',
        'year': '2023',
        'month': 'jan',
        'abstract': 'This is a test abstract for the article.',
        'keywords': 'test, example, research',
        'doi': '10.1000/test123',
        'url': 'https://example.com/test-article'
    }
