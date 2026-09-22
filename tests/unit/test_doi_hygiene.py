#!/usr/bin/env python3
"""Tests for DOI fill / PII→doi.org hygiene in core BibTeXProcessor."""

from processing.config import Configuration
from processing.core.bibtex_processor import BibTeXProcessor


def test_doi_fill_from_config():
    proc = BibTeXProcessor()
    fields = {}
    assert proc.apply_doi_hygiene('gjerdeGettingYesFasttracking2022', fields) is True
    assert fields['doi'] == Configuration.DOI_FILLS['gjerdeGettingYesFasttracking2022']
    assert proc.apply_doi_hygiene('gjerdeGettingYesFasttracking2022', fields) is False


def test_prefer_doi_over_sciencedirect():
    proc = BibTeXProcessor()
    doi = '10.1016/j.marpol.2020.104059'
    fields = {
        'doi': doi,
        'website': 'https://www.sciencedirect.com/science/article/pii/S0308597X20303365',
    }
    assert proc.apply_doi_hygiene('harden-daviesRightsNaturePerspectives2020', fields) is True
    assert fields['website'] == f'https://doi.org/{doi}'


def test_inject_adds_missing_doi_field():
    proc = BibTeXProcessor()
    content = """@article{gjerdeGettingYesFasttracking2022,
	title = {Getting Beyond Yes},
	year = {2022}
}
"""
    fields = {}
    updated = proc.inject_doi_hygiene_into_content(
        content, 'gjerdeGettingYesFasttracking2022', fields
    )
    assert 'doi = {10.1038/s44183-022-00006-2}' in updated
    assert fields['doi'] == '10.1038/s44183-022-00006-2'
