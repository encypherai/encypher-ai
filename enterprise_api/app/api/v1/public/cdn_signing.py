"""Public CDN Edge Provenance Worker signing endpoints.

These endpoints do NOT require authentication. They are designed for the
Encypher Cloudflare Edge Provenance Worker to auto-sign publisher content
with C2PA provenance markers that survive copy-paste. Rate limited by
IP and domain.
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.public_rate_limiter import public_rate_limiter
from app.models.cdn_content_record import CdnContentRecord
from app.schemas.cdn_content_schemas import (
    CdnClaimRequest,
    CdnProvisionRequest,
    CdnProvisionResponse,
    CdnSignRequest,
    CdnSignResponse,
)
from app.services.cdn_signing_service import provision_domain, sign_or_retrieve

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/public/cdn", tags=["Public - CDN Edge Provenance"])


@router.post(
    "/provision",
    response_model=CdnProvisionResponse,
    summary="Auto-provision a domain for CDN edge signing",
    description="""
    Public endpoint called by the Cloudflare Edge Provenance Worker on first
    request. Resolves or creates an organization for the publisher domain
    using cross-channel resolution (checks Prebid, CDN, and dashboard orgs).

    **No authentication required.**

    Returns org_id, domain_token, dashboard_url, and claim_url. The worker
    caches this in KV for subsequent requests.

    **Rate Limiting:** 60 requests/minute per IP.
    """,
    responses={
        200: {"description": "Domain provisioned or existing org resolved"},
        429: {"description": "Rate limit exceeded"},
    },
)
async def cdn_provision(
    provision_request: CdnProvisionRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> CdnProvisionResponse:
    """Provision or resolve an org for a CDN domain."""
    await public_rate_limiter(request, endpoint_type="cdn_provision")

    try:
        result = await provision_domain(
            db=db,
            domain=provision_request.domain,
            worker_version=provision_request.worker_version,
        )
        return CdnProvisionResponse(**result)

    except Exception as e:
        logger.error("CDN provision failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Provisioning failed",
        )


@router.post(
    "/sign",
    response_model=CdnSignResponse,
    summary="Sign article content for CDN edge marker embedding",
    description="""
    Public endpoint for the Cloudflare Edge Provenance Worker. Accepts article
    text extracted from HTML at the edge, signs it with micro+ECC+C2PA markers
    at sentence-level granularity, and returns an embedding plan that the worker
    applies to inject invisible markers into the HTML text nodes.

    **No authentication required.** Signing options are controlled by the
    org's tier (set via dashboard), not by the worker.

    Content text is never stored. Only hashes, metadata, embedding plans, and
    C2PA manifests are persisted. Duplicate requests for the same content on
    the same domain return the existing embedding plan without charging quota.

    **Rate Limiting:**
    - 60 requests/minute per IP
    - 1,000 unique content signatures per domain per month (free tier)
    """,
    responses={
        200: {"description": "Content signed or existing embedding plan returned"},
        429: {"description": "Rate limit or quota exceeded"},
    },
)
async def cdn_sign(
    sign_request: CdnSignRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> CdnSignResponse:
    """Sign article content and return embedding plan for CDN edge injection."""
    await public_rate_limiter(request, endpoint_type="cdn_sign")

    try:
        result = await sign_or_retrieve(
            db=db,
            text_content=sign_request.text,
            page_url=sign_request.page_url,
            org_id=sign_request.org_id,
            document_title=sign_request.document_title,
            boundary_selector=sign_request.boundary_selector,
        )
        return CdnSignResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("CDN sign failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Signing failed",
        )


@router.get(
    "/manifest/{record_id}",
    summary="Retrieve a CDN content manifest",
    description="Returns the C2PA manifest metadata for a signed CDN content record.",
    responses={
        200: {"description": "Manifest metadata"},
        404: {"description": "Record not found"},
    },
)
async def cdn_manifest(
    record_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Serve a stored CDN content manifest by record ID."""
    result = await db.execute(select(CdnContentRecord).where(CdnContentRecord.id == record_id))
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
            "claim_generator": store.get("claim_generator", "Encypher CDN Provenance/1.0"),
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
    summary="Check signing status for a CDN domain",
    description="Returns signing statistics for a CDN-provisioned domain.",
    responses={
        200: {"description": "Domain signing stats"},
    },
)
async def cdn_status(
    domain: str,
    db: AsyncSession = Depends(get_db),
):
    """Return signing stats for a CDN-provisioned domain."""
    from app.services.cdn_signing_service import _generate_cdn_org_id, resolve_publisher_org
    from app.models.organization import Organization

    # Try to find the org via cross-channel resolution
    cdn_org_id = _generate_cdn_org_id(domain.lower())
    result = await db.execute(
        select(
            Organization.id,
            Organization.documents_signed,
            Organization.monthly_quota,
            Organization.tier,
        ).where(Organization.id == cdn_org_id)
    )
    row = result.one_or_none()

    if not row:
        return {
            "domain": domain,
            "provisioned": False,
            "total_signed": 0,
            "quota_remaining": 1000,
        }

    org_id, signed, quota, tier = row
    remaining = max(0, quota - signed) if quota != -1 else -1

    return {
        "domain": domain,
        "provisioned": True,
        "org_id": org_id,
        "tier": tier,
        "total_signed": signed,
        "quota_limit": quota,
        "quota_remaining": remaining,
        "upgrade_url": f"https://encypher.com/enterprise?ref=cdn&domain={domain}",
    }
