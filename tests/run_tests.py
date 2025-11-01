#!/usr/bin/env python3
"""
Test runner script for the paper processing test suite.
Provides convenient commands for running different types of tests.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ SUCCESS")
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ FAILED")
        if e.stdout:
            print("STDOUT:")
            print(e.stdout)
        if e.stderr:
            print("STDERR:")
            print(e.stderr)
        return False


def run_unit_tests():
    """Run unit tests."""
    cmd = ["python", "-m", "pytest", "tests/unit/", "-v", "--tb=short"]
    return run_command(cmd, "Unit Tests")


def run_integration_tests():
    """Run integration tests."""
    cmd = ["python", "-m", "pytest", "tests/integration/", "-v", "--tb=short"]
    return run_command(cmd, "Integration Tests")


def run_performance_tests():
    """Run performance tests."""
    cmd = ["python", "-m", "pytest", "tests/performance/", "-v", "--tb=short", "-m", "performance"]
    return run_command(cmd, "Performance Tests")


def run_bibtex_syntax_tests():
    """Run BibTeX syntax validation tests."""
    cmd = ["python", "-m", "pytest", "tests/unit/test_bibtex_syntax_validation.py", "-v", "--tb=short"]
    return run_command(cmd, "BibTeX Syntax Validation Tests")


def run_all_tests():
    """Run all tests."""
    cmd = ["python", "-m", "pytest", "tests/", "-v", "--tb=short"]
    return run_command(cmd, "All Tests")


def run_fast_tests():
    """Run fast tests (exclude slow performance tests)."""
    cmd = ["python", "-m", "pytest", "tests/", "-v", "--tb=short", "-m", "not slow"]
    return run_command(cmd, "Fast Tests (Excluding Slow Performance Tests)")


def run_coverage():
    """Run tests with coverage reporting."""
    cmd = ["python", "-m", "pytest", "tests/", "--cov=processing", "--cov-report=html", "--cov-report=term"]
    return run_command(cmd, "Tests with Coverage")


def run_lint():
    """Run linting checks."""
    cmd = ["python", "-m", "flake8", "processing/", "tests/"]
    return run_command(cmd, "Linting Checks")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Test runner for paper processing")
    parser.add_argument("--unit", action="store_true", help="Run unit tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--performance", action="store_true", help="Run performance tests")
    parser.add_argument("--bibtex-syntax", action="store_true", help="Run BibTeX syntax tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--fast", action="store_true", help="Run fast tests (exclude slow)")
    parser.add_argument("--coverage", action="store_true", help="Run tests with coverage")
    parser.add_argument("--lint", action="store_true", help="Run linting checks")
    parser.add_argument("--ci", action="store_true", help="Run CI test suite")
    
    args = parser.parse_args()
    
    # Change to project root directory
    project_root = Path(__file__).parent.parent
    import os
    os.chdir(project_root)
    
    success = True
    
    if args.unit:
        success &= run_unit_tests()
    elif args.integration:
        success &= run_integration_tests()
    elif args.performance:
        success &= run_performance_tests()
    elif args.bibtex_syntax:
        success &= run_bibtex_syntax_tests()
    elif args.fast:
        success &= run_fast_tests()
    elif args.coverage:
        success &= run_coverage()
    elif args.lint:
        success &= run_lint()
    elif args.ci:
        # CI test suite: run all tests except slow performance tests
        success &= run_fast_tests()
        success &= run_lint()
    elif args.all:
        success &= run_all_tests()
    else:
        # Default: run fast tests
        success &= run_fast_tests()
    
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
