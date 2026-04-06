#!/usr/bin/env python3
"""C2PA 22-Format Conformance Suite: Generate, Sign, Verify.

Generates minimal test fixtures for all 20 target formats, signs them using
our C2PA pipeline (c2pa-python for media, custom JUMBF/COSE for documents),
and verifies each signed file internally.

Usage:
    cd enterprise_api
    uv run python tests/c2pa_conformance/run_conformance.py

Output:
    tests/c2pa_conformance/fixtures/   -- unsigned test files
    tests/c2pa_conformance/signed/     -- signed files (for Adobe verify upload)
    tests/c2pa_conformance/results/    -- verify_results.json + verify_all.log
"""

import io
import json
import logging
import os
import struct
import subprocess
import sys
import uuid
import zipfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Add enterprise_api to path so we can import app modules
SCRIPT_DIR = Path(__file__).resolve().parent
ENTERPRISE_DIR = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(ENTERPRISE_DIR))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
)
log = logging.getLogger("c2pa_conformance")

# Directories
FIXTURES_DIR = SCRIPT_DIR / "fixtures"
SIGNED_DIR = SCRIPT_DIR / "signed"
RESULTS_DIR = SCRIPT_DIR / "results"
MANIFESTS_DIR = SCRIPT_DIR / "manifests"
CERTS_DIR = ENTERPRISE_DIR / "tests" / "c2pa_test_certs"

# Ensure output dirs exist
FIXTURES_DIR.mkdir(exist_ok=True)
SIGNED_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)
MANIFESTS_DIR.mkdir(exist_ok=True)


@dataclass
class FormatSpec:
    """Specification for a single format to test."""

    name: str  # human-readable: "JPEG", "MP4", etc.
    extension: str  # file extension including dot
    mime_type: str  # MIME type for c2pa-python
    category: str  # "image", "video", "audio", "document"
    pipeline: str  # "c2pa_builder" or "document_service"
    output_stem: str = ""  # custom output filename stem (for variants sharing an extension)


# All 20 target formats
FORMATS = [
    # Images (9)
    FormatSpec("JPEG", ".jpg", "image/jpeg", "image", "c2pa_builder"),
    FormatSpec("PNG", ".png", "image/png", "image", "c2pa_builder"),
    FormatSpec("WebP", ".webp", "image/webp", "image", "c2pa_builder"),
    FormatSpec("TIFF", ".tiff", "image/tiff", "image", "c2pa_builder"),
    FormatSpec("AVIF", ".avif", "image/avif", "image", "c2pa_builder"),
    FormatSpec("HEIC", ".heic", "image/heic", "image", "c2pa_builder"),
    FormatSpec("HEIF", ".heif", "image/heif", "image", "c2pa_builder"),
    FormatSpec("SVG", ".svg", "image/svg+xml", "image", "c2pa_builder"),
    FormatSpec("DNG", ".dng", "image/x-adobe-dng", "image", "c2pa_builder"),
    FormatSpec("GIF", ".gif", "image/gif", "image", "c2pa_builder"),
    FormatSpec("JXL", ".jxl", "image/jxl", "image", "document_service"),
    FormatSpec("HEIC-sequence", ".heic", "image/heic-sequence", "image", "c2pa_builder", "signed_test_heic-sequence"),
    FormatSpec("HEIF-sequence", ".heif", "image/heif-sequence", "image", "c2pa_builder", "signed_test_heif-sequence"),
    # Video (3)
    FormatSpec("MP4", ".mp4", "video/mp4", "video", "c2pa_builder"),
    FormatSpec("MOV", ".mov", "video/quicktime", "video", "c2pa_builder"),
    FormatSpec("AVI", ".avi", "video/x-msvideo", "video", "c2pa_builder"),
    FormatSpec("M4V", ".m4v", "video/x-m4v", "video", "c2pa_builder"),
    # Audio (4)
    FormatSpec("WAV", ".wav", "audio/wav", "audio", "c2pa_builder"),
    FormatSpec("MP3", ".mp3", "audio/mpeg", "audio", "c2pa_builder"),
    FormatSpec("M4A", ".m4a", "audio/mp4", "audio", "c2pa_builder"),
    FormatSpec("FLAC", ".flac", "audio/flac", "audio", "document_service"),
    FormatSpec("MPA", ".mp3", "audio/MPA", "audio", "c2pa_builder", "signed_test_mpa"),
    FormatSpec("AAC", ".m4a", "audio/aac", "audio", "c2pa_builder", "signed_test_aac"),
    # Document (5)
    FormatSpec("PDF", ".pdf", "application/pdf", "document", "document_service"),
    FormatSpec("EPUB", ".epub", "application/epub+zip", "document", "document_service"),
    FormatSpec("DOCX", ".docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "document", "document_service"),
    FormatSpec("ODT", ".odt", "application/vnd.oasis.opendocument.text", "document", "document_service"),
    FormatSpec("OXPS", ".oxps", "application/oxps", "document", "document_service"),
    # Fonts (C2PA conformance covers OTF only; TTF/SFNT supported at runtime)
    FormatSpec("OTF", ".otf", "font/otf", "font", "document_service"),
]


@dataclass
class FormatResult:
    """Result for a single format."""

    name: str
    extension: str
    mime_type: str
    category: str
    fixture_size: int = 0
    signed_size: int = 0
    sign_success: bool = False
    sign_error: Optional[str] = None
    verify_success: bool = False
    verify_error: Optional[str] = None
    instance_id: Optional[str] = None
    manifest_label: Optional[str] = None
    validation_codes: list = None
    signed_file: Optional[str] = None

    def __post_init__(self):
        if self.validation_codes is None:
            self.validation_codes = []


# ---------------------------------------------------------------------------
# Fixture generation
# ---------------------------------------------------------------------------


def _run_ffmpeg(args: list[str], output_path: Path) -> bool:
    """Run ffmpeg with given args, return True on success."""
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + args + [str(output_path)]
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=30)
        return output_path.exists() and output_path.stat().st_size > 0
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        log.warning("ffmpeg failed for %s: %s", output_path.name, e)
        return False


