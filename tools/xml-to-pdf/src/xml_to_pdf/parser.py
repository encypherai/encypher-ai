# TEAM_153: XML parser for research paper documents
"""Parse research paper XML into a structured document model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from lxml import etree


@dataclass
class Author:
    name: str
    affiliation: str = ""


@dataclass
class Reference:
    id: str
    text: str


@dataclass
class Subsection:
    id: str
    heading: str
    paragraphs: list[str] = field(default_factory=list)


@dataclass
class Section:
    id: str
    heading: str
    paragraphs: list[str] = field(default_factory=list)
    subsections: list[Subsection] = field(default_factory=list)


@dataclass
class Paper:
    title: str
    authors: list[Author] = field(default_factory=list)
    abstract: str = ""
    keywords: list[str] = field(default_factory=list)
    sections: list[Section] = field(default_factory=list)
    references: list[Reference] = field(default_factory=list)

    def plain_text(self) -> str:
        """Return the full document as plain text for signing."""
        parts: list[str] = []
        parts.append(self.title)
        parts.append("")
        parts.append(", ".join(a.name for a in self.authors))
        parts.append("")
        parts.append(self.abstract.strip())
        parts.append("")

        for section in self.sections:
            parts.append(section.heading)
            for para in section.paragraphs:
                parts.append(para.strip())
            for sub in section.subsections:
                parts.append(sub.heading)
                for para in sub.paragraphs:
                    parts.append(para.strip())
            parts.append("")

        if self.references:
            parts.append("References")
            for ref in self.references:
                parts.append(ref.text.strip())

        return "\n\n".join(parts)


def parse_xml(xml_path: str) -> Paper:
    """Parse a research paper XML file into a Paper dataclass."""
    tree = etree.parse(xml_path)  # noqa: S320
    root = tree.getroot()

    paper = Paper(title="")

    # Frontmatter
    fm = root.find("frontmatter")
    if fm is not None:
        title_el = fm.find("title")
        if title_el is not None and title_el.text:
            paper.title = title_el.text.strip()

        for author_el in fm.findall(".//author"):
            paper.authors.append(
                Author(
                    name=(author_el.text or "").strip(),
                    affiliation=author_el.get("affiliation", ""),
                )
            )

        abstract_el = fm.find("abstract")
        if abstract_el is not None and abstract_el.text:
            paper.abstract = abstract_el.text.strip()

        for kw_el in fm.findall(".//keyword"):
            if kw_el.text:
                paper.keywords.append(kw_el.text.strip())

    # Body sections
    body = root.find("body")
    if body is not None:
        for sec_el in body.findall("section"):
            section = _parse_section(sec_el)
            paper.sections.append(section)

    # References
    for ref_el in root.findall(".//reference"):
        ref_id = ref_el.get("id", "")
        paper.references.append(
            Reference(id=ref_id, text=(ref_el.text or "").strip())
        )

    return paper


def _parse_section(sec_el: etree._Element) -> Section:
    section = Section(
        id=sec_el.get("id", ""),
        heading="",
    )
    heading_el = sec_el.find("heading")
    if heading_el is not None and heading_el.text:
        section.heading = heading_el.text.strip()

    for para_el in sec_el.findall("paragraph"):
        if para_el.text:
            section.paragraphs.append(para_el.text.strip())

    for sub_el in sec_el.findall("subsection"):
        sub = Subsection(id=sub_el.get("id", ""), heading="")
        sub_heading = sub_el.find("heading")
        if sub_heading is not None and sub_heading.text:
            sub.heading = sub_heading.text.strip()
        for para_el in sub_el.findall("paragraph"):
            if para_el.text:
                sub.paragraphs.append(para_el.text.strip())
        section.subsections.append(sub)

    return section
