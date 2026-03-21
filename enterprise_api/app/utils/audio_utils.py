"""Audio utility functions for the C2PA audio signing pipeline.

Provides: validation, format detection via magic bytes, SHA-256 hashing,
and MIME type mapping for supported audio formats.
"""

import logging
import struct
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Supported audio MIME types for C2PA signing (c2pa-python 0.29.0 / c2pa-rs 0.78.4)
SUPPORTED_AUDIO_MIME_TYPES = frozenset(
    {
        "audio/wav",
        "audio/wave",
        "audio/vnd.wave",
        "audio/x-wav",
        "audio/mpeg",
        "audio/mp4",
    }
)

# Canonical MIME type mapping (normalize variants to canonical form)
_CANONICAL_MIME = {
    "audio/wav": "audio/wav",
    "audio/wave": "audio/wav",
    "audio/vnd.wave": "audio/wav",
    "audio/x-wav": "audio/wav",
    "audio/mpeg": "audio/mpeg",
    "audio/mp3": "audio/mpeg",
    "audio/mp4": "audio/mp4",
    "audio/m4a": "audio/mp4",
    "audio/x-m4a": "audio/mp4",
    "audio/aac": "audio/mp4",
}

# File extension to canonical MIME type
EXTENSION_TO_MIME = {
    ".wav": "audio/wav",
    ".wave": "audio/wav",
    ".mp3": "audio/mpeg",
    ".m4a": "audio/mp4",
    ".mp4": "audio/mp4",
    ".aac": "audio/mp4",
}

# Maximum audio file size: 100 MB
AUDIO_MAX_SIZE_BYTES = 100 * 1024 * 1024

# Magic byte signatures for format detection
_RIFF_MAGIC = b"RIFF"
_WAVE_MAGIC = b"WAVE"
_ID3_MAGIC = b"ID3"
_MP3_SYNC_BYTES = (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2")  # MPEG sync words
_FTYP_OFFSET = 4  # ftyp box type at offset 4 in ISO BMFF


def canonicalize_mime_type(mime_type: str) -> str:
    """Normalize an audio MIME type to its canonical form.

    Returns the canonical MIME type string, or the original if not recognized.
    """
    return _CANONICAL_MIME.get(mime_type.lower().strip(), mime_type)


def detect_audio_format(data: bytes) -> Optional[str]:
    """Detect audio format from file magic bytes.

    Returns the canonical MIME type string, or None if format is unrecognized.
    """
    if len(data) < 12:
        return None

    # WAV: RIFF....WAVE
    if data[:4] == _RIFF_MAGIC and data[8:12] == _WAVE_MAGIC:
        return "audio/wav"

    # MP3: ID3 tag or MPEG sync word
    if data[:3] == _ID3_MAGIC:
        return "audio/mpeg"
    if data[:2] in _MP3_SYNC_BYTES:
        return "audio/mpeg"

    # ISO BMFF (M4A/AAC/MP4): ftyp box
    if len(data) >= 8 and data[4:8] == b"ftyp":
        return "audio/mp4"

    return None


def validate_audio(
    data: bytes,
    mime_type: str,
    max_size_bytes: int = AUDIO_MAX_SIZE_BYTES,
) -> Tuple[str, int]:
    """Validate audio data for C2PA signing.

    Args:
        data: Raw audio file bytes.
        mime_type: Declared MIME type string.
        max_size_bytes: Maximum allowed file size.

    Returns:
        Tuple of (canonical_mime_type, file_size_bytes).

    Raises:
        ValueError: If the audio file is invalid, too large, or has an
                    unsupported MIME type.
    """
    if not data:
        raise ValueError("Audio data is empty")

    size = len(data)
    if size > max_size_bytes:
        raise ValueError(f"Audio size {size} bytes exceeds maximum of {max_size_bytes} bytes")

    canonical = canonicalize_mime_type(mime_type)
    if canonical not in SUPPORTED_AUDIO_MIME_TYPES:
        raise ValueError(f"Unsupported audio MIME type: {mime_type!r}. Supported: {sorted(SUPPORTED_AUDIO_MIME_TYPES)}")

    detected = detect_audio_format(data)
    if detected is not None and detected != canonical:
        raise ValueError(f"MIME type mismatch: declared {mime_type!r} (canonical: {canonical}) but file magic bytes indicate {detected!r}")

    if detected is None:
        logger.warning(
            "Could not detect audio format from magic bytes for declared type %s; proceeding with declared type",
            mime_type,
        )

    return canonical, size


def get_wav_info(data: bytes) -> Optional[dict]:
    """Extract basic WAV metadata from file bytes.

    Returns dict with sample_rate, channels, bits_per_sample, duration_seconds,
    or None if not a valid WAV.
    """
    if len(data) < 44 or data[:4] != _RIFF_MAGIC or data[8:12] != _WAVE_MAGIC:
        return None

    try:
        # Parse fmt chunk (expected at offset 12)
        if data[12:16] != b"fmt ":
            return None
        fmt_size = struct.unpack_from("<I", data, 16)[0]
        if fmt_size < 16:
            return None
        (
            audio_format,
            channels,
            sample_rate,
            byte_rate,
            block_align,
            bits_per_sample,
        ) = struct.unpack_from("<HHIIHH", data, 20)

        # Find data chunk
        offset = 20 + fmt_size
        data_size = 0
        while offset < len(data) - 8:
            chunk_id = data[offset : offset + 4]
            chunk_size = struct.unpack_from("<I", data, offset + 4)[0]
            if chunk_id == b"data":
                data_size = chunk_size
                break
            offset += 8 + chunk_size
            if chunk_size % 2:
                offset += 1  # RIFF padding

        duration = data_size / byte_rate if byte_rate > 0 else 0.0

        return {
            "sample_rate": sample_rate,
            "channels": channels,
            "bits_per_sample": bits_per_sample,
            "duration_seconds": round(duration, 3),
        }
    except (struct.error, ZeroDivisionError):
        return None
