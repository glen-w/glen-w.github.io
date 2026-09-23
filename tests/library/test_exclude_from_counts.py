#!/usr/bin/env python3
"""Tests for library exclude-from-counts helpers and filter integration."""

from pathlib import Path

import pytest
import yaml

from processing.library.catalog import CatalogGenerator
from processing.library.dynamic_filters import DynamicFiltersGenerator
from processing.library.exclude_from_counts import (
    entry_is_excluded,
    filter_timeline_repos,
    load_exclude_tokens,
    load_timeline_exclude_names,
    repo_is_excluded,
)


@pytest.mark.library
@pytest.mark.unit
class TestExcludeFromCounts:
    def test_load_tokens_from_list(self, library_project_root: Path):
        path = library_project_root / "_data" / "library_exclude_from_counts.yml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            '- "The Dark Frontier: Unlocking the Secrets of the Deep Sea"\n'
            "- DarkFrontier\n",
            encoding="utf-8",
        )
        tokens = load_exclude_tokens(str(library_project_root))
        assert "the dark frontier: unlocking the secrets of the deep sea" in tokens
        assert "darkfrontier" in tokens

    def test_missing_file_is_empty(self, library_project_root: Path):
        assert load_exclude_tokens(str(library_project_root)) == set()

    def test_match_by_title_or_id(self):
        tokens = {"the dark frontier: unlocking the secrets of the deep sea"}
        assert entry_is_excluded(
            {
                "ID": "DarkFrontier",
                "title": "The Dark Frontier: Unlocking the Secrets of the Deep Sea",
            },
            tokens,
        )
        assert entry_is_excluded({"ID": "other", "title": "Other Book"}, tokens) is False
        assert entry_is_excluded(
            {"ID": "DarkFrontier", "title": "Other"},
            {"darkfrontier"},
        )

    def test_filters_omit_excluded_from_counts(self, library_project_root: Path):
        path = library_project_root / "_data" / "library_exclude_from_counts.yml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            '- "The Dark Frontier: Unlocking the Secrets of the Deep Sea"\n',
            encoding="utf-8",
        )
        entries = [
            {
                "ID": "mine",
                "ENTRYTYPE": "book",
                "title": "My Book",
                "annote": "[type]\nBook\n[role]\nauthor",
            },
            {
                "ID": "DarkFrontier",
                "ENTRYTYPE": "book",
                "title": "The Dark Frontier: Unlocking the Secrets of the Deep Sea",
                "annote": "[type]\nBook\n[role]\ninterview\nquoted",
            },
            {
                "ID": "other",
                "ENTRYTYPE": "book",
                "title": "Another Book",
                "annote": "[type]\nBook\n[role]\nauthor",
            },
        ]
        DynamicFiltersGenerator(str(library_project_root)).generate_filters(entries)
        data = yaml.safe_load(
            (library_project_root / "_data" / "dynamic_filters.yml").read_text()
        )
        assert data["entry_type_counts"]["Book"] == 2
        assert data["role_tag_counts"]["author"] == 2
        assert "interview" not in data["role_tag_counts"]
        assert "quoted" not in data["role_tag_counts"]
        assert "Book" in data["entry_types"]

    def test_catalog_marks_nocount_and_parity(self, library_project_root: Path):
        path = library_project_root / "_data" / "library_exclude_from_counts.yml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("- DarkFrontier\n", encoding="utf-8")
        entries = [
            {
                "ID": "mine",
                "ENTRYTYPE": "book",
                "title": "My Book",
                "year": "2020",
                "annote": "[type]\nBook\n[role]\nauthor",
            },
            {
                "ID": "DarkFrontier",
                "ENTRYTYPE": "book",
                "title": "The Dark Frontier: Unlocking the Secrets of the Deep Sea",
                "year": "2026",
                "annote": "[type]\nBook\n[role]\ninterview",
            },
        ]
        DynamicFiltersGenerator(str(library_project_root)).generate_filters(entries)
        catalog, _ = CatalogGenerator(str(library_project_root)).generate(
            entries, check_parity=True
        )
        by_id = {item["id"]: item for item in catalog["items"]}
        assert by_id["DarkFrontier"].get("nocount") is True
        assert "nocount" not in by_id["mine"]
        filters = yaml.safe_load(
            (library_project_root / "_data" / "dynamic_filters.yml").read_text()
        )
        assert filters["entry_type_counts"]["Book"] == 1


@pytest.mark.library
@pytest.mark.unit
class TestTimelineExclude:
    def test_load_repo_names(self, library_project_root: Path):
        path = library_project_root / "_data" / "library_exclude_from_timeline.yml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("- hoops\n- glen-w/folk-directory\n", encoding="utf-8")
        tokens = load_timeline_exclude_names(str(library_project_root))
        assert tokens == {"hoops", "glen-w/folk-directory"}

    def test_missing_timeline_file_is_empty(self, library_project_root: Path):
        assert load_timeline_exclude_names(str(library_project_root)) == set()

    def test_match_short_name_or_full_name(self):
        tokens = {"hoops", "glen-w/folk-directory", "academia_obscura"}
        assert repo_is_excluded({"id": "glen-w/hoops", "name": "hoops"}, tokens)
        assert repo_is_excluded(
            {"repo": "glen-w/folk-directory", "title": "folk-directory"}, tokens
        )
        assert repo_is_excluded(
            {"id": "glen-w/academia_obscura", "name": "academia_obscura"}, tokens
        )
        assert repo_is_excluded({"id": "glen-w/Paperful", "name": "Paperful"}, tokens) is False

    def test_filter_drops_excluded_repos_and_year_marks(self):
        tokens = {"hoops", "glen-w.github.io"}
        repos = [
            {"id": "glen-w/hoops", "name": "hoops"},
            {"id": "glen-w/Paperful", "name": "Paperful"},
            {"id": "glen-w/glen-w.github.io", "name": "glen-w.github.io"},
        ]
        kept = filter_timeline_repos(repos, tokens)
        assert [row["name"] for row in kept] == ["Paperful"]
        marks = [
            {"id": "repo:glen-w/hoops:2026", "repo": "glen-w/hoops", "title": "hoops"},
            {
                "id": "repo:glen-w/Paperful:2026",
                "repo": "glen-w/Paperful",
                "title": "Paperful",
            },
        ]
        kept_marks = filter_timeline_repos(marks, tokens)
        assert [row["title"] for row in kept_marks] == ["Paperful"]
