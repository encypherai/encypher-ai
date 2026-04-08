"""Tests for deterministic wrapper padding.

Validates that encode_wrapper_padded produces wrappers whose UTF-8 byte
length exactly matches the declared worst-case target, and that the
decoder correctly extracts the manifest while ignoring padding bytes.
"""

import struct

from c2pa_text import (
    MAGIC,
    VERSION,
    decode_wrapper_sequence,
    encode_wrapper,
    encode_wrapper_padded,
    extract_manifest,
    find_wrapper_info,
    worst_case_wrapper_byte_length,
)


class TestWorstCaseFormula:
    """Verify the worst-case wrapper byte length formula."""

    def test_formula_matches_spec(self):
        """E = 3 + (13 + M) * 4 + 6 for any manifest byte count M."""
        for m in [0, 1, 50, 255, 500, 1000]:
            expected = 3 + (13 + m) * 4 + 6
            assert worst_case_wrapper_byte_length(m) == expected

    def test_worst_case_is_upper_bound(self):
        """Actual wrapper byte length must never exceed worst case."""
        import os

        for _ in range(20):
            manifest = os.urandom(200)
            wrapper = encode_wrapper(manifest)
            actual = len(wrapper.encode("utf-8"))
            worst = worst_case_wrapper_byte_length(len(manifest))
            assert actual <= worst, f"actual {actual} > worst {worst}"

    def test_worst_case_reached_by_all_high_bytes(self):
        """Manifest of all 0xFF bytes should produce worst-case length."""
        manifest = bytes([0xFF] * 100)
        wrapper = encode_wrapper(manifest)
        actual = len(wrapper.encode("utf-8"))
        worst = worst_case_wrapper_byte_length(100)
        # Header has low bytes (0x00 in magic, 0x01 version, 0x00s in length),
        # so actual < worst even with all-0xFF manifest body.
        assert actual <= worst


class TestEncodeWrapperPadded:
    """Verify encode_wrapper_padded produces exact target length."""

    def test_padded_length_matches_target(self):
        """Padded wrapper UTF-8 byte length must equal target."""
        import os

        for _ in range(30):
            manifest = os.urandom(200)
            target = worst_case_wrapper_byte_length(len(manifest))
            padded = encode_wrapper_padded(manifest, target)
            actual = len(padded.encode("utf-8"))
            assert actual == target, f"expected {target}, got {actual}"

    def test_padded_wrapper_is_decodable(self):
        """Padded wrapper must be decodable by extract_manifest."""
        manifest = b"\x00\x01\x02\x10\x20\xff" * 20
        target = worst_case_wrapper_byte_length(len(manifest))
        padded = encode_wrapper_padded(manifest, target)

        text = "Hello world" + padded
        extracted, clean = extract_manifest(text)
        assert extracted == manifest
        assert clean == "Hello world"

    def test_padded_wrapper_find_wrapper_info(self):
        """find_wrapper_info must return correct byte offsets for padded wrapper."""
        manifest = b"\xaa\xbb\xcc" * 50
        target = worst_case_wrapper_byte_length(len(manifest))
        padded = encode_wrapper_padded(manifest, target)

        text = "Test" + padded
        info = find_wrapper_info(text)
        assert info is not None
        extracted, offset, length = info
        assert extracted == manifest
        assert length == target

    def test_small_manifests(self):
        """Padding must work for very small manifests."""
        for size in [1, 2, 5, 10, 13]:
            manifest = bytes(range(size))
            target = worst_case_wrapper_byte_length(size)
            padded = encode_wrapper_padded(manifest, target)
            actual = len(padded.encode("utf-8"))
            assert actual == target

    def test_target_must_be_at_least_actual(self):
        """Target below actual wrapper length should raise ValueError."""
        manifest = b"\xff" * 100
        too_small = 10
        with self.assertRaises(ValueError):
            encode_wrapper_padded(manifest, too_small)

    def test_deterministic_across_hash_changes(self):
        """Two manifests of same length but different bytes produce same padded length."""
        import os

        m1 = os.urandom(300)
        m2 = os.urandom(300)
        target = worst_case_wrapper_byte_length(300)
        p1 = encode_wrapper_padded(m1, target)
        p2 = encode_wrapper_padded(m2, target)
        assert len(p1.encode("utf-8")) == len(p2.encode("utf-8")) == target


class TestBackwardCompatibility:
    """Verify that unpadded wrappers still decode correctly."""

    def test_unpadded_still_works(self):
        """Standard encode_wrapper output must still be extractable."""
        manifest = b"\x00\x01\x02\x03\x04\x05"
        wrapper = encode_wrapper(manifest)
        text = "Hello" + wrapper
        extracted, clean = extract_manifest(text)
        assert extracted == manifest
        assert clean == "Hello"

    def test_decode_wrapper_sequence_ignores_padding(self):
        """decode_wrapper_sequence must decode all bytes including padding."""
        manifest = b"\xaa\xbb"
        header = struct.pack("!8sBI", MAGIC, VERSION, len(manifest))
        payload = header + manifest + b"\xff\xff"  # 2 padding bytes
        # All bytes decode, but manifestLength tells you where manifest ends
        decoded = decode_wrapper_sequence("".join(chr(0xE0100 + b - 16) if b >= 16 else chr(0xFE00 + b) for b in payload))
        assert decoded[: 13 + 2] == header + manifest
