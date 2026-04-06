"""
Spread-spectrum audio watermarking with concatenated ECC.

Embeds a 64-bit payload into an audio signal using pseudo-random
spreading sequences in the time domain. Each coded bit (786 total
after RS + convolutional encoding) is spread across the full audio
duration with a unique PN (pseudo-noise) sequence.

Algorithm:
  EMBED:
    1. Encode 8-byte payload through RS(32,8) + rate-1/3 K=7 conv code
       to produce 786 coded bits.
    2. For each coded bit, generate a PN chip sequence of length
       equal to the audio sample count using HMAC-SHA256(bit_index, seed).
    3. Compute embedding strength alpha from the target SNR and signal power,
       normalised by CODED_BITS (786).
    4. Add alpha * sum(coded_bit_sign[i] * pn[i]) to the time-domain samples.

  DETECT:
    1. For each of the 786 coded bit positions, correlate the audio with the
       expected PN chip sequence to obtain a soft value.
    2. Pass 786 soft values to the Viterbi + RS decoder (ecc_decode).
    3. Confidence = mean absolute correlation, normalised by signal RMS.
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

from app.services.spread_spectrum_ecc import CODED_BITS, ecc_decode, ecc_encode

# pydub is used for MP3/M4A format conversion via ffmpeg.
# Import lazily so the service works without it for WAV-only workloads.
try:
    from pydub import AudioSegment as _AudioSegment

    _PYDUB_AVAILABLE = True
except ImportError:
    _PYDUB_AVAILABLE = False
    _AudioSegment = None  # type: ignore[assignment,misc]

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Minimum normalised correlation to declare watermark present.
# With ECC (786 coded bits), per-bit spreading gain is lower than the
# raw 64-bit scheme. Empirically, clean audio produces ~0.002 and
# a -20 dB watermark produces ~0.004, so 0.003 cleanly separates them.
_DETECTION_THRESHOLD = 0.003


# ---------------------------------------------------------------------------
# PN Sequence Generation
# ---------------------------------------------------------------------------


def _generate_chips(
    bit_index: int,
    seed: bytes,
    n_bins: int,
) -> NDArray[np.float64]:
    """Generate a deterministic +1/-1 chip sequence for a single payload bit.

    Uses HMAC-SHA256(seed, bit_index) to produce a reproducible pseudo-random
    sequence of length n_bins. Each bit gets a fully independent sequence,
    ensuring low cross-correlation between different bits' chip sequences.
    """
    key = hmac.new(seed, bit_index.to_bytes(4, "big"), hashlib.sha256).digest()
    # Use full 32-byte HMAC digest as entropy via SeedSequence for maximum PN diversity
    rng = np.random.default_rng(np.random.SeedSequence(list(key)))
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
) -> Tuple[NDArray[np.float64], float]:
    """Embed a payload into the audio signal using time-domain spread-spectrum.

    The payload is first encoded through a concatenated RS(32,8) + rate-1/3
    convolutional code, producing CODED_BITS (786) coded bits. Each coded bit
    gets its own PN chip sequence, spreading the energy across the full audio.

    Args:
        samples: Mono audio as float64 in [-1, 1].
        sample_rate: Sample rate in Hz.
        payload: Hex string of the payload (up to 16 hex chars = 64 bits).
        seed: Secret key for PN sequence generation.
        snr_db: Target watermark-to-signal ratio in dB (negative = quieter).

    Returns:
        Tuple of (watermarked_samples, confidence).
    """
    n_samples = len(samples)

    # Normalise payload to exactly 8 bytes (zero-pad on the left)
    payload_bytes = bytes.fromhex(payload.zfill(16))

    # ECC encode: 8 bytes -> 786 coded bits (0/1 uint8)
    coded_bits = ecc_encode(payload_bytes)

    # Convert coded bits to ±1 signs: 0 -> -1, 1 -> +1
    coded_signs = (coded_bits.astype(np.float64) * 2.0) - 1.0

    # Compute embedding strength from target watermark-to-signal ratio.
    # watermark_power = alpha^2 * CODED_BITS (PN sequences have unit power)
    # WSR = watermark_power / signal_power = 10^(snr_db/10)
    signal_power = np.mean(samples**2) + 1e-10
    alpha = np.sqrt(signal_power * (10.0 ** (snr_db / 10.0)) / CODED_BITS)

    # Build the composite watermark in time domain.
    # In-place multiply avoids a temporary O(n_samples) array per iteration.
    watermark = np.zeros(n_samples, dtype=np.float64)
    for i in range(CODED_BITS):
        chips = _generate_chips(i, seed, n_samples)
        chips *= coded_signs[i]
        watermark += chips

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
) -> Tuple[bool, Optional[str], float]:
    """Detect and extract a payload from audio using time-domain correlation.

    Correlates against all CODED_BITS (786) PN sequences to produce soft values,
    then decodes through Viterbi + RS to recover the 8-byte payload.

    Args:
        samples: Mono audio as float64 in [-1, 1].
        sample_rate: Sample rate in Hz.
        seed: Same secret key used during embedding.

    Returns:
        Tuple of (detected, payload_hex_or_none, confidence).
    """
    n_samples = len(samples)

    # Correlate with each coded bit's PN sequence to produce soft values.
    # Positive correlation -> coded bit was 1, negative -> coded bit was 0.
    # np.dot avoids allocating a temporary O(n_samples) product array per iteration.
    soft_values = np.zeros(CODED_BITS, dtype=np.float64)
    inv_n = 1.0 / n_samples
    for i in range(CODED_BITS):
        chips = _generate_chips(i, seed, n_samples)
        soft_values[i] = np.dot(samples, chips) * inv_n

    # Confidence: mean absolute correlation normalised by signal RMS.
    signal_rms = np.sqrt(np.mean(samples**2)) + 1e-10
    mean_abs_corr = float(np.mean(np.abs(soft_values)))
    confidence = float(np.clip(mean_abs_corr / signal_rms, 0.0, 1.0))

    if confidence <= _DETECTION_THRESHOLD:
        return False, None, confidence

    # ECC decode: Viterbi + RS erasure decoding
    recovered, _corrected = ecc_decode(soft_values)
    if recovered is None:
        return False, None, confidence

    payload_hex = recovered.hex()
    return True, payload_hex, confidence


# ---------------------------------------------------------------------------
# Audio I/O Helpers
# ---------------------------------------------------------------------------


def _decode_via_pydub(audio_bytes: bytes, fmt: Optional[str] = None) -> Tuple[NDArray[np.float64], int]:
    """Decode audio using pydub (ffmpeg backend) to mono float64 + sample rate.

    Used for formats not supported by libsndfile (MP3, M4A/AAC).
    """
    if not _PYDUB_AVAILABLE:
        raise RuntimeError("pydub is required for MP3/M4A decoding. Install with: uv add pydub")

    seg = _AudioSegment.from_file(io.BytesIO(audio_bytes), format=fmt)
    # Convert to mono, 16-bit PCM via pydub, then hand off to soundfile for
    # clean float64 normalization (avoids manual bit-depth scaling).
    seg = seg.set_channels(1)
    wav_buf = io.BytesIO()
    seg.export(wav_buf, format="wav")
    wav_buf.seek(0)
    data, sr = sf.read(wav_buf, dtype="float64", always_2d=True)
    data = data.ravel()
    return data, sr


def decode_audio(audio_bytes: bytes, fmt: Optional[str] = None) -> Tuple[NDArray[np.float64], int]:
    """Decode audio bytes to mono float64 samples + sample rate.

    Supports WAV, FLAC, OGG via libsndfile directly. Falls back to pydub
    (ffmpeg) for MP3 and M4A/AAC, which libsndfile cannot read.

    Args:
        audio_bytes: Raw audio file bytes.
        fmt: Optional format hint ("mp3", "m4a", "wav", etc.). When None,
             libsndfile is tried first; on failure, pydub is used.
    """
    _PYDUB_FORMATS = {"mp3", "m4a", "aac", "ogg", "opus"}

    if fmt is not None and fmt.lower() in _PYDUB_FORMATS:
        return _decode_via_pydub(audio_bytes, fmt=fmt.lower())

    # Try libsndfile first (fast path for WAV/FLAC/OGG)
    try:
        buf = io.BytesIO(audio_bytes)
        data, sr = sf.read(buf, dtype="float64", always_2d=True)
        if data.ndim == 2 and data.shape[1] > 1:
            data = np.mean(data, axis=1)
        else:
            data = data.ravel()
        return data, sr
    except Exception:
        pass

    # Fall back to pydub for formats soundfile cannot handle
    return _decode_via_pydub(audio_bytes, fmt=fmt)


def encode_audio(
    samples: NDArray[np.float64],
    sample_rate: int,
    output_format: str = "WAV",
    subtype: str = "PCM_16",
    bitrate: str = "128k",
) -> bytes:
    """Encode mono float64 samples to audio bytes.

    Args:
        samples: Mono float64 audio in [-1, 1].
        sample_rate: Sample rate in Hz.
        output_format: Output format. "WAV" and "FLAC" use soundfile directly.
            "MP3" and "M4A" (AAC) use pydub/ffmpeg.
        subtype: PCM subtype for WAV/FLAC (ignored for MP3/M4A).
        bitrate: Bitrate for lossy encoding (MP3/M4A), e.g. "128k", "64k".
    """
    fmt_upper = output_format.upper()

    if fmt_upper in ("WAV", "FLAC", "OGG"):
        buf = io.BytesIO()
        sf.write(buf, samples, sample_rate, format=fmt_upper, subtype=subtype)
        return buf.getvalue()

    # MP3 / M4A path: encode to WAV first, then transcode via pydub
    if not _PYDUB_AVAILABLE:
        raise RuntimeError("pydub is required for MP3/M4A encoding. Install with: uv add pydub")

    wav_buf = io.BytesIO()
    sf.write(wav_buf, samples, sample_rate, format="WAV", subtype="PCM_16")
    wav_buf.seek(0)

    seg = _AudioSegment.from_wav(wav_buf)

    out_buf = io.BytesIO()
    if fmt_upper == "MP3":
        seg.export(out_buf, format="mp3", bitrate=bitrate)
    elif fmt_upper in ("M4A", "AAC"):
        seg.export(out_buf, format="mp4", codec="aac", bitrate=bitrate)
    else:
        raise ValueError(f"Unsupported output format: {output_format!r}. Use WAV, FLAC, OGG, MP3, or M4A.")

    return out_buf.getvalue()
