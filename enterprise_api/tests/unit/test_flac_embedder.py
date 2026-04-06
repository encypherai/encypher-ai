"""Tests for FLAC C2PA embedder."""

import hashlib
import struct

import pytest

from app.utils.flac_c2pa_embedder import (
    C2PA_APP_ID,
    FLAC_MAGIC,
    _parse_metadata_blocks,
    compute_flac_hash,
    create_flac_with_placeholder,
    replace_manifest_in_flac,
)


def _make_minimal_flac() -> bytes:
    """Build a minimal valid FLAC file: magic + STREAMINFO (is_last=1)."""
    # STREAMINFO: 34 bytes of data
    # min_block_size=4096, max_block_size=4096, min_frame_size=0,
    # max_frame_size=0, sample_rate=44100, channels=1(0), bps=16(15),
    # total_samples=0, md5=zeros
    streaminfo_data = (
        b"\x10\x00\x10\x00"  # min/max block size
        b"\x00\x00\x00\x00\x00\x00"  # min/max frame size
        b"\x0a\xc4\x40\xf0\x00\x00\x00\x00" + b"\x00" * 16  # sample_rate/channels/bps/total  # MD5
    )
    assert len(streaminfo_data) == 34

    # STREAMINFO header: is_last=1, type=0, length=34
    header = bytes([0x80]) + struct.pack(">I", 34)[1:]
    return FLAC_MAGIC + header + streaminfo_data


def _make_flac_with_extra_blocks() -> bytes:
    """Build a FLAC file with STREAMINFO + VORBIS_COMMENT + PADDING."""
    streaminfo_data = b"\x10\x00\x10\x00\x00\x00\x00\x00\x00\x00\x0a\xc4\x40\xf0\x00\x00\x00\x00" + b"\x00" * 16

    # STREAMINFO: is_last=0, type=0, length=34
    si_header = bytes([0x00]) + struct.pack(">I", 34)[1:]

    # VORBIS_COMMENT (type=4): is_last=0, 8 bytes of dummy data
    vc_data = b"\x04\x00\x00\x00test\x00\x00\x00\x00"
    vc_header = bytes([0x04]) + struct.pack(">I", len(vc_data))[1:]

    # PADDING (type=1): is_last=1, 16 bytes
    pad_data = b"\x00" * 16
    pad_header = bytes([0x81]) + struct.pack(">I", 16)[1:]

    return FLAC_MAGIC + si_header + streaminfo_data + vc_header + vc_data + pad_header + pad_data


class TestParseMetadataBlocks:
    def test_minimal_flac(self):
        data = _make_minimal_flac()
        blocks = _parse_metadata_blocks(data)
        assert len(blocks) == 1
        assert blocks[0]["type"] == 0  # STREAMINFO
        assert blocks[0]["is_last"] is True
        assert blocks[0]["length"] == 34

    def test_multi_block_flac(self):
        data = _make_flac_with_extra_blocks()
        blocks = _parse_metadata_blocks(data)
        assert len(blocks) == 3
        assert blocks[0]["type"] == 0  # STREAMINFO
        assert blocks[0]["is_last"] is False
        assert blocks[1]["type"] == 4  # VORBIS_COMMENT
        assert blocks[2]["type"] == 1  # PADDING
        assert blocks[2]["is_last"] is True

    def test_not_flac_raises(self):
        with pytest.raises(ValueError, match="Not a valid FLAC"):
            _parse_metadata_blocks(b"RIFF" + b"\x00" * 40)

    def test_truncated_raises(self):
        with pytest.raises(ValueError, match="Not a valid FLAC"):
            _parse_metadata_blocks(b"fLa")


class TestCreateFlacWithPlaceholder:
    def test_minimal_flac_placeholder(self):
        flac = _make_minimal_flac()
        result, offset, length = create_flac_with_placeholder(flac, placeholder_size=1024)

        # Result starts with fLaC magic
        assert result[:4] == FLAC_MAGIC

        # Parse blocks in result
        blocks = _parse_metadata_blocks(result)
        assert len(blocks) == 2

        # STREAMINFO is no longer last
        assert blocks[0]["type"] == 0
        assert blocks[0]["is_last"] is False

        # APPLICATION block is last
        assert blocks[1]["type"] == 2  # APPLICATION
        assert blocks[1]["is_last"] is True

        # APPLICATION block has c2pa app ID
        app_data_start = blocks[1]["data_offset"]
        assert result[app_data_start : app_data_start + 4] == C2PA_APP_ID

        # Placeholder is zeros
        assert result[offset : offset + length] == b"\x00" * 1024
        assert length == 1024

        # Offset matches expected position: after header + app_id
        assert offset == app_data_start + 4

    def test_multi_block_flac_placeholder(self):
        flac = _make_flac_with_extra_blocks()
        result, offset, length = create_flac_with_placeholder(flac, placeholder_size=512)

        blocks = _parse_metadata_blocks(result)
        # STREAMINFO + C2PA APPLICATION + VORBIS_COMMENT + PADDING
        assert len(blocks) == 4
        assert blocks[0]["type"] == 0  # STREAMINFO, not last
        assert blocks[0]["is_last"] is False
        assert blocks[1]["type"] == 2  # APPLICATION (C2PA), not last
        assert blocks[1]["is_last"] is False
        assert blocks[3]["is_last"] is True  # Last block has is_last

        # C2PA block has correct app ID
        app_start = blocks[1]["data_offset"]
        assert result[app_start : app_start + 4] == C2PA_APP_ID

    def test_placeholder_data_is_at_returned_offset(self):
        flac = _make_minimal_flac()
        result, offset, length = create_flac_with_placeholder(flac, placeholder_size=256)
        # All placeholder bytes are zero
        assert result[offset : offset + length] == b"\x00" * 256


