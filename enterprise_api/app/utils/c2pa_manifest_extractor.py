"""Per-format C2PA manifest extraction for Pipeline B formats.

Extracts raw JUMBF manifest store bytes from signed documents, fonts,
FLAC audio, and JPEG XL files. Each format stores the manifest in a
different location per the C2PA spec:

  - PDF: Embedded file stream with AFRelationship = C2PA_Manifest
  - ZIP (EPUB, DOCX, ODT, OXPS): META-INF/content_credential.c2pa entry
  - Font (OTF, TTF): SFNT table with tag 'C2PA'
  - FLAC: APPLICATION metadata block with app_id 'c2pa'
  - JXL: Top-level ISOBMFF box with type 'c2pa'
"""

import io
import logging
import struct
import zipfile
from typing import Optional

_log = logging.getLogger(__name__)

# MIME type to format dispatcher
_DOCUMENT_MIMES = frozenset(
    {
        "application/pdf",
    }
)
_ZIP_MIMES = frozenset(
    {
        "application/epub+zip",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.oasis.opendocument.text",
        "application/oxps",
    }
)
_FONT_MIMES = frozenset({"font/otf", "font/ttf", "font/sfnt"})
_FLAC_MIMES = frozenset({"audio/flac"})
_JXL_MIMES = frozenset({"image/jxl"})

# ZIP manifest path per C2PA spec
ZIP_MANIFEST_PATH = "META-INF/content_credential.c2pa"

# Font constants
_C2PA_TAG = b"C2PA"
_SFNT_VERSIONS = {b"\x00\x01\x00\x00", b"OTTO", b"true", b"typ1"}

# FLAC constants
_FLAC_MAGIC = b"fLaC"
_BLOCK_TYPE_APPLICATION = 2
_C2PA_APP_ID = b"c2pa"

# JXL constants
_JXL_CONTAINER_SIG = b"\x00\x00\x00\x0cJXL \r\n\x87\n"
_C2PA_BOX_TYPE = b"c2pa"


def extract_manifest(data: bytes, mime_type: str) -> Optional[bytes]:
    """Extract C2PA manifest store bytes from a signed file.

    Args:
        data: Raw file bytes.
        mime_type: MIME type of the file.

    Returns:
        Raw JUMBF manifest store bytes, or None if no manifest found.
    """
    if mime_type in _DOCUMENT_MIMES:
        return _extract_from_pdf(data)
    elif mime_type in _ZIP_MIMES:
        return _extract_from_zip(data)
    elif mime_type in _FONT_MIMES:
        return _extract_from_font(data)
    elif mime_type in _FLAC_MIMES:
        return _extract_from_flac(data)
    elif mime_type in _JXL_MIMES:
        return _extract_from_jxl(data)
    else:
        _log.warning("No manifest extraction support for MIME type: %s", mime_type)
        return None


def _extract_from_pdf(data: bytes) -> Optional[bytes]:
    """Extract manifest from PDF embedded file stream.

    Looks for the Associated Files (/AF) entry in the catalog with
    AFRelationship = C2PA_Manifest, then reads the embedded file stream.
    """
    try:
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(data))
        root = reader.trailer["/Root"].get_object()

        af = root.get("/AF")
        if not af:
            _log.debug("PDF has no /AF array in catalog")
            return None

        af_array = af.get_object() if hasattr(af, "get_object") else af
        for entry in af_array:
            obj = entry.get_object() if hasattr(entry, "get_object") else entry
            rel = obj.get("/AFRelationship")
            if rel and str(rel) == "/C2PA_Manifest":
                ef = obj.get("/EF")
                if ef:
                    ef_obj = ef.get_object() if hasattr(ef, "get_object") else ef
                    stream_ref = ef_obj.get("/F")
                    if stream_ref:
                        stream = stream_ref.get_object() if hasattr(stream_ref, "get_object") else stream_ref
                        raw = stream.get_data()
                        return _strip_padding(raw)
        _log.debug("No C2PA_Manifest AF entry found in PDF")
        return None
    except Exception:
        _log.debug("Failed to extract manifest from PDF", exc_info=True)
        return None


def _extract_from_zip(data: bytes) -> Optional[bytes]:
    """Extract manifest from ZIP entry META-INF/content_credential.c2pa."""
    try:
        with zipfile.ZipFile(io.BytesIO(data), "r") as zf:
            if ZIP_MANIFEST_PATH not in zf.namelist():
                _log.debug("No %s entry in ZIP", ZIP_MANIFEST_PATH)
                return None
            raw = zf.read(ZIP_MANIFEST_PATH)
            return _strip_padding(raw)
    except Exception:
        _log.debug("Failed to extract manifest from ZIP", exc_info=True)
        return None


def _extract_from_font(data: bytes) -> Optional[bytes]:
    """Extract manifest from SFNT C2PA table.

    Parses the SFNT table directory to find the C2PA table,
    then reads the table data bytes.
    """
    try:
        if len(data) < 12:
            return None
        version = data[:4]
        if version not in _SFNT_VERSIONS:
            _log.debug("Not a valid SFNT file (version: %r)", version)
            return None

        num_tables = struct.unpack(">H", data[4:6])[0]
        for i in range(num_tables):
            rec_offset = 12 + i * 16
            if rec_offset + 16 > len(data):
                break
            tag = data[rec_offset : rec_offset + 4]
            if tag == _C2PA_TAG:
                _, toff, tlen = struct.unpack(">III", data[rec_offset + 4 : rec_offset + 16])
                if toff + tlen > len(data):
                    _log.debug("C2PA table extends beyond file")
                    return None
                raw = data[toff : toff + tlen]
                return _strip_padding(raw)

        _log.debug("No C2PA table found in SFNT")
        return None
    except Exception:
        _log.debug("Failed to extract manifest from font", exc_info=True)
        return None


