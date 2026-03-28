"""Image Signing Executor for CDN Provenance.

High-level executor that signs an image via the C2PA image signing service,
registers the signed image in the CDN provenance store, and returns a result
dict suitable for API responses.

Mirrors the pattern of signing_executor.py but for the image CDN pipeline.
"""

import base64
import logging
import uuid
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.services.cdn_provenance_service import CdnProvenanceService
from app.services.image_signing_service import sign_image
from app.utils.image_utils import generate_image_id

logger = logging.getLogger(__name__)


async def execute_image_signing(
    *,
    image_bytes: bytes,
    mime_type: str,
    title: str,
    org: Organization,
    db: AsyncSession,
    original_url: Optional[str] = None,
    custom_assertions: Optional[list] = None,
    rights_data: Optional[dict] = None,
) -> dict:
    """Sign an image with C2PA and register it for CDN provenance tracking.

    Pipeline:
    1. Load org's private key + cert chain (or passthrough if not configured).
    2. Call image_signing_service.sign_image() to produce C2PA-embedded bytes.
    3. Register the signed image in cdn_provenance_service (pHash + SHA-256).
    4. Return a result dict for the API response.

    Args:
        image_bytes: Raw original image bytes.
        mime_type: MIME type (e.g. "image/jpeg").
        title: Image title for the C2PA manifest.
        org: Authenticated Organization model instance.
        db: Async database session.
        original_url: Optional canonical URL of the source image.
        custom_assertions: Optional extra C2PA assertions to embed.
        rights_data: Optional rights metadata dict.

    Returns:
        dict with keys: record_id, manifest_url, image_id, phash, sha256,
        signed_bytes_b64, mime_type.

    Raises:
        HTTPException: On signing failure or missing key configuration.
    """
    org_id = org.id
    image_id = generate_image_id()
    document_id = f"cdn_{uuid.uuid4().hex[:16]}"

    # Load signing credentials — use empty strings for passthrough mode
    # x5chain needs leaf cert first, then intermediates
    cert_pem: str = org.certificate_pem or ""
    chain_only: str = org.cert_chain_pem or ""
    cert_chain_pem: str = (cert_pem.strip() + "\n" + chain_only.strip()).strip() if cert_pem else chain_only

    private_key_pem: str = ""
    try:
        from cryptography.hazmat.primitives import serialization

        from app.utils.crypto_utils import load_organization_private_key

        key_obj = await load_organization_private_key(org_id, db)
        # Serialize to PEM for image_signing_service
        if hasattr(key_obj, "private_bytes"):
            private_key_pem = key_obj.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            ).decode("utf-8")
    except Exception as exc:
        logger.warning(
            "image_signing_executor: could not load private key for org=%s (passthrough): %s",
            org_id,
            exc,
        )
        # Passthrough mode — sign_image handles missing keys gracefully

    try:
        result = await sign_image(
            image_data=image_bytes,
            mime_type=mime_type,
            title=title,
            org_id=org_id,
            document_id=document_id,
            image_id=image_id,
            custom_assertions=custom_assertions or [],
            rights_data=rights_data or {},
            signer_private_key_pem=private_key_pem,
            signer_cert_chain_pem=cert_chain_pem,
        )
    except ValueError as exc:
        logger.error("image_signing_executor: validation error org=%s: %s", org_id, exc)
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("image_signing_executor: signing failed org=%s: %s", org_id, exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"code": "IMAGE_SIGNING_FAILED", "message": str(exc)},
        ) from exc

    # Build manifest data dict for provenance storage
    manifest_data = {
        "image_id": result.image_id,
        "c2pa_instance_id": result.c2pa_instance_id,
        "c2pa_manifest_hash": result.c2pa_manifest_hash,
        "c2pa_signed": result.c2pa_signed,
        "original_hash": result.original_hash,
        "signed_hash": result.signed_hash,
        "mime_type": result.mime_type,
        "title": title,
        "document_id": document_id,
    }

    cdn_record = await CdnProvenanceService.register_image(
        db=db,
        org_id=org_id,
        image_bytes=result.signed_bytes,
        mime_type=mime_type,
        manifest_data=manifest_data,
        original_url=original_url,
    )

    record_id = str(cdn_record.id)
    manifest_url = f"/api/v1/cdn/manifests/{record_id}"
    signed_bytes_b64 = base64.b64encode(result.signed_bytes).decode("utf-8")

    return {
        "record_id": record_id,
        "manifest_url": manifest_url,
        "image_id": result.image_id,
        "phash": cdn_record.phash,
        "sha256": cdn_record.content_sha256,
        "signed_bytes_b64": signed_bytes_b64,
        "mime_type": result.mime_type,
    }
