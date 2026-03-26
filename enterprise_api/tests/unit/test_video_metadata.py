"""Tests for video metadata injection/extraction (passthrough signing)."""

import struct

import pytest

from app.utils.video_metadata import (
    extract_encypher_video_metadata,
    inject_encypher_video_metadata,
)

_FIELDS = {
    "instance_id": "urn:uuid:test-vid-5678",
    "org_id": "org_abc",
    "document_id": "doc_vid_xyz",
    "content_hash": "sha256:cafebabe",
}


def _make_mp4_stub() -> bytes:
    """Minimal MP4: ftyp + mdat boxes."""
    ftyp_data = b"isom" + b"\x00\x00\x00\x00" + b"isom" + b"mp41"
    ftyp = struct.pack(">I", 8 + len(ftyp_data)) + b"ftyp" + ftyp_data
    mdat_data = b"\x00" * 100
    mdat = struct.pack(">I", 8 + len(mdat_data)) + b"mdat" + mdat_data
    return ftyp + mdat


def _make_avi_stub() -> bytes:
    """Minimal AVI RIFF container with a proper LIST/movi sub-chunk."""
    movi_data = b"movi" + b"\x00" * 100
    movi_list = b"LIST" + struct.pack("<I", len(movi_data)) + movi_data
    avi_body = b"AVI " + movi_list
    return b"RIFF" + struct.pack("<I", len(avi_body)) + avi_body


class TestMP4Injection:
    def test_roundtrip(self):
        mp4 = _make_mp4_stub()
        embedded = inject_encypher_video_metadata(mp4, "video/mp4", **_FIELDS)

        assert len(embedded) > len(mp4)
        assert embedded[: len(mp4)] == mp4  # original bytes preserved

        extracted = extract_encypher_video_metadata(embedded, "video/mp4")
        assert extracted is not None
        assert extracted["instance_id"] == _FIELDS["instance_id"]
        assert extracted["org_id"] == _FIELDS["org_id"]
        assert extracted["document_id"] == _FIELDS["document_id"]
        assert extracted["content_hash"] == _FIELDS["content_hash"]
        assert extracted["verify"] == "https://verify.encypher.ai/"

    def test_quicktime_also_works(self):
        mp4 = _make_mp4_stub()
        embedded = inject_encypher_video_metadata(mp4, "video/quicktime", **_FIELDS)
        extracted = extract_encypher_video_metadata(embedded, "video/quicktime")
        assert extracted is not None
        assert extracted["instance_id"] == _FIELDS["instance_id"]

    def test_no_metadata_returns_none(self):
        mp4 = _make_mp4_stub()
        assert extract_encypher_video_metadata(mp4, "video/mp4") is None

    def test_unsupported_mime_returns_original(self):
        data = b"some video data"
        result = inject_encypher_video_metadata(data, "video/webm", **_FIELDS)
        assert result == data


class TestAVIInjection:
    def test_roundtrip(self):
        avi = _make_avi_stub()
        embedded = inject_encypher_video_metadata(avi, "video/x-msvideo", **_FIELDS)

        assert embedded[:4] == b"RIFF"
        assert len(embedded) > len(avi)

        extracted = extract_encypher_video_metadata(embedded, "video/x-msvideo")
        assert extracted is not None
        assert extracted["instance_id"] == _FIELDS["instance_id"]
        assert extracted["verify"] == "https://verify.encypher.ai/"

    def test_no_metadata_returns_none(self):
        avi = _make_avi_stub()
        assert extract_encypher_video_metadata(avi, "video/x-msvideo") is None

    def test_invalid_riff_returns_original(self):
        bad = b"not a video"
        result = inject_encypher_video_metadata(bad, "video/x-msvideo", **_FIELDS)
        assert result == bad
