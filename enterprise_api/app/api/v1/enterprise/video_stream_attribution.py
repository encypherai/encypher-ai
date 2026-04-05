"""Enterprise video stream C2PA signing endpoints (C2PA 2.3 Section 19).

POST /enterprise/video/stream/start                  -- Start a stream signing session
POST /enterprise/video/stream/{session_id}/segment   -- Sign a single segment
POST /enterprise/video/stream/{session_id}/finalize  -- Finalize and get Merkle root
GET  /enterprise/video/stream/{session_id}/status    -- Check session status
"""

import base64
import json
import logging
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_enterprise_tier
from app.models.organization import Organization

router = APIRouter()
logger = logging.getLogger(__name__)

require_enterprise_video_stream = require_enterprise_tier("Video stream signing")


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class StreamStartResponse(BaseModel):
    session_id: str
    status: str
    message: str


class StreamSegmentResponse(BaseModel):
    session_id: str
    segment_index: int
    signed_segment_base64: str
    original_hash: str
    signed_hash: str
    c2pa_instance_id: str
    c2pa_manifest_hash: str
    size_bytes: int
    mime_type: str
    c2pa_signed: bool
    watermark_applied: bool


class StreamFinalizeResponse(BaseModel):
    session_id: str
    segment_count: int
    merkle_root: str
    status: str


class StreamStatusResponse(BaseModel):
    session_id: str
    status: str
    segment_count: int
    created_at: float
    last_activity: float
    expires_at: float


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/enterprise/video/stream/start",
    status_code=status.HTTP_201_CREATED,
    summary="Start video stream signing session",
    description=(
        "Create a new session for signing video stream segments. "
        "Signing credentials are cached for the session lifetime. "
        "Each segment is signed individually with manifest chaining."
    ),
    tags=["Video Stream Attribution"],
)
async def stream_start(
    request: Request,
    enable_video_watermark: bool = Form(default=False, description="Embed spread-spectrum watermark in each segment"),
    organization: dict = Depends(require_enterprise_video_stream),
    db: AsyncSession = Depends(get_db),
) -> StreamStartResponse:
    org_id: str = organization["organization_id"]

    # Load org for signing credentials
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail=f"Organization {org_id} not found")

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
        logger.warning("video_stream: could not load private key for org=%s (passthrough): %s", org_id, exc)

    from app.services.video_stream_signing_service import start_stream_session

    session = await start_stream_session(
        org_id=org_id,
        private_key_pem=private_key_pem,
        cert_chain_pem=cert_chain_pem,
        enable_video_watermark=enable_video_watermark,
    )

    return StreamStartResponse(
        session_id=session.session_id,
        status=session.status,
        message="Stream signing session created. Send segments to /enterprise/video/stream/{session_id}/segment",
    )


@router.post(
    "/enterprise/video/stream/{session_id}/segment",
    summary="Sign a video stream segment",
    description="Sign a single CMAF/fMP4 segment with a C2PA manifest. Manifest is chained to the previous segment.",
    tags=["Video Stream Attribution"],
)
async def stream_segment(
    session_id: str,
    request: Request,
    file: UploadFile = File(..., description="Video segment file (fMP4/CMAF)"),
    mime_type: str = Form(default="video/mp4", description="Segment MIME type"),
    title: str = Form(default="stream-segment", description="Segment title"),
    action: str = Form(default="c2pa.created", description="C2PA action"),
    custom_assertions: str = Form(default="[]", description="JSON-encoded assertions"),
    rights_data: str = Form(default="{}", description="JSON-encoded rights metadata"),
    organization: dict = Depends(require_enterprise_video_stream),
) -> StreamSegmentResponse:
    org_id: str = organization["organization_id"]

    from app.services.video_stream_signing_service import get_session, sign_segment

    session = await get_session(session_id, org_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Stream session {session_id} not found or expired")

    try:
        parsed_assertions = json.loads(custom_assertions)
    except (json.JSONDecodeError, TypeError):
        raise HTTPException(status_code=400, detail="custom_assertions must be valid JSON array")

    try:
        parsed_rights = json.loads(rights_data)
    except (json.JSONDecodeError, TypeError):
        raise HTTPException(status_code=400, detail="rights_data must be valid JSON object")

    segment_bytes = await file.read()
    if not segment_bytes:
        raise HTTPException(status_code=400, detail="Uploaded segment is empty")

    try:
        result = await sign_segment(
            session,
            segment_bytes,
            mime_type,
            title=title,
            action=action,
            custom_assertions=parsed_assertions,
            rights_data=parsed_rights,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return StreamSegmentResponse(
        session_id=session_id,
        segment_index=result.segment_index,
        signed_segment_base64=base64.b64encode(result.signed_bytes).decode(),
        original_hash=result.original_hash,
        signed_hash=result.signed_hash,
        c2pa_instance_id=result.c2pa_instance_id,
        c2pa_manifest_hash=result.c2pa_manifest_hash,
        size_bytes=result.size_bytes,
        mime_type=result.mime_type,
        c2pa_signed=result.c2pa_signed,
        watermark_applied=result.watermark_applied,
    )


@router.post(
    "/enterprise/video/stream/{session_id}/finalize",
    summary="Finalize video stream session",
    description="Finalize the stream session and compute a Merkle root over all segment manifest hashes.",
    tags=["Video Stream Attribution"],
)
async def stream_finalize(
    session_id: str,
    request: Request,
    organization: dict = Depends(require_enterprise_video_stream),
) -> StreamFinalizeResponse:
    org_id: str = organization["organization_id"]

    from app.services.video_stream_signing_service import finalize_stream, get_session

    session = await get_session(session_id, org_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Stream session {session_id} not found or expired")

    try:
        result = await finalize_stream(session)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return StreamFinalizeResponse(
        session_id=result.session_id,
        segment_count=result.segment_count,
        merkle_root=result.merkle_root,
        status=result.status,
    )


@router.get(
    "/enterprise/video/stream/{session_id}/status",
    summary="Check stream session status",
    description="Get the current status of a video stream signing session.",
    tags=["Video Stream Attribution"],
)
async def stream_status(
    session_id: str,
    request: Request,
    organization: dict = Depends(require_enterprise_video_stream),
) -> StreamStatusResponse:
    org_id: str = organization["organization_id"]

    from app.services.video_stream_signing_service import get_session

    session = await get_session(session_id, org_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Stream session {session_id} not found or expired")

    return StreamStatusResponse(
        session_id=session.session_id,
        status=session.status,
        segment_count=session.segment_count,
        created_at=session.created_at,
        last_activity=session.last_activity,
        expires_at=session.expires_at,
    )
