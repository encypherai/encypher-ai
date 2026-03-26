"""Document C2PA signing service for PDF and ZIP-based formats.

Handles formats that c2pa-python does not support for embedding:
  PDF: application/pdf
  EPUB: application/epub+zip
  DOCX: application/vnd.openxmlformats-officedocument.wordprocessingml.document
  ODT: application/vnd.oasis.opendocument.text
  OXPS: application/oxps

Uses a two-pass approach:
  1. Insert placeholder manifest into the document
  2. Compute content hashes
  3. Build C2PA manifest (assertions + claim + COSE signature)
  4. Replace placeholder with signed manifest
"""

import logging
from dataclasses import dataclass
from typing import Optional

import cbor2

from app.utils import jumbf
from app.utils.c2pa_claim_builder import (
    HASH_ALG_SHA256,
    build_actions_assertion,
    build_claim_cbor,
    build_collection_data_hash,
    build_data_hash,
    build_provenance_assertion,
)
from app.utils.cose_signer import sign_claim

_log = logging.getLogger(__name__)

SUPPORTED_DOCUMENT_MIME_TYPES = frozenset(
    {
        "application/pdf",
        "application/epub+zip",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.oasis.opendocument.text",
        "application/oxps",
        "font/otf",
        "font/ttf",
        "font/sfnt",
        "audio/flac",
        "image/jxl",
    }
)

