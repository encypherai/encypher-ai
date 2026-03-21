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

    cert_chain_pem: str = org.cert_chain_pem or ""

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
        return await sign_video(
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
