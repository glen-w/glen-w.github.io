#!/usr/bin/env python3
"""
Contract tests for homepage / chrome infra (canonical, socials, script gating,
featured publications). Static file assertions — no Jekyll, no network.
"""

import hashlib
import random
import re
from pathlib import Path

import pytest
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG = PROJECT_ROOT / '_config.yml'
SOCIALS = PROJECT_ROOT / '_data' / 'socials.yml'
SCRIPTS = PROJECT_ROOT / '_includes' / 'scripts.liquid'
FIGURE = PROJECT_ROOT / '_includes' / 'figure.liquid'
DEFAULT = PROJECT_ROOT / '_layouts' / 'default.liquid'
HEADER = PROJECT_ROOT / '_includes' / 'header.liquid'
FOOTER = PROJECT_ROOT / '_includes' / 'footer.liquid'
ABOUT = PROJECT_ROOT / '_layouts' / 'about.liquid'
BIB_HOME = PROJECT_ROOT / '_layouts' / 'bib_home.liquid'
SELECTED = PROJECT_ROOT / '_includes' / 'selected_papers_home.liquid'
PLUGIN = PROJECT_ROOT / '_plugins' / 'homepage_publications.rb'
BLOG = PROJECT_ROOT / '_pages' / 'blog.md'
DROPDOWN = PROJECT_ROOT / '_pages' / 'dropdown.md'
SITEMAP = PROJECT_ROOT / '_pages' / 'sitemap.md'
CREATIVE = PROJECT_ROOT / '_pages' / 'creative.md'
LIBRARY = PROJECT_ROOT / '_pages' / 'library.md'
CNAME = PROJECT_ROOT / 'CNAME'
PAPERS = PROJECT_ROOT / '_bibliography' / 'papers.bib'


def _front_matter(path: Path) -> dict:
    text = path.read_text(encoding='utf-8')
    assert text.startswith('---'), f'{path} missing front matter'
    return yaml.safe_load(text.split('---', 2)[1]) or {}


def _selected_entries(bib_text: str) -> list[tuple[str, int]]:
    """Return (key, year) for entries with selected = {true}."""
    entries = []
    for block in re.split(r'\n(?=@)', bib_text):
        if 'selected = {true}' not in block and 'selected={true}' not in block:
            continue
        key_match = re.search(r'@\w+\{([^,]+),', block)
        year_match = re.search(r'\byear\s*=\s*\{?(\d{4})\}?', block, re.I)
        if key_match and year_match:
            entries.append((key_match.group(1).strip(), int(year_match.group(1))))
    return entries


@pytest.mark.library
class TestSeoContracts:
    def test_site_url_is_custom_domain(self):
        config = CONFIG.read_text(encoding='utf-8')
        assert re.search(r'^url:\s*https://glenwright\.earth\b', config, re.M)

    def test_cname_file(self):
        assert CNAME.read_text(encoding='utf-8').strip() == 'glenwright.earth'

    def test_description_present(self):
        config = yaml.safe_load(CONFIG.read_text(encoding='utf-8'))
        description = (config.get('description') or '').strip()
        assert 'Glen Wright' in description
        assert 'researcher' in description.lower()

    def test_researchgate_is_slug_not_url(self):
        socials = SOCIALS.read_text(encoding='utf-8')
        match = re.search(r'^research_gate_profile:\s*(\S+)', socials, re.M)
        assert match, 'research_gate_profile missing'
        value = match.group(1)
        assert not value.startswith('http'), value
        assert value == 'Glen-Wright'

    def test_sitemap_page_exists(self):
        fm = _front_matter(SITEMAP)
        assert fm.get('permalink') == '/sitemap/'
        body = SITEMAP.read_text(encoding='utf-8')
        assert '/sitemap.xml' in body
        assert '/library/' in body


@pytest.mark.library
class TestScriptGating:
    def test_math_masonry_zoom_are_opt_in(self):
        src = SCRIPTS.read_text(encoding='utf-8')
        assert 'site.enable_math and page.math' in src
        assert 'site.enable_masonry and page.masonry' in src
        assert 'site.enable_medium_zoom and page.medium_zoom' in src

    def test_ga_not_double_initialized(self):
        src = SCRIPTS.read_text(encoding='utf-8')
        assert "gtag('config'" not in src
        assert 'google-analytics-setup.js' in src
        assert 'googletagmanager.com/gtag/js' in src

    def test_creative_and_library_enable_needed_libs(self):
        creative = _front_matter(CREATIVE)
        library = _front_matter(LIBRARY)
        assert creative.get('masonry') is True
        assert creative.get('medium_zoom') is True
        assert library.get('medium_zoom') is True

    def test_figure_srcset_has_no_trailing_comma(self):
        src = FIGURE.read_text(encoding='utf-8')
        assert 'unless forloop.last' in src
        assert 'webp {{ i }}w,{% endfor %}' not in src


