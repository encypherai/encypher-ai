"""Tests for TrustMark HTTP client and payload computation."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.trustmark_client import (
    SOFT_BINDING_ASSERTION_IMAGE,
    TrustMarkClient,
    compute_trustmark_key,
    compute_trustmark_payload,
)


class TestComputeTrustmarkPayload:
    def test_returns_25_hex_chars(self):
        result = compute_trustmark_payload("img_abc123", "org_xyz")
        assert len(result) == 25
        int(result, 16)  # validates hex

    def test_deterministic(self):
        a = compute_trustmark_payload("img_1", "org_1")
        b = compute_trustmark_payload("img_1", "org_1")
        assert a == b

    def test_different_inputs_different_output(self):
        a = compute_trustmark_payload("img_1", "org_1")
        b = compute_trustmark_payload("img_2", "org_1")
        c = compute_trustmark_payload("img_1", "org_2")
        assert a != b
        assert a != c


class TestComputeTrustmarkKey:
    def test_format(self):
        key = compute_trustmark_key("img_abc123", "org_xyz")
        assert key.startswith("tm_img_abc123_")
        assert len(key) > len("tm_img_abc123_")

    def test_deterministic(self):
        a = compute_trustmark_key("img_1", "org_1")
        b = compute_trustmark_key("img_1", "org_1")
        assert a == b

    def test_differs_by_org(self):
        a = compute_trustmark_key("img_1", "org_1")
        b = compute_trustmark_key("img_1", "org_2")
        assert a != b


class TestSoftBindingAssertionImage:
    def test_assertion_label(self):
        assert SOFT_BINDING_ASSERTION_IMAGE["label"] == "c2pa.soft_binding.v1"

    def test_assertion_method(self):
        assert SOFT_BINDING_ASSERTION_IMAGE["data"]["method"] == "encypher.trustmark_neural.v1"

    def test_assertion_payload_bits(self):
        assert SOFT_BINDING_ASSERTION_IMAGE["data"]["payload_bits"] == 100

    def test_assertion_has_description(self):
        assert "description" in SOFT_BINDING_ASSERTION_IMAGE["data"]


class TestTrustMarkClientConfigured:
    def test_is_configured_true(self, monkeypatch: pytest.MonkeyPatch):
        from app import config as cfg

        monkeypatch.setattr(cfg.settings, "image_service_url", "http://localhost:8010")
        client = TrustMarkClient()
        assert client.is_configured is True

    def test_is_configured_false(self, monkeypatch: pytest.MonkeyPatch):
        from app import config as cfg

        monkeypatch.setattr(cfg.settings, "image_service_url", "")
        client = TrustMarkClient()
        assert client.is_configured is False


class TestTrustMarkClientUnconfigured:
    @pytest.mark.asyncio
    async def test_apply_returns_none_when_unconfigured(self):
        with patch("app.config.settings") as mock_settings:
            mock_settings.image_service_url = ""
            client = TrustMarkClient()
            result = await client.apply_watermark("b64data", "image/jpeg", "a" * 25)
        assert result is None

    @pytest.mark.asyncio
    async def test_detect_returns_none_when_unconfigured(self):
        with patch("app.config.settings") as mock_settings:
            mock_settings.image_service_url = ""
            client = TrustMarkClient()
            result = await client.detect_watermark("b64data")
        assert result is None


class TestTrustMarkClientApply:
    @pytest.mark.asyncio
    async def test_happy_path(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "watermarked_b64": "watermarked_data",
            "confidence": 0.99,
        }

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.is_closed = False

        with patch("app.config.settings") as mock_settings:
            mock_settings.image_service_url = "http://localhost:8010"
            client = TrustMarkClient()
            client._client = mock_client
            result = await client.apply_watermark("img_b64", "image/jpeg", "a" * 25)

        assert result is not None
        b64, confidence = result
        assert b64 == "watermarked_data"
        assert confidence == 0.99

    @pytest.mark.asyncio
    async def test_sends_message_bits_key(self):
        """TrustMark uses 'message_bits', not 'payload' like spread-spectrum."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "watermarked_b64": "data",
            "confidence": 0.95,
        }

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.is_closed = False

        with patch("app.config.settings") as mock_settings:
            mock_settings.image_service_url = "http://localhost:8010"
            client = TrustMarkClient()
            client._client = mock_client
            await client.apply_watermark("img_b64", "image/jpeg", "deadbeef" * 3 + "d")

        call_kwargs = mock_client.post.call_args
        body = call_kwargs[1]["json"]
        assert "message_bits" in body
        assert "payload" not in body

    @pytest.mark.asyncio
    async def test_service_unavailable_returns_none(self):
        import httpx

        mock_client = AsyncMock()
        mock_client.post.side_effect = httpx.ConnectError("connection refused")
        mock_client.is_closed = False

        with patch("app.config.settings") as mock_settings:
            mock_settings.image_service_url = "http://localhost:8010"
            client = TrustMarkClient()
            client._client = mock_client
            result = await client.apply_watermark("img_b64", "image/jpeg", "a" * 25)

        assert result is None

    @pytest.mark.asyncio
    async def test_500_response_returns_none(self):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.is_closed = False

        with patch("app.config.settings") as mock_settings:
            mock_settings.image_service_url = "http://localhost:8010"
            client = TrustMarkClient()
            client._client = mock_client
            result = await client.apply_watermark("img_b64", "image/jpeg", "a" * 25)

        assert result is None


class TestTrustMarkClientDetect:
    @pytest.mark.asyncio
    async def test_happy_path(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "detected": True,
            "message_bits": "a" * 25,
            "confidence": 0.95,
        }

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.is_closed = False

        with patch("app.config.settings") as mock_settings:
            mock_settings.image_service_url = "http://localhost:8010"
            client = TrustMarkClient()
            client._client = mock_client
            result = await client.detect_watermark("img_b64")

        assert result is not None
        detected, bits, confidence = result
        assert detected is True
        assert bits == "a" * 25
        assert confidence == 0.95

    @pytest.mark.asyncio
    async def test_not_detected(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "detected": False,
            "message_bits": None,
            "confidence": 0.01,
        }

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.is_closed = False

        with patch("app.config.settings") as mock_settings:
            mock_settings.image_service_url = "http://localhost:8010"
            client = TrustMarkClient()
            client._client = mock_client
            result = await client.detect_watermark("img_b64")

        assert result is not None
        detected, bits, confidence = result
        assert detected is False
        assert bits is None
