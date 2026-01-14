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
    text_span: Optional[tuple[int, int]] = Field(None, description="Start and end UTF-8 byte offsets of this embedding in the input text")
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

@router.post("/encode", response_model=EncodeToolResponse, include_in_schema=False)
async def encode_text(request: EncodeToolRequest) -> EncodeToolResponse:
    """
    Encode text with embedded metadata using the demo key.
    
    This is a public endpoint for interactive demos and evaluation.
    """
    logger.info("Public tools /tools/encode called (deprecated)")
    _ = request
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="Deprecated endpoint. Use /api/v1/sign/advanced (authenticated) instead.",
    )


@router.post("/decode", response_model=DecodeToolResponse, include_in_schema=False)
async def decode_text(
    request: DecodeToolRequest,
    db: AsyncSession = Depends(get_db),
) -> DecodeToolResponse:
    """
    Decode and verify text containing embedded metadata.
    
    This is a public endpoint for interactive demos and evaluation.
    If multiple embeddings are present, results are returned per embedding.
    Verification is performed when the corresponding signer public key can be resolved.
    """
    logger.info("Public tools /tools/decode called (deprecated)")
    _ = request
    _ = db
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="Deprecated endpoint. Use /api/v1/verify instead.",
    )
