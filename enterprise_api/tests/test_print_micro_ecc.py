"""Tests for Print-Survivable Micro ECC Embedding.

TEAM_297 - enterprise_api/app/utils/print_micro_ecc.py

Tests:
  1. Perfect digital roundtrip (encode -> decode)
  2. Payload construction and determinism
  3. RS error recovery (inject symbol errors)
  4. RS erasure recovery (known-position erasures)
  5. Short text graceful no-op
  6. Interleaving distribution verification
  7. Base-4 symbol encoding correctness
  8. HMAC verification
  9. Various document lengths
"""

from __future__ import annotations

import os
import random

import pytest

os.environ.setdefault("KEY_ENCRYPTION_KEY", "0" * 64)
os.environ.setdefault("ENCRYPTION_NONCE", "0" * 24)

from app.utils.print_micro_ecc import (
    CHAR_TO_SYMBOL,
    DATA_BYTES,
    HAIR_SPACE,
    HMAC_BYTES,
    LOG_ID_BYTES,
    MIN_POSITIONS,
    PAYLOAD_BYTES,
    REGULAR_SPACE,
    SIX_PER_EM_SPACE,
    SPACE_CHAR_SET,
    SYMBOL_CHARS,
    SYMBOLS_PER_BYTE,
    THIN_SPACE,
    _bytes_to_symbols,
    _select_positions,
    _symbols_to_bytes,
    build_document_payload,
    build_payload,
    decode_print_micro_ecc,
    decode_with_erasures,
    encode_print_micro_ecc,
    extract_hmac,
    extract_log_id,
    verify_hmac,
)


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------


def _long_text(word_count: int = 200) -> str:
    """Return plain text with enough words for the encoding."""
    words = [f"word{i}" for i in range(word_count)]
    return " ".join(words)


def _sample_log_id() -> bytes:
    return bytes(range(16))


def _sample_signing_key() -> bytes:
    return b"k" * 32


# --------------------------------------------------------------------------
# 1. Perfect digital roundtrip
# --------------------------------------------------------------------------


class TestDigitalRoundtrip:
    def test_encode_decode_roundtrip(self) -> None:
        """Payload survives encode -> decode with no errors."""
        text = _long_text(200)
        payload = build_payload(_sample_log_id(), _sample_signing_key())
        assert len(payload) == PAYLOAD_BYTES

        encoded = encode_print_micro_ecc(text, payload)
        decoded = decode_print_micro_ecc(encoded)

        assert decoded is not None, "decode returned None - encoding not detected"
        assert len(decoded) == DATA_BYTES
        # The decoded 32 bytes should match the first 32 bytes of the 40-byte payload
        assert decoded == payload[:DATA_BYTES]

    def test_roundtrip_various_payloads(self) -> None:
        """Roundtrip works for different log_id values."""
        text = _long_text(300)
        for i in range(5):
            log_id = os.urandom(16)
            payload = build_payload(log_id, _sample_signing_key())
            encoded = encode_print_micro_ecc(text, payload)
            decoded = decode_print_micro_ecc(encoded)
            assert decoded is not None
            assert decoded == payload[:DATA_BYTES]

    def test_roundtrip_with_content_binding(self) -> None:
        """Roundtrip preserves content-bound HMAC."""
        text = _long_text(200)
        sentence = "The quick brown fox jumps over the lazy dog."
        log_id = _sample_log_id()
        signing_key = _sample_signing_key()

        payload = build_payload(log_id, signing_key, sentence_text=sentence)
        encoded = encode_print_micro_ecc(text, payload)
        decoded = decode_print_micro_ecc(encoded)

        assert decoded is not None
        assert verify_hmac(decoded, signing_key, sentence_text=sentence)

    def test_roundtrip_exact_minimum_words(self) -> None:
        """Roundtrip works with exactly the minimum word count."""
        # 192 positions need 193 words (192 inter-word gaps)
        text = _long_text(193)
        payload = build_payload(_sample_log_id(), _sample_signing_key())
        encoded = encode_print_micro_ecc(text, payload)
        decoded = decode_print_micro_ecc(encoded)
        assert decoded is not None
        assert decoded == payload[:DATA_BYTES]

    def test_roundtrip_large_document(self) -> None:
        """Roundtrip works with a large document (1000 words)."""
        text = _long_text(1000)
        payload = build_payload(_sample_log_id(), _sample_signing_key())
        encoded = encode_print_micro_ecc(text, payload)
        decoded = decode_print_micro_ecc(encoded)
        assert decoded is not None
        assert decoded == payload[:DATA_BYTES]


