"""SSOT registry of supported image formats for C2PA signing.

Three-tier architecture:
  Tier A -- Pillow native: JPEG, PNG, WebP, TIFF, GIF
  Tier B -- Plugin-backed: HEIC, HEIF, HEIC-sequence, HEIF-sequence, AVIF
  Tier C -- Bypass (magic-byte validation only): SVG, JXL, DNG
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, FrozenSet, Optional, Sequence


class FormatTier(str, Enum):
    A = "pillow_native"
    B = "plugin_backed"
    C = "bypass"


@dataclass(frozen=True)
class ImageFormat:
    mime_type: str
    tier: FormatTier
    pil_format: Optional[str]  # None for Tier C
    supports_exif_strip: bool
    extensions: tuple


# ---- Format definitions ----

_FORMATS: Sequence[ImageFormat] = (
    # Tier A -- Pillow native
    ImageFormat("image/jpeg", FormatTier.A, "JPEG", True, (".jpg", ".jpeg")),
    ImageFormat("image/png", FormatTier.A, "PNG", True, (".png",)),
    ImageFormat("image/webp", FormatTier.A, "WEBP", True, (".webp",)),
    ImageFormat("image/tiff", FormatTier.A, "TIFF", True, (".tiff", ".tif")),
    ImageFormat("image/gif", FormatTier.A, "GIF", True, (".gif",)),
    # Tier B -- Plugin-backed (pillow-heif, Pillow native AVIF)
    ImageFormat("image/heic", FormatTier.B, "HEIF", True, (".heic",)),
    ImageFormat("image/heif", FormatTier.B, "HEIF", True, (".heif",)),
    ImageFormat("image/heic-sequence", FormatTier.B, "HEIF", True, (".heics",)),
    ImageFormat("image/heif-sequence", FormatTier.B, "HEIF", True, (".heifs",)),
    ImageFormat("image/avif", FormatTier.B, "AVIF", True, (".avif",)),
    # Tier C -- Bypass (magic-byte validation, no Pillow)
    ImageFormat("image/svg+xml", FormatTier.C, None, False, (".svg",)),
    # JXL: magic-byte validation only. c2pa-rs 0.78.4 does not support JXL signing;
    # image_signing_service.py rejects image/jxl before calling c2pa.Builder.sign().
    # Kept here so validate_image() can confirm a JXL magic signature is present
    # (useful for the verify endpoint and format detection).
    ImageFormat("image/jxl", FormatTier.C, None, False, (".jxl",)),
    ImageFormat("image/x-adobe-dng", FormatTier.C, None, False, (".dng",)),
)

# ---- Lookup tables ----

FORMAT_BY_MIME: Dict[str, ImageFormat] = {fmt.mime_type: fmt for fmt in _FORMATS}

# Alias: image/jpg -> image/jpeg
FORMAT_BY_MIME["image/jpg"] = FORMAT_BY_MIME["image/jpeg"]

SUPPORTED_IMAGE_MIME_TYPES: FrozenSet[str] = frozenset(FORMAT_BY_MIME.keys())

# Canonical MIME type mapping for c2pa-python Builder.sign().
# Animated HEIF/HEIC sequence variants use the same ISO BMFF container as
# their still-image counterparts; c2pa-rs accepts the base type for both.
_CANONICAL_MIME: Dict[str, str] = {
    "image/heic-sequence": "image/heic",
    "image/heif-sequence": "image/heif",
}


def canonicalize_mime_type(mime_type: str) -> str:
    """Normalize an image MIME type to the canonical form accepted by c2pa-python.

    Currently maps animated sequence variants to their still-image base types:
      image/heic-sequence -> image/heic
      image/heif-sequence -> image/heif

    All other MIME types are returned unchanged.
    """
    return _CANONICAL_MIME.get(mime_type.lower().strip(), mime_type)


MIME_TO_PIL_FORMAT: Dict[str, str] = {mime: fmt.pil_format for mime, fmt in FORMAT_BY_MIME.items() if fmt.pil_format}


def is_pillow_format(mime_type: str) -> bool:
    """Return True if the format can be opened by Pillow (Tier A or B)."""
    fmt = FORMAT_BY_MIME.get(mime_type)
    return fmt is not None and fmt.tier in (FormatTier.A, FormatTier.B)


def is_bypass_format(mime_type: str) -> bool:
    """Return True if the format bypasses Pillow (Tier C)."""
    fmt = FORMAT_BY_MIME.get(mime_type)
    return fmt is not None and fmt.tier == FormatTier.C


def supports_exif_strip(mime_type: str) -> bool:
    """Return True if EXIF stripping is supported for this format."""
    fmt = FORMAT_BY_MIME.get(mime_type)
    return fmt is not None and fmt.supports_exif_strip


def get_tier(mime_type: str) -> Optional[FormatTier]:
    """Return the tier for a MIME type, or None if unsupported."""
    fmt = FORMAT_BY_MIME.get(mime_type)
    return fmt.tier if fmt else None


# ---- Magic byte signatures for Tier C ----

# SVG: starts with XML declaration or <svg tag (with optional BOM)
SVG_SIGNATURES = (b"<?xml", b"<svg", b"\xef\xbb\xbf<?xml", b"\xef\xbb\xbf<svg")

# DNG: TIFF-structured -- little-endian or big-endian header
DNG_TIFF_LE = b"II\x2a\x00"
DNG_TIFF_BE = b"MM\x00\x2a"

# JXL: naked codestream or ISO BMFF container
JXL_CODESTREAM = b"\xff\x0a"
JXL_CONTAINER = b"\x00\x00\x00\x0cJXL \r\n\x87\n"


def validate_magic_bytes(data: bytes, mime_type: str) -> None:
    """Validate Tier C format via magic byte signatures.

    Raises ValueError if the data does not match the declared MIME type.
    """
    if mime_type == "image/svg+xml":
        # Strip leading whitespace for detection
        stripped = data.lstrip()
        if not any(stripped.startswith(sig) for sig in SVG_SIGNATURES):
            raise ValueError("Data does not appear to be a valid SVG document")
        return

    if mime_type == "image/x-adobe-dng":
        if len(data) < 4:
            raise ValueError("Data too short for DNG")
        header = data[:4]
        if header not in (DNG_TIFF_LE, DNG_TIFF_BE):
            raise ValueError("Data does not have a valid TIFF/DNG header")
        return

    if mime_type == "image/jxl":
        if len(data) < 2:
            raise ValueError("Data too short for JXL")
        if not (data[:2] == JXL_CODESTREAM or data[:12] == JXL_CONTAINER):
            raise ValueError("Data does not have a valid JPEG XL signature")
        return

    raise ValueError(f"No magic byte validation for MIME type: {mime_type}")


def ensure_heif_plugin() -> None:
    """Register pillow-heif opener if available. Safe to call multiple times."""
    try:
        import pillow_heif

        pillow_heif.register_heif_opener()
    except ImportError:
        pass