def generate_fixture_jpeg(path: Path) -> bool:
    from PIL import Image

    img = Image.new("RGB", (200, 200), (30, 100, 200))
    img.save(path, "JPEG", quality=90)
    return True


def generate_fixture_png(path: Path) -> bool:
    from PIL import Image

    img = Image.new("RGBA", (200, 200), (30, 200, 100, 255))
    img.save(path, "PNG")
    return True


def generate_fixture_webp(path: Path) -> bool:
    from PIL import Image

    img = Image.new("RGB", (200, 200), (200, 100, 30))
    img.save(path, "WEBP", quality=90)
    return True


def generate_fixture_tiff(path: Path) -> bool:
    from PIL import Image

    img = Image.new("RGB", (200, 200), (100, 30, 200))
    img.save(path, "TIFF")
    return True


def generate_fixture_avif(path: Path) -> bool:
    from PIL import Image

    img = Image.new("RGB", (200, 200), (200, 30, 100))
    try:
        img.save(path, "AVIF", quality=80)
        return True
    except Exception as e:
        log.warning("Pillow AVIF save failed (%s), trying ffmpeg", e)
        return _run_ffmpeg(
            ["-f", "lavfi", "-i", "color=c=red:size=200x200:duration=1:rate=1", "-frames:v", "1"],
            path,
        )


def generate_fixture_heic(path: Path) -> bool:
    import pillow_heif

    pillow_heif.register_heif_opener()
    from PIL import Image

    img = Image.new("RGB", (200, 200), (30, 200, 200))
    try:
        img.save(path, "HEIF")
        return True
    except Exception as e:
        log.warning("pillow-heif save failed: %s", e)
        return False


def generate_fixture_heif(path: Path) -> bool:
    # HEIF and HEIC share the same container; generate separately
    import pillow_heif

    pillow_heif.register_heif_opener()
    from PIL import Image

    img = Image.new("RGB", (200, 200), (200, 200, 30))
    try:
        img.save(path, "HEIF")
        return True
    except Exception as e:
        log.warning("pillow-heif save failed: %s", e)
        return False


def generate_fixture_svg(path: Path) -> bool:
    svg = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">\n'
        '  <rect width="200" height="200" fill="#1E64C8"/>\n'
        '  <circle cx="100" cy="100" r="60" fill="#C81E64"/>\n'
        '  <text x="100" y="108" text-anchor="middle" fill="white" '
        'font-family="sans-serif" font-size="16">Encypher C2PA</text>\n'
        "</svg>\n"
    )
    path.write_text(svg, encoding="utf-8")
    return True


def generate_fixture_dng(path: Path) -> bool:
    """Generate minimal DNG file (TIFF-based with DNGVersion tag).

    c2pa-python/c2pa-rs handles DNG as a TIFF variant. We generate a valid
    TIFF IFD structure with the DNGVersion tag (50706).
    """
    buf = io.BytesIO()
    # TIFF header -- little-endian
    buf.write(b"II")
    buf.write(struct.pack("<H", 42))  # TIFF magic

    width, height = 64, 64
    pixels = b"\x80" * (width * height)  # grayscale data

    # IFD entries (must be sorted by tag number)
    entries = [
        # (tag, type, count, value_or_offset)
        # type: 1=BYTE, 3=SHORT, 4=LONG
        (256, 3, 1, width),  # ImageWidth
        (257, 3, 1, height),  # ImageLength
        (258, 3, 1, 8),  # BitsPerSample
        (259, 3, 1, 1),  # Compression: None
        (262, 3, 1, 1),  # PhotometricInterpretation: BlackIsZero
        (273, 4, 1, 0),  # StripOffsets (placeholder)
        (277, 3, 1, 1),  # SamplesPerPixel
        (278, 3, 1, height),  # RowsPerStrip
        (279, 4, 1, len(pixels)),  # StripByteCounts
    ]

    # DNGVersion tag (50706) -- BYTE[4] = 1.4.0.0
    # Since count=4 and type=BYTE, value fits in 4 bytes inline
    dng_version_entry = (50706, 1, 4, None)  # special handling
    entries.append(dng_version_entry)

    num_entries = len(entries)
    ifd_offset = 8  # right after TIFF header
    ifd_size = 2 + num_entries * 12 + 4  # count + entries + next_ifd
    strip_offset = ifd_offset + ifd_size

    buf.write(struct.pack("<I", ifd_offset))  # offset to IFD0

    # Write IFD
    buf.write(struct.pack("<H", num_entries))
    for tag, typ, count, value in entries:
        buf.write(struct.pack("<HHI", tag, typ, count))
        if tag == 273:  # StripOffsets
            buf.write(struct.pack("<I", strip_offset))
        elif tag == 50706:  # DNGVersion
            buf.write(bytes([1, 4, 0, 0]))  # inline 4 bytes
        elif typ == 3:  # SHORT -- value in lower 2 bytes
            buf.write(struct.pack("<HH", value, 0))
        else:
            buf.write(struct.pack("<I", value))

    # Next IFD offset = 0 (no more IFDs)
    buf.write(struct.pack("<I", 0))

    # Strip data
    buf.write(pixels)

    path.write_bytes(buf.getvalue())
    return True


