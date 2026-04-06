"""
Spread-spectrum video watermarking (Y-channel).

Embeds a 64-bit payload into the luminance (Y) channel of video frames using
pseudo-random spreading sequences in the spatial/temporal domain. Each payload
bit is spread across a full block of Y-channel pixels with a unique PN sequence,
making the watermark robust to common video transformations.

The PN generation is mathematically identical to the audio service. The key
difference is that the input signal is 2D Y-channel pixel values (flattened to
1D for PN correlation) rather than audio samples.

ECC uses a two-layer concatenated code (RS(32,8) + rate-1/3 convolutional) to
expand the 64-bit payload to 786 coded bits, then spreads each coded bit across
the full pixel block. Soft-decision Viterbi + erasure-assisted RS decoding
recovers the payload even under significant pixel noise.

Algorithm:
  EMBED:
    1. Flatten the Y-channel pixel block to a 1D signal.
    2. ECC-encode the 8-byte payload to 786 coded bits via ecc_encode().
    3. For each coded bit, generate a PN chip sequence of length equal to the
       pixel count using HMAC-SHA256(bit_index, seed).
    4. Compute embedding strength alpha from the target WSR and signal power.
    5. Add alpha * bit_sign[i] * pn[i] to the pixel values.
    6. Clip to [0, 255] to maintain valid pixel range.

  DETECT:
    1. Flatten the Y-channel pixel block to a 1D signal.
    2. For each of the 786 coded bit positions, correlate the signal with the
       expected PN sequence to produce a soft float value.
    3. Pass the 786 soft values to ecc_decode() for Viterbi + RS recovery.
    4. Confidence = mean absolute correlation, normalized by signal RMS.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
from typing import Optional, Tuple

import numpy as np
from numpy.typing import NDArray

from app.services.spread_spectrum_ecc import CODED_BITS, ecc_decode, ecc_encode

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DETECTION_THRESHOLD = 0.01  # Minimum normalized correlation to declare detection


# ---------------------------------------------------------------------------
# PN Sequence Generation
# ---------------------------------------------------------------------------


def _generate_chips(
    seed: bytes,
    bit_index: int,
    length: int,
) -> NDArray[np.float64]:
    """Generate a deterministic +1/-1 chip sequence for a single payload bit.

    Uses HMAC-SHA256(seed, bit_index) to produce a reproducible pseudo-random
    sequence of length `length`. Each bit gets a fully independent sequence,
    ensuring low cross-correlation between different bits' chip sequences.

    This function is mathematically identical to the audio service's
    _generate_chips() - the signature order is (seed, bit_index, length)
    to match the SOW specification.
    """
    key = hmac.new(seed, bit_index.to_bytes(4, "big"), hashlib.sha256).digest()
    # Use full 32-byte HMAC digest as entropy via SeedSequence for maximum PN diversity
    rng = np.random.default_rng(np.random.SeedSequence(list(key)))
    chips = rng.choice([-1.0, 1.0], size=length)
    return chips


# ---------------------------------------------------------------------------
# Core Embed / Detect
# ---------------------------------------------------------------------------


def embed(
    y_signal: NDArray[np.float64],
    payload_hex: str,
    seed: bytes,
    wsr_db: float = -30.0,
) -> Tuple[NDArray[np.float64], float]:
    """Embed payload into flattened Y-channel signal using ECC.

    Args:
        y_signal:    1D float64 array of Y-channel pixel values (flattened across
                     frames in a block). Values should be in [0, 255].
        payload_hex: 16-char hex string (64-bit payload).
        seed:        Secret seed for PN generation.
        wsr_db:      Watermark-to-signal ratio in dB (default -30).

    Returns:
        (watermarked_signal, confidence) where watermarked_signal has the same
        shape as y_signal with values clipped to [0, 255].

    Implementation note:
        Y-channel pixel values have a large DC component (~128) which would
        swamp the PN correlation if used directly. The signal is normalized to
        the zero-mean [-1, 1] domain (matching the audio service's conventions)
        before embedding, then denormalized after. Callers pass and receive raw
        [0, 255] values; the normalization is internal.
    """
    n_pixels = len(y_signal)

    # Normalize to zero-mean [-1, 1] domain to eliminate DC correlation bias.
    y_norm = (y_signal / 127.5) - 1.0

    # ECC-encode: 8 bytes -> 786 coded bits (uint8, 0/1)
    payload_bytes = bytes.fromhex(payload_hex.zfill(16))
    coded_bits = ecc_encode(payload_bytes)

    # Convert coded bits to +1/-1 signs
    bit_signs = np.where(coded_bits, 1.0, -1.0).astype(np.float64)

    # Compute embedding strength from target watermark-to-signal ratio.
    # WSR = watermark_power / signal_power = 10^(wsr_db/10)
    signal_power = np.mean(y_norm**2) + 1e-10
    alpha = np.sqrt(signal_power * (10.0 ** (wsr_db / 10.0)) / CODED_BITS)

    # Build the composite watermark in normalized domain.
    # In-place multiply avoids a temporary O(n_pixels) array per iteration.
    watermark = np.zeros(n_pixels, dtype=np.float64)
    for i in range(CODED_BITS):
        chips = _generate_chips(seed, i, n_pixels)
        chips *= bit_signs[i]
        watermark += chips

    watermark *= alpha

    # Add watermark, clip to [-1, 1], then denormalize back to [0, 255]
    wm_norm = np.clip(y_norm + watermark, -1.0, 1.0)
    watermarked = (wm_norm + 1.0) * 127.5

    # Compute actual WSR for confidence reporting
    noise = watermarked - y_signal
    noise_power = np.mean(noise**2) + 1e-10
    signal_power_pixels = np.mean(y_signal**2) + 1e-10
    actual_wsr = 10.0 * np.log10(signal_power_pixels / noise_power)
    confidence = min(1.0, max(0.0, 1.0 - abs(actual_wsr - abs(wsr_db)) / 60.0))

    return watermarked, confidence


def detect(
    y_signal: NDArray[np.float64],
    seed: bytes,
) -> Tuple[bool, Optional[str], float]:
    """Detect and extract payload from Y-channel signal using ECC.

    Args:
        y_signal:    1D float64 array of Y-channel pixel values (flattened).
                     Values should be in [0, 255].
        seed:        Same secret seed used during embedding.

    Returns:
        (detected, payload_hex_or_None, confidence)
    """
    n_pixels = len(y_signal)

    # Normalize to zero-mean [-1, 1] domain before correlation.
    y_norm = (y_signal / 127.5) - 1.0

    # Correlate with each of the 786 coded bit PN sequences to produce soft values.
    # Positive = confident 1, negative = confident 0, magnitude = confidence.
    # np.dot avoids allocating a temporary O(n_pixels) product array per iteration.
    soft_values = np.zeros(CODED_BITS, dtype=np.float64)
    inv_n = 1.0 / n_pixels
    for i in range(CODED_BITS):
        chips = _generate_chips(seed, i, n_pixels)
        soft_values[i] = np.dot(y_norm, chips) * inv_n

    # Confidence: mean absolute correlation normalized by signal RMS.
    signal_rms = np.sqrt(np.mean(y_norm**2)) + 1e-10
    mean_abs_corr = float(np.mean(np.abs(soft_values)))
    confidence = float(np.clip(mean_abs_corr / signal_rms, 0.0, 1.0))

    detected = confidence > _DETECTION_THRESHOLD

    if not detected:
        return False, None, confidence

    # ECC decode: soft Viterbi + RS recovery
    result_bytes, error_count = ecc_decode(soft_values)
    if result_bytes is None:
        return False, None, confidence

    # Penalize confidence if many symbols were corrected
    if error_count > 0:
        correction_penalty = min(0.5, error_count / 32.0)
        confidence = float(np.clip(confidence * (1.0 - correction_penalty), 0.0, 1.0))

    payload_hex = result_bytes.hex()
    return True, payload_hex, confidence
