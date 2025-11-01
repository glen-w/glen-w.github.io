#!/usr/bin/env python3
"""
Refactored script to process papers from Zotero export:
1. Copy _bibliography/Exported Items.bib to _bibliography/papers.bib
2. Parse BibTeX entries with proper nested brace handling
3. Copy PDF files to assets/pdf with renamed filenames
4. Generate thumbnail previews for each PDF
5. Add pdf/slides and preview tags to BibTeX entries (slides for presentations, pdf for papers)
6. Add dimensions=true and altmetric=true tags to entries with DOI for citation tracking
7. Update PDF metadata with BibTeX information
8. Support regenerate mode to clean existing files and start fresh

This is the refactored version with improved maintainability and robustness.
"""

import argparse
import sys
import os
from config import Configuration
from paper_processor import PaperProcessor
from bibtex_validator import BibTeXValidator
from validation_checker import ValidationChecker


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Process papers.bib, generate PDF thumbnails, and add tags')
    parser.add_argument('--thumbnail-size', default='600x', 
                       help='Thumbnail size in format WIDTHxHEIGHT or WIDTHx for auto height (default: 600x)')
    parser.add_argument('--bibtex-file', default='_bibliography/Exported Items.bib',
                       help='Path to source BibTeX file from Zotero (default: _bibliography/Exported Items.bib)')
    parser.add_argument('--regenerate', action='store_true',
                       help='Delete all existing PDFs and thumbnails, then regenerate everything')
    parser.add_argument('--force', action='store_true',
                       help='Force reprocessing of entries even if they already have tags')
    parser.add_argument('--update-metadata', action='store_true', default=True,
                       help='Update PDF metadata with BibTeX information (default: True)')
    parser.add_argument('--no-metadata', action='store_true',
                       help='Skip PDF metadata updating')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output for detailed processing information')
    parser.add_argument('--test', action='store_true',
                       help='Test mode: process only first 5 entries for quick testing')
    parser.add_argument('--test-count', type=int, default=5,
                       help='Number of entries to process in test mode (default: 5)')
    parser.add_argument('--force-refetch-metadata', action='store_true',
                       help='Force re-fetching of metadata from external APIs, ignoring cache and existing fields')
    parser.add_argument('--clear-cache', action='store_true',
                       help='Clear the metadata cache before processing')
    parser.add_argument('--rename-urls', action='store_true', default=True,
                       help='Rename "url" fields to "website" fields for Jekyll compatibility (default: True)')
    parser.add_argument('--no-rename-urls', action='store_true',
                       help='Skip renaming "url" fields to "website" fields')
    parser.add_argument('--validate-bibtex', action='store_true', default=True,
                       help='Validate BibTeX syntax after processing (default: True)')
    parser.add_argument('--no-validate', action='store_true',
                       help='Skip BibTeX validation')
    parser.add_argument('--install-validation-tools', action='store_true',
                       help='Show installation instructions for validation tools')
    parser.add_argument('--rename-only', action='store_true',
                       help='Only perform PDF/image renaming and copying, skip metadata fetching and BibTeX processing')
    parser.add_argument('--validate', action='store_true', default=True,
                       help='Run comprehensive validation checks after processing (default: True)')
    parser.add_argument('--no-comprehensive-validate', action='store_true',
                       help='Skip comprehensive validation checks')
    
    args = parser.parse_args()
    
    # Create configuration and processor
    config = Configuration()
    processor = PaperProcessor(config)
    
    # Handle metadata updating preference
    update_metadata = args.update_metadata and not args.no_metadata
    
    # Handle URL renaming preference
    rename_urls = args.rename_urls and not args.no_rename_urls
    
    # Handle validation preference
    validate_bibtex = args.validate_bibtex and not args.no_validate
    
    # Handle comprehensive validation preference
    run_validation = args.validate and not args.no_comprehensive_validate
    
    # Show installation instructions if requested
    if args.install_validation_tools:
        validator = BibTeXValidator()
        instructions = validator.install_recommended_tools()
        if instructions:
            print("Recommended BibTeX validation tools to install:")
            for instruction in instructions:
                print(f"  {instruction}")
        else:
            print("All recommended validation tools are already installed!")
        return
    
    # Clear cache if requested
    if args.clear_cache:
        processor.metadata_fetcher.clear_cache()
    
    # Process papers
    processor.process_papers(
        source_bibtex_file=args.bibtex_file,
        regenerate=args.regenerate,
        force=args.force,
        update_metadata=update_metadata,
        thumbnail_size=args.thumbnail_size,
        test_mode=args.test,
        test_count=args.test_count,
        verbose=args.verbose,
        force_refetch_metadata=args.force_refetch_metadata,
        rename_urls=rename_urls,
        rename_only=args.rename_only
    )
    
    # Run comprehensive validation and fixing if requested
    if run_validation:
        output_file = '_bibliography/papers.bib'
        if os.path.exists(output_file):
            print("\n🔍 Running comprehensive validation and fixing issues...")
            validator = ValidationChecker(config)
            validation_results = validator.validate_and_fix_entries(output_file)
            
            # Exit with error code if validation failed
            if validation_results['failed_entries'] > 0 and not args.test:
                print(f"\n❌ Validation failed with {validation_results['failed_entries']} failed entries")
                sys.exit(1)
        else:
            print("⚠️  Output file not found for validation: {output_file}")
    
    # Validate BibTeX output if requested
    if validate_bibtex:
        output_file = '_bibliography/papers.bib'
        if os.path.exists(output_file):
            print("\n🔍 Validating BibTeX output...")
            validator = BibTeXValidator()
            results = validator.validate_file(output_file, verbose=args.verbose)
            
            if results.get('valid', False):
                print("✅ BibTeX validation passed")
            else:
                print("❌ BibTeX validation failed:")
                for error in results.get('errors', []):
                    print(f"   {error}")
                
                # Don't exit with error code in test mode
                if not args.test:
                    sys.exit(1)
        else:
            print("⚠️  Output file not found for validation: {output_file}")


if __name__ == "__main__":
    main()
