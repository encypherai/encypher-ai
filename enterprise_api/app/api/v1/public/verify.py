"""
Public verification API endpoints.

These endpoints do NOT require authentication and are designed for
third-party verification of embedded content.

Now supports invisible Unicode embeddings from encypher-ai package.
"""

import hmac
import logging
import re
from datetime import datetime
from typing import Any, Dict, Optional, cast

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_content_db, get_db
from app.middleware.api_key_auth import authenticate_api_key, get_api_key_from_header
from app.middleware.public_rate_limiter import public_rate_limiter
from app.models.content_reference import ContentReference
from app.models.merkle import MerkleRoot
from app.schemas.embeddings import (
    BatchVerifyRequest,
    BatchVerifyResponse,
    BatchVerifyResult,
    C2PAInfo,
    ContentInfo,
    DocumentInfo,
    ErrorResponse,
    LicensingInfo,
    MerkleProofInfo,
    VerifyEmbeddingResponse,
)
from app.utils.c2pa_verifier import c2pa_verifier
from app.utils.crypto_utils import load_organization_public_key

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/public", tags=["Public - Verification"])

MAX_EXTRACT_AND_VERIFY_BYTES = 2 * 1024 * 1024
MAX_VERIFY_BATCH_BYTES = 256 * 1024

SIGNATURE_PATTERN = re.compile(r"^[0-9a-fA-F]{8,64}$")


def _signature_matches(signature_hash: Optional[str], provided: str) -> bool:
    if not signature_hash:
        return False

    full_hash = signature_hash.lower()
    provided_lower = provided.lower()
    if len(provided_lower) > len(full_hash):
        return False

    return hmac.compare_digest(full_hash[: len(provided_lower)], provided_lower)


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
    - Does not return DB-stored text
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
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
    },
)
async def verify_embedding(
    ref_id: str,
    request: Request,
    signature: str = Query(..., description="HMAC signature (8+ hex characters)"),
    core_db: AsyncSession = Depends(get_db),
    content_db: AsyncSession = Depends(get_content_db),
    api_key: Optional[str] = Depends(get_api_key_from_header),
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
            organization = await authenticate_api_key(api_key=api_key, db=core_db)
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
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ref_id format (must be 8 hex characters)")

        # Validate signature format
        if not SIGNATURE_PATTERN.fullmatch(signature):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid signature format (must be 8-64 hex characters)",
            )

        # Look up content reference by ref_id
        try:
            ref_id_int = int(ref_id, 16)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ref_id format (must be hex)")

        result = await content_db.execute(select(ContentReference).where(ContentReference.id == ref_id_int))
        reference = result.scalar_one_or_none()

        if not reference:
            logger.warning(f"Verification failed for ref_id: {ref_id}")
            return VerifyEmbeddingResponse(valid=False, ref_id=ref_id, error="Invalid signature or reference not found")

        signature_hash = cast(Optional[str], reference.signature_hash)
        if not _signature_matches(signature_hash, signature):
            logger.warning(f"Signature mismatch for ref_id: {ref_id}")
            return VerifyEmbeddingResponse(valid=False, ref_id=ref_id, error="Invalid signature or reference not found")

        # Get associated Merkle root
        result = await content_db.execute(select(MerkleRoot).where(MerkleRoot.id == reference.merkle_root_id))
        merkle_root = result.scalar_one_or_none()

        if not merkle_root:
            logger.error(f"Merkle root not found for reference: {ref_id}")
            return VerifyEmbeddingResponse(valid=False, ref_id=ref_id, error="Associated Merkle root not found")

        # Build response with metadata (no DB-backed text)
        content_info = ContentInfo(text_preview=None, leaf_hash=reference.leaf_hash, leaf_index=reference.leaf_index)

        # Extract document metadata
        doc_metadata = cast(Dict[str, Any], merkle_root.doc_metadata or {})
        document_info = DocumentInfo(
            document_id=reference.document_id,
            title=doc_metadata.get("title"),
            published_at=doc_metadata.get("published_at"),
            author=doc_metadata.get("author"),
            organization=reference.organization_id,  # TODO: Map to org name
        )

        # Merkle proof info
        merkle_proof_info = MerkleProofInfo(root_hash=merkle_root.root_hash, verified=True, proof_url=f"/api/v1/public/proof/{ref_id}")

        # C2PA info (if available) - Now with actual verification!
        c2pa_info = None
        if reference.c2pa_manifest_url:
            manifest_url = cast(str, reference.c2pa_manifest_url)
            # Verify the C2PA manifest (async)
            c2pa_result = await c2pa_verifier.verify_manifest_url(manifest_url)

            validation_type = "cryptographic" if c2pa_result.signatures and all(sig.verified for sig in c2pa_result.signatures) else "non_cryptographic"
            c2pa_info = C2PAInfo(
                manifest_url=manifest_url,
                manifest_hash=reference.c2pa_manifest_hash or c2pa_result.manifest_hash,
                validated=c2pa_result.valid,
                validation_type=validation_type,
                validation_details=c2pa_result.to_dict() if c2pa_result else None,
            )

        # Licensing info (if available)
        licensing_info = None
        if reference.license_type:
            licensing_info = LicensingInfo(
                license_type=reference.license_type,
                license_url=reference.license_url,
                usage_terms="Contact publisher for licensing details",
                contact_email=doc_metadata.get("contact_email"),
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
            verification_url=reference.to_verification_url(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying embedding: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to verify embedding")


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
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
    },
)
async def batch_verify_embeddings(
    batch_request: BatchVerifyRequest,
    request: Request,
    core_db: AsyncSession = Depends(get_db),
    content_db: AsyncSession = Depends(get_content_db),
    api_key: Optional[str] = Depends(get_api_key_from_header),
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
            organization = await authenticate_api_key(api_key=api_key, db=core_db)
            logger.info(f"Authenticated batch verification from org {organization['organization_id']}")
        except HTTPException as e:
            # Log but don't fail - fall back to unauthenticated access
            logger.warning(f"Authentication failed, falling back to public access: {e.detail}")

    # Rate limiting check (only for unauthenticated requests)
    if not organization:
        await public_rate_limiter(request, endpoint_type="verify_batch")

    try:
        payload_bytes = 0
        for ref_req in batch_request.references:
            payload_bytes += len(ref_req.ref_id.encode("utf-8"))
            payload_bytes += len(ref_req.signature.encode("utf-8"))
        if payload_bytes > MAX_VERIFY_BATCH_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Batch verification payload too large",
            )

        # Validate batch size
        if len(batch_request.references) > 50:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Maximum 50 embeddings per batch request")

        logger.info(f"Batch verification request for {len(batch_request.references)} embeddings")

        results = []
        valid_count = 0
        invalid_count = 0

        for ref_req in batch_request.references:
            try:
                # Look up content reference by ref_id
                try:
                    ref_id_int = int(ref_req.ref_id, 16)
                except ValueError:
                    results.append(BatchVerifyResult(ref_id=ref_req.ref_id, valid=False, error="Invalid ref_id format"))
                    invalid_count += 1
                    continue

                result = await content_db.execute(select(ContentReference).where(ContentReference.id == ref_id_int))
                reference = result.scalar_one_or_none()

                if not SIGNATURE_PATTERN.fullmatch(ref_req.signature):
                    results.append(
                        BatchVerifyResult(
                            ref_id=ref_req.ref_id,
                            valid=False,
                            error="Invalid signature or reference not found",
                        )
                    )
                    invalid_count += 1
                    continue

                signature_hash = cast(Optional[str], reference.signature_hash) if reference else None
                if reference and _signature_matches(signature_hash, ref_req.signature):
                    results.append(BatchVerifyResult(ref_id=ref_req.ref_id, valid=True, document_id=reference.document_id))
                    valid_count += 1
                else:
                    results.append(BatchVerifyResult(ref_id=ref_req.ref_id, valid=False, error="Invalid signature or reference not found"))
                    invalid_count += 1

            except Exception as e:
                logger.warning(f"Error verifying ref_id {ref_req.ref_id}: {e}")
                results.append(BatchVerifyResult(ref_id=ref_req.ref_id, valid=False, error=str(e)))
                invalid_count += 1

        logger.info(f"Batch verification complete: {valid_count} valid, {invalid_count} invalid")

        return BatchVerifyResponse(results=results, total=len(batch_request.references), valid_count=valid_count, invalid_count=invalid_count)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch verification: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process batch verification")


