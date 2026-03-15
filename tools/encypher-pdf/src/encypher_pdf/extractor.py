from __future__ import annotations

import re
import zlib
from pathlib import Path


class PdfExtractionError(Exception):
    pass


def _read_bytes(pdf_path: str | Path) -> bytes:
    path = Path(pdf_path)
    if not path.exists():
        raise PdfExtractionError(f"PDF not found: {path}")
    return path.read_bytes()


def _find_stream_object_bytes(pdf_bytes: bytes, object_number: int) -> tuple[bytes, bool]:
    marker = f"{object_number} 0 obj".encode("latin-1")
    obj_idx = pdf_bytes.find(marker)
    if obj_idx == -1:
        raise PdfExtractionError(f"Could not locate object {object_number} in PDF")

    stream_marker = b"stream\n"
    stream_idx = pdf_bytes.find(stream_marker, obj_idx)
    marker_len = len(stream_marker)
    if stream_idx == -1:
        stream_marker = b"stream\r\n"
        stream_idx = pdf_bytes.find(stream_marker, obj_idx)
        marker_len = len(stream_marker)
    if stream_idx == -1:
        raise PdfExtractionError(f"Could not locate stream for object {object_number}")

    end_marker = b"endstream"
    end_idx = pdf_bytes.find(end_marker, stream_idx)
    if end_idx == -1:
        raise PdfExtractionError(f"Could not locate endstream for object {object_number}")

    dict_region = pdf_bytes[obj_idx:stream_idx]
    stream_bytes = pdf_bytes[stream_idx + marker_len : end_idx]
    stream_bytes = stream_bytes.rstrip(b"\r\n")
    compressed = b"FlateDecode" in dict_region
    return stream_bytes, compressed


def extract_signed_text(pdf_path: str | Path) -> str | None:
    pdf_bytes = _read_bytes(pdf_path)
    marker = b"EncypherSignedText"
    marker_idx = pdf_bytes.find(marker)
    if marker_idx == -1:
        return None

    ref_region = pdf_bytes[marker_idx + len(marker) : marker_idx + len(marker) + 40].decode("latin-1", errors="replace")
    ref_match = re.search(r"\s+(\d+)\s+0\s+R", ref_region)
    if not ref_match:
        raise PdfExtractionError("Could not parse EncypherSignedText object reference")

    object_number = int(ref_match.group(1))
    stream_bytes, compressed = _find_stream_object_bytes(pdf_bytes, object_number)
    if compressed:
        try:
            stream_bytes = zlib.decompress(stream_bytes)
        except zlib.error as exc:
            raise PdfExtractionError("Could not decompress EncypherSignedText stream") from exc

    try:
        return stream_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PdfExtractionError("Could not decode EncypherSignedText stream as UTF-8") from exc


def extract_text_pymupdf(pdf_path: str | Path) -> str:
    try:
        import fitz
    except ImportError as exc:
        raise PdfExtractionError("PyMuPDF is required for extractor-based text extraction") from exc

    doc = fitz.open(str(pdf_path))
    try:
        return "\n".join(page.get_text() for page in doc)
    finally:
        doc.close()


def extract_text(pdf_path: str | Path, *, prefer_signed_stream: bool = True) -> str:
    if prefer_signed_stream:
        signed = extract_signed_text(pdf_path)
        if signed is not None:
            return signed
    return extract_text_pymupdf(pdf_path)
