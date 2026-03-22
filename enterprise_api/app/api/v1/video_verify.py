"""Public video verification endpoint: /verify/video.

No authentication required. Rate-limited via public_rate_limiter.
Signing remains Enterprise-gated in enterprise/video_attribution.py.
"""

import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile, status
from pydantic import BaseModel

from app.config import settings
from app.middleware.public_rate_limiter import public_rate_limiter

router = APIRouter()
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Response schema
# ---------------------------------------------------------------------------


class PublicVideoVerifyResponse(BaseModel):
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
    "/verify/video",
    summary="Verify a C2PA-signed video file",
    description=(
        "Public endpoint. Accepts a video file as multipart/form-data, extracts "
        "and verifies the embedded JUMBF C2PA manifest. No authentication required."
    ),
)
async def verify_video(
    request: Request,
    file: UploadFile = File(..., description="Video file to verify"),
    mime_type: str = Form(..., description="Video MIME type (video/mp4, video/quicktime, video/x-msvideo)"),
) -> PublicVideoVerifyResponse:
    """Verify a C2PA manifest embedded in a video file."""
    correlation_id = str(uuid.uuid4())
    verified_at = datetime.now(timezone.utc).isoformat()

    await public_rate_limiter(request, endpoint_type="verify_video")

    video_bytes = await file.read()
    if not video_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    if len(video_bytes) > settings.public_video_max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Payload exceeds {settings.public_video_max_size_bytes} bytes limit",
        )

    from app.services.video_verification_service import verify_video_c2pa

    result = verify_video_c2pa(video_bytes, mime_type)

    return PublicVideoVerifyResponse(
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
