"""Public Prebid auto-provenance signing endpoints.

These endpoints do NOT require authentication. They are designed for the
Encypher RTD provider module in Prebid.js to auto-sign publisher content
with C2PA provenance. Rate limited by IP and domain.
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Depends

from app.database import get_db
from app.dependencies import _get_client_ip
from app.middleware.public_rate_limiter import public_rate_limiter
from app.models.prebid_content_record import PrebidContentRecord
from app.schemas.prebid_schemas import PrebidSignRequest, PrebidSignResponse
from app.services.prebid_signing_service import sign_or_retrieve

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/public/prebid", tags=["Public - Prebid Provenance"])


@router.post(
    "/sign",
    response_model=PrebidSignResponse,
    summary="Auto-sign article content for Prebid RTD module",
    description="""
    Public endpoint for the Encypher RTD provider module. Accepts article
    text extracted from the DOM, signs it with C2PA provenance (notarization
    model), and returns a manifest URL for injection into OpenRTB bid requests.

    **No authentication required.**

    Content text is never stored. Only hashes, metadata, and C2PA manifests
    are persisted. Duplicate requests for the same content on the same domain
    return the existing manifest without charging quota.

    **Rate Limiting:**
    - 60 requests/minute per IP
    - 1,000 unique content signatures per domain per month (free tier)
    """,
    responses={
        200: {"description": "Content signed or existing manifest returned"},
        429: {"description": "Rate limit or quota exceeded"},
    },
)
async def prebid_sign(
    sign_request: PrebidSignRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> PrebidSignResponse:
    """Sign article content for Prebid RTD module (Path C)."""
    await public_rate_limiter(request, endpoint_type="prebid_sign")

    try:
        result = await sign_or_retrieve(
            db=db,
            page_url=sign_request.page_url,
            text_content=sign_request.text,
            document_title=sign_request.document_title,
        )
        return PrebidSignResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Prebid sign failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Signing failed",
        )


@router.get(
    "/manifest/{record_id}",
    summary="Retrieve a Prebid content manifest",
    description="Returns the C2PA manifest metadata for a signed content record.",
    responses={
        200: {"description": "Manifest metadata"},
        404: {"description": "Record not found"},
    },
)
async def prebid_manifest(
    record_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Serve a stored Prebid content manifest by record ID."""
    result = await db.execute(select(PrebidContentRecord).where(PrebidContentRecord.id == record_id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Manifest not found")

    store = record.manifest_store or {}
    return JSONResponse(
        content={
            "status": "ok",
            "manifest_url": record.manifest_url,
            "signerTier": record.signer_tier,
            "signedAt": record.signed_at.isoformat() if record.signed_at else None,
            "content_hash": record.content_hash,
            "domain": record.domain,
            "canonical_url": record.canonical_url,
            "claim_generator": store.get("claim_generator", "Encypher Prebid Provenance/1.0"),
            "action": "c2pa.created",
            "document_id": store.get("document_id"),
            "verification_url": store.get("verification_url"),
        },
        headers={
            "Access-Control-Allow-Origin": "*",
            "Cache-Control": "public, max-age=86400",
        },
    )


@router.get(
    "/status/{domain}",
    summary="Check signing status for a domain",
    description="Returns signing statistics for a Prebid-provisioned domain.",
    responses={
        200: {"description": "Domain signing stats"},
    },
)
async def prebid_status(
    domain: str,
    db: AsyncSession = Depends(get_db),
):
    """Return signing stats for a Prebid-provisioned domain."""
    from app.services.prebid_signing_service import _generate_prebid_org_id
    from app.models.organization import Organization

    org_id = _generate_prebid_org_id(domain.lower())
    result = await db.execute(
        select(
            Organization.documents_signed,
            Organization.monthly_quota,
        ).where(Organization.id == org_id)
    )
    row = result.one_or_none()

    if not row:
        return {
            "domain": domain,
            "provisioned": False,
            "total_signed": 0,
            "quota_remaining": FREE_TIER_MONTHLY_QUOTA,
        }

    signed, quota = row
    remaining = max(0, quota - signed) if quota != -1 else -1

    return {
        "domain": domain,
        "provisioned": True,
        "org_id": org_id,
        "total_signed": signed,
        "quota_limit": quota,
        "quota_remaining": remaining,
        "upgrade_url": f"https://encypher.com/enterprise?ref=prebid&domain={domain}",
    }


FREE_TIER_MONTHLY_QUOTA = 1000
