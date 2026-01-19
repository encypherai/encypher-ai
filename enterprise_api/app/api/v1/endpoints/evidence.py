"""
Evidence Generation API Endpoints (TEAM_044 - Patent FIG. 11).

These endpoints enable generation of court-ready evidence packages
for content attribution and provenance verification.
"""

import logging
import time
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_organization
from app.schemas.evidence import (
    EvidenceGenerateRequest,
    EvidenceGenerateResponse,
)
from app.services.evidence_service import evidence_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/evidence", tags=["Evidence Generation"])


@router.post("/generate", response_model=EvidenceGenerateResponse)
async def generate_evidence(
    request: EvidenceGenerateRequest,
    organization: Dict = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> EvidenceGenerateResponse:
    """
    Generate an evidence package for content attribution.

    This endpoint creates a comprehensive evidence package containing:
    - Content hash verification
    - Merkle proof (if available)
    - Signature verification chain
    - Timestamp verification
    - Source attribution details

    **Tier Requirement:** Enterprise

    Patent Reference: FIG. 11 - Evidence Generation & Attribution Flow
    """
    start_time = time.time()
    organization_id = organization["organization_id"]

    # Tier gating - Enterprise only
    tier = organization.get("tier", "starter").lower()
    tier_levels = {"starter": 0, "professional": 1, "business": 2, "enterprise": 3}
    if tier_levels.get(tier, 0) < 3:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FEATURE_NOT_AVAILABLE",
                "message": "Evidence generation requires Enterprise tier",
                "required_tier": "enterprise",
                "current_tier": tier,
                "upgrade_url": "/billing/upgrade",
            },
        )

    try:
        evidence = await evidence_service.generate_evidence(
            db=db,
            organization_id=organization_id,
            target_text=request.target_text,
            document_id=request.document_id,
            include_merkle_proof=request.include_merkle_proof,
            include_signature_chain=request.include_signature_chain,
            include_timestamp_proof=request.include_timestamp_proof,
        )

        processing_time_ms = (time.time() - start_time) * 1000

        logger.info(
            f"Generated evidence package {evidence.evidence_id} for org {organization_id}: "
            f"attribution_found={evidence.attribution_found}, time={processing_time_ms:.2f}ms"
        )

        return EvidenceGenerateResponse(
            success=True,
            evidence=evidence,
            processing_time_ms=round(processing_time_ms, 2),
            message="Evidence package generated successfully",
        )

    except Exception as e:
        logger.error(f"Failed to generate evidence: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "EVIDENCE_GENERATION_FAILED", "message": str(e)},
        )
