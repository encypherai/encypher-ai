"""
API endpoints for Merkle tree operations.

Enterprise tier endpoints for content attribution and plagiarism detection.
"""
import time
import logging
from typing import Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.merkle import (
    DocumentEncodeRequest,
    DocumentEncodeResponse,
    MerkleRootResponse,
    SourceAttributionRequest,
    SourceAttributionResponse,
    SourceMatch,
    PlagiarismDetectionRequest,
    PlagiarismDetectionResponse,
    SourceDocumentMatch,
    HeatMapData,
    ErrorResponse
)
from app.services.merkle_service import MerkleService
from app.models.merkle import MerkleRoot

logger = logging.getLogger(__name__)

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
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def encode_document(
    request: DocumentEncodeRequest,
    db: AsyncSession = Depends(get_db),
    # TODO: Add authentication dependency
    # current_org: Organization = Depends(get_current_organization)
) -> DocumentEncodeResponse:
    """
    Encode a document into Merkle trees.
    
    Args:
        request: Document encoding request
        db: Database session
    
    Returns:
        DocumentEncodeResponse with root hashes and metadata
    
    Raises:
        HTTPException: If encoding fails
    """
    start_time = time.time()
    
    # TODO: Replace with actual organization from auth
    organization_id = "org_demo"
    
    try:
        logger.info(
            f"Encoding document {request.document_id} for org {organization_id} "
            f"at levels: {request.segmentation_levels}"
        )
        
        # TODO: Check organization tier and quota
        # if not current_org.merkle_enabled:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Merkle tree features not enabled for this organization"
        #     )
        
        # TODO: Check and update quota
        # if current_org.merkle_calls_this_month >= current_org.monthly_merkle_quota:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Monthly Merkle tree quota exceeded"
        #     )
        
        # Encode the document
        roots: Dict[str, MerkleRoot] = await MerkleService.encode_document(
            db=db,
            organization_id=organization_id,
            document_id=request.document_id,
            text=request.text,
            segmentation_levels=request.segmentation_levels,
            metadata=request.metadata,
            include_words=request.include_words
        )
        
        # Convert to response format
        roots_response = {}
        total_segments = {}
        
        for level, root in roots.items():
            roots_response[level] = MerkleRootResponse(
                root_id=root.root_id,
                document_id=root.document_id,
                root_hash=root.root_hash,
                tree_depth=root.tree_depth,
                total_leaves=root.total_leaves,
                segmentation_level=root.segmentation_level,
                created_at=root.created_at,
                metadata=root.doc_metadata
            )
            total_segments[level] = root.total_leaves
        
        processing_time_ms = (time.time() - start_time) * 1000
        
        logger.info(
            f"Successfully encoded document {request.document_id} in {processing_time_ms:.2f}ms"
        )
        
        return DocumentEncodeResponse(
            success=True,
            message="Document encoded successfully",
            document_id=request.document_id,
            organization_id=organization_id,
            roots=roots_response,
            total_segments=total_segments,
            processing_time_ms=processing_time_ms
        )
        
    except ValueError as e:
        logger.error(f"Validation error encoding document: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error encoding document {request.document_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to encode document"
        )


# ============================================================================
# Source Attribution Endpoint
# ============================================================================

