"""Unified media signing endpoint for C2PA conformance.

POST /sign/media -- Sign any supported media file with a C2PA manifest.

Supports all C2PA Conformance Program green-list formats:
  Images: JPEG, PNG, WebP, TIFF, AVIF, HEIC, HEIF, SVG, DNG, GIF, JXL
  Video:  MP4, MOV, AVI, M4V
  Audio:  WAV, MP3, M4A/AAC, MPA
  Docs:   PDF

Accepts an optional ingredient file for C2PA provenance chain (c2pa.edited).
"""

import base64
import logging
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_organization
from app.models.organization import Organization

router = APIRouter()
logger = logging.getLogger(__name__)

# Tier gate: enterprise, strategic_partner, demo
_ALLOWED_TIERS = {"enterprise", "strategic_partner", "demo"}


def _require_enterprise(organization: dict = Depends(get_current_organization)) -> dict:
    tier = (organization.get("tier") or "free").lower().replace("-", "_")
    if tier not in _ALLOWED_TIERS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FEATURE_NOT_AVAILABLE",
                "message": "Media C2PA signing requires Enterprise tier",
                "required_tier": "enterprise",
                "current_tier": tier,
            },
        )
    return organization


# Green-list MIME types from C2PA Conformance Program
_IMAGE_MIMES = frozenset(
    {
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/tiff",
        "image/avif",
        "image/heic",
        "image/heif",
        "image/heic-sequence",
        "image/heif-sequence",
        "image/svg+xml",
        "image/x-adobe-dng",
        "image/gif",
        "image/jxl",
    }
)
_VIDEO_MIMES = frozenset(
    {
        "video/mp4",
        "video/quicktime",
        "video/x-msvideo",
        "video/x-m4v",
    }
)
_AUDIO_MIMES = frozenset(
    {
        "audio/wav",
        "audio/wave",
        "audio/x-wav",
        "audio/mpeg",
        "audio/mp3",
        "audio/mpa",
        "audio/mp4",
        "audio/x-m4a",
        "audio/aac",
    }
)
_DOCUMENT_MIMES = frozenset(
    {
        "application/pdf",
    }
)
_ALL_SUPPORTED = _IMAGE_MIMES | _VIDEO_MIMES | _AUDIO_MIMES | _DOCUMENT_MIMES


def _classify(mime: str) -> str:
    m = mime.lower().strip()
    if m in _IMAGE_MIMES:
        return "image"
    if m in _VIDEO_MIMES:
        return "video"
    if m in _AUDIO_MIMES:
        return "audio"
    if m in _DOCUMENT_MIMES:
        return "document"
    return "unknown"


