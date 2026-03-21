"""Image utility functions for the C2PA image signing pipeline.

Provides: validation, EXIF extraction/stripping, pHash computation,
SHA-256 hashing, thumbnail resizing, and XMP provenance injection/extraction.
"""

import logging
import secrets
import struct
import xml.etree.ElementTree as ET
import zlib
from io import BytesIO
from html import escape as _html_escape
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# Supported MIME types for image signing
SUPPORTED_MIME_TYPES = frozenset(
    {
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/webp",
        "image/tiff",
        "image/heic",
    }
)

MIME_TO_PIL_FORMAT = {
    "image/jpeg": "JPEG",
    "image/jpg": "JPEG",
    "image/png": "PNG",
    "image/webp": "WEBP",
    "image/tiff": "TIFF",
    "image/heic": "HEIC",
}

# Maximum image size: 10 MB
IMAGE_MAX_SIZE_BYTES = 10 * 1024 * 1024


def validate_image(data: bytes, mime_type: str, max_size_bytes: int = IMAGE_MAX_SIZE_BYTES) -> Tuple[int, int, str]:
    """
    Validate image data and return (width, height, format).

    Args:
        data: Raw image bytes.
        mime_type: MIME type string, e.g. "image/jpeg".

    Returns:
        Tuple of (width_px, height_px, pil_format_string).

    Raises:
        ValueError: If the image exceeds the size limit, has an unsupported
                    MIME type, or cannot be decoded by Pillow.
    """
    if len(data) > max_size_bytes:
        raise ValueError(f"Image size {len(data)} bytes exceeds maximum of {max_size_bytes} bytes")
    if mime_type not in SUPPORTED_MIME_TYPES:
        raise ValueError(f"Unsupported MIME type: {mime_type!r}. Supported types: {sorted(SUPPORTED_MIME_TYPES)}")
    try:
        from PIL import Image

        with Image.open(BytesIO(data)) as img:
            width, height = img.size
            fmt = img.format or "UNKNOWN"
    except Exception as exc:
        raise ValueError(f"Cannot decode image: {exc}") from exc
    return width, height, fmt


def extract_exif(data: bytes) -> Dict:
    """
    Extract EXIF metadata from image bytes.

    Returns a flat dict of tag name -> value. Empty dict if no EXIF present
    or piexif is not installed.
    """
    try:
        import piexif

        exif_bytes = piexif.load(data)
        result: Dict = {}
        tag_map = {
            "0th": piexif.ImageIFD,
            "Exif": piexif.ExifIFD,
            "GPS": piexif.GPSIFD,
        }
        for ifd_name, ifd_tags in tag_map.items():
            ifd_data = exif_bytes.get(ifd_name, {})
            if not isinstance(ifd_data, dict):
                continue
            for tag_id, value in ifd_data.items():
                tag_name = piexif.TAGS.get(ifd_name, {}).get(tag_id, {}).get("name", str(tag_id))
                # Decode bytes to string for JSON serialization
                if isinstance(value, bytes):
                    try:
                        value = value.decode("utf-8", errors="replace")
                    except Exception:
                        value = repr(value)
                result[tag_name] = value
        return result
    except Exception:
        return {}


def strip_exif(data: bytes, mime_type: Optional[str] = None, quality: int = 95) -> bytes:
    """
    Strip EXIF metadata from image bytes (GPS, device PII removal).

    Re-encodes with Pillow to drop any EXIF payload. Returns clean image bytes.

    Args:
        data: Raw image bytes.
        mime_type: Optional MIME type hint (e.g. "image/jpeg"). When not provided,
                   the format is inferred from the image data.
        quality: JPEG/WebP re-encode quality (1-100, default 95).
    """
    try:
        from PIL import Image

        with Image.open(BytesIO(data)) as img:
            detected_fmt = img.format or "JPEG"
            buf = BytesIO()
            # Determine output format from mime_type or detected format
            if mime_type:
                pil_fmt = MIME_TO_PIL_FORMAT.get(mime_type.lower(), detected_fmt)
            else:
                pil_fmt = detected_fmt
            save_kwargs: Dict = {"format": pil_fmt}
            if pil_fmt.upper() in ("JPEG", "JPG"):
                save_kwargs["format"] = "JPEG"
                save_kwargs["quality"] = quality
            elif pil_fmt.upper() == "WEBP":
                save_kwargs["quality"] = quality
            img.save(buf, **save_kwargs)
        return buf.getvalue()
    except Exception as exc:
        logger.warning("strip_exif failed, returning original bytes: %s", exc)
        return data


