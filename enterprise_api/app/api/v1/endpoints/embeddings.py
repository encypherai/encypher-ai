"""
API endpoints for minimal signed embeddings.

Enterprise tier endpoints for creating and managing content embeddings.
"""
import time
import logging
import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.embeddings import (
    EncodeWithEmbeddingsRequest,
    EncodeWithEmbeddingsResponse,
    EmbeddingInfo,
    MerkleTreeInfo,
    ErrorResponse
)
from app.services.embedding_service import EmbeddingService
from app.services.merkle_service import MerkleService
from app.models.merkle import MerkleRoot

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/enterprise/embeddings", tags=["Enterprise - Embeddings"])

# Initialize embedding service with secret key from environment
SECRET_KEY = os.getenv('EMBEDDING_SECRET_KEY', 'default_secret_key_change_in_production_32bytes!!').encode()
embedding_service = EmbeddingService(SECRET_KEY)


# ============================================================================
# Document Encoding with Embeddings
# ============================================================================

@router.post(
    "/encode-with-embeddings",
    response_model=EncodeWithEmbeddingsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Encode Document with Minimal Signed Embeddings",
    description="""
    Encode a document into Merkle tree AND generate minimal signed embeddings.
    
    This endpoint:
    1. Segments the document text at specified level (sentence/paragraph/etc.)
    2. Builds Merkle tree and stores in database
    3. Generates compact 28-byte embeddings for each segment
    4. Stores embedding references in database
    5. Optionally injects embeddings into content (HTML, Markdown, etc.)
    
    **Embeddings are portable** - they travel with content when copied and enable
    third-party verification without API keys.
    
    **Enterprise Tier Only** - Requires valid organization with embedding features enabled.
    
    **Rate Limits:**
    - Enterprise tier: 1000 documents/month
    
    **Processing Time:**
    - Small documents (<1000 words): ~150-250ms
    - Medium documents (1000-10000 words): ~500ms-3s
    - Large documents (>10000 words): ~2-15s
    """,
    responses={
        201: {"description": "Document encoded successfully with embeddings"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Quota exceeded or feature not enabled"},
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def encode_with_embeddings(
    request: EncodeWithEmbeddingsRequest,
    db: AsyncSession = Depends(get_db),
    # TODO: Add authentication dependency
    # current_org: Organization = Depends(get_current_organization)
) -> EncodeWithEmbeddingsResponse:
    """
    Encode a document with minimal signed embeddings.
    
    Args:
        request: Document encoding request with embedding options
        db: Database session
    
    Returns:
        EncodeWithEmbeddingsResponse with Merkle tree and embeddings
    
    Raises:
        HTTPException: If encoding fails
    """
    start_time = time.time()
    
    # TODO: Replace with actual organization from auth
    organization_id = "org_demo"
    
    try:
        logger.info(
            f"Encoding document {request.document_id} with embeddings "
            f"for org {organization_id} at {request.segmentation_level} level"
        )
        
        # TODO: Check organization tier and quota
        # if not current_org.embeddings_enabled:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Embedding features not enabled for this organization"
        #     )
        
        # Step 1: Build Merkle tree (existing functionality)
        merkle_roots = await MerkleService.encode_document(
            db=db,
            organization_id=organization_id,
            document_id=request.document_id,
            text=request.text,
            segmentation_levels=[request.segmentation_level],
            metadata=request.metadata,
            include_words=False
        )
        
        merkle_root = merkle_roots[request.segmentation_level]
        
        # Step 2: Get segments and hashes
        from app.utils.segmentation import HierarchicalSegmenter
        segmenter = HierarchicalSegmenter(request.text, include_words=False)
        segments = segmenter.get_segments(request.segmentation_level)
        
        # Compute leaf hashes
        from app.utils.merkle import compute_hash
        leaf_hashes = [compute_hash(segment) for segment in segments]
        
        # Step 3: Generate minimal signed embeddings
        license_info = None
        if request.license:
            license_info = {
                'type': request.license.type,
                'url': request.license.url
            }
        
        embeddings = await embedding_service.create_embeddings(
            db=db,
            organization_id=organization_id,
            document_id=request.document_id,
            merkle_root_id=merkle_root.root_id,
            segments=segments,
            leaf_hashes=leaf_hashes,
            c2pa_manifest_url=request.c2pa_manifest_url,
            c2pa_manifest_hash=request.c2pa_manifest_hash,
            license_info=license_info,
            expires_at=request.expires_at
        )
        
        # Step 4: Convert embeddings to response format
        embedding_infos = []
        for emb in embeddings:
            info = EmbeddingInfo(
                leaf_index=emb.leaf_index,
                text=emb.text_content if request.embedding_options.include_text else None,
                ref_id=format(emb.ref_id, '08x'),
                signature=emb.signature[:8],
                embedding=emb.to_compact_string(),
                verification_url=emb.to_url(),
                leaf_hash=emb.leaf_hash
            )
            embedding_infos.append(info)
        
        # Step 5: Optionally inject embeddings into content
        embedded_content = None
        if request.embedding_options.format and request.embedding_options.format != 'json':
            # Import embedding utilities
            if request.embedding_options.format == 'html':
                from app.utils.embeddings.html_embedder import HTMLEmbedder
                embedded_content = HTMLEmbedder.embed_in_paragraphs(
                    html=request.text,  # Assume text is HTML
                    embeddings=embeddings,
                    method=request.embedding_options.method
                )
            # TODO: Add other formats (markdown, pdf, plain)
        
        processing_time_ms = (time.time() - start_time) * 1000
        
        logger.info(
            f"Successfully encoded document {request.document_id} with "
            f"{len(embeddings)} embeddings in {processing_time_ms:.2f}ms"
        )
        
        return EncodeWithEmbeddingsResponse(
            success=True,
            document_id=request.document_id,
            merkle_tree=MerkleTreeInfo(
                root_hash=merkle_root.root_hash,
                total_leaves=merkle_root.total_leaves,
                tree_depth=merkle_root.tree_depth
            ),
            embeddings=embedding_infos,
            embedded_content=embedded_content,
            statistics={
                'total_sentences': len(segments),
                'embeddings_created': len(embeddings),
                'processing_time_ms': round(processing_time_ms, 2),
                'average_embedding_size': 28,  # Compact format
                'segmentation_level': request.segmentation_level
            }
        )
        
    except ValueError as e:
        logger.error(f"Validation error encoding document: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error encoding document with embeddings: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to encode document with embeddings"
        )
