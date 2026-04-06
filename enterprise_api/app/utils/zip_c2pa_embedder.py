"""C2PA manifest embedding for ZIP-based document formats.

Supports: EPUB, DOCX (OOXML), ODT (ODF), OXPS (OpenXPS).

Per C2PA spec, the manifest is stored at META-INF/content_credential.c2pa
as an uncompressed, unencrypted entry. Content binding uses the
c2pa.hash.collection.data assertion.

Two-pass approach:
  1. Create ZIP with zero-filled placeholder manifest
  2. Hash all files + central directory
  3. Build and sign the manifest
  4. Replace placeholder with real manifest bytes
"""

import hashlib
import io
import logging
import struct
import zipfile
from typing import Optional

_log = logging.getLogger(__name__)

MANIFEST_PATH = "META-INF/content_credential.c2pa"


def _hash_local_file_entry(zip_bytes: bytes, info: zipfile.ZipInfo, alg: str = "sha256") -> bytes:
    """Hash a ZIP file's local file header + compressed data + optional data descriptor.

    Per C2PA spec: hash covers local file header + compressed/encrypted content
    + data descriptor (if present).
    """
    offset = info.header_offset
    # Local file header: 30 bytes fixed + filename_len + extra_len
    if offset + 30 > len(zip_bytes):
        raise ValueError(f"Invalid local file header offset for {info.filename}")

    # Parse local file header to get exact size
    sig = struct.unpack_from("<I", zip_bytes, offset)[0]
    if sig != 0x04034B50:
        raise ValueError(f"Invalid local file header signature for {info.filename}")

    fname_len = struct.unpack_from("<H", zip_bytes, offset + 26)[0]
    extra_len = struct.unpack_from("<H", zip_bytes, offset + 28)[0]
    header_size = 30 + fname_len + extra_len
    data_size = info.compress_size

    # Check for data descriptor (bit 3 of general purpose flag)
    gp_flag = struct.unpack_from("<H", zip_bytes, offset + 6)[0]
    descriptor_size = 0
    if gp_flag & 0x08:
        # Data descriptor: optional signature (4) + crc32 (4) + compressed_size (4) + uncompressed_size (4)
        desc_offset = offset + header_size + data_size
        if desc_offset + 4 <= len(zip_bytes):
            maybe_sig = struct.unpack_from("<I", zip_bytes, desc_offset)[0]
            if maybe_sig == 0x08074B50:
                descriptor_size = 16  # signature + crc32 + sizes
            else:
                descriptor_size = 12  # crc32 + sizes (no signature)

    total_size = header_size + data_size + descriptor_size
    entry_bytes = zip_bytes[offset : offset + total_size]

    h = hashlib.new(alg)
    h.update(entry_bytes)
    return h.digest()


def _hash_central_directory(zip_bytes: bytes, manifest_filename: str, alg: str = "sha256") -> bytes:
    """Hash the ZIP central directory, skipping the manifest's CRC-32 field.

    Per C2PA spec: hash each central directory header sequentially,
    except skip the CRC-32 field (4 bytes at offset 16) of the manifest entry.
    Then include the End of Central Directory record.
    """
    # Find the End of Central Directory record (scan backwards)
    eocd_offset = _find_eocd(zip_bytes)
    if eocd_offset is None:
        raise ValueError("Cannot find End of Central Directory record")

    cd_offset = struct.unpack_from("<I", zip_bytes, eocd_offset + 16)[0]
    cd_size = struct.unpack_from("<I", zip_bytes, eocd_offset + 12)[0]

    h = hashlib.new(alg)
    pos = cd_offset
    cd_end = cd_offset + cd_size

    while pos < cd_end:
        sig = struct.unpack_from("<I", zip_bytes, pos)[0]
        if sig != 0x02014B50:
            break

        fname_len = struct.unpack_from("<H", zip_bytes, pos + 28)[0]
        extra_len = struct.unpack_from("<H", zip_bytes, pos + 30)[0]
        comment_len = struct.unpack_from("<H", zip_bytes, pos + 32)[0]
        entry_size = 46 + fname_len + extra_len + comment_len

        fname = zip_bytes[pos + 46 : pos + 46 + fname_len].decode("utf-8", errors="replace")

        if fname == manifest_filename:
            # Hash everything EXCEPT the CRC-32 field (4 bytes at offset 16)
            h.update(zip_bytes[pos : pos + 16])
            # Skip CRC-32 (4 bytes at offset 16)
            h.update(zip_bytes[pos + 20 : pos + entry_size])
        else:
            h.update(zip_bytes[pos : pos + entry_size])

        pos += entry_size

    # Include the End of Central Directory record
    h.update(zip_bytes[eocd_offset:])

    return h.digest()


def _find_eocd(data: bytes) -> Optional[int]:
    """Find the End of Central Directory record offset."""
    # EOCD signature: 0x06054b50
    sig = b"PK\x05\x06"
    # Search backwards from end (EOCD is at least 22 bytes)
    search_start = max(0, len(data) - 65557)  # max comment = 65535
    idx = data.rfind(sig, search_start)
    return idx if idx >= 0 else None


