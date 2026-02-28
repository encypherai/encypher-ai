"""Rich article signing router: POST /sign/rich endpoint.

Signs rich articles (text + embedded images) as a single atomic provenance unit
using the C2PA standard. Each image gets a standalone JUMBF-embedded C2PA manifest,
and the article-level manifest binds text + images via an ingredient list.
"""
import asyncio
import logging
import uuid

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_content_db, get_db
from app.dependencies import require_sign_permission
from app.middleware.api_rate_limiter import api_rate_limiter
from app.observability.metrics import increment
from app.schemas.api_response import ErrorCode
from app.schemas.rich_sign_schemas import RichArticleSignRequest
from app.services.rich_signing_service import execute_rich_signing
from app.services.webhook_dispatcher import emit_document_signed
from app.utils.quota import QuotaManager, QuotaType

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/sign/rich",
    status_code=status.HTTP_201_CREATED,
    summary="Sign rich article (text + images) with C2PA",
    description="""
Sign a rich article containing both text and embedded images as a single
atomic provenance unit.

Each image receives a standalone C2PA JUMBF-embedded manifest. The article-level
composite manifest binds text (via Merkle root) and all images (via ingredient
references) into a single provenance record.

**Tier feature matrix:**

| Feature | Free | Enterprise |
|---------|------|------------|
| Basic image C2PA signing | Yes | Yes |
| pHash attribution indexing | Yes | Yes |
| TrustMark neural watermark | No | Yes |

**Quota:** Each call consumes (N_images + 1 text + 1 composite) signatures.

**Images:** Up to 20 images per request. Each image is base64-encoded in the
request body and returned base64-encoded in the response. Publishers are
responsible for hosting signed images on their own CDN.
""",
    responses={
        201: {"description": "Article signed successfully"},
        400: {"description": "Invalid request (bad image data, unsupported MIME type)"},
        403: {"description": "Feature requires higher tier or insufficient quota"},
        422: {"description": "Image signing or text signing failed"},
        429: {"description": "Rate limit exceeded"},
        503: {"description": "Signing credentials not configured"},
    },
)
async def sign_rich_content(
    request: RichArticleSignRequest,
    http_request: Request,
    response: Response,
    organization: dict = Depends(require_sign_permission),
    core_db: AsyncSession = Depends(get_db),
    content_db: AsyncSession = Depends(get_content_db),
):
    """
    Sign a rich article with text + embedded images.

    Validates the request, checks quota, signs all images and text, builds the
    composite manifest, and returns base64-encoded signed images plus the composite
    manifest summary.
    """
    correlation_id = (
        getattr(http_request.state, "request_id", None)
        or f"req-{uuid.uuid4().hex[:12]}"
    )
    tier = (organization.get("tier") or "free").lower().replace("-", "_")
    org_id = organization["organization_id"]

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

    # Quota check: 1 (text) + N_images (images) + 1 (composite) = N+2 signatures
    quota_increment = len(request.images) + 2
    await QuotaManager.check_quota(
        db=core_db,
        organization_id=org_id,
        quota_type=QuotaType.C2PA_SIGNATURES,
        increment=quota_increment,
    )

    # Execute rich signing pipeline
    result = await execute_rich_signing(
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

    # Emit webhook for rich article signing
    if result.get("success") and result.get("data"):
        data = result["data"]
        asyncio.create_task(
            emit_document_signed(
                organization_id=org_id,
                document_id=data["document_id"],
                title=request.document_title,
                document_type="rich_article",
            )
        )

    if result.get("success"):
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)
    else:
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=result)
