# TEAM_156: Tests for ZW embedding detection and UUID extraction.
"""Unit tests for app.utils.zw_detect module."""

from __future__ import annotations

from uuid import UUID, uuid4

from app.utils.zw_detect import (
    ZWNJ,
    ZWJ,
    CGJ,
    MVS,
    extract_uuid_from_signature,
    find_zw_signatures,
)


# ---------------------------------------------------------------------------
# Helpers — replicate minimal encode logic for test fixtures
# ---------------------------------------------------------------------------

_CHARS = [ZWNJ, ZWJ, CGJ, MVS]


def _encode_byte(b: int) -> str:
    result = []
    v = b
    for _ in range(4):
        result.append(_CHARS[v % 4])
        v //= 4
    return "".join(result)


def _encode_bytes(data: bytes) -> str:
    return "".join(_encode_byte(b) for b in data)


def _make_zw_signature(sentence_uuid: UUID) -> str:
    """Build a 128-char ZW signature (UUID + fake HMAC)."""
    uuid_bytes = sentence_uuid.bytes  # 16 bytes
    fake_hmac = b"\xab" * 16  # 16 bytes
    return _encode_bytes(uuid_bytes + fake_hmac)


# ---------------------------------------------------------------------------
# find_zw_signatures
# ---------------------------------------------------------------------------


class TestFindZwSignatures:
    def test_no_signatures_in_plain_text(self):
        assert find_zw_signatures("Hello, world!") == []

    def test_single_signature(self):
        uid = uuid4()
        sig = _make_zw_signature(uid)
        text = f"Hello{sig} world"
        result = find_zw_signatures(text)
        assert len(result) == 1
        start, end, extracted = result[0]
        assert extracted == sig
        assert end - start == 128

    def test_multiple_signatures(self):
        uid1 = uuid4()
        uid2 = uuid4()
        sig1 = _make_zw_signature(uid1)
        sig2 = _make_zw_signature(uid2)
        text = f"First sentence.{sig1} Second sentence.{sig2}"
        result = find_zw_signatures(text)
        assert len(result) == 2

    def test_short_sequence_ignored(self):
        # 64 chars (< 128) should not be detected
        short = ZWNJ * 64
        assert find_zw_signatures(f"text{short}more") == []

    def test_exactly_128_chars(self):
        sig = ZWNJ * 128
        result = find_zw_signatures(sig)
        assert len(result) == 1

    def test_256_chars_yields_two_signatures(self):
        sig = ZWNJ * 256
        result = find_zw_signatures(sig)
        assert len(result) == 2


# ---------------------------------------------------------------------------
# extract_uuid_from_signature
# ---------------------------------------------------------------------------


class TestExtractUuidFromSignature:
    def test_round_trip(self):
        uid = uuid4()
        sig = _make_zw_signature(uid)
        extracted = extract_uuid_from_signature(sig)
        assert extracted == uid

    def test_wrong_length_returns_none(self):
        assert extract_uuid_from_signature("abc") is None

    def test_specific_uuid(self):
        uid = UUID("12345678-1234-5678-1234-567812345678")
        sig = _make_zw_signature(uid)
        extracted = extract_uuid_from_signature(sig)
        assert extracted == uid

    def test_all_zeros_uuid(self):
        uid = UUID(int=0)
        sig = _make_zw_signature(uid)
        extracted = extract_uuid_from_signature(sig)
        assert extracted == uid
