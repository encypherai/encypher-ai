"""Public audio verification endpoint: /verify/audio.

No authentication required. Rate-limited via public_rate_limiter.
Signing remains Enterprise-gated in enterprise/audio_attribution.py.
"""

import base64
import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field

from app.config import settings
from app.middleware.public_rate_limiter import public_rate_limiter

router = APIRouter()
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class PublicAudioVerifyRequest(BaseModel):
    """Request to verify a C2PA manifest in an audio file."""

    audio_data: str = Field(
        ...,
        description="Base64-encoded audio file bytes",
    )
    mime_type: str = Field(
        ...,
        description="Audio MIME type (audio/wav, audio/mpeg, audio/mp4)",
    )


class PublicAudioVerifyResponse(BaseModel):
    success: bool
    valid: bool
    c2pa_manifest_valid: bool
    hash_matches: bool
    c2pa_instance_id: str | None = None
    signer: str | None = None
    signed_at: str | None = None
    manifest_data: dict | None = None
    error: str | None = None
    correlation_id: str | None = None
    verified_at: str | None = None


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.post(
    "/verify/audio",
    summary="Verify a C2PA-signed audio file",
    description=(
        "Public endpoint. Accepts a base64-encoded audio file, extracts and " "verifies the embedded JUMBF C2PA manifest. No authentication required."
    ),
)
async def verify_audio(
    payload: PublicAudioVerifyRequest,
    request: Request,
) -> PublicAudioVerifyResponse:
    """Verify a C2PA manifest embedded in an audio file supplied as base64."""
    correlation_id = str(uuid.uuid4())
    verified_at = datetime.now(timezone.utc).isoformat()

    await public_rate_limiter(request, endpoint_type="verify_audio")

    try:
        audio_bytes = base64.b64decode(payload.audio_data, validate=True)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 audio data")

    if not audio_bytes:
        raise HTTPException(status_code=400, detail="audio_data is empty")

    if len(audio_bytes) > settings.public_audio_max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Payload exceeds {settings.public_audio_max_size_bytes} bytes limit",
        )

    from app.services.audio_verification_service import verify_audio_c2pa

    result = verify_audio_c2pa(audio_bytes, payload.mime_type)

    return PublicAudioVerifyResponse(
        success=result.valid,
        valid=result.valid,
        c2pa_manifest_valid=result.c2pa_manifest_valid,
        hash_matches=result.hash_matches,
        c2pa_instance_id=result.c2pa_instance_id,
        signer=result.signer,
        signed_at=result.signed_at,
        manifest_data=result.manifest_data,
        error=result.error,
        correlation_id=correlation_id,
        verified_at=verified_at,
    )
