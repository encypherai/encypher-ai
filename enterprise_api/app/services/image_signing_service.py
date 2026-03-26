"""Image signing service: C2PA JUMBF embedding for individual images.

This service signs images using c2pa-python, embeds a C2PA manifest as JUMBF
data, strips EXIF metadata before signing, and returns the signed image bytes
plus metadata for storage.
"""

import logging
import uuid
from dataclasses import dataclass
from io import BytesIO
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class SignedImageResult:
    """Result of signing an individual image with c2pa-python."""

    image_id: str
    signed_bytes: bytes
    original_hash: str  # sha256: hex of pre-sign (post-EXIF-strip) bytes
    signed_hash: str  # sha256: hex of post-sign bytes
    c2pa_instance_id: str  # "urn:uuid:..."
    c2pa_manifest_hash: str  # sha256 of manifest bytes
    size_bytes: int
    mime_type: str
    c2pa_signed: bool = True  # False in passthrough mode (no cert configured)


async def sign_image(
    *,
    image_data: bytes,
    mime_type: str,
    title: str,
    org_id: str,
    document_id: str,
    image_id: str,
    custom_assertions: List[dict],
    rights_data: dict,
    signer_private_key_pem: str,
    signer_cert_chain_pem: str,
    action: str = "c2pa.created",
    image_quality: int = 95,
    digital_source_type: Optional[str] = None,
) -> SignedImageResult:
    """
    Sign an image with a C2PA manifest (JUMBF embedding).

    Pipeline:
    1. Validate image (size, format)
    2. Strip EXIF (GPS / device serial removal)
    3. Compute original_hash (pre-sign, post-EXIF-strip)
    4. Build C2PA manifest dict
    5. Create c2pa Signer from PEM keys
    6. Use c2pa.Builder to sign -> get signed_bytes
    7. Compute signed_hash and manifest_hash
    8. Return SignedImageResult

    Args:
        image_data: Raw image bytes.
        mime_type: MIME type (e.g. "image/jpeg").
        title: Image title for C2PA manifest.
        org_id: Organization identifier.
        document_id: Parent document identifier.
        image_id: Unique image identifier (e.g. "img_aabbccdd").
        custom_assertions: Additional C2PA assertions to embed.
        rights_data: Rights metadata dict for com.encypher.rights.v1 assertion.
        signer_private_key_pem: PKCS8 PEM-encoded private key.
        signer_cert_chain_pem: PEM-encoded cert chain (EE cert + CA chain).
        action: C2PA action string (default "c2pa.created").
        image_quality: JPEG/WebP re-encode quality (1-100).

    Returns:
        SignedImageResult with signed image bytes and metadata.

    Raises:
        ValueError: If image validation fails.
        Exception: If C2PA signing fails.
    """
    from app.config import settings
    from app.utils.image_format_registry import canonicalize_mime_type
    from app.utils.image_utils import (
        compute_sha256,
        strip_exif,
        validate_image,
    )

    # Step 1: Validate
    validate_image(image_data, mime_type)

    # JXL uses a custom ISOBMFF embedder (not c2pa-rs). Route to document signing.
    if mime_type.lower().strip() == "image/jxl":
        raise ValueError(
            "image/jxl must be signed via the document signing pipeline "
            "(sign_document with mime_type='image/jxl'), not the image signing service. "
            "The custom ISOBMFF embedder handles JXL container files."
        )

    # Step 2: Strip EXIF (must happen before signing)
    clean_bytes = strip_exif(image_data, mime_type=mime_type, quality=image_quality)

    # Step 3: Compute original_hash (after EXIF strip, before C2PA signing)
    original_hash = compute_sha256(clean_bytes)

    # Passthrough mode: skip JUMBF embedding when no cert is configured or the
    # IMAGE_SIGNING_PASSTHROUGH flag is set. EXIF is still stripped, all hashes
    # and metadata are still computed and stored. Use for local dev / CI.
    # Never enable in production -- the returned image will have no C2PA manifest.
    passthrough = settings.signing_passthrough or settings.image_signing_passthrough or not (signer_private_key_pem and signer_cert_chain_pem)
    if passthrough:
        logger.debug("Image signing passthrough: XMP embedding for image_id=%s", image_id)
        from app.utils.image_utils import inject_encypher_xmp

        instance_id = "urn:uuid:" + str(uuid.uuid4())
        embedded_bytes = inject_encypher_xmp(
            image_bytes=clean_bytes,
            mime_type=mime_type,
            instance_id=instance_id,
            org_id=org_id,
            document_id=document_id,
            image_hash=original_hash,
        )
        signed_hash = compute_sha256(embedded_bytes)
        return SignedImageResult(
            image_id=image_id,
            signed_bytes=embedded_bytes,
            original_hash=original_hash,
            signed_hash=signed_hash,
            c2pa_instance_id=instance_id,
            c2pa_manifest_hash="sha256:" + "0" * 64,  # sentinel for passthrough
            size_bytes=len(embedded_bytes),
            mime_type=mime_type,
            c2pa_signed=False,
        )

    import c2pa

    from app.utils.c2pa_manifest import build_c2pa_manifest_dict
    from app.utils.c2pa_signer import create_signer_from_pem

    # Step 4: Build manifest
    manifest_dict = build_c2pa_manifest_dict(
        title=title,
        org_id=org_id,
        document_id=document_id,
        asset_id=image_id,
        asset_id_key="image_id",
        action=action,
        custom_assertions=custom_assertions,
        rights_data=rights_data,
        digital_source_type=digital_source_type,
    )
    c2pa_instance_id = manifest_dict["instance_id"]

    # Step 5: Create signer
    signer = create_signer_from_pem(signer_private_key_pem, signer_cert_chain_pem)

    try:
        # Step 6: Build and sign
        # Use canonical MIME type for c2pa-python (e.g. heic-sequence -> heic).
        # The original mime_type is preserved in the returned SignedImageResult.
        c2pa_mime = canonicalize_mime_type(mime_type)
        builder = c2pa.Builder(manifest_dict)
        dest = BytesIO()
        manifest_bytes = builder.sign(
            signer,
            c2pa_mime,
            BytesIO(clean_bytes),
            dest,
        )
        dest.seek(0)
        signed_bytes = dest.read()
    finally:
        signer.close()

    # Step 7: Compute hashes
    signed_hash = compute_sha256(signed_bytes)
    c2pa_manifest_hash = compute_sha256(manifest_bytes)

    return SignedImageResult(
        image_id=image_id,
        signed_bytes=signed_bytes,
        original_hash=original_hash,
        signed_hash=signed_hash,
        c2pa_instance_id=c2pa_instance_id,
        c2pa_manifest_hash=c2pa_manifest_hash,
        size_bytes=len(signed_bytes),
        mime_type=mime_type,
        c2pa_signed=True,
    )
