"""
Multi-Source Hash Table Lookup API Endpoints (TEAM_044 - Patent FIG. 8).

These endpoints enable lookup of content across multiple sources
with chronological ordering and authority ranking.
"""

import logging
import time
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_organization
from app.schemas.multi_source import (
    MultiSourceLookupRequest,
    MultiSourceLookupResponse,
)
from app.services.multi_source_service import multi_source_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/attribution", tags=["Multi-Source Attribution"])


@router.post("/multi-source", response_model=MultiSourceLookupResponse)
async def multi_source_lookup(
    request: MultiSourceLookupRequest,
    organization: Dict = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> MultiSourceLookupResponse:
    """
    Look up content across multiple sources.

    Returns all matching sources with linked-list tracking,
    chronological ordering, and optional authority ranking.

    **Tier Requirement:** Business+ (Authority ranking requires Enterprise)

    Patent Reference: FIG. 8 - Multi-Source Hash Table Lookup
    """
    start_time = time.time()
    organization_id = organization["organization_id"]

    # TEAM_145: Multi-source lookup available to all tiers; authority ranking requires Enterprise
    tier = organization.get("tier", "free").lower()
    is_enterprise = tier in {"enterprise", "strategic_partner", "demo"}

    # Authority ranking requires Enterprise
    if request.include_authority_score and not is_enterprise:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FEATURE_NOT_AVAILABLE",
                "message": "Authority ranking requires Enterprise tier",
                "required_tier": "enterprise",
                "current_tier": tier,
                "upgrade_url": "/billing/upgrade",
            },
        )

    try:
        sources, query_hash, original_source = await multi_source_service.lookup_sources(
            db=db,
            organization_id=organization_id,
            text_segment=request.text_segment,
            include_all_sources=request.include_all_sources,
            order_by=request.order_by,
            include_authority_score=request.include_authority_score,
            max_results=request.max_results,
        )

        processing_time_ms = (time.time() - start_time) * 1000

        # Determine if sources form a chain
        has_chain = len(sources) > 1
        chain_length = len(sources)

        logger.info(f"Multi-source lookup for org {organization_id}: found {len(sources)} sources, time={processing_time_ms:.2f}ms")

        return MultiSourceLookupResponse(
            success=True,
            query_hash=query_hash,
            total_sources=len(sources),
            sources=sources,
            original_source=original_source,
            has_chain=has_chain,
            chain_length=chain_length,
            processing_time_ms=round(processing_time_ms, 2),
            message=f"Found {len(sources)} source(s) for the queried content",
        )

    except Exception as e:
        logger.error(f"Failed to perform multi-source lookup: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "LOOKUP_FAILED", "message": str(e)},
        )
