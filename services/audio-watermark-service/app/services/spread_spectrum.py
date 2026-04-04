"""
Spread-spectrum audio watermarking.

Embeds a 64-bit payload into an audio signal using pseudo-random
spreading sequences in the time domain. Each payload bit is spread
across the full audio duration with a unique PN (pseudo-noise)
sequence, making the watermark robust to common audio transformations.

Algorithm:
  EMBED:
    1. For each payload bit, generate a PN chip sequence of length
       equal to the audio sample count using HMAC-SHA256(bit_index, seed).
    2. Compute embedding strength alpha from the target SNR and signal power.
    3. Add alpha * sum(bit_sign[i] * pn[i]) to the time-domain samples.

  DETECT:
    1. For each payload bit, correlate the audio with the expected
       PN chip sequence.
    2. Positive correlation -> bit=1, negative -> bit=0.
    3. Confidence = mean absolute correlation, normalized by signal RMS.
"""

from __future__ import annotations

import hashlib
import hmac
import io
import logging
from typing import Optional, Tuple

import numpy as np
import soundfile as sf
from numpy.typing import NDArray

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DETECTION_THRESHOLD = 0.01  # Minimum normalized correlation to declare detection


# ---------------------------------------------------------------------------
# PN Sequence Generation
# ---------------------------------------------------------------------------


def _generate_chips(
    bit_index: int,
    seed: bytes,
    chip_rate: int,
    n_bins: int,
) -> NDArray[np.float64]:
    """Generate a deterministic +1/-1 chip sequence for a single payload bit.

    Uses HMAC-SHA256(seed, bit_index) to produce a reproducible pseudo-random
    sequence of length n_bins. Each bit gets a fully independent sequence,
    ensuring low cross-correlation between different bits' chip sequences.

    chip_rate is reserved for future use (e.g., controlling active bins per bit).
    """
    key = hmac.new(seed, bit_index.to_bytes(4, "big"), hashlib.sha256).digest()
    rng = np.random.RandomState(int.from_bytes(key[:4], "big"))
    chips = rng.choice([-1.0, 1.0], size=n_bins)
    return chips


# ---------------------------------------------------------------------------
# Core Embed / Detect
# ---------------------------------------------------------------------------


def embed(
    samples: NDArray[np.float64],
    sample_rate: int,
    payload: str,
    seed: bytes,
    snr_db: float = -20.0,
    chip_rate: int = 8,
    payload_bits: int = 64,
) -> Tuple[NDArray[np.float64], float]:
    """Embed a payload into the audio signal using time-domain spread-spectrum.

    Args:
        samples: Mono audio as float64 in [-1, 1].
        sample_rate: Sample rate in Hz.
        payload: Hex string of the payload (16 chars for 64 bits).
        seed: Secret key for PN sequence generation.
        snr_db: Target watermark-to-signal ratio in dB (negative = quieter).
        chip_rate: Reserved for future use.
        payload_bits: Number of payload bits to embed.

    Returns:
        Tuple of (watermarked_samples, confidence).
    """
    if len(payload) * 4 < payload_bits:
        raise ValueError(f"Payload hex {payload!r} too short for {payload_bits} bits")

    n_samples = len(samples)

    # Convert hex payload to bit signs: 0 -> -1, 1 -> +1
    payload_int = int(payload, 16)
    bit_signs = np.array(
        [1.0 if (payload_int >> (payload_bits - 1 - i)) & 1 else -1.0 for i in range(payload_bits)],
        dtype=np.float64,
    )

    # Compute embedding strength from target watermark-to-signal ratio.
    # watermark_power = alpha^2 * payload_bits (PN sequences have unit power)
    # WSR = watermark_power / signal_power = 10^(snr_db/10)
    signal_power = np.mean(samples**2) + 1e-10
    alpha = np.sqrt(signal_power * (10.0 ** (snr_db / 10.0)) / payload_bits)

    # Build the composite watermark in time domain
    watermark = np.zeros(n_samples, dtype=np.float64)
    for i in range(payload_bits):
        chips = _generate_chips(i, seed, chip_rate, n_samples)
        watermark += bit_signs[i] * chips

    watermark *= alpha

    # Add watermark and clip to valid range
    watermarked = np.clip(samples + watermark, -1.0, 1.0)

    # Compute actual SNR for confidence reporting
    noise = watermarked - samples
    noise_power = np.mean(noise**2) + 1e-10
    actual_snr = 10.0 * np.log10(signal_power / noise_power)
    confidence = min(1.0, max(0.0, 1.0 - abs(actual_snr - abs(snr_db)) / 60.0))

    return watermarked, confidence


def detect(
    samples: NDArray[np.float64],
    sample_rate: int,
    seed: bytes,
    chip_rate: int = 8,
    payload_bits: int = 64,
) -> Tuple[bool, Optional[str], float]:
    """Detect and extract a payload from audio using time-domain correlation.

    Args:
        samples: Mono audio as float64 in [-1, 1].
        sample_rate: Sample rate in Hz.
        seed: Same secret key used during embedding.
        chip_rate: Same chip rate used during embedding.
        payload_bits: Number of payload bits.

    Returns:
        Tuple of (detected, payload_hex_or_none, confidence).
    """
    n_samples = len(samples)

    # Correlate with each bit's PN sequence
    correlations = np.zeros(payload_bits)
    for i in range(payload_bits):
        chips = _generate_chips(i, seed, chip_rate, n_samples)
        correlations[i] = np.mean(samples * chips)

    # Extract bits: positive correlation -> 1, negative -> 0
    extracted_bits = (correlations > 0).astype(int)

    # Confidence: mean absolute correlation normalized by signal RMS.
    # Without a watermark, correlations are ~0 (PN uncorrelated with signal).
    # With a watermark, |correlation| ~ alpha.
    signal_rms = np.sqrt(np.mean(samples**2)) + 1e-10
    abs_corr = np.abs(correlations)
    mean_abs_corr = float(np.mean(abs_corr))
    confidence = float(np.clip(mean_abs_corr / signal_rms, 0.0, 1.0))

    detected = confidence > _DETECTION_THRESHOLD

    if detected:
        payload_int = 0
        for bit in extracted_bits:
            payload_int = (payload_int << 1) | int(bit)
        payload_hex = f"{payload_int:0{payload_bits // 4}x}"
        return True, payload_hex, confidence
    else:
        return False, None, confidence


# ---------------------------------------------------------------------------
# Audio I/O Helpers
# ---------------------------------------------------------------------------


def decode_audio(audio_bytes: bytes) -> Tuple[NDArray[np.float64], int]:
    """Decode audio bytes to mono float64 samples + sample rate."""
    buf = io.BytesIO(audio_bytes)
    data, sr = sf.read(buf, dtype="float64", always_2d=True)
    # Convert to mono by averaging channels
    if data.ndim == 2 and data.shape[1] > 1:
        data = np.mean(data, axis=1)
    else:
        data = data.ravel()
    return data, sr


def encode_audio(
    samples: NDArray[np.float64],
    sample_rate: int,
    output_format: str = "WAV",
    subtype: str = "PCM_16",
) -> bytes:
    """Encode mono float64 samples to audio bytes."""
    buf = io.BytesIO()
    sf.write(buf, samples, sample_rate, format=output_format, subtype=subtype)
    return buf.getvalue()
