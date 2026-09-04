#!/usr/bin/env python3
"""
Unit tests for FileManager class.
Tests file operations including copying, directory creation, and thumbnail generation.
"""

import shutil
import subprocess

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

from processing.utils.file_manager import FileManager
from processing.config import Configuration

MAGICK = shutil.which('magick')


@pytest.mark.unit
class TestFileManager:
    """Unit tests for FileManager class."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return Configuration()
    
    @pytest.fixture
    def file_manager(self, config):
        """Create FileManager instance for testing."""
        return FileManager(config)
    
    @patch('os.makedirs')
    @patch('shutil.copy2')
    @patch('os.path.exists')
    def test_copy_file_success(self, mock_exists, mock_copy, mock_makedirs, file_manager):
        """Test copying file successfully."""
        mock_exists.return_value = False
        mock_copy.return_value = None
        
        result = file_manager.copy_file("/source/file.pdf", "/dest/file.pdf", force=False)
        
        assert result is True
        mock_copy.assert_called_once_with("/source/file.pdf", "/dest/file.pdf")
    
    @patch('os.makedirs')
    @patch('os.path.exists')
    def test_copy_file_already_exists(self, mock_exists, mock_makedirs, file_manager):
        """Test copying file when destination already exists."""
        mock_exists.return_value = True
        
        result = file_manager.copy_file("/source/file.pdf", "/dest/file.pdf", force=False)
        
        assert result is True  # Should return True even if file exists
    
    @patch('os.makedirs')
    @patch('shutil.copy2', side_effect=Exception("Permission denied"))
    @patch('os.path.exists')
    def test_copy_file_failure(self, mock_exists, mock_copy, mock_makedirs, file_manager):
        """Test copying file when copy operation fails."""
        mock_exists.return_value = False
        
        result = file_manager.copy_file("/source/file.pdf", "/dest/file.pdf", force=False)
        
        assert result is False
    
    @patch('os.makedirs')
    @patch('subprocess.run')
    @patch('os.path.exists')
    @patch('os.path.getsize')
    def test_generate_pdf_thumbnail_success(self, mock_getsize, mock_exists, mock_run, mock_makedirs, file_manager):
        """Test generating PDF thumbnail successfully."""
        mock_exists.return_value = True
        mock_getsize.return_value = 5000  # Larger than MIN_THUMBNAIL_SIZE
        mock_run.return_value = MagicMock(returncode=0)
        
        result = file_manager.generate_pdf_thumbnail("/path/to/file.pdf", "/path/to/thumb.jpg", "600x")
        
        assert result is True
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert cmd[0] == 'magick'
        assert '-resize' in cmd
        assert '-gravity' in cmd
        assert '-extent' in cmd
        assert cmd[cmd.index('-extent') + 1] == file_manager.config.PREVIEW_CANVAS
    
    @patch('os.makedirs')
    @patch('subprocess.run')
    @patch('os.path.exists')
    @patch('os.path.getsize')
    def test_generate_pdf_thumbnail_too_small(self, mock_getsize, mock_exists, mock_run, mock_makedirs, file_manager):
        """Test generating PDF thumbnail when result is too small."""
        mock_exists.return_value = True
        mock_getsize.return_value = 100  # Smaller than MIN_THUMBNAIL_SIZE
        mock_run.return_value = MagicMock(returncode=0)
        
        result = file_manager.generate_pdf_thumbnail("/path/to/file.pdf", "/path/to/thumb.jpg", "600x")
        
        assert result is False
    
    @patch('os.makedirs')
    @patch('subprocess.run')
    def test_generate_pdf_thumbnail_fallback(self, mock_run, mock_makedirs, file_manager):
        """Test PDF thumbnail generation with fallback to legacy convert command."""
        # First call fails (magick not found), second succeeds (convert works)
        mock_run.side_effect = [
            MagicMock(returncode=1),  # magick fails
            MagicMock(returncode=0)   # convert succeeds
        ]
        
        with patch('os.path.exists', return_value=True), \
             patch('os.path.getsize', return_value=5000):
            result = file_manager.generate_pdf_thumbnail("/path/to/file.pdf", "/path/to/thumb.jpg", "600x")
        
        assert result is True
        assert mock_run.call_count == 2  # Should try both commands
    
    @patch('os.makedirs')
    @patch('subprocess.run')
    @patch('os.path.exists')
    @patch('os.path.getsize')
    def test_generate_svg_thumbnail_success(self, mock_getsize, mock_exists, mock_run, mock_makedirs, file_manager):
        """Test generating SVG thumbnail successfully."""
        mock_exists.return_value = True
        mock_getsize.return_value = 5000
        mock_run.return_value = MagicMock(returncode=0)
        
        result = file_manager.generate_svg_thumbnail("/path/to/file.svg", "/path/to/thumb.jpg", "600x")
        
        assert result is True
        mock_run.assert_called_once()
    
    @patch('os.makedirs')
    @patch('subprocess.run')
    @patch('os.path.exists')
    @patch('os.path.getsize')
    def test_optimize_preview_image_success(self, mock_getsize, mock_exists, mock_run, mock_makedirs, file_manager):
        """Test optimizing a source image into a compressed preview thumbnail."""
        mock_exists.return_value = True
        mock_getsize.return_value = 5000
        mock_run.return_value = MagicMock(returncode=0, stderr='', stdout='aabbcc')

        result = file_manager.optimize_preview_image("/path/to/source.jpg", "/path/to/thumb.jpg")

        assert result is True
        cmds = [call.args[0] for call in mock_run.call_args_list]
        cmd = next(c for c in cmds if '-extent' in c and '-resize' in c)
        assert cmd[0] == 'magick'
        assert '-quality' in cmd
        assert '-strip' in cmd
        assert '-gravity' in cmd
        resize_idx = cmd.index('-resize')
        assert cmd[resize_idx + 1].endswith('>')
        assert '640' in cmd[resize_idx + 1]
        assert cmd[cmd.index('-extent') + 1] == '480x640'
        assert cmd[cmd.index('-background') + 1] == '#aabbcc'

    def test_sample_pad_color_picks_mat_that_preserves_logo_contrast(self, file_manager):
        assert file_manager._hex_luminance('#0a0a0a') < 0.22
        assert file_manager._hex_luminance('#aabbcc') > 0.22
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = [
                MagicMock(returncode=0, stdout='True\n', stderr=''),
                MagicMock(returncode=0, stdout='0\n', stderr=''),
                MagicMock(returncode=0, stdout='0.39\n', stderr=''),
            ]
            assert file_manager._sample_pad_color('/path/to/white-logo.png') == '#1a1a1a'
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = [
                MagicMock(returncode=0, stdout='True\n', stderr=''),
                MagicMock(returncode=0, stdout='0.40\n', stderr=''),
                MagicMock(returncode=0, stdout='0.05\n', stderr=''),
            ]
            assert file_manager._sample_pad_color('/path/to/dark-logo.png') == '#f0f0f0'
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = [
                MagicMock(returncode=0, stdout='False\n', stderr=''),
                MagicMock(returncode=0, stdout='aabbcc', stderr=''),
            ]
            assert file_manager._sample_pad_color('/path/to/photo.jpg') == '#aabbcc'

    def test_normalize_thumbnail_geometry(self, file_manager):
        """Test ImageMagick geometry normalization for shrink-only resize."""
        assert file_manager._normalize_thumbnail_geometry('480x') == '480x>'
        assert file_manager._normalize_thumbnail_geometry('480x>') == '480x>'
        assert file_manager._normalize_thumbnail_geometry('480x640>') == '480x640>'
        assert file_manager._normalize_thumbnail_geometry('200x200!') == '200x200!'

    def test_canvas_from_size(self, file_manager):
        assert file_manager._canvas_from_size('480x640>') == '480x640'
        assert file_manager._canvas_from_size('600x800') == '600x800'
        assert file_manager._canvas_from_size('480x>') == file_manager.config.PREVIEW_CANVAS

    def test_preview_fit_args(self, file_manager):
        args = file_manager._preview_fit_args('480x640>', 'white')
        assert args[args.index('-resize') + 1] == '480x640>'
        assert args[args.index('-gravity') + 1] == 'center'
        assert args[args.index('-background') + 1] == 'white'
        assert args[args.index('-extent') + 1] == '480x640'

    def test_default_thumbnail_size_is_three_by_four(self, file_manager):
        assert file_manager.config.DEFAULT_THUMBNAIL_SIZE == '480x640>'
        assert file_manager.config.PREVIEW_CANVAS == '480x640'

    @patch('os.remove')
    @patch('os.replace')
    @patch('os.close')
    @patch('tempfile.mkstemp', return_value=(3, '/tmp/preview.tmp.jpeg'))
    @patch('subprocess.run')
    @patch('os.path.exists')
    @patch('os.path.getsize')
    def test_normalize_preview_image(self, mock_getsize, mock_exists, mock_run, mock_mkstemp, mock_close, mock_replace, mock_remove, file_manager):
        mock_exists.return_value = True
        mock_getsize.return_value = 5000
        mock_run.return_value = MagicMock(returncode=0, stdout='112233', stderr='')

        result = file_manager.normalize_preview_image('/assets/img/publication_preview/example.jpeg')

        assert result is True
        mock_replace.assert_called_once_with('/tmp/preview.tmp.jpeg', '/assets/img/publication_preview/example.jpeg')
        cmds = [call.args[0] for call in mock_run.call_args_list]
        cmd = next(c for c in cmds if '-extent' in c)
        assert cmd[0] == 'magick'
        assert '-gravity' in cmd
        assert cmd[cmd.index('-extent') + 1] == '480x640'
        assert cmd[cmd.index('-resize') + 1].endswith('>')

    @patch.object(FileManager, 'normalize_preview_image', return_value=True)
    @patch('os.path.isfile', return_value=True)
    @patch('os.path.isdir', return_value=True)
    @patch('os.listdir', return_value=['a.jpeg', 'b.jpg', 'notes.txt', 'c.webp'])
    def test_normalize_preview_directory(self, mock_listdir, mock_isdir, mock_isfile, mock_normalize, file_manager):
        stats = file_manager.normalize_preview_directory('/previews')

        assert stats['normalized'] == 2
        assert stats['failed'] == 0
        assert mock_normalize.call_count == 2
    
    @patch('os.makedirs')
    def test_ensure_directories_exist(self, mock_makedirs, file_manager):
        """Test ensuring directories exist."""
        file_manager.ensure_directories_exist()
        
        # Should call makedirs for each directory
        assert mock_makedirs.call_count >= 1
    
    @patch('os.path.exists')
    @patch('os.remove')
    def test_cleanup_file(self, mock_remove, mock_exists, file_manager):
        """Test cleaning up a file."""
        mock_exists.return_value = True
        
        file_manager._cleanup_file("/path/to/file.pdf")
        
        mock_remove.assert_called_once_with("/path/to/file.pdf")
    
    @patch('os.path.exists')
    def test_cleanup_file_not_exists(self, mock_exists, file_manager):
        """Test cleaning up file that doesn't exist."""
        mock_exists.return_value = False
        
        # Should not raise exception
        file_manager._cleanup_file("/path/to/nonexistent.pdf")

    @pytest.mark.skipif(MAGICK is None, reason='ImageMagick magick not on PATH')
    def test_optimize_preview_fits_wide_source_to_canvas(self, file_manager, tmp_path):
        source = tmp_path / 'wide.png'
        dest = tmp_path / 'preview.jpeg'
        subprocess.run([MAGICK, '-size', '800x200', 'xc:#c04040', str(source)], check=True)
        assert file_manager.optimize_preview_image(str(source), str(dest)) is True
        geometry = subprocess.run(
            [MAGICK, 'identify', '-format', '%wx%h', str(dest)],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        assert geometry == '480x640'

    @pytest.mark.skipif(MAGICK is None, reason='ImageMagick magick not on PATH')
    def test_normalize_preview_pads_existing_jpeg_in_place(self, file_manager, tmp_path):
        path = tmp_path / 'existing.jpeg'
        subprocess.run([MAGICK, '-size', '300x100', 'xc:#2040a0', str(path)], check=True)
        assert file_manager.normalize_preview_image(str(path)) is True
        geometry = subprocess.run(
            [MAGICK, 'identify', '-format', '%wx%h', str(path)],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        assert geometry == '480x640'

    @pytest.mark.skipif(MAGICK is None, reason='ImageMagick magick not on PATH')
    def test_generate_pdf_thumbnail_fits_canvas(self, file_manager, tmp_path):
        pdf = tmp_path / 'page.pdf'
        dest = tmp_path / 'from_pdf.jpeg'
        subprocess.run([MAGICK, '-size', '800x600', 'xc:#f5f5f5', str(pdf)], check=True)
        assert file_manager.generate_pdf_thumbnail(str(pdf), str(dest)) is True
        geometry = subprocess.run(
            [MAGICK, 'identify', '-format', '%wx%h', str(dest)],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        assert geometry == '480x640'
