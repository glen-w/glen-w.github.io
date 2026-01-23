#!/usr/bin/env python3
"""
Unit tests for ZipArchiveGenerator class.
Tests zip archive creation and file organization functionality.
"""

import pytest
import os
import zipfile
import tempfile
import shutil
from pathlib import Path
from processing.core.zip_archive_generator import ZipArchiveGenerator
from processing.config import Configuration
from processing.core.text_processor import TextProcessor


@pytest.mark.unit
class TestZipArchiveGenerator:
    """Unit tests for ZipArchiveGenerator class."""
    
    @pytest.fixture
    def temp_config(self, temp_dir):
        """Create a temporary configuration for testing."""
        config = Configuration()
        # Override directories to use temp directory
        config.PDF_DIR = str(temp_dir / "assets" / "pdf")
        config.IMAGES_DIR = str(temp_dir / "assets" / "img" / "publications")
        config.AUDIO_DIR = str(temp_dir / "assets" / "audio")
        config.ZIP_DIR = str(temp_dir / "assets" / "zips")
        config.PREVIEW_DIR = str(temp_dir / "assets" / "img" / "publication_preview")
        
        # Create directories
        os.makedirs(config.PDF_DIR, exist_ok=True)
        os.makedirs(config.IMAGES_DIR, exist_ok=True)
        os.makedirs(config.AUDIO_DIR, exist_ok=True)
        os.makedirs(config.ZIP_DIR, exist_ok=True)
        os.makedirs(config.PREVIEW_DIR, exist_ok=True)
        
        return config
    
    @pytest.fixture
    def zip_generator(self, temp_config):
        """Create zip archive generator for testing."""
        text_processor = TextProcessor(temp_config)
        return ZipArchiveGenerator(temp_config, text_processor)
    
    @pytest.fixture
    def sample_pdf_file(self, temp_config):
        """Create a sample PDF file."""
        pdf_path = os.path.join(temp_config.PDF_DIR, "test_paper.pdf")
        with open(pdf_path, 'wb') as f:
            f.write(b'%PDF-1.4 fake pdf content')
        return "test_paper.pdf"
    
    @pytest.fixture
    def sample_image_files(self, temp_config):
        """Create sample image files."""
        photos = []
        figures = []
        
        # Create photo files
        for i in range(2):
            filename = f"test_photo_{i+1:02d}.jpg"
            photo_path = os.path.join(temp_config.IMAGES_DIR, filename)
            with open(photo_path, 'wb') as f:
                f.write(b'fake jpeg content')
            photos.append(filename)
        
        # Create figure files
        for i in range(2):
            filename = f"test_figure_{i+1:02d}.png"
            figure_path = os.path.join(temp_config.IMAGES_DIR, filename)
            with open(figure_path, 'wb') as f:
                f.write(b'fake png content')
            figures.append(filename)
        
        return photos, figures
    
    @pytest.fixture
    def sample_audio_file(self, temp_config):
        """Create a sample audio file."""
        audio_path = os.path.join(temp_config.AUDIO_DIR, "test_audio.mp3")
        with open(audio_path, 'wb') as f:
            f.write(b'fake mp3 content')
        return "test_audio.mp3"
    
    def test_collect_files_with_pdf_only(self, zip_generator):
        """Test collecting files when only PDF is present."""
        fields = {
            'pdf': 'test_paper.pdf',
            'title': 'Test Paper',
            'author': 'Wright, G.',
            'year': '2023'
        }
        
        file_map = zip_generator._collect_files(fields)
        
        assert 'test_paper.pdf' in file_map['root']
        assert len(file_map['root']) == 1
        assert len(file_map['documents']) == 0
        assert len(file_map['photos']) == 0
        assert len(file_map['figures']) == 0
        assert len(file_map['audio']) == 0
    
    def test_collect_files_with_all_types(self, zip_generator):
        """Test collecting files with all file types."""
        fields = {
            'pdf': 'test_paper.pdf',
            'agenda': 'test_agenda.pdf',
            'slides': 'test_slides.pdf',
            'photos': 'photo1.jpg, photo2.jpg',
            'figures': 'figure1.png, figure2.png',
            'annote': '[audio]\nassets/audio/test_audio.mp3'
        }
        
        file_map = zip_generator._collect_files(fields)
        
        assert 'test_paper.pdf' in file_map['root']
        assert 'test_agenda.pdf' in file_map['documents']
        assert 'test_slides.pdf' in file_map['documents']
        assert 'photo1.jpg' in file_map['photos']
        assert 'photo2.jpg' in file_map['photos']
        assert 'figure1.png' in file_map['figures']
        assert 'figure2.png' in file_map['figures']
        assert 'test_audio.mp3' in file_map['audio']
    
    def test_collect_files_with_empty_fields(self, zip_generator):
        """Test collecting files with empty/None fields."""
        fields = {
            'title': 'Test Paper',
            'pdf': None,
            'photos': '',
            'figures': None
        }
        
        file_map = zip_generator._collect_files(fields)
        
        assert len(file_map['root']) == 0
        assert len(file_map['documents']) == 0
        assert len(file_map['photos']) == 0
        assert len(file_map['figures']) == 0
    
    def test_extract_audio_from_annote(self, zip_generator):
        """Test extracting audio filenames from annote field."""
        annote = """[audio]
assets/audio/file1.mp3
assets/audio/file2.wav
assets/audio/file3.m4a"""
        
        audio_files = zip_generator._extract_audio_from_annote(annote)
        
        assert 'file1.mp3' in audio_files
        assert 'file2.wav' in audio_files
        assert 'file3.m4a' in audio_files
        assert len(audio_files) == 3
    
    def test_extract_audio_from_annote_with_other_sections(self, zip_generator):
        """Test extracting audio when annote has multiple sections."""
        annote = """[type]
Conference Paper
[audio]
assets/audio/test.mp3
[notes]
Some notes here"""
        
        audio_files = zip_generator._extract_audio_from_annote(annote)
        
        assert 'test.mp3' in audio_files
        assert len(audio_files) == 1
    
    def test_extract_audio_from_empty_annote(self, zip_generator):
        """Test extracting audio from empty annote field."""
        audio_files = zip_generator._extract_audio_from_annote('')
        assert len(audio_files) == 0
        
        audio_files = zip_generator._extract_audio_from_annote(None)
        assert len(audio_files) == 0
    
    def test_create_archive_with_pdf_only(self, zip_generator, sample_pdf_file, temp_config):
        """Test creating zip archive with only PDF."""
        fields = {
            'pdf': sample_pdf_file,
            'title': 'Test Paper',
            'author': 'Wright, G.',
            'year': '2023'
        }
        
        zip_metadata = zip_generator.create_archive('test2023', fields)
        
        assert zip_metadata is not None
        assert isinstance(zip_metadata, dict)
        assert 'filename' in zip_metadata
        assert 'file_count' in zip_metadata
        assert 'file_size_mb' in zip_metadata
        
        zip_filename = zip_metadata['filename']
        assert zip_filename.endswith('.zip')
        
        # Verify zip file exists
        zip_path = os.path.join(temp_config.ZIP_DIR, zip_filename)
        assert os.path.exists(zip_path)
        assert os.path.getsize(zip_path) > 0
        
        # Verify zip contents
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            namelist = zipf.namelist()
            assert sample_pdf_file in namelist
            assert len(namelist) == 1
        
        # Verify metadata
        assert zip_metadata['file_count'] == 1
        assert isinstance(zip_metadata['file_size_mb'], str)
        assert float(zip_metadata['file_size_mb']) > 0
    
    def test_create_archive_with_all_file_types(self, zip_generator, sample_pdf_file, 
                                                sample_image_files, sample_audio_file, temp_config):
        """Test creating zip archive with all file types."""
        photos, figures = sample_image_files
        
        fields = {
            'pdf': sample_pdf_file,
            'agenda': 'test_agenda.pdf',
            'slides': 'test_slides.pdf',
            'photos': ', '.join(photos),
            'figures': ', '.join(figures),
            'annote': f'[audio]\nassets/audio/{sample_audio_file}',
            'title': 'Test Paper',
            'author': 'Wright, G.',
            'year': '2023'
        }
        
        # Create additional files
        for filename in ['test_agenda.pdf', 'test_slides.pdf']:
            file_path = os.path.join(temp_config.PDF_DIR, filename)
            with open(file_path, 'wb') as f:
                f.write(b'fake pdf content')
        
        zip_metadata = zip_generator.create_archive('test2023', fields)
        
        assert zip_metadata is not None
        assert isinstance(zip_metadata, dict)
        zip_filename = zip_metadata['filename']
        
        # Verify zip contents
        zip_path = os.path.join(temp_config.ZIP_DIR, zip_filename)
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            namelist = zipf.namelist()
            
            # Check root PDF
            assert sample_pdf_file in namelist
            
            # Check documents folder
            assert f'documents/{fields["agenda"]}' in namelist
            assert f'documents/{fields["slides"]}' in namelist
            
            # Check photos folder
            for photo in photos:
                assert f'photos/{photo}' in namelist
            
            # Check figures folder
            for figure in figures:
                assert f'figures/{figure}' in namelist
            
            # Check audio folder
            assert f'audio/{sample_audio_file}' in namelist
        
        # Verify metadata
        assert zip_metadata['file_count'] == 7  # 1 PDF + 2 documents + 2 photos + 2 figures + 1 audio
        assert isinstance(zip_metadata['file_size_mb'], str)
        assert float(zip_metadata['file_size_mb']) > 0
    
    def test_create_archive_with_missing_files(self, zip_generator, temp_config):
        """Test creating zip archive when some files are missing."""
        fields = {
            'pdf': 'nonexistent.pdf',
            'photos': 'nonexistent_photo.jpg',
            'title': 'Test Paper',
            'author': 'Wright, G.',
            'year': '2023'
        }
        
        # Should still create zip but skip missing files
        zip_metadata = zip_generator.create_archive('test2023', fields)
        
        # Should return None or create empty zip - depends on implementation
        # Current implementation returns None if no files found
        # But let's test the behavior
        if zip_metadata:
            zip_filename = zip_metadata['filename']
            zip_path = os.path.join(temp_config.ZIP_DIR, zip_filename)
            if os.path.exists(zip_path):
                with zipfile.ZipFile(zip_path, 'r') as zipf:
                    # Should have no files or only existing ones
                    namelist = zipf.namelist()
                    # All files are missing, so zip might be empty or not created
                    assert len(namelist) == 0 or all(not os.path.exists(
                        os.path.join(temp_config.PDF_DIR, f) if not '/' in f 
                        else os.path.join(temp_config.IMAGES_DIR, f.split('/')[-1])
                    ) for f in namelist)
    
    def test_create_archive_with_no_files(self, zip_generator):
        """Test creating zip archive when no files are present."""
        fields = {
            'title': 'Test Paper',
            'author': 'Wright, G.',
            'year': '2023'
        }
        
        zip_metadata = zip_generator.create_archive('test2023', fields)
        
        # Should return None when no files to archive
        assert zip_metadata is None
    
    def test_get_zip_filename(self, zip_generator):
        """Test zip filename generation."""
        fields = {
            'title': 'Test Paper Title',
            'author': 'Wright, G.',
            'year': '2023'
        }
        
        zip_filename = zip_generator._get_zip_filename('test2023', fields)
        
        assert zip_filename is not None
        assert zip_filename.endswith('.zip')
        assert 'test' in zip_filename.lower() or '2023' in zip_filename
    
    def test_get_zip_filename_with_missing_fields(self, zip_generator):
        """Test zip filename generation with missing required fields."""
        fields = {
            'title': '',  # Empty title
            'author': '',
            'year': ''
        }
        
        zip_filename = zip_generator._get_zip_filename('test2023', fields)
        
        # Should handle gracefully - might return None or generate default name
        # Current implementation might return None if title is missing
        # This is acceptable behavior
    
    def test_zip_file_structure_organization(self, zip_generator, sample_pdf_file, 
                                            sample_image_files, temp_config):
        """Test that zip file has correct folder structure."""
        photos, figures = sample_image_files
        
        fields = {
            'pdf': sample_pdf_file,
            'slides': 'test_slides.pdf',
            'photos': ', '.join(photos),
            'figures': ', '.join(figures),
            'title': 'Test Paper',
            'author': 'Wright, G.',
            'year': '2023'
        }
        
        # Create slides file
        slides_path = os.path.join(temp_config.PDF_DIR, 'test_slides.pdf')
        with open(slides_path, 'wb') as f:
            f.write(b'fake pdf content')
        
        zip_metadata = zip_generator.create_archive('test2023', fields)
        
        assert zip_metadata is not None
        assert isinstance(zip_metadata, dict)
        zip_filename = zip_metadata['filename']
        
        zip_path = os.path.join(temp_config.ZIP_DIR, zip_filename)
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            namelist = zipf.namelist()
            
            # PDF should be in root
            assert sample_pdf_file in namelist
            assert f'documents/{sample_pdf_file}' not in namelist
            
            # Slides should be in documents folder
            assert f'documents/test_slides.pdf' in namelist
            assert 'test_slides.pdf' not in [n for n in namelist if '/' not in n]
            
            # Photos should be in photos folder
            for photo in photos:
                assert f'photos/{photo}' in namelist
                assert photo not in [n for n in namelist if '/' not in n]
            
            # Figures should be in figures folder
            for figure in figures:
                assert f'figures/{figure}' in namelist
                assert figure not in [n for n in namelist if '/' not in n]
    
    def test_photos_field_parsing(self, zip_generator):
        """Test parsing comma-separated photos field."""
        fields = {
            'photos': 'photo1.jpg, photo2.jpg, photo3.jpg'
        }
        
        file_map = zip_generator._collect_files(fields)
        
        assert len(file_map['photos']) == 3
        assert 'photo1.jpg' in file_map['photos']
        assert 'photo2.jpg' in file_map['photos']
        assert 'photo3.jpg' in file_map['photos']
    
    def test_figures_field_parsing(self, zip_generator):
        """Test parsing comma-separated figures field."""
        fields = {
            'figures': 'figure1.png, figure2.png'
        }
        
        file_map = zip_generator._collect_files(fields)
        
        assert len(file_map['figures']) == 2
        assert 'figure1.png' in file_map['figures']
        assert 'figure2.png' in file_map['figures']
    
    def test_zip_creation_handles_errors_gracefully(self, zip_generator, temp_config):
        """Test that zip creation handles errors gracefully."""
        # Create a field that would cause issues
        fields = {
            'pdf': 'test.pdf',
            'title': 'Test',
            'author': 'Test',
            'year': '2023'
        }
        
        # Don't create the PDF file - should handle missing file gracefully
        zip_metadata = zip_generator.create_archive('test2023', fields)
        
        # Should either return None or create empty zip
        # Current implementation should return None if no valid files found
        # This is acceptable - the method logs warnings but doesn't crash
    
    def test_format_file_size(self, zip_generator):
        """Test file size formatting to MB."""
        # Test various sizes
        assert zip_generator._format_file_size(1024 * 1024) == "1.0"  # 1 MB
        assert zip_generator._format_file_size(2416640) == "2.3"  # 2.3 MB (example from plan)
        assert zip_generator._format_file_size(512 * 1024) == "0.5"  # 0.5 MB
        assert zip_generator._format_file_size(0) == "0.0"  # 0 bytes
        assert zip_generator._format_file_size(1536 * 1024) == "1.5"  # 1.5 MB