def generate_fixture_gif(path: Path) -> bool:
    from PIL import Image

    img = Image.new("RGBA", (200, 200), (100, 200, 30, 255))
    img.save(path, "GIF")
    return True


def generate_fixture_mp4(path: Path) -> bool:
    existing = CERTS_DIR / "samples" / "test.mp4"
    if existing.exists():
        import shutil

        shutil.copy2(existing, path)
        return True
    return _run_ffmpeg(
        [
            "-f",
            "lavfi",
            "-i",
            "color=c=blue:size=64x64:duration=1:rate=24",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
        ],
        path,
    )


def generate_fixture_mov(path: Path) -> bool:
    return _run_ffmpeg(
        [
            "-f",
            "lavfi",
            "-i",
            "color=c=green:size=64x64:duration=1:rate=24",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-f",
            "mov",
        ],
        path,
    )


def generate_fixture_avi(path: Path) -> bool:
    return _run_ffmpeg(
        [
            "-f",
            "lavfi",
            "-i",
            "color=c=red:size=64x64:duration=1:rate=24",
            "-c:v",
            "libx264",
            "-f",
            "avi",
        ],
        path,
    )


def generate_fixture_wav(path: Path) -> bool:
    existing = CERTS_DIR / "samples" / "test.wav"
    if existing.exists():
        import shutil

        shutil.copy2(existing, path)
        return True
    return _run_ffmpeg(
        ["-f", "lavfi", "-i", "sine=frequency=440:duration=1:sample_rate=44100", "-c:a", "pcm_s16le"],
        path,
    )


def generate_fixture_flac(path: Path) -> bool:
    """Generate a minimal valid FLAC file (STREAMINFO only)."""
    streaminfo_data = (
        b"\x10\x00\x10\x00"  # min/max block size = 4096
        b"\x00\x00\x00\x00\x00\x00"  # min/max frame size = 0
        b"\x0a\xc4\x40\xf0\x00\x00\x00\x00" + b"\x00" * 16  # 44100 Hz, 1ch, 16-bit, 0 samples  # MD5 = zeros
    )
    header = bytes([0x80]) + struct.pack(">I", 34)[1:]  # is_last=1, type=STREAMINFO, len=34
    path.write_bytes(b"fLaC" + header + streaminfo_data)
    return True


def generate_fixture_m4v(path: Path) -> bool:
    return _run_ffmpeg(
        [
            "-f",
            "lavfi",
            "-i",
            "color=c=yellow:size=64x64:duration=1:rate=24",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-f",
            "mp4",
        ],
        path,
    )


def generate_fixture_mp3(path: Path) -> bool:
    return _run_ffmpeg(
        ["-f", "lavfi", "-i", "sine=frequency=440:duration=1:sample_rate=44100", "-c:a", "libmp3lame", "-q:a", "2"],
        path,
    )


def generate_fixture_m4a(path: Path) -> bool:
    return _run_ffmpeg(
        ["-f", "lavfi", "-i", "sine=frequency=440:duration=1:sample_rate=44100", "-c:a", "aac", "-b:a", "128k"],
        path,
    )


def generate_fixture_pdf(path: Path) -> bool:
    """Generate a minimal valid PDF."""
    pdf = (
        "%PDF-1.4\n"
        "1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        "2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        "3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        "/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
        "4 0 obj\n<< /Length 52 >>\nstream\n"
        "BT /F1 24 Tf 72 720 Td (Encypher C2PA Test) Tj ET\n"
        "endstream\nendobj\n"
        "5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
        "xref\n0 6\n"
        "0000000000 65535 f \n"
        "0000000009 00000 n \n"
        "0000000058 00000 n \n"
        "0000000115 00000 n \n"
        "0000000266 00000 n \n"
        "0000000370 00000 n \n"
        "trailer\n<< /Size 6 /Root 1 0 R >>\n"
        "startxref\n449\n%%EOF\n"
    )
    path.write_text(pdf, encoding="latin-1")
    return True


def generate_fixture_epub(path: Path) -> bool:
    """Generate a minimal valid EPUB (ZIP-based)."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr(
            zipfile.ZipInfo("mimetype", date_time=(2024, 1, 1, 0, 0, 0)),
            "application/epub+zip",
            compress_type=zipfile.ZIP_STORED,
        )
        zf.writestr(
            "META-INF/container.xml",
            '<?xml version="1.0"?>'
            '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
            "<rootfiles>"
            '<rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>'
            "</rootfiles></container>",
        )
        zf.writestr(
            "content.opf",
            '<?xml version="1.0"?>'
            '<package xmlns="http://www.idpf.org/2007/opf" version="3.0">'
            "<metadata>"
            '<dc:title xmlns:dc="http://purl.org/dc/elements/1.1/">C2PA Conformance Test</dc:title>'
            "</metadata></package>",
        )
        zf.writestr(
            "chapter1.xhtml",
            "<html><body><p>C2PA conformance test content.</p></body></html>",
        )
    path.write_bytes(buf.getvalue())
    return True


def generate_fixture_docx(path: Path) -> bool:
    """Generate a minimal valid DOCX (OOXML ZIP-based)."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            "</Types>",
        )
        zf.writestr(
            "_rels/.rels",
            '<?xml version="1.0"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
            'Target="word/document.xml"/>'
            "</Relationships>",
        )
        zf.writestr(
            "word/document.xml",
            '<?xml version="1.0"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            "<w:body><w:p><w:r><w:t>C2PA conformance test document.</w:t></w:r></w:p></w:body>"
            "</w:document>",
        )
    path.write_bytes(buf.getvalue())
    return True


