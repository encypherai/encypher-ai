"""Comprehensive tests for the concatenated ECC module (RS + convolutional + soft Viterbi)."""

import numpy as np
import pytest

from spread_spectrum_ecc import (
    _conv_encode,
    _erasure_bridge,
    _rs_decode,
    _rs_encode,
    _viterbi_decode,
    ecc_decode,
    ecc_encode,
)


# ---------------------------------------------------------------------------
# Reed-Solomon tests
# ---------------------------------------------------------------------------


class TestReedSolomon:
    def test_rs_encode_decode_roundtrip(self):
        """8 random bytes through RS encode/decode, no errors."""
        rng = np.random.default_rng(42)
        data = bytes(rng.integers(0, 256, size=8, dtype=np.uint8))
        encoded = _rs_encode(data)
        assert len(encoded) == 32
        decoded = _rs_decode(encoded)
        assert decoded == data

    def test_rs_decode_with_errors(self):
        """Inject up to 12 symbol errors, verify recovery."""
        rng = np.random.default_rng(123)
        data = bytes(rng.integers(0, 256, size=8, dtype=np.uint8))
        encoded = bytearray(_rs_encode(data))

        # Corrupt exactly 12 symbols (the maximum correctable)
        error_positions = rng.choice(32, size=12, replace=False)
        for pos in error_positions:
            encoded[pos] ^= rng.integers(1, 256)

        decoded = _rs_decode(bytes(encoded))
        assert decoded == data

    def test_rs_decode_failure(self):
        """Inject 13+ symbol errors, verify returns None."""
        rng = np.random.default_rng(456)
        data = bytes(rng.integers(0, 256, size=8, dtype=np.uint8))
        encoded = bytearray(_rs_encode(data))

        # Corrupt 13 symbols (beyond correction capacity)
        error_positions = rng.choice(32, size=13, replace=False)
        for pos in error_positions:
            encoded[pos] ^= rng.integers(1, 256)

        decoded = _rs_decode(bytes(encoded))
        assert decoded is None

    def test_rs_decode_with_erasures(self):
        """Inject up to 24 erasures with known positions, verify recovery."""
        rng = np.random.default_rng(789)
        data = bytes(rng.integers(0, 256, size=8, dtype=np.uint8))
        encoded = bytearray(_rs_encode(data))

        # Erase 24 symbols (the maximum erasure-correctable)
        erasure_positions = list(rng.choice(32, size=24, replace=False))
        for pos in erasure_positions:
            encoded[pos] = 0

        decoded = _rs_decode(bytes(encoded), erasure_pos=erasure_positions)
        assert decoded == data


# ---------------------------------------------------------------------------
# Convolutional encoder / Viterbi decoder tests
# ---------------------------------------------------------------------------


class TestConvolutionalCode:
    def test_conv_encode_decode_roundtrip(self):
        """Random bits through conv encode + Viterbi decode (no noise), perfect recovery."""
        rng = np.random.default_rng(42)
        # 256 data bits (as would come from 32 RS bytes)
        bits = rng.integers(0, 2, size=256, dtype=np.uint8)

        # Append K-1=6 tail bits
        bits_with_tail = np.concatenate([bits, np.zeros(6, dtype=np.uint8)])
        coded = _conv_encode(bits_with_tail)
        assert len(coded) == 262 * 3  # 786

        # Perfect soft values: map 0->-1.0, 1->+1.0
        soft = np.where(coded == 1, 1.0, -1.0)
        decoded_bits, confidence = _viterbi_decode(soft)

        # Strip tail bits; compare data bits
        assert len(decoded_bits) >= 256
        np.testing.assert_array_equal(decoded_bits[:256], bits)

    def test_conv_encode_deterministic(self):
        """Same input always produces same output."""
        bits = np.array([1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0], dtype=np.uint8)  # 8 data + 6 tail
        out1 = _conv_encode(bits)
        out2 = _conv_encode(bits)
        np.testing.assert_array_equal(out1, out2)

    def test_viterbi_soft_vs_hard(self):
        """Add Gaussian noise, compare BER of soft Viterbi vs hard decisions. Soft should win."""
        rng = np.random.default_rng(99)
        bits = rng.integers(0, 2, size=256, dtype=np.uint8)
        bits_with_tail = np.concatenate([bits, np.zeros(6, dtype=np.uint8)])
        coded = _conv_encode(bits_with_tail)

        # BPSK: 0->-1.0, 1->+1.0
        bpsk = np.where(coded == 1, 1.0, -1.0).astype(np.float64)

        # Add moderate noise
        noise = rng.normal(0, 0.8, size=len(bpsk))
        received = bpsk + noise

        # Soft Viterbi decode
        decoded_soft, _ = _viterbi_decode(received)

        # Hard decision decode (quantize to +/-1 then Viterbi)
        hard_received = np.where(received >= 0, 1.0, -1.0)
        decoded_hard, _ = _viterbi_decode(hard_received)

        ber_soft = np.mean(decoded_soft[:256] != bits)
        ber_hard = np.mean(decoded_hard[:256] != bits)

        # Soft decoding should have equal or lower BER
        assert ber_soft <= ber_hard + 0.01, f"Soft BER {ber_soft:.4f} should be <= Hard BER {ber_hard:.4f}"


# ---------------------------------------------------------------------------
# Full pipeline tests
# ---------------------------------------------------------------------------