@router.post(
    "/sign/media",
    status_code=status.HTTP_200_OK,
    summary="Sign any media file with a C2PA manifest",
    description=(
        "Sign a media file (image, video, audio, or document) with a C2PA manifest. "
        "Supports all C2PA Conformance Program formats. Optionally accepts a previously "
        "signed file as an ingredient for provenance chain (c2pa.edited) workflows."
    ),
    tags=["Media Signing"],
)
async def sign_media(
    file: UploadFile = File(..., description="Media file to sign"),
    title: str = Form(default="Untitled", description="Title for the C2PA manifest"),
    action: str = Form(default="c2pa.created", description="C2PA action: c2pa.created or c2pa.edited"),
    digital_source_type: Optional[str] = Form(default=None, description="IPTC digital source type"),
    ingredient: Optional[UploadFile] = File(default=None, description="Previously signed file to reference as ingredient"),
    enable_audio_watermark: bool = Form(default=False, description="Apply spread-spectrum audio watermark (Enterprise only, audio files only)"),
    organization: dict = Depends(_require_enterprise),
    db: AsyncSession = Depends(get_db),
):
    """Sign a media file with C2PA manifest, with optional ingredient for provenance chains."""
    from app.services.unified_verify_service import sniff_mime_type

    org_id = organization.get("organization_id")
    if not org_id:
        raise HTTPException(status_code=400, detail="Organization ID missing")

    # Read file and determine MIME type
    file_data = await file.read()
    mime_type = sniff_mime_type(file_data, file.filename, file.content_type or "application/octet-stream")
    mime_lower = mime_type.lower().strip()

    if mime_lower not in _ALL_SUPPORTED:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "UNSUPPORTED_MEDIA_TYPE",
                "message": f"MIME type {mime_type!r} is not supported for C2PA signing",
                "supported": sorted(_ALL_SUPPORTED),
            },
        )

    category = _classify(mime_lower)

    # Read ingredient if provided
    ingredient_data: Optional[bytes] = None
    ingredient_mime: Optional[str] = None
    if ingredient:
        ingredient_data = await ingredient.read()
        ingredient_mime = sniff_mime_type(
            ingredient_data,
            ingredient.filename,
            ingredient.content_type or "application/octet-stream",
        )
        if action == "c2pa.created":
            action = "c2pa.edited"
        logger.info("Ingredient provided: mime=%s size=%d", ingredient_mime, len(ingredient_data))

    # Load org for signing credentials
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()
    if org is None:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Load signing credentials (leaf cert + chain for x5chain)
    cert_pem: str = org.certificate_pem or ""
    chain_only: str = org.cert_chain_pem or ""
    cert_chain_pem: str = (cert_pem.strip() + "\n" + chain_only.strip()).strip() if cert_pem else chain_only

    private_key_pem: str = ""
    private_key_error: str = ""
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
        private_key_error = str(exc)
        logger.warning("sign_media: could not load private key for org=%s: %s", org_id, exc)

    # Determine passthrough reason (if any) so the response can explain
    # why c2pa_signed is false. This mirrors the logic in each signing service.
    from app.config import settings as _settings

    passthrough_reason: Optional[str] = None
    if _settings.signing_passthrough:
        passthrough_reason = "settings_override_global"
    elif category == "image" and _settings.image_signing_passthrough:
        passthrough_reason = "settings_override_image"
    elif category == "video" and _settings.video_signing_passthrough:
        passthrough_reason = "settings_override_video"
    elif category == "audio" and _settings.audio_signing_passthrough:
        passthrough_reason = "settings_override_audio"
    elif not private_key_pem and not cert_chain_pem:
        passthrough_reason = "no_private_key_and_no_certificate"
        if private_key_error:
            passthrough_reason += f": {private_key_error}"
    elif not private_key_pem:
        passthrough_reason = "no_private_key"
        if private_key_error:
            passthrough_reason += f": {private_key_error}"
    elif not cert_chain_pem:
        passthrough_reason = "no_certificate"

    document_id = f"doc_{uuid.uuid4().hex[:16]}"

    if category == "image":
        signed_result = await _sign_image(
            file_data,
            mime_lower,
            title,
            org_id,
            document_id,
            private_key_pem,
            cert_chain_pem,
            action,
            digital_source_type,
            ingredient_data,
            ingredient_mime,
        )
    elif category == "video":
        signed_result = await _sign_video(
            file_data,
            mime_lower,
            title,
            org_id,
            document_id,
            private_key_pem,
            cert_chain_pem,
            action,
            digital_source_type,
            ingredient_data,
            ingredient_mime,
        )
    elif category == "audio":
        signed_result = await _sign_audio(
            file_data,
            mime_lower,
            title,
            org_id,
            document_id,
            private_key_pem,
            cert_chain_pem,
            action,
            digital_source_type,
            ingredient_data,
            ingredient_mime,
            enable_audio_watermark=enable_audio_watermark,
        )
    elif category == "document":
        signed_result = await _sign_document(
            file_data,
            mime_lower,
            title,
            org_id,
            document_id,
            private_key_pem,
            cert_chain_pem,
            action,
            ingredient_data,
            ingredient_mime,
        )
    else:
        raise HTTPException(status_code=422, detail=f"Cannot route MIME type: {mime_type}")

    # Attach passthrough_reason when the file was not actually C2PA-signed
    if not signed_result.get("c2pa_signed") and passthrough_reason:
        signed_result["passthrough_reason"] = passthrough_reason

    return signed_result


async def _sign_image(
    data,
    mime,
    title,
    org_id,
    document_id,
    private_key_pem,
    cert_chain_pem,
    action,
    digital_source_type,
    ingredient_data,
    ingredient_mime,
):
    from app.services.image_signing_service import sign_image
    from app.utils.image_utils import generate_image_id

    # JXL routes through document signing pipeline
    if mime == "image/jxl":
        return await _sign_document(
            data,
            mime,
            title,
            org_id,
            document_id,
            private_key_pem,
            cert_chain_pem,
            action,
            ingredient_data,
            ingredient_mime,
        )

    image_id = generate_image_id()
    result = await sign_image(
        image_data=data,
        mime_type=mime,
        title=title,
        org_id=org_id,
        document_id=document_id,
        image_id=image_id,
        custom_assertions=[],
        rights_data={},
        signer_private_key_pem=private_key_pem,
        signer_cert_chain_pem=cert_chain_pem,
        action=action,
        digital_source_type=digital_source_type,
        ingredient_data=ingredient_data,
        ingredient_mime=ingredient_mime,
    )
    return {
        "success": True,
        "media_type": "image",
        "asset_id": result.image_id,
        "mime_type": result.mime_type,
        "c2pa_instance_id": result.c2pa_instance_id,
        "c2pa_signed": result.c2pa_signed,
        "original_hash": result.original_hash,
        "signed_hash": result.signed_hash,
        "size_bytes": result.size_bytes,
        "signed_file_b64": base64.b64encode(result.signed_bytes).decode("utf-8"),
        "has_ingredient": ingredient_data is not None,
    }