@router.post(
    "/attribute",
    response_model=SourceAttributionResponse,
    summary="Find Source Documents",
    description="""
    Find source documents that contain a specific text segment.
    
    This endpoint searches the Merkle tree index to find which documents
    contain the provided text segment.
    
    **Use Cases:**
    - Verify if a text segment appears in your document repository
    - Find the original source of a quote or passage
    - Check if content has been previously published
    
    **Enterprise Tier Only**
    """,
    responses={
        200: {"description": "Search completed successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def find_sources(
    request: SourceAttributionRequest,
    db: AsyncSession = Depends(get_db)
) -> SourceAttributionResponse:
    """
    Find source documents containing a text segment.
    
    Args:
        request: Source attribution request
        db: Database session
    
    Returns:
        SourceAttributionResponse with matching sources
    """
    start_time = time.time()
    
    try:
        # Find matching sources
        sources = await MerkleService.find_sources(
            db=db,
            text_segment=request.text_segment,
            segmentation_level=request.segmentation_level,
            normalize=request.normalize
        )
        
        # Convert to response format
        from app.utils.merkle import compute_hash, normalize_for_hashing
        
        if request.normalize:
            normalized = normalize_for_hashing(
                request.text_segment,
                lowercase=True,
                normalize_unicode_chars=True
            )
            query_hash = compute_hash(normalized)
        else:
            query_hash = compute_hash(request.text_segment)
        
        source_matches = []
        for subhash, root in sources:
            match = SourceMatch(
                document_id=root.document_id,
                organization_id=root.organization_id,
                root_hash=root.root_hash,
                segmentation_level=root.segmentation_level,
                matched_hash=subhash.hash_value,
                text_content=subhash.text_content if subhash.text_content else None,
                confidence=1.0  # Exact hash match = 100% confidence
            )
            source_matches.append(match)
        
        processing_time_ms = (time.time() - start_time) * 1000
        
        return SourceAttributionResponse(
            success=True,
            query_hash=query_hash,
            matches_found=len(source_matches),
            sources=source_matches,
            processing_time_ms=processing_time_ms
        )
        
    except Exception as e:
        logger.error(f"Error finding sources: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to find sources"
        )


# ============================================================================
# Plagiarism Detection Endpoint
# ============================================================================

@router.post(
    "/detect-plagiarism",
    response_model=PlagiarismDetectionResponse,
    summary="Detect Plagiarism",
    description="""
    Analyze text for potential plagiarism by comparing against indexed documents.
    
    This endpoint:
    1. Segments the target text
    2. Checks each segment against the Merkle tree index
    3. Identifies matching source documents
    4. Calculates match percentages and confidence scores
    5. Generates a heat map showing which parts match
    
    **Use Cases:**
    - Academic plagiarism detection
    - Content originality verification
    - Copyright infringement detection
    - Duplicate content identification
    
    **Enterprise Tier Only**
    """,
    responses={
        200: {"description": "Analysis completed successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def detect_plagiarism(
    request: PlagiarismDetectionRequest,
    db: AsyncSession = Depends(get_db)
) -> PlagiarismDetectionResponse:
    """
    Detect plagiarism in target text.
    
    Args:
        request: Plagiarism detection request
        db: Database session
    
    Returns:
        PlagiarismDetectionResponse with analysis results
    """
    start_time = time.time()
    
    # TODO: Replace with actual organization from auth
    organization_id = "org_demo"
    
    try:
        # Generate attribution report
        report = await MerkleService.generate_attribution_report(
            db=db,
            organization_id=organization_id,
            target_text=request.target_text,
            segmentation_level=request.segmentation_level,
            target_document_id=request.target_document_id,
            include_heat_map=request.include_heat_map
        )
        
        # Filter sources by minimum match percentage
        filtered_sources = [
            SourceDocumentMatch(
                document_id=doc['document_id'],
                organization_id=doc['organization_id'],
                segmentation_level=doc['segmentation_level'],
                matched_segments=doc['matched_segments'],
                total_leaves=doc['total_leaves'],
                match_percentage=doc['match_percentage'],
                confidence_score=doc['confidence_score'],
                doc_metadata=doc.get('doc_metadata')
            )
            for doc in report.source_documents
            if doc['match_percentage'] >= request.min_match_percentage
        ]
        
        # Convert heat map data
        heat_map = None
        if report.heat_map_data:
            heat_map = HeatMapData(
                positions=report.heat_map_data['positions'],
                total_segments=report.heat_map_data['total_segments'],
                matched_segments=report.heat_map_data['matched_segments'],
                match_percentage=report.heat_map_data['match_percentage']
            )
        
        processing_time_ms = (time.time() - start_time) * 1000
        
        overall_match_pct = (
            (report.matched_segments / report.total_segments) * 100
            if report.total_segments > 0 else 0
        )
        
        return PlagiarismDetectionResponse(
            success=True,
            report_id=report.report_id,
            target_document_id=report.target_document_id,
            total_segments=report.total_segments,
            matched_segments=report.matched_segments,
            overall_match_percentage=round(overall_match_pct, 2),
            source_documents=filtered_sources,
            heat_map_data=heat_map,
            processing_time_ms=processing_time_ms,
            scan_timestamp=report.scan_timestamp
        )
        
    except Exception as e:
        logger.error(f"Error detecting plagiarism: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to detect plagiarism"
        )
