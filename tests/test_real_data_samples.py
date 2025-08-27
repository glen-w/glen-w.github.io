#!/usr/bin/env python3
"""
Tests using real data samples from papers.bib to ensure the script works correctly
with actual BibTeX entries, including the new dimensions tag functionality.
"""

import pytest
import os
import tempfile
import shutil
import sys
from unittest.mock import patch, MagicMock, mock_open

# Add the parent directory to the path so we can import process_papers
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import bibtexparser
    from bibtexparser.bparser import BibTexParser
    BIBTEXPARSER_AVAILABLE = True
except ImportError:
    BIBTEXPARSER_AVAILABLE = False

from process_papers import (
    parse_bibtex_entry,
    clean_nested_braces,
    extract_file_paths,
    prepare_pdf_metadata,
    add_pdf_and_preview_tags,
    entry_has_pdf_and_preview_tags,
    clean_title_for_filename,
    extract_author_names_for_filename,
    extract_journal_or_publisher_for_filename,
    process_papers_bib
)


class TestRealDataSamples:
    """Test with real BibTeX entries from papers.bib."""
    
    # Real data samples from papers.bib (simplified for testing)
    SAMPLE_ENTRY_WITHOUT_DOI = """@article{Wright2011a,
    title = {Marine energy},
    copyright = {CC0 1.0 Universal Public Domain Dedication},
    number = {August},
    journal = {New Zealand Law Journal},
    author = {Wright, Glen and Leary, David},
    year = {2011},
    keywords = {wave energy, New Zealand, ocean energy, tidal energy},
    pages = {227--230},
    file = {PDF:/Users/89298/Documents/papers/storage/BGREJ9II/2011-Marine_energy.pdf:application/pdf}
}"""
    
    SAMPLE_ENTRY_WITH_DOI = """@article{Wright2011b,
    title = {Conceptualising and combating transnational environmental crime},
    volume = {14},
    copyright = {CC0 1.0 Universal Public Domain Dedication},
    url = {https://link.springer.com/article/10.1007/s12117-011-9130-4},
    doi = {10.1007/s12117-011-9130-4},
    abstract = {To date, transnational environmental crime has been poorly attended to by the transnational organised crime and transnational policing discourse. Academics have focused on individual elements of environmental crime, neglecting a broader theoretical discussion, while national and international institutions have prioritised other forms of organised crime, giving little thought to the nuanced nature of transnational environmental crime and how this should be reflected in policing and countermeasures. This paper attempts to rectify this by conceptualising transnational environmental crime and suggesting ways forward for countermeasure development. The paper will begin by looking at the problem of environmental crime, its value, scope and effects, concluding that the damaging nature of transnational environmental crime demands a greater focus on its policing. The nature of transnational environmental crime will then be discussed by reference to traditional forms of organised crime. It will be argued that, while transnational environmental crime is a form of organised crime, and has some features in common with the traditional organised crimes, such as drug smuggling and people trafficking, it is the substantial differences that should guide the approach to developing countermeasures. The development of effective countermeasures, it is concluded, requires a significant change in policy at every level.},
    number = {4},
    journal = {Trends in Organized Crime},
    author = {Wright, Glen},
    year = {2011},
    keywords = {environmental crime, organised crime, trade in endangered species, transnational policing, wildlife crime},
    pages = {332--346},
    file = {Wright - 2011 - Conceptualising and combating transnational enviro.pdf:/Users/89298/Documents/papers/storage/XFBTJGVF/Wright - 2011 - Conceptualising and combating transnational enviro.pdf:application/pdf}
}"""
    
    SAMPLE_ENTRY_WITH_COMPLEX_DOI = """@article{Wright2014a,
    title = {Strengthening the role of science in marine governance through environmental impact assessment: a case study of the marine renewable energy industry},
    volume = {99},
    copyright = {CC0 1.0 Universal Public Domain Dedication},
    issn = {09645691},
    url = {http://linkinghub.elsevier.com/retrieve/pii/S0964569114002099},
    doi = {10.1016/j.ocecoaman.2014.07.004},
    urldate = {2014-10-02},
    journal = {Ocean and Coastal Management},
    author = {Wright, Glen},
    month = oct,
    year = {2014},
    note = {Publisher: Elsevier Ltd},
    pages = {23--30},
    file = {PDF:/Users/89298/Documents/papers/storage/Q2TLEIFP/2014-Strengthening_the_role_of_science_in_marine_governance_through_environmental_impact_assessment_a_case_study_of_the_.pdf:application/pdf}
}"""

    def test_real_entry_parsing_without_doi(self):
        """Test parsing a real BibTeX entry without DOI."""
        citation_key, fields = parse_bibtex_entry(self.SAMPLE_ENTRY_WITHOUT_DOI)
        
        assert citation_key == "Wright2011a"
        assert fields["title"] == "Marine energy"
        assert fields["author"] == "Wright, Glen and Leary, David"
        assert fields["year"] == "2011"
        assert fields["journal"] == "New Zealand Law Journal"
        assert "doi" not in fields
        
        # Test that this entry does not need dimensions tag
        assert not entry_has_pdf_and_preview_tags(fields)  # No pdf/preview tags yet
    
    def test_real_entry_parsing_with_doi(self):
        """Test parsing a real BibTeX entry with DOI."""
        citation_key, fields = parse_bibtex_entry(self.SAMPLE_ENTRY_WITH_DOI)
        
        assert citation_key == "Wright2011b"
        assert fields["title"] == "Conceptualising and combating transnational environmental crime"
        assert fields["author"] == "Wright, Glen"
        assert fields["year"] == "2011"
        assert fields["journal"] == "Trends in Organized Crime"
        assert fields["doi"] == "10.1007/s12117-011-9130-4"
        
        # Test that this entry needs dimensions tag due to DOI
        fields_with_basic_tags = {**fields, "pdf": "test.pdf", "preview": "test.jpeg"}
        assert not entry_has_pdf_and_preview_tags(fields_with_basic_tags)  # Missing dimensions
        
        fields_with_all_tags = {**fields_with_basic_tags, "dimensions": "true"}
        assert entry_has_pdf_and_preview_tags(fields_with_all_tags)  # All tags present
    
    def test_real_entry_filename_generation_without_doi(self):
        """Test filename generation with real entry without DOI."""
        citation_key, fields = parse_bibtex_entry(self.SAMPLE_ENTRY_WITHOUT_DOI)
        
        # Test title cleaning
        clean_title = clean_title_for_filename(fields["title"])
        assert clean_title == "Marine_energy"
        
        # Test author name extraction
        author_names = extract_author_names_for_filename(fields["author"])
        assert author_names == "Glen_Wright_David_Leary"
        
        # Test journal extraction
        journal = extract_journal_or_publisher_for_filename(fields)
        assert journal == "New_Zealand_Law_Journal"
    
    def test_real_entry_filename_generation_with_doi(self):
        """Test filename generation with real entry with DOI."""
        citation_key, fields = parse_bibtex_entry(self.SAMPLE_ENTRY_WITH_DOI)
        
        # Test title cleaning (long title with special words)
        clean_title = clean_title_for_filename(fields["title"])
        # The actual function behavior keeps "and" as it's not in the common words list for this length
        expected_title = "Conceptualising_and_combating_transnational_environmental_crime"
        assert clean_title == expected_title
        
        # Test author name extraction
        author_names = extract_author_names_for_filename(fields["author"])
        assert author_names == "Glen_Wright"
        
        # Test journal extraction
        journal = extract_journal_or_publisher_for_filename(fields)
        assert journal == "Trends_in_Organized_Crime"
    
    def test_real_entry_complex_title_processing(self):
        """Test processing of complex title with special characters."""
        citation_key, fields = parse_bibtex_entry(self.SAMPLE_ENTRY_WITH_COMPLEX_DOI)
        
        # Test title cleaning (very long title with special characters)
        clean_title = clean_title_for_filename(fields["title"])
        # The actual function doesn't truncate at 100 chars, it removes common words
        assert len(clean_title) > 100  # Actually quite long
        assert "Strengthening" in clean_title
        assert "science" in clean_title
        assert "marine" in clean_title
        assert "&" not in clean_title  # Special characters should be removed
        
        # Check specific expected content
        expected_words = ["Strengthening", "role", "science", "marine", "governance", "environmental", "impact", "assessment", "case", "study", "renewable", "energy", "industry"]
        for word in expected_words:
            assert word in clean_title
    
    def test_real_entry_file_path_extraction(self):
        """Test file path extraction from real entries."""
        citation_key, fields = parse_bibtex_entry(self.SAMPLE_ENTRY_WITHOUT_DOI)
        
        file_paths = extract_file_paths(fields.get("file", ""))
        assert len(file_paths) == 1
        assert file_paths[0] == "/Users/89298/Documents/papers/storage/BGREJ9II/2011-Marine_energy.pdf"
        
        # Test complex file path
        citation_key, fields = parse_bibtex_entry(self.SAMPLE_ENTRY_WITH_DOI)
        file_paths = extract_file_paths(fields.get("file", ""))
        assert len(file_paths) == 1
        expected_path = "/Users/89298/Documents/papers/storage/XFBTJGVF/Wright - 2011 - Conceptualising and combating transnational enviro.pdf"
        assert file_paths[0] == expected_path
    
    def test_real_entry_metadata_preparation(self):
        """Test PDF metadata preparation with real entries."""
        citation_key, fields = parse_bibtex_entry(self.SAMPLE_ENTRY_WITH_DOI)
        
        metadata = prepare_pdf_metadata(fields)
        
        assert metadata["title"] == "Conceptualising and combating transnational environmental crime"
        assert metadata["author"] == "Wright, Glen"  # Only first author
        assert metadata["producer"] == "glen-w's Al-folio Helper"
        
        # The prepare_pdf_metadata function doesn't add 'subject' field by default
        # It only adds title, author, creator, and producer
        assert "title" in metadata
        assert "author" in metadata
        assert "producer" in metadata
        
        # Test with abstract
        assert "abstract" in fields
        assert len(fields["abstract"]) > 100  # Should have substantial abstract
    
    @pytest.mark.skipif(not BIBTEXPARSER_AVAILABLE, reason="bibtexparser not available")
    def test_real_entry_tag_addition_without_doi(self):
        """Test adding tags to real entry without DOI."""
        bibtex_content = self.SAMPLE_ENTRY_WITHOUT_DOI
        citation_key, fields = parse_bibtex_entry(bibtex_content)
        
        # Add tags
        modified_content = add_pdf_and_preview_tags(
            bibtex_content, citation_key, "test.jpeg", "test.pdf", fields
        )
        
        # Validate with bibtexparser
        parser = BibTexParser(common_strings=True)
        parser.ignore_nonstandard_types = False
        parser.homogenize_fields = False
        
        parsed = parser.parse(modified_content)
        assert len(parsed.entries) == 1
        
        entry = parsed.entries[0]
        assert entry["ID"] == citation_key
        assert entry.get("preview") == "test.jpeg"
        assert entry.get("pdf") == "test.pdf"
        assert entry.get("dimensions") is None  # No DOI, so no dimensions tag
        
        # Original fields should be preserved
        assert entry.get("title") == "Marine energy"
        assert entry.get("journal") == "New Zealand Law Journal"
    
    @pytest.mark.skipif(not BIBTEXPARSER_AVAILABLE, reason="bibtexparser not available")
    def test_real_entry_tag_addition_with_doi(self):
        """Test adding tags to real entry with DOI."""
        bibtex_content = self.SAMPLE_ENTRY_WITH_DOI
        citation_key, fields = parse_bibtex_entry(bibtex_content)
        
        # Add tags
        modified_content = add_pdf_and_preview_tags(
            bibtex_content, citation_key, "test.jpeg", "test.pdf", fields
        )
        
        # Validate with bibtexparser
        parser = BibTexParser(common_strings=True)
        parser.ignore_nonstandard_types = False
        parser.homogenize_fields = False
        
        parsed = parser.parse(modified_content)
        assert len(parsed.entries) == 1
        
        entry = parsed.entries[0]
        assert entry["ID"] == citation_key
        assert entry.get("preview") == "test.jpeg"
        assert entry.get("pdf") == "test.pdf"
        assert entry.get("dimensions") == "true"  # DOI present, so dimensions tag added
        
        # Original fields should be preserved
        assert entry.get("title") == "Conceptualising and combating transnational environmental crime"
        assert entry.get("doi") == "10.1007/s12117-011-9130-4"
        assert entry.get("journal") == "Trends in Organized Crime"
    
    @pytest.mark.skipif(not BIBTEXPARSER_AVAILABLE, reason="bibtexparser not available")
    def test_real_entry_complex_processing(self):
        """Test processing complex real entry with special characters."""
        bibtex_content = self.SAMPLE_ENTRY_WITH_COMPLEX_DOI
        citation_key, fields = parse_bibtex_entry(bibtex_content)
        
        # Add tags
        modified_content = add_pdf_and_preview_tags(
            bibtex_content, citation_key, "complex.jpeg", "complex.pdf", fields
        )
        
        # Validate with bibtexparser
        parser = BibTexParser(common_strings=True)
        parser.ignore_nonstandard_types = False
        parser.homogenize_fields = False
        
        parsed = parser.parse(modified_content)
        assert len(parsed.entries) == 1
        
        entry = parsed.entries[0]
        assert entry["ID"] == citation_key
        assert entry.get("preview") == "complex.jpeg"
        assert entry.get("pdf") == "complex.pdf"
        assert entry.get("dimensions") == "true"  # DOI present
        
        # Check complex fields are preserved
        assert "Strengthening the role of science" in entry.get("title", "")
        assert entry.get("doi") == "10.1016/j.ocecoaman.2014.07.004"
        assert "Ocean" in entry.get("journal", "")
    
    def test_real_entries_mixed_processing(self):
        """Test processing multiple real entries with mixed DOI presence."""
        entries_data = [
            (self.SAMPLE_ENTRY_WITHOUT_DOI, "Wright2011a", False),  # No DOI
            (self.SAMPLE_ENTRY_WITH_DOI, "Wright2011b", True),      # Has DOI
            (self.SAMPLE_ENTRY_WITH_COMPLEX_DOI, "Wright2014a", True), # Has DOI
        ]
        
        for bibtex_content, expected_key, has_doi in entries_data:
            citation_key, fields = parse_bibtex_entry(bibtex_content)
            
            assert citation_key == expected_key
            
            if has_doi:
                assert "doi" in fields
                assert fields["doi"].strip()
                
                # Should require dimensions tag
                fields_with_basic = {**fields, "pdf": "test.pdf", "preview": "test.jpeg"}
                assert not entry_has_pdf_and_preview_tags(fields_with_basic)
                
                fields_with_all = {**fields_with_basic, "dimensions": "true"}
                assert entry_has_pdf_and_preview_tags(fields_with_all)
            else:
                assert "doi" not in fields or not fields.get("doi", "").strip()
                
                # Should not require dimensions tag
                fields_with_basic = {**fields, "pdf": "test.pdf", "preview": "test.jpeg"}
                assert entry_has_pdf_and_preview_tags(fields_with_basic)
    
    def test_real_data_integration_workflow(self):
        """Test the complete workflow with real data."""
        # Create a temporary file with real data
        test_content = f"""
{self.SAMPLE_ENTRY_WITHOUT_DOI}

{self.SAMPLE_ENTRY_WITH_DOI}
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bib', delete=False) as f:
            f.write(test_content)
            temp_file = f.name
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Mock all external operations
                with patch('process_papers.check_dependencies', return_value=True), \
                     patch('process_papers.copy_pdf_file', return_value=True), \
                     patch('process_papers.generate_pdf_thumbnail', return_value=True), \
                     patch('process_papers.update_pdf_metadata', return_value=True), \
                     patch('os.path.exists', return_value=True), \
                     patch('os.path.getsize', return_value=10000), \
                     patch('os.makedirs'):
                    
                    # Run the processing
                    process_papers_bib(
                        temp_file, 
                        output_dir=os.path.join(temp_dir, "assets", "pdf"),
                        test_mode=True, 
                        test_count=2
                    )
                    
                    # Read the modified file
                    with open(temp_file, 'r') as f:
                        modified_content = f.read()
                    
                    # Check that entries were processed
                    assert "preview = {" in modified_content
                    assert "pdf = {" in modified_content
                    
                    # Check dimensions tag only for entry with DOI
                    lines = modified_content.split('\n')
                    wright2011a_section = []
                    wright2011b_section = []
                    current_section = None
                    
                    for line in lines:
                        if "Wright2011a" in line:
                            current_section = wright2011a_section
                        elif "Wright2011b" in line:
                            current_section = wright2011b_section
                        elif line.strip().startswith('@') and current_section is not None:
                            current_section = None
                        
                        if current_section is not None:
                            current_section.append(line)
                    
                    # Wright2011a (no DOI) should not have dimensions tag
                    wright2011a_text = '\n'.join(wright2011a_section)
                    assert "dimensions = {true}" not in wright2011a_text
                    
                    # Wright2011b (has DOI) should have dimensions tag
                    wright2011b_text = '\n'.join(wright2011b_section)
                    assert "dimensions = {true}" in wright2011b_text
        
        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.unlink(temp_file)


if __name__ == "__main__":
    pytest.main([__file__])