def _extract_from_flac(data: bytes) -> Optional[bytes]:
    """Extract manifest from FLAC APPLICATION metadata block.

    Parses FLAC metadata blocks to find the APPLICATION block with
    app_id 'c2pa', then reads the manifest data after the app_id.
    """
    try:
        if len(data) < 8 or data[:4] != _FLAC_MAGIC:
            return None

        pos = 4  # After magic
        while pos < len(data):
            if pos + 4 > len(data):
                break
            header_byte = data[pos]
            is_last = bool(header_byte & 0x80)
            block_type = header_byte & 0x7F
            block_length = struct.unpack(">I", b"\x00" + data[pos + 1 : pos + 4])[0]
            data_start = pos + 4

            if block_type == _BLOCK_TYPE_APPLICATION and block_length >= 4:
                app_id = data[data_start : data_start + 4]
                if app_id == _C2PA_APP_ID:
                    manifest_start = data_start + 4
                    manifest_length = block_length - 4
                    raw = data[manifest_start : manifest_start + manifest_length]
                    return _strip_padding(raw)

            pos = data_start + block_length
            if is_last:
                break

        _log.debug("No C2PA APPLICATION block found in FLAC")
        return None
    except Exception:
        _log.debug("Failed to extract manifest from FLAC", exc_info=True)
        return None


def _extract_from_jxl(data: bytes) -> Optional[bytes]:
    """Extract manifest from JXL ISOBMFF c2pa box.

    Parses top-level ISOBMFF boxes to find the 'c2pa' box,
    then reads the manifest data from the box payload.
    """
    try:
        if len(data) < 12:
            return None
        if data[:12] != _JXL_CONTAINER_SIG:
            _log.debug("Not a JXL ISOBMFF container")
            return None

        pos = 0
        while pos + 8 <= len(data):
            box_size = struct.unpack(">I", data[pos : pos + 4])[0]
            box_type = data[pos + 4 : pos + 8]

            if box_size == 1:
                # Extended size (64-bit)
                if pos + 16 > len(data):
                    break
                box_size = struct.unpack(">Q", data[pos + 8 : pos + 16])[0]
                header_size = 16
            elif box_size == 0:
                # Box extends to EOF
                box_size = len(data) - pos
                header_size = 8
            else:
                header_size = 8

            if box_type == _C2PA_BOX_TYPE:
                payload_start = pos + header_size
                payload_len = box_size - header_size
                raw = data[payload_start : payload_start + payload_len]
                return _strip_padding(raw)

            if box_size < 8:
                break
            pos += box_size

        _log.debug("No c2pa box found in JXL")
        return None
    except Exception:
        _log.debug("Failed to extract manifest from JXL", exc_info=True)
        return None


# --- Extraction info helpers (for hash re-verification) ---


def get_font_c2pa_table_range(data: bytes) -> Optional[tuple[int, int]]:
    """Find the byte offset and length of the C2PA table in an SFNT font.

    Returns (offset, length) or None if not found.
    """
    if len(data) < 12 or data[:4] not in _SFNT_VERSIONS:
        return None
    num_tables = struct.unpack(">H", data[4:6])[0]
    for i in range(num_tables):
        rec_offset = 12 + i * 16
        if rec_offset + 16 > len(data):
            return None
        tag = data[rec_offset : rec_offset + 4]
        if tag == _C2PA_TAG:
            _, toff, tlen = struct.unpack(">III", data[rec_offset + 4 : rec_offset + 16])
            return (toff, tlen)
    return None


def get_flac_c2pa_data_range(data: bytes) -> Optional[tuple[int, int]]:
    """Find the byte offset and length of the C2PA manifest data in a FLAC file.

    Returns (data_offset, data_length) where data_offset is after the app_id.
    """
    if len(data) < 8 or data[:4] != _FLAC_MAGIC:
        return None
    pos = 4
    while pos < len(data):
        if pos + 4 > len(data):
            break
        header_byte = data[pos]
        is_last = bool(header_byte & 0x80)
        block_type = header_byte & 0x7F
        block_length = struct.unpack(">I", b"\x00" + data[pos + 1 : pos + 4])[0]
        data_start = pos + 4
        if block_type == _BLOCK_TYPE_APPLICATION and block_length >= 4:
            app_id = data[data_start : data_start + 4]
            if app_id == _C2PA_APP_ID:
                return (data_start + 4, block_length - 4)
        pos = data_start + block_length
        if is_last:
            break
    return None


def get_jxl_c2pa_data_range(data: bytes) -> Optional[tuple[int, int]]:
    """Find the byte offset and length of the C2PA manifest data in a JXL file.

    Returns (data_offset, data_length) of the c2pa box payload.
    """
    if len(data) < 12 or data[:12] != _JXL_CONTAINER_SIG:
        return None
    pos = 0
    while pos + 8 <= len(data):
        box_size = struct.unpack(">I", data[pos : pos + 4])[0]
        box_type = data[pos + 4 : pos + 8]
        if box_size == 1:
            if pos + 16 > len(data):
                break
            box_size = struct.unpack(">Q", data[pos + 8 : pos + 16])[0]
            header_size = 16
        elif box_size == 0:
            box_size = len(data) - pos
            header_size = 8
        else:
            header_size = 8
        if box_type == _C2PA_BOX_TYPE:
            return (pos + header_size, box_size - header_size)
        if box_size < 8:
            break
        pos += box_size
    return None


def _strip_padding(data: bytes) -> bytes:
    """Strip trailing zero-byte padding from manifest data."""
    return data.rstrip(b"\x00")
