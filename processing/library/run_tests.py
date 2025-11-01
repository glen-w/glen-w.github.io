#!/usr/bin/env python3
"""
Test runner script for the library generator.

This script provides a convenient way to run tests with different configurations.
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"❌ Command not found: {cmd[0]}")
        print("Make sure pytest is installed: pip install -r requirements-test.txt")
        return False

def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run library generator tests")
    parser.add_argument(
        '--unit', 
        action='store_true', 
        help='Run only unit tests'
    )
    parser.add_argument(
        '--integration', 
        action='store_true', 
        help='Run only integration tests'
    )
    parser.add_argument(
        '--coverage', 
        action='store_true', 
        help='Run with coverage reporting'
    )
    parser.add_argument(
        '--html', 
        action='store_true', 
        help='Generate HTML test report'
    )
    parser.add_argument(
        '--parallel', 
        action='store_true', 
        help='Run tests in parallel'
    )
    parser.add_argument(
        '--verbose', 
        action='store_true', 
        help='Verbose output'
    )
    parser.add_argument(
        '--file', 
        type=str, 
        help='Run specific test file'
    )
    
    args = parser.parse_args()
    
    # Change to the script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Build pytest command
    cmd = ['python', '-m', 'pytest']
    
    # Add test selection
    if args.unit:
        cmd.extend(['-m', 'unit'])
    elif args.integration:
        cmd.extend(['-m', 'integration'])
    elif args.file:
        cmd.append(f'tests/{args.file}')
    else:
        cmd.append('tests/')
    
    # Add options
    if args.coverage:
        cmd.extend(['--cov=.', '--cov-report=term-missing', '--cov-report=html'])
    
    if args.html:
        cmd.extend(['--html=test_report.html', '--self-contained-html'])
    
    if args.parallel:
        cmd.extend(['-n', 'auto'])
    
    if args.verbose:
        cmd.append('-v')
    else:
        cmd.append('-q')
    
    # Run tests
    success = run_command(cmd, "Library Generator Tests")
    
    if success:
        print(f"\n{'='*60}")
        print("🎉 All tests passed!")
        if args.coverage:
            print("📊 Coverage report generated in htmlcov/index.html")
        if args.html:
            print("📄 HTML test report generated in test_report.html")
        print('='*60)
    else:
        print(f"\n{'='*60}")
        print("💥 Some tests failed!")
        print("Check the output above for details.")
        print('='*60)
        sys.exit(1)

if __name__ == "__main__":
    main()
