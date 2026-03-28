"""Video Signing Executor.

High-level executor that signs video via the C2PA video signing service,
loading per-org credentials from the database. Mirrors the pattern of
image_signing_executor.py.
"""

import logging
import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.services.video_signing_service import SignedVideoResult, sign_video

logger = logging.getLogger(__name__)


async def execute_video_signing(
    *,
    video_bytes: bytes,
    mime_type: str,
    title: str,
    org: Organization,
    db: AsyncSession,
    document_id: str | None = None,
    custom_assertions: list[dict] | None = None,
    rights_data: dict | None = None,
    action: str = "c2pa.created",
    digital_source_type: str | None = None,
) -> SignedVideoResult:
    """Sign video with C2PA using org credentials.

    Pipeline:
    1. Load org's private key + cert chain (or passthrough if not configured).
    2. Call video_signing_service.sign_video() to produce C2PA-embedded bytes.
    3. Return SignedVideoResult.

    Raises:
        HTTPException: On signing failure or missing key configuration.
    """
    org_id = org.id
    video_id = f"vid_{uuid.uuid4().hex[:16]}"
    document_id = document_id or f"doc_{uuid.uuid4().hex[:16]}"

    # x5chain needs leaf cert first, then intermediates
    _cert_pem: str = org.certificate_pem or ""
    _chain_only: str = org.cert_chain_pem or ""
    cert_chain_pem: str = (_cert_pem.strip() + "\n" + _chain_only.strip()).strip() if _cert_pem else _chain_only

    private_key_pem: str = ""
    try:
        from cryptography.hazmat.primitives import serialization

        from app.utils.crypto_utils import load_organization_private_key

        key_obj = await load_organization_private_key(org_id, db)
        if hasattr(key_obj, "private_bytes"):
            private_key_pem = key_obj.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            ).decode("utf-8")
    except Exception as exc:
        logger.warning(
            "video_signing_executor: could not load private key for org=%s (passthrough): %s",
            org_id,
            exc,
        )

    try:
        result = await sign_video(
            video_data=video_bytes,
            mime_type=mime_type,
            title=title,
            org_id=org_id,
            document_id=document_id,
            video_id=video_id,
            custom_assertions=custom_assertions or [],
            rights_data=rights_data or {},
            signer_private_key_pem=private_key_pem,
            signer_cert_chain_pem=cert_chain_pem,
            action=action,
            digital_source_type=digital_source_type,
        )
    except ValueError as exc:
        logger.error("video_signing_executor: validation error org=%s: %s", org_id, exc)
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("video_signing_executor: signing failed org=%s: %s", org_id, exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"code": "VIDEO_SIGNING_FAILED", "message": "Video signing failed"},
        ) from exc

    # Persist SignedVideo record
    try:
        from app.models.signed_video import SignedVideo
        from app.utils.video_utils import compute_video_phash

        phash_val = compute_video_phash(result.signed_bytes)

        row = SignedVideo(
            organization_id=org_id,
            document_id=document_id,
            video_id=result.video_id,
            title=title,
            mime_type=result.mime_type,
            original_hash=result.original_hash,
            signed_hash=result.signed_hash,
            size_bytes=result.size_bytes,
            c2pa_instance_id=result.c2pa_instance_id,
            c2pa_manifest_hash=result.c2pa_manifest_hash,
            c2pa_signed=result.c2pa_signed,
            digital_source_type=digital_source_type,
            phash=phash_val,
        )
        db.add(row)
        await db.commit()
    except Exception as exc:
        logger.warning(
            "video_signing_executor: failed to persist SignedVideo for org=%s video=%s: %s",
            org_id,
            result.video_id,
            exc,
        )

    return result
