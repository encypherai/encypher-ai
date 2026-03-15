from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from encypher_pdf.extractor import extract_signed_text


class PdfInspectionError(Exception):
    pass


def inspect_pdf(pdf_path: str | Path) -> dict[str, Any]:
    try:
        import fitz
    except ImportError as exc:
        raise PdfInspectionError("PyMuPDF is required for PDF inspection") from exc

    path = Path(pdf_path)
    if not path.exists():
        raise PdfInspectionError(f"PDF not found: {path}")

    doc = fitz.open(str(path))
    try:
        fonts: dict[str, dict[str, Any]] = {}
        tounicode_entries: list[dict[str, int]] = []
        invisible_codepoints: set[int] = set()
        content_streams = 0

        for page_index in range(doc.page_count):
            page = doc[page_index]
            for font in page.get_fonts(full=True):
                xref = int(font[0])
                fonts[str(xref)] = {
                    "xref": xref,
                    "basefont": font[3],
                    "name": font[4],
                    "encoding": font[5],
                }
            content_streams += len(page.get_contents())

        for i in range(1, doc.xref_length()):
            try:
                stream = doc.xref_stream(i)
            except Exception:
                continue
            if not stream or b"beginbfchar" not in stream:
                continue
            text = stream.decode("ascii", errors="replace")
            matches = re.findall(r"<([0-9A-Fa-f]+)>\s+<([0-9A-Fa-f]+)>", text)
            for gid_hex, cp_hex in matches:
                cp_value = int(cp_hex, 16)
                tounicode_entries.append({"gid": int(gid_hex, 16), "unicode": cp_value})
                if (
                    0xFE00 <= cp_value <= 0xFE0F
                    or 0xE0100 <= cp_value <= 0xE01EF
                    or cp_value in {0x200B, 0x200C, 0x200D, 0xFEFF, 0x034F, 0x180E, 0x00AD, 0x000A}
                ):
                    invisible_codepoints.add(cp_value)

        signed_text = extract_signed_text(path)
        return {
            "path": str(path),
            "page_count": doc.page_count,
            "content_stream_count": content_streams,
            "fonts": sorted(fonts.values(), key=lambda item: item["xref"]),
            "font_count": len(fonts),
            "has_signed_text_stream": signed_text is not None,
            "signed_text_length": len(signed_text) if signed_text is not None else 0,
            "tounicode_entry_count": len(tounicode_entries),
            "invisible_codepoints": sorted(invisible_codepoints),
        }
    finally:
        doc.close()
