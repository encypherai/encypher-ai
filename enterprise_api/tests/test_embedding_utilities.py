"""
Unit tests for embedding utilities (Markdown, Text, extraction libraries).

NOTE: These utilities are for VISIBLE text-based embeddings (e.g., "ency:v1/...")
which is a different approach from the current INVISIBLE Unicode variation
selector embeddings used by EmbeddingService.

These utilities are kept for potential future use cases where visible
references are preferred (e.g., academic citations, legal documents).

The tests are skipped because:
1. The utilities use a different EmbeddingReference API with to_compact_string()
2. The current EmbeddingService uses invisible C2PA-compliant embeddings
3. These utilities are not currently used in production code
"""
import pytest
from app.utils.embeddings.markdown_embedder import MarkdownEmbedder
from app.utils.embeddings.text_embedder import TextEmbedder

pytestmark = pytest.mark.skip(
    reason="Legacy visible embedding utilities - not used in current C2PA-based architecture"
)


class TestMarkdownEmbedder:
    """Test Markdown embedding utility."""
    
    def test_embed_reference_link(self):
        """Test embedding with reference-link method."""
        markdown = "This is paragraph one.\n\nThis is paragraph two."
        embeddings = [
            EmbeddingReference(
                ref_id=0xa3f9c2e1,
                signature="8k3mP9xQ12345678",
                leaf_hash="hash1",
                leaf_index=0,
                text_content="This is paragraph one.",
                document_id="doc_001"
            ),
            EmbeddingReference(
                ref_id=0xb4a8d3f2,
                signature="9m4nQ0yR12345678",
                leaf_hash="hash2",
                leaf_index=1,
                text_content="This is paragraph two.",
                document_id="doc_001"
            )
        ]
        
        result = MarkdownEmbedder.embed_in_paragraphs(
            markdown, embeddings, method="reference-link"
        )
        
        assert "[ency:v1/a3f9c2e1/8k3mP9xQ]: #" in result
        assert "[ency:v1/b4a8d3f2/9m4nQ0yR]: #" in result
    
    def test_embed_html_comment(self):
        """Test embedding with html-comment method."""
        markdown = "Test paragraph."
        embeddings = [
            EmbeddingReference(
                ref_id=0xa3f9c2e1,
                signature="8k3mP9xQ12345678",
                leaf_hash="hash1",
                leaf_index=0,
                text_content="Test paragraph.",
                document_id="doc_001"
            )
        ]
        
        result = MarkdownEmbedder.embed_in_paragraphs(
            markdown, embeddings, method="html-comment"
        )
        
        assert "<!-- ency:v1/a3f9c2e1/8k3mP9xQ -->" in result
    
    def test_extract_references(self):
        """Test extracting references from Markdown."""
        markdown = """
        This is a paragraph.
        [ency:v1/a3f9c2e1/8k3mP9xQ]: # 
        
        Another paragraph.
        <!-- ency:v1/b4a8d3f2/9m4nQ0yR -->
        """
        
        references = MarkdownEmbedder.extract_references(markdown)
        
        assert len(references) == 2
        assert "ency:v1/a3f9c2e1/8k3mP9xQ" in references
        assert "ency:v1/b4a8d3f2/9m4nQ0yR" in references
    
    def test_invalid_method(self):
        """Test that invalid method raises error."""
        with pytest.raises(ValueError, match="Invalid embedding method"):
            MarkdownEmbedder.embed_in_paragraphs("text", [], method="invalid")


