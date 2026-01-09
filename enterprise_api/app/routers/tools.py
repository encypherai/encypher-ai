"""
Tools router for public encode/decode demo endpoints.

These endpoints use a demo key for the public website tools,
allowing users to try encoding/decoding without authentication.
"""
import logging
import re
from typing import Any, Dict, Literal, Optional

from encypher.core.constants import MetadataTarget
from encypher.core.unicode_metadata import UnicodeMetadata
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.utils.crypto_utils import get_demo_private_key, load_organization_public_key
from app.utils.multi_embedding import extract_and_verify_all_embeddings, extract_all_embeddings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tools", tags=["Public Tools"])


# =============================================================================
# Request/Response Models
# =============================================================================

class EncodeToolRequest(BaseModel):
    """Request model for encoding text with metadata."""
    
    original_text: str = Field(
        ..., 
        description="The original text to embed metadata into.",
        min_length=1,
        max_length=100000,
    )
    target: Optional[Literal[
        "whitespace", "punctuation", "first_letter", "last_letter", "all_characters"
    ]] = Field(
        "first_letter",
        description="Where to embed metadata.",
    )
    metadata_format: Optional[Literal["basic", "manifest", "c2pa_v2_2"]] = Field(
        "c2pa_v2_2",
        description="Format of metadata to embed.",
    )
    ai_info: Optional[Dict[str, Any]] = Field(
        None,
        description="AI model information for C2PA manifest.",
    )
    custom_metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Custom key-value pairs to embed.",
    )


class EncodeToolResponse(BaseModel):
    """Response model for encoding."""
    
    encoded_text: str = Field(..., description="Text with embedded metadata.")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata that was embedded.")
    error: Optional[str] = None


class DecodeToolRequest(BaseModel):
    """Request model for decoding text."""
    
    encoded_text: str = Field(
        ..., 
        description="The text containing embedded metadata.",
        min_length=1,
        max_length=100000,
    )


class VerifyVerdict(BaseModel):
    """Verification verdict details."""
    
    valid: bool = False
    tampered: bool = False
    reason_code: str = "UNKNOWN"
    signer_id: Optional[str] = None
    signer_name: Optional[str] = None
    timestamp: Optional[str] = None


class EmbeddingResult(BaseModel):
    """Result for a single embedding found in text."""
    
    index: int = Field(..., description="Index of this embedding (0-based)")
    metadata: Optional[Dict[str, Any]] = None
    verification_status: Literal["Success", "Failure", "Key Not Found", "Not Attempted", "Error"] = "Not Attempted"
    error: Optional[str] = None
    verdict: Optional[VerifyVerdict] = None
    text_span: Optional[tuple[int, int]] = Field(None, description="Start and end position of this embedding in the original text")
    clean_text: Optional[str] = Field(None, description="The text covered by this embedding (without the wrapper)")


class DecodeToolResponse(BaseModel):
    """Response model for decoding."""
    
    metadata: Optional[Dict[str, Any]] = None
    verification_status: Literal["Success", "Failure", "Key Not Found", "Not Attempted", "Error"] = "Not Attempted"
    error: Optional[str] = None
    raw_hidden_data: Optional[VerifyVerdict] = None
    # New fields for multiple embeddings
    embeddings_found: int = Field(0, description="Number of embeddings found in the text")
    all_embeddings: Optional[list[EmbeddingResult]] = Field(None, description="All embeddings found, with individual verification results")


# =============================================================================
# Demo Key Management
# =============================================================================

# Demo keys are loaded from environment or generated at startup
_demo_private_key = None
_demo_public_key = None
_demo_signer_id = "org_demo"


