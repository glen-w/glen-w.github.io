"""
Utility modules for the paper processing pipeline.
"""

from processing.utils.field_cleaner import FieldCleaner
from processing.utils.field_remover import remove_fields_from_bibtex
from processing.utils.file_field_manager import FileFieldManager
from processing.utils.file_field_parser import FileEntry, FileFieldParser
from processing.utils.file_manager import FileManager
from processing.utils.image_classifier import ImageClassifier
from processing.utils.metadata_fetcher import MetadataFetcher

__all__ = [
    'FieldCleaner',
    'remove_fields_from_bibtex',
    'FileFieldManager',
    'FileEntry',
    'FileFieldParser',
    'FileManager',
    'ImageClassifier',
    'MetadataFetcher',
]