# --------------------------------------------------------------------------
# 2. Payload construction
# --------------------------------------------------------------------------


class TestPayloadConstruction:
    def test_payload_size(self) -> None:
        """build_payload returns exactly 40 bytes."""
        payload = build_payload(_sample_log_id(), _sample_signing_key())
        assert len(payload) == PAYLOAD_BYTES  # 40

    def test_payload_contains_log_id(self) -> None:
        """First 16 bytes of data contain the log_id."""
        log_id = _sample_log_id()
        payload = build_payload(log_id, _sample_signing_key())
        # RS decode to get data portion
        from reedsolo import RSCodec

        rs = RSCodec(8)
        data = bytes(rs.decode(payload)[0])
        assert data[:LOG_ID_BYTES] == log_id

    def test_payload_deterministic(self) -> None:
        """Same inputs produce the same payload."""
        log_id = _sample_log_id()
        key = _sample_signing_key()
        p1 = build_payload(log_id, key)
        p2 = build_payload(log_id, key)
        assert p1 == p2

    def test_different_log_ids_different_payloads(self) -> None:
        """Different log_ids produce different payloads."""
        key = _sample_signing_key()
        p1 = build_payload(os.urandom(16), key)
        p2 = build_payload(os.urandom(16), key)
        assert p1 != p2

    def test_document_payload_deterministic(self) -> None:
        """build_document_payload is deterministic."""
        p1 = build_document_payload("org-abc", "doc-xyz")
        p2 = build_document_payload("org-abc", "doc-xyz")
        assert p1 == p2
        assert len(p1) == PAYLOAD_BYTES

    def test_document_payload_different_inputs(self) -> None:
        """Different org/doc produce different payloads."""
        p1 = build_document_payload("org-1", "doc-1")
        p2 = build_document_payload("org-2", "doc-1")
        p3 = build_document_payload("org-1", "doc-2")
        assert p1 != p2
        assert p1 != p3


# --------------------------------------------------------------------------
# 3. RS error recovery
# --------------------------------------------------------------------------


class TestRSErrorRecovery:
    def _inject_symbol_errors(self, text: str, num_errors: int, seed: int = 42) -> str:
        """Replace some encoded space characters with different space chars."""
        rng = random.Random(seed)
        chars = list(text)
        space_positions = [i for i, c in enumerate(chars) if c in SPACE_CHAR_SET]

        # Select interleaved positions (same as encoder)
        selected = _select_positions(len(space_positions), MIN_POSITIONS)
        encode_indices = [space_positions[s] for s in selected]

        # Pick random positions to corrupt
        error_positions = rng.sample(range(len(encode_indices)), num_errors)
        for ep in error_positions:
            char_idx = encode_indices[ep]
            current_sym = CHAR_TO_SYMBOL[chars[char_idx]]
            # Replace with a different symbol
            new_sym = (current_sym + rng.randint(1, 3)) % 4
            chars[char_idx] = SYMBOL_CHARS[new_sym]

        return "".join(chars)

    def test_recover_from_1_error(self) -> None:
        """RS corrects 1 symbol error."""
        text = _long_text(200)
        payload = build_payload(_sample_log_id(), _sample_signing_key())
        encoded = encode_print_micro_ecc(text, payload)
        corrupted = self._inject_symbol_errors(encoded, 1)
        decoded = decode_print_micro_ecc(corrupted)
        assert decoded is not None
        assert decoded == payload[:DATA_BYTES]

    def test_recover_from_8_errors(self) -> None:
        """RS(48,32) corrects up to 8 unknown byte errors."""
        text = _long_text(250)
        payload = build_payload(_sample_log_id(), _sample_signing_key())
        encoded = encode_print_micro_ecc(text, payload)

        # RS(48,32) over GF(256) corrects up to 8 unknown byte errors.
        # Inject 8 symbol errors spread across different bytes:
        corrupted = self._inject_symbol_errors(encoded, 8, seed=99)
        decoded = decode_print_micro_ecc(corrupted)
        assert decoded is not None
        assert decoded == payload[:DATA_BYTES]

    def test_fail_on_too_many_errors(self) -> None:
        """RS fails when more than 8 byte-level errors are present."""
        text = _long_text(250)
        payload = build_payload(_sample_log_id(), _sample_signing_key())
        encoded = encode_print_micro_ecc(text, payload)

        # Inject errors spread across many different bytes
        # With 30 symbol errors spread across ~30 bytes, RS cannot recover
        corrupted = self._inject_symbol_errors(encoded, 30, seed=123)
        decoded = decode_print_micro_ecc(corrupted)
        assert decoded is None


