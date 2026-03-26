"""C2PA manifest embedding for FLAC audio files.

Per C2PA spec, the manifest is stored in a FLAC APPLICATION metadata block
with application ID "c2pa" (0x63327061). Content binding uses c2pa.hash.data
with an exclusion range covering the manifest data bytes.

FLAC structure:
  Magic: "fLaC" (4 bytes)
  Metadata blocks: [is_last(1 bit) | type(7 bits) | length(24 bits)] + data
    Type 0: STREAMINFO (required, always first)
    Type 2: APPLICATION (used for C2PA manifest)
  Audio frames follow after all metadata blocks.

Two-pass approach:
  1. Insert APPLICATION block with zero-filled placeholder after STREAMINFO
  2. Hash everything except the manifest data range
  3. Build and sign the manifest
  4. Replace placeholder with actual manifest bytes
"""

import hashlib
import logging
import struct

_log = logging.getLogger(__name__)

FLAC_MAGIC = b"fLaC"
BLOCK_TYPE_STREAMINFO = 0
BLOCK_TYPE_APPLICATION = 2
C2PA_APP_ID = b"c2pa"  # 0x63327061


def _parse_metadata_blocks(data: bytes) -> list[dict]:
    """Parse FLAC metadata blocks (does not parse audio frames).

    Returns:
        List of dicts with keys: offset, header_offset, type, is_last,
        length, data_offset (offset of block data after header).
    """
    if len(data) < 4 or data[:4] != FLAC_MAGIC:
        raise ValueError("Not a valid FLAC file (missing fLaC magic)")

    blocks = []
    pos = 4  # skip magic

    while pos < len(data):
        if pos + 4 > len(data):
            raise ValueError("Truncated metadata block header")

        header_byte = data[pos]
        is_last = bool(header_byte & 0x80)
        block_type = header_byte & 0x7F
        length = struct.unpack(">I", b"\x00" + data[pos + 1 : pos + 4])[0]

        blocks.append(
            {
                "header_offset": pos,
                "type": block_type,
                "is_last": is_last,
                "length": length,
                "data_offset": pos + 4,
            }
        )

        pos += 4 + length

        if is_last:
            break

    return blocks


