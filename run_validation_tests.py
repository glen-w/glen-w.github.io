#!/usr/bin/env python3
"""
Comprehensive test runner for BibTeX validation and processing.
Runs all validation tests and provides detailed reporting.
"""

import pytest
import sys
import os
from pathlib import Path


def run_all_tests():
    """Run all validation and processing tests."""
    print("🧪 Running comprehensive BibTeX validation and processing tests...")
    print("=" * 70)
    
    # Test files to run
    test_files = [
        "test_enhanced_validator.py",
        "test_field_cleaner.py", 
        "test_bibtex_formatter.py",
        "test_validation_scenarios.py"
    ]
    
    # Check if test files exist
    missing_files = []
    for test_file in test_files:
        if not os.path.exists(test_file):
            missing_files.append(test_file)
    
    if missing_files:
        print(f"❌ Missing test files: {', '.join(missing_files)}")
        return False
    
    # Run tests with verbose output
    test_args = [
        "-v",  # Verbose output
        "--tb=short",  # Short traceback format
        "--durations=10",  # Show 10 slowest tests
        "--color=yes",  # Colored output
    ]
    
    # Add all test files
    test_args.extend(test_files)
    
    # Run pytest
    exit_code = pytest.main(test_args)
    
    print("=" * 70)
    if exit_code == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    
    return exit_code == 0


def run_specific_test(test_name):
    """Run a specific test file."""
    test_file = f"test_{test_name}.py"
    
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return False
    
    print(f"🧪 Running {test_name} tests...")
    print("=" * 50)
    
    exit_code = pytest.main(["-v", "--tb=short", test_file])
    
    print("=" * 50)
    if exit_code == 0:
        print(f"✅ {test_name} tests passed!")
    else:
        print(f"❌ {test_name} tests failed!")
    
    return exit_code == 0


def run_validation_on_real_file():
    """Run validation on the actual papers.bib file."""
    print("🔍 Running validation on papers.bib...")
    print("=" * 50)
    
    bibtex_file = "_bibliography/papers.bib"
    if not os.path.exists(bibtex_file):
        print(f"❌ File not found: {bibtex_file}")
        return False
    
    try:
        from enhanced_validator import EnhancedValidator
        from config import Configuration
        
        config = Configuration()
        validator = EnhancedValidator(config)
        results = validator.validate_bibtex_file(bibtex_file)
        
        print(f"📊 Validation Results for {bibtex_file}:")
        print(f"  Total entries: {results['total_entries']}")
        print(f"  Passed: {results['passed_entries']}")
        print(f"  Failed: {results['failed_entries']}")
        print(f"  Warnings: {len(results['warnings'])}")
        print(f"  Errors: {len(results['errors'])}")
        
        # Show issues by type
        issues_by_type = results['issues_by_type']
        for issue_type, issues in issues_by_type.items():
            if issues:
                print(f"\n🔍 {issue_type.replace('_', ' ').title()}: {len(issues)} issues")
                for issue in issues[:3]:  # Show first 3
                    print(f"    {issue}")
                if len(issues) > 3:
                    print(f"    ... and {len(issues) - 3} more")
        
        if results['failed_entries'] == 0:
            print("\n✅ All validation checks passed!")
            return True
        else:
            print(f"\n❌ {results['failed_entries']} entries failed validation")
            return False
            
    except Exception as e:
        print(f"❌ Error running validation: {e}")
        return False


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run BibTeX validation and processing tests')
    parser.add_argument('--test', choices=['all', 'validator', 'cleaner', 'formatter', 'scenarios'],
                       default='all', help='Which tests to run')
    parser.add_argument('--validate-real', action='store_true',
                       help='Run validation on the actual papers.bib file')
    parser.add_argument('--list-tests', action='store_true',
                       help='List available test files')
    
    args = parser.parse_args()
    
    if args.list_tests:
        print("Available test files:")
        test_files = [
            "test_enhanced_validator.py - Enhanced validator tests",
            "test_field_cleaner.py - Field cleaner tests", 
            "test_bibtex_formatter.py - BibTeX formatter tests",
            "test_validation_scenarios.py - Real-world scenario tests"
        ]
        for test_file in test_files:
            print(f"  {test_file}")
        return 0
    
    success = True
    
    if args.validate_real:
        success = run_validation_on_real_file() and success
    
    if args.test == 'all':
        success = run_all_tests() and success
    elif args.test == 'validator':
        success = run_specific_test('enhanced_validator') and success
    elif args.test == 'cleaner':
        success = run_specific_test('field_cleaner') and success
    elif args.test == 'formatter':
        success = run_specific_test('bibtex_formatter') and success
    elif args.test == 'scenarios':
        success = run_specific_test('validation_scenarios') and success
    
    if success:
        print("\n🎉 All operations completed successfully!")
        return 0
    else:
        print("\n💥 Some operations failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
