"""Pydantic schemas for Verification Service"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class SignatureVerify(BaseModel):
    """Schema for signature verification"""
    content: str = Field(..., min_length=1)
    signature: str
    public_key_pem: str


class DocumentVerify(BaseModel):
    """Schema for complete document verification"""
    document_id: str
    content: str = Field(..., min_length=1)


class TamperCheck(BaseModel):
    """Schema for tampering check"""
    document_id: str
    current_content: str


class VerificationResponse(BaseModel):
    """Schema for verification response"""
    is_valid: bool
    is_tampered: bool
    signature_valid: bool
    hash_valid: bool
    confidence_score: float
    similarity_score: Optional[float]
    signer_id: Optional[str]
    warnings: Optional[List[str]]
    verification_time_ms: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class VerificationHistory(BaseModel):
    """Schema for verification history"""
    id: str
    document_id: str
    is_valid: bool
    is_tampered: bool
    confidence_score: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class VerificationStats(BaseModel):
    """Schema for verification statistics"""
    total_verifications: int
    valid_verifications: int
    invalid_verifications: int
    tampered_documents: int
    average_confidence_score: float
    average_verification_time_ms: float


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str


class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str
