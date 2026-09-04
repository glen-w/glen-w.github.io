#!/usr/bin/env python3
"""
CLI / incremental / regenerate safety tests (requirements 80–99 subset).
"""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from processing.config import Configuration
from processing.core.bibtex_processor import BibTeXProcessor
from processing.core.entry_processor import EntryProcessor
from processing.core.paper_processor import PaperProcessor
from processing.core.pdf_processor import PDFProcessor
from processing.core.text_processor import TextProcessor
from processing.core.zip_archive_generator import ZipArchiveGenerator
from processing.library.generator import LibraryPageGenerator
from processing.utils.file_field_manager import FileFieldManager
from processing.utils.file_field_parser import FileFieldParser
from processing.utils.file_manager import FileManager
from processing.validation.enhanced_validator import EnhancedValidator


@pytest.fixture
def config():
    return Configuration()


@pytest.fixture
def entry_processor(config):
    text_processor = TextProcessor(config)
    file_manager = FileManager(config)
    pdf_processor = PDFProcessor(config, text_processor)
    bibtex_processor = BibTeXProcessor(config, text_processor)
    zip_generator = ZipArchiveGenerator(config, text_processor)
    file_field_manager = FileFieldManager(FileFieldParser())
    return EntryProcessor(
        config=config,
        file_manager=file_manager,
        pdf_processor=pdf_processor,
        bibtex_processor=bibtex_processor,
        text_processor=text_processor,
        zip_archive_generator=zip_generator,
        file_field_manager=file_field_manager,
    )


@pytest.mark.unit
class TestIncrementalFileChecks:
    """Reqs 82–85: incremental missing outputs + remote URLs."""

    @patch('os.path.exists')
    def test_incremental_missing_pdf_is_not_processed(self, mock_exists, entry_processor, config):
        def exists(path):
            path = str(path)
            if path.endswith('preview.jpg') or 'publication_preview' in path:
                return True
            if path.endswith('file.pdf') or config.PDF_DIR in path:
                return False
            return False

        mock_exists.side_effect = exists
        fields = {'preview': 'preview.jpg', 'pdf': 'file.pdf'}
        assert entry_processor.is_entry_processed(fields, incremental=True) is False

    @patch('os.path.exists')
    def test_incremental_missing_image_bundle_is_not_processed(
        self, mock_exists, entry_processor, config
    ):
        def exists(path):
            path = str(path)
            if 'preview.jpg' in path or 'file.pdf' in path:
                return True
            if 'photo1.jpg' in path:
                return False
            return True

        mock_exists.side_effect = exists
        fields = {
            'preview': 'preview.jpg',
            'pdf': 'file.pdf',
            'photos': 'photo1.jpg',
        }
        assert entry_processor.is_entry_processed(fields, incremental=True) is False

    @patch('os.path.exists')
    def test_remote_http_url_not_checked_as_local(self, mock_exists, entry_processor):
        mock_exists.return_value = False
        fields = {
            'preview': 'https://cdn.example.com/preview.jpg',
            'pdf': 'https://cdn.example.com/paper.pdf',
        }
        # Remote URLs are skipped in _output_files_exist; with no local refs, True
        assert entry_processor.is_entry_processed(fields, incremental=True) is True
        # Ensure we never asked os.path.exists for the remote URL strings themselves
        for call in mock_exists.call_args_list:
            arg = str(call.args[0]) if call.args else ''
            assert not arg.startswith('https://')


@pytest.mark.unit
@pytest.mark.library
class TestTestModeLibraryIsolation:
    """Req 87: test_mode must not write production _library."""

    def test_test_mode_writes_temp_not_production_library(self, tmp_path, config):
        production_library = Path(config._root) / '_library'
        temp_out = tmp_path / 'library_test_out'
        temp_out.mkdir()
        bib = tmp_path / 'test.bib'
        bib.write_text(
            '@article{iso2024,\n'
            '  title = {Isolation Test},\n'
            '  author = {Wright, Glen},\n'
            '  year = {2024},\n'
            '  month = {1}\n'
            '}\n',
            encoding='utf-8',
        )

        before = set(production_library.glob('*.md')) if production_library.exists() else set()

        gen = LibraryPageGenerator(
            bib_file=str(bib),
            output_dir=str(temp_out),
            test_mode=True,
            skip_dynamic_filters=True,
        )
        assert Path(gen.output_dir).resolve() == temp_out.resolve()
        assert Path(gen.output_dir).resolve() != production_library.resolve()

        gen.run()

        after = set(production_library.glob('*.md')) if production_library.exists() else set()
        assert after == before
        assert list(temp_out.glob('*.md')), 'expected pages under temp output_dir'


