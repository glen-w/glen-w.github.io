"""Tests for ORCID / public-profile resolution from on-disk sources."""

from pathlib import Path

import json
import yaml

from processing.library.coauthors import collaborators_list, write_coauthor_artifacts
from processing.library.person_profile import lookup_profile, profile_url


def test_profile_url_prefers_orcid():
    assert profile_url(orcid="0000-0001-2345-6789", openalex="A1") == (
        "https://orcid.org/0000-0001-2345-6789"
    )
    assert profile_url(openalex="A99") == "https://openalex.org/A99"
    assert profile_url(scholar="abc") == "https://scholar.google.com/citations?user=abc"


def test_normalize_scholar_and_link_ping(monkeypatch):
    from processing.library.twenty_people import (
        check_profile_links,
        normalize_scholar_id,
        profile_link_targets,
    )

    assert normalize_scholar_id("https://scholar.google.com/citations?user=AbC_12-x&hl=en") == "AbC_12-x"
    assert normalize_scholar_id("AbC_12-x") == "AbC_12-x"
    assert normalize_scholar_id("") == ""

    row = {
        "name": "Jane",
        "orcid": "0000-0001-2345-6789",
        "url": "https://example.edu/jane",
        "scholar": "AbC_12-x",
    }
    kinds = {k for k, _ in profile_link_targets(row)}
    assert kinds == {"orcid", "url", "scholar"}

    def fake_ping(url, timeout=8.0):
        if "example.edu" in url:
            return False, "HTTP 404"
        return True, "200"

    monkeypatch.setattr(
        "processing.library.twenty_people._ping_url",
        fake_ping,
    )
    broken = check_profile_links([row], workers=2)
    assert len(broken) == 1
    assert broken[0]["kind"] == "url"


def test_lookup_prefers_twenty_scholar(tmp_path: Path):
    data = tmp_path / "_data"
    assets = tmp_path / "assets" / "json"
    data.mkdir(parents=True)
    assets.mkdir(parents=True)
    (data / "people_profiles.yml").write_text(
        yaml.dump(
            {
                "people": [
                    {"name": "Jane Doe", "scholar": "TwentySchol"},
                ]
            }
        ),
        encoding="utf-8",
    )
    (assets / "citations.json").write_text(
        json.dumps({"people": [{"name": "Jane Doe", "scholar": "CiteSchol"}]}),
        encoding="utf-8",
    )
    from processing.library.person_profile import load_citation_profiles
    from processing.library.twenty_people import load_people_profiles

    profile = lookup_profile(
        "Jane Doe",
        twenty_profiles=load_people_profiles(str(tmp_path)),
        citation_profiles=load_citation_profiles(str(tmp_path)),
    )
    assert profile["scholar"] == "TwentySchol"


def test_lookup_uses_citation_orcid_and_coauthor_homepage(tmp_path: Path):
    data = tmp_path / "_data"
    assets = tmp_path / "assets" / "json"
    data.mkdir(parents=True)
    assets.mkdir(parents=True)

    (data / "coauthors.yml").write_text(
        yaml.dump(
            {
                "doe": [
                    {"firstname": ["Jane", "J."], "url": "https://example.edu/jane"},
                ]
            }
        ),
        encoding="utf-8",
    )
    (data / "people_profiles.yml").write_text(
        yaml.dump(
            {
                "source": "twenty",
                "people": [
                    {
                        "name": "Jane Doe",
                        "orcid": "0000-0001-1111-1111",
                        "url": "https://twenty.example/jane",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (assets / "citations.json").write_text(
        json.dumps(
            {
                "people": [
                    {
                        "name": "Jane Doe",
                        "orcid": "0000-0001-9999-9999",
                        "openalex": "A1",
                    },
                    {
                        "name": "Sam Solo",
                        "openalex": "A2",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    from processing.library.person_profile import (
        load_citation_profiles,
        load_coauthor_urls,
    )
    from processing.library.twenty_people import load_people_profiles

    twenty = load_people_profiles(str(tmp_path))
    cited = load_citation_profiles(str(tmp_path))
    urls = load_coauthor_urls(str(tmp_path))

    jane = lookup_profile(
        "Jane Doe",
        twenty_profiles=twenty,
        citation_profiles=cited,
        coauthor_urls=urls,
    )
    # Twenty wins for both ORCID and website.
    assert jane["orcid"] == "0000-0001-1111-1111"
    assert jane["url"] == "https://twenty.example/jane"

    sam = lookup_profile(
        "Sam Solo",
        twenty_profiles=twenty,
        citation_profiles=cited,
        coauthor_urls=urls,
    )
    # OpenAlex is not a website icon target.
    assert "url" not in sam


def test_collaborators_list_enriches_from_disk(tmp_path: Path):
    data = tmp_path / "_data"
    assets = tmp_path / "assets" / "json"
    data.mkdir(parents=True)
    assets.mkdir(parents=True)
    (assets / "citations.json").write_text(
        json.dumps(
            {
                "people": [
                    {"name": "Jane Doe", "orcid": "0000-0001-2222-2222"},
                ]
            }
        ),
        encoding="utf-8",
    )
    graph = {
        "people": [
            {"id": "glen-wright", "name": "Glen Wright", "self": True, "count": 2},
            {"id": "jane-doe", "name": "Jane Doe", "self": False, "count": 2},
            {"id": "sam-solo", "name": "Sam Solo", "self": False, "count": 1},
        ],
        "edges": [],
        "works": [],
    }
    rows = collaborators_list(graph, project_root=str(tmp_path))
    assert len(rows) == 1
    assert rows[0]["name"] == "Jane Doe"
    assert rows[0]["orcid"] == "0000-0001-2222-2222"

    write_coauthor_artifacts(str(tmp_path), graph)
    dumped = yaml.safe_load((data / "collaborators.yml").read_text(encoding="utf-8"))
    assert dumped[0]["orcid"] == "0000-0001-2222-2222"
    people = json.loads((assets / "coauthors.json").read_text(encoding="utf-8"))["people"]
    jane = next(p for p in people if p["name"] == "Jane Doe")
    assert jane["orcid"] == "0000-0001-2222-2222"
