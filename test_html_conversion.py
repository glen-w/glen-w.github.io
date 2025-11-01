#!/usr/bin/env python3
"""
Test script for HTML to PDF conversion functionality.
This script tests the HTML processor with a sample HTML file.
"""

import os
import sys
import tempfile

# Add the processing directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'processing'))

from processing.core.html_processor import HTMLProcessor
from processing.config import Configuration

def create_test_html():
    """Create a test HTML file for conversion."""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Test HTML Snapshot</title>
</head>
<body>
    <h1>Test HTML Snapshot</h1>
    <p>This is a test HTML file to verify HTML to PDF conversion functionality.</p>
    <h2>Features to Test</h2>
    <ul>
        <li>HTML structure preservation</li>
        <li>Text formatting</li>
        <li>List formatting</li>
        <li>Title extraction</li>
    </ul>
    <h2>Sample Content</h2>
    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
    <blockquote>
        This is a blockquote to test special formatting.
    </blockquote>
    <p>More content to ensure the PDF has sufficient length for testing.</p>
</body>
</html>"""
    
    # Create temporary HTML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(html_content)
        return f.name

def test_html_conversion():
    """Test HTML to PDF conversion."""
    print("🧪 Testing HTML to PDF conversion...")
    
    # Create test HTML file
    html_path = create_test_html()
    print(f"📄 Created test HTML file: {html_path}")
    
    try:
        # Initialize HTML processor
        config = Configuration()
        processor = HTMLProcessor(config)
        
        # Check if WeasyPrint is available
        if not processor.weasyprint_available:
            print("❌ WeasyPrint not available. Install with: pip install weasyprint")
            return False
        
        # Create output directory
        output_dir = "test_output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Test conversion
        output_path = os.path.join(output_dir, "test_conversion.pdf")
        
        print(f"🔄 Converting HTML to PDF...")
        success = processor.convert_html_to_pdf(
            html_path, 
            output_path, 
            title="Test HTML Snapshot",
            author="Test Author",
            verbose=True
        )
        
        if success:
            print(f"✅ Successfully converted HTML to PDF: {output_path}")
            
            # Check if file exists and has content
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"📊 PDF file size: {file_size} bytes")
                
                if file_size > 0:
                    print("✅ PDF file created successfully with content")
                    return True
                else:
                    print("❌ PDF file is empty")
                    return False
            else:
                print("❌ PDF file was not created")
                return False
        else:
            print("❌ HTML to PDF conversion failed")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    finally:
        # Clean up test HTML file
        if os.path.exists(html_path):
            os.unlink(html_path)
            print(f"🧹 Cleaned up test HTML file")

def test_html_validation():
    """Test HTML file validation."""
    print("\n🧪 Testing HTML file validation...")
    
    # Create test HTML file
    html_path = create_test_html()
    
    try:
        config = Configuration()
        processor = HTMLProcessor(config)
        
        # Test validation
        is_valid = processor.validate_html_file(html_path)
        print(f"✅ HTML file validation: {'PASSED' if is_valid else 'FAILED'}")
        
        # Test title extraction
        title = processor.get_html_title(html_path)
        print(f"📝 Extracted title: '{title}'")
        
        # Test file type detection
        is_html = processor.is_html_file(html_path)
        print(f"🔍 HTML file detection: {'PASSED' if is_html else 'FAILED'}")
        
        return is_valid and is_html
        
    except Exception as e:
        print(f"❌ Validation test failed with error: {e}")
        return False
    finally:
        # Clean up test HTML file
        if os.path.exists(html_path):
            os.unlink(html_path)

def main():
    """Run all tests."""
    print("🚀 Starting HTML to PDF conversion tests...\n")
    
    # Test HTML validation
    validation_success = test_html_validation()
    
    # Test HTML to PDF conversion
    conversion_success = test_html_conversion()
    
    # Summary
    print(f"\n📋 Test Summary:")
    print(f"   HTML Validation: {'✅ PASSED' if validation_success else '❌ FAILED'}")
    print(f"   HTML to PDF Conversion: {'✅ PASSED' if conversion_success else '❌ FAILED'}")
    
    if validation_success and conversion_success:
        print(f"\n🎉 All tests passed! HTML to PDF conversion is working correctly.")
        return 0
    else:
        print(f"\n❌ Some tests failed. Please check the error messages above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