def compute_phash(data: bytes) -> int:
    """
    Compute perceptual hash (average hash) of image bytes.

    Uses imagehash.average_hash on a Pillow-decoded image.
    Returns a signed int64 value (matching the BIGINT column).
    Returns 0 if computation fails.

    Args:
        data: Raw image bytes.

    Returns:
        Signed 64-bit integer pHash, or 0 on failure.
    """
    try:
        import imagehash
        from PIL import Image

        with Image.open(BytesIO(data)) as img:
            h = imagehash.average_hash(img, hash_size=8)  # 8x8 = 64 bits

        # imagehash returns a hash object; convert to int via its hex string.
        unsigned = int(str(h), 16)
        # Convert to signed int64 for PostgreSQL BIGINT compatibility
        if unsigned >= (1 << 63):
            return unsigned - (1 << 64)
        return unsigned
    except Exception as exc:
        logger.warning("pHash computation failed: %s", exc)
        return 0


# Re-export from shared module for backward compatibility
from app.utils.hashing import compute_sha256  # noqa: F811, E402


def resize_for_thumbnail(data: bytes, max_px: int = 256) -> bytes:
    """
    Resize image so its longest side is at most max_px pixels.

    Returns JPEG bytes of the thumbnail.

    Args:
        data: Raw image bytes.
        max_px: Maximum dimension in pixels (default 256).

    Returns:
        JPEG bytes of the resized image.
    """
    try:
        from PIL import Image

        with Image.open(BytesIO(data)) as img:
            # Pillow 10+ uses Image.Resampling.LANCZOS; older versions use Image.LANCZOS
            _resampling = getattr(Image, "Resampling", None)
            resample = _resampling.LANCZOS if _resampling else Image.LANCZOS  # type: ignore[attr-defined]
            img.thumbnail((max_px, max_px), resample)
            buf = BytesIO()
            img.save(buf, format="JPEG", quality=85)
        return buf.getvalue()
    except Exception as exc:
        raise ValueError(f"Cannot create thumbnail: {exc}") from exc


def generate_image_id() -> str:
    """Generate a unique image ID in the format img_xxxxxxxx (8 random hex chars)."""
    return "img_" + secrets.token_hex(4)


# ---------------------------------------------------------------------------
# XMP provenance injection / extraction (ISO 16684)
# ---------------------------------------------------------------------------

_XMP_NS = "https://encypher.ai/schemas/v1"
_XMP_NS_PREFIX = "ency"
_XMP_VERIFY_URL = "https://verify.encypher.ai/"
_JPEG_XMP_HEADER = b"http://ns.adobe.com/xap/1.0/\x00"  # 29 bytes
_XMP_PACKET_BEGIN = "<?xpacket begin='\xef\xbb\xbf' id='W5M0MpCehiHzreSzNTczkc9d'?>"
_XMP_PACKET_END = "<?xpacket end='r'?>"


def _xml_attr_escape(value: str) -> str:
    """Escape a string for safe inclusion in an XML attribute value."""
    return _html_escape(value, quote=True)


def _build_xmp_packet(
    instance_id: str,
    org_id: str,
    document_id: str,
    image_hash: str,
) -> bytes:
    """Return UTF-8 XMP packet bytes with Encypher provenance fields."""
    esc_instance_id = _xml_attr_escape(instance_id)
    esc_org_id = _xml_attr_escape(org_id)
    esc_document_id = _xml_attr_escape(document_id)
    esc_image_hash = _xml_attr_escape(image_hash)
    xmp = (
        f"{_XMP_PACKET_BEGIN}\n"
        "<x:xmpmeta xmlns:x='adobe:ns:meta/'>\n"
        "<rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'>\n"
        "<rdf:Description rdf:about=''\n"
        f"  xmlns:{_XMP_NS_PREFIX}='{_XMP_NS}'\n"
        f"  {_XMP_NS_PREFIX}:instance_id='{esc_instance_id}'\n"
        f"  {_XMP_NS_PREFIX}:org_id='{esc_org_id}'\n"
        f"  {_XMP_NS_PREFIX}:document_id='{esc_document_id}'\n"
        f"  {_XMP_NS_PREFIX}:image_hash='{esc_image_hash}'\n"
        f"  {_XMP_NS_PREFIX}:verify='{_XMP_VERIFY_URL}'\n"
        "/>\n"
        "</rdf:RDF>\n"
        "</x:xmpmeta>\n"
        f"{_XMP_PACKET_END}"
    )
    return xmp.encode("utf-8")


def inject_encypher_xmp(
    image_bytes: bytes,
    mime_type: str,
    instance_id: str,
    org_id: str,
    document_id: str,
    image_hash: str,
) -> bytes:
    """Inject Encypher provenance XMP into an image. Returns original on error."""
    try:
        xmp_data = _build_xmp_packet(instance_id, org_id, document_id, image_hash)
        mt = mime_type.lower()
        if mt in ("image/jpeg", "image/jpg"):
            return _jpeg_inject_xmp(image_bytes, xmp_data)
        elif mt == "image/png":
            return _png_inject_xmp(image_bytes, xmp_data)
        else:
            return image_bytes  # WebP/TIFF: return unchanged
    except Exception as exc:
        logger.warning("inject_encypher_xmp failed, returning original: %s", exc)
        return image_bytes


