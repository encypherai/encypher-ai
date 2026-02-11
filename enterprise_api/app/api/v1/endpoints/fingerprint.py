"""
Robust Fingerprint API Endpoints (TEAM_044).

These endpoints enable keyed fingerprint encoding and detection
for content that survives text modifications.
"""

import logging
import time
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_organization
from app.schemas.fingerprint import (
    FingerprintDetectRequest,
    FingerprintDetectResponse,
    FingerprintEncodeRequest,
    FingerprintEncodeResponse,
)
from app.services.fingerprint_service import fingerprint_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/fingerprint", tags=["Fingerprint"])


@router.post("/encode", response_model=FingerprintEncodeResponse)
async def encode_fingerprint(
    request: FingerprintEncodeRequest,
    organization: Dict = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> FingerprintEncodeResponse:
    """
    Encode a robust fingerprint into text.

    Fingerprints use secret-seeded placement of invisible markers
    that survive text modifications like paraphrasing or truncation.

    **Tier Requirement:** Enterprise
    """
    start_time = time.time()
    organization_id = organization["organization_id"]

    # TEAM_145: Fingerprinting requires Enterprise tier
    tier = organization.get("tier", "free").lower()
    if tier not in {"enterprise", "strategic_partner", "demo"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FEATURE_NOT_AVAILABLE",
                "message": "Robust fingerprinting requires Enterprise tier",
                "required_tier": "enterprise",
                "current_tier": tier,
                "upgrade_url": "/billing/upgrade",
            },
        )

    try:
        fingerprinted_text, fingerprint_id, key_hash, markers_count = await fingerprint_service.encode_fingerprint(
            db=db,
            organization_id=organization_id,
            document_id=request.document_id,
            text=request.text,
            density=request.fingerprint_density,
            fingerprint_key=request.fingerprint_key,
            metadata=request.metadata,
        )

        processing_time_ms = (time.time() - start_time) * 1000

        logger.info(f"Encoded fingerprint {fingerprint_id} for org {organization_id}: {markers_count} markers, time={processing_time_ms:.2f}ms")

        return FingerprintEncodeResponse(
            success=True,
            document_id=request.document_id,
            fingerprint_id=fingerprint_id,
            fingerprinted_text=fingerprinted_text,
            fingerprint_key_hash=key_hash,
            markers_embedded=markers_count,
            processing_time_ms=round(processing_time_ms, 2),
            message=f"Fingerprint encoded with {markers_count} markers",
        )

    except Exception as e:
        logger.error(f"Failed to encode fingerprint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "FINGERPRINT_ENCODE_FAILED", "message": str(e)},
        )


@router.post("/detect", response_model=FingerprintDetectResponse)
async def detect_fingerprint(
    request: FingerprintDetectRequest,
    organization: Dict = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> FingerprintDetectResponse:
    """
    Detect a fingerprint in text.

    Detection uses score-based matching with confidence threshold
    to identify fingerprinted content even after modifications.

    **Tier Requirement:** Enterprise
    """
    start_time = time.time()
    organization_id = organization["organization_id"]

    # TEAM_145: Fingerprint detection requires Enterprise tier
    tier = organization.get("tier", "free").lower()
    if tier not in {"enterprise", "strategic_partner", "demo"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FEATURE_NOT_AVAILABLE",
                "message": "Robust fingerprinting requires Enterprise tier",
                "required_tier": "enterprise",
                "current_tier": tier,
                "upgrade_url": "/billing/upgrade",
            },
        )

    try:
        detected, matches = await fingerprint_service.detect_fingerprint(
            db=db,
            organization_id=organization_id,
            text=request.text,
            fingerprint_key=request.fingerprint_key,
            confidence_threshold=request.confidence_threshold,
            return_positions=request.return_positions,
        )

        processing_time_ms = (time.time() - start_time) * 1000

        best_match = matches[0] if matches else None

        logger.info(f"Fingerprint detection for org {organization_id}: detected={detected}, matches={len(matches)}, time={processing_time_ms:.2f}ms")

        return FingerprintDetectResponse(
            success=True,
            fingerprint_detected=detected,
            matches=matches,
            best_match=best_match,
            processing_time_ms=round(processing_time_ms, 2),
            message=f"Detection complete: {len(matches)} fingerprint(s) found" if detected else "No fingerprint detected",
        )

    except Exception as e:
        logger.error(f"Failed to detect fingerprint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "FINGERPRINT_DETECT_FAILED", "message": str(e)},
        )
