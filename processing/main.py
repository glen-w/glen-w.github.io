#!/usr/bin/env python3
"""
Main script to process papers from Zotero export with modular architecture.
This version uses separate modules for different processing steps with enhanced validation.

IMPORTANT: NEVER edit _bibliography/papers.bib directly! This file gets overwritten
on every new Zotero export. All fixes must be made to this script and its modules
to ensure they are applied during processing.

The script now uses enhanced validation by default for robust error detection and
automatic fixing of common BibTeX issues during processing.
"""

import argparse
import sys
import os

# Add the processing directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Configuration
from core.paper_processor import PaperProcessor
from core.post_processor import PostProcessor
from validation.simple_validator import SimpleValidator
from validation.enhanced_validator import EnhancedValidator
from utils.field_remover import remove_fields_from_bibtex


def main():
    """Main entry point with modular approach."""
    parser = argparse.ArgumentParser(description='Process papers.bib with modular approach')
    
    # Processing options
    parser.add_argument('--thumbnail-size', default='600x', 
                       help='Thumbnail size in format WIDTHxHEIGHT or WIDTHx for auto height (default: 600x)')
    parser.add_argument('--bibtex-file', default='../_bibliography/Exported Items.bib',
                       help='Path to source BibTeX file from Zotero (default: ../_bibliography/Exported Items.bib)')
    parser.add_argument('--regenerate', action='store_true',
                       help='Delete all existing PDFs and thumbnails, then regenerate everything')
    parser.add_argument('--force', action='store_true',
                       help='Force reprocessing of entries even if they already have tags')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output for detailed processing information')
    parser.add_argument('--test', action='store_true',
                       help='Test mode: process only first 5 entries for quick testing')
    parser.add_argument('--test-count', type=int, default=5,
                       help='Number of entries to process in test mode (default: 5)')
    parser.add_argument('--update-pdf-metadata', action='store_true',
                       help='Update PDF metadata with BibTeX information (default: False, opt-in feature)')
    parser.add_argument('--no-pdf-metadata', action='store_true',
                       help='Explicitly disable PDF metadata updating (overrides config and --update-pdf-metadata)')
    
    # Post-processing options
    parser.add_argument('--clean-file-field', action='store_true',
                       help='Clean file field from processed files after processing')
    parser.add_argument('--remove-file-field', action='store_true', default=True,
                       help='Remove file field entirely from processed entries (default: True, use --keep-file-field to disable)')
    parser.add_argument('--keep-file-field', action='store_true',
                       help='Keep file field in processed entries (overrides default removal)')
    parser.add_argument('--remove-fields', nargs='+',
                       help='Remove specific fields from all entries after processing')
    
    # Validation options
    parser.add_argument('--validate', action='store_true', default=True,
                       help='Run validation after processing (default: True)')
    parser.add_argument('--no-validate', action='store_true',
                       help='Skip validation')
    parser.add_argument('--simple-validate', action='store_true',
                       help='Use simple validator instead of enhanced validator (enhanced is default)')
    parser.add_argument('--enhanced-validate', action='store_true', default=True,
                       help='Use enhanced validator with detailed issue reporting (default: True, can be omitted)')
    
    # Utility options
    parser.add_argument('--clean-only', action='store_true',
                       help='Only run post-processing cleanup, skip main processing')
    parser.add_argument('--remove-only', action='store_true',
                       help='Only remove specified fields, skip main processing')
    parser.add_argument('--library-items', action='store_true',
                       help='Only generate library items, skip main processing')
    parser.add_argument('--dynamic-filters', action='store_true',
                       help='Only generate dynamic filters, skip main processing')
    
    args = parser.parse_args()
    
    # Create configuration
    config = Configuration()
    
    # Handle utility-only modes
    if args.clean_only:
        return run_cleanup_only(config, args)
    elif args.remove_only:
        return run_removal_only(args)
    elif args.library_items:
        return run_library_items_only(args)
    elif args.dynamic_filters:
        return run_dynamic_filters_only(args)
    
    # Run main processing
    success = run_main_processing(config, args)
    if not success:
        return 1
    
    # Run post-processing cleanup
    # Note: remove_file_field defaults to True unless --keep-file-field is specified
    should_remove_file_field = args.remove_file_field and not args.keep_file_field
    if args.clean_file_field or should_remove_file_field or args.remove_fields:
        success = run_post_processing(config, args)
        if not success:
            return 1
    
    # Run validation
    if args.validate and not args.no_validate:
        success = run_validation(config, args)
        if not success:
            return 1
    
    # Run dynamic filters generation
    success = run_dynamic_filters_generation(args)
    if not success:
        print("⚠️  Dynamic filters generation failed, but main processing completed successfully")
        return 0
    
    # Run library page generation
    success = run_library_generation(args)
    if not success:
        print("⚠️  Library generation failed, but main processing completed successfully")
        return 0
    
    # Run mapping generation
    success = run_mapping_generation(args)
    if not success:
        print("⚠️  Mapping generation failed, but main processing completed successfully")
        return 0
    
    print("\n✅ All processing completed successfully!")
    return 0


