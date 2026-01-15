"""
Verification router for C2PA manifest verification.

Provides both HTML-friendly verification pages and JSON APIs used by SDKs.
"""
import time
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from app.database import get_db
from app.dependencies import get_current_organization_dep
from app.models.request_models import VerifyRequest
from app.services.merkle_service import MerkleService
from app.services import verification_logic
from app.utils.quota import QuotaManager, QuotaType

router = APIRouter()


class VerifyAdvancedRequest(BaseModel):
    text: str = Field(..., min_length=1)
    include_attribution: bool = Field(default=False)
    detect_plagiarism: bool = Field(default=False)
    include_heat_map: bool = Field(default=False)
    min_match_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    segmentation_level: str = Field(default="sentence")
    search_scope: str = Field(default="organization")


@router.get("/verify/{document_id}", include_in_schema=False)
async def verify_by_document_id_deprecated(document_id: str):
    return JSONResponse(
        status_code=410,
        content={
            "success": False,
            "error": {
                "code": "ENDPOINT_DEPRECATED",
                "message": "This endpoint has been moved to the verification-service for independent scaling.",
                "hint": f"Use GET https://api.encypherai.com/api/v1/verify/{document_id} instead.",
            },
        },
    )


@router.post(
    "/verify/advanced",
    summary="Advanced verification",
    description="Verify signed content and optionally run attribution/plagiarism analysis.",
)
async def verify_advanced(
    request: VerifyAdvancedRequest,
    organization: dict = Depends(get_current_organization_dep),
    db: AsyncSession = Depends(get_db),
):
    tier = (organization.get("tier") or "starter").lower().replace("-", "_")
    tier_levels = {"starter": 0, "professional": 1, "business": 2, "enterprise": 3, "strategic_partner": 3, "demo": 3}
    org_tier_level = tier_levels.get(tier, 0)
    if not organization.get("can_verify", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your API key does not have permission to verify content",
        )

    scope = (request.search_scope or "organization").strip().lower()
    if scope not in {"organization", "public", "all"}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="search_scope must be one of: organization, public, all",
        )
    if scope == "all" and tier not in {"enterprise", "strategic_partner", "demo"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FEATURE_NOT_AVAILABLE",
                "message": "Cross-organization search requires Enterprise tier",
                "required_tier": "enterprise",
            },
        )

    correlation_id = f"req-{uuid4().hex}"
    execution = await verification_logic.execute_verification(payload_text=request.text, db=db)
    reason_code = verification_logic.determine_reason_code(execution=execution)
    verdict = verification_logic.build_verdict(
        execution=execution,
        reason_code=reason_code,
        payload_bytes=len(request.text.encode("utf-8")),
    )

    response_payload: Dict[str, Any] = {
        "success": True,
        "data": verdict.model_dump() if hasattr(verdict, "model_dump") else verdict.dict(),
        "error": None,
        "correlation_id": correlation_id,
    }

    if request.include_attribution:
        if org_tier_level < 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FEATURE_NOT_AVAILABLE",
                    "message": "Attribution lookup requires Professional tier or higher",
                    "required_tier": "professional",
                },
            )
        await QuotaManager.check_quota(
            db=db,
            organization_id=organization["organization_id"],
            quota_type=QuotaType.MERKLE_ATTRIBUTION,
            increment=1,
            features=organization.get("features", {}),
        )

        sources = await MerkleService.find_sources(
            db=db,
            text_segment=request.text,
            segmentation_level=request.segmentation_level,
            normalize=True,
        )

        from app.utils.merkle import compute_hash, normalize_for_hashing

        normalized = normalize_for_hashing(
            request.text,
            lowercase=True,
            normalize_unicode_chars=True,
        )
        query_hash = compute_hash(normalized)

        response_payload["attribution"] = {
            "query_hash": query_hash,
            "matches_found": len(sources),
            "sources": [
                {
                    "document_id": root.document_id,
                    "organization_id": root.organization_id,
                    "root_hash": root.root_hash,
                    "segmentation_level": root.segmentation_level,
                    "matched_hash": subhash.hash_value,
                    "text_content": getattr(subhash, "text_content", None),
                    "confidence": 1.0,
                }
                for subhash, root in sources
            ],
        }

    if request.detect_plagiarism:
        if org_tier_level < 2:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FEATURE_NOT_AVAILABLE",
                    "message": "Plagiarism detection requires Business tier or higher",
                    "required_tier": "business",
                },
            )
        await QuotaManager.check_quota(
            db=db,
            organization_id=organization["organization_id"],
            quota_type=QuotaType.MERKLE_PLAGIARISM,
            increment=1,
            features=organization.get("features", {}),
        )

        start = time.perf_counter()
        report = await MerkleService.generate_attribution_report(
            db=db,
            organization_id=organization["organization_id"],
            target_text=request.text,
            segmentation_level=request.segmentation_level,
            target_document_id=None,
            include_heat_map=request.include_heat_map,
        )
        duration_ms = int((time.perf_counter() - start) * 1000)

        source_documents = [
            doc
            for doc in (report.source_documents or [])
            if doc.get("match_percentage", 0.0) >= request.min_match_percentage
        ]

        overall_pct = (
            (report.matched_segments / report.total_segments) * 100
            if getattr(report, "total_segments", 0) else 0.0
        )

        response_payload["plagiarism"] = {
            "report_id": str(report.id),
            "total_segments": report.total_segments,
            "matched_segments": report.matched_segments,
            "overall_match_percentage": round(overall_pct, 2),
            "source_documents": source_documents,
            "heat_map_data": report.heat_map_data if request.include_heat_map else None,
            "processing_time_ms": duration_ms,
            "scan_timestamp": getattr(report, "scan_timestamp", None),
        }

    return JSONResponse(status_code=status.HTTP_200_OK, content=response_payload)


@router.post("/verify", include_in_schema=False)
async def verify_content_deprecated(verify_request: VerifyRequest):
    _ = verify_request
    return JSONResponse(
        status_code=410,
        content={
            "success": False,
            "error": {
                "code": "ENDPOINT_DEPRECATED",
                "message": "This endpoint has been moved to the verification-service for independent scaling.",
                "hint": "Use POST https://api.encypherai.com/api/v1/verify with the same request body.",
            },
        },
    )
