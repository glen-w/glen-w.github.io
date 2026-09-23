"""Scholar citation merge, without network calls."""

from processing.library.scholar_citations import (
    extract_authors,
    is_glen,
    merge_scholar,
    name_key,
    next_cited_by_page,
    parse_organic,
    plan_first_pages,
    plan_second_pages,
    rank_next_pages,
    redact,
    wants_another_author_page,
)


def _graph():
    return {
        "v": 1,
        "source": "openalex",
        "people": [
            {
                "id": "glen-wright",
                "name": "Glen Wright",
                "self": True,
                "citedMe": 2,
                "citedByMe": 0,
            },
            {
                "id": "kristina-maria-gjerde-a1",
                "name": "Kristina Maria Gjerde",
                "self": False,
                "citedMe": 5,
                "citedByMe": 0,
                "openalex": "A1",
            },
            {
                "id": "bob-smith-a2",
                "name": "Bob Smith",
                "self": False,
                "citedMe": 1,
                "citedByMe": 0,
                "openalex": "A2",
            },
            {
                "id": "ann-smith-a3",
                "name": "Ann Smith",
                "self": False,
                "citedMe": 1,
                "citedByMe": 0,
                "openalex": "A3",
            },
            {
                "id": "alice-smith-a4",
                "name": "Alice Smith",
                "self": False,
                "citedMe": 1,
                "citedByMe": 0,
                "openalex": "A4",
            },
        ],
        "edges": [
            {
                "source": "kristina-maria-gjerde-a1",
                "target": "glen-wright",
                "count": 1,
                "works": ["W1"],
                "direction": "cites_me",
            },
            {
                "source": "bob-smith-a2",
                "target": "glen-wright",
                "count": 1,
                "works": ["W2"],
                "direction": "cites_me",
            },
            {
                "source": "ann-smith-a3",
                "target": "glen-wright",
                "count": 1,
                "works": ["W3"],
                "direction": "cites_me",
            },
            {
                "source": "alice-smith-a4",
                "target": "glen-wright",
                "count": 1,
                "works": ["W4"],
                "direction": "cites_me",
            },
        ],
        "works": [
            {"id": "W1", "title": "Existing paper about high seas governance", "year": 2018},
            {
                "id": "W2",
                "title": "Another title that is long enough to match",
                "year": 2019,
                "doi": "10.1000/existing",
            },
            {"id": "W3", "title": "Ann wrote this paper about the ocean", "year": 2017},
            {"id": "W4", "title": "Alice wrote this paper about the ocean", "year": 2016},
        ],
    }


def _citing():
    return {
        "author_id": "QHaIr0sAAAAJ",
        "fetched": "2026-09-23T00:00:00Z",
        "searches": 3,
        "citing": [
            {
                "id": "gs-EXISTING",
                "title": "Existing paper about high seas governance",
                "year": 2018,
                "doi": "",
                "link": "https://example.test/existing",
                "authors": [
                    {"name": "K. M. Gjerde", "author_id": ""},
                    {"name": "Jane Coauthor", "author_id": "JANE1"},
                ],
            },
            {
                "id": "gs-NEW",
                "title": "A brand new citing article about BBNJ",
                "year": 2024,
                "doi": "10.1000/existing",
                "link": "https://doi.org/10.1000/existing",
                "authors": [
                    {"name": "Glen Wright", "author_id": "QHaIr0sAAAAJ"},
                    {"name": "Bob Smith", "author_id": "BOB1"},
                    {"name": "Jane Coauthor", "author_id": "JANE1"},
                ],
            },
            {
                "id": "gs-AMBIG",
                "title": "Ambiguous surname should not merge onto Ann or Alice",
                "year": 2023,
                "authors": [{"name": "A. Smith", "author_id": "ASMITH"}],
            },
        ],
    }


