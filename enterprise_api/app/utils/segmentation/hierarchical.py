"""
Hierarchical text segmentation.

Combines sentence, paragraph, and section segmentation into a unified structure.
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

from .sentence import segment_sentences
from .paragraph import segment_paragraphs
from .section import segment_sections
from .word import segment_words_simple

# Import default segmenter (spaCy-based with Unicode normalization)
try:
    from .default import segment_sentences_default, segment_words_default, SPACY_AVAILABLE
    USE_DEFAULT = True
except ImportError:
    USE_DEFAULT = False
    SPACY_AVAILABLE = False


@dataclass
class HierarchicalSegment:
    """
    A segment in a hierarchical structure.
    
    Attributes:
        text: The text content
        level: Segmentation level (sentence/paragraph/section)
        index: Position within level
        parent_index: Index of parent segment (if any)
        children_indices: Indices of child segments
        metadata: Additional metadata
    """
    text: str
    level: str
    index: int
    parent_index: Optional[int] = None
    children_indices: List[int] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'text': self.text,
            'level': self.level,
            'index': self.index,
            'parent_index': self.parent_index,
            'children_indices': self.children_indices,
            'metadata': self.metadata
        }


class HierarchicalSegmenter:
    """
    Segments text at multiple hierarchical levels.
    
    Creates a structure where:
    - Sections contain paragraphs
    - Paragraphs contain sentences
    - Each level can be queried independently
    """
    
    def __init__(self, text: str, include_words: bool = False):
        """
        Initialize segmenter with text.
        
        Args:
            text: Input text to segment
            include_words: If True, also segment at word level (finest granularity)
        """
        self.text = text
        self.include_words = include_words
        self.words: List[str] = []
        self.sentences: List[str] = []
        self.paragraphs: List[str] = []
        self.sections: List[str] = []
        self.hierarchy: Dict[str, List[HierarchicalSegment]] = {}
        
        # Perform segmentation
        self._segment_all_levels()
    
    def _segment_all_levels(self) -> None:
        """Segment text at all levels using best available methods."""
        # Use spaCy-based default segmentation if available
        if USE_DEFAULT and SPACY_AVAILABLE:
            if self.include_words:
                self.words = segment_words_default(self.text, normalize=True)
            self.sentences = segment_sentences_default(self.text, normalize=True)
        else:
            # Fallback to regex-based segmentation
            if self.include_words:
                self.words = segment_words_simple(self.text)
            self.sentences = segment_sentences(self.text)
        
        # Paragraph and section segmentation (regex-based is fine for these)
        self.paragraphs = segment_paragraphs(self.text)
        self.sections = segment_sections(self.text)
    
    def get_segments(self, level: str) -> List[str]:
        """
        Get segments at a specific level.
        
        Args:
            level: 'word', 'sentence', 'paragraph', or 'section'
        
        Returns:
            List of segments
        
        Raises:
            ValueError: If level is invalid
        """
        if level == 'word':
            if not self.include_words:
                raise ValueError("Word segmentation not enabled. Initialize with include_words=True")
            return self.words
        elif level == 'sentence':
            return self.sentences
        elif level == 'paragraph':
            return self.paragraphs
        elif level == 'section':
            return self.sections
        else:
            valid_levels = "'word', 'sentence', 'paragraph', or 'section'" if self.include_words else "'sentence', 'paragraph', or 'section'"
            raise ValueError(f"Invalid level: {level}. Must be {valid_levels}")
    
    def count_segments(self, level: str) -> int:
        """
        Count segments at a specific level.
        
        Args:
            level: 'sentence', 'paragraph', or 'section'
        
        Returns:
            Number of segments
        """
        return len(self.get_segments(level))
    
    def build_hierarchy(self) -> Dict[str, List[HierarchicalSegment]]:
        """
        Build hierarchical structure linking all levels.
        
        Returns:
            Dictionary mapping levels to hierarchical segments
        """
        hierarchy = {
            'sentence': [],
            'paragraph': [],
            'section': []
        }
        
        # Create sentence segments
        for i, sentence in enumerate(self.sentences):
            hierarchy['sentence'].append(
                HierarchicalSegment(
                    text=sentence,
                    level='sentence',
                    index=i,
                    metadata={'length': len(sentence)}
                )
            )
        
        # Create paragraph segments and link sentences
        for i, paragraph in enumerate(self.paragraphs):
            para_sentences = segment_sentences(paragraph)
            sentence_indices = []
            
            # Find which sentences belong to this paragraph
            for sent_idx, sentence in enumerate(self.sentences):
                if sentence in para_sentences:
                    sentence_indices.append(sent_idx)
                    if sent_idx < len(hierarchy['sentence']):
                        hierarchy['sentence'][sent_idx].parent_index = i
            
            hierarchy['paragraph'].append(
                HierarchicalSegment(
                    text=paragraph,
                    level='paragraph',
                    index=i,
                    children_indices=sentence_indices,
                    metadata={'length': len(paragraph), 'sentence_count': len(para_sentences)}
                )
            )
        
        # Create section segments and link paragraphs
        for i, section in enumerate(self.sections):
            section_paragraphs = segment_paragraphs(section)
            paragraph_indices = []
            
            # Find which paragraphs belong to this section
            for para_idx, paragraph in enumerate(self.paragraphs):
                if paragraph in section_paragraphs:
                    paragraph_indices.append(para_idx)
                    if para_idx < len(hierarchy['paragraph']):
                        hierarchy['paragraph'][para_idx].parent_index = i
            
            hierarchy['section'].append(
                HierarchicalSegment(
                    text=section,
                    level='section',
                    index=i,
                    children_indices=paragraph_indices,
                    metadata={'length': len(section), 'paragraph_count': len(section_paragraphs)}
                )
            )
        
        self.hierarchy = hierarchy
        return hierarchy
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize segmenter state to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            'text_length': len(self.text),
            'sentence_count': len(self.sentences),
            'paragraph_count': len(self.paragraphs),
            'section_count': len(self.sections),
            'sentences': self.sentences,
            'paragraphs': self.paragraphs,
            'sections': self.sections
        }


def build_hierarchical_structure(text: str) -> Dict[str, List[str]]:
    """
    Build hierarchical structure from text (convenience function).
    
    Args:
        text: Input text
    
    Returns:
        Dictionary with 'sentences', 'paragraphs', 'sections' keys
    
    Example:
        >>> text = "First sentence. Second sentence.\\n\\nNew paragraph."
        >>> structure = build_hierarchical_structure(text)
        >>> structure['sentences']
        ['First sentence.', 'Second sentence.', 'New paragraph.']
    """
    segmenter = HierarchicalSegmenter(text)
    return {
        'sentences': segmenter.sentences,
        'paragraphs': segmenter.paragraphs,
        'sections': segmenter.sections
    }


def segment_at_all_levels(text: str) -> Dict[str, List[str]]:
    """
    Segment text at all levels (alias for build_hierarchical_structure).
    
    Args:
        text: Input text
    
    Returns:
        Dictionary with segments at all levels
    """
    return build_hierarchical_structure(text)