def _get_demo_keys():
    """Get demo keys for public tools.
    
    IMPORTANT: This MUST use the same key source as embedding_executor.py
    to ensure content signed with user API keys can be verified.
    Both use crypto_utils.get_demo_private_key() which loads from
    settings.demo_private_key_bytes (hex format).
    """
    global _demo_private_key, _demo_public_key
    
    if _demo_private_key is not None:
        return _demo_private_key, _demo_public_key
    
    # Use the SAME key loading function as embedding_executor.py
    # This ensures signing and verification use the same key
    _demo_private_key = get_demo_private_key()
    _demo_public_key = _demo_private_key.public_key()
    logger.info("Loaded demo keys from crypto_utils.get_demo_private_key()")
    return _demo_private_key, _demo_public_key


def _get_target_enum(target_str: str) -> MetadataTarget:
    """Map target string to MetadataTarget enum."""
    target_map = {
        "whitespace": MetadataTarget.WHITESPACE,
        "punctuation": MetadataTarget.PUNCTUATION,
        "first_letter": MetadataTarget.FIRST_LETTER,
        "last_letter": MetadataTarget.LAST_LETTER,
        "all_characters": MetadataTarget.ALL_CHARACTERS,
    }
    
    target_lower = (target_str or "first_letter").lower()
    if target_lower not in target_map:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid target: {target_str}. Must be one of: {list(target_map.keys())}"
        )
    return target_map[target_lower]




# =============================================================================
# Endpoints
# =============================================================================

