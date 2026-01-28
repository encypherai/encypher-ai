"""
Verification router for C2PA manifest verification.

Provides both HTML-friendly verification pages and JSON APIs used by SDKs.
"""

import difflib
import time
import unicodedata
from typing import Any, Dict, List, Optional, cast

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID, uuid4

from app.crud import merkle as merkle_crud
from app.database import get_content_db, get_db
from app.dependencies import get_current_organization_dep
from app.models.merkle import MerkleRoot
from app.models.request_models import VerifyRequest
from app.schemas.fuzzy_fingerprint import FuzzySearchConfig
from app.services import verification_logic
from app.services.fuzzy_fingerprint_service import fuzzy_fingerprint_service
from app.services.merkle_service import MerkleService
from app.utils.merkle import MerkleTree, compute_leaf_hash
from app.utils.segmentation import HierarchicalSegmenter
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
    fuzzy_search: Optional[FuzzySearchConfig] = Field(default=None)


def _extract_manifest_metadata(manifest: Dict[str, Any]) -> Dict[str, Any]:
    metadata: Dict[str, Any] = {}
    if not isinstance(manifest, dict):
        return metadata

    def _merge(payload: Any) -> None:
        if isinstance(payload, dict):
            metadata.update(payload)

    _merge(manifest.get("custom_metadata"))
    nested_manifest = manifest.get("manifest")
    if isinstance(nested_manifest, dict):
        _merge(nested_manifest.get("custom_metadata"))

    assertions = manifest.get("assertions", [])
    if isinstance(assertions, list):
        for assertion in assertions:
            if not isinstance(assertion, dict):
                continue
            if assertion.get("label") == "org.encypher.metadata":
                _merge(assertion.get("data"))

    return metadata


def _build_localization_events(
    *,
    stored_hashes: List[str],
    request_hashes: List[str],
    request_segments: List[str],
) -> Dict[str, Any]:
    matcher = difflib.SequenceMatcher(a=stored_hashes, b=request_hashes, autojunk=False)
    events: List[Dict[str, Any]] = []
    counts = {"changed": 0, "inserted": 0, "deleted": 0}

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        if tag == "replace":
            event_type = "changed"
            counts["changed"] += max(j2 - j1, i2 - i1)
        elif tag == "insert":
            event_type = "inserted"
            counts["inserted"] += j2 - j1
        else:
            event_type = "deleted"
            counts["deleted"] += i2 - i1

        events.append(
            {
                "type": event_type,
                "stored_range": [i1, i2],
                "request_range": [j1, j2],
                "request_previews": [segment[:200] for segment in request_segments[j1:j2]] if j2 > j1 else [],
            }
        )

    return {"events": events, "counts": counts}


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
    content_db: AsyncSession = Depends(get_content_db),
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

    manifest_metadata = _extract_manifest_metadata(execution.manifest)
    document_id = manifest_metadata.get("document_id")
    organization_id = manifest_metadata.get("organization_id") or execution.signer_id

    tamper_detection: Optional[Dict[str, Any]] = None
    tamper_localization: Optional[Dict[str, Any]] = None

    if document_id and organization_id:
        statement = (
            select(MerkleRoot)
            .where(
                MerkleRoot.document_id == document_id,
                MerkleRoot.organization_id == organization_id,
                MerkleRoot.segmentation_level == request.segmentation_level,
            )
            .order_by(MerkleRoot.created_at.desc())
            .limit(1)
        )
        merkle_result = await content_db.execute(statement)
        merkle_root = merkle_result.scalar_one_or_none()

        if merkle_root:
            normalized_text = unicodedata.normalize("NFC", request.text)
            segmenter = HierarchicalSegmenter(normalized_text, include_words=False)
            try:
                segments = segmenter.get_segments(request.segmentation_level)
            except ValueError:
                segments = []

            if segments:
                tree = MerkleTree(segments, segmentation_level=request.segmentation_level)
                computed_root_hash = tree.root.hash
                root_match = computed_root_hash == merkle_root.root_hash

                tamper_detection = {
                    "status": "computed",
                    "segmentation_level": request.segmentation_level,
                    "root_match": root_match,
                    "stored_root_hash": merkle_root.root_hash,
                    "computed_root_hash": computed_root_hash,
                    "segment_count": len(segments),
                }

                root_id = cast(UUID, merkle_root.id)
                stored_subhashes = await merkle_crud.find_subhashes_by_root(
                    db=content_db,
                    root_id=root_id,
                    node_type="leaf",
                )
                stored_subhashes = sorted(stored_subhashes, key=lambda item: item.position_index)
                stored_hashes = [cast(str, subhash.hash_value) for subhash in stored_subhashes]
                request_hashes = [compute_leaf_hash(segment) for segment in segments]

                tamper_localization = _build_localization_events(
                    stored_hashes=stored_hashes,
                    request_hashes=request_hashes,
                    request_segments=segments,
                )
            else:
                tamper_detection = {
                    "status": "no_segments",
                    "segmentation_level": request.segmentation_level,
                    "segment_count": 0,
                }
        else:
            tamper_detection = {
                "status": "root_not_found",
                "segmentation_level": request.segmentation_level,
            }
    else:
        tamper_detection = {
            "status": "metadata_missing",
            "segmentation_level": request.segmentation_level,
        }

    response_payload["tamper_detection"] = tamper_detection
    if tamper_localization is not None:
        response_payload["tamper_localization"] = tamper_localization

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

        from app.utils.merkle import compute_hash
        from app.utils.segmentation.default import normalize_for_hashing

        normalized = normalize_for_hashing(
            request.text,
            lowercase=True,
            normalize_unicode_chars=True,
        )
        query_hash = compute_hash(normalized)

        response_payload["attribution"] = {
            "query_hash": query_hash,
            "query_preview": request.text[:200],
            "matches_found": len(sources),
            "sources": [
                {
                    "document_id": root.document_id,
                    "organization_id": root.organization_id,
                    "root_hash": root.root_hash,
                    "segmentation_level": root.segmentation_level,
                    "matched_hash": subhash.hash_value,
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

        raw_sources = cast(list[Dict[str, Any]], report.source_documents or [])
        source_documents = [doc for doc in raw_sources if doc.get("match_percentage", 0.0) >= request.min_match_percentage]

        overall_pct = (report.matched_segments / report.total_segments) * 100 if getattr(report, "total_segments", 0) else 0.0

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

    fuzzy_config = request.fuzzy_search
    if fuzzy_config and fuzzy_config.enabled:
        if not organization.get("fuzzy_fingerprint_enabled", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FEATURE_NOT_AVAILABLE",
                    "message": "Fuzzy fingerprint search requires Enterprise tier",
                    "required_tier": "enterprise",
                },
            )

        if fuzzy_config.fallback_when_no_binding and verdict.embeddings_found:
            response_payload["fuzzy_search"] = {
                "matches_found": 0,
                "matches": [],
                "processing_time_ms": 0,
                "skipped_reason": "embeddings_found",
            }
        else:
            await QuotaManager.check_quota(
                db=db,
                organization_id=organization["organization_id"],
                quota_type=QuotaType.FUZZY_SEARCH,
                increment=1,
                features=organization.get("features", {}),
            )
            response_payload["fuzzy_search"] = await fuzzy_fingerprint_service.search(
                db=db,
                organization_id=organization["organization_id"],
                text=request.text,
                config=fuzzy_config,
                search_scope=scope,
            )
        response_payload["soft_match"] = response_payload["fuzzy_search"]

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
