"""PDF Generation utilities for EncypherAI.

This module provides a thin wrapper around ReportLab to generate PDFs
with text that has been watermarked using :class:`UnicodeMetadata`.

Fonts can be registered from external TrueType files to ensure proper
Unicode rendering. By default, the built-in Helvetica font is used, but
users are encouraged to supply a full Unicode font for the best results.
"""

from __future__ import annotations

from typing import Callable, Literal, Optional, Tuple, Union

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from .core.payloads import BasicPayload, C2PAPayload, ManifestPayload
from .core.unicode_metadata import MetadataTarget, UnicodeMetadata


class EncypherPDF:
    """Utility class for creating and verifying PDFs with embedded metadata."""

    @staticmethod
    def from_text(
        text: str,
        output_path: str,
        *,
        private_key: PrivateKeyTypes,
        signer_id: str,
        timestamp: Union[str, int, float],
        metadata_format: Literal["basic", "manifest", "cbor_manifest", "c2pa_v2_2"] = "c2pa_v2_2",
        font_path: Optional[str] = None,
        font_name: str = "Helvetica",
        font_size: int = 12,
        claim_generator: Optional[str] = None,
        actions: Optional[list[dict[str, object]]] = None,
        target: Optional[Union[str, MetadataTarget]] = None,
        distribute_across_targets: bool = False,
        add_hard_binding: bool = True,
    ) -> str:
        """Generate a PDF from text with embedded metadata.

        Parameters
        ----------
        text:
            The source text to encode and render.
        output_path:
            Destination file path for the PDF.
        private_key:
            Ed25519 private key used for signing the metadata.
        signer_id:
            Identifier used to look up the public key during verification.
        timestamp:
            Timestamp used in the embedded metadata.
        metadata_format:
            Metadata format passed to :func:`UnicodeMetadata.embed_metadata`.
        font_path:
            Optional path to a TrueType font to register for full Unicode
            rendering. If omitted, the built-in Helvetica font is used.
        font_name:
            Internal font name used by ReportLab after registration.
        font_size:
            Font size in points.
        claim_generator, actions, target, distribute_across_targets, add_hard_binding:
            Additional options forwarded to :func:`UnicodeMetadata.embed_metadata`.

        Returns
        -------
        str
            The path of the generated PDF.
        """

        embedded_text = UnicodeMetadata.embed_metadata(
            text=text,
            private_key=private_key,
            signer_id=signer_id,
            metadata_format=metadata_format,
            timestamp=timestamp,
            claim_generator=claim_generator,
            actions=actions,
            target=target,
            distribute_across_targets=distribute_across_targets,
            add_hard_binding=add_hard_binding,
        )

        if font_path:
            pdfmetrics.registerFont(TTFont(font_name, font_path))

        c = canvas.Canvas(output_path, pagesize=LETTER)
        c.setFont(font_name, font_size)
        width, height = LETTER
        text_object = c.beginText(72, height - 72)
        for line in embedded_text.splitlines():
            text_object.textLine(line)
        c.drawText(text_object)
        c.showPage()
        c.save()
        return output_path

    @staticmethod
    def extract_text(pdf_path: str) -> str:
        """Extract raw text from a PDF file using :mod:`PyMuPDF`."""

        import fitz  # PyMuPDF

        doc = fitz.open(pdf_path)
        text = "".join(page.get_text() for page in doc)
        doc.close()
        return text

    @staticmethod
    def verify_pdf(
        pdf_path: str,
        public_key_resolver: Callable[[str], Optional[Ed25519PublicKey]],
        *,
        require_hard_binding: bool = True,
    ) -> Tuple[bool, Optional[str], Union[BasicPayload, ManifestPayload, C2PAPayload, None]]:
        """Verify metadata embedded in a PDF file."""
        text = EncypherPDF.extract_text(pdf_path)
        return UnicodeMetadata.verify_metadata(
            text,
            public_key_resolver=public_key_resolver,
            require_hard_binding=require_hard_binding,
        )