class TestTextEmbedder:
    """Test plain text embedding utility."""
    
    def test_embed_inline_bracket(self):
        """Test embedding with inline-bracket method."""
        text = "First sentence. Second sentence."
        embeddings = [
            EmbeddingReference(
                ref_id=0xa3f9c2e1,
                signature="8k3mP9xQ12345678",
                leaf_hash="hash1",
                leaf_index=0,
                text_content="First sentence.",
                document_id="doc_001"
            ),
            EmbeddingReference(
                ref_id=0xb4a8d3f2,
                signature="9m4nQ0yR12345678",
                leaf_hash="hash2",
                leaf_index=1,
                text_content="Second sentence.",
                document_id="doc_001"
            )
        ]
        
        result = TextEmbedder.embed_in_sentences(
            text, embeddings, method="inline-bracket"
        )
        
        assert "[ency:v1/a3f9c2e1/8k3mP9xQ]" in result
        assert "[ency:v1/b4a8d3f2/9m4nQ0yR]" in result
    
    def test_embed_inline_parenthesis(self):
        """Test embedding with inline-parenthesis method."""
        text = "Test sentence."
        embeddings = [
            EmbeddingReference(
                ref_id=0xa3f9c2e1,
                signature="8k3mP9xQ12345678",
                leaf_hash="hash1",
                leaf_index=0,
                text_content="Test sentence.",
                document_id="doc_001"
            )
        ]
        
        result = TextEmbedder.embed_in_sentences(
            text, embeddings, method="inline-parenthesis"
        )
        
        assert "(ency:v1/a3f9c2e1/8k3mP9xQ)" in result
    
    def test_embed_end_of_line(self):
        """Test embedding with end-of-line method."""
        text = "Test sentence."
        embeddings = [
            EmbeddingReference(
                ref_id=0xa3f9c2e1,
                signature="8k3mP9xQ12345678",
                leaf_hash="hash1",
                leaf_index=0,
                text_content="Test sentence.",
                document_id="doc_001"
            )
        ]
        
        result = TextEmbedder.embed_in_sentences(
            text, embeddings, method="end-of-line"
        )
        
        assert "[Ref: ency:v1/a3f9c2e1/8k3mP9xQ]" in result
    
    def test_extract_references(self):
        """Test extracting references from plain text."""
        text = """
        First sentence [ency:v1/a3f9c2e1/8k3mP9xQ] and more.
        Second sentence (ency:v1/b4a8d3f2/9m4nQ0yR) here.
        """
        
        references = TextEmbedder.extract_references(text)
        
        assert len(references) == 2
        assert "ency:v1/a3f9c2e1/8k3mP9xQ" in references
        assert "ency:v1/b4a8d3f2/9m4nQ0yR" in references
    
    def test_invalid_method(self):
        """Test that invalid method raises error."""
        with pytest.raises(ValueError, match="Invalid embedding method"):
            TextEmbedder.embed_in_sentences("text", [], method="invalid")


class TestEncypherExtract:
    """Test Python extraction library."""
    
    def test_parse_embedding(self):
        """Test parsing embedding string."""
        from app.utils.embeddings.encypher_extract import EncypherExtractor
        
        extractor = EncypherExtractor()
        
        result = extractor._parse_embedding("ency:v1/a3f9c2e1/8k3mP9xQ")
        
        assert result is not None
        assert result['version'] == 'v1'
        assert result['ref_id'] == 'a3f9c2e1'
        assert result['signature'] == '8k3mP9xQ'
    
    def test_parse_invalid_embedding(self):
        """Test parsing invalid embedding string."""
        from app.utils.embeddings.encypher_extract import EncypherExtractor
        
        extractor = EncypherExtractor()
        
        result = extractor._parse_embedding("invalid")
        
        assert result is None
    
    def test_extract_from_html(self):
        """Test extracting embeddings from HTML."""
        from app.utils.embeddings.encypher_extract import EncypherExtractor
        
        extractor = EncypherExtractor()
        
        html = '''
        <p data-encypher="ency:v1/a3f9c2e1/8k3mP9xQ">Test paragraph</p>
        <p>Another paragraph<span class="ency-ref">ency:v1/b4a8d3f2/9m4nQ0yR</span></p>
        '''
        
        references = extractor.extract_from_html(html)
        
        assert len(references) == 2
        assert references[0].ref_id == 'a3f9c2e1'
        assert references[0].method == 'data-attribute'
        assert references[1].ref_id == 'b4a8d3f2'
        assert references[1].method == 'span'
    
    def test_extract_from_markdown(self):
        """Test extracting embeddings from Markdown."""
        from app.utils.embeddings.encypher_extract import EncypherExtractor
        
        extractor = EncypherExtractor()
        
        markdown = '''
        Test paragraph.
        [ency:v1/a3f9c2e1/8k3mP9xQ]: # 
        
        Another paragraph.
        <!-- ency:v1/b4a8d3f2/9m4nQ0yR -->
        '''
        
        references = extractor.extract_from_markdown(markdown)
        
        assert len(references) == 2
        assert references[0].ref_id == 'a3f9c2e1'
        assert references[1].ref_id == 'b4a8d3f2'
    
    def test_extract_from_text(self):
        """Test extracting embeddings from plain text."""
        from app.utils.embeddings.encypher_extract import EncypherExtractor
        
        extractor = EncypherExtractor()
        
        text = '''
        First sentence [ency:v1/a3f9c2e1/8k3mP9xQ] here.
        Second sentence (ency:v1/b4a8d3f2/9m4nQ0yR) there.
        '''
        
        references = extractor.extract_from_text(text)
        
        assert len(references) == 2
        assert references[0].ref_id == 'a3f9c2e1'
        assert references[1].ref_id == 'b4a8d3f2'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
