"""C2PA manifest embedding for PDF documents.

Per C2PA spec, the manifest is stored as an embedded file stream with:
  - Subtype: application/c2pa
  - AFRelationship: C2PA_Manifest
  - Referenced from the document catalog AF array

Content binding uses c2pa.hash.data with exclusion ranges for the
manifest byte range.

Two-pass approach:
  1. Add embedded file stream with zero-filled placeholder
  2. Determine byte range of the placeholder
  3. Hash the PDF excluding the placeholder range
  4. Build and sign the manifest
  5. Replace placeholder with actual manifest bytes
"""

import hashlib
import io
import logging
from typing import Optional

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    ArrayObject,
    DecodedStreamObject,
    DictionaryObject,
    NameObject,
    NumberObject,
    TextStringObject,
)

_log = logging.getLogger(__name__)

# Marker to find the placeholder in PDF bytes
_PLACEHOLDER_MARKER = b"C2PA_MANIFEST_PLACEHOLDER_START"
_PLACEHOLDER_END = b"C2PA_MANIFEST_PLACEHOLDER_END"


def _compute_hash_with_exclusions(
    data: bytes,
    exclusions: list[dict],
    alg: str = "sha256",
) -> bytes:
    """Compute hash of data, skipping exclusion byte ranges."""
    h = hashlib.new(alg)
    pos = 0
    for excl in sorted(exclusions, key=lambda e: e["start"]):
        start = excl["start"]
        length = excl["length"]
        if pos < start:
            h.update(data[pos:start])
        pos = start + length
    if pos < len(data):
        h.update(data[pos:])
    return h.digest()


def create_pdf_with_placeholder(pdf_bytes: bytes, placeholder_size: int = 32768) -> tuple[bytes, int, int]:
    """Add a C2PA manifest placeholder as an embedded file stream in the PDF.

    Args:
        pdf_bytes: Original PDF bytes.
        placeholder_size: Size of the zero-filled placeholder.

    Returns:
        Tuple of (new_pdf_bytes, placeholder_start_offset, placeholder_length).
    """
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()
    writer.append_pages_from_reader(reader)

    # Create the placeholder content with markers for easy detection
    # The actual manifest bytes will replace this
    inner_size = placeholder_size - len(_PLACEHOLDER_MARKER) - len(_PLACEHOLDER_END)
    placeholder_content = _PLACEHOLDER_MARKER + b"\x00" * max(0, inner_size) + _PLACEHOLDER_END

    # Create embedded file stream
    ef_stream = DecodedStreamObject()
    ef_stream.set_data(placeholder_content)
    ef_stream.update(
        {
            NameObject("/Type"): NameObject("/EmbeddedFile"),
            NameObject("/Subtype"): NameObject("/application#2Fc2pa"),
        }
    )

    # Create file specification dictionary
    filespec = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Filespec"),
            NameObject("/F"): TextStringObject("content_credential.c2pa"),
            NameObject("/UF"): TextStringObject("content_credential.c2pa"),
            NameObject("/AFRelationship"): NameObject("/C2PA_Manifest"),
            NameObject("/Desc"): TextStringObject("C2PA Manifest Store"),
            NameObject("/EF"): DictionaryObject(
                {
                    NameObject("/F"): writer._add_object(ef_stream),
                }
            ),
        }
    )

    filespec_ref = writer._add_object(filespec)

    # Add AF entry to document catalog
    catalog = writer._root_object
    if "/AF" in catalog:
        af_array = catalog["/AF"]
        af_array.append(filespec_ref)
    else:
        catalog[NameObject("/AF")] = ArrayObject([filespec_ref])

    # Also add to EmbeddedFiles name tree
    if "/Names" not in catalog:
        catalog[NameObject("/Names")] = DictionaryObject()
    names = catalog["/Names"]
    if not isinstance(names, DictionaryObject):
        names = DictionaryObject()
        catalog[NameObject("/Names")] = names

    ef_names = ArrayObject([TextStringObject("content_credential.c2pa"), filespec_ref])
    names_obj = names.get_object() if hasattr(names, "get_object") else names
    if isinstance(names_obj, DictionaryObject):
        names_obj[NameObject("/EmbeddedFiles")] = DictionaryObject({NameObject("/Names"): ef_names})

    # Write PDF to bytes
    buf = io.BytesIO()
    writer.write(buf)
    pdf_output = buf.getvalue()

    # Find the placeholder location
    marker_start = pdf_output.find(_PLACEHOLDER_MARKER)
    if marker_start == -1:
        raise RuntimeError("Could not locate placeholder marker in PDF output")
    marker_end = pdf_output.find(_PLACEHOLDER_END, marker_start)
    if marker_end == -1:
        raise RuntimeError("Could not locate placeholder end marker in PDF output")

    placeholder_start = marker_start
    placeholder_length = (marker_end + len(_PLACEHOLDER_END)) - marker_start

    return pdf_output, placeholder_start, placeholder_length


def compute_pdf_hash(
    pdf_bytes: bytes,
    exclusion_start: int,
    exclusion_length: int,
    alg: str = "sha256",
) -> bytes:
    """Compute hash of PDF bytes, excluding the manifest byte range."""
    exclusions = [{"start": exclusion_start, "length": exclusion_length}]
    return _compute_hash_with_exclusions(pdf_bytes, exclusions, alg)


def replace_manifest_in_pdf(
    pdf_bytes: bytes,
    manifest_bytes: bytes,
    placeholder_start: int,
    placeholder_length: int,
) -> bytes:
    """Replace the placeholder with actual manifest bytes in the PDF.

    The manifest must fit within the placeholder. If it doesn't, the caller
    should retry with a larger placeholder_size.

    Args:
        pdf_bytes: PDF bytes containing the placeholder.
        manifest_bytes: Actual C2PA manifest store bytes.
        placeholder_start: Byte offset of the placeholder.
        placeholder_length: Length of the placeholder.

    Returns:
        Updated PDF bytes with manifest embedded.

    Raises:
        ValueError: If manifest is larger than the placeholder.
    """
    if len(manifest_bytes) > placeholder_length:
        raise ValueError(
            f"Manifest ({len(manifest_bytes)} bytes) exceeds placeholder " f"({placeholder_length} bytes). Retry with larger placeholder."
        )

    # Pad manifest to exactly fill the placeholder
    padded = manifest_bytes + b"\x00" * (placeholder_length - len(manifest_bytes))

    return pdf_bytes[:placeholder_start] + padded + pdf_bytes[placeholder_start + placeholder_length :]