def run_main_processing(config: Configuration, args) -> bool:
    """Run the main paper processing."""
    print("📚 Starting main paper processing...")
    
    # Determine PDF metadata update setting
    # Default to config value, but allow CLI override
    update_pdf_metadata = config.UPDATE_PDF_METADATA
    if args.no_pdf_metadata:
        update_pdf_metadata = False
    elif args.update_pdf_metadata:
        update_pdf_metadata = True
    
    processor = PaperProcessor(config)
    
    try:
        processor.process_papers(
            source_bibtex_file=args.bibtex_file,
            regenerate=args.regenerate,
            force=args.force,
            update_metadata=True,
            thumbnail_size=args.thumbnail_size,
            test_mode=args.test,
            test_count=args.test_count,
            verbose=args.verbose,
            force_refetch_metadata=False,
            rename_urls=True,
            rename_only=False,
            update_pdf_metadata=update_pdf_metadata
        )
        return True
    except Exception as e:
        print(f"❌ Main processing failed: {e}")
        return False


def run_post_processing(config: Configuration, args) -> bool:
    """Run post-processing cleanup."""
    print("\n🧹 Starting post-processing cleanup...")
    
    processor = PostProcessor(config)
    output_file = '../_bibliography/papers.bib'
    
    if not os.path.exists(output_file):
        print(f"❌ Output file not found: {output_file}")
        return False
    
    try:
        if args.clean_file_field:
            success = processor.clean_file_field_only(output_file)
            if not success:
                return False
        
        # Remove file field by default unless --keep-file-field is specified
        if args.remove_file_field and not args.keep_file_field:
            success = processor.remove_file_field_entirely(output_file)
            if not success:
                return False
        
        if args.remove_fields:
            success = processor.remove_specific_fields(output_file, args.remove_fields)
            if not success:
                return False
        
        return True
    except Exception as e:
        print(f"❌ Post-processing failed: {e}")
        return False


def run_validation(config: Configuration, args) -> bool:
    """Run validation."""
    print("\n🔍 Running validation...")
    
    output_file = '../_bibliography/papers.bib'
    
    if not os.path.exists(output_file):
        print(f"❌ Output file not found: {output_file}")
        return False
    
    try:
        if args.simple_validate:
            # Use simple validator if explicitly requested
            validator = SimpleValidator(config)
            results = validator.validate_after_processing(output_file)
            validator.print_validation_summary(results)
            all_passed = results.get('valid', False)
        else:
            # Use enhanced validator by default
            validator = EnhancedValidator(config)
            results = validator.validate_bibtex_file(output_file)
            # Enhanced validator prints its own summary
            # Get the validation summary for checking
            summary = validator.get_validation_summary()
            all_passed = summary.get('all_passed', False)
        
        if not all_passed:
            print("\n❌ Validation failed")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False


def run_cleanup_only(config: Configuration, args) -> int:
    """Run only post-processing cleanup."""
    print("🧹 Running cleanup only...")
    
    success = run_post_processing(config, args)
    if not success:
        return 1
    
    # Run validation
    if args.validate and not args.no_validate:
        success = run_validation(config, args)
        if not success:
            return 1
    
    print("\n✅ Cleanup completed successfully!")
    return 0


def run_removal_only(args) -> int:
    """Run only field removal."""
    print("🗑️  Running field removal only...")
    
    if not args.remove_fields:
        print("❌ --remove-fields is required for removal-only mode")
        return 1
    
    output_file = '../_bibliography/papers.bib'
    if not os.path.exists(output_file):
        print(f"❌ Output file not found: {output_file}")
        return 1
    
    success = remove_fields_from_bibtex(output_file, args.remove_fields)
    if not success:
        return 1
    
    print("\n✅ Field removal completed successfully!")
    return 0


def run_library_items_only(args) -> int:
    """Run only library items generation."""
    print("📖 Starting library items generation...")
    
    success = run_library_generation(args)
    if not success:
        print("❌ Library items generation failed")
        return 1
    
    print("\n✅ Library items generation completed successfully!")
    return 0


def run_library_generation(args) -> bool:
    """Run library page generation."""
    print("\n📖 Starting library page generation...")
    
    try:
        # Import the library generator
        from library.generator import LibraryPageGenerator
        
        # Create generator with same test mode as process_papers
        bib_file = args.bibtex_file or '../_bibliography/papers.bib'
        generator = LibraryPageGenerator(
            bib_file=bib_file,
            output_dir='../_library',
            test_mode=args.test
        )
        
        # Run the generation
        generator.run()
        return True
        
    except Exception as e:
        print(f"❌ Library generation failed: {e}")
        return False


