"""Video utility functions for the C2PA video signing pipeline.

Provides: validation, format detection via magic bytes, SHA-256 hashing,
and MIME type mapping for supported video formats.
"""

import logging
import os
import struct
import subprocess
import tempfile
from io import BytesIO
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Supported video MIME types for C2PA signing (c2pa-python 0.29.0 / c2pa-rs 0.78.4)
SUPPORTED_VIDEO_MIME_TYPES = frozenset(
    {
        "video/mp4",
        "video/quicktime",
        "video/x-m4v",
        "video/x-msvideo",
        "video/avi",
        "video/msvideo",
    }
)

# Canonical MIME type mapping (normalize variants to canonical form)
_CANONICAL_MIME = {
    "video/mp4": "video/mp4",
    "video/quicktime": "video/quicktime",
    "video/x-m4v": "video/x-m4v",
    "video/x-msvideo": "video/x-msvideo",
    "video/avi": "video/x-msvideo",
    "video/msvideo": "video/x-msvideo",
}

# File extension to canonical MIME type
EXTENSION_TO_MIME = {
    ".mp4": "video/mp4",
    ".mov": "video/quicktime",
    ".m4v": "video/x-m4v",
    ".avi": "video/x-msvideo",
}

# Maximum video file size: 500 MB
VIDEO_MAX_SIZE_BYTES = 500 * 1024 * 1024

# Magic byte signatures for format detection
_FTYP_OFFSET = 4  # ftyp box type at offset 4 in ISO BMFF
_RIFF_MAGIC = b"RIFF"
_AVI_MAGIC = b"AVI "
_EBML_MAGIC = b"\x1a\x45\xdf\xa3"

# ISO BMFF family: ftyp-detected video may be declared as any of these
_ISO_BMFF_CANONICAL_MIMES = frozenset({"video/mp4", "video/quicktime", "video/x-m4v"})


def canonicalize_mime_type(mime_type: str) -> str:
    """Normalize a video MIME type to its canonical form.

    Returns the canonical MIME type string, or the original if not recognized.
    """
    return _CANONICAL_MIME.get(mime_type.lower().strip(), mime_type)


def detect_video_format(data: bytes) -> Optional[str]:
    """Detect video format from file magic bytes.

    Returns the canonical MIME type string, or None if format is unrecognized.
    """
    if len(data) < 12:
        return None

    # EBML magic (WebM/MKV) -- not in supported set, will trigger rejection
    if data[:4] == _EBML_MAGIC:
        return "video/webm"

    # ISO BMFF (MP4/MOV/M4V): ftyp box at offset 4
    if len(data) >= 8 and data[4:8] == b"ftyp":
        return "video/mp4"

    # AVI: RIFF....AVI
    if data[:4] == _RIFF_MAGIC and data[8:12] == _AVI_MAGIC:
        return "video/x-msvideo"

    return None


def validate_video(
    data: bytes,
    mime_type: str,
    max_size_bytes: int = VIDEO_MAX_SIZE_BYTES,
) -> Tuple[str, int]:
    """Validate video data for C2PA signing.

    Args:
        data: Raw video file bytes.
        mime_type: Declared MIME type string.
        max_size_bytes: Maximum allowed file size.

    Returns:
        Tuple of (canonical_mime_type, file_size_bytes).

    Raises:
        ValueError: If the video file is invalid, too large, or has an
                    unsupported MIME type.
    """
    if not data:
        raise ValueError("Video data is empty")

    size = len(data)
    if size > max_size_bytes:
        raise ValueError(f"Video size {size} bytes exceeds maximum of {max_size_bytes} bytes")

    canonical = canonicalize_mime_type(mime_type)
    if canonical not in SUPPORTED_VIDEO_MIME_TYPES:
        raise ValueError(f"Unsupported video MIME type: {mime_type!r}. Supported: {sorted(SUPPORTED_VIDEO_MIME_TYPES)}")

    detected = detect_video_format(data)
    if detected is not None:
        # ISO BMFF family: ftyp-detected video may be declared as mp4, quicktime, or x-m4v
        if detected == "video/mp4" and canonical in _ISO_BMFF_CANONICAL_MIMES:
            pass  # all ISO BMFF family -- not a mismatch
        elif detected != canonical:
            raise ValueError(f"MIME type mismatch: declared {mime_type!r} (canonical: {canonical}) but file magic bytes indicate {detected!r}")

    if detected is None:
        logger.warning(
            "Could not detect video format from magic bytes for declared type %s; proceeding with declared type",
            mime_type,
        )

    return canonical, size


def compute_video_phash(data: bytes) -> int:
    """Compute a perceptual hash for a video file.

    Extracts the first video frame via ffmpeg, then computes an 8x8
    average perceptual hash (64-bit) using imagehash. Returns a signed
    int64 for PostgreSQL BIGINT compatibility.

    Returns 0 on any failure (matches image_utils.compute_phash behavior).
    """
    if not data:
        return 0

    input_path = ""
    frame_path = ""
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_in:
            tmp_in.write(data)
            input_path = tmp_in.name

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_out:
            frame_path = tmp_out.name

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                input_path,
                "-frames:v",
                "1",
                "-f",
                "image2",
                "-vcodec",
                "mjpeg",
                frame_path,
            ],
            capture_output=True,
            timeout=30,
        )

        if not os.path.exists(frame_path) or os.path.getsize(frame_path) == 0:
            return 0

        import imagehash
        from PIL import Image

        with Image.open(frame_path) as img:
            h = imagehash.average_hash(img, hash_size=8)

        unsigned = int(str(h), 16)
        if unsigned >= (1 << 63):
            return unsigned - (1 << 64)
        return unsigned

    except Exception:
        logger.debug("compute_video_phash failed, returning 0", exc_info=True)
        return 0
    finally:
        for path in (input_path, frame_path):
            if path:
                try:
                    os.unlink(path)
                except OSError:
                    pass
