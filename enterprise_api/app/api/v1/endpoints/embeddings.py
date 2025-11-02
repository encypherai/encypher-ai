"""
API endpoints for minimal signed embeddings.

Enterprise tier endpoints for creating and managing content embeddings.
Built on top of the free encypher-ai package with enterprise features.
"""
import time
import logging
from typing import Optional, Dict

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
from app.middleware.api_key_auth import require_embedding_permission
from app.utils.crypto_utils import load_organization_private_key

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/enterprise/embeddings", tags=["Enterprise - Embeddings"])


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
    organization: Dict = Depends(require_embedding_permission)
) -> EncodeWithEmbeddingsResponse:
    """
    Encode a document with invisible signed embeddings using encypher-ai.
    
    Enterprise features:
    - Merkle tree integration for hierarchical authentication
    - Database storage for content tracking
    - Per-sentence invisible embeddings
    - Public verification API
    
    Args:
        request: Document encoding request with embedding options
        db: Database session
        organization: Authenticated organization
    
    Returns:
        EncodeWithEmbeddingsResponse with Merkle tree and invisible embeddings
    
    Raises:
        HTTPException: If encoding fails
    """
    start_time = time.time()
    
    # Get organization ID from authenticated organization
    organization_id = organization["organization_id"]
    
    try:
        logger.info(
            f"Encoding document {request.document_id} with invisible embeddings "
            f"for org {organization_id} ({organization['organization_name']}) "
            f"at {request.segmentation_level} level using encypher-ai"
        )
        
        # Load organization's private key for signing
        try:
            private_key = await load_organization_private_key(organization_id, db)
            signer_id = f"org_{organization_id}"
        except ValueError as e:
            logger.error(f"Failed to load private key for org {organization_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "NO_PRIVATE_KEY",
                    "message": "Organization has no private key configured. "
                    "Please complete certificate onboarding first.",
                    "details": str(e),
                },
            )
        
        # Initialize embedding service with organization's key
        embedding_service = EmbeddingService(private_key, signer_id)
        
        # Free tier (document-level): Skip Merkle tree and segmentation
        # Just create ONE C2PA wrapper for the entire document
        if request.segmentation_level == 'document':
            logger.info(f"Document-level signing (free tier) - no segmentation")
            from app.utils.merkle import compute_hash
            segments = [request.text]  # Single segment = entire document
            leaf_hashes = [compute_hash(request.text)]  # Single hash for entire document
            merkle_root_id = None  # No Merkle tree for free tier
            merkle_root = None
        else:
            # Enterprise tier: Build Merkle tree and segment
            logger.info(f"Enterprise tier - building Merkle tree at {request.segmentation_level} level")
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
            merkle_root_id = merkle_root.root_id
            
            # Get segments and hashes
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
            merkle_root_id=merkle_root_id,  # None for free tier
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
                text=emb.embedded_text if request.embedding_options.include_text else None,
                ref_id=None,  # No visible ref_id with invisible embeddings
                signature=None,  # No visible signature with invisible embeddings
                embedding=None,  # No visible embedding string
                verification_url=None,  # Verification is done by extracting from text
                leaf_hash=emb.leaf_hash
            )
            embedding_infos.append(info)
        
        # Step 5: Combine all embedded segments into full document
        # Each segment already has invisible embedding from encypher-ai
        embedded_content = "\n".join(emb.embedded_text for emb in embeddings)
        
        processing_time_ms = (time.time() - start_time) * 1000
        
        logger.info(
            f"Successfully encoded document {request.document_id} with "
            f"{len(embeddings)} invisible embeddings in {processing_time_ms:.2f}ms"
        )
        
        # Build Merkle tree info (None for free tier)
        merkle_tree_info = None
        if merkle_root:
            merkle_tree_info = MerkleTreeInfo(
                root_hash=merkle_root.root_hash,
                total_leaves=merkle_root.total_leaves,
                tree_depth=merkle_root.tree_depth
            )
        
        return EncodeWithEmbeddingsResponse(
            success=True,
            document_id=request.document_id,
            merkle_tree=merkle_tree_info,
            embeddings=embedding_infos,
            embedded_content=embedded_content,
            statistics={
                'total_sentences': len(segments),
                'embeddings_created': len(embeddings),
                'processing_time_ms': round(processing_time_ms, 2),
                'uses_invisible_embeddings': True,
                'segmentation_level': request.segmentation_level,
                'tier': 'free' if request.segmentation_level == 'document' else 'enterprise'
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
