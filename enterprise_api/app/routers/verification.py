"""
Verification router for C2PA manifest verification.

Provides both HTML-friendly verification pages and JSON APIs used by SDKs.
"""

import difflib
import time
import unicodedata
from typing import Any, Dict, List, Optional, cast

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID, uuid4

from app.crud import merkle as merkle_crud
from app.database import get_content_db, get_db
from app.dependencies import get_current_organization_dep
from app.models.merkle import MerkleRoot
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



@router.post(
    "/verify/advanced",
    summary="Advanced verification",
    description="""
Verify signed content and optionally run attribution, plagiarism detection, and fuzzy fingerprint search.

Requires an authenticated API key with verify permission.

---

## Request Fields

| Field | Type | Default | Values | Tier | Description |
|-------|------|---------|--------|------|-------------|
| `text` | string | *(required)* | any (min 1 char) | Free | The text to verify. Should contain invisible C2PA embeddings from a prior `/sign` call. |
| `segmentation_level` | string | `"sentence"` | `document`, `sentence`, `paragraph`, `section` | Free | Granularity used for tamper detection. Should match the level used during signing. |
| `search_scope` | string | `"organization"` | `organization`, `public`, `all` | `all` requires Enterprise | Scope for attribution / plagiarism lookups. `organization` = only your org's documents. `public` = publicly indexed docs. `all` = cross-organization (Enterprise only). |
| `include_attribution` | bool | `false` | | Free | Run attribution analysis — find source documents that match segments of the submitted text. |
| `detect_plagiarism` | bool | `false` | | Free | Run plagiarism detection — generate a full plagiarism report with match percentages per source. |
| `include_heat_map` | bool | `false` | | Free | Include a segment-level heat map in the plagiarism report (only used when `detect_plagiarism` is `true`). |
| `min_match_percentage` | float | `0.0` | 0.0 – 100.0 | Free | Minimum match percentage to include a source in the plagiarism report. |
| `fuzzy_search` | object | *null* | see below | Enterprise | Optional fuzzy fingerprint search configuration. |

### `fuzzy_search` Object (Enterprise)

| Field | Type | Default | Values | Description |
|-------|------|---------|--------|-------------|
| `enabled` | bool | `false` | | Whether to run fuzzy fingerprint search. |
| `algorithm` | string | `"simhash"` | `simhash` | Fingerprint algorithm. |
| `levels` | string[] | `["sentence", "paragraph"]` | `sentence`, `paragraph`, `document` | Segmentation levels to search. |
| `similarity_threshold` | float | `0.82` | 0.0 – 1.0 | Minimum similarity score for a match. |
| `max_candidates` | int | `20` | 1 – 200 | Maximum number of candidate matches to return. |
| `include_merkle_proof` | bool | `true` | | Whether to include Merkle proofs for matches. |
| `fallback_when_no_binding` | bool | `true` | | Only run fuzzy search when no embeddings are found in the text. |

---

## Response

The response always includes:

- **`data`** — Verification verdict with `is_signed`, `reason_code`, `embeddings_found`, etc.
- **`tamper_detection`** — Merkle root comparison at the requested segmentation level.
- **`tamper_localization`** — Per-segment diff showing changed / inserted / deleted segments (when Merkle root exists).

Conditionally included based on request flags:

- **`attribution`** — List of source document matches with `document_id`, `organization_id`, `confidence`.
- **`plagiarism`** — Full plagiarism report with `overall_match_percentage`, `source_documents`, optional `heat_map_data`.
- **`fuzzy_search`** — Fuzzy fingerprint matches with similarity scores.

---

## Examples

**Basic verification:**
```json
{
    "text": "Signed content with invisible C2PA embeddings..."
}
```

**Verification with attribution and plagiarism:**
```json
{
    "text": "Content to check...",
    "segmentation_level": "sentence",
    "include_attribution": true,
    "detect_plagiarism": true,
    "include_heat_map": true,
    "min_match_percentage": 10.0
}
```

**Verification with fuzzy search (Enterprise):**
```json
{
    "text": "Content that may have been modified...",
    "fuzzy_search": {
        "enabled": true,
        "similarity_threshold": 0.75,
        "max_candidates": 50,
        "fallback_when_no_binding": false
    }
}
```
""",
)
async def verify_advanced(
    request: VerifyAdvancedRequest,
    organization: dict = Depends(get_current_organization_dep),
    db: AsyncSession = Depends(get_db),
    content_db: AsyncSession = Depends(get_content_db),
):
    # TEAM_166: All verification features available to free tier.
    # Only cross-org search (scope="all") and fuzzy fingerprint require enterprise.
    tier = (organization.get("tier") or "free").lower().replace("-", "_")
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
    execution = await verification_logic.execute_verification(payload_text=request.text, db=db, content_db=content_db)
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
        # TEAM_145: Attribution is available to all tiers (free/enterprise/strategic_partner)
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
        # TEAM_145: Plagiarism detection is available to all tiers
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

    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(response_payload))