class TestFullPipeline:
    def test_full_pipeline_no_noise(self):
        """8-byte payload through ecc_encode + ecc_decode with perfect soft values."""
        payload = b"\xde\xad\xbe\xef\xca\xfe\xba\xbe"
        coded_bits = ecc_encode(payload)
        assert coded_bits.shape == (786,)
        assert coded_bits.dtype == np.uint8
        assert set(np.unique(coded_bits)).issubset({0, 1})

        # Perfect soft values
        soft = np.where(coded_bits == 1, 1.0, -1.0).astype(np.float64)
        recovered, corrected = ecc_decode(soft)
        assert recovered == payload
        assert corrected == 0  # No corrections needed

    def test_full_pipeline_moderate_noise(self):
        """Add Gaussian noise (sigma=0.5, ~5% raw BER), verify ECC recovers payload."""
        rng = np.random.default_rng(2024)
        payload = bytes(rng.integers(0, 256, size=8, dtype=np.uint8))
        coded_bits = ecc_encode(payload)

        bpsk = np.where(coded_bits == 1, 1.0, -1.0).astype(np.float64)
        noise = rng.normal(0, 0.5, size=len(bpsk))
        received = bpsk + noise

        recovered, corrected = ecc_decode(received)
        assert recovered == payload

    def test_full_pipeline_heavy_noise(self):
        """Add Gaussian noise (sigma=1.0, ~15% raw BER), verify ECC still recovers."""
        rng = np.random.default_rng(2025)
        payload = bytes(rng.integers(0, 256, size=8, dtype=np.uint8))
        coded_bits = ecc_encode(payload)

        bpsk = np.where(coded_bits == 1, 1.0, -1.0).astype(np.float64)
        noise = rng.normal(0, 1.0, size=len(bpsk))
        received = bpsk + noise

        recovered, corrected = ecc_decode(received)
        assert recovered == payload

    def test_full_pipeline_extreme_noise(self):
        """Add noise beyond correction capacity, verify graceful failure (returns None)."""
        rng = np.random.default_rng(2026)
        payload = bytes(rng.integers(0, 256, size=8, dtype=np.uint8))
        coded_bits = ecc_encode(payload)

        bpsk = np.where(coded_bits == 1, 1.0, -1.0).astype(np.float64)
        # Very heavy noise: sigma=3.0 gives ~30%+ raw BER
        noise = rng.normal(0, 3.0, size=len(bpsk))
        received = bpsk + noise

        recovered, corrected = ecc_decode(received)
        assert recovered is None


# ---------------------------------------------------------------------------
# Erasure bridge test
# ---------------------------------------------------------------------------


class TestErasureBridge:
    def test_erasure_bridge(self):
        """Artificially zero out some soft values (low confidence), verify they become erasures and RS exploits them."""
        rng = np.random.default_rng(555)
        payload = bytes(rng.integers(0, 256, size=8, dtype=np.uint8))
        coded_bits = ecc_encode(payload)

        bpsk = np.where(coded_bits == 1, 1.0, -1.0).astype(np.float64)

        # Add mild noise
        noise = rng.normal(0, 0.3, size=len(bpsk))
        received = bpsk + noise

        # Zero out soft values for ~8 symbols worth of coded bits
        # Each RS symbol = 8 bits, each bit = 3 coded bits, so 8 symbols = 192 coded bits
        # Zero those out to create low-confidence region
        received[:192] = rng.normal(0, 0.01, size=192)

        recovered, corrected = ecc_decode(received, erasure_threshold=0.1)
        assert recovered == payload

    def test_erasure_bridge_internal(self):
        """Directly test _erasure_bridge marks low-confidence symbols as erasures."""
        # 32 symbols = 256 bits
        decoded_bits = np.zeros(256, dtype=np.uint8)
        # High confidence everywhere except symbols 0-3 (bits 0-31)
        bit_confidence = np.ones(256, dtype=np.float64) * 5.0
        bit_confidence[:32] = 0.05  # Low confidence for first 4 symbols

        data_bytes, erasure_positions = _erasure_bridge(decoded_bits, bit_confidence, threshold=0.1)
        assert len(data_bytes) == 32
        assert set(erasure_positions) == {0, 1, 2, 3}


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_all_zeros_payload(self):
        """Edge case: b'\\x00' * 8."""
        payload = b"\x00" * 8
        coded_bits = ecc_encode(payload)
        soft = np.where(coded_bits == 1, 1.0, -1.0).astype(np.float64)
        recovered, corrected = ecc_decode(soft)
        assert recovered == payload
        assert corrected == 0

    def test_all_ones_payload(self):
        """Edge case: b'\\xff' * 8."""
        payload = b"\xff" * 8
        coded_bits = ecc_encode(payload)
        soft = np.where(coded_bits == 1, 1.0, -1.0).astype(np.float64)
        recovered, corrected = ecc_decode(soft)
        assert recovered == payload
        assert corrected == 0

    def test_random_payloads(self):
        """20 random 8-byte payloads, all roundtrip successfully."""
        rng = np.random.default_rng(1337)
        for i in range(20):
            payload = bytes(rng.integers(0, 256, size=8, dtype=np.uint8))
            coded_bits = ecc_encode(payload)
            soft = np.where(coded_bits == 1, 1.0, -1.0).astype(np.float64)
            recovered, corrected = ecc_decode(soft)
            assert recovered == payload, f"Failed on random payload {i}: {payload.hex()}"

    def test_payload_length_validation(self):
        """ecc_encode rejects payloads != 8 bytes."""
        with pytest.raises(ValueError, match="exactly 8 bytes"):
            ecc_encode(b"\x00" * 7)
        with pytest.raises(ValueError, match="exactly 8 bytes"):
            ecc_encode(b"\x00" * 9)
        with pytest.raises(ValueError, match="exactly 8 bytes"):
            ecc_encode(b"")