class TestComputeFlacHash:
    def test_excludes_manifest_range(self):
        flac = _make_minimal_flac()
        result, offset, length = create_flac_with_placeholder(flac, placeholder_size=128)

        hash1 = compute_flac_hash(result, offset, length)

        # Manually compute expected hash (skip exclusion range)
        h = hashlib.sha256()
        h.update(result[:offset])
        h.update(result[offset + length :])
        expected = h.digest()

        assert hash1 == expected

    def test_different_data_same_hash_with_exclusion(self):
        """Replacing manifest data should not change the hash (exclusion works)."""
        flac = _make_minimal_flac()
        result, offset, length = create_flac_with_placeholder(flac, placeholder_size=128)

        hash1 = compute_flac_hash(result, offset, length)

        # Replace placeholder with different bytes
        modified = result[:offset] + b"\xff" * length + result[offset + length :]
        hash2 = compute_flac_hash(modified, offset, length)

        assert hash1 == hash2


class TestReplaceManifestInFlac:
    def test_replace_basic(self):
        flac = _make_minimal_flac()
        result, offset, length = create_flac_with_placeholder(flac, placeholder_size=256)

        manifest = b"C2PA_MANIFEST_DATA_HERE"
        final = replace_manifest_in_flac(result, manifest, offset, length)

        # Manifest data appears at offset
        assert final[offset : offset + len(manifest)] == manifest
        # Remaining placeholder is zero-padded
        assert final[offset + len(manifest) : offset + length] == b"\x00" * (length - len(manifest))

        # File outside exclusion is unchanged
        assert final[:offset] == result[:offset]
        assert final[offset + length :] == result[offset + length :]

    def test_replace_too_large_raises(self):
        flac = _make_minimal_flac()
        result, offset, length = create_flac_with_placeholder(flac, placeholder_size=64)

        with pytest.raises(ValueError, match="exceeds placeholder"):
            replace_manifest_in_flac(result, b"\xff" * 65, offset, length)

    def test_replace_exact_fit(self):
        flac = _make_minimal_flac()
        result, offset, length = create_flac_with_placeholder(flac, placeholder_size=100)

        manifest = b"\xab" * 100
        final = replace_manifest_in_flac(result, manifest, offset, length)
        assert final[offset : offset + length] == manifest


class TestRoundTrip:
    def test_hash_survives_replacement(self):
        """Hash computed on placeholder matches hash computed on replaced file
        (both exclude the manifest range)."""
        flac = _make_minimal_flac()
        result, offset, length = create_flac_with_placeholder(flac, placeholder_size=512)

        hash_before = compute_flac_hash(result, offset, length)

        manifest = b"SIGNED_MANIFEST_STORE_" * 20
        assert len(manifest) <= length

        final = replace_manifest_in_flac(result, manifest, offset, length)
        hash_after = compute_flac_hash(final, offset, length)

        assert hash_before == hash_after

    def test_result_is_valid_flac(self):
        """After embedding, the file still has valid FLAC structure."""
        flac = _make_minimal_flac()
        result, offset, length = create_flac_with_placeholder(flac, placeholder_size=128)

        manifest = b"TEST" * 10
        final = replace_manifest_in_flac(result, manifest, offset, length)

        assert final[:4] == FLAC_MAGIC
        blocks = _parse_metadata_blocks(final)
        assert len(blocks) >= 2
        assert blocks[0]["type"] == 0  # STREAMINFO
        # Last block has is_last set
        assert blocks[-1]["is_last"] is True

    def test_fixture_file(self):
        """Test with the actual conformance fixture."""
        import os

        fixture = os.path.join(
            os.path.dirname(__file__),
            "..",
            "c2pa_conformance",
            "fixtures",
            "test.flac",
        )
        if not os.path.exists(fixture):
            pytest.skip("test.flac fixture not found")

        flac_bytes = open(fixture, "rb").read()
        assert flac_bytes[:4] == FLAC_MAGIC

        result, offset, length = create_flac_with_placeholder(flac_bytes, placeholder_size=256)
        assert result[:4] == FLAC_MAGIC

        blocks = _parse_metadata_blocks(result)
        assert len(blocks) >= 2

        hash1 = compute_flac_hash(result, offset, length)
        manifest = b"FIXTURE_TEST" * 15
        final = replace_manifest_in_flac(result, manifest, offset, length)
        hash2 = compute_flac_hash(final, offset, length)
        assert hash1 == hash2
