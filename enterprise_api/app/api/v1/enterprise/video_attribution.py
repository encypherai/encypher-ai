"""Enterprise video C2PA signing and verification endpoints.

POST /enterprise/video/sign      -- Sign a video file with a C2PA manifest (multipart upload)
POST /enterprise/video/verify    -- Verify a C2PA manifest in a video file (multipart upload)
GET  /enterprise/video/download/{video_id} -- Download signed video bytes
"""

import base64
import json
import logging
import time
import uuid
from typing import Dict, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_organization
from app.models.organization import Organization

router = APIRouter()
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tier gate
# ---------------------------------------------------------------------------

_ALLOWED_TIERS = {"enterprise", "strategic_partner", "demo"}


def require_enterprise_video(
    organization: dict = Depends(get_current_organization),
) -> dict:
    """Require Enterprise (or equivalent) tier for video C2PA endpoints."""
    tier = (organization.get("tier") or "free").lower().replace("-", "_")
    if tier not in _ALLOWED_TIERS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FEATURE_NOT_AVAILABLE",
                "message": "Video C2PA signing requires Enterprise tier",
                "required_tier": "enterprise",
                "current_tier": tier,
                "upgrade_url": "/billing/upgrade",
            },
        )
    return organization


# ---------------------------------------------------------------------------
# Signed video temp cache (for large file downloads)
# ---------------------------------------------------------------------------

_VIDEO_DOWNLOAD_TTL = 600  # 10 minutes
_VIDEO_RESPONSE_THRESHOLD = 50 * 1024 * 1024  # 50 MB - above this, use download endpoint
# Dict of video_id -> (signed_bytes, org_id, expiry_timestamp)
_signed_video_cache: Dict[str, tuple] = {}


def _cache_signed_video(video_id: str, signed_bytes: bytes, org_id: str) -> None:
    """Store signed video bytes for later download."""
    _cleanup_expired_cache()
    _signed_video_cache[video_id] = (signed_bytes, org_id, time.time() + _VIDEO_DOWNLOAD_TTL)


def _get_cached_video(video_id: str, org_id: str) -> Optional[bytes]:
    """Retrieve cached signed video bytes, or None if expired/missing."""
    _cleanup_expired_cache()
    entry = _signed_video_cache.get(video_id)
    if entry is None:
        return None
    signed_bytes, cached_org_id, expiry = entry
    if cached_org_id != org_id:
        return None  # org mismatch
    if time.time() > expiry:
        _signed_video_cache.pop(video_id, None)
        return None
    return signed_bytes


def _cleanup_expired_cache() -> None:
    """Remove expired entries from the cache."""
    now = time.time()
    expired = [k for k, (_, _, exp) in _signed_video_cache.items() if now > exp]
    for k in expired:
        del _signed_video_cache[k]


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class VideoSignResponse(BaseModel):
    success: bool
    video_id: str
    document_id: str
    signed_video_base64: Optional[str] = Field(
        default=None,
        description="Base64-encoded signed video (null for files > 50MB; use download_url instead)",
    )
    download_url: Optional[str] = Field(
        default=None,
        description="URL to download signed video (for files > 50MB)",
    )
    original_hash: str
    signed_hash: str
    c2pa_instance_id: str
    c2pa_manifest_hash: str
    size_bytes: int
    mime_type: str
    c2pa_signed: bool


