#!/usr/bin/env python3
"""
Library Page Generator

Automatically generates individual markdown pages for each bibliography item
with rich features including share buttons, social posting, PDF embedding, and galleries.

Usage:
    python generate_library_pages.py [--test] [--bib-file PATH] [--output-dir PATH]
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
import yaml
from slugify import slugify
import re

# Add the processing directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from library.bib_parser import BibParser
from library.content_generator import ContentGenerator
from library.dynamic_filters import DynamicFiltersGenerator


class LibraryPageGenerator:
    """Main class for generating library pages from BibTeX files."""
    
    def __init__(self, bib_file=None, output_dir=None, test_mode=False):
        """Initialize the generator.
        
        Args:
            bib_file (str): Path to the BibTeX file
            output_dir (str): Output directory for generated pages
            test_mode (bool): If True, only process 5 latest items with location
        """
        # Get the project root directory (two levels up from this script)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        self.bib_file = bib_file or os.path.join(project_root, "_bibliography", "papers.bib")
        self.output_dir = output_dir or os.path.join(project_root, "_library")
        self.test_mode = test_mode
        
        # Initialize components
        self.bib_parser = BibParser()
        self.content_generator = ContentGenerator()
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
    
    def load_bibliography(self):
        """Load and parse the BibTeX file."""
        # Create a safe wrapper for convert_to_unicode that handles the combining() error
        def safe_convert_to_unicode(record):
            """Wrapper that handles Unicode conversion errors gracefully."""
            try:
                return convert_to_unicode(record)
            except (TypeError, ValueError) as e:
                # If there's an error with Unicode conversion (e.g., combining() issue),
                # return the record as-is. This is safe for library page generation.
                if "combining()" in str(e):
                    # Log but don't fail - we can still generate pages without Unicode conversion
                    return record
                raise
        
        try:
            with open(self.bib_file, 'r', encoding='utf-8') as bibtex_file:
                parser = BibTexParser(common_strings=True)
                parser.customization = safe_convert_to_unicode
                bib_database = bibtexparser.load(bibtex_file, parser=parser)
            
            print(f"Loaded {len(bib_database.entries)} entries from {self.bib_file}")
            return bib_database.entries
            
        except FileNotFoundError:
            print(f"Error: BibTeX file not found: {self.bib_file}")
            sys.exit(1)
        except Exception as e:
            print(f"Error loading BibTeX file: {e}")
            sys.exit(1)
    
    def filter_test_entries(self, entries):
        """Filter entries for test mode - get 5 most recent entries."""
        if not self.test_mode:
            return entries
        
        # Sort by year (descending) and take the first 5
        def get_year(entry):
            year = entry.get('year', '0')
            try:
                return int(year)
            except (ValueError, TypeError):
                return 0
        
        sorted_entries = sorted(entries, key=get_year, reverse=True)
        test_entries = sorted_entries[:5]
        
        print(f"Test mode: Processing {len(test_entries)} most recent entries")
        for entry in test_entries:
            title = entry.get('title', 'Untitled')
            year = entry.get('year', 'Unknown')
            entry_type = entry.get('type', 'Unknown')
            print(f"  - {title} ({year}) - {entry_type}")
        
        return test_entries
    
    def generate_filename(self, entry):
        """Generate filename for the markdown page using proper accent handling."""
        from core.text_processor import TextProcessor
        from config import Configuration
        
        # Use the same text processing logic as PDF generation
        config = Configuration()
        text_processor = TextProcessor(config)
        
        title = entry.get('title', 'untitled')
        if not title or title.strip() == '':
            title = 'untitled'
        
        # First remove filler words to make title more concise
        condensed_title = text_processor.remove_filler_words(title)
        
        # Use the new slugify method with proper accent handling
        clean_title = text_processor.slugify_title(condensed_title, max_length=70)
        
        # Generate filename
        filename = f"{clean_title}.md"
        
        return filename
    
    def generate_page(self, entry):
        """Generate a single library page."""
        filename = self.generate_filename(entry)
        filepath = os.path.join(self.output_dir, filename)
        
        # Generate content
        front_matter = self.content_generator.generate_front_matter(entry)
        content = self.content_generator.generate_content(entry)
        
        # Write the file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(front_matter)
            f.write('\n\n')
            f.write(content)
        
        return filepath
    
    def run(self):
        """Run the generation process."""
        print("Starting library page generation...")
        print(f"Mode: {'TEST' if self.test_mode else 'FULL'}")
        print(f"BibTeX file: {self.bib_file}")
        print(f"Output directory: {self.output_dir}")
        print("-" * 50)
        
        # Load bibliography
        entries = self.load_bibliography()
        
        # Filter for test mode if needed
        entries = self.filter_test_entries(entries)
        
        if not entries:
            print("No entries to process")
            return
        
        # Generate pages
        generated_files = []
        for i, entry in enumerate(entries, 1):
            try:
                filepath = self.generate_page(entry)
                generated_files.append(filepath)
                title = entry.get('title', 'Untitled')
                print(f"[{i}/{len(entries)}] Generated: {os.path.basename(filepath)} - {title}")
            except Exception as e:
                print(f"Error generating page for {entry.get('title', 'Unknown')}: {e}")
                continue
        
        # Generate dynamic filters
        project_root = os.path.dirname(os.path.dirname(self.output_dir))
        filters_generator = DynamicFiltersGenerator(project_root)
        filters_generator.generate_filters(entries)
        
        print("-" * 50)
        print(f"Generation complete! Created {len(generated_files)} pages.")
        
        if self.test_mode:
            print("\nTest mode summary:")
            print("- Only processed 5 most recent entries")
            print("- Use without --test flag to process all entries")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate library pages from BibTeX files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_library_pages.py --test
  python generate_library_pages.py --bib-file custom.bib --output-dir _custom_library
  python generate_library_pages.py --test --bib-file "_bibliography/Exported Items.bib"
        """
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test mode: only process 5 most recent entries'
    )
    
    parser.add_argument(
        '--bib-file',
        type=str,
        help='Path to BibTeX file (default: _bibliography/papers.bib)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        help='Output directory for generated pages (default: _library)'
    )
    
    args = parser.parse_args()
    
    # Create generator and run
    generator = LibraryPageGenerator(
        bib_file=args.bib_file,
        output_dir=args.output_dir,
        test_mode=args.test
    )
    
    generator.run()


if __name__ == "__main__":
    main()