@router.post("/encode", response_model=EncodeToolResponse)
async def encode_text(request: EncodeToolRequest) -> EncodeToolResponse:
    """
    Encode text with embedded metadata using the demo key.
    
    This is a public endpoint for the website demo tool.
    All encoding uses a server-side demo key.
    """
    logger.info(f"Encode request: target={request.target}, format={request.metadata_format}")
    
    try:
        private_key, _ = _get_demo_keys()
        target_enum = _get_target_enum(request.target or "first_letter")
        
        # Build metadata
        custom_metadata = request.custom_metadata or {}
        if "source" not in custom_metadata:
            custom_metadata["source"] = "Encypher Demo"

        # Determine format
        metadata_format = request.metadata_format or "c2pa_v2_2"

        # Build C2PA-compliant actions
        actions = []
        custom_assertions = []

        # Add c2pa.created action (core library will add if not present)
        from datetime import datetime, timezone
        iso_timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        # If AI info provided, add as custom assertion per C2PA 2.2
        if request.ai_info:
            claim_generator = request.ai_info.get("claim_generator", "Encypher Demo UI")
            provenance = request.ai_info.get("provenance", "")

            # Add c2pa.generative-ai assertion (if we have model info)
            if provenance or claim_generator:
                custom_assertions.append({
                    "label": "c2pa.generative-ai",
                    "data": {
                        "softwareAgent": claim_generator,
                        "description": provenance if provenance else "AI-assisted content generation"
                    }
                })

        # Encode
        if metadata_format == "c2pa_v2_2":
            encoded_text = UnicodeMetadata.embed_metadata(
                text=request.original_text,
                private_key=private_key,
                signer_id=_demo_signer_id,
                metadata_format="manifest",
                target=target_enum,
                actions=actions if actions else None,
                custom_assertions=custom_assertions if custom_assertions else None,
                claim_generator=request.ai_info.get("claim_generator") if request.ai_info else "Encypher Demo UI",
                timestamp=iso_timestamp,
            )
        else:
            encoded_text = UnicodeMetadata.embed_metadata(
                text=request.original_text,
                private_key=private_key,
                signer_id=_demo_signer_id,
                metadata_format=metadata_format,
                target=target_enum,
                custom_metadata=custom_metadata,
            )
        
        logger.info(f"Successfully encoded text with {metadata_format} format")

        # Extract the manifest to return it in the response
        extracted_metadata = UnicodeMetadata.extract_metadata(text=encoded_text)
        manifest_data = extracted_metadata if extracted_metadata else {}

        return EncodeToolResponse(
            encoded_text=encoded_text,
            metadata=manifest_data,
            error=None,
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Encoding failed (ValueError): {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Encoding failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Encoding failed. Please try again."
        )


@router.post("/decode", response_model=DecodeToolResponse)
async def decode_text(
    request: DecodeToolRequest,
    db: AsyncSession = Depends(get_db),
) -> DecodeToolResponse:
    """
    Decode and verify text containing embedded metadata.
    
    This is a public endpoint for the website demo tool.
    Supports multiple embeddings in a single text (Encypher proprietary feature).
    Verification uses Trust Anchor lookup - checks database for org public keys.
    Falls back to demo key for demo-signed content.
    """
    logger.info("Decode request received")
    
    try:
        _, public_key = _get_demo_keys()
        demo_signer_ids = {_demo_signer_id, "org_demo", "demo-signer-id", "c2pa-demo-signer-001"}
        
        # Check for multiple embeddings first (Encypher proprietary feature)
        multi_result = extract_all_embeddings(request.encoded_text)
        
        if multi_result.total_found > 1:
            # Multiple embeddings found - use multi-embedding verification
            logger.info(f"Found {multi_result.total_found} embeddings in text")
            
            # Pre-resolve all signer keys from Trust Anchor database
            # This checks the FULL trust anchor list, not just demo keys
            resolved_keys: dict = {}
            for emb in multi_result.embeddings:
                if emb.signer_id and emb.signer_id not in resolved_keys:
                    try:
                        # load_organization_public_key handles:
                        # - org_demo -> demo key
                        # - user_* -> demo key  
                        # - org_* -> database lookup
                        resolved_keys[emb.signer_id] = await load_organization_public_key(emb.signer_id, db)
                        logger.debug(f"Resolved key for {emb.signer_id} from Trust Anchor")
                    except Exception as e:
                        logger.warning(f"Failed to resolve key for {emb.signer_id}: {e}")
                        # Fall back to demo key for known demo signer IDs
                        if emb.signer_id in demo_signer_ids:
                            resolved_keys[emb.signer_id] = public_key
                        else:
                            resolved_keys[emb.signer_id] = None
            
            def public_key_resolver(signer_id: str):
                """Resolve public key from pre-fetched Trust Anchor results."""
                if signer_id in resolved_keys:
                    return resolved_keys[signer_id]
                # Final fallback for demo signer IDs not in database
                if signer_id in demo_signer_ids:
                    return public_key
                return None
            
            # Verify all embeddings
            verified_result = await extract_and_verify_all_embeddings(
                request.encoded_text,
                public_key_resolver,
                demo_signer_ids,
            )
            
            # Convert to response format
            all_embeddings = []
            for emb in verified_result.embeddings:
                allowed_statuses = {"Success", "Failure", "Key Not Found", "Not Attempted", "Error"}
                raw_status = emb.verification_status
                # Backwards/defensive: older or internal code may emit non-schema values like "Tampered".
                if raw_status == "Tampered":
                    safe_status = "Failure"
                elif raw_status in allowed_statuses:
                    safe_status = raw_status
                else:
                    safe_status = "Error"

                # Determine tampered status - check both signature and content hash
                is_tampered = (
                    (not emb.signature_valid and emb.metadata is not None) or
                    emb.content_hash_valid is False
                )
                # Determine reason code
                if emb.signature_valid and emb.content_hash_valid is not False:
                    reason_code = "VERIFIED"
                elif emb.content_hash_valid is False:
                    reason_code = "CONTENT_MODIFIED"
                else:
                    reason_code = "VERIFICATION_FAILED"
                
                all_embeddings.append(EmbeddingResult(
                    index=emb.index,
                    metadata=emb.metadata,
                    verification_status=safe_status,
                    error=emb.error,
                    verdict=VerifyVerdict(
                        valid=emb.signature_valid and emb.content_hash_valid is not False,
                        tampered=is_tampered,
                        reason_code=reason_code,
                        signer_id=emb.signer_id,
                        signer_name=emb.signer_name,
                    ),
                    text_span=emb.span,
                    clean_text=emb.segment_text[:500] if emb.segment_text else None,  # Truncate for response
                ))
            
            # Determine overall status
            if verified_result.all_valid:
                overall_status = "Success"
                overall_error = None
            elif verified_result.any_valid:
                overall_status = "Failure"
                valid_count = sum(
                    1
                    for e in verified_result.embeddings
                    if e.signature_valid and getattr(e, "content_hash_valid", None) is not False
                )
                overall_error = f"Found {verified_result.total_found} embeddings, but only {valid_count} verified successfully."
            else:
                overall_status = "Failure"
                overall_error = f"Found {verified_result.total_found} embeddings, but none could be verified."
            
            # Use first embedding's metadata as primary (for backwards compatibility)
            primary_metadata = verified_result.embeddings[0].metadata if verified_result.embeddings else None
            primary_verdict = all_embeddings[0].verdict if all_embeddings else None
            
            return DecodeToolResponse(
                metadata=primary_metadata,
                verification_status=overall_status,
                error=overall_error,
                raw_hidden_data=primary_verdict,
                embeddings_found=verified_result.total_found,
                all_embeddings=all_embeddings,
            )
        
        # Single embedding or no embeddings - use standard extraction
        # First, try to find the wrapper and extract just the signed segment
        # This handles the case where user copy-pastes entire page with extra content
        # Per C2PA spec (Manifests_Text.adoc), the exclusions field tells us exactly
        # how many bytes of content should precede the wrapper in the original signed text.
        import unicodedata
        from encypher.interop.c2pa.text_wrapper import find_and_decode
        text_to_verify = request.encoded_text
        wrapper_info = None
        content_extraction_note = None

        manifest_bytes, _clean_text, span = find_and_decode(request.encoded_text)
        if manifest_bytes is not None and span is not None:
            wrapper_start, wrapper_end = span
            wrapper_info = (manifest_bytes, wrapper_start, wrapper_end)
            logger.info(f"Found C2PA wrapper at char positions [{wrapper_start}:{wrapper_end}]")

            # Per C2PA spec: use exclusions to determine the exact content that was hashed
            try:
                from encypher.core.payloads import deserialize_jumbf_payload, deserialize_c2pa_payload_from_cbor
                from encypher.core.signing import extract_payload_from_cose_sign1
                import base64

                manifest_store = deserialize_jumbf_payload(manifest_bytes)
                if isinstance(manifest_store, dict) and manifest_store.get("cose_sign1"):
                    cose_bytes = base64.b64decode(manifest_store["cose_sign1"])
                    cbor_payload = extract_payload_from_cose_sign1(cose_bytes)
                    if cbor_payload:
                        c2pa_manifest = deserialize_c2pa_payload_from_cbor(cbor_payload)
                        assertions = c2pa_manifest.get("assertions", [])
                        hard_binding = next((a for a in assertions if a.get("label") == "c2pa.hash.data.v1"), None)
                        if hard_binding:
                            exclusions = hard_binding.get("data", {}).get("exclusions", [])
                            if exclusions and isinstance(exclusions[0], dict):
                                # Per C2PA spec: exclusion.start = byte offset where wrapper begins
                                # This tells us exactly how many UTF-8 bytes of content preceded the wrapper
                                original_content_bytes = exclusions[0].get("start", 0)
                                wrapper_byte_length = exclusions[0].get("length", 0)

                                logger.info(f"C2PA exclusion: original content was {original_content_bytes} bytes before wrapper")

                                # Normalize text per C2PA spec (NFC normalization required)
                                normalized_text = unicodedata.normalize("NFC", request.encoded_text)

                                # Wrapper segment lives in normalized_text at the same char span
                                wrapper_segment = normalized_text[wrapper_start:wrapper_end]
                                normalized_wrapper_pos = wrapper_start

                                if normalized_wrapper_pos >= 0:
                                    # Work BACKWARDS from wrapper position to extract exactly
                                    # original_content_bytes worth of UTF-8 content
                                    text_before_wrapper_normalized = normalized_text[:normalized_wrapper_pos]

                                    # Convert to UTF-8 bytes to work with byte offsets
                                    bytes_before_wrapper = text_before_wrapper_normalized.encode("utf-8")
                                    actual_bytes_before = len(bytes_before_wrapper)

                                    logger.info(f"Actual bytes before wrapper in pasted text: {actual_bytes_before}")

                                    if actual_bytes_before > original_content_bytes:
                                        # Extra page chrome detected - extract only the signed portion
                                        # Take the LAST original_content_bytes bytes before the wrapper
                                        signed_content_bytes = bytes_before_wrapper[-original_content_bytes:]

                                        # Decode back to string and append wrapper
                                        signed_content = signed_content_bytes.decode("utf-8")
                                        text_to_verify = signed_content + wrapper_segment

                                        extra_bytes = actual_bytes_before - original_content_bytes
                                        content_extraction_note = f"Extracted {original_content_bytes} bytes of signed content (removed {extra_bytes} bytes of page chrome)"
                                        logger.info(content_extraction_note)

                                        # Verify extraction
                                        verify_bytes = len(text_to_verify[:text_to_verify.find(wrapper_segment)].encode("utf-8"))
                                        logger.info(f"Verification: extracted content is {verify_bytes} bytes, expected {original_content_bytes}")
                                    elif actual_bytes_before < original_content_bytes:
                                        # Less content than expected - content may have been truncated
                                        logger.warning(f"Content appears truncated: {actual_bytes_before} bytes found, {original_content_bytes} expected")
                                        wrapper_end_normalized = normalized_wrapper_pos + len(wrapper_segment)
                                        text_to_verify = normalized_text[:wrapper_end_normalized]
                                    else:
                                        # Exact match - use as-is (truncate after wrapper)
                                        wrapper_end_normalized = normalized_wrapper_pos + len(wrapper_segment)
                                        text_to_verify = normalized_text[:wrapper_end_normalized]
                                        logger.info("Content length matches expected - no extraction needed")
            except Exception as e:
                logger.warning(f"Could not extract exclusion info from manifest: {e}", exc_info=True)
                # Fall back to using text up to wrapper end
                text_to_verify = request.encoded_text[:wrapper_end]
        
        decoded_metadata = UnicodeMetadata.extract_metadata(text=text_to_verify)
        
        if not decoded_metadata:
            logger.warning("No metadata found in text")
            return DecodeToolResponse(
                metadata=None,
                verification_status="Failure",
                error="No metadata found in the provided text.",
                raw_hidden_data=VerifyVerdict(
                    valid=False,
                    tampered=False,
                    reason_code="NO_METADATA",
                ),
                embeddings_found=0,
            )
        
        # Extract signer_id from metadata to do async lookup before verification
        signer_id_from_metadata = None
        if isinstance(decoded_metadata, dict):
            manifest = decoded_metadata.get("manifest", {})
            if isinstance(manifest, dict):
                signer_id_from_metadata = manifest.get("signer_id")
            if not signer_id_from_metadata:
                signer_id_from_metadata = decoded_metadata.get("signer_id")
            if not signer_id_from_metadata:
                claim_info = decoded_metadata.get("claim_generator_info", {})
                if isinstance(claim_info, dict):
                    signer_id_from_metadata = claim_info.get("signer_id")
        
        logger.info(f"Extracted signer_id from metadata: {signer_id_from_metadata}")
        
        # Pre-fetch the public key for the signer from Trust Anchor database
        # load_organization_public_key handles all cases:
        # - org_demo -> demo key
        # - user_* -> demo key
        # - org_* -> database lookup
        org_public_key = None
        if signer_id_from_metadata:
            try:
                org_public_key = await load_organization_public_key(signer_id_from_metadata, db)
                logger.info(f"Resolved key for {signer_id_from_metadata} from Trust Anchor")
            except ValueError:
                logger.warning(f"Signer {signer_id_from_metadata} not found in Trust Anchor database")
                # Fall back to demo key for known demo signer IDs
                if signer_id_from_metadata in demo_signer_ids:
                    org_public_key = public_key
            except Exception as e:
                logger.warning(f"Error looking up signer {signer_id_from_metadata}: {e}")
                if signer_id_from_metadata in demo_signer_ids:
                    org_public_key = public_key
        
        def public_key_resolver(signer_id: str):
            """Resolve public key - use pre-fetched key or fall back to demo."""
            if org_public_key and signer_id == signer_id_from_metadata:
                return org_public_key
            # Fallback for demo signer IDs
            if signer_id in demo_signer_ids:
                return public_key
            logger.warning(f"Unknown signer_id: {signer_id}")
            return None
        
        # Verify metadata signature using the extracted segment (not full pasted text)
        try:
            verification_result = UnicodeMetadata.verify_metadata(
                text=text_to_verify,
                public_key_resolver=public_key_resolver,
                return_payload_on_failure=True,
            )
            
            if isinstance(verification_result, tuple) and len(verification_result) == 3:
                signature_valid, signer_id, payload = verification_result
            elif isinstance(verification_result, dict):
                signature_valid = verification_result.get("valid", False)
                signer_id = verification_result.get("signer_id")
                payload = verification_result.get("payload", decoded_metadata)
            else:
                signature_valid = False
                signer_id = None
                payload = decoded_metadata
            
            reason_code = "VERIFIED" if signature_valid else "VERIFICATION_FAILED"

            if signer_id:
                if org_public_key and signer_id == signer_id_from_metadata:
                    signer_name = f"{signer_id} (Verified via Trust Anchor)"
                elif signer_id in demo_signer_ids:
                    signer_name = f"{signer_id} (Demo Key)"
                else:
                    signer_name = f"{signer_id} (Unknown Signer)"
            else:
                signer_name = None

            verdict = VerifyVerdict(
                valid=signature_valid,
                tampered=not signature_valid and decoded_metadata is not None,
                reason_code=reason_code,
                signer_id=signer_id,
                signer_name=signer_name,
            )

            if signature_valid:
                verification_status = "Success"
                error_msg = None
            else:
                verification_status = "Failure"
                if signer_name and "Unknown Signer" in signer_name:
                    error_msg = f"Manifest found but signer '{signer_id}' is not in our Trust Anchor database. The signature cannot be verified."
                elif signer_name:
                    # Check if we detected extra page chrome - provide helpful message
                    if content_extraction_note:
                        error_msg = (
                            f"Manifest found and signed by '{signer_name}', but verification failed. "
                            f"It appears you may have copied extra content (like page headers/footers) along with the signed text. "
                            f"Please copy only the article content, not the entire page."
                        )
                    else:
                        error_msg = f"Manifest found and signed by '{signer_name}', but the content has been modified since signing. The signature is no longer valid."
                else:
                    error_msg = "Manifest found but signature verification failed. The content may have been modified or the signer is unknown."
            
            # Build single embedding result for consistent UI display
            single_embedding = EmbeddingResult(
                index=0,
                metadata=payload if isinstance(payload, dict) else decoded_metadata,
                verification_status=verification_status,
                error=error_msg if not signature_valid else None,
                verdict=verdict,
                text_span=None,
                clean_text=None,
            )
            
            return DecodeToolResponse(
                metadata=payload if isinstance(payload, dict) else decoded_metadata,
                verification_status=verification_status,
                error=error_msg,
                raw_hidden_data=verdict,
                embeddings_found=1,
                all_embeddings=[single_embedding],
            )
            
        except Exception as e:
            logger.warning(f"Verification failed: {e}")
            return DecodeToolResponse(
                metadata=decoded_metadata if isinstance(decoded_metadata, dict) else None,
                verification_status="Error",
                error=str(e),
                raw_hidden_data=VerifyVerdict(
                    valid=False,
                    tampered=False,
                    reason_code="VERIFICATION_ERROR",
                ),
                embeddings_found=1,
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Decoding failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Decoding failed. Please try again."
        )
