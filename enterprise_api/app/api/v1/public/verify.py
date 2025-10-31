"""
Public verification API endpoints.

These endpoints do NOT require authentication and are designed for
third-party verification of embedded content.

Now supports invisible Unicode embeddings from encypher-ai package.
"""
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field

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
from app.services.embedding_service import EmbeddingService
from app.models.content_reference import ContentReference
from app.models.merkle import MerkleRoot
from app.middleware.public_rate_limiter import public_rate_limiter
from app.middleware.api_key_auth import get_api_key_from_header, authenticate_api_key
from app.utils.c2pa_verifier import c2pa_verifier
from app.utils.crypto_utils import load_organization_public_key

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/public", tags=["Public - Verification"])


# ============================================================================
# Request/Response Schemas for Invisible Embeddings
# ============================================================================

class ExtractAndVerifyRequest(BaseModel):
    """Request to extract and verify invisible embedding from text."""
    text: str = Field(..., description="Text with invisible embedding")


class ExtractAndVerifyResponse(BaseModel):
    """Response from extracting and verifying invisible embedding."""
    valid: bool = Field(..., description="Whether embedding is valid")
    verified_at: Optional[datetime] = Field(None, description="Verification timestamp")
    content: Optional[ContentInfo] = Field(None, description="Content information")
    document: Optional[DocumentInfo] = Field(None, description="Document information")
    merkle_proof: Optional[MerkleProofInfo] = Field(None, description="Merkle proof information")
    c2pa: Optional[C2PAInfo] = Field(None, description="C2PA information")
    licensing: Optional[LicensingInfo] = Field(None, description="Licensing information")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Verified metadata from embedding")
    error: Optional[str] = Field(None, description="Error message if invalid")


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
    request: Request,
    signature: str = Query(..., description="HMAC signature (8+ hex characters)"),
    db: AsyncSession = Depends(get_db),
    api_key: Optional[str] = Depends(get_api_key_from_header)
) -> VerifyEmbeddingResponse:
    """
    Verify an embedding and return associated metadata.
    
    This endpoint supports both authenticated and unauthenticated access:
    - **Unauthenticated:** Rate limited to 1000 requests/hour per IP
    - **Authenticated:** Higher limits based on organization tier, usage tracked
    
    Args:
        ref_id: Reference ID (8 hex characters)
        signature: HMAC signature (8+ hex characters)
        db: Database session
        api_key: Optional API key for authenticated access
    
    Returns:
        VerifyEmbeddingResponse with verification result and metadata
    
    Raises:
        HTTPException: If verification fails or reference not found
    """
    # Optional authentication - if API key provided, authenticate and track usage
    organization = None
    if api_key:
        try:
            organization = await authenticate_api_key(api_key=api_key, db=db)
            logger.info(f"Authenticated verification request from org {organization['organization_id']}")
        except HTTPException as e:
            # Log but don't fail - fall back to unauthenticated access
            logger.warning(f"Authentication failed, falling back to public access: {e.detail}")
    
    # Rate limiting check (only for unauthenticated requests)
    if not organization:
        await public_rate_limiter(request, endpoint_type="verify_single")
    
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
        
        # C2PA info (if available) - Now with actual verification!
        c2pa_info = None
        if reference.c2pa_manifest_url:
            # Verify the C2PA manifest
            c2pa_result = c2pa_verifier.verify_manifest_url(reference.c2pa_manifest_url)
            
            c2pa_info = C2PAInfo(
                manifest_url=reference.c2pa_manifest_url,
                manifest_hash=reference.c2pa_manifest_hash or c2pa_result.manifest_hash,
                verified=c2pa_result.valid,
                verification_details=c2pa_result.to_dict() if c2pa_result else None
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
    batch_request: BatchVerifyRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    api_key: Optional[str] = Depends(get_api_key_from_header)
) -> BatchVerifyResponse:
    """
    Verify multiple embeddings in batch.
    
    This endpoint supports both authenticated and unauthenticated access:
    - **Unauthenticated:** Rate limited to 100 requests/hour per IP
    - **Authenticated:** Higher limits based on organization tier, usage tracked
    
    Args:
        batch_request: Batch verification request
        request: FastAPI request
        db: Database session
        api_key: Optional API key for authenticated access
    
    Returns:
        BatchVerifyResponse with results for all embeddings
    
    Raises:
        HTTPException: If request is invalid
    """
    # Optional authentication - if API key provided, authenticate and track usage
    organization = None
    if api_key:
        try:
            organization = await authenticate_api_key(api_key=api_key, db=db)
            logger.info(f"Authenticated batch verification from org {organization['organization_id']}")
        except HTTPException as e:
            # Log but don't fail - fall back to unauthenticated access
            logger.warning(f"Authentication failed, falling back to public access: {e.detail}")
    
    # Rate limiting check (only for unauthenticated requests)
    if not organization:
        await public_rate_limiter(request, endpoint_type="verify_batch")
    
    try:
        # Validate batch size
        if len(batch_request.references) > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 50 embeddings per batch request"
            )
        
        logger.info(f"Batch verification request for {len(batch_request.references)} embeddings")
        
        results = []
        valid_count = 0
        invalid_count = 0
        
        for ref_req in batch_request.references:
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
            total=len(batch_request.references),
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


