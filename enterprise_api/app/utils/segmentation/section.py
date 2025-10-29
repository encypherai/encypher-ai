"""
Section-level text segmentation.

Segments text into sections based on headers and structural markers.
"""
import re
from typing import List, Dict, Any


def segment_sections(text: str, min_length: int = 50) -> List[str]:
    """
    Segment text into sections.
    
    Sections are detected by:
    - Markdown headers (# ## ###)
    - All-caps lines (SECTION TITLE)
    - Numbered sections (1. Section, 1.1 Subsection)
    - Horizontal rules (---, ***)
    
    Args:
        text: Input text to segment
        min_length: Minimum section length in characters (default: 50)
    
    Returns:
        List of sections
    
    Example:
        >>> text = "# Introduction\\nText here.\\n\\n# Methods\\nMore text."
        >>> segment_sections(text)
        ['# Introduction\\nText here.', '# Methods\\nMore text.']
    """
    if not text or not text.strip():
        return []
    
    lines = text.split('\n')
    sections = []
    current_section = []
    
    for line in lines:
        stripped = line.strip()
        
        # Check for section markers
        is_markdown_header = stripped.startswith('#')
        is_horizontal_rule = stripped.startswith(('---', '***', '___')) and len(stripped) >= 3
        is_numbered_section = re.match(r'^\d+(\.\d+)*\.?\s+[A-Z]', stripped)
        is_all_caps_header = (
            len(stripped) > 0 and 
            len(stripped) < 100 and 
            stripped.isupper() and 
            not stripped.startswith(('HTTP', 'URL', 'API', 'ID'))
        )
        
        is_section_break = (
            is_markdown_header or 
            is_horizontal_rule or 
            is_numbered_section or 
            is_all_caps_header
        )
        
        if is_section_break and current_section:
            # Save previous section
            section_text = '\n'.join(current_section).strip()
            if len(section_text) >= min_length:
                sections.append(section_text)
            current_section = []
        
        current_section.append(line)
    
    # Add final section
    if current_section:
        section_text = '\n'.join(current_section).strip()
        if len(section_text) >= min_length:
            sections.append(section_text)
    
    return sections


def segment_sections_with_titles(text: str) -> List[Dict[str, Any]]:
    """
    Segment text into sections with extracted titles.
    
    Args:
        text: Input text
    
    Returns:
        List of dicts with 'title' and 'content' keys
    
    Example:
        >>> text = "# Introduction\\nText here."
        >>> segment_sections_with_titles(text)
        [{'title': 'Introduction', 'content': 'Text here.', 'level': 1}]
    """
    if not text or not text.strip():
        return []
    
    lines = text.split('\n')
    sections = []
    current_title = None
    current_level = 0
    current_content = []
    
    for line in lines:
        stripped = line.strip()
        
        # Check for markdown header
        header_match = re.match(r'^(#{1,6})\s+(.+)$', stripped)
        if header_match:
            # Save previous section
            if current_title is not None:
                sections.append({
                    'title': current_title,
                    'content': '\n'.join(current_content).strip(),
                    'level': current_level
                })
            
            # Start new section
            current_level = len(header_match.group(1))
            current_title = header_match.group(2).strip()
            current_content = []
            continue
        
        # Check for numbered section
        numbered_match = re.match(r'^(\d+(?:\.\d+)*)\.\s+(.+)$', stripped)
        if numbered_match:
            # Save previous section
            if current_title is not None:
                sections.append({
                    'title': current_title,
                    'content': '\n'.join(current_content).strip(),
                    'level': current_level
                })
            
            # Start new section
            section_num = numbered_match.group(1)
            current_level = section_num.count('.') + 1
            current_title = numbered_match.group(2).strip()
            current_content = []
            continue
        
        # Add to current section content
        if current_title is not None:
            current_content.append(line)
    
    # Add final section
    if current_title is not None:
        sections.append({
            'title': current_title,
            'content': '\n'.join(current_content).strip(),
            'level': current_level
        })
    
    return sections


def extract_section_titles(text: str) -> List[str]:
    """
    Extract section titles from text.
    
    Args:
        text: Input text
    
    Returns:
        List of section titles
    """
    sections = segment_sections_with_titles(text)
    return [section['title'] for section in sections]


def count_sections(text: str) -> int:
    """
    Count sections in text.
    
    Args:
        text: Input text
    
    Returns:
        Number of sections
    """
    return len(segment_sections(text))
