"""
TEAM_088: Regression tests for C2PA wrapper placement at document level.

Ensures that document-level signing places the C2PA wrapper at the END of
the visible text, not mid-text (e.g., before the last word). The C2PA spec
requires the wrapper to be appended after all visible content.

Root cause: The advanced signing path was adding a per-segment basic embedding
(using WHITESPACE target) even for document-level signing, inserting invisible
characters mid-text. The C2PA wrapper itself was correctly appended at the end,
but the basic embedding was the visible artifact before the last word.
"""

import unicodedata
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

try:
    from encypher.core.keys import generate_ed25519_key_pair
    from encypher.interop.c2pa.text_wrapper import find_and_decode

    ENCYPHER_AVAILABLE = True
except ImportError:
    ENCYPHER_AVAILABLE = False
    pytest.skip("encypher-ai not available", allow_module_level=True)

from app.services.embedding_service import EmbeddingService

# Variation selector ranges per C2PA spec
VS_START = 0xFE00
VS_END = 0xFE0F
VS_SUP_START = 0xE0100
VS_SUP_END = 0xE01EF
ZWNBSP = 0xFEFF


def _is_invisible(ch: str) -> bool:
    """Return True if character is a variation selector or ZWNBSP."""
    cp = ord(ch)
    if VS_START <= cp <= VS_END:
        return True
    if VS_SUP_START <= cp <= VS_SUP_END:
        return True
    if cp == ZWNBSP:
        return True
    return False


def _visible_text(text: str) -> str:
    """Strip all variation selectors and ZWNBSP from text."""
    return "".join(ch for ch in text if not _is_invisible(ch))


def _find_first_invisible_index(text: str) -> int | None:
    """Return the index of the first invisible character, or None."""
    for i, ch in enumerate(text):
        if _is_invisible(ch):
            return i
    return None


class TestDocumentLevelC2PAPlacement:
    """Verify C2PA wrapper is placed at end of text for document-level signing."""

    @pytest.fixture
    def key_pair(self):
        private_key, public_key = generate_ed25519_key_pair()
        return private_key, public_key

    @pytest.fixture
    def service(self, key_pair):
        private_key, _ = key_pair
        return EmbeddingService(private_key, "test_signer_088")

    @pytest.fixture
    async def db_session(self):
        mock_db = AsyncMock()
        mock_db.add_all = MagicMock()
        mock_db.commit = AsyncMock()
        return mock_db

    @pytest.mark.asyncio
    async def test_document_level_wrapper_at_end(self, service, db_session):
        """TEAM_088: Document-level C2PA wrapper must be at the end of visible text."""
        text = (
            "TrendSearch\n"
            "With our newest TrendSearch technology, you can search for relevant trends.\n\n"
            "TrendChat\n"
            "It is your personal, on-demand consultant for turning insights into strategic action."
        )
        segments = [text]
        leaf_hashes = ["hash_doc"]

        _, embedded_document = await service.create_embeddings(
            db=db_session,
            organization_id="org_088",
            document_id="doc_088",
            merkle_root_id=None,
            segments=segments,
            leaf_hashes=leaf_hashes,
        )

        # The visible text should be unchanged
        visible = _visible_text(embedded_document)
        assert visible == unicodedata.normalize("NFC", text), "Visible text must match original (NFC-normalized)"

        # The first invisible character must appear AFTER all visible text
        first_invis = _find_first_invisible_index(embedded_document)
        assert first_invis is not None, "Embedded document must contain invisible characters"

        visible_length = len(unicodedata.normalize("NFC", text))
        assert first_invis >= visible_length, (
            f"First invisible character at index {first_invis} is before end of "
            f"visible text (length {visible_length}). The C2PA wrapper must be "
            f"appended at the end, not inserted mid-text."
        )

    @pytest.mark.asyncio
    async def test_document_level_c2pa_wrapper_decodable(self, service, db_session):
        """TEAM_088: Document-level embedded text must contain a valid C2PA wrapper."""
        text = "This is a simple test document for C2PA embedding."
        segments = [text]
        leaf_hashes = ["hash_simple"]

        _, embedded_document = await service.create_embeddings(
            db=db_session,
            organization_id="org_088",
            document_id="doc_simple",
            merkle_root_id=None,
            segments=segments,
            leaf_hashes=leaf_hashes,
        )

        # The C2PA wrapper must be extractable
        manifest_bytes, clean_text, span = find_and_decode(embedded_document)
        assert manifest_bytes is not None, "C2PA wrapper must be present and decodable"
        assert len(manifest_bytes) > 0, "Manifest bytes must not be empty"

        # Clean text (wrapper removed) must match original
        expected = unicodedata.normalize("NFC", text)
        assert clean_text == expected, f"Clean text after wrapper removal must match original.\nExpected: {expected!r}\nGot:      {clean_text!r}"

    @pytest.mark.asyncio
    async def test_document_level_preserves_newlines(self, service, db_session):
        """TEAM_088: Document-level signing must preserve original whitespace structure."""
        text = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
        segments = [text]
        leaf_hashes = ["hash_newlines"]

        _, embedded_document = await service.create_embeddings(
            db=db_session,
            organization_id="org_088",
            document_id="doc_newlines",
            merkle_root_id=None,
            segments=segments,
            leaf_hashes=leaf_hashes,
        )

        visible = _visible_text(embedded_document)
        expected = unicodedata.normalize("NFC", text)
        assert visible == expected, "Document-level signing must preserve newlines and paragraph breaks"

    @pytest.mark.asyncio
    async def test_document_level_with_custom_assertions(self, service, db_session):
        """TEAM_088: Custom assertions must not cause mid-text embedding."""
        text = "Content with custom assertions for provenance tracking."
        segments = [text]
        leaf_hashes = ["hash_custom"]

        custom_assertions = [
            {
                "label": "org.encypher.user-provenance",
                "data": {"text": "This is AI-generated content."},
            }
        ]

        _, embedded_document = await service.create_embeddings(
            db=db_session,
            organization_id="org_088",
            document_id="doc_custom",
            merkle_root_id=None,
            segments=segments,
            leaf_hashes=leaf_hashes,
            custom_assertions=custom_assertions,
        )

        visible = _visible_text(embedded_document)
        expected = unicodedata.normalize("NFC", text)
        assert visible == expected, "Custom assertions must not cause visible text changes"

        first_invis = _find_first_invisible_index(embedded_document)
        visible_length = len(expected)
        assert first_invis is not None and first_invis >= visible_length, "Custom assertions must not cause mid-text invisible character insertion"

    @pytest.mark.asyncio
    async def test_multi_segment_still_gets_per_segment_embeddings(self, service, db_session):
        """Multi-segment (sentence-level) signing should still add per-segment embeddings."""
        segments = ["First sentence.", "Second sentence.", "Third sentence."]
        leaf_hashes = ["hash1", "hash2", "hash3"]

        embeddings, embedded_document = await service.create_embeddings(
            db=db_session,
            organization_id="org_088",
            document_id="doc_multi",
            merkle_root_id=uuid4(),
            segments=segments,
            leaf_hashes=leaf_hashes,
        )

        assert len(embeddings) == 3

        # Each segment's embedded_text should differ from original (has basic embedding)
        for emb in embeddings:
            assert len(emb.embedded_text) > len(emb.text_content), f"Segment '{emb.text_content}' should have per-segment basic embedding"
