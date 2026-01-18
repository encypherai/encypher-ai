"""
API endpoints for Merkle tree operations.

Enterprise tier endpoints for content attribution and plagiarism detection.
"""

import logging
import time
from typing import Dict

from fastapi import APIRouter, Body, Depends, HTTPException, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_organization
from app.models.merkle import MerkleRoot
from app.schemas.merkle import (
    DocumentEncodeRequest,
    DocumentEncodeResponse,
    ErrorResponse,
    HeatMapData,
    MerkleRootResponse,
    PlagiarismDetectionRequest,
    PlagiarismDetectionResponse,
    SourceAttributionRequest,
    SourceAttributionResponse,
    SourceDocumentMatch,
    SourceMatch,
)
from app.services.fuzzy_fingerprint_service import fuzzy_fingerprint_service
from app.services.merkle_service import MerkleService
from app.utils.quota import QuotaManager, QuotaType

logger = logging.getLogger(__name__)


def require_merkle_feature(organization: dict = Depends(get_current_organization)) -> dict:
    """
    Dependency that requires Professional+ tier.

    Raises HTTPException 403 if the organization doesn't have Professional+ tier.
    """
    tier = (organization.get("tier") or "starter").lower().replace("-", "_")
    allowed_tiers = {"professional", "business", "enterprise", "strategic_partner", "demo"}
    if tier not in allowed_tiers:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FEATURE_NOT_AVAILABLE",
                "message": "Merkle tree features require Professional tier or higher",
                "upgrade_url": "/billing/upgrade",
            },
        )
    return organization


router = APIRouter(prefix="/enterprise/merkle", tags=["Enterprise - Merkle Trees"])


# ============================================================================
# Document Encoding Endpoint
# ============================================================================


@router.post(
    "/encode",
    response_model=DocumentEncodeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Encode Document into Merkle Trees",
    description="""
    Encode a document into Merkle trees at specified segmentation levels.
    
    This endpoint:
    1. Segments the document text at multiple levels (word/sentence/paragraph/section)
    2. Builds Merkle trees for each segmentation level
    3. Stores all tree data in the database for future attribution queries
    4. Returns root hashes and tree metadata
    
    **Enterprise Tier Only** - Requires valid organization with Merkle features enabled.
    
    **Rate Limits:**
    - Free tier: Not available
    - Enterprise tier: 1000 documents/month
    
    **Processing Time:**
    - Small documents (<1000 words): ~100-200ms
    - Medium documents (1000-10000 words): ~500ms-2s
    - Large documents (>10000 words): ~2-10s
    """,
    responses={
        201: {"description": "Document encoded successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Quota exceeded or feature not enabled"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
)
async def encode_document(
    request: DocumentEncodeRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
    organization: dict = Depends(require_merkle_feature),
) -> DocumentEncodeResponse:
    """
    Encode a document into Merkle trees.

    Args:
        request: Document encoding request
        db: Database session
        organization: Authenticated organization with merkle feature

    Returns:
        DocumentEncodeResponse with root hashes and metadata

    Raises:
        HTTPException: If encoding fails
    """
    start_time = time.time()
    organization_id = organization["organization_id"]

    # Check and increment quota (1 per document, regardless of size)
    await QuotaManager.check_quota(
        db=db,
        organization_id=organization_id,
        quota_type=QuotaType.MERKLE_ENCODING,
        increment=1,  # Per document, not per sentence
        features=organization.get("features", {}),
    )

    try:
        logger.info(f"Encoding document {request.document_id} for org {organization_id} at levels: {request.segmentation_levels}")

        # Encode the document
        roots: Dict[str, MerkleRoot] = await MerkleService.encode_document(
            db=db,
            organization_id=organization_id,
            document_id=request.document_id,
            text=request.text,
            segmentation_levels=request.segmentation_levels,
            metadata=request.metadata,
            include_words=request.include_words,
        )

        fuzzy_index_summary = None
        if request.fuzzy_fingerprint and request.fuzzy_fingerprint.enabled:
            if not organization.get("fuzzy_fingerprint_enabled", False):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "code": "FEATURE_NOT_AVAILABLE",
                        "message": "Fuzzy fingerprint indexing requires Enterprise tier",
                        "required_tier": "enterprise",
                    },
                )

            await QuotaManager.check_quota(
                db=db,
                organization_id=organization_id,
                quota_type=QuotaType.FUZZY_INDEX,
                increment=1,
                features=organization.get("features", {}),
            )

            fuzzy_index_summary = await fuzzy_fingerprint_service.index_document(
                db=db,
                organization_id=organization_id,
                document_id=request.document_id,
                text=request.text,
                config=request.fuzzy_fingerprint,
                merkle_roots=roots,
            )

        # Convert to response format
        roots_response = {}
        total_segments = {}

        for level, root in roots.items():
            roots_response[level] = MerkleRootResponse(
                root_id=str(root.id),  # Use 'id' and convert UUID to string
                document_id=root.document_id,
                root_hash=root.root_hash,
                tree_depth=root.tree_depth,
                total_leaves=root.leaf_count,
                segmentation_level=root.segmentation_level,
                created_at=root.created_at,
                metadata=root.doc_metadata,
            )
            total_segments[level] = root.leaf_count

        processing_time_ms = (time.time() - start_time) * 1000

        logger.info(f"Successfully encoded document {request.document_id} in {processing_time_ms:.2f}ms")

        # Add quota usage headers
        quota_headers = await QuotaManager.get_quota_headers(
            db=db,
            organization_id=organization_id,
            quota_type=QuotaType.MERKLE_ENCODING,
        )
        for header, value in quota_headers.items():
            response.headers[header] = value

        return DocumentEncodeResponse(
            success=True,
            message="Document encoded successfully",
            document_id=request.document_id,
            organization_id=organization_id,
            roots=roots_response,
            total_segments=total_segments,
            processing_time_ms=processing_time_ms,
            fuzzy_index=fuzzy_index_summary,
        )

    except ValueError as e:
        logger.error(f"Validation error encoding document: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error encoding document {request.document_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to encode document")


# ============================================================================
# Source Attribution Endpoint
# ============================================================================


@router.post(
    "/attribute",
    include_in_schema=False,
)
async def find_sources_deprecated(
    _payload: dict = Body(...),
    _db: AsyncSession = Depends(get_db),
    _organization: dict = Depends(require_merkle_feature),
) -> JSONResponse:
    return JSONResponse(
        status_code=410,
        content={
            "success": False,
            "error": {
                "code": "ENDPOINT_DEPRECATED",
                "message": "This endpoint has been consolidated into POST /api/v1/verify/advanced.",
                "hint": "Use POST /api/v1/verify/advanced with include_attribution=true.",
            },
        },
    )


# ============================================================================
# Plagiarism Detection Endpoint
# ============================================================================


@router.post(
    "/detect-plagiarism",
    include_in_schema=False,
)
async def detect_plagiarism_deprecated(
    _payload: dict = Body(...),
    _db: AsyncSession = Depends(get_db),
    _organization: dict = Depends(require_merkle_feature),
) -> JSONResponse:
    return JSONResponse(
        status_code=410,
        content={
            "success": False,
            "error": {
                "code": "ENDPOINT_DEPRECATED",
                "message": "This endpoint has been consolidated into POST /api/v1/verify/advanced.",
                "hint": "Use POST /api/v1/verify/advanced with detect_plagiarism=true.",
            },
        },
    )
