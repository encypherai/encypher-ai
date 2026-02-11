# TEAM_153: Tests for enterprise API signer
"""Tests for the signing integration."""

from unittest.mock import MagicMock, patch

import pytest

from xml_to_pdf.signer import (
    EMBEDDING_MODES,
    SignResult,
    SigningError,
    _extract_document,
    get_api_key,
    sign_text,
)


class TestEmbeddingModes:
    """Verify all expected embedding modes are defined."""

    def test_c2pa_full_mode(self):
        assert "c2pa_full" in EMBEDDING_MODES
        assert EMBEDDING_MODES["c2pa_full"]["manifest_mode"] == "full"
        assert EMBEDDING_MODES["c2pa_full"]["segmentation_level"] == "document"

    def test_lightweight_mode(self):
        assert "lightweight" in EMBEDDING_MODES
        assert EMBEDDING_MODES["lightweight"]["manifest_mode"] == "lightweight_uuid"
        assert EMBEDDING_MODES["lightweight"]["segmentation_level"] == "sentence"

    def test_minimal_mode(self):
        assert "minimal" in EMBEDDING_MODES
        assert EMBEDDING_MODES["minimal"]["manifest_mode"] == "minimal_uuid"
        assert EMBEDDING_MODES["minimal"]["segmentation_level"] == "sentence"

    def test_zw_sentence_mode(self):
        assert "zw_sentence" in EMBEDDING_MODES
        assert EMBEDDING_MODES["zw_sentence"]["manifest_mode"] == "zw_embedding"
        assert EMBEDDING_MODES["zw_sentence"]["segmentation_level"] == "sentence"

    def test_zw_document_mode(self):
        assert "zw_document" in EMBEDDING_MODES
        assert EMBEDDING_MODES["zw_document"]["manifest_mode"] == "zw_embedding"
        assert EMBEDDING_MODES["zw_document"]["segmentation_level"] == "document"

    def test_five_modes_total(self):
        assert len(EMBEDDING_MODES) == 5


class TestGetApiKey:
    """Test API key retrieval."""

    def test_missing_key_raises(self, monkeypatch):
        monkeypatch.delenv("ENCYPHER_API_KEY", raising=False)
        with pytest.raises(SigningError, match="ENCYPHER_API_KEY"):
            get_api_key()

    def test_key_from_env(self, monkeypatch):
        monkeypatch.setenv("ENCYPHER_API_KEY", "test-key-123")
        assert get_api_key() == "test-key-123"


class TestExtractDocument:
    """Test response parsing logic."""

    def test_nested_data_document(self):
        resp = {"data": {"document": {"signed_text": "hello", "document_id": "1"}}}
        doc = _extract_document(resp)
        assert doc["signed_text"] == "hello"

    def test_flat_data(self):
        resp = {"data": {"signed_text": "hello", "document_id": "1"}}
        doc = _extract_document(resp)
        assert doc["signed_text"] == "hello"

    def test_top_level_document(self):
        resp = {"document": {"signed_text": "hello", "document_id": "1"}}
        doc = _extract_document(resp)
        assert doc["signed_text"] == "hello"

    def test_flat_response(self):
        resp = {"signed_text": "hello", "document_id": "1"}
        doc = _extract_document(resp)
        assert doc["signed_text"] == "hello"

    def test_missing_signed_text_raises(self):
        with pytest.raises(SigningError, match="Could not find"):
            _extract_document({"error": "bad"})


class TestSignText:
    """Test sign_text with mocked HTTP."""

    def test_invalid_mode_raises(self):
        with pytest.raises(SigningError, match="Unknown mode"):
            sign_text("text", "title", "nonexistent_mode", api_key="k")

    @patch("xml_to_pdf.signer.httpx.Client")
    def test_successful_sign(self, mock_client_cls, monkeypatch):
        monkeypatch.setenv("ENCYPHER_API_KEY", "test-key")

        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_resp.json.return_value = {
            "success": True,
            "data": {
                "document": {
                    "signed_text": "signed content here",
                    "document_id": "doc-abc",
                    "verification_url": "https://verify.example.com/doc-abc",
                    "total_segments": 3,
                    "merkle_root": "abc123",
                    "instance_id": "inst-xyz",
                }
            },
        }

        mock_client = MagicMock()
        mock_client.post.return_value = mock_resp
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_cls.return_value = mock_client

        result = sign_text("test text", "Test Title", "c2pa_full")

        assert isinstance(result, SignResult)
        assert result.mode == "c2pa_full"
        assert result.signed_text == "signed content here"
        assert result.document_id == "doc-abc"
        assert result.total_segments == 3
        assert result.merkle_root == "abc123"

    @patch("xml_to_pdf.signer.httpx.Client")
    def test_api_error_raises(self, mock_client_cls, monkeypatch):
        monkeypatch.setenv("ENCYPHER_API_KEY", "test-key")

        mock_resp = MagicMock()
        mock_resp.status_code = 403
        mock_resp.text = "Forbidden"

        mock_client = MagicMock()
        mock_client.post.return_value = mock_resp
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_cls.return_value = mock_client

        with pytest.raises(SigningError, match="403"):
            sign_text("text", "title", "c2pa_full")

    @patch("xml_to_pdf.signer.httpx.Client")
    def test_correct_payload_for_zw_sentence(self, mock_client_cls, monkeypatch):
        monkeypatch.setenv("ENCYPHER_API_KEY", "test-key")

        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_resp.json.return_value = {
            "data": {"document": {
                "signed_text": "s", "document_id": "d",
                "verification_url": "v", "total_segments": 1,
            }}
        }

        mock_client = MagicMock()
        mock_client.post.return_value = mock_resp
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_cls.return_value = mock_client

        sign_text("text", "title", "zw_sentence")

        call_args = mock_client.post.call_args
        payload = call_args.kwargs.get("json") or call_args[1].get("json")
        assert payload["options"]["manifest_mode"] == "zw_embedding"
        assert payload["options"]["segmentation_level"] == "sentence"