# --------------------------------------------------------------------------
# 4. RS erasure recovery
# --------------------------------------------------------------------------


class TestRSErasureRecovery:
    def test_recover_from_16_erasures(self) -> None:
        """RS(48,32) corrects up to 16 known-position erasures."""
        text = _long_text(250)
        payload = build_payload(_sample_log_id(), _sample_signing_key())
        encoded = encode_print_micro_ecc(text, payload)

        # Corrupt 16 symbol positions (4 full bytes) and mark as erasures
        chars = list(encoded)
        space_positions = [i for i, c in enumerate(chars) if c in SPACE_CHAR_SET]
        selected = _select_positions(len(space_positions), MIN_POSITIONS)
        encode_indices = [space_positions[s] for s in selected]

        # Corrupt symbols at byte-aligned positions, each in a different byte
        erasure_symbols = [i * 4 for i in range(16)]  # 16 symbols, each in different byte
        for sym_idx in erasure_symbols:
            char_idx = encode_indices[sym_idx]
            chars[char_idx] = REGULAR_SPACE  # overwrite with regular space

        corrupted = "".join(chars)
        decoded = decode_with_erasures(corrupted, erasure_indices=erasure_symbols)
        assert decoded is not None
        assert decoded == payload[:DATA_BYTES]


# --------------------------------------------------------------------------
# 5. Short text graceful no-op
# --------------------------------------------------------------------------


class TestShortText:
    def test_short_text_returns_unmodified(self) -> None:
        """Text too short for payload returns unmodified."""
        short_text = "This text is too short for print micro ECC."
        payload = build_payload(_sample_log_id(), _sample_signing_key())
        result = encode_print_micro_ecc(short_text, payload)
        assert result == short_text

    def test_short_text_decode_returns_none(self) -> None:
        """Decoding short text returns None."""
        short_text = "This text is too short."
        result = decode_print_micro_ecc(short_text)
        assert result is None

    def test_191_spaces_returns_unmodified(self) -> None:
        """Text with exactly 191 spaces (one short of minimum) returns unmodified."""
        text = " ".join(["word"] * 192)  # 191 spaces
        assert text.count(REGULAR_SPACE) == 191
        payload = build_payload(_sample_log_id(), _sample_signing_key())
        result = encode_print_micro_ecc(text, payload)
        assert result == text


# --------------------------------------------------------------------------
# 6. Interleaving distribution
# --------------------------------------------------------------------------


class TestInterleaving:
    def test_positions_evenly_distributed(self) -> None:
        """Selected positions are evenly spread across available spaces."""
        positions = _select_positions(300, 192)
        assert len(positions) == 192

        # Check monotonically increasing
        for i in range(1, len(positions)):
            assert positions[i] > positions[i - 1]

        # Check spread: first position near start, last near end
        assert positions[0] == 0
        assert positions[-1] >= 295  # close to 300

        # Check roughly even gaps
        gaps = [positions[i + 1] - positions[i] for i in range(len(positions) - 1)]
        avg_gap = sum(gaps) / len(gaps)
        assert 1.0 <= avg_gap <= 3.0  # 300/192 ~= 1.5625

    def test_minimum_positions_returns_identity(self) -> None:
        """When total == needed, every position is selected."""
        positions = _select_positions(192, 192)
        assert positions == list(range(192))

    def test_insufficient_positions_returns_empty(self) -> None:
        """When total < needed, returns empty list."""
        positions = _select_positions(100, 192)
        assert positions == []


# --------------------------------------------------------------------------
# 7. Base-4 symbol encoding correctness
# --------------------------------------------------------------------------


