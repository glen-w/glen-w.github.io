#!/usr/bin/env python3
"""Contract tests for the personality pack in the live tree."""

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
class TestPersonalityPack:
    def test_live_core_files_exist(self) -> None:
        expected = [
            ROOT / "assets" / "js" / "personality.js",
            ROOT / "_sass" / "_personality.scss",
            ROOT / "docs" / "dev" / "personality-pack-notes.md",
        ]
        missing = [str(p.relative_to(ROOT)) for p in expected if not p.is_file()]
        assert missing == []
        assert not (ROOT / "_includes" / "personality-chip.liquid").is_file()
        assert not (ROOT / "_data" / "now.yml").is_file()

    def test_accent_and_intensity_dial(self) -> None:
        scss = (ROOT / "_sass" / "_personality.scss").read_text(encoding="utf-8")
        assert "--personality-accent: #3d5f5c" in scss
        assert "--personality-accent: #8aa8a4" in scss
        for token in (
            "--personality-ease",
            "--personality-reveal-y",
            "--personality-reveal-ms",
            "--personality-lift",
        ):
            assert token in scss
        assert "--personality-parallax" not in scss
        assert ".personality-chip" not in scss
        assert "will-change" not in scss
        assert "prefers-reduced-motion: reduce" in scss
        assert "@view-transition" in scss
        assert '.card[data-category="collage"]' in scss
        assert "rotate(1deg)" in scss
        assert ".publications .links a.btn" in scss
        assert ".publications .card[data-category" not in scss

    def test_reveal_allowlist_skips_library_cards(self) -> None:
        js = (ROOT / "assets" / "js" / "personality.js").read_text(encoding="utf-8")
        assert "#libraryResults" in js
        assert ".publications li" not in js
        assert "main article > *" not in js
        assert "#libraryApp > .library-search" in js
        assert "prefers-reduced-motion" in js
        assert "initParallax" not in js
        assert "js-personality-portrait" not in js
        assert "will-change" not in js
        assert "webgl" not in js.lower()
        assert "particle" not in js.lower()

    def test_hooks_wired_and_sandbox_config_not_copied(self) -> None:
        main_scss = (ROOT / "assets" / "css" / "main.scss").read_text(encoding="utf-8")
        assert '"personality"' in main_scss
        scripts = (ROOT / "_includes" / "scripts.liquid").read_text(encoding="utf-8")
        assert "personality.js" in scripts
        header = (ROOT / "_includes" / "header.liquid").read_text(encoding="utf-8")
        assert "personality-chip.liquid" not in header
        about = (ROOT / "_layouts" / "about.liquid").read_text(encoding="utf-8")
        assert "js-personality-portrait" not in about
        default = (ROOT / "_layouts" / "default.liquid").read_text(encoding="utf-8")
        assert "data-personality" in default
        config = yaml.safe_load((ROOT / "_config.yml").read_text(encoding="utf-8"))
        assert config.get("personality", {}).get("enabled") is True
        assert config.get("enable_darkmode") is False
        assert (config.get("imagemagick") or {}).get("enabled") is True
        exclude = config.get("exclude") or []
        assert "assets/pdf/" not in exclude
        assert "sandbox/" in exclude

    def test_sandbox_gitignored(self) -> None:
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        assert "sandbox/personality-site/" in gitignore
