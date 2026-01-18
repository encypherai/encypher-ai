"""
Pydantic schemas for Encoding Service
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


# Document Schemas
class DocumentSign(BaseModel):
    """Schema for signing a document"""

    content: str = Field(..., min_length=1)
    metadata: Optional[Dict[str, Any]] = None
    format: str = Field(default="text", pattern="^(text|json|markdown)$")
    api_key: str = Field(..., description="API key for signing")


class DocumentEmbed(BaseModel):
    """Schema for embedding metadata"""

    content: str = Field(..., min_length=1)
    metadata: Dict[str, Any] = Field(..., min_length=1)
    format: str = Field(default="text", pattern="^(text|json|markdown)$")


class SignedDocumentResponse(BaseModel):
    """Schema for signed document response"""

    document_id: str
    encoded_content: str
    signature: str
    content_hash: str
    manifest: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentInfo(BaseModel):
    """Schema for document information"""

    id: str
    document_id: str
    content_hash: str
    signature: str
    signer_id: str
    format: str
    encoding_method: str
    is_active: bool
    created_at: datetime
    metadata: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class ManifestResponse(BaseModel):
    """Schema for manifest response"""

    manifest_id: str
    version: str
    content_hash: str
    signature: str
    algorithm: str
    hash_algorithm: str
    metadata: Dict[str, Any]


# Operation Schemas
class OperationStats(BaseModel):
    """Schema for operation statistics"""

    total_operations: int
    successful_operations: int
    failed_operations: int
    average_processing_time_ms: float
    total_content_size_bytes: int


# Response Schemas
class MessageResponse(BaseModel):
    """Generic message response"""

    message: str


class ErrorResponse(BaseModel):
    """Error response schema"""

    detail: str