class TestBase4Encoding:
    def test_bytes_to_symbols_roundtrip(self) -> None:
        """bytes -> symbols -> bytes roundtrip."""
        data = os.urandom(48)
        symbols = _bytes_to_symbols(data)
        assert len(symbols) == 192  # 48 * 4
        recovered = _symbols_to_bytes(symbols)
        assert recovered == data

    def test_known_byte_encoding(self) -> None:
        """Verify bit extraction for a known byte value."""
        # 0xA5 = 0b10100101 -> symbols: 10, 10, 01, 01 = [2, 2, 1, 1]
        symbols = _bytes_to_symbols(bytes([0xA5]))
        assert symbols == [2, 2, 1, 1]

    def test_zero_byte(self) -> None:
        """0x00 -> [0, 0, 0, 0]."""
        symbols = _bytes_to_symbols(bytes([0x00]))
        assert symbols == [0, 0, 0, 0]

    def test_ff_byte(self) -> None:
        """0xFF -> [3, 3, 3, 3]."""
        symbols = _bytes_to_symbols(bytes([0xFF]))
        assert symbols == [3, 3, 3, 3]

    def test_all_symbols_in_range(self) -> None:
        """All symbols are 0-3."""
        data = os.urandom(40)
        symbols = _bytes_to_symbols(data)
        for s in symbols:
            assert 0 <= s <= 3


# --------------------------------------------------------------------------
# 8. HMAC verification
# --------------------------------------------------------------------------


class TestHMACVerification:
    def test_verify_hmac_success(self) -> None:
        """verify_hmac returns True for correct key."""
        log_id = _sample_log_id()
        key = _sample_signing_key()
        payload = build_payload(log_id, key)

        from reedsolo import RSCodec

        rs = RSCodec(8)
        data = bytes(rs.decode(payload)[0])
        assert verify_hmac(data, key)

    def test_verify_hmac_wrong_key(self) -> None:
        """verify_hmac returns False for wrong key."""
        log_id = _sample_log_id()
        key = _sample_signing_key()
        payload = build_payload(log_id, key)

        from reedsolo import RSCodec

        rs = RSCodec(8)
        data = bytes(rs.decode(payload)[0])
        assert not verify_hmac(data, b"x" * 32)

    def test_verify_hmac_content_bound(self) -> None:
        """Content-bound HMAC verifies with correct sentence."""
        log_id = _sample_log_id()
        key = _sample_signing_key()
        sentence = "Test sentence for binding."
        payload = build_payload(log_id, key, sentence_text=sentence)

        from reedsolo import RSCodec

        rs = RSCodec(8)
        data = bytes(rs.decode(payload)[0])
        assert verify_hmac(data, key, sentence_text=sentence)
        # Wrong sentence fails
        assert not verify_hmac(data, key, sentence_text="Wrong sentence.")

    def test_extract_log_id_and_hmac(self) -> None:
        """extract_log_id and extract_hmac return correct slices."""
        log_id = _sample_log_id()
        key = _sample_signing_key()
        payload = build_payload(log_id, key)

        from reedsolo import RSCodec

        rs = RSCodec(8)
        data = bytes(rs.decode(payload)[0])

        assert extract_log_id(data) == log_id
        assert len(extract_hmac(data)) == HMAC_BYTES


# --------------------------------------------------------------------------
# 9. No false positives on plain text
# --------------------------------------------------------------------------


class TestFalsePositives:
    def test_plain_text_no_false_positive(self) -> None:
        """Plain text with only regular spaces -> decode returns None."""
        text = _long_text(300)
        assert THIN_SPACE not in text
        assert HAIR_SPACE not in text
        assert SIX_PER_EM_SPACE not in text
        result = decode_print_micro_ecc(text)
        assert result is None

    def test_text_with_random_thin_spaces_no_valid_decode(self) -> None:
        """Random thin spaces should not produce a valid RS decode."""
        text = _long_text(300)
        chars = list(text)
        # Randomly replace some spaces with thin spaces
        rng = random.Random(42)
        space_positions = [i for i, c in enumerate(chars) if c == REGULAR_SPACE]
        for pos in rng.sample(space_positions, 50):
            chars[pos] = THIN_SPACE
        mangled = "".join(chars)
        # RS should reject this as corrupted (overwhelming number of errors)
        result = decode_print_micro_ecc(mangled)
        assert result is None
