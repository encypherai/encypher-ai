"""Tests for vs256_rs_crypto -- RS-protected VS256 signatures."""

from __future__ import annotations

import random

import pytest

from app.utils.vs256_crypto import (
    BYTE_TO_VS,
    LOG_ID_BYTES,
    MAGIC_PREFIX,
    MAGIC_PREFIX_LEN,
    VS_CHAR_SET,
    VS_TO_BYTE,
    generate_log_id,
)
from app.utils.vs256_rs_crypto import (
    DATA_BYTES,
    HMAC_BYTES,
    SIGNATURE_CHARS,
    create_embedded_sentence,
    create_signed_marker,
    derive_signing_key_from_private_key,
    find_all_markers,
    recover_from_partial_extraction,
    verify_signed_marker,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def signing_key() -> bytes:
    return b"test_signing_key_32_bytes_long!!"


@pytest.fixture
def log_id() -> bytes:
    return generate_log_id()


@pytest.fixture
def test_keypair():
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    private_key = Ed25519PrivateKey.generate()
    return private_key, private_key.public_key()


# ---------------------------------------------------------------------------
# Basic creation and verification
# ---------------------------------------------------------------------------


class TestCreateAndVerify:
    def test_signature_length(self, signing_key, log_id):
        sig = create_signed_marker(log_id, signing_key)
        assert len(sig) == SIGNATURE_CHARS  # 44

    def test_starts_with_magic_prefix(self, signing_key, log_id):
        sig = create_signed_marker(log_id, signing_key)
        assert sig[:MAGIC_PREFIX_LEN] == MAGIC_PREFIX

    def test_all_chars_are_vs(self, signing_key, log_id):
        sig = create_signed_marker(log_id, signing_key)
        for ch in sig:
            assert ch in VS_CHAR_SET, f"Non-VS char: U+{ord(ch):04X}"

    def test_roundtrip_verify(self, signing_key, log_id):
        sig = create_signed_marker(log_id, signing_key)
        valid, extracted = verify_signed_marker(sig, signing_key)
        assert valid
        assert extracted == log_id

    def test_returns_bytes(self, signing_key, log_id):
        sig = create_signed_marker(log_id, signing_key)
        valid, extracted = verify_signed_marker(sig, signing_key)
        assert valid
        assert isinstance(extracted, bytes)
        assert len(extracted) == LOG_ID_BYTES

    def test_wrong_key_fails(self, signing_key, log_id):
        sig = create_signed_marker(log_id, signing_key)
        wrong_key = b"wrong_key_wrong_key_wrong_key_32"
        valid, _ = verify_signed_marker(sig, wrong_key)
        assert not valid

    def test_wrong_log_id_length_raises(self, signing_key):
        with pytest.raises(ValueError, match="log_id must be"):
            create_signed_marker(b"\x00" * 15, signing_key)

    def test_tampered_payload_detected(self, signing_key, log_id):
        sig = create_signed_marker(log_id, signing_key)
        chars = list(sig)
        # Corrupt 5 payload positions to exceed RS correction capacity (>4 errors)
        for offset in range(5):
            idx = MAGIC_PREFIX_LEN + offset
            b = VS_TO_BYTE[chars[idx]]
            chars[idx] = BYTE_TO_VS[(b + 1) % 256]
        valid, _ = verify_signed_marker("".join(chars), signing_key)
        assert not valid

    def test_short_signature_rejected(self, signing_key):
        valid, _ = verify_signed_marker("too short", signing_key)
        assert not valid

    def test_wrong_magic_rejected(self, signing_key, log_id):
        sig = create_signed_marker(log_id, signing_key)
        bad = BYTE_TO_VS[0] + sig[1:]
        valid, _ = verify_signed_marker(bad, signing_key)
        assert not valid

    def test_content_binding_correct_text(self, signing_key, log_id):
        sentence = "The central bank raised rates."
        sig = create_signed_marker(log_id, signing_key, sentence_text=sentence)
        valid, extracted = verify_signed_marker(sig, signing_key, sentence_text=sentence)
        assert valid
        assert extracted == log_id

    def test_content_binding_wrong_text_fails(self, signing_key, log_id):
        sentence = "The central bank raised rates."
        sig = create_signed_marker(log_id, signing_key, sentence_text=sentence)
        valid, _ = verify_signed_marker(sig, signing_key, sentence_text="The central bank cut rates.")
        assert not valid

    def test_content_binding_nfc_stable(self, signing_key, log_id):
        sig = create_signed_marker(log_id, signing_key, sentence_text="Cafe\u0301 prices increased.")
        valid, extracted = verify_signed_marker(sig, signing_key, sentence_text="Caf\u00e9 prices increased.")
        assert valid
        assert extracted == log_id

    def test_legacy_signature_verifies_without_sentence_text(self, signing_key, log_id):
        sig = create_signed_marker(log_id, signing_key)
        valid, extracted = verify_signed_marker(sig, signing_key)
        assert valid
        assert extracted == log_id


# ---------------------------------------------------------------------------
# Reed-Solomon error correction
# ---------------------------------------------------------------------------


class TestReedSolomonRecovery:
    def test_recovers_from_1_erasure(self, signing_key, log_id):
        sig = create_signed_marker(log_id, signing_key)
        chars = list(sig)
        erase_idx = 5
        chars[MAGIC_PREFIX_LEN + erase_idx] = BYTE_TO_VS[0]
        corrupted = "".join(chars)
        valid, extracted = verify_signed_marker(corrupted, signing_key, erase_positions=[erase_idx])
        assert valid
        assert extracted == log_id

    def test_recovers_from_4_erasures(self, signing_key, log_id):
        sig = create_signed_marker(log_id, signing_key)
        chars = list(sig)
        erase_positions = [0, 7, 15, 25]
        for pos in erase_positions:
            chars[MAGIC_PREFIX_LEN + pos] = BYTE_TO_VS[0]
        corrupted = "".join(chars)
        valid, extracted = verify_signed_marker(corrupted, signing_key, erase_positions=erase_positions)
        assert valid
        assert extracted == log_id

    def test_recovers_from_8_erasures(self, signing_key, log_id):
        """Maximum erasure capacity: 8 known positions."""
        sig = create_signed_marker(log_id, signing_key)
        chars = list(sig)
        erase_positions = [0, 3, 7, 11, 15, 19, 23, 27]
        for pos in erase_positions:
            chars[MAGIC_PREFIX_LEN + pos] = BYTE_TO_VS[0]
        corrupted = "".join(chars)
        valid, extracted = verify_signed_marker(corrupted, signing_key, erase_positions=erase_positions)
        assert valid
        assert extracted == log_id

    def test_fails_with_9_erasures(self, signing_key, log_id):
        """Beyond RS capacity: 9 erasures should fail."""
        sig = create_signed_marker(log_id, signing_key)
        chars = list(sig)
        erase_positions = [0, 3, 5, 7, 11, 15, 19, 23, 27]
        for pos in erase_positions:
            chars[MAGIC_PREFIX_LEN + pos] = BYTE_TO_VS[0]
        corrupted = "".join(chars)
        valid, _ = verify_signed_marker(corrupted, signing_key, erase_positions=erase_positions)
        assert not valid

    def test_corrects_up_to_4_unknown_errors(self, signing_key, log_id):
        """RS can correct up to 4 unknown errors (no erase_positions)."""
        sig = create_signed_marker(log_id, signing_key)
        chars = list(sig)
        for pos in [2, 10, 20, 30]:
            b = VS_TO_BYTE[chars[MAGIC_PREFIX_LEN + pos]]
            chars[MAGIC_PREFIX_LEN + pos] = BYTE_TO_VS[(b + 1) % 256]
        corrupted = "".join(chars)
        valid, extracted = verify_signed_marker(corrupted, signing_key)
        assert valid
        assert extracted == log_id


# ---------------------------------------------------------------------------
# Detection in text
# ---------------------------------------------------------------------------


class TestFindInText:
    def test_finds_single_signature(self, signing_key, log_id):
        sig = create_signed_marker(log_id, signing_key)
        text = f"Hello {sig}world."
        found = find_all_markers(text)
        assert len(found) == 1
        assert found[0][2] == sig

    def test_finds_multiple_signatures(self, signing_key):
        sigs = [create_signed_marker(generate_log_id(), signing_key) for _ in range(2)]
        text = f"First{sigs[0]} Second{sigs[1]} End"
        found = find_all_markers(text)
        assert len(found) == 2

    def test_no_false_positives_in_plain_text(self):
        assert find_all_markers("Hello World") == []


# ---------------------------------------------------------------------------
# Safe embedding
# ---------------------------------------------------------------------------


class TestSafeEmbedding:
    def test_embeds_before_punctuation(self, signing_key, log_id):
        result = create_embedded_sentence("Hello.", log_id, signing_key)
        assert result.endswith(".")
        assert len(result) == len("Hello.") + SIGNATURE_CHARS

    def test_roundtrip_with_safe_embedding(self, signing_key, log_id):
        sentence = "Test sentence."
        embedded = create_embedded_sentence(sentence, log_id, signing_key)
        found = find_all_markers(embedded)
        assert len(found) == 1
        # create_embedded_sentence binds to sentence_text; pass it for verification
        valid, extracted = verify_signed_marker(found[0][2], signing_key, sentence_text=sentence)
        assert valid
        assert extracted == log_id


# ---------------------------------------------------------------------------
# Partial extraction recovery
# ---------------------------------------------------------------------------


class TestPartialExtraction:
    def test_full_extraction_succeeds(self, signing_key, log_id):
        sig = create_signed_marker(log_id, signing_key)
        entries = [(i, ch) for i, ch in enumerate(sig)]
        ok, extracted, _ = recover_from_partial_extraction(entries)
        assert ok
        assert extracted == log_id

    def test_recovers_with_4_missing_payload_chars(self, signing_key, log_id):
        sig = create_signed_marker(log_id, signing_key)
        entries = [(i, ch) for i, ch in enumerate(sig)]
        for pos in [MAGIC_PREFIX_LEN + 5, MAGIC_PREFIX_LEN + 10, MAGIC_PREFIX_LEN + 20, MAGIC_PREFIX_LEN + 28]:
            entries[pos] = (pos, None)
        ok, extracted, _ = recover_from_partial_extraction(entries)
        assert ok
        assert extracted == log_id

    def test_fails_with_missing_magic(self, signing_key, log_id):
        sig = create_signed_marker(log_id, signing_key)
        entries = [(i, ch) for i, ch in enumerate(sig)]
        entries[0] = (0, None)
        ok, _, _ = recover_from_partial_extraction(entries)
        assert not ok

    def test_fails_with_too_many_missing(self, signing_key, log_id):
        sig = create_signed_marker(log_id, signing_key)
        entries = [(i, ch) for i, ch in enumerate(sig)]
        for i in range(9):
            pos = MAGIC_PREFIX_LEN + i * 3
            if pos < SIGNATURE_CHARS:
                entries[pos] = (pos, None)
        ok, _, _ = recover_from_partial_extraction(entries)
        assert not ok


# ---------------------------------------------------------------------------
# Key derivation
# ---------------------------------------------------------------------------


class TestKeyDerivation:
    def test_deterministic(self, test_keypair):
        private_key, _ = test_keypair
        k1 = derive_signing_key_from_private_key(private_key)
        k2 = derive_signing_key_from_private_key(private_key)
        assert k1 == k2
        assert len(k1) == 32

    def test_different_from_vs256_key(self, test_keypair):
        """RS key derivation uses different salt than plain vs256."""
        from app.utils.vs256_crypto import derive_signing_key_from_private_key as vs256_derive

        private_key, _ = test_keypair
        rs_key = derive_signing_key_from_private_key(private_key)
        plain_key = vs256_derive(private_key)
        assert rs_key != plain_key


# ---------------------------------------------------------------------------
# Poppler dedup simulation
# ---------------------------------------------------------------------------


class TestPopplerSimulation:
    def test_rs_recovers_from_typical_poppler_loss(self, signing_key):
        """Simulate poppler dedup on a contiguous 44-char block."""
        random.seed(42)
        successes = 0
        trials = 100

        for _ in range(trials):
            lid = generate_log_id()
            sig = create_signed_marker(lid, signing_key)

            seen_codepoints: set[str] = set()
            surviving_chars: list[tuple[int, str | None]] = []
            for i, ch in enumerate(sig):
                if i < MAGIC_PREFIX_LEN:
                    surviving_chars.append((i, ch))
                    seen_codepoints.add(ch)
                elif ch in seen_codepoints:
                    surviving_chars.append((i, None))
                else:
                    seen_codepoints.add(ch)
                    surviving_chars.append((i, ch))

            ok, extracted, _ = recover_from_partial_extraction(surviving_chars)
            if ok and extracted == lid:
                successes += 1

        assert successes >= 90, f"Expected >=90% recovery, got {successes}/{trials}"


# ---------------------------------------------------------------------------
# Size constants
# ---------------------------------------------------------------------------


def test_signature_chars_is_44():
    """44 = 4 magic + 40 payload (32 data + 8 RS parity)."""
    assert SIGNATURE_CHARS == 44


def test_data_bytes_is_32():
    """32 = 16-byte log_id + 16-byte HMAC."""
    assert DATA_BYTES == 32


def test_hmac_bytes_is_16():
    assert HMAC_BYTES == 16