class VideoVerifyResponse(BaseModel):
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
    "/enterprise/video/sign",
    status_code=status.HTTP_201_CREATED,
    summary="Sign video with C2PA manifest",
    description=(
        "Embed a C2PA manifest into a video file (MP4, MOV, M4V, AVI). "
        "Upload as multipart/form-data. The signed video is returned as base64 "
        "for files under 50MB, or via a download URL for larger files. "
        "Requires a configured signing certificate (SSL.com or BYOK)."
    ),
    tags=["Video Attribution"],
)
async def video_sign(
    request: Request,
    file: UploadFile = File(..., description="Video file (MP4, MOV, M4V, AVI)"),
    mime_type: str = Form(..., description="Video MIME type (video/mp4, video/quicktime, video/x-msvideo)"),
    title: str = Form(default="untitled-video", description="Title for C2PA manifest"),
    document_id: Optional[str] = Form(default=None, description="Custom document ID (auto-generated if omitted)"),
    action: str = Form(default="c2pa.created", description="C2PA action (c2pa.created, c2pa.edited, c2pa.transcoded)"),
    custom_assertions: str = Form(default="[]", description="JSON-encoded list of additional C2PA assertions"),
    rights_data: str = Form(default="{}", description="JSON-encoded rights metadata"),
    organization: dict = Depends(require_enterprise_video),
    db: AsyncSession = Depends(get_db),
) -> VideoSignResponse:
    org_id: str = organization["organization_id"]

    # Parse JSON form fields
    try:
        parsed_assertions = json.loads(custom_assertions)
    except (json.JSONDecodeError, TypeError):
        raise HTTPException(status_code=400, detail="custom_assertions must be valid JSON array")

    try:
        parsed_rights = json.loads(rights_data)
    except (json.JSONDecodeError, TypeError):
        raise HTTPException(status_code=400, detail="rights_data must be valid JSON object")

    # Read video bytes
    video_bytes = await file.read()
    if not video_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    # Load Organization model
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail=f"Organization {org_id} not found")

    doc_id = document_id or f"doc_{uuid.uuid4().hex[:16]}"

    from app.services.video_signing_executor import execute_video_signing

    try:
        signing_result = await execute_video_signing(
            video_bytes=video_bytes,
            mime_type=mime_type,
            title=title,
            org=org,
            db=db,
            document_id=doc_id,
            custom_assertions=parsed_assertions,
            rights_data=parsed_rights,
            action=action,
        )
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # Determine response format based on size
    signed_b64: Optional[str] = None
    download_url: Optional[str] = None

    if len(signing_result.signed_bytes) <= _VIDEO_RESPONSE_THRESHOLD:
        signed_b64 = base64.b64encode(signing_result.signed_bytes).decode()
    else:
        _cache_signed_video(signing_result.video_id, signing_result.signed_bytes, org_id)
        download_url = f"/api/v1/enterprise/video/download/{signing_result.video_id}"

    return VideoSignResponse(
        success=True,
        video_id=signing_result.video_id,
        document_id=doc_id,
        signed_video_base64=signed_b64,
        download_url=download_url,
        original_hash=signing_result.original_hash,
        signed_hash=signing_result.signed_hash,
        c2pa_instance_id=signing_result.c2pa_instance_id,
        c2pa_manifest_hash=signing_result.c2pa_manifest_hash,
        size_bytes=signing_result.size_bytes,
        mime_type=signing_result.mime_type,
        c2pa_signed=signing_result.c2pa_signed,
    )


@router.post(
    "/enterprise/video/verify",
    summary="Verify C2PA manifest in video file",
    description="Extract and verify the C2PA manifest embedded in a video file. Upload as multipart/form-data.",
    tags=["Video Attribution"],
)
async def video_verify(
    request: Request,
    file: UploadFile = File(..., description="Video file to verify"),
    mime_type: str = Form(..., description="Video MIME type"),
    organization: dict = Depends(require_enterprise_video),
) -> VideoVerifyResponse:
    video_bytes = await file.read()
    if not video_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    from app.services.video_verification_service import verify_video_c2pa

    result = verify_video_c2pa(video_bytes, mime_type)

    return VideoVerifyResponse(
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


@router.get(
    "/enterprise/video/download/{video_id}",
    summary="Download signed video",
    description="Download signed video bytes. Available for 10 minutes after signing files larger than 50MB.",
    tags=["Video Attribution"],
)
async def video_download(
    video_id: str,
    request: Request,
    organization: dict = Depends(require_enterprise_video),
) -> Response:
    org_id: str = organization["organization_id"]
    signed_bytes = _get_cached_video(video_id, org_id)
    if signed_bytes is None:
        raise HTTPException(
            status_code=404,
            detail="Signed video not found or expired. Re-sign the video to generate a new download.",
        )
    return Response(
        content=signed_bytes,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{video_id}.mp4"'},
    )
