"""Unit tests for citation-network helpers (no network)."""

from processing.library.citations import (
    _merge_scholar_cache,
    citers_list,
    normalize_doi,
    person_slug,
    short_id,
)


def test_normalize_doi():
    assert normalize_doi("https://doi.org/10.1038/s44183-022-00006-2") == "10.1038/s44183-022-00006-2"
    assert normalize_doi("DOI:10.1/x") == "10.1/x"
    assert normalize_doi("10.3389/fmars.2023.1173682/full") == "10.3389/fmars.2023.1173682"
    assert normalize_doi("10.1007/978-3-319-71064-8_131-1.pdf") == "10.1007/978-3-319-71064-8_131-1"


def test_short_id():
    assert short_id("https://openalex.org/A5030178171") == "A5030178171"


def test_person_slug_includes_openalex_id():
    assert person_slug("Jane Doe", "A123") == "jane-doe-a123"


def test_missing_scholar_cache_leaves_graph(tmp_path):
    graph = {"people": [{"id": "glen-wright", "self": True}], "edges": [], "works": []}
    assert _merge_scholar_cache(graph, str(tmp_path), max_people=10) is graph


def test_citers_list_threshold():
    graph = {
        "people": [
            {"name": "Glen Wright", "self": True, "citedMe": 10},
            {"name": "A", "citedMe": 3},
            {"name": "B", "citedMe": 1},
            {"name": "C", "citedMe": 2},
        ]
    }
    rows = citers_list(graph, min_count=2)
    assert [r["name"] for r in rows] == ["A", "C"]


def test_citers_list_includes_orcid_or_profile_url():
    graph = {
        "people": [
            {"name": "Glen Wright", "self": True, "citedMe": 10, "orcid": "0000-0002-9162-9618"},
            {"name": "Ada", "citedMe": 3, "orcid": "0000-0001-2345-6789"},
            {"name": "Bea", "citedMe": 2, "openalex": "A123"},
            {"name": "Cid", "citedMe": 2, "scholar": "abcXYZ"},
            {"name": "Dee", "citedMe": 2},
        ]
    }
    rows = {row["name"]: row for row in citers_list(graph, min_count=2)}
    assert rows["Ada"]["orcid"] == "0000-0001-2345-6789"
    # OpenAlex / Scholar are not websites — no globe icon URL.
    assert "url" not in rows["Bea"]
    assert "url" not in rows["Cid"]
    assert "orcid" not in rows["Dee"] and "url" not in rows["Dee"]
