"""C2PA manifest embedding for SFNT-based font files (OTF/TTF).

Per C2PA spec, the manifest is stored as an SFNT table with tag 'C2PA'.
Content binding uses c2pa.hash.data with an exclusion range covering
the C2PA table bytes.

SFNT structure:
  Header (12 bytes): sfVersion(4) + numTables(2) + searchRange(2)
                     + entrySelector(2) + rangeShift(2)
  Table records (16 bytes each): tag(4) + checksum(4) + offset(4) + length(4)
  Table data: aligned to 4-byte boundaries

Two-pass approach:
  1. Add C2PA table with zero-filled placeholder
  2. Hash everything except the C2PA table range
  3. Build and sign the manifest
  4. Replace placeholder with actual manifest bytes
"""

import hashlib
import logging
import math
import struct
from typing import Optional

_log = logging.getLogger(__name__)

C2PA_TAG = b"C2PA"

# SFNT magic numbers
SFNT_TRUETYPE = b"\x00\x01\x00\x00"
SFNT_OPENTYPE = b"OTTO"
SFNT_TRUE = b"true"
SFNT_TYP1 = b"typ1"

VALID_SFNT_VERSIONS = (SFNT_TRUETYPE, SFNT_OPENTYPE, SFNT_TRUE, SFNT_TYP1)


def _pad4(n: int) -> int:
    """Round up to next 4-byte boundary."""
    return (n + 3) & ~3


def _compute_table_checksum(data: bytes) -> int:
    """Compute SFNT table checksum (sum of 32-bit big-endian words)."""
    # Pad to 4-byte boundary
    padded = data + b"\x00" * (_pad4(len(data)) - len(data))
    total = 0
    for i in range(0, len(padded), 4):
        total = (total + struct.unpack(">I", padded[i : i + 4])[0]) & 0xFFFFFFFF
    return total


def _search_range(n: int) -> tuple[int, int, int]:
    """Compute searchRange, entrySelector, rangeShift for n tables."""
    entry_selector = int(math.log2(n)) if n > 0 else 0
    search_range = (2**entry_selector) * 16
    range_shift = n * 16 - search_range
    return search_range, entry_selector, range_shift


def parse_sfnt(data: bytes) -> dict:
    """Parse SFNT table directory.

    Returns:
        Dict with 'version', 'tables' (list of {tag, checksum, offset, length}).
    """
    if len(data) < 12:
        raise ValueError("Data too short for SFNT header")

    version = data[:4]
    if version not in VALID_SFNT_VERSIONS:
        raise ValueError(f"Not a valid SFNT font (version tag: {version!r})")

    num_tables = struct.unpack(">H", data[4:6])[0]
    tables = []
    for i in range(num_tables):
        off = 12 + i * 16
        if off + 16 > len(data):
            raise ValueError("SFNT table directory truncated")
        tag = data[off : off + 4]
        checksum, toff, tlen = struct.unpack(">III", data[off + 4 : off + 16])
        tables.append(
            {
                "tag": tag,
                "checksum": checksum,
                "offset": toff,
                "length": tlen,
            }
        )

    return {"version": version, "tables": tables}


def create_font_with_placeholder(font_bytes: bytes, placeholder_size: int = 32768) -> tuple[bytes, int, int]:
    """Add a C2PA table with zero-filled placeholder to an SFNT font.

    Args:
        font_bytes: Original font bytes.
        placeholder_size: Size of the zero-filled C2PA table data.

    Returns:
        Tuple of (new_font_bytes, c2pa_table_data_offset, c2pa_table_data_length).
    """
    info = parse_sfnt(font_bytes)
    version = info["version"]
    old_tables = info["tables"]

    # Remove existing C2PA table if present
    old_tables = [t for t in old_tables if t["tag"] != C2PA_TAG]

    # Read table data from original
    table_data = {}
    for t in old_tables:
        table_data[t["tag"]] = font_bytes[t["offset"] : t["offset"] + t["length"]]

    # Add C2PA placeholder
    c2pa_data = b"\x00" * placeholder_size
    all_tags = [t["tag"] for t in old_tables] + [C2PA_TAG]
    all_tags.sort()  # SFNT tables must be sorted by tag

    num_tables = len(all_tags)
    search_range, entry_selector, range_shift = _search_range(num_tables)

    # Build new font
    # Header
    header = version + struct.pack(">HHH", num_tables, search_range, range_shift)
    # Note: entrySelector goes between searchRange and rangeShift
    header = version + struct.pack(">HHHH", num_tables, search_range, entry_selector, range_shift)

    # Calculate offsets: header(12) + table_records(num_tables * 16) = data_start
    data_start = 12 + num_tables * 16
    current_offset = data_start

    # Build table records and data
    records = []
    data_blocks = []
    c2pa_offset = 0
    c2pa_length = 0

    for tag in all_tags:
        if tag == C2PA_TAG:
            tdata = c2pa_data
        else:
            tdata = table_data[tag]

        checksum = _compute_table_checksum(tdata)
        records.append(struct.pack(">4sIII", tag, checksum, current_offset, len(tdata)))

        if tag == C2PA_TAG:
            c2pa_offset = current_offset
            c2pa_length = len(tdata)

        data_blocks.append(tdata)
        # Pad to 4-byte boundary
        pad_len = _pad4(len(tdata)) - len(tdata)
        if pad_len > 0:
            data_blocks.append(b"\x00" * pad_len)
        current_offset += _pad4(len(tdata))

    result = header + b"".join(records) + b"".join(data_blocks)
    return result, c2pa_offset, c2pa_length


def compute_font_hash(
    font_bytes: bytes,
    exclusion_start: int,
    exclusion_length: int,
    alg: str = "sha256",
) -> bytes:
    """Compute hash of font bytes, excluding the C2PA table data range."""
    h = hashlib.new(alg)
    h.update(font_bytes[:exclusion_start])
    after = exclusion_start + exclusion_length
    if after < len(font_bytes):
        h.update(font_bytes[after:])
    return h.digest()


def replace_manifest_in_font(
    font_bytes: bytes,
    manifest_bytes: bytes,
    c2pa_offset: int,
    c2pa_length: int,
) -> bytes:
    """Replace the C2PA table placeholder with actual manifest bytes.

    Args:
        font_bytes: Font bytes containing the placeholder.
        manifest_bytes: Actual C2PA manifest store bytes.
        c2pa_offset: Byte offset of the C2PA table data.
        c2pa_length: Length of the C2PA table placeholder.

    Returns:
        Updated font bytes.

    Raises:
        ValueError: If manifest is larger than the placeholder.
    """
    if len(manifest_bytes) > c2pa_length:
        raise ValueError(
            f"Manifest ({len(manifest_bytes)} bytes) exceeds C2PA table placeholder ({c2pa_length} bytes). Retry with larger placeholder."
        )

    # Pad to fill the placeholder exactly
    padded = manifest_bytes + b"\x00" * (c2pa_length - len(manifest_bytes))
    return font_bytes[:c2pa_offset] + padded + font_bytes[c2pa_offset + c2pa_length :]