def create_flac_with_placeholder(flac_bytes: bytes, placeholder_size: int = 32768) -> tuple[bytes, int, int]:
    """Insert a C2PA APPLICATION block with zero-filled placeholder.

    The block is inserted immediately after STREAMINFO. The is_last flag
    on the preceding block is cleared, and the new block is marked is_last
    only if it's the final metadata block.

    Args:
        flac_bytes: Original FLAC file bytes.
        placeholder_size: Size of the zero-filled manifest placeholder.

    Returns:
        Tuple of (new_flac_bytes, manifest_data_offset, manifest_data_length).
        The offset/length refer to the manifest data inside the APPLICATION
        block (after the 4-byte app ID), which is the exclusion range.
    """
    blocks = _parse_metadata_blocks(flac_bytes)
    if not blocks or blocks[0]["type"] != BLOCK_TYPE_STREAMINFO:
        raise ValueError("First metadata block must be STREAMINFO")

    # Remove any existing C2PA APPLICATION block
    existing_c2pa = [b for b in blocks if b["type"] == BLOCK_TYPE_APPLICATION and flac_bytes[b["data_offset"] : b["data_offset"] + 4] == C2PA_APP_ID]

    # Find insertion point: right after STREAMINFO
    streaminfo = blocks[0]
    insert_after_offset = streaminfo["data_offset"] + streaminfo["length"]

    # Build the new APPLICATION block
    # Block data = app_id(4) + manifest_placeholder(placeholder_size)
    app_block_data_len = 4 + placeholder_size

    # Determine is_last: the C2PA block is last if STREAMINFO was last
    # (i.e., no other blocks follow). If other blocks exist, keep their
    # is_last flags and insert C2PA as non-last.
    remaining_blocks = [b for b in blocks[1:] if b not in existing_c2pa]

    if not remaining_blocks:
        # Only STREAMINFO existed -- C2PA block becomes the last
        c2pa_is_last = True
    else:
        c2pa_is_last = False

    # Build new C2PA block header: is_last=0 (or 1), type=2, length=app_block_data_len
    c2pa_header_byte = BLOCK_TYPE_APPLICATION & 0x7F
    if c2pa_is_last and not remaining_blocks:
        c2pa_header_byte |= 0x80
    c2pa_header = bytes([c2pa_header_byte]) + struct.pack(">I", app_block_data_len)[1:]
    c2pa_block = c2pa_header + C2PA_APP_ID + (b"\x00" * placeholder_size)

    # Rebuild the file
    result = bytearray()

    # 1. Copy magic
    result.extend(FLAC_MAGIC)

    # 2. Copy STREAMINFO with is_last cleared (since C2PA block follows)
    si_header = bytearray(flac_bytes[streaminfo["header_offset"] : streaminfo["header_offset"] + 4])
    si_header[0] &= 0x7F  # clear is_last bit
    result.extend(si_header)
    result.extend(flac_bytes[streaminfo["data_offset"] : streaminfo["data_offset"] + streaminfo["length"]])

    # 3. Insert C2PA APPLICATION block
    c2pa_block_offset = len(result)
    result.extend(c2pa_block)

    # The manifest data starts after header(4) + app_id(4)
    manifest_data_offset = c2pa_block_offset + 4 + 4  # header + app_id
    manifest_data_length = placeholder_size

    # 4. Copy remaining metadata blocks (if any), preserving their is_last flags
    for i, blk in enumerate(remaining_blocks):
        blk_start = blk["header_offset"]
        blk_end = blk["data_offset"] + blk["length"]
        blk_bytes = bytearray(flac_bytes[blk_start:blk_end])

        if c2pa_is_last:
            # Shouldn't happen (remaining_blocks is empty if c2pa_is_last)
            pass
        elif i == len(remaining_blocks) - 1:
            # Last remaining block gets is_last=1
            blk_bytes[0] |= 0x80
        else:
            blk_bytes[0] &= 0x7F

        result.extend(blk_bytes)

    # 5. Copy audio frames (everything after metadata)
    last_block = existing_c2pa[-1] if existing_c2pa else blocks[-1]
    # Find the actual end of all original metadata
    all_original = blocks
    audio_start = max(b["data_offset"] + b["length"] for b in all_original)
    if audio_start < len(flac_bytes):
        result.extend(flac_bytes[audio_start:])

    return bytes(result), manifest_data_offset, manifest_data_length


def compute_flac_hash(
    flac_bytes: bytes,
    exclusion_start: int,
    exclusion_length: int,
    alg: str = "sha256",
) -> bytes:
    """Compute hash of FLAC bytes, excluding the manifest data range."""
    h = hashlib.new(alg)
    h.update(flac_bytes[:exclusion_start])
    after = exclusion_start + exclusion_length
    if after < len(flac_bytes):
        h.update(flac_bytes[after:])
    return h.digest()


def replace_manifest_in_flac(
    flac_bytes: bytes,
    manifest_bytes: bytes,
    manifest_offset: int,
    manifest_length: int,
) -> bytes:
    """Replace the placeholder manifest data with actual manifest bytes.

    Args:
        flac_bytes: FLAC bytes containing the zero-filled placeholder.
        manifest_bytes: Actual C2PA manifest store bytes.
        manifest_offset: Byte offset of the manifest data in the file.
        manifest_length: Length of the placeholder region.

    Returns:
        Updated FLAC bytes with manifest embedded.

    Raises:
        ValueError: If manifest is larger than the placeholder.
    """
    if len(manifest_bytes) > manifest_length:
        raise ValueError(f"Manifest ({len(manifest_bytes)} bytes) exceeds placeholder " f"({manifest_length} bytes). Retry with larger placeholder.")

    # Pad to fill the placeholder exactly
    padded = manifest_bytes + b"\x00" * (manifest_length - len(manifest_bytes))
    return flac_bytes[:manifest_offset] + padded + flac_bytes[manifest_offset + manifest_length :]