# ============================================================================
# DEPRECATED: Extract and Verify Invisible Embeddings
# Use POST /api/v1/verify instead (verification-service)
# ============================================================================
# This endpoint has been removed. Use the unified /api/v1/verify endpoint
# which provides full C2PA compliance and richer response format.
# ============================================================================


@router.post(
    "/extract-and-verify",
    deprecated=True,
    summary="DEPRECATED - Use POST /api/v1/verify instead",
    description="""
    **⚠️ DEPRECATED: This endpoint is deprecated and will be removed.**
    
    Please use `POST /api/v1/verify` instead, which provides:
    - Full C2PA trust chain validation
    - Document info, licensing, and C2PA details (all free)
    - Merkle proof (with API key)
    - Better performance via verification-service
    """,
    responses={
        301: {"description": "Redirect to /api/v1/verify"},
    },
)
async def extract_and_verify_embedding(
    extract_request: ExtractAndVerifyRequest,
    request: Request,
):
    """
    DEPRECATED: Use POST /api/v1/verify instead.
    
    This endpoint is deprecated. Please migrate to the unified /api/v1/verify
    endpoint which provides full C2PA compliance and a richer response format.
    """
    from fastapi.responses import JSONResponse
    
    logger.warning("Deprecated endpoint /public/extract-and-verify called. Use /api/v1/verify instead.")
    
    return JSONResponse(
        status_code=status.HTTP_410_GONE,
        content={
            "error": "This endpoint is deprecated",
            "message": "Please use POST /api/v1/verify instead",
            "migration_guide": "The unified /api/v1/verify endpoint provides full C2PA compliance, document info, licensing, and C2PA details for free. Merkle proof requires an API key.",
            "new_endpoint": "/api/v1/verify",
        },
    )
