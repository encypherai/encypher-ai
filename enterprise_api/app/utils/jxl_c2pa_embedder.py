"""C2PA manifest embedding for JPEG XL files in ISOBMFF container format.

Per C2PA spec, ISOBMFF-based formats store the manifest in a top-level box.
For JXL, we use a 'c2pa' box (4CC) containing the JUMBF manifest store.
Content binding uses c2pa.hash.data with an exclusion range covering the
manifest data bytes inside the c2pa box.

JXL has two container variants:
  - Bare codestream: starts with ff 0a -- NO box structure, CANNOT embed C2PA
  - ISOBMFF container: starts with 00 00 00 0c 4a 58 4c 20 0d 0a 87 0a
    followed by ftyp, jxlc/jxlp, and other ISOBMFF boxes

This embedder only supports the ISOBMFF container variant.

Two-pass approach:
  1. Append a 'c2pa' box with zero-filled placeholder at end of file
  2. Hash everything except the c2pa box data range
  3. Build and sign the manifest
  4. Replace placeholder with actual manifest bytes
"""

import hashlib
import logging
import struct

_log = logging.getLogger(__name__)

# JXL magic signatures
JXL_CONTAINER_SIGNATURE = b"\x00\x00\x00\x0cJXL \r\n\x87\n"
JXL_CODESTREAM_SIGNATURE = b"\xff\x0a"

# ISOBMFF box type for C2PA manifest store
C2PA_BOX_TYPE = b"c2pa"

# Standard ISOBMFF box header size
BOX_HEADER_SIZE = 8  # size(4) + type(4)


def _read_box_header(data: bytes, offset: int) -> tuple[int, bytes, int]:
    """Read an ISOBMFF box header at offset.

    Returns:
        Tuple of (box_size, box_type, header_size).
        box_size is the total box size including header.
        header_size is 8 for normal boxes, 16 for extended-size boxes.
    """
    if offset + 8 > len(data):
        raise ValueError(f"Not enough data for box header at offset {offset}")

    size = struct.unpack(">I", data[offset : offset + 4])[0]
    box_type = data[offset + 4 : offset + 8]

    if size == 1:
        # Extended size (64-bit)
        if offset + 16 > len(data):
            raise ValueError("Not enough data for extended box size")
        size = struct.unpack(">Q", data[offset + 8 : offset + 16])[0]
        return size, box_type, 16
    elif size == 0:
        # Box extends to end of data
        return len(data) - offset, box_type, 8
    else:
        return size, box_type, 8


def parse_jxl_boxes(data: bytes) -> list[dict]:
    """Parse top-level ISOBMFF boxes in a JXL container file.

    Returns:
        List of dicts with keys: offset, size, type, header_size, data_offset.
    """
    if len(data) < 12 or data[:12] != JXL_CONTAINER_SIGNATURE:
        if len(data) >= 2 and data[:2] == JXL_CODESTREAM_SIGNATURE:
            raise ValueError("JXL file is a bare codestream (no ISOBMFF container). " "C2PA embedding requires the ISOBMFF container variant.")
        raise ValueError("Not a valid JXL ISOBMFF container file")

    boxes = []
    offset = 0

    while offset < len(data):
        box_size, box_type, header_size = _read_box_header(data, offset)

        boxes.append(
            {
                "offset": offset,
                "size": box_size,
                "type": box_type,
                "header_size": header_size,
                "data_offset": offset + header_size,
            }
        )

        offset += box_size

    return boxes


def create_jxl_with_placeholder(jxl_bytes: bytes, placeholder_size: int = 32768) -> tuple[bytes, int, int]:
    """Append a C2PA box with zero-filled placeholder to a JXL container file.

    If a c2pa box already exists, it is removed first.

    Args:
        jxl_bytes: Original JXL container bytes.
        placeholder_size: Size of the zero-filled manifest placeholder.

    Returns:
        Tuple of (new_jxl_bytes, manifest_data_offset, manifest_data_length).
        The offset/length refer to the manifest data inside the c2pa box
        (after the 8-byte box header), which is the exclusion range.
    """
    boxes = parse_jxl_boxes(jxl_bytes)

    # Build new file: copy all boxes except existing c2pa, then append new c2pa
    result = bytearray()

    for box in boxes:
        if box["type"] == C2PA_BOX_TYPE:
            _log.debug("Removing existing c2pa box at offset %d", box["offset"])
            continue
        result.extend(jxl_bytes[box["offset"] : box["offset"] + box["size"]])

    # Append new c2pa box: header(8) + placeholder data
    c2pa_box_size = BOX_HEADER_SIZE + placeholder_size
    c2pa_header = struct.pack(">I", c2pa_box_size) + C2PA_BOX_TYPE

    manifest_data_offset = len(result) + BOX_HEADER_SIZE
    result.extend(c2pa_header)
    result.extend(b"\x00" * placeholder_size)

    return bytes(result), manifest_data_offset, placeholder_size


def compute_jxl_hash(
    jxl_bytes: bytes,
    exclusion_start: int,
    exclusion_length: int,
    alg: str = "sha256",
) -> bytes:
    """Compute hash of JXL bytes, excluding the manifest data range."""
    h = hashlib.new(alg)
    h.update(jxl_bytes[:exclusion_start])
    after = exclusion_start + exclusion_length
    if after < len(jxl_bytes):
        h.update(jxl_bytes[after:])
    return h.digest()


def replace_manifest_in_jxl(
    jxl_bytes: bytes,
    manifest_bytes: bytes,
    manifest_offset: int,
    manifest_length: int,
) -> bytes:
    """Replace the placeholder manifest data with actual manifest bytes.

    Args:
        jxl_bytes: JXL bytes containing the zero-filled placeholder.
        manifest_bytes: Actual C2PA manifest store bytes (JUMBF).
        manifest_offset: Byte offset of the manifest data in the file.
        manifest_length: Length of the placeholder region.

    Returns:
        Updated JXL bytes with manifest embedded.

    Raises:
        ValueError: If manifest is larger than the placeholder.
    """
    if len(manifest_bytes) > manifest_length:
        raise ValueError(f"Manifest ({len(manifest_bytes)} bytes) exceeds placeholder " f"({manifest_length} bytes). Retry with larger placeholder.")

    # Pad to fill the placeholder exactly
    padded = manifest_bytes + b"\x00" * (manifest_length - len(manifest_bytes))
    return jxl_bytes[:manifest_offset] + padded + jxl_bytes[manifest_offset + manifest_length :]
