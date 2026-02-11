"""Signing router for content signing with C2PA manifests.

This module provides the unified /sign endpoint with tier-gated options.
All signing features are available through this single endpoint.
"""

import asyncio
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_content_db, get_db
from app.dependencies import get_current_organization_dep, require_sign_permission
from app.middleware.api_rate_limiter import api_rate_limiter
from app.observability.metrics import increment
from app.schemas.api_response import ErrorCode, get_batch_limit
from app.schemas.sign_schemas import UnifiedSignRequest
from app.services.organization_bootstrap import ensure_organization_exists
from app.services.unified_signing_service import execute_unified_signing
from app.services.webhook_dispatcher import emit_document_signed
from app.utils.quota import QuotaManager, QuotaType

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Unified Sign Endpoint
# =============================================================================


@router.post(
    "/sign",
    status_code=status.HTTP_201_CREATED,
    summary="Sign content with C2PA manifest",
    description="""
Sign content with C2PA manifest. Features are gated by tier.

**Tier Feature Matrix:**

| Feature | Free | Enterprise |
|---------|------|------------|
| Basic C2PA signing | ✅ | ✅ |
| Sentence/paragraph/section segmentation | ✅ | ✅ |
| Advanced manifest modes | ✅ | ✅ |
| Attribution indexing | ✅ | ✅ |
| Custom assertions | ✅ | ✅ |
| Rights metadata | ✅ | ✅ |
| Batch signing (up to 10) | ✅ | ✅ |
| Word-level segmentation | ❌ | ✅ |
| Dual binding | ❌ | ✅ |
| Fingerprinting | ❌ | ✅ |
| Batch size | 10 | 100 |

**Single Document:**
```json
{
    "text": "Content to sign...",
    "document_title": "My Article",
    "options": {
        "segmentation_level": "sentence"
    }
}
```

**Batch:**
```json
{
    "documents": [
        {"text": "First doc...", "document_title": "Doc 1"},
        {"text": "Second doc...", "document_title": "Doc 2"}
    ],
    "options": {
        "segmentation_level": "sentence"
    }
}
```

The response includes `meta.features_gated` showing features available at higher tiers.
""",
    responses={
        201: {"description": "Content signed successfully"},
        400: {"description": "Invalid request"},
        403: {"description": "Feature requires higher tier"},
        429: {"description": "Rate limit exceeded"},
    },
)
async def sign_content(
    request: UnifiedSignRequest,
    http_request: Request,
    response: Response,
    organization: dict = Depends(require_sign_permission),
    core_db: AsyncSession = Depends(get_db),
    content_db: AsyncSession = Depends(get_content_db),
):
    """
    Unified sign endpoint with tier-gated options.
    
    This endpoint consolidates /sign and /sign/advanced into a single endpoint.
    Features are automatically gated based on the organization's tier.
    """
    correlation_id = f"req-{uuid.uuid4().hex[:12]}"
    # TEAM_145: Default to free tier
    tier = (organization.get("tier") or "free").lower().replace("-", "_")
    org_id = organization["organization_id"]
    
    # Get batch size for rate limiting
    documents = request.get_documents()
    batch_size = len(documents)
    
    # Check batch limit
    batch_limit = get_batch_limit(tier)
    if batch_size > batch_limit:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "success": False,
                "data": None,
                "error": {
                    "code": ErrorCode.E_TIER_REQUIRED,
                    "message": f"Batch size {batch_size} exceeds limit of {batch_limit} for {tier} tier",
                    "hint": "Upgrade your plan to increase batch limits",
                },
                "correlation_id": correlation_id,
                "meta": {"tier": tier},
            },
        )
    
    # Rate limiting
    rate_result = api_rate_limiter.check_with_reset(
        organization_id=org_id,
        scope="sign",
        tier=tier,
    )
    
    for header, value in api_rate_limiter.get_headers(rate_result).items():
        response.headers[header] = value
    
    if not rate_result.allowed:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "success": False,
                "data": None,
                "error": {
                    "code": ErrorCode.E_RATE_SIGN,
                    "message": "Signing rate limit exceeded",
                    "hint": f"Rate limit is {rate_result.limit} requests per minute for {tier} tier",
                },
                "correlation_id": correlation_id,
                "meta": {"tier": tier, "rate_limit_remaining": 0},
            },
            headers=api_rate_limiter.get_headers(rate_result),
        )
    
    await ensure_organization_exists(core_db, organization)
    
    # Check monthly quota
    await QuotaManager.check_quota(
        db=core_db,
        organization_id=org_id,
        quota_type=QuotaType.C2PA_SIGNATURES,
        increment=batch_size,
    )
    
    # Execute unified signing
    result = await execute_unified_signing(
        request=request,
        organization=organization,
        core_db=core_db,
        content_db=content_db,
        correlation_id=correlation_id,
    )
    
    # Add quota headers
    quota_headers = await QuotaManager.get_quota_headers(
        db=core_db,
        organization_id=org_id,
        quota_type=QuotaType.C2PA_SIGNATURES,
    )
    for header, value in quota_headers.items():
        response.headers[header] = value
    
    increment("sign_requests")
    
    # Emit webhook events for each document
    if result.get("success") and result.get("data"):
        data = result["data"]
        if data.get("document"):
            asyncio.create_task(
                emit_document_signed(
                    organization_id=org_id,
                    document_id=data["document"]["document_id"],
                    title=request.document_title,
                    document_type=request.options.document_type,
                )
            )
        elif data.get("documents"):
            for doc_result in data["documents"]:
                asyncio.create_task(
                    emit_document_signed(
                        organization_id=org_id,
                        document_id=doc_result["document_id"],
                        title=doc_result.get("metadata", {}).get("title"),
                        document_type=request.options.document_type,
                    )
                )
    
    # Return appropriate status code
    if result.get("success"):
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)
    else:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content=result)


# =============================================================================
# Legacy /sign/advanced Endpoint (REMOVED)
# =============================================================================


@router.post(
    "/sign/advanced",
    deprecated=True,
    summary="REMOVED - Use POST /sign with options instead",
    description="""
**⚠️ REMOVED: This endpoint has been removed.**

Please use `POST /sign` with options instead.

Migration example:
```json
// Old /sign/advanced request
{
    "document_id": "doc1",
    "text": "...",
    "segmentation_level": "sentence"
}

// New /sign request
{
    "text": "...",
    "document_id": "doc1",
    "options": {
        "segmentation_level": "sentence"
    }
}
```
""",
    responses={
        410: {"description": "Endpoint removed"},
    },
)
async def sign_advanced():
    """REMOVED: Use /sign with options instead."""
    logger.warning("Removed endpoint /sign/advanced called. Use /sign with options instead.")
    
    return JSONResponse(
        status_code=status.HTTP_410_GONE,
        content={
            "error": "This endpoint has been removed",
            "message": "Please use POST /sign with options instead",
            "migration_guide": "Move segmentation_level and other advanced options into the 'options' object",
            "new_endpoint": "/api/v1/sign",
        },
    )
