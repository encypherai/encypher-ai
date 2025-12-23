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
from app.utils.crypto_utils import load_organization_public_key

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
    
    # Try to load from settings (check both DEMO_PRIVATE_KEY_HEX and SECRET_KEY)
    key_hex = settings.demo_private_key_hex or settings.secret_key
    if key_hex:
        try:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
            key_bytes = bytes.fromhex(key_hex)
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
    Verification uses Trust Anchor lookup - checks database for org public keys.
    Falls back to demo key for demo-signed content.
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
        
        # Extract signer_id from metadata to do async lookup before verification
        signer_id_from_metadata = None
        if isinstance(decoded_metadata, dict):
            # Try multiple paths to find signer_id
            # Path 1: manifest.signer_id
            manifest = decoded_metadata.get("manifest", {})
            if isinstance(manifest, dict):
                signer_id_from_metadata = manifest.get("signer_id")
            # Path 2: direct signer_id
            if not signer_id_from_metadata:
                signer_id_from_metadata = decoded_metadata.get("signer_id")
            # Path 3: claim_generator_info.signer_id (C2PA format)
            if not signer_id_from_metadata:
                claim_info = decoded_metadata.get("claim_generator_info", {})
                if isinstance(claim_info, dict):
                    signer_id_from_metadata = claim_info.get("signer_id")
        
        logger.info(f"Extracted signer_id from metadata: {signer_id_from_metadata}")
        
        # Pre-fetch the public key for the signer (async lookup)
        # For user_ orgs, load_organization_public_key will return the demo key
        org_public_key = None
        if signer_id_from_metadata:
            # Skip pre-fetch for known demo signers (they use the demo key directly)
            if signer_id_from_metadata in (_demo_signer_id, "org_demo", "demo-signer-id", "c2pa-demo-signer-001"):
                org_public_key = public_key  # Use demo key
                logger.info(f"Using demo key for demo signer {signer_id_from_metadata}")
            else:
                try:
                    org_public_key = await load_organization_public_key(signer_id_from_metadata, db)
                    logger.info(f"Found public key for signer {signer_id_from_metadata} in Trust Anchor")
                except ValueError:
                    logger.warning(f"Signer {signer_id_from_metadata} not found in Trust Anchor database")
                except Exception as e:
                    logger.warning(f"Error looking up signer {signer_id_from_metadata}: {e}")
        
        # Define synchronous public key resolver using pre-fetched keys
        def public_key_resolver(signer_id: str):
            """Look up public key - uses pre-fetched org key or demo key."""
            # Check if we have a pre-fetched org key for this signer
            if org_public_key and signer_id == signer_id_from_metadata:
                return org_public_key
            # Fall back to demo key for demo signer IDs
            if signer_id in (_demo_signer_id, "org_demo", "demo-signer-id", "c2pa-demo-signer-001"):
                return public_key
            # For user_ orgs that weren't pre-fetched, use demo key
            if signer_id.startswith("user_"):
                logger.info(f"Using demo key for user org {signer_id}")
                return public_key
            logger.warning(f"Unknown signer_id: {signer_id}")
            return None
        
        # Verify metadata signature
        try:
            verification_result = UnicodeMetadata.verify_metadata(
                text=request.encoded_text,
                public_key_resolver=public_key_resolver,
                return_payload_on_failure=True,
            )
            
            # Parse verification result
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
            
            # Core library handles hard binding verification automatically
            # signature_valid = False means either signature is invalid OR hard binding check failed
            reason_code = "VERIFIED" if signature_valid else "VERIFICATION_FAILED"

            # Determine signer name based on whether we found an org key
            if signer_id:
                if org_public_key and signer_id == signer_id_from_metadata:
                    # Verified via Trust Anchor (database lookup)
                    signer_name = f"{signer_id} (Verified via Trust Anchor)"
                elif signer_id in (_demo_signer_id, "org_demo", "demo-signer-id", "c2pa-demo-signer-001"):
                    signer_name = f"{signer_id} (Demo Key)"
                else:
                    signer_name = f"{signer_id} (Unknown Signer)"
            else:
                signer_name = None

            # Build verdict
            verdict = VerifyVerdict(
                valid=signature_valid,
                tampered=not signature_valid and decoded_metadata is not None,
                reason_code=reason_code,
                signer_id=signer_id,
                signer_name=signer_name,
            )

            # Determine verification status with descriptive messaging
            if signature_valid:
                verification_status = "Success"
                error_msg = None
            else:
                verification_status = "Failure"
                # Provide more descriptive error based on what we found
                if signer_name and "Unknown Signer" in signer_name:
                    error_msg = f"Manifest found but signer '{signer_id}' is not in our Trust Anchor database. The signature cannot be verified."
                elif signer_name:
                    error_msg = f"Manifest found and signed by '{signer_name}', but the content has been modified since signing. The signature is no longer valid."
                else:
                    error_msg = "Manifest found but signature verification failed. The content may have been modified or the signer is unknown."
            
            return DecodeToolResponse(
                metadata=payload if isinstance(payload, dict) else decoded_metadata,
                verification_status=verification_status,
                error=error_msg,
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
