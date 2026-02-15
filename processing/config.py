#!/usr/bin/env python3
"""
Configuration class for process_papers.py
Centralizes all constants, settings, and configuration values.
"""

import os
from pathlib import Path
from typing import Dict, List


def _project_root() -> Path:
    """Project root (repo root): directory containing processing/ and assets/. Resolved from this file so paths do not depend on cwd."""
    return Path(__file__).resolve().parent.parent


class Configuration:
    """Centralized configuration for the paper processing system.
    Paths are resolved relative to the project root (config file location) so they do not depend on current working directory.
    """
    _root = _project_root()

    # File paths and directories (absolute, so no phantom folders outside repo when run from different cwd)
    SOURCE_BIBTEX_FILE = str(_root / "_bibliography" / "Exported Items.bib")
    WORKING_BIBTEX_FILE = str(_root / "_bibliography" / "papers.bib")
    CACHE_FILE = str(_root / "_metadata_cache.json")

    # Fields safe to merge from existing in incremental mode (pipeline outputs / derived metadata only).
    # Do not include normal bibliographic fields (title, author, date, etc.); export always wins for those.
    PIPELINE_OUTPUT_FIELDS = (
        'preview', 'pdf', 'slides', 'agenda',
        'zip_archive', 'zip_file_count', 'zip_file_size_mb',
        'figures', 'photos',
    )

    # Output directories
    PDF_DIR = str(_root / "assets" / "pdf")
    PREVIEW_DIR = str(_root / "assets" / "img" / "publication_preview")
    IMAGES_DIR = str(_root / "assets" / "img" / "publications")
    AUDIO_DIR = str(_root / "assets" / "audio")
    ZIP_DIR = str(_root / "assets" / "zips")
    
    # File extensions
    PDF_EXTENSIONS = ['.pdf']
    IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif']
    PREVIEW_EXTENSIONS = ['.jpeg', '.jpg']
    
    # API settings
    SEMANTIC_SCHOLAR_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
    CROSSREF_URL = "https://api.crossref.org/works"
    API_TIMEOUT = 10
    API_RETRY_ATTEMPTS = 3
    
    # Thumbnail settings
    DEFAULT_THUMBNAIL_SIZE = "600x"
    THUMBNAIL_DENSITY = "300"
    THUMBNAIL_QUALITY = "95"
    MIN_THUMBNAIL_SIZE = 1000  # bytes
    
    # Text processing
    MAX_TITLE_LENGTH = 50
    MAX_JOURNAL_LENGTH = 30
    MAX_ABSTRACT_LENGTH = 500
    MAX_FILENAME_LENGTH = 120
    
    # Conservative filler words to remove from titles/filenames
    FILLER_WORDS = {
        # Articles & conjunctions
        'a', 'an', 'the', 'and', 'or', 'but', 'nor', 'so', 'yet',

        # Prepositions
        'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from',
        'up', 'about', 'into', 'through', 'during', 'before', 'after',
        'above', 'below', 'down', 'out', 'off', 'over', 'under',

        # Time/sequence fillers
        'again', 'further', 'then', 'once',

        # Auxiliaries / verbs
        'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did',
        'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'shall',

        # Pronouns
        'it', 'its', 'this', 'that', 'these', 'those',
        'their', 'his', 'her', 'our', 'your', 'my', 'me', 'we', 'they',

        # Demonstratives / determiners
        'such', 'same', 'other', 'another', 'each', 'every',
        'any', 'all', 'both', 'some', 'many', 'few',

        # Quantifiers
        'more', 'most', 'less', 'least', 'several',

        # Adverbs of degree/focus
        'very', 'much', 'quite', 'rather', 'even', 'just', 'only', 'still',

        # Conservative academic filler words
        'study', 'paper', 'article',
    }
    
    # Required fields for metadata completeness
    REQUIRED_METADATA_FIELDS = ['doi', 'abstract', 'keywords', 'journal']
    MIN_REQUIRED_FIELDS = 3
    
    # Text fields that need cleaning
    TEXT_FIELDS_TO_CLEAN = ['title', 'author', 'journal', 'publisher', 'institution', 'abstract', 'keywords', 'booktitle', 'type', 'series']
    FILENAME_FIELDS = ['title', 'author', 'journal', 'publisher', 'institution']
    
    # Presentation keywords
    PRESENTATION_KEYWORDS = ['presenter', 'speaker', 'prezi', 'miro', 'moderator']
    
    # Featured keywords
    FEATURED_KEYWORD = 'featured'
    
    # PDF metadata
    PDF_PRODUCER = "RENWeB"
    UPDATE_PDF_METADATA = True  # Update PDF metadata by default when processing papers
    PDF_METADATA_BACKUP_DIR = "../backups/pdf_metadata"
    PDF_METADATA_BACKUP_RETENTION_DAYS = 30
    
    # Image classification settings
    ENABLE_IMAGE_CONTENT_ANALYSIS = False  # Enable PIL-based image analysis (slower but more accurate)
    IMAGE_CLASSIFICATION_VERBOSE = False  # Print classification details during processing
    
    # Error messages
    ERROR_MESSAGES = {
        'file_not_found': "❌ Error: Source file {} not found!",
        'dependency_missing': "❌ Exiting due to missing dependencies.",
        'api_error': "⚠️  Error fetching from {}: {}",
        'file_copy_error': "❌ Error copying {}: {}",
        'thumbnail_error': "❌ Error generating thumbnail: {}",
        'metadata_error': "❌ Error updating PDF metadata: {}",
        'bibtex_error': "❌ Error reading/writing BibTeX file: {}"
    }
    
    # Success messages
    SUCCESS_MESSAGES = {
        'file_copied': "✅ Copied: {} -> {}",
        'thumbnail_generated': "✅ Generated thumbnail: {}",
        'metadata_updated': "✅ Updated PDF metadata: {}",
        'cache_loaded': "📚 Loaded metadata cache with {} entries",
        'cache_saved': "💾 Saved metadata cache with {} entries"
    }
    
    @classmethod
    def ensure_directories_exist(cls) -> None:
        """Ensure all required directories exist."""
        directories = [cls.PDF_DIR, cls.PREVIEW_DIR, cls.IMAGES_DIR, cls.AUDIO_DIR, cls.ZIP_DIR]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    @classmethod
    def ensure_pdf_metadata_backup_dir_exists(cls) -> None:
        """Ensure PDF metadata backup directory exists."""
        os.makedirs(cls.PDF_METADATA_BACKUP_DIR, exist_ok=True)
    
    @classmethod
    def get_backup_filename(cls, original_file: str) -> str:
        """Generate a backup filename with timestamp."""
        import time
        base_name = Path(original_file).stem
        extension = Path(original_file).suffix
        return f"{base_name}_backup_{int(time.time())}{extension}"
    
    @classmethod
    def is_presentation(cls, keywords: str) -> bool:
        """Check if keywords indicate a presentation."""
        if not keywords:
            return False
        keywords_lower = keywords.lower()
        return any(keyword in keywords_lower for keyword in cls.PRESENTATION_KEYWORDS)
    
    @classmethod
    def is_featured(cls, keywords: str) -> bool:
        """Check if keywords contain 'featured'."""
        if not keywords:
            return False
        return cls.FEATURED_KEYWORD in keywords.lower()
    
    @classmethod
    def get_required_dependencies(cls) -> List[str]:
        """Get list of required dependencies."""
        return ['PyPDF2', 'requests']
    
    @classmethod
    def get_optional_dependencies(cls) -> List[str]:
        """Get list of optional dependencies."""
        return ['ImageMagick']
