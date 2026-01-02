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
    """Get or generate demo keys for public tools."""
    global _demo_private_key, _demo_public_key
    
    if _demo_private_key is not None:
        return _demo_private_key, _demo_public_key
    
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization
    
    # Try to load from PEM format first (legacy keys)
    if settings.demo_private_key_pem:
        try:
            pem_str = settings.demo_private_key_pem
            # Handle escaped newlines from environment variables
            if '\\n' in pem_str:
                pem_str = pem_str.replace('\\n', '\n')
            private_key = serialization.load_pem_private_key(pem_str.encode(), password=None)
            if isinstance(private_key, Ed25519PrivateKey):
                _demo_private_key = private_key
                _demo_public_key = _demo_private_key.public_key()
                logger.info("Loaded demo keys from PEM format")
                return _demo_private_key, _demo_public_key
        except Exception as e:
            logger.warning(f"Failed to load demo keys from PEM: {e}")
    
    # Try to load from hex format (check both DEMO_PRIVATE_KEY_HEX and SECRET_KEY)
    key_hex = settings.demo_private_key_hex or settings.secret_key
    if key_hex:
        try:
            key_bytes = bytes.fromhex(key_hex)
            _demo_private_key = Ed25519PrivateKey.from_private_bytes(key_bytes)
            _demo_public_key = _demo_private_key.public_key()
            logger.info("Loaded demo keys from hex format")
            return _demo_private_key, _demo_public_key
        except Exception as e:
            logger.warning(f"Failed to load demo keys from hex: {e}")
    
    try:
        _demo_private_key = get_demo_private_key()
        _demo_public_key = _demo_private_key.public_key()
        logger.info("Loaded demo keys from enterprise_api demo key configuration")
        return _demo_private_key, _demo_public_key
    except Exception as e:
        logger.error(f"Failed to load demo keys: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Demo keys not available"
        )


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
            
            # Build public key resolver that handles all signers
            async def resolve_public_key(signer_id: str):
                if signer_id in demo_signer_ids:
                    return public_key
                if signer_id and signer_id.startswith("user_"):
                    return public_key
                try:
                    return await load_organization_public_key(signer_id, db)
                except Exception:
                    return None
            
            # Create sync wrapper for the resolver
            resolved_keys: dict = {}
            for emb in multi_result.embeddings:
                if emb.signer_id:
                    if emb.signer_id in demo_signer_ids or (emb.signer_id and emb.signer_id.startswith("user_")):
                        resolved_keys[emb.signer_id] = public_key
                    else:
                        try:
                            resolved_keys[emb.signer_id] = await load_organization_public_key(emb.signer_id, db)
                        except Exception:
                            resolved_keys[emb.signer_id] = None
            
            def public_key_resolver(signer_id: str):
                if signer_id in resolved_keys:
                    return resolved_keys[signer_id]
                if signer_id in demo_signer_ids:
                    return public_key
                if signer_id and signer_id.startswith("user_"):
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
                all_embeddings.append(EmbeddingResult(
                    index=emb.index,
                    metadata=emb.metadata,
                    verification_status=emb.verification_status,
                    error=emb.error,
                    verdict=VerifyVerdict(
                        valid=emb.signature_valid,
                        tampered=not emb.signature_valid and emb.metadata is not None,
                        reason_code="VERIFIED" if emb.signature_valid else "VERIFICATION_FAILED",
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
                valid_count = sum(1 for e in verified_result.embeddings if e.signature_valid)
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
        import c2pa_text
        import unicodedata
        text_to_verify = request.encoded_text
        wrapper_info = None
        content_extraction_note = None
        
        if hasattr(c2pa_text, "find_wrapper_info"):
            wrapper_info = c2pa_text.find_wrapper_info(request.encoded_text)
            if wrapper_info:
                manifest_bytes, wrapper_start, wrapper_end = wrapper_info
                logger.info(f"Found wrapper at char positions [{wrapper_start}:{wrapper_end}]")
                
                # Try to extract the exclusion info from the manifest to determine
                # how much content should be before the wrapper
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
                                    expected_exclusion_start = exclusions[0].get("start", 0)
                                    
                                    # Normalize the text first (C2PA requires NFC normalization)
                                    normalized_text = unicodedata.normalize("NFC", request.encoded_text)
                                    
                                    # Find wrapper position in normalized text
                                    wrapper_segment = request.encoded_text[wrapper_start:wrapper_end]
                                    normalized_wrapper_pos = normalized_text.find(wrapper_segment)
                                    
                                    if normalized_wrapper_pos >= 0:
                                        # Calculate actual bytes before wrapper in normalized text
                                        text_before_wrapper = normalized_text[:normalized_wrapper_pos]
                                        actual_bytes_before_wrapper = len(text_before_wrapper.encode("utf-8"))
                                        
                                        logger.info(f"Exclusion in manifest: start={expected_exclusion_start}")
                                        logger.info(f"Actual bytes before wrapper: {actual_bytes_before_wrapper}")
                                        
                                        if actual_bytes_before_wrapper > expected_exclusion_start:
                                            # There's extra content before the signed segment
                                            # We need to extract text starting from the correct byte position
                                            extra_bytes = actual_bytes_before_wrapper - expected_exclusion_start
                                            logger.info(f"Detected {extra_bytes} extra bytes of page chrome")
                                            
                                            # Find the character position that corresponds to skipping extra_bytes
                                            byte_count = 0
                                            char_start = 0
                                            for i, char in enumerate(normalized_text):
                                                if byte_count >= extra_bytes:
                                                    char_start = i
                                                    break
                                                byte_count += len(char.encode("utf-8"))
                                            
                                            # Find where wrapper ends in normalized text
                                            wrapper_end_normalized = normalized_wrapper_pos + len(wrapper_segment)
                                            
                                            # Extract the signed segment
                                            text_to_verify = normalized_text[char_start:wrapper_end_normalized]
                                            content_extraction_note = f"Extracted signed segment: removed {extra_bytes} bytes of page chrome"
                                            logger.info(content_extraction_note)
                                            
                                            # Verify the extraction is correct
                                            new_bytes_before = len(text_to_verify[:text_to_verify.find(wrapper_segment)].encode("utf-8"))
                                            logger.info(f"After extraction: bytes before wrapper = {new_bytes_before}, expected = {expected_exclusion_start}")
                                        else:
                                            # No extra content, use normalized text up to wrapper end
                                            wrapper_end_normalized = normalized_wrapper_pos + len(wrapper_segment)
                                            text_to_verify = normalized_text[:wrapper_end_normalized]
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
        
        # Pre-fetch the public key for the signer
        org_public_key = None
        if signer_id_from_metadata:
            if signer_id_from_metadata in demo_signer_ids:
                org_public_key = public_key
                logger.info(f"Using demo key for demo signer {signer_id_from_metadata}")
            else:
                try:
                    org_public_key = await load_organization_public_key(signer_id_from_metadata, db)
                    logger.info(f"Found public key for signer {signer_id_from_metadata} in Trust Anchor")
                except ValueError:
                    logger.warning(f"Signer {signer_id_from_metadata} not found in Trust Anchor database")
                except Exception as e:
                    logger.warning(f"Error looking up signer {signer_id_from_metadata}: {e}")
        
        def public_key_resolver(signer_id: str):
            if org_public_key and signer_id == signer_id_from_metadata:
                return org_public_key
            if signer_id in demo_signer_ids:
                return public_key
            if signer_id.startswith("user_"):
                logger.info(f"Using demo key for user org {signer_id}")
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
            
            return DecodeToolResponse(
                metadata=payload if isinstance(payload, dict) else decoded_metadata,
                verification_status=verification_status,
                error=error_msg,
                raw_hidden_data=verdict,
                embeddings_found=1,
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
