"""Batch signing and verification endpoints."""
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_sign_permission, require_verify_permission
from app.middleware.api_rate_limiter import api_rate_limiter
from app.schemas.batch import BatchResponseEnvelope, BatchSignRequest, BatchVerifyRequest
from app.services.batch_service import batch_service

router = APIRouter(prefix="/api/v1", tags=["Batch"])


def _correlation_id(request: Request) -> str:
    return request.headers.get("x-request-id") or f"req-{uuid4().hex}"


@router.post("/batch/sign", response_model=BatchResponseEnvelope)
async def batch_sign(
    batch_request: BatchSignRequest,
    request: Request,
    response: Response,
    organization: dict = Depends(require_sign_permission),
    db: AsyncSession = Depends(get_db),
) -> BatchResponseEnvelope:
    """Sign multiple documents in a single request."""

    correlation_id = _correlation_id(request)
    allowed, retry_after, remaining, limit = api_rate_limiter.check(
        organization_id=organization["organization_id"],
        scope="batch_sign",
    )
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"code": "E_RATE_BATCH_SIGN", "message": "Batch signing rate limit exceeded"},
            headers={"Retry-After": str(retry_after or 1)},
        )
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Limit"] = str(limit)

    return await batch_service.sign_batch(
        db=db,
        request=batch_request,
        organization=organization,
        correlation_id=correlation_id,
    )


@router.post("/batch/verify", response_model=BatchResponseEnvelope)
async def batch_verify(
    batch_request: BatchVerifyRequest,
    request: Request,
    response: Response,
    organization: dict = Depends(require_verify_permission),
    db: AsyncSession = Depends(get_db),
) -> BatchResponseEnvelope:
    """Verify multiple documents in a single request."""

    correlation_id = _correlation_id(request)
    allowed, retry_after, remaining, limit = api_rate_limiter.check(
        organization_id=organization["organization_id"],
        scope="batch_verify",
    )
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"code": "E_RATE_BATCH_VERIFY", "message": "Batch verification rate limit exceeded"},
            headers={"Retry-After": str(retry_after or 1)},
        )
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Limit"] = str(limit)

    return await batch_service.verify_batch(
        db=db,
        request=batch_request,
        organization=organization,
        correlation_id=correlation_id,
    )
