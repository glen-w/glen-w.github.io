"""Tests for the co-author collaboration graph builder."""

from pathlib import Path

import pytest
import yaml

from processing.library.bib_parser import BibParser
from processing.library.coauthors import (
    CLIQUE_AUTHOR_LIMIT,
    build_coauthor_graph,
    collaborators_list,
    write_coauthor_artifacts,
)


def _author(first: str, last: str) -> dict:
    return {"first": first, "last": last, "full": f"{last}, {first}"}


def _entry(entry_id: str, authors: str, *, year: str = "2020", title: str = "A Paper") -> dict:
    return {
        "ID": entry_id,
        "ENTRYTYPE": "article",
        "title": title,
        "author": authors,
        "year": year,
    }


def _item(entry_id: str, *, title: str = "A Paper", year: int = 2020, path: str = "") -> dict:
    row = {
        "id": entry_id,
        "title": title,
        "year": year,
    }
    if path:
        row["info"] = path
    return row


@pytest.mark.library
@pytest.mark.unit
class TestCoauthorGraph:
    def test_merges_glen_wright_and_g_wright(self):
        entries = [
            _entry("One", "Wright, Glen and Doe, Jane", year="2018"),
            _entry("Two", "Wright, G. and Doe, Jane", year="2021"),
        ]
        items = [
            _item("One", year=2018, path="/library/one/"),
            _item("Two", year=2021, path="/library/two/"),
        ]
        graph = build_coauthor_graph(entries, items)
        people = {person["id"]: person for person in graph["people"]}
        assert "glen-wright" in people
        assert people["glen-wright"]["self"] is True
        assert people["glen-wright"]["name"] == "Glen Wright"
        assert people["glen-wright"]["count"] == 2
        assert len([p for p in graph["people"] if p["id"].startswith("g-wright")]) == 0
        jane = next(p for p in graph["people"] if "doe" in p["id"] or "Jane" in p["name"])
        assert jane["count"] == 2

    def test_initial_attaches_to_single_full_name(self):
        entries = [
            _entry("A", "Wright, Glen and Rochette, J.", year="2015"),
            _entry("B", "Wright, Glen and Rochette, Julien", year="2016"),
        ]
        items = [_item("A", year=2015), _item("B", year=2016)]
        graph = build_coauthor_graph(entries, items)
        people = {person["name"]: person for person in graph["people"]}
        assert "Julien Rochette" in people
        assert people["Julien Rochette"]["count"] == 2
        assert "J. Rochette" not in people

    def test_ambiguous_initial_left_unmatched(self):
        entries = [
            _entry("A", "Wright, Glen and Smith, John", year="2015"),
            _entry("B", "Wright, Glen and Smith, Jane", year="2016"),
            _entry("C", "Wright, Glen and Smith, J.", year="2017"),
        ]
        items = [_item("A", year=2015), _item("B", year=2016), _item("C", year=2017)]
        graph = build_coauthor_graph(entries, items)
        names = {person["name"] for person in graph["people"]}
        assert "John Smith" in names
        assert "Jane Smith" in names
        assert "J. Smith" in names
        john = next(p for p in graph["people"] if p["name"] == "John Smith")
        jane = next(p for p in graph["people"] if p["name"] == "Jane Smith")
        initial = next(p for p in graph["people"] if p["name"] == "J. Smith")
        assert john["count"] == 1
        assert jane["count"] == 1
        assert initial["count"] == 1

    def test_large_author_list_does_not_create_coauthor_clique(self):
        others = [f"Author{i}, First{i}" for i in range(CLIQUE_AUTHOR_LIMIT)]
        # Glen + 8 others = 9 authors → star only
        author_field = " and ".join(["Wright, Glen"] + others)
        entries = [_entry("Big", author_field, year="2022")]
        items = [_item("Big", year=2022, path="/library/big/")]
        graph = build_coauthor_graph(entries, items)

        assert len(graph["people"]) == 1 + CLIQUE_AUTHOR_LIMIT
        for edge in graph["edges"]:
            assert "glen-wright" in (edge["source"], edge["target"])
        # No edge solely between two co-authors
        coauthor_only = [
            edge
            for edge in graph["edges"]
            if edge["source"] != "glen-wright" and edge["target"] != "glen-wright"
        ]
        assert coauthor_only == []
        assert len(graph["edges"]) == CLIQUE_AUTHOR_LIMIT

    def test_small_author_list_forms_clique(self):
        entries = [
            _entry(
                "Trio",
                "Wright, Glen and Doe, Jane and Roe, Richard",
                year="2019",
            )
        ]
        items = [_item("Trio", year=2019)]
        graph = build_coauthor_graph(entries, items)
        pairs = {
            frozenset((edge["source"], edge["target"])) for edge in graph["edges"]
        }
        assert len(pairs) == 3  # Glen–Jane, Glen–Richard, Jane–Richard

    def test_edge_weight_counts_shared_works(self):
        entries = [
            _entry("One", "Wright, Glen and Doe, Jane", year="2018"),
            _entry("Two", "Wright, Glen and Doe, Jane", year="2019"),
            _entry("Three", "Wright, Glen and Doe, Jane and Roe, Richard", year="2020"),
        ]
        items = [
            _item("One", year=2018),
            _item("Two", year=2019),
            _item("Three", year=2020),
        ]
        graph = build_coauthor_graph(entries, items)
        glen_jane = next(
            edge
            for edge in graph["edges"]
            if frozenset((edge["source"], edge["target"]))
            == frozenset(("glen-wright", next(p["id"] for p in graph["people"] if "Doe" in p["name"])))
        )
        assert glen_jane["count"] == 3
        assert set(glen_jane["works"]) == {"One", "Two", "Three"}

    def test_library_path_present_on_works(self):
        entries = [_entry("Pathy", "Wright, Glen and Doe, Jane")]
        items = [_item("Pathy", path="/library/pathy-paper/")]
        graph = build_coauthor_graph(entries, items)
        assert len(graph["works"]) == 1
        assert graph["works"][0]["path"] == "/library/pathy-paper/"
        assert graph["works"][0]["id"] == "Pathy"

    def test_alias_file_forces_merge(self, tmp_path: Path):
        data_dir = tmp_path / "_data"
        data_dir.mkdir()
        (data_dir / "coauthor_aliases.yml").write_text(
            "- name: Julien Rochette\n  aliases:\n    - Jules Rochette\n",
            encoding="utf-8",
        )
        # Nickname would not auto-merge without the alias file
        entries = [
            _entry("A", "Wright, Glen and Rochette, Julien", year="2015"),
            _entry("B", "Wright, Glen and Rochette, Jules", year="2016"),
        ]
        items = [_item("A", year=2015), _item("B", year=2016)]
        graph = build_coauthor_graph(entries, items, project_root=str(tmp_path))
        names = {person["name"] for person in graph["people"]}
        assert "Julien Rochette" in names
        assert "Jules Rochette" not in names
        julien = next(p for p in graph["people"] if p["name"] == "Julien Rochette")
        assert julien["count"] == 2

    def test_write_artifacts_and_collaborators_list(self, tmp_path: Path):
        entries = [
            _entry("One", "Wright, Glen and Doe, Jane", year="2018"),
            _entry("Two", "Wright, Glen and Doe, Jane", year="2019"),
            _entry("Three", "Wright, Glen and Solo, Sam", year="2020"),
        ]
        items = [
            _item("One", year=2018, path="/library/one/"),
            _item("Two", year=2019, path="/library/two/"),
            _item("Three", year=2020, path="/library/three/"),
        ]
        graph = build_coauthor_graph(entries, items)
        graph_path, list_path = write_coauthor_artifacts(str(tmp_path), graph)
        assert Path(graph_path).is_file()
        assert Path(list_path).is_file()
        rows = collaborators_list(graph)
        names = {row["name"] for row in rows}
        assert "Jane Doe" in names
        assert "Sam Solo" not in names  # only one shared work
        dumped = yaml.safe_load(Path(list_path).read_text(encoding="utf-8"))
        assert dumped[0]["name"] == "Jane Doe"
        assert dumped[0]["count"] == 2
