"""Batch signing and verification endpoints."""
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_sign_permission, require_verify_permission
from app.middleware.api_rate_limiter import api_rate_limiter
from app.schemas.batch import BatchResponseEnvelope, BatchSignRequest, BatchVerifyRequest
from app.services.batch_service import batch_service
from app.utils.quota import QuotaManager, QuotaType

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
    tier = organization.get("tier", "starter")
    
    result = api_rate_limiter.check_with_reset(
        organization_id=organization["organization_id"],
        scope="batch_sign",
        tier=tier,
    )
    
    # Add rate limit headers to response
    for header, value in api_rate_limiter.get_headers(result).items():
        response.headers[header] = value
    
    if not result.allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "code": "E_RATE_BATCH_SIGN",
                "message": "Batch signing rate limit exceeded",
                "hint": f"Rate limit is {result.limit} requests per minute for {tier} tier",
            },
            headers=api_rate_limiter.get_headers(result),
        )

    # Check monthly quota for batch operations (1 per batch request)
    await QuotaManager.check_quota(
        db=db,
        organization_id=organization["organization_id"],
        quota_type=QuotaType.BATCH_OPERATIONS,
        increment=1,
    )

    # Also count each document against C2PA signatures quota
    await QuotaManager.check_quota(
        db=db,
        organization_id=organization["organization_id"],
        quota_type=QuotaType.C2PA_SIGNATURES,
        increment=len(batch_request.items),
    )

    result = await batch_service.sign_batch(
        db=db,
        request=batch_request,
        organization=organization,
        correlation_id=correlation_id,
    )
    
    # Add quota usage headers to response
    quota_headers = await QuotaManager.get_quota_headers(
        db=db,
        organization_id=organization["organization_id"],
        quota_type=QuotaType.BATCH_OPERATIONS,
    )
    for header, value in quota_headers.items():
        response.headers[header] = value
    
    return result


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
    tier = organization.get("tier", "starter")
    
    result = api_rate_limiter.check_with_reset(
        organization_id=organization["organization_id"],
        scope="batch_verify",
        tier=tier,
    )
    
    # Add rate limit headers to response
    for header, value in api_rate_limiter.get_headers(result).items():
        response.headers[header] = value
    
    if not result.allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "code": "E_RATE_BATCH_VERIFY",
                "message": "Batch verification rate limit exceeded",
                "hint": f"Rate limit is {result.limit} requests per minute for {tier} tier",
            },
            headers=api_rate_limiter.get_headers(result),
        )

    return await batch_service.verify_batch(
        db=db,
        request=batch_request,
        organization=organization,
        correlation_id=correlation_id,
    )