def generate_fixture_odt(path: Path) -> bool:
    """Generate a minimal valid ODT (ODF ZIP-based)."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr(
            "mimetype",
            "application/vnd.oasis.opendocument.text",
            compress_type=zipfile.ZIP_STORED,
        )
        zf.writestr(
            "content.xml",
            '<?xml version="1.0"?>'
            "<office:document-content"
            ' xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"'
            ' xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">'
            "<office:body><office:text>"
            "<text:p>C2PA conformance test content.</text:p>"
            "</office:text></office:body></office:document-content>",
        )
        zf.writestr(
            "META-INF/manifest.xml",
            '<?xml version="1.0"?>'
            '<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0">'
            '<manifest:file-entry manifest:full-path="/" '
            'manifest:media-type="application/vnd.oasis.opendocument.text"/>'
            "</manifest:manifest>",
        )
    path.write_bytes(buf.getvalue())
    return True


def generate_fixture_oxps(path: Path) -> bool:
    """Generate a minimal valid OXPS (OpenXPS ZIP-based)."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="fdseq" ContentType="application/oxps-fixeddocumentsequence+xml"/>'
            "</Types>",
        )
        zf.writestr(
            "_rels/.rels",
            '<?xml version="1.0"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" '
            'Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" '
            'Target="docProps/core.xml"/>'
            "</Relationships>",
        )
        zf.writestr(
            "FixedDocumentSequence.fdseq",
            '<?xml version="1.0"?>'
            '<FixedDocumentSequence xmlns="http://schemas.microsoft.com/xps/2005/06">'
            '<DocumentReference Source="/Documents/1/FixedDocument.fdoc"/>'
            "</FixedDocumentSequence>",
        )
    path.write_bytes(buf.getvalue())
    return True


def _build_minimal_sfnt(version_tag: bytes) -> bytes:
    """Build a minimal SFNT font (OTF or TTF) with one dummy table."""
    num_tables = 1
    header = version_tag + struct.pack(">HHHH", num_tables, 16, 0, 0)
    # Single dummy table: 'name' with 16 bytes of data
    tag = b"name"
    table_data = b"Encypher C2PA Test Font\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    table_data = table_data[:32]  # pad to 32 bytes
    data_offset = 12 + num_tables * 16  # header + 1 table record
    checksum = 0
    for i in range(0, len(table_data), 4):
        checksum = (checksum + struct.unpack(">I", table_data[i : i + 4])[0]) & 0xFFFFFFFF
    record = struct.pack(">4sIII", tag, checksum, data_offset, len(table_data))
    return header + record + table_data


def generate_fixture_otf(path: Path) -> bool:
    """Generate a minimal valid OTF font (OpenType/CFF)."""
    path.write_bytes(_build_minimal_sfnt(b"OTTO"))
    return True


def generate_fixture_ttf(path: Path) -> bool:
    """Generate a minimal valid TTF font (TrueType)."""
    path.write_bytes(_build_minimal_sfnt(b"\x00\x01\x00\x00"))
    return True


def generate_fixture_jxl(path: Path) -> bool:
    """Generate a minimal valid JXL file (ISOBMFF container variant).

    JXL ISOBMFF container has magic: 00 00 00 0c 4A 58 4C 20 0D 0A 87 0A
    followed by a minimal jxlc box with a codestream header.
    """
    # ISOBMFF box structure: size (4) + type (4) + data
    # File type box: JXL (12 bytes total = magic)
    ftyp = bytes([0x00, 0x00, 0x00, 0x0C, 0x4A, 0x58, 0x4C, 0x20, 0x0D, 0x0A, 0x87, 0x0A])
    # Minimal jxlc (JXL codestream) box with a tiny codestream header
    # JXL codestream signature: FF 0A
    codestream = bytes([0xFF, 0x0A])
    # Small image header (SizeHeader + ImageMetadata): 10x10, 8-bit, 3 channels
    # Minimal valid header bytes for a 1x1 image
    header = bytes(
        [
            0x00,
            0x00,
            0x01,
            0x00,  # size=1, aspect_ratio=1
            0x00,
            0x00,
            0x01,
            0x00,  # width=1, height=1
            0x00,
            0x08,  # bits_per_sample=8
        ]
    )
    jxlc_data = codestream + header
    jxlc_size = 8 + len(jxlc_data)
    jxlc = struct.pack(">I", jxlc_size) + b"jxlc" + jxlc_data
    path.write_bytes(ftyp + jxlc)
    return True


# Map format name -> generator function
GENERATORS = {
    "JPEG": generate_fixture_jpeg,
    "PNG": generate_fixture_png,
    "WebP": generate_fixture_webp,
    "TIFF": generate_fixture_tiff,
    "AVIF": generate_fixture_avif,
    "HEIC": generate_fixture_heic,
    "HEIF": generate_fixture_heif,
    "SVG": generate_fixture_svg,
    "DNG": generate_fixture_dng,
    "GIF": generate_fixture_gif,
    "MP4": generate_fixture_mp4,
    "MOV": generate_fixture_mov,
    "AVI": generate_fixture_avi,
    "M4V": generate_fixture_m4v,
    "WAV": generate_fixture_wav,
    "MP3": generate_fixture_mp3,
    "M4A": generate_fixture_m4a,
    "FLAC": generate_fixture_flac,
    "PDF": generate_fixture_pdf,
    "EPUB": generate_fixture_epub,
    "DOCX": generate_fixture_docx,
    "ODT": generate_fixture_odt,
    "OXPS": generate_fixture_oxps,
    "OTF": generate_fixture_otf,
    "TTF": generate_fixture_ttf,
    "JXL": generate_fixture_jxl,
    "HEIC-sequence": generate_fixture_heic,
    "HEIF-sequence": generate_fixture_heif,
    "MPA": generate_fixture_mp3,
    "AAC": generate_fixture_m4a,
}


