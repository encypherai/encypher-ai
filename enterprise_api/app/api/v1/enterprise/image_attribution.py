"""Enterprise image attribution endpoint: POST /enterprise/images/attribution."""

import base64
import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_content_db
from app.dependencies import require_sign_permission
from app.schemas.image_attribution_schemas import (
    ImageAttributionMatchResponse,
    ImageAttributionRequest,
    ImageAttributionResponse,
)
from app.services.image_fingerprint_service import search_by_phash

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/enterprise/images/attribution",
    summary="Find images by perceptual similarity (Enterprise: cross-org)",
    description=(
        "Search for images with similar visual content using perceptual hashing (pHash). "
        "scope='org' is available to all tiers. "
        "scope='all' (cross-organization search) requires Enterprise tier."
    ),
    tags=["Image Attribution"],
)
async def image_attribution(
    payload: ImageAttributionRequest,
    request: Request,
    organization: dict = Depends(require_sign_permission),
    content_db: AsyncSession = Depends(get_content_db),
) -> ImageAttributionResponse:
    org_id: str = organization["organization_id"]
    features = organization.get("features", {})

    # Cross-org search requires Enterprise
    if payload.scope == "all" and not features.get("image_fuzzy_search", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=("scope='all' cross-organization search requires Enterprise tier. Use scope='org' for organization-scoped search."),
        )

    # Resolve pHash from image_data or direct hex input
    if payload.image_data is not None:
        try:
            image_bytes = base64.b64decode(payload.image_data)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid base64 image_data")
        from app.utils.image_utils import compute_phash

        try:
            phash_int = compute_phash(image_bytes)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=f"Cannot compute pHash: {exc}")
        phash_hex = format(phash_int & 0xFFFFFFFFFFFFFFFF, "016x")
    else:
        # Parse hex pHash from payload.phash (guaranteed non-None by schema validator)
        try:
            phash_unsigned = int(payload.phash, 16)  # type: ignore[arg-type]
            # Convert to signed int64 for PostgreSQL BIGINT compatibility
            phash_int = phash_unsigned if phash_unsigned < (1 << 63) else phash_unsigned - (1 << 64)
            phash_hex = payload.phash  # type: ignore[assignment]
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid phash hex string")

    matches = await search_by_phash(
        phash_query=phash_int,
        threshold_bits=payload.threshold,
        scope=payload.scope,
        org_id=org_id if payload.scope == "org" else None,
        db=content_db,
    )

    return ImageAttributionResponse(
        success=True,
        query_phash=phash_hex,
        match_count=len(matches),
        matches=[
            ImageAttributionMatchResponse(
                image_id=m.image_id,
                document_id=m.document_id,
                organization_id=m.organization_id if payload.scope == "all" else org_id,
                filename=m.filename,
                hamming_distance=m.hamming_distance,
                similarity_score=m.similarity_score,
                signed_hash=m.signed_hash,
                created_at=m.created_at,
            )
            for m in matches
        ],
        scope=payload.scope,
        threshold=payload.threshold,
    )
