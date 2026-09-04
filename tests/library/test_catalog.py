"""Tests for the library catalog generator (default suite: tests/library)."""

import json
from pathlib import Path

import pytest
import yaml

from processing.library.bib_parser import BibParser
from processing.library.catalog import CatalogGenerator, CatalogParityError, MAX_AUTHOR_LIMIT
from processing.library.generator import LibraryPageGenerator


GOLDEN_IDS = [
    "Wright2011a",
    "Wright2016a",
    "Rochette2015b",
    "HighSeasTreaty2023",
    "rochetteVersProtectionHaute2018",
    "FossilFoolsDay2007",
]

REPO_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_PATH = Path(__file__).resolve().parent / "golden" / "catalog_expected.json"


@pytest.fixture
def generator(library_project_root):
    return CatalogGenerator(
        str(library_project_root),
        library_dir=str(library_project_root / "_library"),
    )


def _entry(**kwargs):
    entry = {
        "ID": "TestKey",
        "ENTRYTYPE": "article",
        "title": "A Test Title",
        "author": "Wright, Glen and Doe, Jane",
        "year": "2020",
        "journal": "Test Journal",
        "annote": "[type]\njournal article\n[role]\nlead author",
    }
    entry.update(kwargs)
    return entry


@pytest.mark.library
@pytest.mark.unit
class TestJekyllPageSlug:
    def test_underscores_become_hyphens(self):
        stem = "glen_wright_denmark-how-long-term-policy"
        assert CatalogGenerator.jekyll_page_slug(stem) == (
            "glen-wright-denmark-how-long-term-policy"
        )

    def test_hyphen_only_slug_is_unchanged(self):
        assert CatalogGenerator.jekyll_page_slug("fossil-fools-day") == "fossil-fools-day"

    def test_library_index_uses_jekyll_slug(self, tmp_path):
        library_dir = tmp_path / "custom_library"
        library_dir.mkdir()
        (library_dir / "glen_wright_example-title.md").write_text(
            "---\nbibtex_key: ExampleKey\n---\n",
            encoding="utf-8",
        )
        gen = CatalogGenerator(str(tmp_path), library_dir=str(library_dir))
        page = gen._get_library_index()["ExampleKey"]
        assert page["slug"] == "glen-wright-example-title"
        assert page["info"] == "/library/glen-wright-example-title/"


@pytest.mark.library
@pytest.mark.unit
class TestAuthorShortForm:
    def test_omits_solo_author(self):
        authors = [{"first": "Glen", "last": "Wright", "full": "Wright, Glen"}]
        assert CatalogGenerator.format_authors_short(authors) is None

    def test_two_authors_use_and(self):
        authors = [
            {"first": "Glen", "last": "Wright", "full": "Wright, Glen"},
            {"first": "David", "last": "Leary", "full": "Leary, David"},
        ]
        result = CatalogGenerator.format_authors_short(authors)
        assert result["text"] == "Glen Wright and David Leary"
        assert "<em>Glen Wright</em>" in result["html"]
        assert "et al." not in result["text"]

    def test_three_authors_use_and_before_last(self):
        authors = [
            {"first": "Julien", "last": "Rochette", "full": "Rochette, Julien"},
            {"first": "Isabel", "last": "Seeger", "full": "Seeger, Isabel"},
            {"first": "Glen", "last": "Wright", "full": "Wright, Glen"},
        ]
        result = CatalogGenerator.format_authors_short(authors)
        assert result["text"] == "Julien Rochette, Isabel Seeger, and Glen Wright"

    def test_more_than_limit_uses_et_al(self):
        authors = [
            {"first": f"First{i}", "last": f"Last{i}", "full": f"Last{i}, First{i}"}
            for i in range(MAX_AUTHOR_LIMIT + 2)
        ]
        result = CatalogGenerator.format_authors_short(authors)
        assert result["text"].endswith(" et al.")
        assert result["text"].count(",") == MAX_AUTHOR_LIMIT - 1


