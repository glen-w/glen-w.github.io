#!/usr/bin/env python3
"""
Simple test runner for process_papers.py
Run with: python run_tests.py
"""

import subprocess
import sys
import os

def run_tests():
    """Run the test suite."""
    print("🧪 Running process_papers.py test suite...")
    
    # Check if pytest is available
    try:
        import pytest
        print("✅ pytest is available")
    except ImportError:
        print("❌ pytest not found. Installing test dependencies...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements-test.txt'], 
                          check=True, capture_output=True)
            print("✅ Test dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install test dependencies: {e}")
            return 1
    
    # Run the tests
    print("\n🚀 Starting test execution...")
    try:
        result = subprocess.run([sys.executable, '-m', 'pytest', 'tests/', '-v'], 
                              capture_output=False)
        return result.returncode
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())