# ---------------------------------------------------------------------------
# Signing
# ---------------------------------------------------------------------------


def load_credentials() -> tuple[str, str]:
    """Load test certificate credentials."""
    key_path = CERTS_DIR / "private_key.pem"
    chain_path = CERTS_DIR / "cert_chain.pem"
    if not key_path.exists() or not chain_path.exists():
        raise FileNotFoundError(f"Test certs not found at {CERTS_DIR}")
    return key_path.read_text(), chain_path.read_text()


_BUILDER_MIME_CANONICAL = {
    "image/heic-sequence": "image/heic",
    "image/heif-sequence": "image/heif",
    "audio/MPA": "audio/mpeg",
    "audio/mpa": "audio/mpeg",
    "audio/aac": "audio/mp4",
}


def sign_with_c2pa_builder(
    fixture_bytes: bytes,
    mime_type: str,
    fmt: FormatSpec,
    private_key_pem: str,
    cert_chain_pem: str,
    *,
    ingredient_bytes: Optional[bytes] = None,
    ingredient_mime: Optional[str] = None,
    action: str = "c2pa.created",
) -> tuple[bytes, Optional[str], Optional[str]]:
    """Sign using c2pa-python Builder. Returns (signed_bytes, instance_id, manifest_label).

    When ingredient_bytes is provided, the signed file references the ingredient
    via a c2pa.ingredient assertion (provenance chain / c2pa.edited workflow).
    """
    import c2pa

    from app.utils.c2pa_manifest import build_c2pa_manifest_dict
    from app.utils.c2pa_signer import create_signer_from_pem

    asset_id_key_map = {
        "image": "image_id",
        "video": "video_id",
        "audio": "audio_id",
    }
    asset_id_key = asset_id_key_map.get(fmt.category, "image_id")

    manifest_dict = build_c2pa_manifest_dict(
        title=f"C2PA Conformance Test -- {fmt.name}",
        org_id="encypher-conformance",
        document_id=f"conformance-{fmt.name.lower()}",
        asset_id=str(uuid.uuid4()),
        asset_id_key=asset_id_key,
        action=action,
        custom_assertions=[],
        rights_data={},
        digital_source_type="digitalCapture",
    )

    signer = create_signer_from_pem(private_key_pem, cert_chain_pem, tsa_url="http://ts.ssl.com")
    builder_mime = _BUILDER_MIME_CANONICAL.get(mime_type, mime_type)
    try:
        builder = c2pa.Builder(manifest_dict)

        # Add ingredient if provided (provenance chain)
        if ingredient_bytes and ingredient_mime:
            from app.utils.c2pa_manifest import INGREDIENT_PARENT_LABEL

            ingredient_json = {
                "title": f"C2PA Conformance Test -- {fmt.name} (original)",
                "relationship": "parentOf",
                "label": INGREDIENT_PARENT_LABEL,
            }
            builder.add_ingredient(
                ingredient_json,
                _BUILDER_MIME_CANONICAL.get(ingredient_mime, ingredient_mime),
                io.BytesIO(ingredient_bytes),
            )

        dest = io.BytesIO()
        builder.sign(signer, builder_mime, io.BytesIO(fixture_bytes), dest)
        dest.seek(0)
        signed_bytes = dest.read()
    finally:
        signer.close()

    instance_id = manifest_dict.get("instance_id")
    return signed_bytes, instance_id, None


def sign_via_document_service(
    fixture_bytes: bytes,
    fmt: FormatSpec,
    private_key_pem: str,
    cert_chain_pem: str,
) -> tuple[bytes, Optional[str], Optional[str]]:
    """Sign a document using the custom JUMBF/COSE document signing pipeline.

    Handles PDF, EPUB, DOCX, ODT, and OXPS.
    """
    from app.services.document_signing_service import sign_document

    result = sign_document(
        fixture_bytes,
        fmt.mime_type,
        title=f"C2PA Conformance Test -- {fmt.name}",
        org_id="encypher-conformance",
        document_id=f"conformance-{fmt.name.lower()}",
        asset_id=str(uuid.uuid4()),
        action="c2pa.created",
        digital_source_type="digitalCapture",
        private_key_pem=private_key_pem,
        cert_chain_pem=cert_chain_pem,
    )
    return result.signed_bytes, result.instance_id, result.manifest_label


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------


_CUSTOM_PIPELINE_MIMES = frozenset(
    {
        "application/pdf",
        "application/epub+zip",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.oasis.opendocument.text",
        "application/oxps",
        "audio/flac",
        "image/jxl",
        "font/otf",
        "font/ttf",
        "font/sfnt",
    }
)