def run_dynamic_filters_generation(args) -> bool:
    """Run dynamic filters generation as part of main processing."""
    print("\n🏷️  Starting dynamic filters generation...")
    
    try:
        # Import the dynamic filters generator
        from library.dynamic_filters import DynamicFiltersGenerator
        from library.bib_parser import BibParser
        import bibtexparser
        from bibtexparser.bparser import BibTexParser
        from bibtexparser.customization import convert_to_unicode
        import unicodedata
        
        # Create a safe wrapper for convert_to_unicode that handles the combining() error
        def safe_convert_to_unicode(record):
            """Wrapper that handles Unicode conversion errors gracefully."""
            try:
                return convert_to_unicode(record)
            except (TypeError, ValueError) as e:
                # If there's an error with Unicode conversion (e.g., combining() issue),
                # return the record as-is. This is safe for tag extraction.
                if "combining()" in str(e):
                    # Log but don't fail - we can still extract tags without Unicode conversion
                    return record
                raise
        
        # Load bibliography entries from processed file
        bib_file = '../_bibliography/papers.bib'
        with open(bib_file, 'r', encoding='utf-8') as f:
            parser = BibTexParser(common_strings=True)
            parser.customization = safe_convert_to_unicode
            bib_database = bibtexparser.load(f, parser=parser)
        
        # Generate dynamic filters
        project_root = '../'
        filters_generator = DynamicFiltersGenerator(project_root)
        filters_generator.generate_filters(bib_database.entries)
        
        return True
        
    except Exception as e:
        print(f"❌ Dynamic filters generation failed: {e}")
        return False


def run_dynamic_filters_only(args) -> bool:
    """Run only dynamic filters generation."""
    print("\n🏷️  Starting dynamic filters generation...")
    
    try:
        # Import the dynamic filters generator
        from library.dynamic_filters import DynamicFiltersGenerator
        from library.bib_parser import BibParser
        import bibtexparser
        from bibtexparser.bparser import BibTexParser
        from bibtexparser.customization import convert_to_unicode
        
        # Create a safe wrapper for convert_to_unicode that handles the combining() error
        def safe_convert_to_unicode(record):
            """Wrapper that handles Unicode conversion errors gracefully."""
            try:
                return convert_to_unicode(record)
            except (TypeError, ValueError) as e:
                # If there's an error with Unicode conversion (e.g., combining() issue),
                # return the record as-is. This is safe for tag extraction.
                if "combining()" in str(e):
                    # Log but don't fail - we can still extract tags without Unicode conversion
                    return record
                raise
        
        # Load bibliography from processed file
        bib_file = '../_bibliography/papers.bib'
        with open(bib_file, 'r', encoding='utf-8') as f:
            parser = BibTexParser(common_strings=True)
            parser.customization = safe_convert_to_unicode
            bib_database = bibtexparser.load(f, parser=parser)
        
        entries = bib_database.entries
        print(f"Loaded {len(entries)} entries from {bib_file}")
        
        # Filter for test mode if needed
        if args.test:
            # Sort by year and take the 5 most recent
            entries_with_year = []
            for entry in entries:
                year = entry.get('year', '0000')
                try:
                    year_int = int(year)
                except (ValueError, TypeError):
                    year_int = 0
                entries_with_year.append((year_int, entry))
            
            entries_with_year.sort(key=lambda x: x[0], reverse=True)
            entries = [entry for year, entry in entries_with_year[:5]]
            print(f"Test mode: Processing {len(entries)} most recent entries")
        
        # Generate filters
        generator = DynamicFiltersGenerator('..')
        generator.generate_filters(entries)
        return True
        
    except Exception as e:
        print(f"❌ Dynamic filters generation failed: {e}")
        return False


def run_mapping_generation(args) -> bool:
    """Run mapping generation."""
    print("\n🗺️  Starting mapping generation...")
    
    try:
        # Import the mapping processor
        from mapping.processor import MappingProcessor
        
        # Create processor with same test mode as process_papers
        # If regenerate mode is enabled, also refresh the geocoding cache
        processor = MappingProcessor(
            bib_file_path='../_bibliography/papers.bib',
            output_dir='../assets/mapping',
            test_mode=args.test,
            refresh_cache=args.regenerate,  # Refresh cache if in regenerate mode
            cache_only=False      # Default to processing all locations
        )
        
        # Run the processing
        success = processor.process_locations()
        return success
        
    except Exception as e:
        print(f"❌ Mapping generation failed: {e}")
        return False


if __name__ == "__main__":
    sys.exit(main())
