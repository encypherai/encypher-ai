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

    allowed, retry_after, remaining, limit = api_rate_limiter.check(
        organization_id=organization["organization_id"],
        scope="sign",
    )
    if not allowed:
        detail = {
            "code": "E_RATE_SIGN",
            "message": "Signing rate limit exceeded",
        }
        headers = {"Retry-After": str(retry_after or 1)}
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=detail, headers=headers)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Limit"] = str(limit)

    result = await execute_signing(
        request=request,
        organization=organization,
        db=db,
        document_id=request.document_id,
    )
    increment("sign_requests")
    return result
