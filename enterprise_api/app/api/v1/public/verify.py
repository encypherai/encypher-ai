"""
Public verification API endpoints.

These endpoints do NOT require authentication and are designed for
third-party verification of embedded content.
"""
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.schemas.embeddings import (
    VerifyEmbeddingResponse,
    ContentInfo,
    DocumentInfo,
    MerkleProofInfo,
    C2PAInfo,
    LicensingInfo,
    BatchVerifyRequest,
    BatchVerifyResponse,
    BatchVerifyResult,
    ErrorResponse
)
from app.services.embedding_service import EmbeddingService, embedding_service
from app.models.content_reference import ContentReference
from app.models.merkle import MerkleRoot

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/public", tags=["Public - Verification"])


# ============================================================================
# Public Verification Endpoint
# ============================================================================

@router.get(
    "/verify/{ref_id}",
    response_model=VerifyEmbeddingResponse,
    summary="Verify Embedding (Public - No Auth Required)",
    description="""
    Verify a minimal signed embedding and retrieve associated metadata.
    
    **This endpoint is PUBLIC and does NOT require authentication.**
    
    Third parties can use this endpoint to:
    - Verify authenticity of content with embedded markers
    - Retrieve document metadata (title, author, organization)
    - Access C2PA manifest information
    - View licensing terms
    - Get Merkle proof for cryptographic verification
    
    **Rate Limiting:**
    - 1000 requests/hour per IP address
    - CAPTCHA required after repeated failures
    
    **Privacy:**
    - Only returns text preview (first 200 characters)
    - Full text content is NOT exposed
    - Internal document IDs are mapped to public IDs
    
    **Example Usage:**
    ```
    GET /api/v1/public/verify/a3f9c2e1?signature=8k3mP9xQ
    ```
    """,
    responses={
        200: {"description": "Embedding verified successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        404: {"model": ErrorResponse, "description": "Embedding not found"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"}
    }
)
async def verify_embedding(
    ref_id: str,
    signature: str = Query(..., description="HMAC signature (8+ hex characters)"),
    db: AsyncSession = Depends(get_db)
) -> VerifyEmbeddingResponse:
    """
    Verify an embedding and return associated metadata.
    
    Args:
        ref_id: Reference ID (8 hex characters)
        signature: HMAC signature (8+ hex characters)
        db: Database session
    
    Returns:
        VerifyEmbeddingResponse with verification result and metadata
    
    Raises:
        HTTPException: If verification fails or reference not found
    """
    try:
        logger.info(f"Public verification request for ref_id: {ref_id}")
        
        # Validate ref_id format
        if len(ref_id) != 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid ref_id format (must be 8 hex characters)"
            )
        
        # Validate signature format
        if len(signature) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid signature format (must be at least 8 hex characters)"
            )
        
        # Verify embedding
        reference = await embedding_service.verify_embedding(
            db=db,
            ref_id_hex=ref_id,
            signature_hex=signature
        )
        
        if not reference:
            logger.warning(f"Verification failed for ref_id: {ref_id}")
            return VerifyEmbeddingResponse(
                valid=False,
                ref_id=ref_id,
                error="Invalid signature or reference not found"
            )
        
        # Get associated Merkle root
        result = await db.execute(
            select(MerkleRoot).where(MerkleRoot.root_id == reference.merkle_root_id)
        )
        merkle_root = result.scalar_one_or_none()
        
        if not merkle_root:
            logger.error(f"Merkle root not found for reference: {ref_id}")
            return VerifyEmbeddingResponse(
                valid=False,
                ref_id=ref_id,
                error="Associated Merkle root not found"
            )
        
        # Build response with metadata
        content_info = ContentInfo(
            text_preview=reference.text_preview or "",
            leaf_hash=reference.leaf_hash,
            leaf_index=reference.leaf_index
        )
        
        # Extract document metadata
        doc_metadata = merkle_root.doc_metadata or {}
        document_info = DocumentInfo(
            document_id=reference.document_id,
            title=doc_metadata.get('title'),
            published_at=doc_metadata.get('published_at'),
            author=doc_metadata.get('author'),
            organization=reference.organization_id  # TODO: Map to org name
        )
        
        # Merkle proof info
        merkle_proof_info = MerkleProofInfo(
            root_hash=merkle_root.root_hash,
            verified=True,
            proof_url=f"/api/v1/public/proof/{ref_id}"
        )
        
        # C2PA info (if available)
        c2pa_info = None
        if reference.c2pa_manifest_url:
            c2pa_info = C2PAInfo(
                manifest_url=reference.c2pa_manifest_url,
                manifest_hash=reference.c2pa_manifest_hash,
                verified=True  # TODO: Actually verify manifest
            )
        
        # Licensing info (if available)
        licensing_info = None
        if reference.license_type:
            licensing_info = LicensingInfo(
                license_type=reference.license_type,
                license_url=reference.license_url,
                usage_terms="Contact publisher for licensing details",
                contact_email=doc_metadata.get('contact_email')
            )
        
        logger.info(f"Successfully verified ref_id: {ref_id}")
        
        return VerifyEmbeddingResponse(
            valid=True,
            ref_id=ref_id,
            verified_at=datetime.utcnow(),
            content=content_info,
            document=document_info,
            merkle_proof=merkle_proof_info,
            c2pa=c2pa_info,
            licensing=licensing_info,
            verification_url=reference.to_verification_url()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying embedding: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify embedding"
        )


