"""
Robust Fingerprint Mode Schemas (TEAM_044).

These schemas define request/response models for keyed fingerprint
encoding and detection, providing resilience against content modification.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class FingerprintEncodeRequest(BaseModel):
    """
    Request to encode a robust fingerprint into text.
    
    Fingerprints use secret-seeded placement of invisible markers
    that survive text modifications like paraphrasing or truncation.
    """
    
    document_id: str = Field(..., description="Unique document identifier")
    text: str = Field(..., description="Text to fingerprint", min_length=10)
    fingerprint_density: float = Field(
        default=0.1,
        description="Density of fingerprint markers (0.01-0.5)",
        ge=0.01,
        le=0.5,
    )
    fingerprint_key: Optional[str] = Field(
        default=None,
        description="Optional custom fingerprint key (auto-generated if not provided)"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional metadata to associate with fingerprint"
    )


class FingerprintEncodeResponse(BaseModel):
    """Response after encoding a fingerprint."""
    
    success: bool = Field(..., description="Whether encoding succeeded")
    document_id: str = Field(..., description="Document identifier")
    fingerprint_id: str = Field(..., description="Unique fingerprint identifier")
    fingerprinted_text: str = Field(..., description="Text with embedded fingerprint")
    fingerprint_key_hash: str = Field(..., description="Hash of fingerprint key (for verification)")
    markers_embedded: int = Field(..., description="Number of markers embedded")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    message: str = Field(..., description="Status message")


class FingerprintDetectRequest(BaseModel):
    """
    Request to detect a fingerprint in text.
    
    Detection uses score-based matching with confidence threshold
    to identify fingerprinted content even after modifications.
    """
    
    text: str = Field(..., description="Text to scan for fingerprint", min_length=10)
    fingerprint_key: Optional[str] = Field(
        default=None,
        description="Fingerprint key to search for (searches all if not provided)"
    )
    confidence_threshold: float = Field(
        default=0.6,
        description="Minimum confidence threshold for detection (0.0-1.0)",
        ge=0.0,
        le=1.0,
    )
    return_positions: bool = Field(
        default=False,
        description="Return positions of detected markers"
    )


class FingerprintMatch(BaseModel):
    """Details of a detected fingerprint match."""
    
    fingerprint_id: str = Field(..., description="Matched fingerprint ID")
    document_id: str = Field(..., description="Source document ID")
    organization_id: str = Field(..., description="Source organization ID")
    confidence: float = Field(..., description="Detection confidence (0-1)", ge=0, le=1)
    markers_found: int = Field(..., description="Number of markers detected")
    markers_expected: int = Field(..., description="Number of markers expected")
    marker_positions: Optional[List[int]] = Field(
        default=None,
        description="Positions of detected markers (if requested)"
    )
    created_at: datetime = Field(..., description="When fingerprint was created")


class FingerprintDetectResponse(BaseModel):
    """Response after fingerprint detection."""
    
    success: bool = Field(..., description="Whether detection succeeded")
    fingerprint_detected: bool = Field(..., description="Whether a fingerprint was detected")
    matches: List[FingerprintMatch] = Field(
        default_factory=list,
        description="List of fingerprint matches"
    )
    best_match: Optional[FingerprintMatch] = Field(
        None,
        description="Best matching fingerprint (highest confidence)"
    )
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    message: str = Field(..., description="Status message")