async def _sign_video(
    data,
    mime,
    title,
    org_id,
    document_id,
    private_key_pem,
    cert_chain_pem,
    action,
    digital_source_type,
    ingredient_data,
    ingredient_mime,
):
    from app.services.video_signing_service import sign_video

    video_id = f"vid_{uuid.uuid4().hex[:16]}"
    result = await sign_video(
        video_data=data,
        mime_type=mime,
        title=title,
        org_id=org_id,
        document_id=document_id,
        video_id=video_id,
        custom_assertions=[],
        rights_data={},
        signer_private_key_pem=private_key_pem,
        signer_cert_chain_pem=cert_chain_pem,
        action=action,
        digital_source_type=digital_source_type,
        ingredient_data=ingredient_data,
        ingredient_mime=ingredient_mime,
    )
    return {
        "success": True,
        "media_type": "video",
        "asset_id": result.video_id,
        "mime_type": result.mime_type,
        "c2pa_instance_id": result.c2pa_instance_id,
        "c2pa_signed": result.c2pa_signed,
        "original_hash": result.original_hash,
        "signed_hash": result.signed_hash,
        "size_bytes": result.size_bytes,
        "signed_file_b64": base64.b64encode(result.signed_bytes).decode("utf-8"),
        "has_ingredient": ingredient_data is not None,
    }


async def _sign_audio(
    data,
    mime,
    title,
    org_id,
    document_id,
    private_key_pem,
    cert_chain_pem,
    action,
    digital_source_type,
    ingredient_data,
    ingredient_mime,
    enable_audio_watermark: bool = False,
):
    from app.services.audio_signing_service import sign_audio

    audio_id = f"aud_{uuid.uuid4().hex[:16]}"

    # Build custom assertions, including soft-binding declaration when watermarking
    custom_assertions: list[dict] = []
    if enable_audio_watermark:
        custom_assertions.append(
            {
                "label": "c2pa.soft_binding.v1",
                "data": {
                    "method": "encypher.spread_spectrum_audio.v1",
                    "payload_bits": 64,
                    "description": "Spread-spectrum audio watermark embedded in signal domain",
                },
            }
        )

    result = await sign_audio(
        audio_data=data,
        mime_type=mime,
        title=title,
        org_id=org_id,
        document_id=document_id,
        audio_id=audio_id,
        custom_assertions=custom_assertions,
        rights_data={},
        signer_private_key_pem=private_key_pem,
        signer_cert_chain_pem=cert_chain_pem,
        action=action,
        digital_source_type=digital_source_type,
        ingredient_data=ingredient_data,
        ingredient_mime=ingredient_mime,
    )

    # Apply spread-spectrum watermark after C2PA signing (modifies audio signal)
    watermark_applied = False
    watermark_key_val = None
    if enable_audio_watermark:
        from app.services.audio_watermark_client import (
            audio_watermark_client,
            compute_audio_watermark_key,
            compute_audio_watermark_payload,
        )

        if audio_watermark_client.is_configured:
            signed_b64 = base64.b64encode(result.signed_bytes).decode()
            payload_hex = compute_audio_watermark_payload(audio_id, org_id)
            wm_result = await audio_watermark_client.apply_watermark(signed_b64, mime, payload_hex)
            if wm_result is not None:
                watermarked_b64, _confidence = wm_result
                result.signed_bytes = base64.b64decode(watermarked_b64)
                from app.utils.hashing import compute_sha256

                result.signed_hash = compute_sha256(result.signed_bytes)
                result.size_bytes = len(result.signed_bytes)
                watermark_applied = True
                watermark_key_val = compute_audio_watermark_key(audio_id, org_id)
                logger.info("Audio watermark applied: audio_id=%s doc=%s", audio_id, document_id)
            else:
                logger.warning("Audio watermark failed for audio_id=%s, continuing without watermark", audio_id)

    return {
        "success": True,
        "media_type": "audio",
        "asset_id": result.audio_id,
        "mime_type": result.mime_type,
        "c2pa_instance_id": result.c2pa_instance_id,
        "c2pa_signed": result.c2pa_signed,
        "original_hash": result.original_hash,
        "signed_hash": result.signed_hash,
        "size_bytes": result.size_bytes,
        "signed_file_b64": base64.b64encode(result.signed_bytes).decode("utf-8"),
        "has_ingredient": ingredient_data is not None,
        "watermark_applied": watermark_applied,
        "watermark_key": watermark_key_val,
    }


async def _sign_document(
    data,
    mime,
    title,
    org_id,
    document_id,
    private_key_pem,
    cert_chain_pem,
    action,
    ingredient_data,
    ingredient_mime,
):
    from app.services.document_signing_service import sign_document

    result = sign_document(
        data,
        mime,
        title=title,
        org_id=org_id,
        document_id=document_id,
        action=action,
        private_key_pem=private_key_pem,
        cert_chain_pem=cert_chain_pem,
    )

    return {
        "success": True,
        "media_type": "document",
        "asset_id": document_id,
        "mime_type": mime,
        "c2pa_instance_id": result.instance_id,
        "c2pa_signed": True,
        "original_hash": None,
        "signed_hash": None,
        "size_bytes": len(result.signed_bytes),
        "signed_file_b64": base64.b64encode(result.signed_bytes).decode("utf-8"),
        "has_ingredient": ingredient_data is not None,
    }