def test_orcid_match_beats_a_different_name():
    graph = _graph()
    graph["people"][1]["orcid"] = "0000-0001-2345-6789"
    citing = {
        "citing": [
            {
                "id": "gs-ORCID",
                "title": "A paper that only matches through ORCID",
                "year": 2024,
                "authors": [
                    {
                        "name": "Maria Gomez",
                        "author_id": "MG",
                        "orcid": "https://orcid.org/0000-0001-2345-6789",
                    }
                ],
            }
        ]
    }
    merged = merge_scholar(graph, citing, max_people=10)
    gjerde = next(person for person in merged["people"] if person["id"] == "kristina-maria-gjerde-a1")
    assert gjerde["scholar"] == "MG"
    assert gjerde["orcid"] == "0000-0001-2345-6789"
    assert not any(person["name"] == "Maria Gomez" for person in merged["people"])


def test_name_key_and_glen():
    assert name_key("Kristina Maria Gjerde") == ("gjerde", "k")
    assert name_key("Gjerde, K. M.") == ("gjerde", "k")
    assert name_key("Prince") is None
    assert is_glen("Glen Wright")
    assert is_glen("Wright, Glen")
    assert is_glen("G. Wright")
    assert not is_glen("George Wright")


def test_title_dedup_name_merge_and_cocite():
    merged = merge_scholar(_graph(), _citing(), max_people=10)
    people = {person["id"]: person for person in merged["people"]}
    gjerde = people["kristina-maria-gjerde-a1"]
    assert gjerde["citedMe"] == 5
    jane = next(person for person in merged["people"] if person["name"] == "Jane Coauthor")
    assert jane["scholar"] == "JANE1"
    assert jane["citedMe"] == 2
    bob = people["bob-smith-a2"]
    assert bob["citedMe"] == 1
    assert bob["scholar"] == "BOB1"

    glen = people["glen-wright"]
    assert glen["citedMe"] == 5

    works = {work["id"]: work for work in merged["works"]}
    assert "gs-EXISTING" not in works
    assert "gs-NEW" not in works
    assert works["W2"]["doi"] == "10.1000/existing"

    ambig = next(person for person in merged["people"] if person.get("scholar") == "ASMITH")
    assert ambig["id"] not in {"ann-smith-a3", "alice-smith-a4"}

    co = [
        edge
        for edge in merged["edges"]
        if edge["direction"] == "co_cite"
        and {edge["source"], edge["target"]} == {gjerde["id"], jane["id"]}
    ]
    assert len(co) == 1
    assert co[0]["works"] == ["W1"]
    pair = [
        edge
        for edge in merged["edges"]
        if edge["direction"] == "co_cite" and bob["id"] in {edge["source"], edge["target"]} and jane["id"] in {edge["source"], edge["target"]}
    ]
    assert len(pair) == 1
    assert pair[0]["works"] == ["W2"]
    assert merged["source"] == "openalex+scholar"


def test_cocite_only_among_kept_people():
    graph = _graph()
    citing = {
        "citing": [
            {
                "id": "gs-CLIQUE",
                "title": "Shared citing paper with three authors",
                "year": 2022,
                "authors": [
                    {"name": "Kristina Maria Gjerde", "author_id": "KG"},
                    {"name": "Bob Smith", "author_id": "BOB"},
                    {"name": "Carol New", "author_id": "CAROL"},
                ],
            }
        ]
    }
    merged = merge_scholar(graph, citing, max_people=2)
    ids = {person["id"] for person in merged["people"]}
    assert "kristina-maria-gjerde-a1" in ids
    assert "bob-smith-a2" in ids
    assert not any(person["name"] == "Carol New" for person in merged["people"])
    co_pairs = {
        frozenset((edge["source"], edge["target"]))
        for edge in merged["edges"]
        if edge["direction"] == "co_cite"
    }
    assert co_pairs == {frozenset(("kristina-maria-gjerde-a1", "bob-smith-a2"))}


