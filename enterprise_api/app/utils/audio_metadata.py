"""Audio metadata injection/extraction for Encypher passthrough signing.

Embeds Encypher provenance fields into audio containers so that passthrough-
signed files carry recoverable attribution metadata. Mirrors the XMP injection
pattern used for images.

Supported formats:
- MP3: ID3v2 TXXX frames (ENCYPHER_INSTANCE_ID, ENCYPHER_ORG_ID, etc.)
- WAV: RIFF LIST/INFO chunk with Encypher key-value pairs
- M4A/AAC: not supported for injection (returns bytes unchanged)
"""

import json
import logging
import struct
from typing import Optional

logger = logging.getLogger(__name__)

_ENCYPHER_FIELDS = ("instance_id", "org_id", "document_id", "content_hash")


def inject_encypher_audio_metadata(
    audio_bytes: bytes,
    mime_type: str,
    instance_id: str,
    org_id: str,
    document_id: str,
    content_hash: str,
) -> bytes:
    """Inject Encypher provenance metadata into an audio file.

    Returns original bytes unchanged on unsupported formats or errors.
    """
    try:
        mt = mime_type.lower()
        if mt in ("audio/mpeg", "audio/mp3"):
            return _mp3_inject_id3(audio_bytes, instance_id, org_id, document_id, content_hash)
        elif mt in ("audio/wav", "audio/x-wav", "audio/wave"):
            return _wav_inject_riff(audio_bytes, instance_id, org_id, document_id, content_hash)
        else:
            return audio_bytes
    except Exception as exc:
        logger.warning("inject_encypher_audio_metadata failed, returning original: %s", exc)
        return audio_bytes


def extract_encypher_audio_metadata(audio_bytes: bytes, mime_type: str) -> Optional[dict]:
    """Extract Encypher provenance fields from an audio file.

    Returns None if not present or on error.
    """
    try:
        mt = mime_type.lower()
        if mt in ("audio/mpeg", "audio/mp3"):
            return _mp3_extract_id3(audio_bytes)
        elif mt in ("audio/wav", "audio/x-wav", "audio/wave"):
            return _wav_extract_riff(audio_bytes)
        else:
            return None
    except Exception as exc:
        logger.warning("extract_encypher_audio_metadata failed: %s", exc)
        return None


# ---------------------------------------------------------------------------
# MP3 / ID3v2 -- TXXX (user-defined text) frames
# ---------------------------------------------------------------------------

_ID3_TXXX_PREFIX = "ENCYPHER_"


def _make_txxx_frame(description: str, value: str) -> bytes:
    """Build an ID3v2.3 TXXX frame: encoding + description + NUL + value."""
    # Encoding byte 0x03 = UTF-8
    payload = b"\x03" + description.encode("utf-8") + b"\x00" + value.encode("utf-8")
    # Frame header: "TXXX" + 4-byte big-endian size + 2 flag bytes
    return b"TXXX" + struct.pack(">I", len(payload)) + b"\x00\x00" + payload


def _mp3_inject_id3(
    mp3_bytes: bytes,
    instance_id: str,
    org_id: str,
    document_id: str,
    content_hash: str,
) -> bytes:
    """Inject Encypher TXXX frames into an MP3's ID3v2 tag."""
    fields = {
        "ENCYPHER_INSTANCE_ID": instance_id,
        "ENCYPHER_ORG_ID": org_id,
        "ENCYPHER_DOCUMENT_ID": document_id,
        "ENCYPHER_CONTENT_HASH": content_hash,
        "ENCYPHER_VERIFY": "https://verify.encypher.com",
    }

    txxx_data = b""
    for desc, val in fields.items():
        txxx_data += _make_txxx_frame(desc, val)

    has_id3 = mp3_bytes[:3] == b"ID3"

    if has_id3:
        # Existing ID3v2 tag -- insert our frames after the header
        # ID3 header: "ID3" + 2 version bytes + 1 flag byte + 4 syncsafe size bytes
        if len(mp3_bytes) < 10:
            return mp3_bytes
        flags = mp3_bytes[5]
        old_size = _decode_syncsafe(mp3_bytes[6:10])
        # Skip extended header if present
        header_end = 10
        if flags & 0x40:  # extended header flag
            if len(mp3_bytes) >= 14:
                ext_size = _decode_syncsafe(mp3_bytes[10:14])
                header_end = 10 + ext_size

        # Insert our TXXX frames at the start of the frame area
        old_frames = mp3_bytes[header_end : 10 + old_size]
        new_frames = txxx_data + old_frames
        new_size = len(new_frames)
        new_header = mp3_bytes[:6] + _encode_syncsafe(new_size)
        return new_header + new_frames + mp3_bytes[10 + old_size :]
    else:
        # No ID3 tag -- prepend a new ID3v2.3 header
        new_size = len(txxx_data)
        id3_header = b"ID3" + b"\x03\x00" + b"\x00" + _encode_syncsafe(new_size)
        return id3_header + txxx_data + mp3_bytes


