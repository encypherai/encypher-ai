"""Unified verification service -- routes content to the appropriate
verification backend and maps results to a consistent response envelope.

TEAM_273: Consolidates text, image, audio, and video verification into
a single entry point. Phase 2 adds advanced features (Merkle tamper
detection, attribution, plagiarism, fuzzy search, print fingerprint).
"""

from __future__ import annotations

import asyncio
import difflib
import logging
import time
import unicodedata
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import merkle as merkle_crud
from app.models.content_reference import ContentReference
from app.models.merkle import MerkleRoot
from app.schemas.verify_schemas import (
    ContentInfo,
    SignerInfo,
    UnifiedVerifyResponse,
    VerifyOptions,
)
from app.utils.c2pa_verifier_core import C2paVerificationResult

logger = logging.getLogger(__name__)

# MIME type categories for routing
from app.utils.image_format_registry import SUPPORTED_IMAGE_MIME_TYPES

_IMAGE_MIMES = SUPPORTED_IMAGE_MIME_TYPES | frozenset({"image/bmp"})
_AUDIO_MIMES = frozenset(
    {
        "audio/mpeg",
        "audio/mp3",
        "audio/wav",
        "audio/wave",
        "audio/x-wav",
        "audio/ogg",
        "audio/flac",
        "audio/aac",
        "audio/mp4",
        "audio/x-m4a",
        "audio/webm",
    }
)
_VIDEO_MIMES = frozenset(
    {
        "video/mp4",
        "video/webm",
        "video/ogg",
        "video/quicktime",
        "video/x-msvideo",
        "video/avi",
        "video/msvideo",
        "video/x-matroska",
        "video/mpeg",
    }
)


def classify_mime(mime_type: str) -> str:
    """Map a MIME type to a media category.

    Returns one of: ``"image"``, ``"audio"``, ``"video"``, or ``"unknown"``.
    """
    mime_lower = mime_type.lower().strip()
    if mime_lower in _IMAGE_MIMES or mime_lower.startswith("image/"):
        return "image"
    if mime_lower in _AUDIO_MIMES or mime_lower.startswith("audio/"):
        return "audio"
    if mime_lower in _VIDEO_MIMES or mime_lower.startswith("video/"):
        return "video"
    return "unknown"


# ---------------------------------------------------------------------------
# Helpers ported from routers/verification.py
# ---------------------------------------------------------------------------


def _extract_manifest_metadata(manifest: Any) -> Dict[str, Any]:
    """Extract document/org metadata from a verification manifest."""
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
    """Diff stored vs request leaf hashes and produce localization events."""
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


# ---------------------------------------------------------------------------
# Advanced feature functions
# ---------------------------------------------------------------------------


async def run_merkle_verification(
    text: str,
    segmentation_level: str,
    document_id: Optional[str],
    organization_id: Optional[str],
    content_db: AsyncSession,
) -> Dict[str, Any]:
    """Run Merkle root verification and tamper localization."""
    result: Dict[str, Any] = {}

    if not document_id or not organization_id:
        result["tamper_detection"] = {
            "status": "metadata_missing",
            "segmentation_level": segmentation_level,
        }
        return result

    statement = (
        select(MerkleRoot)
        .where(
            MerkleRoot.document_id == document_id,
            MerkleRoot.organization_id == organization_id,
            MerkleRoot.segmentation_level == segmentation_level,
        )
        .order_by(MerkleRoot.created_at.desc())
        .limit(1)
    )
    merkle_result = await content_db.execute(statement)
    merkle_root = merkle_result.scalar_one_or_none()

    if not merkle_root:
        result["tamper_detection"] = {
            "status": "root_not_found",
            "segmentation_level": segmentation_level,
        }
        return result

    from app.utils.merkle import MerkleTree, compute_leaf_hash
    from app.utils.segmentation import HierarchicalSegmenter

    normalized_text = unicodedata.normalize("NFC", text)
    segmenter = HierarchicalSegmenter(normalized_text, include_words=False)
    try:
        segments = segmenter.get_segments(segmentation_level)
    except ValueError:
        segments = []

    if not segments:
        result["tamper_detection"] = {
            "status": "no_segments",
            "segmentation_level": segmentation_level,
            "segment_count": 0,
        }
        return result

    tree = MerkleTree(segments, segmentation_level=segmentation_level)
    computed_root_hash = tree.root.hash
    root_match = computed_root_hash == merkle_root.root_hash

    result["tamper_detection"] = {
        "status": "computed",
        "segmentation_level": segmentation_level,
        "root_match": root_match,
        "stored_root_hash": merkle_root.root_hash,
        "computed_root_hash": computed_root_hash,
        "segment_count": len(segments),
    }

    # Tamper localization (always computed when root exists)
    root_id = cast(UUID, merkle_root.id)
    stored_subhashes = await merkle_crud.find_subhashes_by_root(
        db=content_db,
        root_id=root_id,
        node_type="leaf",
    )
    stored_subhashes = sorted(stored_subhashes, key=lambda item: item.position_index)
    stored_hashes = [cast(str, subhash.hash_value) for subhash in stored_subhashes]
    request_hashes = [compute_leaf_hash(segment) for segment in segments]

    result["tamper_localization"] = _build_localization_events(
        stored_hashes=stored_hashes,
        request_hashes=request_hashes,
        request_segments=segments,
    )

    return result


