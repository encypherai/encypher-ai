"""Tests for audio watermark HTTP client and payload computation."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.audio_watermark_client import (
    AudioWatermarkClient,
    compute_audio_watermark_key,
    compute_audio_watermark_payload,
)


class TestComputeAudioWatermarkPayload:
    def test_returns_16_hex_chars(self):
        result = compute_audio_watermark_payload("audio_abc123", "org_xyz")
        assert len(result) == 16
        int(result, 16)  # validates hex

    def test_deterministic(self):
        a = compute_audio_watermark_payload("audio_1", "org_1")
        b = compute_audio_watermark_payload("audio_1", "org_1")
        assert a == b

    def test_different_inputs_different_output(self):
        a = compute_audio_watermark_payload("audio_1", "org_1")
        b = compute_audio_watermark_payload("audio_2", "org_1")
        c = compute_audio_watermark_payload("audio_1", "org_2")
        assert a != b
        assert a != c


class TestComputeAudioWatermarkKey:
    def test_format(self):
        key = compute_audio_watermark_key("audio_abc123", "org_xyz")
        assert key.startswith("awm_audio_abc123_")
        assert len(key) > len("awm_audio_abc123_")

    def test_deterministic(self):
        a = compute_audio_watermark_key("audio_1", "org_1")
        b = compute_audio_watermark_key("audio_1", "org_1")
        assert a == b


class TestAudioWatermarkClientUnconfigured:
    @pytest.mark.asyncio
    async def test_apply_returns_none_when_unconfigured(self):
        with patch("app.services.audio_watermark_client.settings") as mock_settings:
            mock_settings.audio_watermark_service_url = ""
            client = AudioWatermarkClient()
            result = await client.apply_watermark("b64data", "audio/wav", "a" * 16)
        assert result is None

    @pytest.mark.asyncio
    async def test_detect_returns_none_when_unconfigured(self):
        with patch("app.services.audio_watermark_client.settings") as mock_settings:
            mock_settings.audio_watermark_service_url = ""
            client = AudioWatermarkClient()
            result = await client.detect_watermark("b64data", "audio/wav")
        assert result is None


class TestAudioWatermarkClientApply:
    @pytest.mark.asyncio
    async def test_happy_path(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "watermarked_b64": "watermarked_audio_data",
            "payload": "deadbeefcafebabe",
            "confidence": 0.95,
            "processing_time_ms": 123.4,
        }

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with (
            patch("app.services.audio_watermark_client.settings") as mock_settings,
            patch("app.services.audio_watermark_client.httpx.AsyncClient", return_value=mock_client),
        ):
            mock_settings.audio_watermark_service_url = "http://localhost:8011"
            client = AudioWatermarkClient()
            result = await client.apply_watermark("audio_b64", "audio/wav", "deadbeefcafebabe")

        assert result is not None
        b64, confidence = result
        assert b64 == "watermarked_audio_data"
        assert confidence == 0.95

    @pytest.mark.asyncio
    async def test_passes_snr_db_when_provided(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "watermarked_b64": "data",
            "payload": "deadbeefcafebabe",
            "confidence": 0.9,
            "processing_time_ms": 100.0,
        }

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with (
            patch("app.services.audio_watermark_client.settings") as mock_settings,
            patch("app.services.audio_watermark_client.httpx.AsyncClient", return_value=mock_client),
        ):
            mock_settings.audio_watermark_service_url = "http://localhost:8011"
            client = AudioWatermarkClient()
            await client.apply_watermark("audio_b64", "audio/wav", "deadbeefcafebabe", snr_db=-30.0)

        call_kwargs = mock_client.post.call_args
        body = call_kwargs[1]["json"] if "json" in call_kwargs[1] else call_kwargs[0][1]
        assert body["snr_db"] == -30.0

    @pytest.mark.asyncio
    async def test_service_unavailable_returns_none(self):
        import httpx

        mock_client = AsyncMock()
        mock_client.post.side_effect = httpx.ConnectError("connection refused")
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with (
            patch("app.services.audio_watermark_client.settings") as mock_settings,
            patch("app.services.audio_watermark_client.httpx.AsyncClient", return_value=mock_client),
        ):
            mock_settings.audio_watermark_service_url = "http://localhost:8011"
            client = AudioWatermarkClient()
            result = await client.apply_watermark("audio_b64", "audio/wav", "a" * 16)

        assert result is None

    @pytest.mark.asyncio
    async def test_500_response_returns_none(self):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with (
            patch("app.services.audio_watermark_client.settings") as mock_settings,
            patch("app.services.audio_watermark_client.httpx.AsyncClient", return_value=mock_client),
        ):
            mock_settings.audio_watermark_service_url = "http://localhost:8011"
            client = AudioWatermarkClient()
            result = await client.apply_watermark("audio_b64", "audio/wav", "a" * 16)

        assert result is None


class TestAudioWatermarkClientDetect:
    @pytest.mark.asyncio
    async def test_happy_path(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "detected": True,
            "payload": "deadbeefcafebabe",
            "confidence": 0.92,
            "processing_time_ms": 85.0,
        }

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with (
            patch("app.services.audio_watermark_client.settings") as mock_settings,
            patch("app.services.audio_watermark_client.httpx.AsyncClient", return_value=mock_client),
        ):
            mock_settings.audio_watermark_service_url = "http://localhost:8011"
            client = AudioWatermarkClient()
            result = await client.detect_watermark("audio_b64", "audio/wav")

        assert result is not None
        detected, payload, confidence = result
        assert detected is True
        assert payload == "deadbeefcafebabe"
        assert confidence == 0.92

    @pytest.mark.asyncio
    async def test_not_detected(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "detected": False,
            "payload": None,
            "confidence": 0.01,
            "processing_time_ms": 80.0,
        }

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with (
            patch("app.services.audio_watermark_client.settings") as mock_settings,
            patch("app.services.audio_watermark_client.httpx.AsyncClient", return_value=mock_client),
        ):
            mock_settings.audio_watermark_service_url = "http://localhost:8011"
            client = AudioWatermarkClient()
            result = await client.detect_watermark("audio_b64", "audio/wav")

        assert result is not None
        detected, payload, confidence = result
        assert detected is False
        assert payload is None
