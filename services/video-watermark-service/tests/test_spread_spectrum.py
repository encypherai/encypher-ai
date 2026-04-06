"""
Tests for the spread-spectrum Y-channel watermarking module (ECC-enabled).

Signal-size notes:
  ECC expands 64 payload bits to 786 coded bits (RS(32,8) + rate-1/3 convolutional),
  reducing per-bit spreading gain by ~12x compared to the non-ECC path. Reliable
  detection therefore requires a larger pixel count or higher WSR than before.

  Unit tests use -5 dB WSR with N=200,000 pixels to maintain reliable detection
  while keeping runtime acceptable. The imperceptibility test still uses -30 dB
  WSR (production setting) and only checks PSNR - detection at -30 dB requires
  production block sizes (~276M pixels per block).
"""

import numpy as np

from app.services.spread_spectrum import _generate_chips, detect, embed
from app.services.spread_spectrum_ecc import CODED_BITS

SEED_A = b"test-seed-alpha"
SEED_B = b"test-seed-beta"

# ECC expands payload to CODED_BITS=786. At -5 dB WSR and N=200,000 pixels the
# per-coded-bit correlation SNR is well above the detection threshold.
TEST_N = 200_000
TEST_WSR_DB = -5.0


def _random_y_signal(n: int = TEST_N, seed: int = 42) -> np.ndarray:
    """Synthetic Y-channel signal with realistic pixel value distribution."""
    rng = np.random.default_rng(seed)
    return rng.uniform(20.0, 235.0, size=n)


def _random_payload(rng: np.random.Generator) -> str:
    # Use 63-bit range to stay within int64 bounds
    val = int(rng.integers(0, 2**63))
    return f"{val:016x}"


# ---------------------------------------------------------------------------
# PN chip generation
# ---------------------------------------------------------------------------


def test_pn_chip_determinism():
    """Same seed + bit_index + length always produces the same chips."""
    chips_1 = _generate_chips(SEED_A, 0, 1000)
    chips_2 = _generate_chips(SEED_A, 0, 1000)
    np.testing.assert_array_equal(chips_1, chips_2)


def test_pn_chip_uniqueness():
    """Different bit_indices produce different chip sequences."""
    chips_0 = _generate_chips(SEED_A, 0, 1000)
    chips_1 = _generate_chips(SEED_A, 1, 1000)
    chips_2 = _generate_chips(SEED_A, 2, 1000)
    assert not np.array_equal(chips_0, chips_1), "bit 0 and bit 1 chips must differ"
    assert not np.array_equal(chips_0, chips_2), "bit 0 and bit 2 chips must differ"
    assert not np.array_equal(chips_1, chips_2), "bit 1 and bit 2 chips must differ"


def test_pn_chip_values():
    """All chip values must be exactly +1 or -1."""
    chips = _generate_chips(SEED_A, 7, 5000)
    assert set(np.unique(chips)).issubset({-1.0, 1.0}), "chips must be binary +1/-1"


# ---------------------------------------------------------------------------
# ECC constants
# ---------------------------------------------------------------------------


def test_ecc_coded_bits_constant():
    """CODED_BITS must be 786 (RS(32,8) + rate-1/3 conv, 262 input bits)."""
    assert CODED_BITS == 786


# ---------------------------------------------------------------------------
# Embed / detect roundtrip
# ---------------------------------------------------------------------------


def test_embed_detect_roundtrip():
    """Embed a known payload, then detect it - payload must match exactly."""
    y_signal = _random_y_signal(TEST_N)
    payload = "deadbeefcafe0123"  # pragma: allowlist secret

    watermarked, confidence = embed(y_signal, payload, SEED_A, wsr_db=TEST_WSR_DB)
    assert watermarked.shape == y_signal.shape
    assert 0.0 <= confidence <= 1.0

    detected, extracted, conf = detect(watermarked, SEED_A)
    assert detected, "watermark should be detected"
    assert extracted == payload, f"extracted {extracted!r} != embedded {payload!r}"
    assert conf > 0.0


def test_embed_detect_roundtrip_multiple_payloads():
    """10 random payloads should all roundtrip correctly."""
    rng = np.random.default_rng(99)
    y_signal = _random_y_signal(TEST_N)

    for _ in range(10):
        payload = _random_payload(rng)
        watermarked, _conf = embed(y_signal, payload, SEED_A, wsr_db=TEST_WSR_DB)
        detected, extracted, conf = detect(watermarked, SEED_A)
        assert detected, f"payload {payload!r} not detected after roundtrip"
        assert extracted == payload, f"extracted {extracted!r} != embedded {payload!r}"


def test_no_false_positive():
    """Clean signal (no watermark) should not trigger detection."""
    y_signal = _random_y_signal(TEST_N, seed=7)
    detected, payload, confidence = detect(y_signal, SEED_A)
    assert not detected, f"false positive: clean signal detected with confidence {confidence:.4f}"
    assert payload is None


def test_wrong_seed():
    """Embed with SEED_A, detect with SEED_B: must not recover the correct payload."""
    y_signal = _random_y_signal(TEST_N, seed=13)
    payload = "0011223344556677"

    watermarked, _ = embed(y_signal, payload, SEED_A, wsr_db=TEST_WSR_DB)
    detected, extracted, confidence = detect(watermarked, SEED_B)

    # Either not detected, or detected with wrong payload
    if detected:
        assert extracted != payload, "wrong seed must not recover the correct payload"


def test_imperceptibility():
    """Watermarked signal PSNR vs original must exceed 40 dB at -30 dB WSR.

    Uses a larger pixel count (200k) so the PSNR is stable; detection is not
    asserted here because -30 dB requires ~1M+ pixels for reliable detection
    (production block sizes are 300 frames * 720 * 1280 = ~276M pixels).
    """
    y_signal = _random_y_signal(200_000, seed=55)
    payload = "aabbccddeeff0011"

    watermarked, _ = embed(y_signal, payload, SEED_A, wsr_db=-30.0)

    mse = np.mean((watermarked - y_signal) ** 2)
    if mse == 0.0:
        psnr = float("inf")
    else:
        # MAX value is 255 for Y-channel pixels
        psnr = 10.0 * np.log10((255.0**2) / mse)

    assert psnr > 40.0, f"PSNR {psnr:.1f} dB is below 40 dB imperceptibility threshold"


# ---------------------------------------------------------------------------
# ECC-specific test: noise injection and error correction
# ---------------------------------------------------------------------------


def test_ecc_noise_recovery():
    """Embed with ECC, inject pixel noise, verify ECC recovers the payload.

    This test confirms that the ECC layer (RS + Viterbi) recovers the payload
    even after additive noise degrades the watermark SNR. At -5 dB WSR with
    200k pixels and moderate noise (sigma=8), recovery should succeed.
    """
    rng = np.random.default_rng(2024)
    y_signal = _random_y_signal(TEST_N, seed=17)
    payload = "cafebabe12345678"  # pragma: allowlist secret

    # Embed at -5 dB WSR
    watermarked, _ = embed(y_signal, payload, SEED_A, wsr_db=TEST_WSR_DB)

    # Inject additive Gaussian noise (sigma=8 pixel units) to degrade the channel
    noise = rng.normal(0.0, 8.0, size=TEST_N)
    noisy = np.clip(watermarked + noise, 0.0, 255.0)

    detected, extracted, conf = detect(noisy, SEED_A)
    assert detected, f"ECC failed to recover payload after noise injection (conf={conf:.4f})"
    assert extracted == payload, f"ECC recovered wrong payload: {extracted!r} != {payload!r}"
