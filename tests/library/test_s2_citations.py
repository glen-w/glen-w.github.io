"""Semantic Scholar merge, without network calls."""

from processing.library.s2_citations import merge_s2, paper_from_s2


def _graph():
    return {
        "v": 1,
        "source": "openalex+scholar",
        "people": [
            {
                "id": "glen-wright",
                "name": "Glen Wright",
                "self": True,
                "orcid": "0000-0002-9162-9618",
                "citedMe": 1,
                "citedByMe": 1,
            },
            {
                "id": "ada-lovelace-a1",
                "name": "Ada Lovelace",
                "self": False,
                "openalex": "A1",
                "orcid": "0000-0001-2345-6789",
                "citedMe": 1,
                "citedByMe": 0,
            },
        ],
        "edges": [
            {
                "source": "ada-lovelace-a1",
                "target": "glen-wright",
                "count": 1,
                "works": ["W-CITE"],
                "direction": "cites_me",
            },
            {
                "source": "glen-wright",
                "target": "ada-lovelace-a1",
                "count": 1,
                "works": ["W-SEED"],
                "direction": "i_cite",
            },
        ],
        "works": [
            {"id": "W-SEED", "title": "Glen's paper about the high seas treaty", "year": 2020, "doi": "10.1000/seed"},
            {"id": "W-CITE", "title": "An existing citing paper with a long title", "year": 2021, "doi": "10.1000/cite"},
        ],
    }


def test_paper_from_s2_wrapper():
    paper = paper_from_s2(
        {
            "citingPaper": {
                "paperId": "abc",
                "title": "Citing",
                "year": 2022,
                "externalIds": {"DOI": "https://doi.org/10.1000/abc"},
                "authors": [
                    {
                        "authorId": "99",
                        "name": "Ada Lovelace",
                        "externalIds": {"ORCID": "0000-0001-2345-6789"},
                    }
                ],
            }
        }
    )
    assert paper["id"] == "s2-abc"
    assert paper["doi"] == "10.1000/abc"
    assert paper["authors"][0]["orcid"] == "0000-0001-2345-6789"


def test_merge_adds_edges_and_matches_orcid_and_doi():
    merged = merge_s2(
        _graph(),
        {
            "fetched": "2026-09-23T00:00:00Z",
            "citing": [
                {
                    "id": "s2-known",
                    "title": "An existing citing paper with a long title",
                    "year": 2021,
                    "doi": "10.1000/cite",
                    "authors": [
                        {"name": "A. Lovelace", "author_id": "S2ADA", "orcid": "0000-0001-2345-6789"},
                        {"name": "Bea New", "author_id": "BEA", "orcid": ""},
                    ],
                },
                {
                    "id": "s2-fresh",
                    "title": "A brand new citing article about marine biodiversity",
                    "year": 2024,
                    "doi": "10.1000/fresh",
                    "authors": [{"name": "Bea New", "author_id": "BEA", "orcid": ""}],
                },
            ],
            "references": [
                {
                    "seed_work_id": "W-SEED",
                    "paper": {
                        "id": "s2-ref",
                        "title": "A referenced paper about ocean governance law",
                        "year": 2015,
                        "doi": "10.1000/ref",
                        "authors": [{"name": "Cara Cited", "author_id": "CARA", "orcid": ""}],
                    },
                }
            ],
        },
        max_people=10,
    )
    people = {person["id"]: person for person in merged["people"]}
    ada = people["ada-lovelace-a1"]
    assert ada["s2"] == "S2ADA"
    assert ada["citedMe"] == 1
    bea = next(person for person in merged["people"] if person["name"] == "Bea New")
    assert bea["citedMe"] == 2
    cara = next(person for person in merged["people"] if person["name"] == "Cara Cited")
    cite_edge = next(
        edge
        for edge in merged["edges"]
        if edge["direction"] == "i_cite" and edge["target"] == cara["id"]
    )
    assert cite_edge["source"] == "glen-wright"
    assert cite_edge["works"] == ["W-SEED"]
    works = {work["id"] for work in merged["works"]}
    assert "s2-known" not in works
    assert "W-CITE" in works
    assert "s2-fresh" in works
    assert merged["source"] == "openalex+scholar+s2"
    co = [
        edge
        for edge in merged["edges"]
        if edge["direction"] == "co_cite" and bea["id"] in {edge["source"], edge["target"]} and ada["id"] in {edge["source"], edge["target"]}
    ]
    assert len(co) == 1
    assert co[0]["works"] == ["W-CITE"]
