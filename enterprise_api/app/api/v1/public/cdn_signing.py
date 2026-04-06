"""Public CDN Edge Provenance Worker signing endpoints.

These endpoints do NOT require authentication. They are designed for the
Encypher Cloudflare Edge Provenance Worker to auto-sign publisher content
with C2PA provenance markers that survive copy-paste. Rate limited by
IP and domain.

The /domains endpoint requires authentication (used by the dashboard).
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
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
from app.services.cdn_signing_service import claim_domain, provision_domain, sign_or_retrieve

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


@router.post(
    "/claim",
    summary="Claim a CDN domain by verifying the Edge Provenance Worker",
    description="""
    Authenticated endpoint. Verifies that the Edge Provenance Worker is
    deployed on the given domain by fetching its .well-known/encypher-verify
    endpoint. On success, links the CDN domain to the authenticated user's
    organization.
    """,
    responses={
        200: {"description": "Domain claim result"},
    },
)
async def cdn_claim(
    claim_request: CdnClaimRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Claim a CDN-provisioned domain for the authenticated user's org."""
    from app.middleware.auth import get_current_user

    user = await get_current_user(request, db)

    result = await claim_domain(
        db=db,
        domain=claim_request.domain,
        user_id=str(user.id),
        user_org_id=user.active_organization_id,
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Claim failed"),
        )

    return result


@router.get(
    "/domains",
    summary="List CDN edge provenance domains for the current org",
    description="""
    Authenticated endpoint for the dashboard. Returns all domains where the
    Edge Provenance Worker has been deployed and provisioned for the
    current user's organization.
    """,
    responses={
        200: {"description": "List of CDN edge domains"},
    },
)
async def cdn_domains(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """List CDN domains with signing stats for the authenticated user's org."""
    from app.middleware.auth import get_current_user

    user = await get_current_user(request, db)
    org_id = user.active_organization_id
    if not org_id:
        return []

    # Query distinct domains for this org with stats
    result = await db.execute(
        select(
            CdnContentRecord.domain,
            func.count(CdnContentRecord.id).label("articles_signed"),
            func.max(CdnContentRecord.signed_at).label("last_signed_at"),
            func.min(CdnContentRecord.created_at).label("created_at"),
        )
        .where(CdnContentRecord.organization_id == org_id)
        .group_by(CdnContentRecord.domain)
        .order_by(func.max(CdnContentRecord.signed_at).desc())
    )
    rows = result.all()

    return [
        {
            "domain": row.domain,
            "org_id": org_id,
            "articles_signed": row.articles_signed,
            "last_signed_at": row.last_signed_at.isoformat() if row.last_signed_at else None,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "claim_status": "verified",  # If queried via dashboard, user is already verified
        }
        for row in rows
    ]
