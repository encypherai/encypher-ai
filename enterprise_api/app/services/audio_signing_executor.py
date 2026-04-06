"""Audio Signing Executor.

High-level executor that signs audio via the C2PA audio signing service,
loading per-org credentials from the database. Mirrors the pattern of
image_signing_executor.py.
"""

import logging
import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.services.audio_signing_service import SignedAudioResult, sign_audio

logger = logging.getLogger(__name__)


async def execute_audio_signing(
    *,
    audio_bytes: bytes,
    mime_type: str,
    title: str,
    org: Organization,
    db: AsyncSession,
    document_id: str | None = None,
    custom_assertions: list[dict] | None = None,
    rights_data: dict | None = None,
    action: str = "c2pa.created",
    enable_audio_watermark: bool = False,
) -> SignedAudioResult:
    """Sign audio with C2PA using org credentials.

    Pipeline:
    1. Load org's private key + cert chain (or passthrough if not configured).
    2. Call audio_signing_service.sign_audio() to produce C2PA-embedded bytes.
    3. Return SignedAudioResult.

    Raises:
        HTTPException: On signing failure or missing key configuration.
    """
    org_id = org.id
    audio_id = f"aud_{uuid.uuid4().hex[:16]}"
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
            "audio_signing_executor: could not load private key for org=%s (passthrough): %s",
            org_id,
            exc,
        )

    from app.services.audio_watermark_client import SOFT_BINDING_ASSERTION

    # Add soft-binding assertion when watermarking is enabled
    assertions = list(custom_assertions or [])
    if enable_audio_watermark:
        assertions.append(SOFT_BINDING_ASSERTION)

    try:
        result = await sign_audio(
            audio_data=audio_bytes,
            mime_type=mime_type,
            title=title,
            org_id=org_id,
            document_id=document_id,
            audio_id=audio_id,
            custom_assertions=assertions,
            rights_data=rights_data or {},
            signer_private_key_pem=private_key_pem,
            signer_cert_chain_pem=cert_chain_pem,
            action=action,
        )
    except ValueError as exc:
        logger.error("audio_signing_executor: validation error org=%s: %s", org_id, exc)
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("audio_signing_executor: signing failed org=%s: %s", org_id, exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"code": "AUDIO_SIGNING_FAILED", "message": "Audio signing failed"},
        ) from exc

    # Apply spread-spectrum watermark after C2PA signing
    if enable_audio_watermark:
        from app.services.audio_watermark_client import apply_watermark_to_signed_audio

        wm_result = await apply_watermark_to_signed_audio(result.signed_bytes, mime_type, audio_id, org_id)
        if wm_result is not None:
            result.signed_bytes, result.signed_hash, _wm_key = wm_result
            result.size_bytes = len(result.signed_bytes)
            logger.info("Audio watermark applied: audio_id=%s org=%s", audio_id, org_id)

    return result
