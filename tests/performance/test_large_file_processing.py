#!/usr/bin/env python3
"""
Performance tests for large file processing.
Tests processing performance with large BibTeX files and many entries.
"""

import pytest
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

from processing.core.bibtex_processor import BibTeXProcessor
from processing.validation.enhanced_validator import EnhancedValidator
from processing.core.text_processor import TextProcessor
from processing.config import Configuration


@pytest.mark.performance
@pytest.mark.slow
class TestLargeFileProcessing:
    """Performance tests for large file processing."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return Configuration()
    
    @pytest.fixture
    def bibtex_processor(self, config):
        """Create BibTeX processor for testing."""
        text_processor = TextProcessor(config)
        return BibTeXProcessor(config, text_processor)
    
    @pytest.fixture
    def validator(self, config):
        """Create enhanced validator for testing."""
        return EnhancedValidator(config)
    
    def generate_large_bibtex_content(self, num_entries: int) -> str:
        """Generate large BibTeX content for testing."""
        content = ""
        for i in range(num_entries):
            entry = f"""@article{{test{i:04d},
                title = {{Test Title {i} with {{nested}} braces and special chars @#$%^&*()}},
                author = {{Author, Test {i} and Another, Author {i}}},
                year = {{2023}},
                journal = {{Journal of {{Complex}} Science {i}}},
                doi = {{10.1000/test{i:04d}}},
                url = {{https://example.com/paper{i}}},
                abstract = {{This is a very long abstract for entry {i} that contains many words and might cause issues when processing. It has multiple sentences and contains various punctuation marks, numbers, and special characters. The abstract should be handled correctly without breaking BibTeX syntax.}},
                keywords = {{test{i}, performance, validation, large, file}},
                file = {{test{i}.pdf:/path/to/test{i}.pdf:application/pdf; image{i}.jpg:/path/to/image{i}.jpg:image/jpeg; thumbnail{i}.png:/path/to/thumbnail{i}.png:image/png}}
            }}

            """
            content += entry
        return content
    
    def test_large_file_parsing_performance(self, bibtex_processor, temp_dir):
        """Test parsing performance with large files."""
        # Generate large content
        large_content = self.generate_large_bibtex_content(1000)
        large_file = temp_dir / "large.bib"
        large_file.write_text(large_content)
        
        # Measure parsing time
        start_time = time.time()
        entries = bibtex_processor.parse_bibtex_entries(large_content)
        parsing_time = time.time() - start_time
        
        # Verify results
        assert len(entries) == 1000
        assert parsing_time < 10.0  # Should parse 1000 entries in under 10 seconds
        
        print(f"Parsed 1000 entries in {parsing_time:.2f} seconds")
    
    def test_large_file_validation_performance(self, validator, temp_dir):
        """Test validation performance with large files."""
        # Generate large content
        large_content = self.generate_large_bibtex_content(500)
        large_file = temp_dir / "large.bib"
        large_file.write_text(large_content)
        
        # Measure validation time
        start_time = time.time()
        results = validator.validate_bibtex_file(str(large_file))
        validation_time = time.time() - start_time
        
        # Verify results
        assert results['total_entries'] == 500
        assert validation_time < 15.0  # Should validate 500 entries in under 15 seconds
        
        print(f"Validated 500 entries in {validation_time:.2f} seconds")
    
    def test_large_file_cleaning_performance(self, bibtex_processor, temp_dir):
        """Test cleaning performance with large files."""
        # Generate large content with some malformed entries
        large_content = self.generate_large_bibtex_content(1000)
        # Add some malformed entries
        malformed_entries = """@article{malformed1,
            title = {Malformed Title
            author = {Test Author},,
            year = {2023},
        }

        @article{malformed2,
            title = {Another {Malformed} Title}
            author = {Test Author}
            year = {2023}
        }

        """
        large_content += malformed_entries
        
        # Measure cleaning time
        start_time = time.time()
        cleaned = bibtex_processor.clean_malformed_entries(large_content)
        cleaning_time = time.time() - start_time
        
        # Verify results
        assert len(cleaned) > 0
        assert cleaning_time < 5.0  # Should clean 1000+ entries in under 5 seconds
        
        print(f"Cleaned 1000+ entries in {cleaning_time:.2f} seconds")
    
    def test_memory_usage_large_files(self, bibtex_processor, temp_dir):
        """Test memory usage with large files."""
        import psutil
        import os
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Generate very large content
        large_content = self.generate_large_bibtex_content(2000)
        large_file = temp_dir / "very_large.bib"
        large_file.write_text(large_content)
        
        # Process the large file
        entries = bibtex_processor.parse_bibtex_entries(large_content)
        cleaned = bibtex_processor.clean_malformed_entries(large_content)
        
        # Get final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Verify results
        assert len(entries) == 2000
        assert memory_increase < 100  # Should not use more than 100MB additional memory
        
        print(f"Memory usage increased by {memory_increase:.2f} MB for 2000 entries")
    
    def test_concurrent_processing_performance(self, bibtex_processor, temp_dir):
        """Test concurrent processing performance."""
        import concurrent.futures
        import threading
        
        # Generate multiple large files
        files = []
        for i in range(5):
            content = self.generate_large_bibtex_content(200)
            file_path = temp_dir / f"large_{i}.bib"
            file_path.write_text(content)
            files.append(file_path)
        
        def process_file(file_path):
            """Process a single file."""
            content = file_path.read_text()
            entries = bibtex_processor.parse_bibtex_entries(content)
            cleaned = bibtex_processor.clean_malformed_entries(content)
            return len(entries)
        
        # Measure concurrent processing time
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(process_file, file_path) for file_path in files]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        concurrent_time = time.time() - start_time
        
        # Measure sequential processing time
        start_time = time.time()
        sequential_results = [process_file(file_path) for file_path in files]
        sequential_time = time.time() - start_time
        
        # Verify results
        assert all(result == 200 for result in results)
        assert all(result == 200 for result in sequential_results)
        
        print(f"Concurrent processing: {concurrent_time:.2f} seconds")
        print(f"Sequential processing: {sequential_time:.2f} seconds")
        print(f"Speedup: {sequential_time / concurrent_time:.2f}x")
    
    def test_large_file_validation_error_detection(self, validator, temp_dir):
        """Test error detection performance with large files containing errors."""
        # Generate large content with various errors
        large_content = self.generate_large_bibtex_content(1000)
        
        # Add various types of errors
        error_entries = []
        for i in range(100):
            if i % 4 == 0:
                # Trailing comma error
                error_entries.append(f"""@article{{error{i},
                    title = {{Error Title {i}}},
                    author = {{Error Author {i}}},
                    year = {{2023}},
                }}""")
            elif i % 4 == 1:
                # Double comma error
                error_entries.append(f"""@article{{error{i},
                    title = {{Error Title {i}}},
                    author = {{Error Author {i}}},,
                    year = {{2023}}
                }}""")
            elif i % 4 == 2:
                # Internal braces error
                error_entries.append(f"""@article{{error{i},
                    title = {{Error Title with {{nested}} braces}},
                    author = {{Error Author {i}}},
                    year = {{2023}}
                }}""")
            else:
                # Unrenamed files error
                error_entries.append(f"""@article{{error{i},
                    title = {{Error Title {i}}},
                    author = {{Error Author {i}}},
                    year = {{2023}},
                    pdf = {{54439519274_cf052b44d1_k.pdf}}
                }}""")
        
        large_content += "\n".join(error_entries)
        large_file = temp_dir / "large_with_errors.bib"
        large_file.write_text(large_content)
        
        # Measure validation time
        start_time = time.time()
        results = validator.validate_bibtex_file(str(large_file))
        validation_time = time.time() - start_time
        
        # Verify results
        assert results['total_entries'] == 1100
        assert results['failed_entries'] == 100
        assert validation_time < 20.0  # Should validate 1100 entries in under 20 seconds
        
        # Check that errors were detected
        issues_by_type = results['issues_by_type']
        assert len(issues_by_type['trailing_commas']) > 0
        assert len(issues_by_type['double_commas']) > 0
        assert len(issues_by_type['internal_braces']) > 0
        assert len(issues_by_type['unrenamed_files']) > 0
        
        print(f"Validated 1100 entries with 100 errors in {validation_time:.2f} seconds")
    
    def test_large_file_tag_addition_performance(self, bibtex_processor, temp_dir):
        """Test tag addition performance with large files."""
        # Generate large content
        large_content = self.generate_large_bibtex_content(500)
        large_file = temp_dir / "large.bib"
        large_file.write_text(large_content)
        
        # Parse entries
        entries = bibtex_processor.parse_bibtex_entries(large_content)
        
        # Measure tag addition time
        start_time = time.time()
        modified_content = large_content
        
        for entry in entries[:100]:  # Add tags to first 100 entries
            citation_key = entry['citation_key']
            modified_content = bibtex_processor.add_multiple_tags(
                modified_content, citation_key, {
                    'pdf': f'{citation_key}.pdf',
                    'preview': f'{citation_key}.jpg',
                    'selected': 'true'
                }
            )
        
        tag_addition_time = time.time() - start_time
        
        # Verify results
        assert tag_addition_time < 10.0  # Should add tags to 100 entries in under 10 seconds
        
        print(f"Added tags to 100 entries in {tag_addition_time:.2f} seconds")
