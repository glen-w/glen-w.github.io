"""Work collapse for the citation graph (no network)."""

from processing.library.citations import authorship_people
from processing.library.work_identity import dedupe_graph, normalize_orcid, title_similarity


def _graph():
    return {
        "people": [
            {"id": "glen-wright", "name": "Glen Wright", "self": True, "citedMe": 0, "citedByMe": 0},
            {"id": "ada", "name": "Ada Lovelace", "self": False, "citedMe": 0, "citedByMe": 0},
        ],
        "edges": [
            {
                "source": "ada",
                "target": "glen-wright",
                "count": 2,
                "works": ["W1", "gs-dup"],
                "direction": "cites_me",
            }
        ],
        "works": [
            {"id": "gs-dup", "title": "Equity and justice should underpin the discourse on tipping points", "year": 2024},
            {
                "id": "W1",
                "title": "Equity and justice should underpin the discourse on tipping points",
                "year": 2024,
                "doi": "10.1000/same",
            },
            {
                "id": "W2",
                "title": "A different paper about marine governance and law",
                "year": 2020,
                "doi": "10.1000/other",
                "path": "/library/other/",
            },
            {
                "id": "gs-other",
                "title": "A different paper about marine governance and law",
                "year": 2020,
                "doi": "10.9999/not-the-same",
                "path": "/library/not-same/",
            },
            {
                "id": "W3",
                "title": "Ocean energy governance in the north sea basin",
                "year": 2018,
                "path": "/library/ocean-2018/",
            },
            {
                "id": "gs-year",
                "title": "Ocean energy governance in the north sea basin",
                "year": 2019,
                "path": "/library/ocean-2019/",
            },
        ],
    }


def test_normalize_orcid_from_url():
    assert normalize_orcid("https://orcid.org/0000-0002-9162-9618") == "0000-0002-9162-9618"
    assert normalize_orcid("") == ""


def test_same_title_collapses_onto_openalex_id():
    graph = dedupe_graph(_graph())
    ids = {work["id"] for work in graph["works"]}
    assert "W1" in ids
    assert "gs-dup" not in ids
    edge = graph["edges"][0]
    assert edge["works"] == ["W1"]
    assert edge["count"] == 1
    ada = next(person for person in graph["people"] if person["id"] == "ada")
    assert ada["citedMe"] == 1
    glen = next(person for person in graph["people"] if person["self"])
    assert glen["citedMe"] == 1


def test_different_dois_stay_split():
    graph = dedupe_graph(_graph())
    ids = {work["id"] for work in graph["works"]}
    assert "W2" in ids
    assert "gs-other" in ids


def test_same_title_different_year_stays_split():
    graph = dedupe_graph(_graph())
    ids = {work["id"] for work in graph["works"]}
    assert "W3" in ids
    assert "gs-year" in ids


def test_near_title_merges_and_keeps_doi():
    graph = _graph()
    graph["works"].append(
        {
            "id": "gs-near",
            "title": "Equity and justice should underpin the discourse on tipping point",
            "year": 2024,
        }
    )
    graph["edges"][0]["works"].append("gs-near")
    assert title_similarity(
        "Equity and justice should underpin the discourse on tipping points",
        "Equity and justice should underpin the discourse on tipping point",
    ) >= 0.92
    merged = dedupe_graph(graph)
    ids = {work["id"] for work in merged["works"]}
    assert "gs-near" not in ids
    kept = next(work for work in merged["works"] if work["id"] == "W1")
    assert kept["doi"] == "10.1000/same"


def test_unreferenced_library_path_is_kept():
    graph = _graph()
    graph["works"].append(
        {
            "id": "W-SEED",
            "title": "A library paper that nobody has cited yet at all",
            "year": 2022,
            "doi": "10.1000/seed-only",
            "path": "/library/seed/",
        }
    )
    merged = dedupe_graph(graph)
    assert any(work["id"] == "W-SEED" for work in merged["works"])


def test_authorship_people_keeps_orcid():
    work = {
        "authorships": [
            {
                "author": {
                    "id": "https://openalex.org/A123",
                    "display_name": "Ada Lovelace",
                    "orcid": "https://orcid.org/0000-0001-2345-6789",
                }
            },
            {"author": {"id": "https://openalex.org/A123", "display_name": "Ada Lovelace"}},
        ]
    }
    assert authorship_people(work) == [("A123", "Ada Lovelace", "0000-0001-2345-6789")]
