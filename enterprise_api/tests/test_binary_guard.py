"""Tests for binary/encoding guard on text inputs.

Verifies Unix Agent Design criterion 3 (binary guard): text endpoints
reject null bytes, control characters, and other binary content with
a clear, actionable error message.
"""

import pytest
from pydantic import ValidationError

from app.schemas.sign_schemas import SignDocument, UnifiedSignRequest, validate_text_content
from app.schemas.batch import BatchItemPayload


class TestValidateTextContent:
    """Unit tests for the validate_text_content helper."""

    def test_normal_text_passes(self):
        assert validate_text_content("Hello, world!") == "Hello, world!"

    def test_unicode_text_passes(self):
        assert validate_text_content("Bonjour le monde") == "Bonjour le monde"

    def test_multiline_text_passes(self):
        text = "Line one\nLine two\r\nLine three\tTabbed"
        assert validate_text_content(text) == text

    def test_null_byte_rejected(self):
        with pytest.raises(ValueError, match="null bytes"):
            validate_text_content("hello\x00world")

    def test_null_byte_at_start_rejected(self):
        with pytest.raises(ValueError, match="null bytes"):
            validate_text_content("\x00hello")

    def test_control_char_rejected(self):
        with pytest.raises(ValueError, match="control character"):
            validate_text_content("hello\x01world")

    def test_bell_char_rejected(self):
        with pytest.raises(ValueError, match="control character"):
            validate_text_content("hello\x07world")

    def test_tab_allowed(self):
        assert validate_text_content("col1\tcol2") == "col1\tcol2"

    def test_newline_allowed(self):
        assert validate_text_content("line1\nline2") == "line1\nline2"

    def test_carriage_return_allowed(self):
        assert validate_text_content("line1\r\nline2") == "line1\r\nline2"

    def test_empty_string_passes(self):
        assert validate_text_content("") == ""


class TestSignDocumentBinaryGuard:
    """SignDocument.text field rejects binary content."""

    def test_valid_text(self):
        doc = SignDocument(text="Good content")
        assert doc.text == "Good content"

    def test_null_byte_in_text(self):
        with pytest.raises(ValidationError, match="null bytes"):
            SignDocument(text="bad\x00content")

    def test_control_char_in_text(self):
        with pytest.raises(ValidationError, match="control character"):
            SignDocument(text="bad\x02content")


class TestUnifiedSignRequestBinaryGuard:
    """UnifiedSignRequest.text field rejects binary content."""

    def test_valid_single_text(self):
        req = UnifiedSignRequest(text="Good content")
        assert req.text == "Good content"

    def test_null_byte_in_single_text(self):
        with pytest.raises(ValidationError, match="null bytes"):
            UnifiedSignRequest(text="bad\x00content")

    def test_null_byte_in_batch_document(self):
        with pytest.raises(ValidationError, match="null bytes"):
            UnifiedSignRequest(
                documents=[
                    SignDocument(text="good text"),
                    SignDocument(text="bad\x00text"),
                ]
            )


class TestBatchItemPayloadBinaryGuard:
    """BatchItemPayload.text field rejects binary content."""

    def test_valid_text(self):
        item = BatchItemPayload(document_id="doc1", text="Good content")
        assert item.text == "Good content"

    def test_null_byte_rejected(self):
        with pytest.raises(ValidationError, match="null bytes"):
            BatchItemPayload(document_id="doc1", text="bad\x00content")

    def test_control_char_rejected(self):
        with pytest.raises(ValidationError, match="control character"):
            BatchItemPayload(document_id="doc1", text="bad\x03content")