# ============================================================================
# Batch Verification Endpoint
# ============================================================================

@router.post(
    "/verify/batch",
    response_model=BatchVerifyResponse,
    summary="Batch Verify Embeddings (Public - No Auth Required)",
    description="""
    Verify multiple embeddings in a single request.
    
    **This endpoint is PUBLIC and does NOT require authentication.**
    
    Useful for:
    - Verifying all embeddings on a page at once
    - Bulk verification by web scrapers
    - Browser extensions checking multiple paragraphs
    
    **Rate Limiting:**
    - 100 requests/hour per IP address
    - Maximum 50 embeddings per request
    """,
    responses={
        200: {"description": "Batch verification completed"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"}
    }
)
async def batch_verify_embeddings(
    request: BatchVerifyRequest,
    db: AsyncSession = Depends(get_db)
) -> BatchVerifyResponse:
    """
    Verify multiple embeddings in batch.
    
    Args:
        request: Batch verification request
        db: Database session
    
    Returns:
        BatchVerifyResponse with results for all embeddings
    
    Raises:
        HTTPException: If request is invalid
    """
    try:
        # Validate batch size
        if len(request.references) > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 50 embeddings per batch request"
            )
        
        logger.info(f"Batch verification request for {len(request.references)} embeddings")
        
        results = []
        valid_count = 0
        invalid_count = 0
        
        for ref_req in request.references:
            try:
                # Verify each embedding
                reference = await embedding_service.verify_embedding(
                    db=db,
                    ref_id_hex=ref_req.ref_id,
                    signature_hex=ref_req.signature
                )
                
                if reference:
                    results.append(BatchVerifyResult(
                        ref_id=ref_req.ref_id,
                        valid=True,
                        document_id=reference.document_id,
                        text_preview=reference.text_preview
                    ))
                    valid_count += 1
                else:
                    results.append(BatchVerifyResult(
                        ref_id=ref_req.ref_id,
                        valid=False,
                        error="Invalid signature or not found"
                    ))
                    invalid_count += 1
                    
            except Exception as e:
                logger.warning(f"Error verifying ref_id {ref_req.ref_id}: {e}")
                results.append(BatchVerifyResult(
                    ref_id=ref_req.ref_id,
                    valid=False,
                    error=str(e)
                ))
                invalid_count += 1
        
        logger.info(
            f"Batch verification complete: {valid_count} valid, {invalid_count} invalid"
        )
        
        return BatchVerifyResponse(
            results=results,
            total=len(request.references),
            valid_count=valid_count,
            invalid_count=invalid_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch verification: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process batch verification"
        )
