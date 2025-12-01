"""Signing router for content signing with C2PA manifests."""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_sign_permission
from app.middleware.api_rate_limiter import api_rate_limiter
from app.observability.metrics import increment
from app.models.request_models import SignRequest
from app.models.response_models import SignResponse
from app.services.signing_executor import execute_signing

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

    signing_result = await execute_signing(
        request=request,
        organization=organization,
        db=db,
        document_id=request.document_id,
    )
    increment("sign_requests")
    return signing_result
