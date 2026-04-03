"""Tests for audio metadata injection/extraction (passthrough signing)."""

import struct

import pytest

from app.utils.audio_metadata import (
    extract_encypher_audio_metadata,
    inject_encypher_audio_metadata,
)

_FIELDS = {
    "instance_id": "urn:uuid:test-1234",
    "org_id": "org_abc",
    "document_id": "doc_xyz",
    "content_hash": "sha256:deadbeef",
}


def _make_mp3_stub() -> bytes:
    """Minimal MP3: just sync frames, no ID3."""
    # MP3 sync word (MPEG1, Layer III, 128kbps, 44100Hz, stereo)
    return b"\xff\xfb\x90\x00" + b"\x00" * 413


def _make_mp3_with_id3() -> bytes:
    """MP3 with a minimal existing ID3v2.3 tag."""
    # Build a small TIT2 frame
    payload = b"\x03" + b"Test Title"  # encoding=UTF8 + text
    frame = b"TIT2" + struct.pack(">I", len(payload)) + b"\x00\x00" + payload
    tag_size = len(frame)
    header = b"ID3\x03\x00\x00"  # v2.3, no flags
    header += bytes(
        [
            (tag_size >> 21) & 0x7F,
            (tag_size >> 14) & 0x7F,
            (tag_size >> 7) & 0x7F,
            tag_size & 0x7F,
        ]
    )
    return header + frame + b"\xff\xfb\x90\x00" + b"\x00" * 413


def _make_wav_stub() -> bytes:
    """Minimal WAV with fmt + data chunks."""
    fmt_data = struct.pack("<HHIIHH", 1, 1, 44100, 44100, 1, 8)
    fmt_chunk = b"fmt " + struct.pack("<I", len(fmt_data)) + fmt_data
    audio_data = b"\x80" * 100
    data_chunk = b"data" + struct.pack("<I", len(audio_data)) + audio_data
    riff_body = b"WAVE" + fmt_chunk + data_chunk
    return b"RIFF" + struct.pack("<I", len(riff_body)) + riff_body


class TestMP3Injection:
    def test_roundtrip_no_existing_id3(self):
        mp3 = _make_mp3_stub()
        embedded = inject_encypher_audio_metadata(mp3, "audio/mpeg", **_FIELDS)

        assert embedded != mp3
        assert embedded[:3] == b"ID3"

        extracted = extract_encypher_audio_metadata(embedded, "audio/mpeg")
        assert extracted is not None
        assert extracted["instance_id"] == _FIELDS["instance_id"]
        assert extracted["org_id"] == _FIELDS["org_id"]
        assert extracted["document_id"] == _FIELDS["document_id"]
        assert extracted["content_hash"] == _FIELDS["content_hash"]
        assert extracted["verify"] == "https://verify.encypher.com"

    def test_roundtrip_with_existing_id3(self):
        mp3 = _make_mp3_with_id3()
        embedded = inject_encypher_audio_metadata(mp3, "audio/mpeg", **_FIELDS)

        assert embedded[:3] == b"ID3"

        extracted = extract_encypher_audio_metadata(embedded, "audio/mpeg")
        assert extracted is not None
        assert extracted["instance_id"] == _FIELDS["instance_id"]

    def test_no_metadata_returns_none(self):
        mp3 = _make_mp3_stub()
        assert extract_encypher_audio_metadata(mp3, "audio/mpeg") is None

    def test_unsupported_mime_returns_original(self):
        data = b"some audio data"
        result = inject_encypher_audio_metadata(data, "audio/aac", **_FIELDS)
        assert result == data

    def test_unsupported_mime_extract_returns_none(self):
        assert extract_encypher_audio_metadata(b"data", "audio/aac") is None


class TestWAVInjection:
    def test_roundtrip(self):
        wav = _make_wav_stub()
        embedded = inject_encypher_audio_metadata(wav, "audio/wav", **_FIELDS)

        assert embedded != wav
        assert embedded[:4] == b"RIFF"
        assert len(embedded) > len(wav)

        extracted = extract_encypher_audio_metadata(embedded, "audio/wav")
        assert extracted is not None
        assert extracted["instance_id"] == _FIELDS["instance_id"]
        assert extracted["org_id"] == _FIELDS["org_id"]
        assert extracted["verify"] == "https://verify.encypher.com"

    def test_no_metadata_returns_none(self):
        wav = _make_wav_stub()
        assert extract_encypher_audio_metadata(wav, "audio/wav") is None

    def test_invalid_wav_returns_original(self):
        bad = b"not a wav file"
        result = inject_encypher_audio_metadata(bad, "audio/wav", **_FIELDS)
        assert result == bad
