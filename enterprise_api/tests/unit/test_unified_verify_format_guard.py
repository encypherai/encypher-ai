"""Tests for WebM/MKV format guard in unified verify service."""

import pytest

from app.services.unified_verify_service import verify_media


class TestVideoFormatGuard:
    def test_webm_returns_format_not_supported(self):
        result = verify_media(b"\x1a\x45\xdf\xa3dummy", "video/webm")
        assert result.success is True
        assert result.valid is False
        assert result.reason_code == "FORMAT_NOT_SUPPORTED_FOR_SIGNING"
        assert result.media_type == "video"
        assert "not supported" in result.error.lower()
        assert "MP4" in result.error

    def test_matroska_returns_format_not_supported(self):
        result = verify_media(b"dummydata", "video/x-matroska")
        assert result.success is True
        assert result.valid is False
        assert result.reason_code == "FORMAT_NOT_SUPPORTED_FOR_SIGNING"

    def test_ogg_returns_format_not_supported(self):
        result = verify_media(b"dummydata", "video/ogg")
        assert result.success is True
        assert result.valid is False
        assert result.reason_code == "FORMAT_NOT_SUPPORTED_FOR_SIGNING"

    def test_mp4_does_not_trigger_guard(self):
        """MP4 should proceed to actual C2PA verification, not hit the format guard."""
        result = verify_media(b"\x00\x00\x00\x00ftypmp4", "video/mp4")
        # The actual verify will fail (bad data), but it should NOT be FORMAT_NOT_SUPPORTED
        assert result.reason_code != "FORMAT_NOT_SUPPORTED_FOR_SIGNING"

    def test_quicktime_does_not_trigger_guard(self):
        result = verify_media(b"\x00\x00\x00\x00ftypqt", "video/quicktime")
        assert result.reason_code != "FORMAT_NOT_SUPPORTED_FOR_SIGNING"