def test_non_latin_author_lists_stay_separate():
    citing = {
        "citing": [
            {
                "id": "gs-C1",
                "title": "A sufficiently long chinese citing paper",
                "year": 2024,
                "authors": [{"name": "卢晓强， 刘威", "author_id": ""}],
            },
            {
                "id": "gs-C2",
                "title": "A sufficiently long greek citing paper",
                "year": 2023,
                "authors": [{"name": "Μ Παπαθανασίου", "author_id": ""}],
            },
        ]
    }
    merged = merge_scholar(_graph(), citing, max_people=20)
    names = [person["name"] for person in merged["people"]]
    assert "卢晓强" in names
    assert "刘威" in names
    assert any("Παπαθανασίου" in name for name in names)
    assert not any("卢晓强" in name and "刘威" in name for name in names)


def test_merge_is_idempotent():
    once = merge_scholar(_graph(), _citing(), max_people=10)
    twice = merge_scholar(once, _citing(), max_people=10)
    assert [(p["id"], p["citedMe"]) for p in once["people"]] == [
        (p["id"], p["citedMe"]) for p in twice["people"]
    ]
    assert once["edges"] == twice["edges"]


def test_deeper_pages_prefer_highly_cited_work():
    papers = [
        {"cites_id": "big", "cited_by": 100, "title": "Big"},
        {"cites_id": "mid", "cited_by": 45, "title": "Mid"},
        {"cites_id": "once", "cited_by": 1, "title": "Once"},
    ]
    counts = {"big": {0: 20}, "mid": {0: 20, 20: 20}}
    jobs = rank_next_pages(papers, counts)
    assert [(cites_id, start) for start, _cited, _title, cites_id in jobs] == [
        ("big", 20),
        ("mid", 40),
        ("once", 0),
    ]
    assert next_cited_by_page({"cited_by": 100}, {0: 7}) is None
    assert next_cited_by_page({"cited_by": 50}, {0: 20, 20: 20}) == 40
    assert next_cited_by_page({"cited_by": 30}, {0: 20, 20: 20}) is None


def test_search_plan_respects_budget():
    papers = [
        {"cites_id": "high", "cited_by": 100, "title": "High"},
        {"cites_id": "mid", "cited_by": 30, "title": "Mid"},
        {"cites_id": "low", "cited_by": 5, "title": "Low"},
        {"cites_id": "", "cited_by": 50, "title": "No id"},
        {"cites_id": "zero", "cited_by": 0, "title": "Zero"},
    ]
    first = plan_first_pages(papers, budget=2)
    assert [paper["cites_id"] for paper in first] == ["high", "mid"]
    second = plan_second_pages(
        [
            {"cites_id": "high", "cited_by": 100, "page1_count": 20, "title": "High"},
            {"cites_id": "mid", "cited_by": 30, "page1_count": 12, "title": "Mid"},
            {"cites_id": "low", "cited_by": 40, "page1_count": 20, "title": "Low"},
        ],
        budget=1,
    )
    assert second == ["high"]
    assert wants_another_author_page(100)
    assert not wants_another_author_page(37)


def test_parse_organic_authors_and_redact():
    row = parse_organic(
        {
            "title": "Citing article",
            "result_id": "ABC",
            "link": "https://doi.org/10.1000/abc",
            "publication_info": {
                "summary": "Jane Doe, Glen Wright - 2021 - Ocean journal",
                "authors": [
                    {"name": "Jane Doe", "author_id": "JD"},
                    {"name": "…", "author_id": ""},
                ],
            },
        }
    )
    assert row["id"] == "gs-ABC"
    assert row["doi"] == "10.1000/abc"
    assert row["year"] == 2021
    assert row["authors"] == [{"name": "Jane Doe", "author_id": "JD"}]

    summary_only = {
        "title": "From summary",
        "result_id": "SUM",
        "publication_info": {"summary": "Ada Lovelace, et al. - 2019 - Journal"},
    }
    authors = extract_authors(summary_only)
    assert authors == [{"name": "Ada Lovelace", "author_id": ""}]
    assert redact({"api_key": "secret", "url": "https://serpapi.com/search?api_key=secret&q=1"}) == {
        "api_key": "REDACTED",
        "url": "https://serpapi.com/search?api_key=REDACTED&q=1",
    }
