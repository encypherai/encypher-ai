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
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
    },
)
async def extract_and_verify_embedding(
    extract_request: ExtractAndVerifyRequest,
    request: Request,
    core_db: AsyncSession = Depends(get_db),
    content_db: AsyncSession = Depends(get_content_db),
    api_key: Optional[str] = Depends(get_api_key_from_header),
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
            organization = await authenticate_api_key(api_key=api_key, db=core_db)
            logger.info(f"Authenticated extract-and-verify from org {organization['organization_id']}")
        except HTTPException as e:
            logger.warning(f"Authentication failed, falling back to public access: {e.detail}")

    # Rate limiting (only for unauthenticated requests)
    if not organization:
        await public_rate_limiter(request, endpoint_type="verify_single")

    try:
        payload_bytes = len(extract_request.text.encode("utf-8"))
        if payload_bytes > MAX_EXTRACT_AND_VERIFY_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Extract-and-verify payload too large",
            )

        logger.info("Extract-and-verify request for invisible embedding")

        # Import encypher-ai for extraction
        try:
            from encypher.core.unicode_metadata import UnicodeMetadata
        except ImportError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="encypher-ai package not available")

        # First, extract the signer_id from the text without verification
        # This allows us to load the correct public key
        try:
            logger.info(f"Attempting to extract metadata from text (length: {len(extract_request.text)} chars)")

            # Check for invisible characters in the text
            invisible_count = sum(1 for c in extract_request.text if ord(c) > 0xE0000)
            logger.info(f"Found {invisible_count} invisible Unicode characters in text")

            extracted_metadata = UnicodeMetadata.extract_metadata(extract_request.text)
            logger.info(f"extract_metadata returned: {type(extracted_metadata)} = {extracted_metadata}")

            if not extracted_metadata:
                logger.warning("No metadata found in text. payload_chars=%s", len(extract_request.text))
                return ExtractAndVerifyResponse(valid=False, error="No invisible embedding found in text")

            signer_id = extracted_metadata.get("signer_id")
            if signer_id:
                logger.info(f"Extracted signer_id from metadata: {signer_id}")
            else:
                # Extract signer_id from claim_generator (format: "Encypher Enterprise API/org_demo")
                # The signer_id is the part after the last slash
                claim_generator = extracted_metadata.get("claim_generator", "")
                if "/" in claim_generator:
                    signer_candidate = claim_generator.split("/")[-1]
                    if signer_candidate.startswith(("org_", "user_")):
                        signer_id = signer_candidate
                        logger.info(f"Extracted signer_id from claim_generator: {signer_id}")
                    else:
                        logger.info(
                            "Claim generator does not contain org/user signer id: %s",
                            claim_generator,
                        )

            if not signer_id:
                custom_metadata = extracted_metadata.get("custom_metadata") or {}
                if isinstance(custom_metadata, dict) and custom_metadata.get("organization_id"):
                    signer_id = custom_metadata.get("organization_id")
                    logger.info(f"Extracted signer_id from custom metadata: {signer_id}")

            if not signer_id:
                assertions = extracted_metadata.get("assertions", [])
                for assertion in assertions:
                    if assertion.get("label") == "org.encypher.metadata":
                        data = assertion.get("data", {})
                        if isinstance(data, dict) and data.get("organization_id"):
                            signer_id = data.get("organization_id")
                            logger.info(f"Extracted signer_id from assertions: {signer_id}")
                            break

            if not signer_id:
                assertions = extracted_metadata.get("assertions", [])
                for assertion in assertions:
                    if assertion.get("label") in {"c2pa.actions.v1", "c2pa.actions.v2"}:
                        actions = assertion.get("data", {}).get("actions", [])
                        for action in actions:
                            agent = action.get("softwareAgent")
                            if isinstance(agent, str) and "/" in agent:
                                candidate = agent.split("/")[-1]
                                if candidate.startswith(("org_", "user_")):
                                    signer_id = candidate
                                    logger.info(f"Extracted signer_id from action agent: {signer_id}")
                                    break
                        if signer_id:
                            break

            if not signer_id:
                claim_generator = extracted_metadata.get("claim_generator", "")
                logger.warning(f"Could not extract signer_id from metadata. claim_generator={claim_generator}")
                return ExtractAndVerifyResponse(valid=False, error="Invalid metadata format - missing signer information")

            # Load the public key for this signer
            # Note: signer_id format is "org_<org_id>" (e.g., "org_demo") or "user_<user_id>"
            if signer_id.startswith("org_") or signer_id.startswith("user_"):
                try:
                    # TRUST ANCHOR CHECK:
                    # We look up the public key in our database to verify the signer's identity.
                    # This implements the "Trust" part of the verification.
                    # For user_ orgs, load_organization_public_key returns the demo key.
                    public_key = await load_organization_public_key(signer_id, core_db)
                except ValueError:
                    # Signer is unknown to our Trust Anchor
                    logger.warning(f"Signer ID {signer_id} not found in Trust Anchor database")
                    return ExtractAndVerifyResponse(
                        valid=False, error=f"Unknown Signer: Identity {signer_id} is not recognized by this Trust Anchor."
                    )
            else:
                logger.warning(f"Unknown signer_id format: {signer_id}")
                return ExtractAndVerifyResponse(valid=False, error=f"Unknown signer format: {signer_id}")

            # Create a synchronous resolver that returns the pre-loaded key
            # This avoids the async issue since we already have the key
            def sync_public_key_resolver(resolver_signer_id: str):
                """Return the pre-loaded public key for the expected signer."""
                if resolver_signer_id == signer_id:
                    return public_key
                logger.warning(f"Unexpected signer_id in resolver: {resolver_signer_id} != {signer_id}")
                return None

            # Now verify with the resolver (synchronous call)
            # This implements the "Integrity" part of the verification using the trusted key.
            is_valid, verified_signer_id, payload = UnicodeMetadata.verify_metadata(
                text=extract_request.text, public_key_resolver=sync_public_key_resolver
            )

        except Exception as e:
            logger.error(f"Error extracting/verifying metadata: {e}", exc_info=True)
            return ExtractAndVerifyResponse(valid=False, error=f"Verification error: {str(e)}")

        if not is_valid or not payload:
            logger.warning("No valid invisible embedding found in text")
            return ExtractAndVerifyResponse(valid=False, error="No valid invisible embedding found in text")

        logger.info(f"Payload content: {payload}")

        # Extract enterprise metadata from custom_metadata
        # payload is the C2PA manifest dict
        # Try to find document_id and organization_id from assertions or payload
        custom_metadata = {}
        document_id = None
        organization_id = signer_id if signer_id.startswith("org_") else None
        leaf_index = None
        manifest_uuid = None
        payload_format = payload.get("format") if isinstance(payload, dict) else None
        payload_version = payload.get("version") if isinstance(payload, dict) else None
        payload_timestamp = payload.get("timestamp") if isinstance(payload, dict) else None

        # Check if payload itself has the metadata (from legacy/basic format)
        if payload.get("custom_metadata"):
            custom_metadata = payload.get("custom_metadata")
            document_id = custom_metadata.get("document_id")
            # Override org_id if present in metadata
            if custom_metadata.get("organization_id"):
                organization_id = custom_metadata.get("organization_id")
            leaf_index = custom_metadata.get("leaf_index")
            manifest_uuid = custom_metadata.get("manifest_uuid")

        # Also check assertions for C2PA format
        assertions = payload.get("assertions", [])
        for assertion in assertions:
            # Check for custom metadata assertion
            if assertion.get("label") == "org.encypher.metadata":
                data = assertion.get("data", {})
                custom_metadata.update(data)
                if data.get("document_id"):
                    document_id = data.get("document_id")
                if data.get("organization_id"):
                    organization_id = data.get("organization_id")
                if data.get("manifest_uuid"):
                    manifest_uuid = data.get("manifest_uuid")
            if assertion.get("label") == "c2pa.metadata":
                data = assertion.get("data", {})
                custom_metadata.update(data)
                if data.get("identifier"):
                    document_id = data.get("identifier")

            # Also check actions for implicit metadata if needed
            if assertion.get("label") == "c2pa.actions.v1":
                pass

        if payload_format is None:
            payload_format = extracted_metadata.get("format")
        if payload_format is None and isinstance(payload, dict) and payload.get("@context"):
            payload_format = "c2pa"

        logger.info(f"C2PA verification successful for signer: {signer_id}. DocID: {document_id}")

        reference = None
        # Look up ContentReference in database (enterprise feature) if we have enough info
        if manifest_uuid:
            result = await content_db.execute(
                select(ContentReference).where(
                    ContentReference.embedding_metadata["manifest_uuid"].as_string() == manifest_uuid
                )
            )
            reference = result.scalar_one_or_none()
            if reference:
                document_id = reference.document_id
                organization_id = reference.organization_id
                leaf_index = reference.leaf_index
        elif document_id and organization_id:
            # If leaf_index is missing (full doc), maybe we look for the first one or just by doc_id?
            # For extract-and-verify of a full document, we might not have a specific leaf_index.
            # But ContentReference is per-leaf.
            # If we verified the WHOLE document, we verified the Merkle Root (implicitly).
            # But we don't have a "DocumentReference" table, only "ContentReference".
            # We can try to find ANY reference for this document to validate it exists.

            query = select(ContentReference).where(ContentReference.document_id == document_id, ContentReference.organization_id == organization_id)
            if leaf_index is not None:
                query = query.where(ContentReference.leaf_index == leaf_index)
            else:
                # Just get the first one to validate existence
                query = query.limit(1)

            result = await content_db.execute(query)
            reference = result.scalar_one_or_none()

        if not reference and document_id:
            logger.warning(f"Reference not found in database: doc={document_id}, org={organization_id}, leaf={leaf_index}")

        if not reference:
            logger.warning(f"Reference not found in database: doc={document_id}, org={organization_id}, leaf={leaf_index}")
            return ExtractAndVerifyResponse(
                valid=True,
                verified_at=datetime.utcnow(),
                metadata={
                    "signer_id": signer_id,
                    "timestamp": payload_timestamp,
                    "custom_metadata": custom_metadata,
                    "format": payload_format,
                    "version": payload_version,
                },
                error="Valid embedding but not found in enterprise database",
            )

        # Check expiration
        if reference.expires_at and reference.expires_at < datetime.utcnow():
            logger.warning(f"Reference expired: {document_id}")
            return ExtractAndVerifyResponse(valid=False, error="Embedding has expired")

        # Get associated Merkle root
        merkle_result = await content_db.execute(select(MerkleRoot).where(MerkleRoot.id == reference.merkle_root_id))
        merkle_root = merkle_result.scalar_one_or_none()

        # Build full response with enterprise metadata (preview from request text only)
        content_info = ContentInfo(
            text_preview=extract_request.text[:200] if extract_request.text else None,
            leaf_hash=reference.leaf_hash,
            leaf_index=reference.leaf_index,
        )

        # Extract document metadata
        doc_metadata = cast(Dict[str, Any], merkle_root.doc_metadata) if merkle_root else {}
        document_info = DocumentInfo(
            document_id=reference.document_id,
            title=doc_metadata.get("title"),
            published_at=doc_metadata.get("published_at"),
            author=doc_metadata.get("author"),
            organization=reference.organization_id,
        )

        # Merkle proof info
        merkle_proof_info = None
        if merkle_root:
            merkle_proof_info = MerkleProofInfo(
                root_hash=merkle_root.root_hash, verified=True, proof_url=f"/api/v1/public/proof/{reference.document_id}"
            )

        # C2PA info (if available)
        c2pa_info = None
        if reference.c2pa_manifest_url:
            manifest_url = cast(str, reference.c2pa_manifest_url)
            c2pa_result = await c2pa_verifier.verify_manifest_url(manifest_url)
            validation_type = "cryptographic" if c2pa_result.signatures and all(sig.verified for sig in c2pa_result.signatures) else "non_cryptographic"
            c2pa_info = C2PAInfo(
                manifest_url=manifest_url,
                manifest_hash=reference.c2pa_manifest_hash or c2pa_result.manifest_hash,
                validated=c2pa_result.valid,
                validation_type=validation_type,
                validation_details=c2pa_result.to_dict() if c2pa_result else None,
            )

        # Licensing info
        licensing_info = None
        if reference.license_type:
            licensing_info = LicensingInfo(
                license_type=reference.license_type,
                license_url=reference.license_url,
                usage_terms="Contact publisher for licensing details",
                contact_email=doc_metadata.get("contact_email"),
            )

        logger.info(f"Successfully verified invisible embedding: doc={document_id}, leaf={leaf_index}")

        return ExtractAndVerifyResponse(
            valid=True,
            verified_at=datetime.utcnow(),
            content=content_info,
            document=document_info,
            merkle_proof=merkle_proof_info,
            c2pa=c2pa_info,
            licensing=licensing_info,
            metadata={
                "signer_id": signer_id,
                "timestamp": payload_timestamp,
                "custom_metadata": custom_metadata,
                "format": payload_format,
                "version": payload_version,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting and verifying embedding: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to extract and verify embedding")