def _mp3_extract_id3(mp3_bytes: bytes) -> Optional[dict]:
    """Extract Encypher TXXX frames from an MP3's ID3v2 tag."""
    if mp3_bytes[:3] != b"ID3" or len(mp3_bytes) < 10:
        return None

    tag_size = _decode_syncsafe(mp3_bytes[6:10])
    tag_data = mp3_bytes[10 : 10 + tag_size]

    result = {}
    pos = 0
    while pos + 10 <= len(tag_data):
        frame_id = tag_data[pos : pos + 4]
        if frame_id == b"\x00\x00\x00\x00":
            break
        frame_size = struct.unpack(">I", tag_data[pos + 4 : pos + 8])[0]
        if frame_size == 0:
            break
        frame_data = tag_data[pos + 10 : pos + 10 + frame_size]
        pos += 10 + frame_size

        if frame_id != b"TXXX" or len(frame_data) < 2:
            continue

        encoding = frame_data[0]
        text_data = frame_data[1:]
        if encoding == 3:  # UTF-8
            parts = text_data.split(b"\x00", 1)
        elif encoding == 0:  # Latin-1
            parts = text_data.split(b"\x00", 1)
        else:
            continue

        if len(parts) != 2:
            continue
        desc = parts[0].decode("utf-8", errors="replace")
        value = parts[1].decode("utf-8", errors="replace")

        if desc.startswith(_ID3_TXXX_PREFIX):
            key = desc[len(_ID3_TXXX_PREFIX) :].lower()
            result[key] = value

    if not result:
        return None

    return result


def _decode_syncsafe(data: bytes) -> int:
    """Decode a 4-byte ID3v2 syncsafe integer."""
    return (data[0] << 21) | (data[1] << 14) | (data[2] << 7) | data[3]


def _encode_syncsafe(n: int) -> bytes:
    """Encode an integer as a 4-byte ID3v2 syncsafe integer."""
    return bytes(
        [
            (n >> 21) & 0x7F,
            (n >> 14) & 0x7F,
            (n >> 7) & 0x7F,
            n & 0x7F,
        ]
    )


# ---------------------------------------------------------------------------
# WAV / RIFF -- LIST/INFO chunk with Encypher metadata
# ---------------------------------------------------------------------------


def _wav_inject_riff(
    wav_bytes: bytes,
    instance_id: str,
    org_id: str,
    document_id: str,
    content_hash: str,
) -> bytes:
    """Inject an Encypher JSON comment chunk into a WAV RIFF container."""
    if wav_bytes[:4] != b"RIFF" or len(wav_bytes) < 12:
        return wav_bytes

    # Build a RIFF "ECPH" chunk containing JSON metadata
    metadata = json.dumps(
        {
            "instance_id": instance_id,
            "org_id": org_id,
            "document_id": document_id,
            "content_hash": content_hash,
            "verify": "https://verify.encypher.com",
        },
        separators=(",", ":"),
    ).encode("utf-8")

    # Pad to even length (RIFF requirement)
    if len(metadata) % 2 != 0:
        metadata += b"\x00"

    chunk = b"ECPH" + struct.pack("<I", len(metadata)) + metadata

    # Insert before the closing of the RIFF container
    # Update the RIFF size field (bytes 4-7, little-endian)
    old_riff_size = struct.unpack("<I", wav_bytes[4:8])[0]
    new_riff_size = old_riff_size + len(chunk)
    return wav_bytes[:4] + struct.pack("<I", new_riff_size) + wav_bytes[8:] + chunk


def _wav_extract_riff(wav_bytes: bytes) -> Optional[dict]:
    """Extract Encypher metadata from a WAV RIFF 'ECPH' chunk."""
    if wav_bytes[:4] != b"RIFF" or len(wav_bytes) < 12:
        return None

    pos = 12  # Skip RIFF header + WAVE type
    riff_end = 8 + struct.unpack("<I", wav_bytes[4:8])[0]

    while pos + 8 <= min(len(wav_bytes), riff_end):
        chunk_id = wav_bytes[pos : pos + 4]
        chunk_size = struct.unpack("<I", wav_bytes[pos + 4 : pos + 8])[0]

        if chunk_id == b"ECPH":
            chunk_data = wav_bytes[pos + 8 : pos + 8 + chunk_size]
            return json.loads(chunk_data.rstrip(b"\x00").decode("utf-8"))

        # Skip chunk (align to even boundary)
        pos += 8 + chunk_size
        if pos % 2 != 0:
            pos += 1

    return None
