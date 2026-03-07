# TEAM_158 / TEAM_248: Tests for VS256 embedding detection utility.
"""Tests for vs256_detect — lightweight VS256 signature detection."""

from __future__ import annotations

from uuid import UUID

from reedsolo import RSCodec

from app.utils.vs256_detect import (
    ECC_SIGNATURE_CHARS,
    MAGIC_PREFIX,
    SIGNATURE_CHARS,
    _BYTE_TO_VS,
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


def _make_ecc_signature(log_id_bytes: bytes, hmac128_bytes: bytes) -> str:
    """Build a 44-char RS-protected VS256 ECC signature (RS(40,32)).

    Matches the format used by vs256_rs_crypto.create_signed_marker().
    """
    rs = RSCodec(8)
    data = log_id_bytes + hmac128_bytes  # 32 bytes
    encoded_bytes = bytes(rs.encode(data))  # 40 bytes
    encoded = "".join(_BYTE_TO_VS[b] for b in encoded_bytes)
    return MAGIC_PREFIX + encoded  # 44 chars total


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


# ---------------------------------------------------------------------------
# Tests for 44-char ECC format (vs256_rs_crypto -- current micro+ecc mode)
# ---------------------------------------------------------------------------

class TestECCSignatureDetection:
    """44-char ECC signatures (RS(8) over 40 bytes -> 32 data bytes)."""

    def test_find_ecc_signature(self):
        log_id = UUID("deadbeef-dead-beef-dead-beefdeadbeef").bytes
        sig = _make_ecc_signature(log_id, b"\xab" * 16)
        assert len(sig) == ECC_SIGNATURE_CHARS
        results = find_vs256_signatures(f"Hello {sig} World")
        assert len(results) == 1
        start, end, found = results[0]
        assert found == sig
        assert end - start == ECC_SIGNATURE_CHARS

    def test_ecc_preferred_over_legacy_on_same_magic(self):
        """When both 44 and 36 chars follow the magic prefix, 44-char wins."""
        log_id = UUID("12345678-1234-5678-1234-567812345678").bytes
        sig = _make_ecc_signature(log_id, b"\xcc" * 16)
        # The sig starts with MAGIC_PREFIX; we verify only 44-char is returned
        results = find_vs256_signatures(sig)
        assert len(results) == 1
        assert len(results[0][2]) == ECC_SIGNATURE_CHARS

    def test_extract_uuid_from_ecc_signature(self):
        log_id = UUID("abcdef01-2345-6789-abcd-ef0123456789")
        sig = _make_ecc_signature(log_id.bytes, b"\x99" * 16)
        extracted = extract_uuid_from_vs256_signature(sig)
        assert extracted == log_id

    def test_extract_uuid_from_ecc_roundtrip_with_find(self):
        log_id = UUID("cafebabe-cafe-babe-cafe-babecafebabe")
        sig = _make_ecc_signature(log_id.bytes, b"\x11" * 16)
        text = f"Sentence one.{sig} Sentence two."
        results = find_vs256_signatures(text)
        assert len(results) == 1
        extracted = extract_uuid_from_vs256_signature(results[0][2])
        assert extracted == log_id

    def test_mixed_36_and_44_char_sigs_in_same_text(self):
        """Text may contain both old (36-char) and new (44-char) signatures."""
        old_id = UUID("00000000-0000-0000-0000-000000000001")
        new_id = UUID("00000000-0000-0000-0000-000000000002")
        sig_old = _make_signature(old_id.bytes, b"\xaa" * 16)  # 36 chars
        sig_new = _make_ecc_signature(new_id.bytes, b"\xbb" * 16)  # 44 chars
        text = f"Para one.{sig_old} Para two.{sig_new} End."
        results = find_vs256_signatures(text)
        assert len(results) == 2
        lengths = {end - start for start, end, _ in results}
        assert lengths == {SIGNATURE_CHARS, ECC_SIGNATURE_CHARS}

    def test_uuid_to_log_id_hex_conversion(self):
        """UUID string (with dashes) from detection matches log_id hex (no dashes) in DB."""
        log_id_bytes = UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890").bytes
        sig = _make_ecc_signature(log_id_bytes, b"\x55" * 16)
        extracted_uuid = extract_uuid_from_vs256_signature(sig)
        assert extracted_uuid is not None
        # This is how the verify service builds the lookup key
        uuid_str = str(extracted_uuid)                     # "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        log_id_hex = uuid_str.replace("-", "")             # "a1b2c3d4e5f67890abcdef1234567890"
        # This must match what embedding_service stores as embedding_metadata["log_id"]
        assert log_id_hex == log_id_bytes.hex()

    def test_reassemble_ecc_signature_from_distributed(self):
        """ECC (44-char) signatures survive redistribution across visible chars."""
        log_id = UUID("fedcba09-8765-4321-fedc-ba0987654321")
        sig = _make_ecc_signature(log_id.bytes, b"\x77" * 16)
        assert len(sig) == ECC_SIGNATURE_CHARS
        # Interleave VS chars with visible ASCII
        visible = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghij"
        distributed: list[str] = []
        for i, ch in enumerate(sig):
            if i < len(visible):
                distributed.append(visible[i])
            distributed.append(ch)
        text = "".join(distributed)
        vs_chars = collect_distributed_vs_chars(text)
        reassembled = reassemble_signature_from_distributed(vs_chars)
        assert reassembled == sig
        extracted = extract_uuid_from_vs256_signature(reassembled)
        assert extracted == log_id