@pytest.mark.library
@pytest.mark.unit
class TestCatalogBuild:
    def test_journal_article_list_fields(self, generator):
        entry = _entry(
            pdf="example.pdf",
            preview="example.jpeg",
            doi="10.1000/test",
            abstract="Hello abstract.",
        )
        item, detail = generator.build_item(entry)
        assert item["id"] == "TestKey"
        assert item["type"] == "Journal Article"
        assert item["roles"] == ["lead author"]
        assert item["authors"] == "Glen Wright and Jane Doe"
        assert item["venue"] == "Test Journal"
        assert item["pdf"] == "/assets/pdf/example.pdf"
        assert item["thumb"] == "/assets/img/publication_preview/example-480.webp"
        assert item["doi"] == "https://doi.org/10.1000/test"
        assert "abs" in item["flags"]
        assert "selected" not in item
        assert detail["abstract"] == "Hello abstract."
        assert "photos" not in item.get("flags", [])

    def test_missing_preview_omits_thumb(self, generator):
        item, _detail = generator.build_item(_entry())
        assert "thumb" not in item

    def test_book_and_book_chapter_are_exact_types(self, generator):
        """Client chips match type with ===, so Book must not collide with Book Chapter."""
        book, _ = generator.build_item(
            _entry(ID="BookKey", annote="[type]\nbook\n[role]\nauthor")
        )
        chapter, _ = generator.build_item(
            _entry(ID="ChapKey", annote="[type]\nbook chapter\n[role]\nauthor")
        )
        assert book["type"] == "Book"
        assert chapter["type"] == "Book Chapter"
        assert book["type"] != chapter["type"]

    def test_multi_role_and_no_authors(self, generator):
        entry = _entry(
            ID="NoAuthor",
            author="",
            ENTRYTYPE="misc",
            annote="[type]\nwebinar\n[role]\nfacilitator\nspeaker\n[video]\nhttps://youtu.be/abc",
        )
        item, _detail = generator.build_item(entry)
        assert item["type"] == "Webinar"
        assert item["roles"] == ["facilitator", "speaker"]
        assert "authors" not in item
        assert item["video"] == "https://youtu.be/abc"
        assert "video" in item["flags"]
        assert "speakers" not in item.get("flags", [])

    def test_language_and_odd_type(self, generator):
        entry = _entry(
            annote="[type]\nreport section\n[role]\nco-author\n[language]\nfrench",
            author="Rochette, Julien and Wright, Glen",
        )
        item, _detail = generator.build_item(entry)
        assert item["type"] == "Report Section"
        assert item["roles"] == ["co-author"]
        assert item["langs"] == ["french"]

    def test_selected_from_bib_field(self, generator):
        item, _detail = generator.build_item(_entry(selected="true"))
        assert item["selected"] is True

    def test_selected_from_annote(self, generator):
        item, _detail = generator.build_item(
            _entry(annote="[type]\njournal article\n[role]\nauthor\n[selected]")
        )
        assert item["selected"] is True

    def test_photos_go_to_details_not_list_payload(self, generator):
        entry = _entry(photos="talk_photo_01.jpg, thumbnail.jpg")
        item, detail = generator.build_item(entry)
        assert "photos" in item["flags"]
        assert "photos" not in item
        assert detail["photos"] == [
            {
                "src": "/assets/img/publications/talk_photo_01.jpg",
                "alt": "Photo",
            }
        ]

    def test_generate_writes_json_and_selected_yaml(self, generator, library_project_root):
        entries = [
            _entry(ID="One", selected="true", pdf="one.pdf"),
            _entry(
                ID="Two",
                title="Second",
                year="2019",
                annote="[type]\nblog\n[role]\nauthor",
            ),
        ]
        catalog, details = generator.generate(entries, check_parity=True)
        assert [item["id"] for item in catalog["items"]] == ["One", "Two"]

        catalog_path = library_project_root / "assets" / "json" / "library.json"
        details_path = library_project_root / "assets" / "json" / "library-details.json"
        selected_path = library_project_root / "_data" / "library_selected.yml"
        dumped = json.loads(catalog_path.read_text(encoding="utf-8"))
        assert dumped["items"][0]["id"] == "One"
        assert details_path.is_file()
        selected = yaml.safe_load(selected_path.read_text(encoding="utf-8"))
        assert len(selected) == 1
        assert selected[0]["id"] == "One"
        assert isinstance(details, dict)

    def test_parity_fails_on_count_drift(self, generator):
        catalog = {"v": 1, "items": [{"id": "OnlyOne", "title": "x", "year": 1, "type": "Blog"}]}
        with pytest.raises(CatalogParityError):
            generator.assert_parity(catalog, [_entry(ID="A"), _entry(ID="B")])


@pytest.mark.library
@pytest.mark.requires_bibtexparser
class TestGoldenFixtures:
    def test_real_bib_golden_entries(self):
        bib_path = REPO_ROOT / "_bibliography" / "papers.bib"
        if not bib_path.is_file():
            pytest.skip("papers.bib not available")

        page_gen = LibraryPageGenerator(
            bib_file=str(bib_path),
            output_dir=str(REPO_ROOT / "_library"),
        )
        entries = page_gen.load_bibliography()
        by_id = {entry["ID"]: entry for entry in entries if entry.get("ID")}
        catalog_gen = CatalogGenerator(str(REPO_ROOT))

        expected = json.loads(EXPECTED_PATH.read_text(encoding="utf-8"))

        parser = BibParser()
        for key in GOLDEN_IDS:
            assert key in by_id, f"golden id {key} missing from papers.bib"
            item, detail = catalog_gen.build_item(by_id[key])
            want = expected[key]
            for field, value in want["item"].items():
                assert item.get(field) == value, f"{key}.{field}"
            if "thumb" not in want["item"]:
                assert "thumb" not in item, f"{key} unexpectedly has a thumb"
            for field, value in want.get("detail", {}).items():
                if field == "has_abstract":
                    assert bool(detail.get("abstract")) is value, f"{key}.detail.abstract"
                else:
                    assert detail.get(field) == value, f"{key}.detail.{field}"
            authors = parser.format_authors(by_id[key])
            short = CatalogGenerator.format_authors_short(authors)
            if short:
                assert item["authors"] == short["text"]
            else:
                assert "authors" not in item