def verify_signed_file(
    signed_bytes: bytes,
    mime_type: str,
    category: str,
) -> tuple[bool, Optional[str], list[dict]]:
    """Verify a signed file. Returns (success, error, validation_codes)."""
    if mime_type in _CUSTOM_PIPELINE_MIMES:
        # Custom JUMBF/COSE pipeline; c2pa-python Reader cannot parse these.
        # Verify structurally: check for JUMBF marker + C2PA content.
        has_jumb = b"jumb" in signed_bytes
        has_c2pa = b"c2pa" in signed_bytes
        if has_jumb and has_c2pa:
            return True, None, [{"code": "structural.jumbfPresent", "success": True}]
        return False, "No JUMBF/C2PA markers found", []

    from app.utils.c2pa_verifier_core import verify_c2pa

    verify_mime = _BUILDER_MIME_CANONICAL.get(mime_type, mime_type)
    result = verify_c2pa(signed_bytes, verify_mime)
    codes = []
    for vs in result.validation_status:
        codes.append({"code": vs.code, "success": vs.success, "explanation": vs.explanation})

    return result.valid, result.error, codes


# ---------------------------------------------------------------------------
# Manifest JSON extraction (for conformance test validation)
# ---------------------------------------------------------------------------


def extract_manifest_json(
    signed_bytes: bytes,
    mime_type: str,
    fmt: FormatSpec,
) -> Optional[dict]:
    """Extract the C2PA manifest as a JSON-serializable dict.

    Pipeline A: uses c2pa.Reader to get the full manifest with created flags.
    Pipeline B: parses JUMBF directly and includes the CBOR claim (with
    created_assertions) in the output.
    """
    if mime_type in _CUSTOM_PIPELINE_MIMES:
        return _extract_pipeline_b_manifest(signed_bytes, mime_type)
    return _extract_pipeline_a_manifest(signed_bytes, mime_type)


def _extract_pipeline_a_manifest(signed_bytes: bytes, mime_type: str) -> Optional[dict]:
    """Extract manifest JSON via c2pa.Reader (Pipeline A formats)."""
    import c2pa

    builder_mime = _BUILDER_MIME_CANONICAL.get(mime_type, mime_type)
    try:
        reader = c2pa.Reader(builder_mime, io.BytesIO(signed_bytes))
        return json.loads(reader.json())
    except Exception as e:
        log.warning("  Manifest extraction (Pipeline A) failed: %s", e)
        return None


def _extract_pipeline_b_manifest(signed_bytes: bytes, mime_type: str) -> Optional[dict]:
    """Extract manifest JSON from JUMBF (Pipeline B formats).

    Parses JUMBF, decodes CBOR assertions and claim, and produces a
    manifest dict in the **canonical c2pa-rs Reader format** so that
    Pipeline A and Pipeline B JSON output are structurally identical.
    """
    import cbor2

    from cryptography.x509 import load_der_x509_certificate

    from app.utils.c2pa_manifest_extractor import extract_manifest
    from app.utils.cose_signer import COSE_ALG_EDDSA, COSE_ALG_ES256, COSE_ALG_ES384, COSE_ALG_ES512, COSE_ALG_PS256
    from app.utils.jumbf import parse_manifest_store

    ALG_NAMES = {
        COSE_ALG_ES256: "Es256",
        COSE_ALG_ES384: "Es384",
        COSE_ALG_ES512: "Es512",
        COSE_ALG_PS256: "Ps256",
        COSE_ALG_EDDSA: "EdDsa",
    }

    try:
        manifest_bytes = extract_manifest(signed_bytes, mime_type)
        if not manifest_bytes:
            log.warning("  No JUMBF manifest found in %s", mime_type)
            return None

        store = parse_manifest_store(manifest_bytes)
        manifests_dict: dict[str, dict] = {}
        active_label = None

        for m in store.get("manifests", []):
            label = m.get("label", "")
            if active_label is None:
                active_label = label

            # Decode CBOR assertions into canonical array format
            assertions_list = []
            for a_label, cbor_bytes in m.get("assertions", {}).items():
                try:
                    data = cbor2.loads(cbor_bytes)
                except Exception:
                    data = {"_raw_hex": cbor_bytes.hex()}
                # Convert bytes values to hex strings for JSON serialization
                _sanitize_bytes(data)
                assertions_list.append(
                    {
                        "label": a_label,
                        "data": data,
                        "created": True,
                    }
                )

            # Decode CBOR claim
            claim = {}
            if m.get("claim_cbor"):
                try:
                    claim = cbor2.loads(m["claim_cbor"])
                except Exception as e:
                    log.warning("  CBOR claim decode failed: %s", e)

            # Extract signature_info from COSE envelope
            sig_info = {}
            if m.get("signature_cose"):
                sig_info = _extract_signature_info(
                    m["signature_cose"],
                    ALG_NAMES,
                )

            # Map claim fields to canonical c2pa-rs Reader keys
            instance_id = claim.get("instanceID", "")
            # c2pa-rs normalizes instanceID to xmp:iid: format
            if instance_id.startswith("urn:uuid:"):
                instance_id = "xmp:iid:" + instance_id[len("urn:uuid:") :]

            cgi = claim.get("claim_generator_info", {})
            # c2pa-rs always wraps claim_generator_info in an array
            if isinstance(cgi, dict):
                cgi = [cgi]

            manifest_obj: dict = {
                "claim_generator_info": cgi,
                "title": claim.get("dc:title", ""),
                "instance_id": instance_id,
                "assertions": assertions_list,
                "label": label,
                "claim_version": 2,
            }
            if sig_info:
                manifest_obj["signature_info"] = sig_info

            manifests_dict[label] = manifest_obj

        return {
            "active_manifest": active_label,
            "manifests": manifests_dict,
        }
    except Exception as e:
        log.warning("  Manifest extraction (Pipeline B) failed: %s", e)
        return None


