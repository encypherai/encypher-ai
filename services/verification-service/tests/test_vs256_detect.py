# TEAM_158: Tests for VS256 embedding detection utility.
"""Tests for vs256_detect — lightweight VS256 signature detection."""

from __future__ import annotations

from uuid import UUID

import pytest
from reedsolo import RSCodec

from app.utils.vs256_detect import (
    MAGIC_PREFIX,
    MAGIC_PREFIX_LEN,
    SIGNATURE_CHARS,
    _BYTE_TO_VS,
    _VS_CHAR_SET,
    _VS_TO_BYTE,
    collect_distributed_vs_chars,
    extract_uuid_from_vs256_signature,
    find_vs256_signatures,
    reassemble_signature_from_distributed,
)


def _make_signature(uuid_bytes: bytes, hmac_bytes: bytes) -> str:
    """Build a 36-char VS256 signature from raw UUID + HMAC bytes."""
    payload = uuid_bytes + hmac_bytes
    encoded = "".join(_BYTE_TO_VS[b] for b in payload)
    return MAGIC_PREFIX + encoded


def _make_rs_signature(uuid_bytes: bytes, hmac64_bytes: bytes) -> str:
    """Build a 36-char RS-protected VS256 signature (RS(32,24))."""
    rs = RSCodec(8)
    data = uuid_bytes + hmac64_bytes  # 24 bytes
    encoded_bytes = bytes(rs.encode(data))  # 32 bytes
    encoded = "".join(_BYTE_TO_VS[b] for b in encoded_bytes)
    return MAGIC_PREFIX + encoded


class TestFindVS256Signatures:
    def test_no_signatures_in_plain_text(self):
        assert find_vs256_signatures("Hello World") == []

    def test_detects_single_signature(self):
        uuid_bytes = UUID("12345678-1234-5678-1234-567812345678").bytes
        hmac_bytes = b"\xaa" * 16
        sig = _make_signature(uuid_bytes, hmac_bytes)
        text = f"Hello {sig}World"
        results = find_vs256_signatures(text)
        assert len(results) == 1
        start, end, found_sig = results[0]
        assert found_sig == sig
        assert end - start == SIGNATURE_CHARS

    def test_detects_multiple_signatures(self):
        sig1 = _make_signature(b"\x01" * 16, b"\x02" * 16)
        sig2 = _make_signature(b"\x03" * 16, b"\x04" * 16)
        text = f"First{sig1} Second{sig2} End"
        results = find_vs256_signatures(text)
        assert len(results) == 2

    def test_ignores_partial_prefix(self):
        # Only 3 of 4 magic prefix chars — should not match
        partial = MAGIC_PREFIX[:3] + "X"
        assert find_vs256_signatures(partial) == []

    def test_detects_rs_signature(self):
        """RS-encoded signatures use same magic prefix and length."""
        target = UUID("abcdef01-2345-6789-abcd-ef0123456789")
        sig = _make_rs_signature(target.bytes, b"\xbb" * 8)
        results = find_vs256_signatures(f"text{sig}end")
        assert len(results) == 1
        assert results[0][2] == sig


class TestExtractUUID:
    def test_extracts_correct_uuid(self):
        target = UUID("abcdef01-2345-6789-abcd-ef0123456789")
        sig = _make_signature(target.bytes, b"\xff" * 16)
        extracted = extract_uuid_from_vs256_signature(sig)
        assert extracted == target

    def test_wrong_length_returns_none(self):
        assert extract_uuid_from_vs256_signature("too short") is None

    def test_roundtrip_with_find(self):
        target = UUID("deadbeef-dead-beef-dead-beefdeadbeef")
        sig = _make_signature(target.bytes, b"\x00" * 16)
        text = f"Some text {sig} more text"
        results = find_vs256_signatures(text)
        assert len(results) == 1
        extracted = extract_uuid_from_vs256_signature(results[0][2])
        assert extracted == target

    def test_extracts_uuid_from_rs_signature(self):
        """RS decode should recover the UUID from an RS-encoded signature."""
        target = UUID("12345678-abcd-ef01-2345-678901234567")
        sig = _make_rs_signature(target.bytes, b"\xcc" * 8)
        extracted = extract_uuid_from_vs256_signature(sig)
        assert extracted == target


class TestCollectDistributedVSChars:
    def test_collects_vs_chars_from_mixed_text(self):
        vs1 = _BYTE_TO_VS[10]
        vs2 = _BYTE_TO_VS[20]
        text = f"H{vs1}ello W{vs2}orld"
        collected = collect_distributed_vs_chars(text)
        assert collected == [vs1, vs2]

    def test_empty_text_returns_empty(self):
        assert collect_distributed_vs_chars("") == []

    def test_plain_text_returns_empty(self):
        assert collect_distributed_vs_chars("Hello World") == []

    def test_preserves_order(self):
        chars = [_BYTE_TO_VS[i] for i in range(5)]
        text = "A" + chars[0] + "B" + chars[1] + "C" + chars[2] + "D" + chars[3] + "E" + chars[4]
        collected = collect_distributed_vs_chars(text)
        assert collected == chars


class TestReassembleSignature:
    def test_reassembles_from_distributed(self):
        target = UUID("deadbeef-dead-beef-dead-beefdeadbeef")
        sig = _make_signature(target.bytes, b"\xaa" * 16)
        # Simulate redistribution: interleave VS chars with visible text
        distributed = []
        visible = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        for i, ch in enumerate(sig):
            if i < len(visible):
                distributed.append(visible[i])
            distributed.append(ch)
        text = "".join(distributed)
        vs_chars = collect_distributed_vs_chars(text)
        reassembled = reassemble_signature_from_distributed(vs_chars)
        assert reassembled == sig

    def test_returns_none_when_no_magic(self):
        vs_chars = [_BYTE_TO_VS[i] for i in range(10)]
        assert reassemble_signature_from_distributed(vs_chars) is None

    def test_returns_none_when_too_few_chars(self):
        assert reassemble_signature_from_distributed([]) is None

    def test_reassembles_rs_signature(self):
        target = UUID("12345678-abcd-ef01-2345-678901234567")
        sig = _make_rs_signature(target.bytes, b"\xdd" * 8)
        distributed = []
        visible = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        for i, ch in enumerate(sig):
            if i < len(visible):
                distributed.append(visible[i])
            distributed.append(ch)
        text = "".join(distributed)
        vs_chars = collect_distributed_vs_chars(text)
        reassembled = reassemble_signature_from_distributed(vs_chars)
        assert reassembled == sig
        extracted = extract_uuid_from_vs256_signature(reassembled)
        assert extracted == target
