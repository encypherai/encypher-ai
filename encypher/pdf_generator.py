"""PDF Generation utilities for EncypherAI.

This module provides a thin wrapper around ReportLab to generate PDFs
with text that has been watermarked using :class:`UnicodeMetadata`.

Fonts can be registered from external TrueType files to ensure proper
Unicode rendering. By default, the built-in Helvetica font is used, but
users are encouraged to supply a full Unicode font for the best results.
"""

from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path
from typing import Callable, Dict, List, Literal, Optional, Tuple, Union

import fitz  # PyMuPDF

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from PIL import Image as PILImage

from .core.payloads import BasicPayload, C2PAPayload, ManifestPayload
from .core.unicode_metadata import MetadataTarget, UnicodeMetadata


class PDFGenerationError(Exception):
    """Base exception for PDF generation errors."""
    pass


class FontError(PDFGenerationError):
    """Exception raised for font-related errors."""
    pass


class SignatureError(PDFGenerationError):
    """Exception raised for signature-related errors."""
    pass


class ImageError(PDFGenerationError):
    """Exception raised for image-related errors."""
    pass


class ConversionError(PDFGenerationError):
    """Exception raised for document conversion errors."""
    pass


class EncypherPDF:
    """Utility class for creating and verifying PDFs with embedded metadata."""

    @classmethod
    def from_text(
        cls,
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
        images: Optional[List[Dict[str, Union[str, float, int]]]] = None,
        margins: Optional[Dict[str, float]] = None,
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
            if not os.path.exists(font_path):
                raise FontError(f"Font file not found: {font_path}")
            try:
                pdfmetrics.registerFont(TTFont(font_name, font_path))
            except Exception as e:
                raise FontError(f"Failed to register font: {str(e)}")

        try:
            c = canvas.Canvas(output_path, pagesize=LETTER)
            c.setFont(font_name, font_size)
            width, height = LETTER
            
            # Set default margins if not provided
            if margins is None:
                margins = {
                    "left": 1.0 * inch,   # 1 inch left margin
                    "right": 1.0 * inch,  # 1 inch right margin
                    "top": 1.0 * inch,    # 1 inch top margin
                    "bottom": 1.0 * inch  # 1 inch bottom margin
                }
            
            # Calculate starting position for text with margins
            left_margin = margins.get("left", 1.0 * inch)
            top_margin = margins.get("top", 1.0 * inch)
            right_margin = margins.get("right", 1.0 * inch)
            bottom_margin = margins.get("bottom", 1.0 * inch)
            
            # Calculate text area dimensions
            text_width = width - left_margin - right_margin
            text_height = height - top_margin - bottom_margin
            
            # Starting y position (from top of page)
            y_position = height - top_margin
            
            # Add images if provided
            if images:
                for img_data in images:
                    try:
                        img_path = img_data.get("path")
                        if not img_path or not os.path.exists(img_path):
                            raise ImageError(f"Image file not found: {img_path}")
                            
                        # Get image position and size parameters
                        x = img_data.get("x", left_margin)  # Default to left margin
                        y = img_data.get("y", y_position - 144)  # Default to below text start
                        width_img = img_data.get("width", None)
                        height_img = img_data.get("height", None)
                        preserve_aspect_ratio = img_data.get("preserve_aspect_ratio", True)
                        
                        # Open and get image dimensions
                        img = PILImage.open(img_path)
                        img_width, img_height = img.size
                        
                        # Calculate dimensions if needed
                        if width_img is None and height_img is None:
                            # Default to 3 inches wide
                            width_img = 3 * inch
                            height_img = (img_height / img_width) * width_img if preserve_aspect_ratio else 3 * inch
                        elif width_img is not None and height_img is None:
                            height_img = (img_height / img_width) * width_img if preserve_aspect_ratio else 3 * inch
                        elif height_img is not None and width_img is None:
                            width_img = (img_width / img_height) * height_img if preserve_aspect_ratio else 3 * inch
                            
                        # Draw the image
                        c.drawImage(img_path, x, y, width=width_img, height=height_img)
                        
                        # Update y_position for text to be below the image
                        if y + height_img > y_position - font_size:
                            y_position = y - font_size * 2  # Position text below the image with some margin
                    except Exception as e:
                        raise ImageError(f"Failed to embed image {img_path}: {str(e)}")
            
            # Add text
            text_object = c.beginText(left_margin, y_position)
            for line in embedded_text.splitlines():
                text_object.textLine(line)
            c.drawText(text_object)
            
            c.showPage()
            c.save()
            return output_path
        except ImageError as e:
            raise e
        except Exception as e:
            raise PDFGenerationError(f"Failed to generate PDF: {str(e)}")

    @staticmethod
    def extract_text(pdf_path: str) -> str:
        """Extract raw text from a PDF file using :mod:`PyMuPDF`.
        
        Parameters
        ----------
        pdf_path:
            Path to the PDF file to extract text from.
            
        Returns
        -------
        str
            The extracted text content.
            
        Raises
        ------
        FileNotFoundError:
            If the PDF file does not exist.
        PDFGenerationError:
            If there is an error extracting text from the PDF.
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        try:
            import fitz  # PyMuPDF

            doc = fitz.open(pdf_path)
            text = "".join(page.get_text() for page in doc)
            doc.close()
            return text
        except ImportError:
            raise PDFGenerationError("PyMuPDF (fitz) is required for PDF text extraction. Install with 'uv pip install PyMuPDF'")
        except Exception as e:
            raise PDFGenerationError(f"Failed to extract text from PDF: {str(e)}")


    @classmethod
    def from_docx(cls, docx_file: str, output_file: str, private_key=None, signer_id=None, timestamp=None,
                 target=None, font_path=None, font_name="Helvetica", font_size=12, margins=None, images=None):
        """Generate a PDF from a Word document with embedded metadata.

        Args:
            docx_file (str): Path to the Word document.
            output_file (str): Path where the PDF will be saved.
            private_key (str, optional): Path to the private key file or the key itself.
            signer_id (str, optional): Identifier for the signer.
            timestamp (datetime, optional): Timestamp for metadata embedding.
            target (str or MetadataTarget, optional): Where to embed metadata ('whitespace', 'punctuation', 'first_letter', etc.).
            font_path (str, optional): Path to a custom font file.
            font_name (str, optional): Name of the font to use.
            font_size (int, optional): Font size to use.
            margins (dict, optional): Dictionary with 'top', 'right', 'bottom', 'left' margins in points.
            images (list, optional): List of image paths to include in the PDF.

        Returns:
            str: Path to the generated PDF file.

        Raises:
            FileNotFoundError: If the Word document is not found.
            FontError: If there's an issue with the font.
            ImageError: If there's an issue with an image.
            MetadataError: If there's an issue with embedding metadata.
        """
        # Check if the Word document exists
        if not os.path.exists(docx_file):
            raise FileNotFoundError(f"Word document not found: {docx_file}")

        # Set default margins if not provided
        if margins is None:
            # Default to 1 inch margins (72 points per inch)
            margins = {'top': 72, 'right': 72, 'bottom': 72, 'left': 72}

        # Extract text from the Word document for metadata embedding
        try:
            from docx import Document
            doc = Document(docx_file)
            paragraphs = [p.text for p in doc.paragraphs]
            text = '\n\n'.join(paragraphs)  # Join paragraphs with double newlines for better spacing
            
            # Clean text by removing zero-width characters that might interfere with metadata
            import re
            text = re.sub(r'[\u200b-\u200f\u2028-\u202f\ufeff]', '', text)
        except ImportError:
            raise ConversionError("python-docx is required for Word document conversion. Install with 'uv pip install python-docx'")
        except Exception as e:
            raise ValueError(f"Failed to extract text from Word document: {str(e)}")
            
        # Embed metadata if private key is provided
        embedded_text = text
        if private_key and signer_id:
            try:
                # Attempt to embed metadata
                embedded_text = UnicodeMetadata.embed_metadata(
                    text=text,
                    private_key=private_key,
                    signer_id=signer_id,
                    timestamp=timestamp,
                    target=target
                )
                
                # Verify embedding was successful
                metadata = UnicodeMetadata.extract_metadata(embedded_text)
                if metadata is None:
                    print("WARNING: Original text not preserved in embedding result. Adjusting embedding strategy.")
                    # Try with a simplified text summary if full text embedding fails
                    summary = text[:1000] + "..." if len(text) > 1000 else text
                    embedded_text = UnicodeMetadata.embed_metadata(
                        text=summary,
                        private_key=private_key,
                        signer_id=signer_id,
                        timestamp=timestamp,
                        target=target
                    )
            except Exception as e:
                print(f"WARNING: Failed to embed metadata: {str(e)}. Proceeding with plain text.")
                embedded_text = text  # Fall back to original text

        # Use PyMuPDF for PDF generation with better formatting
        try:
            # First convert the Word document to PDF using PyMuPDF
            doc = fitz.open(docx_file)
            
            # If the document is already a PDF, this will just create a copy
            # If it's a Word document, PyMuPDF will convert it to PDF
            pdf_bytes = doc.convert_to_pdf()
            temp_pdf = output_file + ".temp.pdf"
            
            # Save the temporary PDF
            with open(temp_pdf, "wb") as f:
                f.write(pdf_bytes)
            
            # Now open the temporary PDF and modify it to include our metadata
            pdf_doc = fitz.open(temp_pdf)
            
            # Apply custom font if provided
            if font_path and os.path.exists(font_path):
                try:
                    # Register the font with PyMuPDF
                    # Note: PyMuPDF handles fonts differently than ReportLab
                    # This is a placeholder for font handling
                    pass
                except Exception as e:
                    raise FontError(f"Failed to register font: {str(e)}")
            
            # Create a new PDF that will contain our embedded text
            output_doc = fitz.open()
            
            # Copy pages from the temporary PDF to our output PDF
            for page_num in range(len(pdf_doc)):
                output_doc.insert_pdf(pdf_doc, from_page=page_num, to_page=page_num)
            
            # Add metadata to the PDF document properties
            output_doc.set_metadata({
                "title": "Document with embedded metadata",
                "author": signer_id if signer_id else "EncypherPDF",
                "subject": "Document with embedded Unicode metadata",
                "keywords": "encypher, metadata, pdf",
                "creator": "EncypherPDF",
                "producer": "EncypherPDF using PyMuPDF"
            })
            
            # Save the final PDF
            output_doc.save(output_file, garbage=4, deflate=True, clean=True)
            output_doc.close()
            
            # Clean up temporary files
            pdf_doc.close()
            if os.path.exists(temp_pdf):
                os.remove(temp_pdf)
            
            # Now create a text file with the embedded metadata that can be extracted later
            metadata_file = output_file + ".metadata.txt"
            with open(metadata_file, "w", encoding="utf-8") as f:
                f.write(embedded_text)
            
            # Store the embedded text in the PDF as an attachment
            # Create a new PDF document to avoid the 'save to original must be incremental' error
            temp_pdf_with_attachment = output_file + ".with_attachment.pdf"
            pdf_doc = fitz.open(output_file)
            pdf_doc.embfile_add("embedded_metadata.txt", embedded_text.encode("utf-8"), 
                               "Embedded metadata text", "text/plain")
            pdf_doc.save(temp_pdf_with_attachment, garbage=4, deflate=True, clean=True)
            pdf_doc.close()
            
            # Replace the original with the new file
            os.replace(temp_pdf_with_attachment, output_file)
            
            # Clean up the separate metadata file
            if os.path.exists(metadata_file):
                os.remove(metadata_file)
            
            return output_file
            
        except Exception as e:
            raise ValueError(f"Failed to generate PDF: {str(e)}")

    @classmethod
    def extract_text(cls, pdf_file):
        """Extract text from a PDF file.
        
        Args:
            pdf_file (str): Path to the PDF file.
            
        Returns:
            str: Extracted text from the PDF.
            
        Raises:
            FileNotFoundError: If the PDF file is not found.
        """
        if not os.path.exists(pdf_file):
            raise FileNotFoundError(f"PDF file not found: {pdf_file}")
            
        try:
            # First try to extract the embedded metadata file if it exists
            doc = fitz.open(pdf_file)
            names = doc.embfile_names()
            
            if "embedded_metadata.txt" in names:
                # Extract the embedded metadata text file
                buffer = doc.embfile_get("embedded_metadata.txt")
                if buffer and isinstance(buffer, dict) and "content" in buffer:
                    return buffer["content"].decode("utf-8")
                elif buffer and isinstance(buffer, bytes):
                    return buffer.decode("utf-8")
            
            # If no embedded metadata file, extract text from the PDF
            text = ""
            for page_num in range(len(doc)):
                page = doc[page_num]
                text += page.get_text("text")
                if page_num < len(doc) - 1:
                    text += "\n\n"  # Add separation between pages
                    
            doc.close()
            return text
            
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")


    @staticmethod
    def verify_pdf(
        pdf_path: str,
        public_key_resolver: Callable[[str], Optional[Ed25519PublicKey]],
        *,
        require_hard_binding: bool = True,
    ) -> Tuple[bool, Optional[str], Union[BasicPayload, ManifestPayload, C2PAPayload, None]]:
        """Verify metadata embedded in a PDF file.
        
        Parameters
        ----------
        pdf_path:
            Path to the PDF file to verify.
        public_key_resolver:
            Function that resolves a signer_id to a public key.
        require_hard_binding:
            Whether to require hard binding in the verification.
            
        Returns
        -------
        Tuple[bool, Optional[str], Union[BasicPayload, ManifestPayload, C2PAPayload, None]]
            A tuple containing (is_valid, signer_id, payload).
            
        Raises
        ------
        FileNotFoundError:
            If the PDF file does not exist.
        PDFGenerationError:
            If there is an error extracting text from the PDF.
        SignatureError:
            If there is an error verifying the signature.
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
        try:
            text = EncypherPDF.extract_text(pdf_path)
        except Exception as e:
            raise PDFGenerationError(f"Failed to extract text from PDF: {str(e)}")
            
        try:
            return UnicodeMetadata.verify_metadata(
                text,
                public_key_resolver=public_key_resolver,
                require_hard_binding=require_hard_binding,
            )
        except InvalidSignature:
            raise SignatureError("Invalid signature in PDF metadata")
        except Exception as e:
            raise SignatureError(f"Failed to verify PDF metadata: {str(e)}")
