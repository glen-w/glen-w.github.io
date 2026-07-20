#!/usr/bin/env python3
"""
Static Liquid / HTML contract tests for library header actions (requirement 100).

Loads Liquid includes as text (no Jekyll) and asserts a11y / action markup patterns.
Also checks static HTML fixtures under tests/fixtures/rendering/.
"""

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ACTIONS_LIQUID = PROJECT_ROOT / '_includes' / 'library' / 'actions.liquid'
HERO_LIQUID = PROJECT_ROOT / '_includes' / 'library' / 'hero.liquid'
FIXTURES = Path(__file__).resolve().parents[1] / 'fixtures' / 'rendering'


@pytest.fixture(scope='module')
def actions_src() -> str:
    return ACTIONS_LIQUID.read_text(encoding='utf-8')


@pytest.fixture(scope='module')
def hero_src() -> str:
    return HERO_LIQUID.read_text(encoding='utf-8')


@pytest.mark.rendering
@pytest.mark.library
class TestActionsLiquidContract:
    def test_role_group_and_aria_label(self, actions_src):
        assert 'role="group"' in actions_src
        assert 'aria-label="Document actions"' in actions_src

    def test_primary_button_class(self, actions_src):
        assert 'library-btn-primary' in actions_src
        assert 'library-btn' in actions_src

    def test_noopener_noreferrer_on_links(self, actions_src):
        assert 'rel="noopener noreferrer"' in actions_src

    def test_keyboard_focusable_anchors(self, actions_src):
        assert '<a' in actions_src
        assert 'href=' in actions_src


@pytest.mark.rendering
@pytest.mark.library
class TestHeroLiquidContract:
    def test_preview_img_pattern(self, hero_src):
        assert 'class="img-fluid library-thumbnail"' in hero_src
        assert 'alt="Cover image for {{ page.title }}"' in hero_src
        assert 'onerror=' in hero_src

    def test_fallback_thumbnail_include(self, hero_src):
        assert "include library/fallback_thumbnail.liquid" in hero_src

    def test_actions_include(self, hero_src):
        assert 'include library/actions.liquid' in hero_src


@pytest.mark.rendering
@pytest.mark.library
class TestRenderingFixtures:
    def test_with_primary_pdf(self):
        html = (FIXTURES / 'with_primary_pdf.html').read_text(encoding='utf-8')
        assert 'role="group"' in html
        assert 'aria-label="Document actions"' in html
        assert 'library-btn-primary' in html
        assert 'href="/assets/pdf/sample.pdf"' in html
        assert 'rel="noopener noreferrer"' in html
        assert '<a' in html

    def test_with_video_and_landing(self):
        html = (FIXTURES / 'with_video_and_landing.html').read_text(encoding='utf-8')
        assert 'https://youtu.be/abc123' in html
        assert 'https://example.com/event' in html
        assert 'library-btn-secondary' in html
        assert 'rel="noopener noreferrer"' in html

    def test_empty_resources_no_actions(self):
        html = (FIXTURES / 'empty_resources.html').read_text(encoding='utf-8')
        assert 'library-actions' not in html
        assert 'aria-label="Document actions"' not in html

    def test_broken_preview_alt_and_onerror(self):
        html = (FIXTURES / 'broken_preview.html').read_text(encoding='utf-8')
        assert 'alt="Cover image for Broken Preview Title"' in html
        assert 'onerror=' in html
        assert 'src="/assets/img/publication_preview/missing.jpeg"' in html
        # Documented: empty src is not used; broken/missing files rely on onerror chain
        assert 'src=""' not in html