_ZIP_BASED_MIMES = frozenset(
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


@dataclass
class SignedDocumentResult:
    signed_bytes: bytes
    mime_type: str
    manifest_label: str
    instance_id: str
    original_size: int
    signed_size: int


def is_zip_based(mime_type: str) -> bool:
    return mime_type in _ZIP_BASED_MIMES


def _build_manifest_store(
    assertions_data: list[tuple[str, dict]],
    title: str,
    dc_format: str,
    private_key_pem: str,
    cert_chain_pem: str,
    alg: str = HASH_ALG_SHA256,
) -> tuple[bytes, str]:
    """Build a complete C2PA manifest store (JUMBF bytes).

    Args:
        assertions_data: List of (label, data_dict) for each assertion.
        title: Document title.
        dc_format: MIME type of the asset (required per C2PA spec).
        private_key_pem: PEM private key for signing.
        cert_chain_pem: PEM certificate chain.
        alg: Hash algorithm.

    Returns:
        Tuple of (manifest_store_bytes, manifest_label).
    """
    manifest_label = jumbf.generate_manifest_label()

    # Build assertion JUMBF boxes and collect their inner content for hashing
    assertion_boxes = []
    assertion_refs = []  # (label, inner_content_bytes) for claim hashing

    for label, data_dict in assertions_data:
        cbor_data = cbor2.dumps(data_dict)
        # Build the assertion superbox
        box = jumbf.build_assertion_box(label, cbor_data)
        assertion_boxes.append(box)

        # For claim hashing: hash covers the superbox content (description + content boxes),
        # excluding the outer jumb LBox(4) + TBox(4) header per C2PA spec 14.2.3
        inner_content = box[8:]
        assertion_refs.append((label, inner_content))

    # Build the claim
    claim_cbor = build_claim_cbor(
        manifest_label,
        assertion_refs,
        dc_format=dc_format,
        title=title,
        alg=alg,
    )

    # Sign the claim
    signature_cose = sign_claim(claim_cbor, private_key_pem, cert_chain_pem)

    # Assemble the manifest
    manifest = jumbf.build_manifest(
        manifest_label,
        assertion_boxes,
        claim_cbor,
        signature_cose,
    )

    # Wrap in manifest store
    store = jumbf.build_manifest_store([manifest])
    return store, manifest_label


def sign_zip_document(
    document_bytes: bytes,
    mime_type: str,
    *,
    title: str = "Untitled Document",
    org_id: str = "",
    document_id: str = "",
    asset_id: str = "",
    action: str = "c2pa.created",
    digital_source_type: Optional[str] = None,
    private_key_pem: str,
    cert_chain_pem: str,
    placeholder_size: int = 65536,
) -> SignedDocumentResult:
    """Sign a ZIP-based document with a C2PA manifest.

    Args:
        document_bytes: Original document bytes (EPUB, DOCX, ODT, OXPS).
        mime_type: Document MIME type.
        title: Document title for the manifest.
        org_id: Organization identifier.
        document_id: Document identifier.
        asset_id: Asset identifier.
        action: C2PA action (default: c2pa.created).
        digital_source_type: IPTC digital source type.
        private_key_pem: PEM private key.
        cert_chain_pem: PEM certificate chain.
        placeholder_size: Initial placeholder size.

    Returns:
        SignedDocumentResult with the signed document bytes.
    """
    from app.utils.zip_c2pa_embedder import (
        compute_collection_hashes,
        create_zip_with_placeholder,
        replace_manifest_in_zip,
    )

    original_size = len(document_bytes)

    # Pass 1: Create ZIP with placeholder
    zip_with_placeholder = create_zip_with_placeholder(document_bytes, placeholder_size)

    # Compute hashes
    file_hashes, cd_hash = compute_collection_hashes(zip_with_placeholder)

    # Build assertions
    assertions = [
        ("c2pa.actions.v2", build_actions_assertion(action, digital_source_type)),
        ("c2pa.hash.collection.data", build_collection_data_hash(file_hashes, cd_hash)),
        ("com.encypher.provenance", build_provenance_assertion(org_id, document_id, asset_id)),
    ]

    # Build and sign manifest store
    manifest_store, manifest_label = _build_manifest_store(assertions, title, mime_type, private_key_pem, cert_chain_pem)

    # Check if manifest fits in placeholder
    if len(manifest_store) > placeholder_size:
        _log.info(
            "Manifest (%d bytes) exceeds placeholder (%d bytes), retrying with larger placeholder",
            len(manifest_store),
            placeholder_size,
        )
        # Retry with larger placeholder
        new_size = len(manifest_store) + 4096  # Add headroom
        return sign_zip_document(
            document_bytes,
            mime_type,
            title=title,
            org_id=org_id,
            document_id=document_id,
            asset_id=asset_id,
            action=action,
            digital_source_type=digital_source_type,
            private_key_pem=private_key_pem,
            cert_chain_pem=cert_chain_pem,
            placeholder_size=new_size,
        )

    # Pass 2: Replace placeholder with signed manifest
    signed_bytes = replace_manifest_in_zip(zip_with_placeholder, manifest_store)

    return SignedDocumentResult(
        signed_bytes=signed_bytes,
        mime_type=mime_type,
        manifest_label=manifest_label,
        instance_id="",
        original_size=original_size,
        signed_size=len(signed_bytes),
    )


def sign_pdf_document(
    document_bytes: bytes,
    *,
    title: str = "Untitled Document",
    org_id: str = "",
    document_id: str = "",
    asset_id: str = "",
    action: str = "c2pa.created",
    digital_source_type: Optional[str] = None,
    private_key_pem: str,
    cert_chain_pem: str,
    placeholder_size: int = 65536,
) -> SignedDocumentResult:
    """Sign a PDF document with a C2PA manifest.

    Args:
        document_bytes: Original PDF bytes.
        title: Document title for the manifest.
        org_id: Organization identifier.
        document_id: Document identifier.
        asset_id: Asset identifier.
        action: C2PA action (default: c2pa.created).
        digital_source_type: IPTC digital source type.
        private_key_pem: PEM private key.
        cert_chain_pem: PEM certificate chain.
        placeholder_size: Initial placeholder size.

    Returns:
        SignedDocumentResult with the signed PDF bytes.
    """
    from app.utils.pdf_c2pa_embedder import (
        compute_pdf_hash,
        create_pdf_with_placeholder,
        replace_manifest_in_pdf,
    )

    original_size = len(document_bytes)

    # Pass 1: Create PDF with placeholder
    pdf_with_placeholder, excl_start, excl_length = create_pdf_with_placeholder(document_bytes, placeholder_size)

    # Compute hash excluding the placeholder
    data_hash = compute_pdf_hash(pdf_with_placeholder, excl_start, excl_length)

    # Build assertions
    exclusions = [{"start": excl_start, "length": excl_length}]
    assertions = [
        ("c2pa.actions.v2", build_actions_assertion(action, digital_source_type)),
        ("c2pa.hash.data", build_data_hash(data_hash, exclusions)),
        ("com.encypher.provenance", build_provenance_assertion(org_id, document_id, asset_id)),
    ]

    # Build and sign manifest store
    manifest_store, manifest_label = _build_manifest_store(assertions, title, "application/pdf", private_key_pem, cert_chain_pem)

    # Check if manifest fits in placeholder
    if len(manifest_store) > excl_length:
        _log.info(
            "Manifest (%d bytes) exceeds placeholder (%d bytes), retrying",
            len(manifest_store),
            excl_length,
        )
        new_size = len(manifest_store) + 4096
        return sign_pdf_document(
            document_bytes,
            title=title,
            org_id=org_id,
            document_id=document_id,
            asset_id=asset_id,
            action=action,
            digital_source_type=digital_source_type,
            private_key_pem=private_key_pem,
            cert_chain_pem=cert_chain_pem,
            placeholder_size=new_size,
        )

    # Pass 2: Replace placeholder
    signed_bytes = replace_manifest_in_pdf(pdf_with_placeholder, manifest_store, excl_start, excl_length)

    return SignedDocumentResult(
        signed_bytes=signed_bytes,
        mime_type="application/pdf",
        manifest_label=manifest_label,
        instance_id="",
        original_size=original_size,
        signed_size=len(signed_bytes),
    )


def sign_font(
    font_bytes: bytes,
    *,
    mime_type: str = "font/otf",
    title: str = "Untitled Font",
    org_id: str = "",
    document_id: str = "",
    asset_id: str = "",
    action: str = "c2pa.created",
    digital_source_type: Optional[str] = None,
    private_key_pem: str,
    cert_chain_pem: str,
    placeholder_size: int = 65536,
) -> SignedDocumentResult:
    """Sign an SFNT font (OTF/TTF) with a C2PA manifest.

    The manifest is embedded as a 'C2PA' SFNT table. Content binding uses
    c2pa.hash.data with an exclusion range for the C2PA table bytes.
    """
    from app.utils.font_c2pa_embedder import (
        compute_font_hash,
        create_font_with_placeholder,
        replace_manifest_in_font,
    )

    original_size = len(font_bytes)

    # Pass 1: Add C2PA table with placeholder
    font_with_placeholder, excl_start, excl_length = create_font_with_placeholder(font_bytes, placeholder_size)

    # Compute hash excluding the C2PA table
    data_hash = compute_font_hash(font_with_placeholder, excl_start, excl_length)

    # Build assertions
    exclusions = [{"start": excl_start, "length": excl_length}]
    assertions = [
        ("c2pa.actions.v2", build_actions_assertion(action, digital_source_type)),
        ("c2pa.hash.data", build_data_hash(data_hash, exclusions)),
        ("com.encypher.provenance", build_provenance_assertion(org_id, document_id, asset_id)),
    ]

    # Build and sign manifest store
    manifest_store, manifest_label = _build_manifest_store(assertions, title, mime_type, private_key_pem, cert_chain_pem)

    # Check fit
    if len(manifest_store) > excl_length:
        _log.info(
            "Manifest (%d bytes) exceeds C2PA table (%d bytes), retrying",
            len(manifest_store),
            excl_length,
        )
        new_size = len(manifest_store) + 4096
        return sign_font(
            font_bytes,
            mime_type=mime_type,
            title=title,
            org_id=org_id,
            document_id=document_id,
            asset_id=asset_id,
            action=action,
            digital_source_type=digital_source_type,
            private_key_pem=private_key_pem,
            cert_chain_pem=cert_chain_pem,
            placeholder_size=new_size,
        )

    # Pass 2: Replace placeholder
    signed_bytes = replace_manifest_in_font(font_with_placeholder, manifest_store, excl_start, excl_length)

    return SignedDocumentResult(
        signed_bytes=signed_bytes,
        mime_type=mime_type,
        manifest_label=manifest_label,
        instance_id="",
        original_size=original_size,
        signed_size=len(signed_bytes),
    )


def sign_flac(
    flac_bytes: bytes,
    *,
    title: str = "Untitled Audio",
    org_id: str = "",
    document_id: str = "",
    asset_id: str = "",
    action: str = "c2pa.created",
    digital_source_type: Optional[str] = None,
    private_key_pem: str,
    cert_chain_pem: str,
    placeholder_size: int = 65536,
) -> SignedDocumentResult:
    """Sign a FLAC audio file with a C2PA manifest.

    The manifest is embedded as a FLAC APPLICATION metadata block with
    application ID "c2pa". Content binding uses c2pa.hash.data with an
    exclusion range for the manifest data bytes.
    """
    from app.utils.flac_c2pa_embedder import (
        compute_flac_hash,
        create_flac_with_placeholder,
        replace_manifest_in_flac,
    )

    original_size = len(flac_bytes)

    # Pass 1: Insert APPLICATION block with placeholder
    flac_with_placeholder, excl_start, excl_length = create_flac_with_placeholder(flac_bytes, placeholder_size)

    # Compute hash excluding the manifest data
    data_hash = compute_flac_hash(flac_with_placeholder, excl_start, excl_length)

    # Build assertions
    exclusions = [{"start": excl_start, "length": excl_length}]
    assertions = [
        ("c2pa.actions.v2", build_actions_assertion(action, digital_source_type)),
        ("c2pa.hash.data", build_data_hash(data_hash, exclusions)),
        ("com.encypher.provenance", build_provenance_assertion(org_id, document_id, asset_id)),
    ]

    # Build and sign manifest store
    manifest_store, manifest_label = _build_manifest_store(assertions, title, "audio/flac", private_key_pem, cert_chain_pem)

    # Check fit
    if len(manifest_store) > excl_length:
        _log.info(
            "Manifest (%d bytes) exceeds placeholder (%d bytes), retrying",
            len(manifest_store),
            excl_length,
        )
        new_size = len(manifest_store) + 4096
        return sign_flac(
            flac_bytes,
            title=title,
            org_id=org_id,
            document_id=document_id,
            asset_id=asset_id,
            action=action,
            digital_source_type=digital_source_type,
            private_key_pem=private_key_pem,
            cert_chain_pem=cert_chain_pem,
            placeholder_size=new_size,
        )

    # Pass 2: Replace placeholder
    signed_bytes = replace_manifest_in_flac(flac_with_placeholder, manifest_store, excl_start, excl_length)

    return SignedDocumentResult(
        signed_bytes=signed_bytes,
        mime_type="audio/flac",
        manifest_label=manifest_label,
        instance_id="",
        original_size=original_size,
        signed_size=len(signed_bytes),
    )


def sign_jxl(
    jxl_bytes: bytes,
    *,
    title: str = "Untitled Image",
    org_id: str = "",
    document_id: str = "",
    asset_id: str = "",
    action: str = "c2pa.created",
    digital_source_type: Optional[str] = None,
    private_key_pem: str,
    cert_chain_pem: str,
    placeholder_size: int = 65536,
) -> SignedDocumentResult:
    """Sign a JPEG XL (ISOBMFF container) file with a C2PA manifest.

    The manifest is embedded as a top-level 'c2pa' ISOBMFF box.
    Content binding uses c2pa.hash.data with an exclusion range
    for the manifest data bytes.

    Only the ISOBMFF container variant is supported (not bare codestream).
    """
    from app.utils.jxl_c2pa_embedder import (
        compute_jxl_hash,
        create_jxl_with_placeholder,
        replace_manifest_in_jxl,
    )

    original_size = len(jxl_bytes)

    # Pass 1: Append c2pa box with placeholder
    jxl_with_placeholder, excl_start, excl_length = create_jxl_with_placeholder(jxl_bytes, placeholder_size)

    # Compute hash excluding the manifest data
    data_hash = compute_jxl_hash(jxl_with_placeholder, excl_start, excl_length)

    # Build assertions
    exclusions = [{"start": excl_start, "length": excl_length}]
    assertions = [
        ("c2pa.actions.v2", build_actions_assertion(action, digital_source_type)),
        ("c2pa.hash.data", build_data_hash(data_hash, exclusions)),
        ("com.encypher.provenance", build_provenance_assertion(org_id, document_id, asset_id)),
    ]

    # Build and sign manifest store
    manifest_store, manifest_label = _build_manifest_store(assertions, title, "image/jxl", private_key_pem, cert_chain_pem)

    # Check fit
    if len(manifest_store) > excl_length:
        _log.info(
            "Manifest (%d bytes) exceeds placeholder (%d bytes), retrying",
            len(manifest_store),
            excl_length,
        )
        new_size = len(manifest_store) + 4096
        return sign_jxl(
            jxl_bytes,
            title=title,
            org_id=org_id,
            document_id=document_id,
            asset_id=asset_id,
            action=action,
            digital_source_type=digital_source_type,
            private_key_pem=private_key_pem,
            cert_chain_pem=cert_chain_pem,
            placeholder_size=new_size,
        )

    # Pass 2: Replace placeholder
    signed_bytes = replace_manifest_in_jxl(jxl_with_placeholder, manifest_store, excl_start, excl_length)

    return SignedDocumentResult(
        signed_bytes=signed_bytes,
        mime_type="image/jxl",
        manifest_label=manifest_label,
        instance_id="",
        original_size=original_size,
        signed_size=len(signed_bytes),
    )


def sign_document(
    document_bytes: bytes,
    mime_type: str,
    *,
    title: str = "Untitled Document",
    org_id: str = "",
    document_id: str = "",
    asset_id: str = "",
    action: str = "c2pa.created",
    digital_source_type: Optional[str] = None,
    private_key_pem: str,
    cert_chain_pem: str,
) -> SignedDocumentResult:
    """Sign a document with a C2PA manifest (dispatcher).

    Routes to the appropriate signing method based on MIME type.
    """
    if mime_type not in SUPPORTED_DOCUMENT_MIME_TYPES:
        raise ValueError(f"Unsupported document MIME type: {mime_type}")

    if mime_type == "application/pdf":
        return sign_pdf_document(
            document_bytes,
            title=title,
            org_id=org_id,
            document_id=document_id,
            asset_id=asset_id,
            action=action,
            digital_source_type=digital_source_type,
            private_key_pem=private_key_pem,
            cert_chain_pem=cert_chain_pem,
        )
    elif mime_type in _FONT_MIMES:
        return sign_font(
            document_bytes,
            mime_type=mime_type,
            title=title,
            org_id=org_id,
            document_id=document_id,
            asset_id=asset_id,
            action=action,
            digital_source_type=digital_source_type,
            private_key_pem=private_key_pem,
            cert_chain_pem=cert_chain_pem,
        )
    elif mime_type in _FLAC_MIMES:
        return sign_flac(
            document_bytes,
            title=title,
            org_id=org_id,
            document_id=document_id,
            asset_id=asset_id,
            action=action,
            digital_source_type=digital_source_type,
            private_key_pem=private_key_pem,
            cert_chain_pem=cert_chain_pem,
        )
    elif mime_type in _JXL_MIMES:
        return sign_jxl(
            document_bytes,
            title=title,
            org_id=org_id,
            document_id=document_id,
            asset_id=asset_id,
            action=action,
            digital_source_type=digital_source_type,
            private_key_pem=private_key_pem,
            cert_chain_pem=cert_chain_pem,
        )
    else:
        return sign_zip_document(
            document_bytes,
            mime_type,
            title=title,
            org_id=org_id,
            document_id=document_id,
            asset_id=asset_id,
            action=action,
            digital_source_type=digital_source_type,
            private_key_pem=private_key_pem,
            cert_chain_pem=cert_chain_pem,
        )