@pytest.mark.library
class TestHomepageChrome:
    def test_main_landmark_and_skip_link(self):
        default = DEFAULT.read_text(encoding='utf-8')
        header = HEADER.read_text(encoding='utf-8')
        assert '<main id="main-content"' in default
        assert 'Skip to main content' in header
        assert 'href="#main-content"' in header

    def test_about_has_h1_and_webp_portrait(self):
        about = ABOUT.read_text(encoding='utf-8')
        assert '<h1 class="about-identity">Glen Wright</h1>' in about
        assert 'Portrait of Glen Wright' in about
        assert 'prof_pic-800.webp' in about or "-800.webp" in about

    def test_blog_in_nav_and_overflow_labeled(self):
        assert _front_matter(BLOG).get('nav') is True
        assert _front_matter(DROPDOWN).get('title') == 'more'

    def test_footer_utility_links(self):
        footer = FOOTER.read_text(encoding='utf-8')
        assert 'footer-links' in footer
        assert "/library/" in footer
        assert "/projects/" in footer
        assert "/cv/" in footer
        assert 'mailto:' in footer


@pytest.mark.library
class TestHomepagePublications:
    def test_plugin_and_include_wired(self):
        plugin = PLUGIN.read_text(encoding='utf-8')
        include = SELECTED.read_text(encoding='utf-8')
        config = yaml.safe_load(CONFIG.read_text(encoding='utf-8'))
        hp = config.get('homepage_publications') or {}
        assert hp.get('max') == 8
        assert hp.get('must_show') == 4
        assert 'homepage_bibliography' in include
        assert '/library/' in include
        assert 'SHA256' in plugin
        assert 'must_show' in plugin

    def test_abstracts_use_details(self):
        bib_home = BIB_HOME.read_text(encoding='utf-8')
        assert '<details class="abstract-details">' in bib_home
        assert '<summary>Abstract</summary>' in bib_home

    def test_selected_pool_supports_eight_four_mix(self):
        entries = _selected_entries(PAPERS.read_text(encoding='utf-8'))
        unique = {key: year for key, year in entries}
        assert len(unique) >= 8
        newest = sorted(unique.items(), key=lambda item: (-item[1], item[0]))[:4]
        years = [year for _, year in newest]
        assert years[0] >= years[-1]
        assert years[0] >= 2022

    def test_date_seed_is_stable(self):
        """Same YYYY-MM-DD hex seed always draws the same remainder sample."""
        remainder = ['a', 'b', 'c', 'd', 'e']
        seed = '2026-09-04'
        seed_int = int(hashlib.sha256(seed.encode()).hexdigest()[:16], 16)
        first = random.Random(seed_int).sample(remainder, k=4)
        second = random.Random(seed_int).sample(remainder, k=4)
        assert first == second


@pytest.mark.library
class TestLibraryIndexShell:
    def test_library_index_is_json_catalog_shell(self):
        src = LIBRARY.read_text(encoding='utf-8')
        assert '{% bibliography' not in src
        assert 'selected_papers' not in src
        assert 'bib_search' not in src
        assert "/assets/js/library.js" in src
        assert "/assets/json/library.json" in src
        assert "/assets/json/library-details.json" in src
        assert 'bust_file_cache' in src
        assert 'site.data.library_selected' in src
        assert 'id="libraryApp"' in src
        assert 'aria-live="polite"' in src

    def test_library_js_jump_retries_and_exact_type_match(self):
        src = (PROJECT_ROOT / 'assets' / 'js' / 'library.js').read_text(encoding='utf-8')
        assert 'jumpToHash({ retry: true })' in src
        assert 'function jumpToHash({ retry = false } = {})' in src
        assert 'textContent = "selected publications"' in src
        assert '(item.type || "") === state.value' in src
        assert 'setTimeout(filterItems(searchTerm), 300)' not in src
