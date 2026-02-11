# TEAM_158: Tests for VS256 + Reed-Solomon error-correcting embedding.
"""Tests for vs256_rs_crypto — RS-protected VS256 signatures."""

from __future__ import annotations

import random
from uuid import UUID, uuid4

import pytest
from app.utils.vs256_crypto import (
    BYTE_TO_VS,
    MAGIC_PREFIX,
    MAGIC_PREFIX_LEN,
    VS_CHAR_SET,
    VS_TO_BYTE,
)
from app.utils.vs256_rs_crypto import (
    DATA_BYTES,
    HMAC_BYTES,
    PAYLOAD_BYTES,
    SIGNATURE_CHARS,
    UUID_BYTES,
    create_minimal_signed_uuid,
    create_safely_embedded_sentence,
    derive_signing_key_from_private_key,
    find_all_minimal_signed_uuids,
    recover_from_partial_extraction,
    verify_minimal_signed_uuid,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def signing_key() -> bytes:
    return b"test_signing_key_32_bytes_long!!"


@pytest.fixture
def test_keypair():
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    return private_key, public_key


# ---------------------------------------------------------------------------
# Basic creation and verification
# ---------------------------------------------------------------------------


class TestCreateAndVerify:
    def test_signature_length(self, signing_key):
        sig = create_minimal_signed_uuid(uuid4(), signing_key)
        assert len(sig) == SIGNATURE_CHARS  # 36

    def test_starts_with_magic_prefix(self, signing_key):
        sig = create_minimal_signed_uuid(uuid4(), signing_key)
        assert sig[:MAGIC_PREFIX_LEN] == MAGIC_PREFIX

    def test_all_chars_are_vs(self, signing_key):
        sig = create_minimal_signed_uuid(uuid4(), signing_key)
        for ch in sig:
            assert ch in VS_CHAR_SET, f"Non-VS char: U+{ord(ch):04X}"

    def test_roundtrip_verify(self, signing_key):
        uid = uuid4()
        sig = create_minimal_signed_uuid(uid, signing_key)
        valid, extracted = verify_minimal_signed_uuid(sig, signing_key)
        assert valid
        assert extracted == uid

    def test_wrong_key_fails(self, signing_key):
        sig = create_minimal_signed_uuid(uuid4(), signing_key)
        wrong_key = b"wrong_key_wrong_key_wrong_key_32"
        valid, _ = verify_minimal_signed_uuid(sig, wrong_key)
        assert not valid

    def test_tampered_payload_detected(self, signing_key):
        sig = create_minimal_signed_uuid(uuid4(), signing_key)
        chars = list(sig)
        # Tamper with a UUID byte (position 4 = first UUID char after magic)
        target = MAGIC_PREFIX_LEN + 2
        original_byte = VS_TO_BYTE[chars[target]]
        chars[target] = BYTE_TO_VS[(original_byte + 1) % 256]
        tampered = "".join(chars)
        # RS may correct 1 error, but HMAC should still fail if >4 errors
        # With 1 error, RS corrects it and HMAC passes — this is expected!
        # Let's tamper with 5 positions to exceed RS correction capacity
        for offset in range(5):
            idx = MAGIC_PREFIX_LEN + offset
            b = VS_TO_BYTE[chars[idx]]
            chars[idx] = BYTE_TO_VS[(b + 1) % 256]
        tampered = "".join(chars)
        valid, _ = verify_minimal_signed_uuid(tampered, signing_key)
        assert not valid

    def test_short_signature_rejected(self, signing_key):
        valid, _ = verify_minimal_signed_uuid("too short", signing_key)
        assert not valid

    def test_wrong_magic_rejected(self, signing_key):
        sig = create_minimal_signed_uuid(uuid4(), signing_key)
        # Replace first magic char
        bad = BYTE_TO_VS[0] + sig[1:]
        valid, _ = verify_minimal_signed_uuid(bad, signing_key)
        assert not valid


# ---------------------------------------------------------------------------
# Reed-Solomon error correction
# ---------------------------------------------------------------------------


class TestReedSolomonRecovery:
    def test_recovers_from_1_erasure(self, signing_key):
        uid = uuid4()
        sig = create_minimal_signed_uuid(uid, signing_key)
        chars = list(sig)
        # Erase 1 payload position
        erase_idx = 5  # within payload (after magic)
        chars[MAGIC_PREFIX_LEN + erase_idx] = BYTE_TO_VS[0]  # corrupt
        corrupted = "".join(chars)
        valid, extracted = verify_minimal_signed_uuid(
            corrupted, signing_key, erase_positions=[erase_idx]
        )
        assert valid
        assert extracted == uid

    def test_recovers_from_4_erasures(self, signing_key):
        uid = uuid4()
        sig = create_minimal_signed_uuid(uid, signing_key)
        chars = list(sig)
        erase_positions = [0, 7, 15, 25]
        for pos in erase_positions:
            chars[MAGIC_PREFIX_LEN + pos] = BYTE_TO_VS[0]
        corrupted = "".join(chars)
        valid, extracted = verify_minimal_signed_uuid(
            corrupted, signing_key, erase_positions=erase_positions
        )
        assert valid
        assert extracted == uid

    def test_recovers_from_8_erasures(self, signing_key):
        """Maximum erasure capacity: 8 known positions."""
        uid = uuid4()
        sig = create_minimal_signed_uuid(uid, signing_key)
        chars = list(sig)
        erase_positions = [0, 3, 7, 11, 15, 19, 23, 27]
        for pos in erase_positions:
            chars[MAGIC_PREFIX_LEN + pos] = BYTE_TO_VS[0]
        corrupted = "".join(chars)
        valid, extracted = verify_minimal_signed_uuid(
            corrupted, signing_key, erase_positions=erase_positions
        )
        assert valid
        assert extracted == uid

    def test_fails_with_9_erasures(self, signing_key):
        """Beyond RS capacity: 9 erasures should fail."""
        uid = uuid4()
        sig = create_minimal_signed_uuid(uid, signing_key)
        chars = list(sig)
        erase_positions = [0, 3, 5, 7, 11, 15, 19, 23, 27]
        for pos in erase_positions:
            chars[MAGIC_PREFIX_LEN + pos] = BYTE_TO_VS[0]
        corrupted = "".join(chars)
        valid, _ = verify_minimal_signed_uuid(
            corrupted, signing_key, erase_positions=erase_positions
        )
        assert not valid

    def test_corrects_up_to_4_unknown_errors(self, signing_key):
        """RS can correct up to 4 unknown errors (no erase_positions)."""
        uid = uuid4()
        sig = create_minimal_signed_uuid(uid, signing_key)
        chars = list(sig)
        # Corrupt 4 payload positions without telling the decoder where
        for pos in [2, 10, 20, 30]:
            b = VS_TO_BYTE[chars[MAGIC_PREFIX_LEN + pos]]
            chars[MAGIC_PREFIX_LEN + pos] = BYTE_TO_VS[(b + 1) % 256]
        corrupted = "".join(chars)
        valid, extracted = verify_minimal_signed_uuid(corrupted, signing_key)
        assert valid
        assert extracted == uid


# ---------------------------------------------------------------------------
# Detection in text
# ---------------------------------------------------------------------------


class TestFindInText:
    def test_finds_single_signature(self, signing_key):
        sig = create_minimal_signed_uuid(uuid4(), signing_key)
        text = f"Hello {sig}world."
        found = find_all_minimal_signed_uuids(text)
        assert len(found) == 1
        assert found[0][2] == sig

    def test_finds_multiple_signatures(self, signing_key):
        sig1 = create_minimal_signed_uuid(uuid4(), signing_key)
        sig2 = create_minimal_signed_uuid(uuid4(), signing_key)
        text = f"First{sig1} Second{sig2} End"
        found = find_all_minimal_signed_uuids(text)
        assert len(found) == 2

    def test_no_false_positives_in_plain_text(self):
        assert find_all_minimal_signed_uuids("Hello World") == []


# ---------------------------------------------------------------------------
# Safe embedding
# ---------------------------------------------------------------------------


class TestSafeEmbedding:
    def test_embeds_before_punctuation(self, signing_key):
        uid = uuid4()
        result = create_safely_embedded_sentence("Hello.", uid, signing_key)
        assert result.endswith(".")
        assert len(result) == len("Hello.") + SIGNATURE_CHARS

    def test_roundtrip_with_safe_embedding(self, signing_key):
        uid = uuid4()
        embedded = create_safely_embedded_sentence("Test sentence.", uid, signing_key)
        found = find_all_minimal_signed_uuids(embedded)
        assert len(found) == 1
        valid, extracted = verify_minimal_signed_uuid(found[0][2], signing_key)
        assert valid
        assert extracted == uid


# ---------------------------------------------------------------------------
# Partial extraction recovery
# ---------------------------------------------------------------------------


class TestPartialExtraction:
    def test_full_extraction_succeeds(self, signing_key):
        uid = uuid4()
        sig = create_minimal_signed_uuid(uid, signing_key)
        entries = [(i, ch) for i, ch in enumerate(sig)]
        ok, extracted, _ = recover_from_partial_extraction(entries)
        assert ok
        assert extracted == uid

    def test_recovers_with_4_missing_payload_chars(self, signing_key):
        uid = uuid4()
        sig = create_minimal_signed_uuid(uid, signing_key)
        entries = [(i, ch) for i, ch in enumerate(sig)]
        # Remove 4 payload chars
        for pos in [MAGIC_PREFIX_LEN + 5, MAGIC_PREFIX_LEN + 10,
                     MAGIC_PREFIX_LEN + 20, MAGIC_PREFIX_LEN + 28]:
            entries[pos] = (pos, None)
        ok, extracted, _ = recover_from_partial_extraction(entries)
        assert ok
        assert extracted == uid

    def test_fails_with_missing_magic(self, signing_key):
        sig = create_minimal_signed_uuid(uuid4(), signing_key)
        entries = [(i, ch) for i, ch in enumerate(sig)]
        entries[0] = (0, None)  # missing magic char
        ok, _, _ = recover_from_partial_extraction(entries)
        assert not ok

    def test_fails_with_too_many_missing(self, signing_key):
        sig = create_minimal_signed_uuid(uuid4(), signing_key)
        entries = [(i, ch) for i, ch in enumerate(sig)]
        # Remove 9 payload chars (exceeds RS capacity)
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
        from app.utils.vs256_crypto import (
            derive_signing_key_from_private_key as vs256_derive,
        )
        private_key, _ = test_keypair
        rs_key = derive_signing_key_from_private_key(private_key)
        plain_key = vs256_derive(private_key)
        assert rs_key != plain_key


# ---------------------------------------------------------------------------
# Poppler dedup simulation
# ---------------------------------------------------------------------------


class TestPopplerSimulation:
    def test_rs_recovers_from_typical_poppler_loss(self, signing_key):
        """Simulate poppler dedup on a contiguous 36-char block and verify
        RS can recover the signature."""
        random.seed(42)
        successes = 0
        trials = 100

        for _ in range(trials):
            uid = uuid4()
            sig = create_minimal_signed_uuid(uid, signing_key)

            # Simulate poppler: dedup VS codepoints per base glyph
            # (all 36 chars follow same base glyph in contiguous placement)
            seen_codepoints: set[str] = set()
            surviving_chars: list[tuple[int, str | None]] = []
            for i, ch in enumerate(sig):
                if i < MAGIC_PREFIX_LEN:
                    # Magic prefix always survives (unique chars)
                    surviving_chars.append((i, ch))
                    seen_codepoints.add(ch)
                elif ch in seen_codepoints:
                    # Poppler drops duplicate
                    surviving_chars.append((i, None))
                else:
                    seen_codepoints.add(ch)
                    surviving_chars.append((i, ch))

            ok, extracted, _ = recover_from_partial_extraction(surviving_chars)
            if ok and extracted == uid:
                successes += 1

        # With RS(32,24) and typical ~2.3 char loss, should recover most
        assert successes >= 90, (
            f"Expected >=90% recovery, got {successes}/{trials}"
        )
