"""Signing router for content signing with C2PA manifests."""
import asyncio

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_organization_dep, require_sign_permission
from app.middleware.api_rate_limiter import api_rate_limiter
from app.models.request_models import SignRequest
from app.models.response_models import SignResponse
from app.observability.metrics import increment
from app.schemas.embeddings import EncodeWithEmbeddingsRequest, EncodeWithEmbeddingsResponse
from app.services.embedding_executor import encode_document_with_embeddings
from app.services.signing_executor import execute_signing
from app.services.webhook_dispatcher import emit_document_signed
from app.utils.quota import QuotaManager, QuotaType

router = APIRouter()


@router.post("/sign", response_model=SignResponse)
async def sign_content(
    request: SignRequest,
    response: Response,
    organization: dict = Depends(require_sign_permission),
    db: AsyncSession = Depends(get_db),
) -> SignResponse:
    """Sign content with a C2PA manifest."""
    
    # Get tier from organization context for tier-aware rate limiting
    tier = organization.get("tier", "starter")
    
    result = api_rate_limiter.check_with_reset(
        organization_id=organization["organization_id"],
        scope="sign",
        tier=tier,
    )
    
    # Add rate limit headers to response
    for header, value in api_rate_limiter.get_headers(result).items():
        response.headers[header] = value
    
    if not result.allowed:
        detail = {
            "code": "E_RATE_SIGN",
            "message": "Signing rate limit exceeded",
            "hint": f"Rate limit is {result.limit} requests per minute for {tier} tier",
        }
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            headers=api_rate_limiter.get_headers(result),
        )

    # Check monthly quota for C2PA signatures (1 per document)
    await QuotaManager.check_quota(
        db=db,
        organization_id=organization["organization_id"],
        quota_type=QuotaType.C2PA_SIGNATURES,
        increment=1,
    )

    signing_result = await execute_signing(
        request=request,
        organization=organization,
        db=db,
        document_id=request.document_id,
    )
    
    # Add quota usage headers to response
    quota_headers = await QuotaManager.get_quota_headers(
        db=db,
        organization_id=organization["organization_id"],
        quota_type=QuotaType.C2PA_SIGNATURES,
    )
    for header, value in quota_headers.items():
        response.headers[header] = value
    
    increment("sign_requests")
    
    # Emit webhook event (fire and forget - don't block response)
    asyncio.create_task(
        emit_document_signed(
            organization_id=organization["organization_id"],
            document_id=signing_result.document_id,
            title=request.document_title,
            document_type=request.document_type,
        )
    )
    
    return signing_result


@router.post(
    "/sign/advanced",
    response_model=EncodeWithEmbeddingsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Sign with advanced embedding controls",
    description=(
        "Sign a document while enabling advanced embedding controls (e.g., manifest options and distribution strategies).\n\n"
        "Tier requirements are enforced server-side (typically Professional+ depending on selected options)."
    ),
)
async def sign_advanced(
    request: EncodeWithEmbeddingsRequest,
    organization: dict = Depends(get_current_organization_dep),
    db: AsyncSession = Depends(get_db),
) -> EncodeWithEmbeddingsResponse:
    tier = (organization.get("tier") or "starter").lower().replace("-", "_")
    allowed_tiers = {"professional", "business", "enterprise", "strategic_partner", "demo"}
    if tier not in allowed_tiers:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Advanced signing requires Professional tier or higher. Please upgrade your plan.",
        )

    if not organization.get("can_sign", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your API key does not have permission to sign content",
        )

    return await encode_document_with_embeddings(request=request, organization=organization, db=db)