@pytest.mark.unit
class TestForceAndRegenerate:
    """Reqs 88–90, 92, 96."""

    @patch.object(EntryProcessor, 'process_entry_files', return_value=True)
    @patch.object(EntryProcessor, 'is_entry_processed', return_value=True)
    def test_force_true_calls_process_when_already_processed(
        self, mock_is_processed, mock_process_files, entry_processor
    ):
        entry = {
            'citation_key': 'force2023',
            'fields': {'preview': 'p.jpg', 'pdf': 'f.pdf', 'title': 'T'},
        }
        result = entry_processor.process_entry(
            entry,
            regenerate=False,
            force=True,
            incremental=False,
            update_metadata=False,
            thumbnail_size='600x',
            verbose=False,
            force_refetch_metadata=False,
            rename_only=False,
        )
        assert result is True
        mock_process_files.assert_called_once()

    @patch.object(EntryProcessor, 'process_entry_files')
    @patch.object(EntryProcessor, 'is_entry_processed', return_value=True)
    def test_force_false_skips_when_processed(
        self, mock_is_processed, mock_process_files, entry_processor
    ):
        entry = {
            'citation_key': 'skip2023',
            'fields': {'preview': 'p.jpg', 'pdf': 'f.pdf'},
        }
        result = entry_processor.process_entry(
            entry,
            regenerate=False,
            force=False,
            incremental=False,
            update_metadata=False,
            thumbnail_size='600x',
            verbose=False,
            force_refetch_metadata=False,
            rename_only=False,
        )
        assert result is True
        mock_process_files.assert_not_called()

    def test_regenerate_cleanup_keeps_unmanaged_files(self, tmp_path, config):
        pdf_dir = tmp_path / 'pdf'
        preview_dir = tmp_path / 'preview'
        zip_dir = tmp_path / 'zips'
        images_dir = tmp_path / 'images'
        audio_dir = tmp_path / 'audio'
        for d in (pdf_dir, preview_dir, zip_dir, images_dir, audio_dir):
            d.mkdir()

        (pdf_dir / 'paper.pdf').write_text('x')
        (pdf_dir / 'keep.txt').write_text('keep')
        (preview_dir / 'thumb.jpeg').write_text('x')
        (preview_dir / 'notes.md').write_text('keep')
        (zip_dir / 'a.zip').write_text('x')
        (zip_dir / 'readme.txt').write_text('keep')

        processor = PaperProcessor(config)
        processor.config.PDF_DIR = str(pdf_dir)
        processor.config.PREVIEW_DIR = str(preview_dir)
        processor.config.ZIP_DIR = str(zip_dir)
        processor.config.IMAGES_DIR = str(images_dir)
        processor.config.AUDIO_DIR = str(audio_dir)

        processor._cleanup_existing_files()

        assert not (pdf_dir / 'paper.pdf').exists()
        assert (pdf_dir / 'keep.txt').exists()
        assert not (preview_dir / 'thumb.jpeg').exists()
        assert (preview_dir / 'notes.md').exists()
        assert not (zip_dir / 'a.zip').exists()
        assert (zip_dir / 'readme.txt').exists()

    def test_filename_collision_produces_unique_names(self, config):
        text_processor = TextProcessor(config)
        fields = {
            'title': 'Same Title Collision',
            'author': 'Other, Author',
            'year': '2024',
        }
        session = set()
        first = text_processor.generate_filename(
            'entry_a', fields, 'pdf', existing_filenames=session
        )
        second = text_processor.generate_filename(
            'entry_b', fields, 'pdf', existing_filenames=session
        )
        assert first is not None and second is not None
        assert first != second
        assert first in session and second in session

    def test_thumbnail_fallback_second_source_succeeds(self, entry_processor):
        with patch.object(entry_processor, 'bibtex_processor') as mock_bibtex, \
             patch.object(entry_processor, '_process_single_thumbnail_file') as mock_single:
            mock_bibtex.get_thumbnail_priority_files.return_value = [
                {'path': '/missing/thumb.svg', 'type': 'svg', 'priority': 1},
                {'path': '/ok/slides.pdf', 'type': 'pdf', 'priority': 2},
            ]
            mock_single.side_effect = [False, True]
            fields = {'file': 'x', 'title': 'T', 'year': '2020'}
            result = entry_processor._process_thumbnails_with_priority(
                'fb2020', fields, regenerate=False, force=False,
                thumbnail_size='600x', verbose=False,
            )
            assert result is True
            assert mock_single.call_count == 2


@pytest.mark.unit
class TestCliFailureStatuses:
    """Req 99: library / validation failures surface as failure."""

    def test_library_missing_bib_system_exit(self, tmp_path):
        gen = LibraryPageGenerator(
            bib_file=str(tmp_path / 'missing.bib'),
            output_dir=str(tmp_path / 'out'),
            skip_dynamic_filters=True,
        )
        with pytest.raises(SystemExit) as exc:
            gen.load_bibliography()
        assert exc.value.code == 1

    def test_enhanced_validator_empty_parse_all_passed_false(self, tmp_path, config):
        bib = tmp_path / 'garbage.bib'
        bib.write_text('this is not bibtex {{{{\n', encoding='utf-8')
        validator = EnhancedValidator(config)
        results = validator.validate_bibtex_file(str(bib))
        assert results['all_passed'] is False
        assert results['failed_entries'] >= 1
        assert any('Failed to parse' in e for e in results['errors'])

    def test_normalize_previews_flag_is_utility_only(self):
        main_src = Path(__file__).resolve().parents[2] / 'processing' / 'main.py'
        src = main_src.read_text(encoding='utf-8')
        assert "--normalize-previews" in src
        assert "run_normalize_previews" in src
        assert "normalize_preview_directory" in src
