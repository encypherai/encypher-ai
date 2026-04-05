"""Pydantic schemas for rich article and image verification."""

from typing import List, Optional

from pydantic import BaseModel


class RichVerifyRequest(BaseModel):
    document_id: str


class ImageVerifyRequest(BaseModel):
    image_data: str  # base64-encoded image bytes
    mime_type: str = "image/jpeg"


class ImageVerificationResult(BaseModel):
    image_id: Optional[str] = None
    filename: Optional[str] = None
    valid: bool
    c2pa_manifest_valid: bool
    hash_matches: bool
    trustmark_valid: Optional[bool] = None  # None = not checked
    c2pa_instance_id: Optional[str] = None
    signer: Optional[str] = None
    signed_at: Optional[str] = None
    cryptographically_verified: Optional[bool] = None
    historically_signed_by_us: Optional[bool] = None
    overall_status: Optional[str] = None
    error: Optional[str] = None


class TextVerificationResult(BaseModel):
    valid: bool
    total_segments: Optional[int] = None
    tampered_segments: List[int] = []
    merkle_root_verified: Optional[bool] = None
    error: Optional[str] = None


class SignerIdentity(BaseModel):
    organization_id: Optional[str] = None
    organization_name: Optional[str] = None
    trust_level: str = "unknown"


class RichVerifyResponse(BaseModel):
    success: bool = True
    valid: bool
    verified_at: str
    document_id: str
    content_type: str = "rich_article"
    text_verification: Optional[TextVerificationResult] = None
    image_verifications: List[ImageVerificationResult] = []
    composite_manifest_valid: bool
    all_ingredients_verified: bool
    cryptographically_verified: Optional[bool] = None
    historically_signed_by_us: Optional[bool] = None
    overall_status: Optional[str] = None
    signer_identity: Optional[SignerIdentity] = None
    error: Optional[str] = None
    correlation_id: str


class ImageVerifyResponse(BaseModel):
    success: bool = True
    valid: bool
    verified_at: str
    c2pa_manifest: Optional[dict] = None
    image_id: Optional[str] = None
    document_id: Optional[str] = None
    hash: Optional[str] = None
    phash: Optional[str] = None
    cryptographically_verified: Optional[bool] = None
    db_matched: Optional[bool] = None
    historically_signed_by_us: Optional[bool] = None
    overall_status: Optional[str] = None
    # TrustMark watermark detection results
    watermark_detected: Optional[bool] = None
    watermark_payload: Optional[str] = None
    watermark_confidence: Optional[float] = None
    error: Optional[str] = None
    correlation_id: str
