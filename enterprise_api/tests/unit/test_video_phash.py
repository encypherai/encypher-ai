"""Tests for video perceptual hash computation."""

import struct
from unittest.mock import patch

import pytest

from app.utils.video_utils import compute_video_phash


def _make_mp4_stub() -> bytes:
    """Minimal MP4: ftyp + mdat boxes."""
    ftyp_data = b"isom" + b"\x00\x00\x00\x00" + b"isom" + b"mp41"
    ftyp = struct.pack(">I", 8 + len(ftyp_data)) + b"ftyp" + ftyp_data
    mdat_data = b"\x00" * 100
    mdat = struct.pack(">I", 8 + len(mdat_data)) + b"mdat" + mdat_data
    return ftyp + mdat


class TestComputeVideoPhash:
    def test_returns_int(self):
        """compute_video_phash always returns an int."""
        result = compute_video_phash(_make_mp4_stub())
        assert isinstance(result, int)

    def test_empty_bytes_returns_zero(self):
        """Empty input returns 0 (graceful failure)."""
        assert compute_video_phash(b"") == 0

    def test_ffmpeg_failure_returns_zero(self):
        """When ffmpeg fails, return 0 instead of raising."""
        with patch("app.utils.video_utils.subprocess") as mock_sub:
            mock_sub.run.side_effect = FileNotFoundError("ffmpeg not found")
            result = compute_video_phash(_make_mp4_stub())
        assert result == 0

    def test_ffmpeg_timeout_returns_zero(self):
        """When ffmpeg times out, return 0."""
        import subprocess as real_subprocess

        with patch("app.utils.video_utils.subprocess") as mock_sub:
            mock_sub.TimeoutExpired = real_subprocess.TimeoutExpired
            mock_sub.run.side_effect = real_subprocess.TimeoutExpired(cmd="ffmpeg", timeout=30)
            result = compute_video_phash(_make_mp4_stub())
        assert result == 0

    def test_result_fits_int64(self):
        """pHash value fits in a signed int64 for PostgreSQL BIGINT."""
        result = compute_video_phash(_make_mp4_stub())
        assert -(2**63) <= result <= (2**63 - 1)