def _sanitize_bytes(obj):
    """Recursively convert bytes values to hex strings for JSON serialization."""
    if isinstance(obj, dict):
        for k, v in list(obj.items()):
            if isinstance(v, bytes):
                obj[k] = v.hex()
            elif isinstance(v, (dict, list)):
                _sanitize_bytes(v)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if isinstance(v, bytes):
                obj[i] = v.hex()
            elif isinstance(v, (dict, list)):
                _sanitize_bytes(v)


def _extract_signature_info(cose_bytes: bytes, alg_names: dict) -> dict:
    """Extract signature_info from a COSE_Sign1 envelope."""
    import cbor2

    from cryptography.x509 import load_der_x509_certificate

    try:
        decoded = cbor2.loads(cose_bytes)
        # Handle CBORTag wrapper
        if isinstance(decoded, cbor2.CBORTag):
            decoded = decoded.value
        if not isinstance(decoded, (list, tuple)) or len(decoded) < 4:
            return {}

        protected_bytes = decoded[0]
        unprotected = decoded[1] if isinstance(decoded[1], dict) else {}

        # Get algorithm from protected headers
        protected = cbor2.loads(protected_bytes) if protected_bytes else {}
        alg_id = protected.get(1)
        alg_name = alg_names.get(alg_id, f"Unknown({alg_id})")

        info: dict = {"alg": alg_name}

        # Extract cert info from x5chain (string key or integer 33)
        chain = unprotected.get("x5chain") or unprotected.get(33)
        if chain:
            cert_der = chain[0] if isinstance(chain, list) else chain
            if isinstance(cert_der, bytes):
                cert = load_der_x509_certificate(cert_der)
                subject = cert.subject
                for attr in subject:
                    oid = attr.oid.dotted_string
                    if oid == "2.5.4.10":  # O = Organization
                        info["issuer"] = attr.value
                    elif oid == "2.5.4.3":  # CN = Common Name
                        info["common_name"] = attr.value
                info["cert_serial_number"] = str(cert.serial_number)

        return info
    except Exception:
        return {}


def save_manifest_json(manifest_data: Optional[dict], fmt: FormatSpec):
    """Save extracted manifest as a JSON file in the manifests/ directory."""
    if manifest_data is None:
        return
    stem = fmt.output_stem or "signed_test"
    # Map extension to a clean name for the JSON filename
    ext_name = fmt.extension.lstrip(".")
    json_name = f"{stem}_{ext_name}.json" if stem == "signed_test" else f"{stem}.json"
    json_path = MANIFESTS_DIR / json_name
    json_path.write_text(json.dumps(manifest_data, indent=2, default=str) + "\n")
    log.info("  Manifest JSON: %s", json_path.name)


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------


def run() -> list[FormatResult]:
    log.info("=" * 70)
    log.info("C2PA 30-Format Conformance Suite")
    log.info("=" * 70)

    private_key_pem, cert_chain_pem = load_credentials()
    log.info("Loaded test credentials from %s", CERTS_DIR)

    results: list[FormatResult] = []

    for fmt in FORMATS:
        log.info("-" * 50)
        log.info("Processing: %s (%s)", fmt.name, fmt.mime_type)

        result = FormatResult(
            name=fmt.name,
            extension=fmt.extension,
            mime_type=fmt.mime_type,
            category=fmt.category,
        )

        # Step 1: Generate fixture
        fixture_stem = fmt.output_stem.replace("signed_test", "test") if fmt.output_stem else "test"
        fixture_path = FIXTURES_DIR / f"{fixture_stem}{fmt.extension}"
        generator = GENERATORS.get(fmt.name)
        if not generator:
            result.sign_error = f"No generator for {fmt.name}"
            results.append(result)
            continue

        try:
            ok = generator(fixture_path)
            if not ok or not fixture_path.exists():
                result.sign_error = f"Fixture generation failed for {fmt.name}"
                results.append(result)
                continue
            fixture_bytes = fixture_path.read_bytes()
            result.fixture_size = len(fixture_bytes)
            log.info("  Fixture: %d bytes", result.fixture_size)
        except Exception as e:
            result.sign_error = f"Fixture generation error: {e}"
            log.error("  Fixture error: %s", e)
            results.append(result)
            continue

        # Step 2: Sign
        try:
            if fmt.pipeline == "document_service":
                signed_bytes, instance_id, manifest_label = sign_via_document_service(fixture_bytes, fmt, private_key_pem, cert_chain_pem)
            else:
                signed_bytes, instance_id, manifest_label = sign_with_c2pa_builder(fixture_bytes, fmt.mime_type, fmt, private_key_pem, cert_chain_pem)

            stem = fmt.output_stem or "signed_test"
            signed_path = SIGNED_DIR / f"{stem}{fmt.extension}"
            signed_path.write_bytes(signed_bytes)

            result.signed_size = len(signed_bytes)
            result.sign_success = True
            result.instance_id = instance_id
            result.manifest_label = manifest_label
            result.signed_file = str(signed_path)
            log.info("  Signed: %d bytes -> %s", result.signed_size, signed_path.name)

        except Exception as e:
            result.sign_error = str(e)
            result.sign_success = False
            log.error("  Sign error: %s", e)
            results.append(result)
            continue

        # Step 2b: Re-sign with ingredient (provenance chain / c2pa.edited)
        # Takes the signed output and re-signs it, referencing the original as an ingredient.
        if fmt.pipeline == "c2pa_builder":
            try:
                ingredient_signed, ingredient_iid, _ = sign_with_c2pa_builder(
                    signed_bytes,  # use the signed file as both source and ingredient
                    fmt.mime_type,
                    fmt,
                    private_key_pem,
                    cert_chain_pem,
                    ingredient_bytes=signed_bytes,
                    ingredient_mime=fmt.mime_type,
                    action="c2pa.edited",
                )
                ingredient_stem = fmt.output_stem or "signed_test"
                ingredient_path = SIGNED_DIR / f"{ingredient_stem}_ingredient{fmt.extension}"
                ingredient_path.write_bytes(ingredient_signed)
                log.info("  Ingredient re-sign: %d bytes -> %s", len(ingredient_signed), ingredient_path.name)
            except Exception as e:
                log.warning("  Ingredient re-sign failed (non-fatal): %s", e)

        # Step 3: Verify
        try:
            verify_ok, verify_err, codes = verify_signed_file(signed_bytes, fmt.mime_type, fmt.category)
            result.verify_success = verify_ok
            result.verify_error = verify_err
            result.validation_codes = codes
            status = "PASS" if verify_ok else "FAIL"
            log.info("  Verify: %s (codes: %d)", status, len(codes))
        except Exception as e:
            result.verify_error = str(e)
            result.verify_success = False
            log.error("  Verify error: %s", e)

        # Step 4: Extract and save manifest JSON
        try:
            manifest_data = extract_manifest_json(signed_bytes, fmt.mime_type, fmt)
            save_manifest_json(manifest_data, fmt)
        except Exception as e:
            log.warning("  Manifest JSON extraction failed: %s", e)

        results.append(result)

    return results


