# TEAM_153: Tests for XML parser
"""Tests for the research paper XML parser."""

from pathlib import Path

import pytest

from xml_to_pdf.parser import Author, Paper, Section, parse_xml

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"
SAMPLE_XML = EXAMPLES_DIR / "content_provenance_paper.xml"


class TestParseXML:
    """Test parsing the sample research paper XML."""

    def test_parse_returns_paper(self):
        paper = parse_xml(str(SAMPLE_XML))
        assert isinstance(paper, Paper)

    def test_title_parsed(self):
        paper = parse_xml(str(SAMPLE_XML))
        assert "Content Provenance" in paper.title
        assert "AI Era" in paper.title

    def test_authors_parsed(self):
        paper = parse_xml(str(SAMPLE_XML))
        assert len(paper.authors) == 2
        assert paper.authors[0].name == "Dr. Elena Vasquez"
        assert paper.authors[0].affiliation == "EncypherAI Research"
        assert paper.authors[1].name == "Prof. James Chen"

    def test_abstract_parsed(self):
        paper = parse_xml(str(SAMPLE_XML))
        assert len(paper.abstract) > 100
        assert "large language models" in paper.abstract

    def test_keywords_parsed(self):
        paper = parse_xml(str(SAMPLE_XML))
        assert "content provenance" in paper.keywords
        assert "C2PA" in paper.keywords
        assert len(paper.keywords) == 6

    def test_sections_parsed(self):
        paper = parse_xml(str(SAMPLE_XML))
        assert len(paper.sections) == 5
        assert paper.sections[0].heading == "1. Introduction"
        assert paper.sections[0].id == "introduction"

    def test_section_paragraphs(self):
        paper = parse_xml(str(SAMPLE_XML))
        intro = paper.sections[0]
        assert len(intro.paragraphs) == 3
        assert "generative AI" in intro.paragraphs[0]

    def test_subsections_parsed(self):
        paper = parse_xml(str(SAMPLE_XML))
        methodology = paper.sections[2]  # Section 3: Methodology
        assert len(methodology.subsections) == 3
        assert methodology.subsections[0].heading == "3.1 C2PA Manifests for Text"
        assert methodology.subsections[2].heading == "3.3 Zero-Width Steganographic Embedding"

    def test_subsection_paragraphs(self):
        paper = parse_xml(str(SAMPLE_XML))
        methodology = paper.sections[2]
        zw_sub = methodology.subsections[2]
        assert len(zw_sub.paragraphs) == 3
        assert "base-4 encoding" in zw_sub.paragraphs[0]

    def test_references_parsed(self):
        paper = parse_xml(str(SAMPLE_XML))
        assert len(paper.references) == 5
        assert paper.references[0].id == "ref1"
        assert "C2PA" in paper.references[0].text

    def test_plain_text_contains_all_content(self):
        paper = parse_xml(str(SAMPLE_XML))
        text = paper.plain_text()
        assert paper.title in text
        assert "Dr. Elena Vasquez" in text
        assert "large language models" in text  # abstract
        assert "generative AI" in text  # intro
        assert "base-4 encoding" in text  # methodology
        assert "5,000 news articles" in text  # results
        assert "C2PA Technical Specification" in text  # references

    def test_plain_text_length(self):
        paper = parse_xml(str(SAMPLE_XML))
        text = paper.plain_text()
        # Should be a substantial document (half-page = ~2000-5000 chars)
        assert len(text) > 2000


class TestParseInvalidXML:
    """Test parser behavior with edge cases."""

    def test_nonexistent_file_raises(self, tmp_path):
        with pytest.raises(Exception):
            parse_xml(str(tmp_path / "nonexistent.xml"))

    def test_minimal_xml(self, tmp_path):
        xml = tmp_path / "minimal.xml"
        xml.write_text('<?xml version="1.0"?><paper><frontmatter><title>Test</title></frontmatter><body></body></paper>')
        paper = parse_xml(str(xml))
        assert paper.title == "Test"
        assert paper.sections == []
        assert paper.authors == []

    def test_empty_sections(self, tmp_path):
        xml = tmp_path / "empty_sections.xml"
        xml.write_text(
            '<?xml version="1.0"?>'
            "<paper><frontmatter><title>T</title></frontmatter>"
            '<body><section id="s1"><heading>H</heading></section></body></paper>'
        )
        paper = parse_xml(str(xml))
        assert len(paper.sections) == 1
        assert paper.sections[0].heading == "H"
        assert paper.sections[0].paragraphs == []
