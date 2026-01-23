"""
Paper Processing Pipeline Package

Main package for processing academic papers from Zotero exports.
"""

from processing.config import Configuration
from processing.core.paper_processor import PaperProcessor
from processing.core.post_processor import PostProcessor

__all__ = [
    'Configuration',
    'PaperProcessor',
    'PostProcessor',
]
