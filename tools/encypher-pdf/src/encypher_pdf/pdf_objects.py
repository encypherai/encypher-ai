# TEAM_154: Low-level PDF object serialization
"""
Minimal PDF object model for writing valid PDF files.
Handles object numbering, cross-reference table, and stream encoding.
"""

from __future__ import annotations

import zlib
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PdfStream:
    """A PDF stream object with optional deflate compression."""

    data: bytes
    extra_dict: dict[str, str] = field(default_factory=dict)
    compress: bool = True

    def serialize_dict_and_body(self) -> bytes:
        body = self.data
        entries = dict(self.extra_dict)
        if self.compress:
            body = zlib.compress(body)
            entries["Filter"] = "/FlateDecode"
        entries["Length"] = str(len(body))
        dict_str = " ".join(f"/{k} {v}" for k, v in entries.items())
        return f"<< {dict_str} >>\nstream\n".encode() + body + b"\nendstream"


class PdfWriter:
    """
    Accumulates PDF objects and writes a valid PDF file.

    Usage:
        w = PdfWriter()
        catalog_id = w.add_object(b"<< /Type /Catalog /Pages 2 0 R >>")
        ...
        w.write(path)
    """

    def __init__(self) -> None:
        self._objects: list[bytes] = []

    @property
    def next_id(self) -> int:
        """The object number that will be assigned to the next add_object call."""
        return len(self._objects) + 1

    def reserve_id(self) -> int:
        """Reserve an object ID without adding content yet."""
        self._objects.append(b"")
        return len(self._objects)

    def set_object(self, obj_id: int, content: bytes) -> None:
        """Set the content of a previously reserved object."""
        self._objects[obj_id - 1] = content

    def add_object(self, content: bytes) -> int:
        """Add a PDF object and return its 1-based object number."""
        self._objects.append(content)
        return len(self._objects)

    def add_stream(self, stream: PdfStream) -> int:
        """Add a stream object and return its object number."""
        return self.add_object(stream.serialize_dict_and_body())

    def ref(self, obj_id: int) -> str:
        """Return an indirect reference string like '4 0 R'."""
        return f"{obj_id} 0 R"

    def write(self, path: str) -> None:
        """Write the complete PDF to a file."""
        buf = bytearray()
        buf.extend(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

        offsets: list[int] = []
        for i, obj_content in enumerate(self._objects):
            offsets.append(len(buf))
            obj_num = i + 1
            buf.extend(f"{obj_num} 0 obj\n".encode())
            buf.extend(obj_content)
            buf.extend(b"\nendobj\n\n")

        xref_offset = len(buf)
        num_objects = len(self._objects) + 1  # +1 for the free entry
        buf.extend(b"xref\n")
        buf.extend(f"0 {num_objects}\n".encode())
        buf.extend(b"0000000000 65535 f \n")
        for offset in offsets:
            buf.extend(f"{offset:010d} 00000 n \n".encode())

        buf.extend(b"trailer\n")
        buf.extend(f"<< /Size {num_objects} /Root 1 0 R >>\n".encode())
        buf.extend(b"startxref\n")
        buf.extend(f"{xref_offset}\n".encode())
        buf.extend(b"%%EOF\n")

        with open(path, "wb") as f:
            f.write(buf)
