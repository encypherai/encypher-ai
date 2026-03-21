"""Enterprise audio C2PA signing and verification endpoints.

POST /enterprise/audio/sign   -- Sign an audio file with a C2PA manifest
POST /enterprise/audio/verify -- Verify a C2PA manifest in an audio file
"""

import base64
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Optional

from app.database import get_db
from app.dependencies import get_current_organization, require_sign_permission
from app.models.organization import Organization

router = APIRouter()
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tier gate
# ---------------------------------------------------------------------------

_ALLOWED_TIERS = {"enterprise", "strategic_partner", "demo"}


def require_enterprise_audio(
    organization: dict = Depends(get_current_organization),
) -> dict:
    """Require Enterprise (or equivalent) tier for audio C2PA endpoints."""
    tier = (organization.get("tier") or "free").lower().replace("-", "_")
    if tier not in _ALLOWED_TIERS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FEATURE_NOT_AVAILABLE",
                "message": "Audio C2PA signing requires Enterprise tier",
                "required_tier": "enterprise",
                "current_tier": tier,
                "upgrade_url": "/billing/upgrade",
            },
        )
    return organization


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class AudioSignRequest(BaseModel):
    """Request to sign an audio file with a C2PA manifest."""

    audio_data: str = Field(
        ...,
        description="Base64-encoded audio file bytes",
    )
    mime_type: str = Field(
        ...,
        description="Audio MIME type (audio/wav, audio/mpeg, audio/mp4)",
    )
    title: str = Field(
        default="untitled-audio",
        max_length=500,
        description="Human-readable title for the C2PA manifest",
    )
    document_id: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Custom document identifier. Auto-generated if omitted.",
    )
    action: str = Field(
        default="c2pa.created",
        description="C2PA action verb (e.g. c2pa.created, c2pa.dubbed, c2pa.mixed)",
    )
    custom_assertions: List[dict] = Field(
        default_factory=list,
        description="Additional C2PA assertions to embed",
    )
    rights_data: Dict = Field(
        default_factory=dict,
        description="Rights metadata for com.encypher.rights.v1 assertion",
    )


class AudioSignResponse(BaseModel):
    success: bool
    audio_id: str
    document_id: str
    signed_audio_base64: str
    original_hash: str
    signed_hash: str
    c2pa_instance_id: str
    c2pa_manifest_hash: str
    size_bytes: int
    mime_type: str
    c2pa_signed: bool


class AudioVerifyRequest(BaseModel):
    """Request to verify a C2PA manifest in an audio file."""

    audio_data: str = Field(
        ...,
        description="Base64-encoded audio file bytes",
    )
    mime_type: str = Field(
        ...,
        description="Audio MIME type (audio/wav, audio/mpeg, audio/mp4)",
    )


class AudioVerifyResponse(BaseModel):
    success: bool
    valid: bool
    c2pa_manifest_valid: bool
    hash_matches: bool
    c2pa_instance_id: Optional[str] = None
    signer: Optional[str] = None
    signed_at: Optional[str] = None
    manifest_data: Optional[dict] = None
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/enterprise/audio/sign",
    status_code=status.HTTP_201_CREATED,
    summary="Sign audio with C2PA manifest",
    description=(
        "Embed a C2PA manifest into an audio file (WAV, MP3, or M4A/AAC). "
        "The signed audio is returned as base64. Requires a configured "
        "signing certificate (SSL.com or BYOK)."
    ),
    tags=["Audio Attribution"],
)
async def audio_sign(
    payload: AudioSignRequest,
    request: Request,
    organization: dict = Depends(require_enterprise_audio),
    db: AsyncSession = Depends(get_db),
) -> AudioSignResponse:
    org_id: str = organization["organization_id"]

    # Decode audio bytes
    try:
        audio_bytes = base64.b64decode(payload.audio_data)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid base64 audio_data",
        )

    if not audio_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="audio_data is empty",
        )

    # Load Organization model for per-org credential access
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization {org_id} not found",
        )

    document_id = payload.document_id or f"doc_{uuid.uuid4().hex[:16]}"

    from app.services.audio_signing_executor import execute_audio_signing

    try:
        signing_result = await execute_audio_signing(
            audio_bytes=audio_bytes,
            mime_type=payload.mime_type,
            title=payload.title,
            org=org,
            db=db,
            document_id=document_id,
            custom_assertions=payload.custom_assertions,
            rights_data=payload.rights_data,
            action=payload.action,
        )
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    return AudioSignResponse(
        success=True,
        audio_id=signing_result.audio_id,
        document_id=document_id,
        signed_audio_base64=base64.b64encode(signing_result.signed_bytes).decode(),
        original_hash=signing_result.original_hash,
        signed_hash=signing_result.signed_hash,
        c2pa_instance_id=signing_result.c2pa_instance_id,
        c2pa_manifest_hash=signing_result.c2pa_manifest_hash,
        size_bytes=signing_result.size_bytes,
        mime_type=signing_result.mime_type,
        c2pa_signed=signing_result.c2pa_signed,
    )


@router.post(
    "/enterprise/audio/verify",
    summary="Verify C2PA manifest in audio file",
    description="Extract and verify the C2PA manifest embedded in an audio file. Returns manifest details and validation status.",
    tags=["Audio Attribution"],
)
async def audio_verify(
    payload: AudioVerifyRequest,
    request: Request,
    organization: dict = Depends(require_enterprise_audio),
) -> AudioVerifyResponse:
    try:
        audio_bytes = base64.b64decode(payload.audio_data)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid base64 audio_data",
        )

    if not audio_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="audio_data is empty",
        )

    from app.services.audio_verification_service import verify_audio_c2pa

    result = verify_audio_c2pa(audio_bytes, payload.mime_type)

    return AudioVerifyResponse(
        success=result.valid,
        valid=result.valid,
        c2pa_manifest_valid=result.c2pa_manifest_valid,
        hash_matches=result.hash_matches,
        c2pa_instance_id=result.c2pa_instance_id,
        signer=result.signer,
        signed_at=result.signed_at,
        manifest_data=result.manifest_data,
        error=result.error,
    )