async def run_attribution(
    text: str,
    segmentation_level: str,
    db: AsyncSession,
    organization_id: Optional[str] = None,
    search_scope: str = "organization",
) -> Dict[str, Any]:
    """Run source attribution via MerkleService.

    When ``search_scope`` is ``"organization"`` (default), results are filtered
    to the caller's org to prevent cross-tenant data disclosure.  Only
    ``search_scope="all"`` (Enterprise-gated at the endpoint) returns results
    across all organizations.
    """
    from app.services.merkle_service import MerkleService
    from app.utils.merkle import compute_hash
    from app.utils.segmentation.default import normalize_for_hashing

    sources = await MerkleService.find_sources(
        db=db,
        text_segment=text,
        segmentation_level=segmentation_level,
        normalize=True,
    )

    # Scope results to caller's org unless cross-org search is explicitly enabled
    if search_scope != "all" and organization_id:
        sources = [(sub, root) for sub, root in sources if root.organization_id == organization_id]

    normalized = normalize_for_hashing(text, lowercase=True, normalize_unicode_chars=True)
    query_hash = compute_hash(normalized)

    return {
        "query_hash": query_hash,
        "query_preview": text[:200],
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


async def run_plagiarism(
    text: str,
    segmentation_level: str,
    organization_id: str,
    include_heat_map: bool,
    min_match_percentage: float,
    db: AsyncSession,
) -> Dict[str, Any]:
    """Run plagiarism detection via MerkleService."""
    from app.services.merkle_service import MerkleService

    start = time.perf_counter()
    report = await MerkleService.generate_attribution_report(
        db=db,
        organization_id=organization_id,
        target_text=text,
        segmentation_level=segmentation_level,
        target_document_id=None,
        include_heat_map=include_heat_map,
    )
    duration_ms = int((time.perf_counter() - start) * 1000)

    raw_sources = cast(list[Dict[str, Any]], report.source_documents or [])
    source_documents = [doc for doc in raw_sources if doc.get("match_percentage", 0.0) >= min_match_percentage]

    total_segments = report.total_segments
    overall_pct = (report.matched_segments / total_segments) * 100 if total_segments else 0.0

    return {
        "report_id": str(report.id),
        "total_segments": report.total_segments,
        "matched_segments": report.matched_segments,
        "overall_match_percentage": round(overall_pct, 2),
        "source_documents": source_documents,
        "heat_map_data": report.heat_map_data if include_heat_map else None,
        "processing_time_ms": duration_ms,
        "scan_timestamp": report.scan_timestamp,
    }


async def run_fuzzy_search(
    text: str,
    organization_id: str,
    search_scope: str,
    similarity_threshold: float,
    max_candidates: int,
    fallback_when_no_binding: bool,
    embeddings_found: int,
    db: AsyncSession,
) -> Dict[str, Any]:
    """Run fuzzy fingerprint search."""
    if fallback_when_no_binding and embeddings_found:
        return {
            "matches_found": 0,
            "matches": [],
            "processing_time_ms": 0,
            "skipped_reason": "embeddings_found",
        }

    from app.schemas.fuzzy_fingerprint import FuzzySearchConfig
    from app.services.fuzzy_fingerprint_service import fuzzy_fingerprint_service

    config = FuzzySearchConfig(
        enabled=True,
        similarity_threshold=similarity_threshold,
        max_candidates=max_candidates,
        fallback_when_no_binding=fallback_when_no_binding,
    )

    return await fuzzy_fingerprint_service.search(
        db=db,
        organization_id=organization_id,
        text=text,
        config=config,
        search_scope=search_scope,
    )


def run_print_fingerprint(text: str) -> Dict[str, Any]:
    """Decode print fingerprint from text (passive, cheap)."""
    from app.utils.print_stego import decode_print_fingerprint

    fp_bytes = decode_print_fingerprint(text)
    return {
        "detected": fp_bytes is not None,
        "payload_hex": fp_bytes.hex() if fp_bytes is not None else None,
    }


async def resolve_rights(
    document_id: Optional[str],
    content_db: AsyncSession,
) -> Optional[Dict[str, Any]]:
    """Look up rights resolution URL for a document."""
    if not document_id:
        return None

    stmt = (
        select(ContentReference.rights_resolution_url, ContentReference.rights_snapshot).where(ContentReference.document_id == document_id).limit(1)
    )
    result = await content_db.execute(stmt)
    row = result.first()

    if not row or not row.rights_resolution_url:
        return None

    return {
        "resolution_url": row.rights_resolution_url,
        "snapshot": row.rights_snapshot,
    }


# ---------------------------------------------------------------------------
# C2PA result mapping
# ---------------------------------------------------------------------------


def _map_c2pa_result(
    result: C2paVerificationResult,
    media_type: str,
    correlation_id: str,
) -> UnifiedVerifyResponse:
    """Map a C2paVerificationResult to the unified response envelope."""
    signer = None
    if result.signer:
        signer = SignerInfo(
            organization_id=result.signer,
            organization_name=result.signer,
        )

    content = ContentInfo(
        hash_verified=result.hash_matches,
        c2pa_manifest_valid=result.c2pa_manifest_valid,
        c2pa_instance_id=result.c2pa_instance_id,
        manifest_data=result.manifest_data,
    )

    reason_code = "OK" if result.valid else "SIGNATURE_INVALID"
    if result.error:
        reason_code = "VERIFY_EXCEPTION"

    return UnifiedVerifyResponse(
        success=result.error is None,
        valid=result.valid,
        tampered=not result.valid and result.error is None,
        reason_code=reason_code,
        media_type=media_type,
        verified_at=datetime.now(timezone.utc),
        signer=signer,
        content=content,
        error=result.error,
        correlation_id=correlation_id,
    )


# ---------------------------------------------------------------------------
# Main entry points
# ---------------------------------------------------------------------------


async def verify_text(
    text: str,
    *,
    options: VerifyOptions,
    core_db: AsyncSession,
    content_db: Optional[AsyncSession] = None,
    org_id: Optional[str] = None,
    org_context: Optional[Dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
) -> UnifiedVerifyResponse:
    """Run the full text verification cascade and return a unified response.

    Base verification always runs. Advanced features (Merkle tamper detection,
    attribution, plagiarism, fuzzy search, print fingerprint) run based on
    ``options`` flags and available auth context.
    """
    from app.services.verification_logic import (
        build_verdict,
        determine_reason_code,
        execute_verification,
    )

    cid = correlation_id or uuid.uuid4().hex

    execution = await execute_verification(
        payload_text=text,
        db=core_db,
        content_db=content_db,
    )
    reason_code = determine_reason_code(execution=execution)
    verdict = build_verdict(
        execution=execution,
        reason_code=reason_code,
        payload_bytes=len(text.encode("utf-8")),
    )

    signer = None
    if verdict.signer_id:
        cert_status = None
        ca_backed = None
        trust_level = None
        if execution.resolved_cert:
            cert_status = execution.resolved_cert.status.value
            ca_backed = execution.resolved_cert.is_ca_backed if hasattr(execution.resolved_cert, "is_ca_backed") else None
        if execution.trust_status:
            trust_level = execution.trust_status

        signer = SignerInfo(
            organization_id=verdict.signer_id,
            organization_name=verdict.signer_name,
            trust_level=trust_level,
            certificate_status=cert_status,
            ca_backed=ca_backed,
        )

    manifest = verdict.details.get("manifest", {})
    content = ContentInfo(
        manifest_mode=manifest.get("manifest_mode"),
        embeddings_found=verdict.embeddings_found or manifest.get("micro_signatures_found"),
        leaf_hash_verified=manifest.get("leaf_hash_verified"),
        document_id=manifest.get("document_id"),
        manifest_data=manifest.get("manifest_data"),
    )

    details: Dict[str, Any] = {}
    for key in ("duration_ms", "payload_bytes", "rights_signals", "revocation_check", "trust_status", "trust_warning"):
        if key in verdict.details:
            details[key] = verdict.details[key]

    # --- Advanced features (run concurrently where possible) ---

    # Extract document/org metadata for Merkle and rights lookups
    manifest_metadata = _extract_manifest_metadata(execution.manifest)
    document_id = manifest_metadata.get("document_id")
    organization_id = manifest_metadata.get("organization_id") or execution.signer_id
    effective_org_id = org_id or organization_id

    # Print fingerprint detection (sync, cheap -- run before async gather)
    if options.detect_print_fingerprint:
        details["print_fingerprint"] = run_print_fingerprint(text)

    # Build list of async tasks to run concurrently
    async_tasks: Dict[str, Any] = {}

    if content_db and (document_id or organization_id):
        async_tasks["merkle"] = run_merkle_verification(
            text=text,
            segmentation_level=options.segmentation_level,
            document_id=document_id,
            organization_id=organization_id,
            content_db=content_db,
        )

    if options.include_attribution and content_db:
        async_tasks["attribution"] = run_attribution(
            text=text,
            segmentation_level=options.segmentation_level,
            db=content_db,
            organization_id=effective_org_id,
            search_scope=options.search_scope,
        )

    if options.detect_plagiarism and content_db and effective_org_id:
        async_tasks["plagiarism"] = run_plagiarism(
            text=text,
            segmentation_level=options.segmentation_level,
            organization_id=effective_org_id,
            include_heat_map=options.include_heat_map,
            min_match_percentage=options.min_match_percentage,
            db=content_db,
        )

    if options.fuzzy_search and content_db and effective_org_id:
        embeddings_found = content.embeddings_found or 0
        async_tasks["fuzzy_search"] = run_fuzzy_search(
            text=text,
            organization_id=effective_org_id,
            search_scope=options.search_scope,
            similarity_threshold=options.fuzzy_similarity_threshold,
            max_candidates=options.fuzzy_max_candidates,
            fallback_when_no_binding=options.fuzzy_fallback_when_no_binding,
            embeddings_found=embeddings_found,
            db=content_db,
        )

    if content_db and document_id:
        async_tasks["rights"] = resolve_rights(document_id, content_db)

    # Execute all async advanced features concurrently
    if async_tasks:
        task_names = list(async_tasks.keys())
        results = await asyncio.gather(*async_tasks.values(), return_exceptions=True)

        for name, result in zip(task_names, results):
            if isinstance(result, Exception):
                logger.warning("%s failed: %s", name, result)
                if name == "merkle":
                    details["tamper_detection"] = {"status": "error", "error": str(result)}
                elif name == "rights":
                    pass  # Rights failure is silent
                else:
                    details[name] = {"error": str(result)}
            elif name == "merkle":
                details.update(result)
            elif name == "rights":
                if result:
                    details["rights"] = result
            else:
                details[name] = result

    return UnifiedVerifyResponse(
        success=True,
        valid=verdict.valid,
        tampered=verdict.tampered,
        reason_code=verdict.reason_code,
        media_type="text",
        verified_at=datetime.now(timezone.utc),
        signer=signer,
        content=content,
        details=details,
        error=None,
        correlation_id=cid,
    )


def verify_media(
    data: bytes,
    mime_type: str,
    *,
    correlation_id: Optional[str] = None,
) -> UnifiedVerifyResponse:
    """Verify a binary media file (image, audio, or video) via C2PA."""
    cid = correlation_id or uuid.uuid4().hex
    media_type = classify_mime(mime_type)

    if media_type == "image":
        from app.services.image_verification_service import verify_image_c2pa

        result = verify_image_c2pa(data, mime_type)
    elif media_type == "audio":
        from app.services.audio_verification_service import verify_audio_c2pa

        result = verify_audio_c2pa(data, mime_type)
    elif media_type == "video":
        from app.utils.video_utils import SUPPORTED_VIDEO_MIME_TYPES

        if mime_type.lower().strip() not in SUPPORTED_VIDEO_MIME_TYPES:
            return UnifiedVerifyResponse(
                success=True,
                valid=False,
                tampered=False,
                reason_code="FORMAT_NOT_SUPPORTED_FOR_SIGNING",
                media_type="video",
                verified_at=datetime.now(timezone.utc),
                error=(f"Video format {mime_type!r} is not supported for C2PA signing or verification. Supported video formats: MP4, MOV, M4V, AVI."),
                correlation_id=cid,
            )

        from app.services.video_verification_service import verify_video_c2pa

        result = verify_video_c2pa(data, mime_type)
    else:
        return UnifiedVerifyResponse(
            success=False,
            valid=False,
            tampered=False,
            reason_code="UNSUPPORTED_MEDIA_TYPE",
            media_type="unknown",
            verified_at=datetime.now(timezone.utc),
            error=f"Unsupported MIME type: {mime_type}",
            correlation_id=cid,
        )

    return _map_c2pa_result(result, media_type, cid)
