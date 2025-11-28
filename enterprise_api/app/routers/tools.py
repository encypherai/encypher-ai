"""
Tools router for public encode/decode demo endpoints.

These endpoints use a demo key for the public website tools,
allowing users to try encoding/decoding without authentication.
"""
import logging
from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.constants import MetadataTarget

from app.config import settings

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


class DecodeToolResponse(BaseModel):
    """Response model for decoding."""
    
    metadata: Optional[Dict[str, Any]] = None
    verification_status: Literal["Success", "Failure", "Key Not Found", "Not Attempted", "Error"] = "Not Attempted"
    error: Optional[str] = None
    raw_hidden_data: Optional[VerifyVerdict] = None


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
    
    # Try to load from settings
    if settings.demo_private_key_hex:
        try:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
            key_bytes = bytes.fromhex(settings.demo_private_key_hex)
            _demo_private_key = Ed25519PrivateKey.from_private_bytes(key_bytes)
            _demo_public_key = _demo_private_key.public_key()
            logger.info("Loaded demo keys from environment")
            return _demo_private_key, _demo_public_key
        except Exception as e:
            logger.warning(f"Failed to load demo keys from env: {e}")
    
    # Generate ephemeral keys for demo
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        _demo_private_key = Ed25519PrivateKey.generate()
        _demo_public_key = _demo_private_key.public_key()
        logger.info("Generated ephemeral demo keys")
        return _demo_private_key, _demo_public_key
    except Exception as e:
        logger.error(f"Failed to generate demo keys: {e}")
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
        
        # Build actions for C2PA format
        actions = []
        if request.ai_info:
            actions.append({
                "action": "ai",
                "ai_info": request.ai_info
            })
        if custom_metadata:
            actions.append({
                "action": "custom",
                "custom_data": custom_metadata
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
        
        return EncodeToolResponse(
            encoded_text=encoded_text,
            metadata={
                "format": metadata_format,
                "signer_id": _demo_signer_id,
                "target": request.target,
                "custom_metadata": custom_metadata,
            },
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
async def decode_text(request: DecodeToolRequest) -> DecodeToolResponse:
    """
    Decode and verify text containing embedded metadata.
    
    This is a public endpoint for the website demo tool.
    Verification uses the demo public key.
    """
    logger.info("Decode request received")
    
    try:
        _, public_key = _get_demo_keys()
        
        # Extract metadata
        decoded_metadata = UnicodeMetadata.extract_metadata(text=request.encoded_text)
        
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
            )
        
        # Define public key resolver
        def public_key_resolver(signer_id: str):
            # Accept demo signer IDs
            if signer_id in (_demo_signer_id, "org_demo", "c2pa-demo-signer-001"):
                return public_key
            logger.warning(f"Unknown signer_id: {signer_id}")
            return None
        
        # Verify metadata
        try:
            verification_result = UnicodeMetadata.verify_metadata(
                text=request.encoded_text,
                public_key_resolver=public_key_resolver,
                return_payload_on_failure=True,
            )
            
            # Parse verification result
            if isinstance(verification_result, tuple) and len(verification_result) == 3:
                is_valid, signer_id, payload = verification_result
            elif isinstance(verification_result, dict):
                is_valid = verification_result.get("valid", False)
                signer_id = verification_result.get("signer_id")
                payload = verification_result.get("payload", decoded_metadata)
            else:
                is_valid = False
                signer_id = None
                payload = decoded_metadata
            
            # Build verdict
            verdict = VerifyVerdict(
                valid=is_valid,
                tampered=not is_valid and decoded_metadata is not None,
                reason_code="OK" if is_valid else "SIGNATURE_INVALID",
                signer_id=signer_id,
                signer_name=f"{signer_id} (Demo Key)" if signer_id else None,
            )
            
            return DecodeToolResponse(
                metadata=payload if isinstance(payload, dict) else decoded_metadata,
                verification_status="Success" if is_valid else "Failure",
                error=None if is_valid else "Signature verification failed",
                raw_hidden_data=verdict,
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
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Decoding failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Decoding failed. Please try again."
        )