def compute_collection_hashes(zip_bytes: bytes, alg: str = "sha256") -> tuple[list[dict], bytes]:
    """Compute file hashes and central directory hash for a ZIP file.

    Args:
        zip_bytes: Complete ZIP file bytes (with placeholder manifest).
        alg: Hash algorithm.

    Returns:
        Tuple of (file_hashes, central_directory_hash).
        file_hashes is a list of {"uri": str, "hash": bytes} for each file
        except the manifest.
    """
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        file_hashes = []
        for info in zf.infolist():
            if info.filename == MANIFEST_PATH:
                continue  # Skip the manifest itself
            file_hash = _hash_local_file_entry(zip_bytes, info, alg)
            file_hashes.append(
                {
                    "uri": info.filename,
                    "hash": file_hash,
                }
            )

    cd_hash = _hash_central_directory(zip_bytes, MANIFEST_PATH, alg)
    return file_hashes, cd_hash


def create_zip_with_placeholder(original_bytes: bytes, placeholder_size: int = 32768) -> bytes:
    """Create a new ZIP with a zero-filled placeholder at META-INF/content_credential.c2pa.

    Args:
        original_bytes: Original ZIP file bytes.
        placeholder_size: Size of the zero-filled placeholder.

    Returns:
        New ZIP file bytes with placeholder manifest entry.
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(original_bytes)) as src, zipfile.ZipFile(buf, "w") as dst:
        for info in src.infolist():
            if info.filename == MANIFEST_PATH:
                continue  # Remove existing manifest if present
            data = src.read(info.filename)
            # Preserve compression method
            dst_info = info
            dst.writestr(dst_info, data)

        # Add placeholder manifest (uncompressed, per spec)
        manifest_info = zipfile.ZipInfo(MANIFEST_PATH)
        manifest_info.compress_type = zipfile.ZIP_STORED
        manifest_info.flag_bits = 0
        dst.writestr(manifest_info, b"\x00" * placeholder_size)

    return buf.getvalue()


def replace_manifest_in_zip(zip_bytes: bytes, manifest_bytes: bytes) -> bytes:
    """Replace the placeholder manifest with the real signed manifest in-place.

    Uses direct byte patching to preserve all file offsets and central directory
    layout, ensuring that content hashes computed on the placeholder ZIP remain
    valid after replacement.

    Only the manifest data bytes and the CRC-32 fields (in both the local file
    header and central directory entry) are modified.

    Args:
        zip_bytes: ZIP file bytes containing the placeholder.
        manifest_bytes: Actual C2PA manifest store bytes.

    Returns:
        Updated ZIP file bytes with manifest embedded.
    """
    import zlib

    # Find the manifest entry metadata
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        manifest_info = None
        for info in zf.infolist():
            if info.filename == MANIFEST_PATH:
                manifest_info = info
                break

    if manifest_info is None:
        raise ValueError(f"Manifest entry {MANIFEST_PATH} not found in ZIP")

    if len(manifest_bytes) > manifest_info.file_size:
        raise ValueError(f"Manifest ({len(manifest_bytes)} bytes) exceeds placeholder ({manifest_info.file_size} bytes)")

    # Pad manifest to exactly fill the placeholder
    padded = manifest_bytes + b"\x00" * (manifest_info.file_size - len(manifest_bytes))

    # Locate data within the local file entry
    offset = manifest_info.header_offset
    fname_len = struct.unpack_from("<H", zip_bytes, offset + 26)[0]
    extra_len = struct.unpack_from("<H", zip_bytes, offset + 28)[0]
    data_offset = offset + 30 + fname_len + extra_len

    # Compute new CRC-32 for the replaced content
    new_crc = zlib.crc32(padded) & 0xFFFFFFFF

    result = bytearray(zip_bytes)

    # Patch 1: Replace the file data bytes
    result[data_offset : data_offset + len(padded)] = padded

    # Patch 2: Update CRC-32 in local file header (4 bytes at offset 14)
    struct.pack_into("<I", result, offset + 14, new_crc)

    # Patch 3: Update CRC-32 in the central directory entry
    eocd_offset = _find_eocd(bytes(result))
    if eocd_offset is None:
        raise ValueError("Cannot find End of Central Directory record")

    cd_offset = struct.unpack_from("<I", result, eocd_offset + 16)[0]
    cd_size = struct.unpack_from("<I", result, eocd_offset + 12)[0]
    pos = cd_offset
    cd_end = cd_offset + cd_size

    while pos < cd_end:
        sig = struct.unpack_from("<I", result, pos)[0]
        if sig != 0x02014B50:
            break
        fn_len = struct.unpack_from("<H", result, pos + 28)[0]
        ex_len = struct.unpack_from("<H", result, pos + 30)[0]
        cm_len = struct.unpack_from("<H", result, pos + 32)[0]
        fname = bytes(result[pos + 46 : pos + 46 + fn_len]).decode("utf-8", errors="replace")

        if fname == MANIFEST_PATH:
            # CRC-32 is at offset 16 within the central directory entry
            struct.pack_into("<I", result, pos + 16, new_crc)
            break

        pos += 46 + fn_len + ex_len + cm_len

    return bytes(result)
