"""Video metadata injection/extraction for Encypher passthrough signing.

Embeds Encypher provenance fields into video containers so that passthrough-
signed files carry recoverable attribution metadata. Mirrors the XMP injection
pattern used for images.

Supported formats:
- MP4/MOV/M4V (ISO BMFF): 'uuid' box with Encypher JSON payload
- AVI (RIFF): same ECPH chunk strategy as WAV
"""

import json
import logging
import struct
import uuid as uuid_mod
from typing import Optional

logger = logging.getLogger(__name__)

# Encypher UUID for the BMFF uuid box (deterministic, derived from namespace)
_ENCYPHER_UUID = uuid_mod.uuid5(uuid_mod.NAMESPACE_URL, "https://encypher.ai/schemas/v1/media").bytes  # 16 bytes


def inject_encypher_video_metadata(
    video_bytes: bytes,
    mime_type: str,
    instance_id: str,
    org_id: str,
    document_id: str,
    content_hash: str,
) -> bytes:
    """Inject Encypher provenance metadata into a video file.

    Returns original bytes unchanged on unsupported formats or errors.
    """
    try:
        mt = mime_type.lower()
        if mt in ("video/mp4", "video/quicktime", "video/x-m4v"):
            return _bmff_inject_uuid_box(video_bytes, instance_id, org_id, document_id, content_hash)
        elif mt in ("video/x-msvideo", "video/avi"):
            return _avi_inject_riff(video_bytes, instance_id, org_id, document_id, content_hash)
        else:
            return video_bytes
    except Exception as exc:
        logger.warning("inject_encypher_video_metadata failed, returning original: %s", exc)
        return video_bytes


def extract_encypher_video_metadata(video_bytes: bytes, mime_type: str) -> Optional[dict]:
    """Extract Encypher provenance fields from a video file.

    Returns None if not present or on error.
    """
    try:
        mt = mime_type.lower()
        if mt in ("video/mp4", "video/quicktime", "video/x-m4v"):
            return _bmff_extract_uuid_box(video_bytes)
        elif mt in ("video/x-msvideo", "video/avi"):
            return _avi_extract_riff(video_bytes)
        else:
            return None
    except Exception as exc:
        logger.warning("extract_encypher_video_metadata failed: %s", exc)
        return None


# ---------------------------------------------------------------------------
# ISO BMFF (MP4/MOV/M4V) -- uuid box with Encypher JSON payload
# ---------------------------------------------------------------------------


def _build_metadata_json(instance_id: str, org_id: str, document_id: str, content_hash: str) -> bytes:
    return json.dumps(
        {
            "instance_id": instance_id,
            "org_id": org_id,
            "document_id": document_id,
            "content_hash": content_hash,
            "verify": "https://verify.encypherai.com",
        },
        separators=(",", ":"),
    ).encode("utf-8")


def _bmff_inject_uuid_box(
    mp4_bytes: bytes,
    instance_id: str,
    org_id: str,
    document_id: str,
    content_hash: str,
) -> bytes:
    """Append an Encypher uuid box to an ISO BMFF container."""
    payload = _build_metadata_json(instance_id, org_id, document_id, content_hash)

    # uuid box: 4-byte size (big-endian) + "uuid" + 16-byte UUID + payload
    box_size = 8 + 16 + len(payload)
    uuid_box = struct.pack(">I", box_size) + b"uuid" + _ENCYPHER_UUID + payload

    return mp4_bytes + uuid_box


def _bmff_extract_uuid_box(mp4_bytes: bytes) -> Optional[dict]:
    """Scan top-level BMFF boxes for our Encypher uuid box."""
    pos = 0
    while pos + 8 <= len(mp4_bytes):
        box_size = struct.unpack(">I", mp4_bytes[pos : pos + 4])[0]
        box_type = mp4_bytes[pos + 4 : pos + 8]

        if box_size < 8:
            break

        if box_type == b"uuid" and pos + 24 <= len(mp4_bytes):
            box_uuid = mp4_bytes[pos + 8 : pos + 24]
            if box_uuid == _ENCYPHER_UUID:
                payload = mp4_bytes[pos + 24 : pos + box_size]
                return json.loads(payload.decode("utf-8"))

        pos += box_size

    return None


# ---------------------------------------------------------------------------
# AVI (RIFF) -- ECPH chunk (same as WAV strategy)
# ---------------------------------------------------------------------------


def _avi_inject_riff(
    avi_bytes: bytes,
    instance_id: str,
    org_id: str,
    document_id: str,
    content_hash: str,
) -> bytes:
    """Inject an Encypher JSON chunk into an AVI RIFF container."""
    if avi_bytes[:4] != b"RIFF" or len(avi_bytes) < 12:
        return avi_bytes

    metadata = _build_metadata_json(instance_id, org_id, document_id, content_hash)
    if len(metadata) % 2 != 0:
        metadata += b"\x00"

    chunk = b"ECPH" + struct.pack("<I", len(metadata)) + metadata

    old_riff_size = struct.unpack("<I", avi_bytes[4:8])[0]
    new_riff_size = old_riff_size + len(chunk)
    return avi_bytes[:4] + struct.pack("<I", new_riff_size) + avi_bytes[8:] + chunk


def _avi_extract_riff(avi_bytes: bytes) -> Optional[dict]:
    """Extract Encypher metadata from an AVI RIFF 'ECPH' chunk."""
    if avi_bytes[:4] != b"RIFF" or len(avi_bytes) < 12:
        return None

    pos = 12
    riff_end = 8 + struct.unpack("<I", avi_bytes[4:8])[0]

    while pos + 8 <= min(len(avi_bytes), riff_end):
        chunk_id = avi_bytes[pos : pos + 4]
        chunk_size = struct.unpack("<I", avi_bytes[pos + 4 : pos + 8])[0]

        if chunk_id == b"ECPH":
            chunk_data = avi_bytes[pos + 8 : pos + 8 + chunk_size]
            return json.loads(chunk_data.rstrip(b"\x00").decode("utf-8"))

        pos += 8 + chunk_size
        if pos % 2 != 0:
            pos += 1

    return None