def extract_encypher_xmp(image_bytes: bytes, mime_type: str) -> Optional[dict]:
    """Extract Encypher XMP fields. Returns None if not present or on error."""
    try:
        mt = mime_type.lower()
        if mt in ("image/jpeg", "image/jpg"):
            xmp_data = _jpeg_extract_xmp(image_bytes)
        elif mt == "image/png":
            xmp_data = _png_extract_xmp(image_bytes)
        else:
            return None
        if xmp_data is None:
            return None
        return _parse_encypher_xmp(xmp_data)
    except Exception as exc:
        logger.warning("extract_encypher_xmp failed: %s", exc)
        return None


def _jpeg_inject_xmp(jpeg_bytes: bytes, xmp_data: bytes) -> bytes:
    """Insert XMP APP1 segment after SOI, before existing segments."""
    if jpeg_bytes[:2] != b"\xff\xd8":
        raise ValueError("Not a JPEG")
    payload = _JPEG_XMP_HEADER + xmp_data
    seg_len = len(payload) + 2  # +2 for the length field itself
    app1_seg = b"\xff\xe1" + struct.pack(">H", seg_len) + payload
    return jpeg_bytes[:2] + app1_seg + jpeg_bytes[2:]


def _jpeg_extract_xmp(jpeg_bytes: bytes) -> Optional[bytes]:
    """Extract XMP packet bytes from a JPEG, or None if absent."""
    i = 2  # skip SOI
    while i < len(jpeg_bytes) - 1:
        if jpeg_bytes[i] != 0xFF:
            break
        marker = jpeg_bytes[i : i + 2]
        if marker == b"\xff\xda":  # SOS - no more segments
            break
        if i + 4 > len(jpeg_bytes):
            break
        seg_len = struct.unpack(">H", jpeg_bytes[i + 2 : i + 4])[0]
        seg_data = jpeg_bytes[i + 4 : i + 2 + seg_len]
        if marker == b"\xff\xe1" and seg_data.startswith(_JPEG_XMP_HEADER):
            return seg_data[len(_JPEG_XMP_HEADER) :]
        i += 2 + seg_len
    return None


def _png_inject_xmp(png_bytes: bytes, xmp_data: bytes) -> bytes:
    """Insert iTXt XMP chunk after IHDR."""
    sig = b"\x89PNG\r\n\x1a\n"
    if png_bytes[:8] != sig:
        raise ValueError("Not a PNG")
    # IHDR always at offset 8: 4(len)+4(type)+13(data)+4(CRC) = 25 bytes -> end at 33
    ihdr_end = 8 + 4 + 4 + 13 + 4  # = 33
    # keyword\0 comp_flag comp_method lang\0 trans_kw\0
    keyword = b"XML:com.adobe.xmp\x00\x00\x00\x00\x00"
    chunk_data = keyword + xmp_data
    crc = zlib.crc32(b"iTXt" + chunk_data) & 0xFFFFFFFF
    itxt_chunk = struct.pack(">I", len(chunk_data)) + b"iTXt" + chunk_data + struct.pack(">I", crc)
    return png_bytes[:ihdr_end] + itxt_chunk + png_bytes[ihdr_end:]


def _png_extract_xmp(png_bytes: bytes) -> Optional[bytes]:
    """Extract XMP from PNG iTXt chunk, or None if absent."""
    i = 8  # skip PNG signature
    while i + 8 <= len(png_bytes):
        length = struct.unpack(">I", png_bytes[i : i + 4])[0]
        chunk_type = png_bytes[i + 4 : i + 8]
        chunk_data = png_bytes[i + 8 : i + 8 + length]
        if chunk_type == b"iTXt" and chunk_data.startswith(b"XML:com.adobe.xmp\x00"):
            # skip: keyword(18) + \0(1) + comp_flag(1) + comp_method(1) + lang\0(1) + trans_kw\0(1) = 23
            return chunk_data[23:]
        if chunk_type == b"IEND":
            break
        i += 4 + 4 + length + 4  # len + type + data + CRC
    return None


def _parse_encypher_xmp(xmp_bytes: bytes) -> Optional[dict]:
    """Parse XMP XML and return Encypher namespace fields as dict."""
    try:
        root = ET.fromstring(xmp_bytes.decode("utf-8", errors="replace"))
    except ET.ParseError:
        # Strip xpacket wrappers and retry
        text = xmp_bytes.decode("utf-8", errors="replace")
        start = text.find("<x:xmpmeta")
        end = text.find("</x:xmpmeta>")
        if start == -1 or end == -1:
            return None
        root = ET.fromstring(text[start : end + 12])

    ns_prefix = f"{{{_XMP_NS}}}"
    result: dict = {}
    for elem in root.iter():
        for attr_name, attr_val in elem.attrib.items():
            if attr_name.startswith(ns_prefix):
                key = attr_name[len(ns_prefix) :]
                result[key] = attr_val
    return result if result else None