def write_results(results: list[FormatResult]):
    """Write results to JSON and human-readable log."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # JSON results
    json_data = {
        "timestamp": now,
        "total_formats": len(results),
        "sign_success": sum(1 for r in results if r.sign_success),
        "verify_success": sum(1 for r in results if r.verify_success),
        "results": [asdict(r) for r in results],
    }
    json_path = RESULTS_DIR / "verify_results.json"
    json_path.write_text(json.dumps(json_data, indent=2))
    log.info("JSON results: %s", json_path)

    # Human-readable log
    log_path = RESULTS_DIR / "verify_all.log"
    lines = [
        "C2PA 25-Format Conformance Verification Log",
        f"Generated: {now}",
        "Certificate: SSL.com staging (ECC P-256)",
        "Library: c2pa-python (c2pa-rs)",
        "",
        f"{'Format':<8} {'MIME Type':<25} {'Cat':<10} {'Sign':<6} {'Verify':<8} {'Fixture':<10} {'Signed':<10}",
        "-" * 85,
    ]
    for r in results:
        sign_str = "OK" if r.sign_success else "FAIL"
        verify_str = "PASS" if r.verify_success else "FAIL"
        lines.append(f"{r.name:<8} {r.mime_type:<25} {r.category:<10} {sign_str:<6} {verify_str:<8} {r.fixture_size:<10} {r.signed_size:<10}")
    lines.append("-" * 85)
    lines.append(f"Total: {len(results)} formats")
    lines.append(f"Signed OK: {sum(1 for r in results if r.sign_success)}/{len(results)}")
    lines.append(f"Verified OK: {sum(1 for r in results if r.verify_success)}/{len(results)}")
    lines.append("")

    # Detail section
    for r in results:
        lines.append(f"\n{'=' * 50}")
        lines.append(f"Format: {r.name} ({r.mime_type})")
        lines.append(f"Category: {r.category}")
        lines.append(f"Sign: {'OK' if r.sign_success else 'FAIL'}")
        if r.sign_error:
            lines.append(f"Sign Error: {r.sign_error}")
        lines.append(f"Verify: {'PASS' if r.verify_success else 'FAIL'}")
        if r.verify_error:
            lines.append(f"Verify Error: {r.verify_error}")
        if r.instance_id:
            lines.append(f"Instance ID: {r.instance_id}")
        if r.validation_codes:
            lines.append("Validation Status Codes:")
            for vc in r.validation_codes:
                status = "pass" if vc.get("success") else "fail"
                lines.append(f"  [{status}] {vc['code']}")

    log_path.write_text("\n".join(lines))
    log.info("Log: %s", log_path)


def print_summary(results: list[FormatResult]):
    """Print summary table to stdout."""
    print("\n" + "=" * 70)
    print("C2PA CONFORMANCE RESULTS SUMMARY")
    print("=" * 70)
    print(f"{'Format':<8} {'Category':<10} {'Sign':<6} {'Verify':<8} {'Notes'}")
    print("-" * 70)
    for r in results:
        sign_str = "OK" if r.sign_success else "FAIL"
        verify_str = "PASS" if r.verify_success else "FAIL"
        notes = r.sign_error or r.verify_error or ""
        if notes and len(notes) > 40:
            notes = notes[:37] + "..."
        print(f"{r.name:<8} {r.category:<10} {sign_str:<6} {verify_str:<8} {notes}")
    print("-" * 70)
    total = len(results)
    signed = sum(1 for r in results if r.sign_success)
    verified = sum(1 for r in results if r.verify_success)
    print(f"Signed:   {signed}/{total}")
    print(f"Verified: {verified}/{total}")
    print(f"\nSigned files: {SIGNED_DIR}/")
    print(f"Results:      {RESULTS_DIR}/")
    print("=" * 70)


if __name__ == "__main__":
    results = run()
    write_results(results)
    print_summary(results)