# ============================================================================
# Extract and Verify Invisible Embeddings (NEW)
# ============================================================================

@router.post(
    "/extract-and-verify",
    response_model=ExtractAndVerifyResponse,
    summary="Extract and Verify Invisible Embedding (Public - No Auth Required)",
    description="""
    Extract and verify invisible Unicode embedding from text using encypher-ai.
    
    **This endpoint is PUBLIC and does NOT require authentication.**
    
    This is the NEW verification method for invisible embeddings:
    - Extracts invisible Unicode variation selector embeddings
    - Verifies cryptographic signature using encypher-ai
    - Returns enterprise metadata (Merkle tree, document info, etc.)
    
    **How it works:**
    1. Text contains invisible Unicode variation selectors
    2. encypher-ai extracts and verifies the embedded metadata
    3. Enterprise API looks up Merkle tree and document info
    4. Returns full verification result with all metadata
    
    **Rate Limiting:**
    - 1000 requests/hour per IP address
    
    **Example Usage:**
    ```json
    POST /api/v1/public/extract-and-verify
    {
      "text": "Content with invisible embedding..."
    }
    ```
    """,
    responses={
        200: {"description": "Embedding extracted and verified"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        404: {"model": ErrorResponse, "description": "No embedding found"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"}
    }
)
async def extract_and_verify_embedding(
    extract_request: ExtractAndVerifyRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    api_key: Optional[str] = Depends(get_api_key_from_header)
) -> ExtractAndVerifyResponse:
    """
    Extract and verify invisible embedding from text.
    
    Uses encypher-ai package to extract invisible Unicode embeddings,
    then looks up enterprise metadata in database.
    
    Args:
        extract_request: Request with text containing invisible embedding
        request: FastAPI request
        db: Database session
        api_key: Optional API key for authenticated access
    
    Returns:
        ExtractAndVerifyResponse with verification result and metadata
    
    Raises:
        HTTPException: If extraction/verification fails
    """
    # Optional authentication
    organization = None
    if api_key:
        try:
            organization = await authenticate_api_key(api_key=api_key, db=db)
            logger.info(f"Authenticated extract-and-verify from org {organization['organization_id']}")
        except HTTPException as e:
            logger.warning(f"Authentication failed, falling back to public access: {e.detail}")
    
    # Rate limiting (only for unauthenticated requests)
    if not organization:
        await public_rate_limiter(request, endpoint_type="verify_single")
    
    try:
        logger.info("Extract-and-verify request for invisible embedding")
        
        # Create public key provider function
        # This loads public keys from database by signer_id
        async def public_key_provider(signer_id: str):
            """Load public key for signer_id from database."""
            try:
                # Extract organization ID from signer_id (format: "org_<org_id>")
                if signer_id.startswith("org_"):
                    org_id = signer_id[4:]  # Remove "org_" prefix
                    return await load_organization_public_key(org_id, db)
                else:
                    logger.warning(f"Unknown signer_id format: {signer_id}")
                    return None
            except Exception as e:
                logger.error(f"Failed to load public key for {signer_id}: {e}")
                return None
        
        # Initialize embedding service (we need an instance for verification)
        # Note: We don't need a private key for verification, but the service
        # expects one. We'll need to refactor this to separate verification.
        # For now, we'll use the verify_and_extract_embedding method directly.
        
        # Import encypher-ai for extraction
        try:
            from encypher.core.unicode_metadata import UnicodeMetadata
        except ImportError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="encypher-ai package not available"
            )
        
        # Extract and verify using encypher-ai
        is_valid, signer_id, payload = UnicodeMetadata.verify_metadata(
            text=extract_request.text,
            public_key_provider=public_key_provider
        )
        
        if not is_valid or not payload:
            logger.warning("No valid invisible embedding found in text")
            return ExtractAndVerifyResponse(
                valid=False,
                error="No valid invisible embedding found in text"
            )
        
        # Extract enterprise metadata from custom_metadata
        custom_metadata = payload.custom_metadata or {}
        document_id = custom_metadata.get('document_id')
        organization_id = custom_metadata.get('organization_id')
        leaf_index = custom_metadata.get('leaf_index')
        
        if not all([document_id, organization_id, leaf_index is not None]):
            logger.warning("Missing enterprise metadata in embedding")
            return ExtractAndVerifyResponse(
                valid=True,  # Embedding is valid, but not enterprise
                verified_at=datetime.utcnow(),
                metadata={
                    'signer_id': signer_id,
                    'timestamp': payload.timestamp,
                    'custom_metadata': custom_metadata,
                    'format': payload.format
                },
                error="Valid embedding but missing enterprise metadata"
            )
        
        # Look up ContentReference in database (enterprise feature)
        result = await db.execute(
            select(ContentReference).where(
                ContentReference.document_id == document_id,
                ContentReference.organization_id == organization_id,
                ContentReference.leaf_index == leaf_index
            )
        )
        reference = result.scalar_one_or_none()
        
        if not reference:
            logger.warning(
                f"Reference not found in database: doc={document_id}, "
                f"org={organization_id}, leaf={leaf_index}"
            )
            return ExtractAndVerifyResponse(
                valid=True,
                verified_at=datetime.utcnow(),
                metadata={
                    'signer_id': signer_id,
                    'timestamp': payload.timestamp,
                    'custom_metadata': custom_metadata
                },
                error="Valid embedding but not found in enterprise database"
            )
        
        # Check expiration
        if reference.expires_at and reference.expires_at < datetime.utcnow():
            logger.warning(f"Reference expired: {document_id}")
            return ExtractAndVerifyResponse(
                valid=False,
                error="Embedding has expired"
            )
        
        # Get associated Merkle root
        merkle_result = await db.execute(
            select(MerkleRoot).where(MerkleRoot.root_id == reference.merkle_root_id)
        )
        merkle_root = merkle_result.scalar_one_or_none()
        
        # Build full response with enterprise metadata
        content_info = ContentInfo(
            text_preview=reference.text_preview or "",
            leaf_hash=reference.leaf_hash,
            leaf_index=reference.leaf_index
        )
        
        # Extract document metadata
        doc_metadata = merkle_root.doc_metadata if merkle_root else {}
        document_info = DocumentInfo(
            document_id=reference.document_id,
            title=doc_metadata.get('title'),
            published_at=doc_metadata.get('published_at'),
            author=doc_metadata.get('author'),
            organization=reference.organization_id
        )
        
        # Merkle proof info
        merkle_proof_info = None
        if merkle_root:
            merkle_proof_info = MerkleProofInfo(
                root_hash=merkle_root.root_hash,
                verified=True,
                proof_url=f"/api/v1/public/proof/{reference.document_id}"
            )
        
        # C2PA info (if available)
        c2pa_info = None
        if reference.c2pa_manifest_url:
            c2pa_result = c2pa_verifier.verify_manifest_url(reference.c2pa_manifest_url)
            c2pa_info = C2PAInfo(
                manifest_url=reference.c2pa_manifest_url,
                manifest_hash=reference.c2pa_manifest_hash or c2pa_result.manifest_hash,
                verified=c2pa_result.valid,
                verification_details=c2pa_result.to_dict() if c2pa_result else None
            )
        
        # Licensing info
        licensing_info = None
        if reference.license_type:
            licensing_info = LicensingInfo(
                license_type=reference.license_type,
                license_url=reference.license_url,
                usage_terms="Contact publisher for licensing details",
                contact_email=doc_metadata.get('contact_email')
            )
        
        logger.info(
            f"Successfully verified invisible embedding: doc={document_id}, leaf={leaf_index}"
        )
        
        return ExtractAndVerifyResponse(
            valid=True,
            verified_at=datetime.utcnow(),
            content=content_info,
            document=document_info,
            merkle_proof=merkle_proof_info,
            c2pa=c2pa_info,
            licensing=licensing_info,
            metadata={
                'signer_id': signer_id,
                'timestamp': payload.timestamp,
                'custom_metadata': custom_metadata,
                'format': payload.format,
                'version': payload.version
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting and verifying embedding: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to extract and verify embedding"
        )
