"""
Pydantic schemas for Merkle tree API endpoints.

These schemas define request/response models for the Enterprise API.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, validator


# ============================================================================
# Document Encoding Schemas
# ============================================================================

class DocumentEncodeRequest(BaseModel):
    """Request schema for encoding a document into Merkle trees."""
    
    document_id: str = Field(
        ...,
        description="Unique identifier for the document",
        min_length=1,
        max_length=255,
        example="doc_2024_article_001"
    )
    text: str = Field(
        ...,
        description="Document text content to encode",
        min_length=1,
        example="This is the first sentence. This is the second sentence."
    )
    segmentation_levels: List[str] = Field(
        default=["sentence"],
        description="Segmentation levels to encode (word/sentence/paragraph/section)",
        example=["sentence", "paragraph"]
    )
    include_words: bool = Field(
        default=False,
        description="Whether to include word-level segmentation"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional document metadata (title, author, etc.)",
        example={"title": "My Document", "author": "John Doe", "date": "2024-10-28"}
    )
    
    @validator('segmentation_levels')
    def validate_segmentation_levels(cls, v):
        """Validate segmentation levels."""
        valid_levels = {'word', 'sentence', 'paragraph', 'section'}
        for level in v:
            if level not in valid_levels:
                raise ValueError(f"Invalid segmentation level: {level}. Must be one of {valid_levels}")
        return v
    
    @validator('text')
    def validate_text_length(cls, v):
        """Validate text is not too long."""
        max_length = 10_000_000  # 10MB of text
        if len(v) > max_length:
            raise ValueError(f"Text too long. Maximum {max_length} characters allowed.")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "document_id": "doc_2024_article_001",
                "text": "The quick brown fox jumps over the lazy dog. This is a test document for Merkle tree encoding.",
                "segmentation_levels": ["sentence", "paragraph"],
                "include_words": False,
                "metadata": {
                    "title": "Test Article",
                    "author": "Jane Smith",
                    "date": "2024-10-28"
                }
            }
        }


class MerkleRootResponse(BaseModel):
    """Response schema for a single Merkle root."""
    
    root_id: UUID = Field(..., description="Unique identifier for the Merkle root")
    document_id: str = Field(..., description="Document identifier")
    root_hash: str = Field(..., description="SHA-256 hash of the Merkle tree root")
    tree_depth: int = Field(..., description="Height of the Merkle tree")
    total_leaves: int = Field(..., description="Number of leaf nodes in the tree")
    segmentation_level: str = Field(..., description="Segmentation level (word/sentence/paragraph/section)")
    created_at: datetime = Field(..., description="Timestamp when the root was created")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Document metadata")
    
    class Config:
        from_attributes = True  # Pydantic v2
        schema_extra = {
            "example": {
                "root_id": "550e8400-e29b-41d4-a716-446655440000",
                "document_id": "doc_2024_article_001",
                "root_hash": "a" * 64,
                "tree_depth": 5,
                "total_leaves": 32,
                "segmentation_level": "sentence",
                "created_at": "2024-10-28T12:00:00Z",
                "metadata": {"title": "Test Article"}
            }
        }


class DocumentEncodeResponse(BaseModel):
    """Response schema for document encoding."""
    
    success: bool = Field(..., description="Whether encoding was successful")
    message: str = Field(..., description="Success or error message")
    document_id: str = Field(..., description="Document identifier")
    organization_id: str = Field(..., description="Organization identifier")
    roots: Dict[str, MerkleRootResponse] = Field(
        ...,
        description="Dictionary mapping segmentation level to Merkle root"
    )
    total_segments: Dict[str, int] = Field(
        ...,
        description="Number of segments at each level"
    )
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Document encoded successfully",
                "document_id": "doc_2024_article_001",
                "organization_id": "org_enterprise_001",
                "roots": {
                    "sentence": {
                        "root_id": "550e8400-e29b-41d4-a716-446655440000",
                        "document_id": "doc_2024_article_001",
                        "root_hash": "a" * 64,
                        "tree_depth": 5,
                        "total_leaves": 32,
                        "segmentation_level": "sentence",
                        "created_at": "2024-10-28T12:00:00Z",
                        "metadata": {"title": "Test Article"}
                    }
                },
                "total_segments": {
                    "sentence": 32,
                    "paragraph": 8
                },
                "processing_time_ms": 125.5
            }
        }


# ============================================================================
# Source Attribution Schemas
# ============================================================================

class SourceAttributionRequest(BaseModel):
    """Request schema for finding source documents."""
    
    text_segment: str = Field(
        ...,
        description="Text segment to search for",
        min_length=1,
        example="This is a sentence to find."
    )
    segmentation_level: str = Field(
        default="sentence",
        description="Segmentation level to search at",
        example="sentence"
    )
    normalize: bool = Field(
        default=True,
        description="Whether to normalize text before hashing"
    )
    include_proof: bool = Field(
        default=False,
        description="Whether to include Merkle proof in response"
    )
    
    @validator('segmentation_level')
    def validate_level(cls, v):
        """Validate segmentation level."""
        valid_levels = {'word', 'sentence', 'paragraph', 'section'}
        if v not in valid_levels:
            raise ValueError(f"Invalid segmentation level: {v}")
        return v


class SourceMatch(BaseModel):
    """Schema for a single source match."""
    
    document_id: str = Field(..., description="Source document identifier")
    organization_id: str = Field(..., description="Organization that owns the document")
    root_hash: str = Field(..., description="Merkle root hash")
    segmentation_level: str = Field(..., description="Segmentation level")
    matched_hash: str = Field(..., description="Hash that matched")
    text_content: Optional[str] = Field(None, description="Original text content")
    confidence: float = Field(..., description="Confidence score (0-1)", ge=0, le=1)


class SourceAttributionResponse(BaseModel):
    """Response schema for source attribution."""
    
    success: bool = Field(..., description="Whether search was successful")
    query_hash: str = Field(..., description="Hash of the queried text segment")
    matches_found: int = Field(..., description="Number of matching sources found")
    sources: List[SourceMatch] = Field(..., description="List of matching sources")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


# ============================================================================
# Plagiarism Detection Schemas
# ============================================================================

class PlagiarismDetectionRequest(BaseModel):
    """Request schema for plagiarism detection."""
    
    target_text: str = Field(
        ...,
        description="Text to check for plagiarism",
        min_length=1
    )
    target_document_id: Optional[str] = Field(
        None,
        description="Optional identifier for the target document"
    )
    segmentation_level: str = Field(
        default="sentence",
        description="Segmentation level to analyze"
    )
    include_heat_map: bool = Field(
        default=True,
        description="Whether to generate heat map visualization data"
    )
    min_match_percentage: float = Field(
        default=0.0,
        description="Minimum match percentage to include in results",
        ge=0,
        le=100
    )
    
    @validator('segmentation_level')
    def validate_level(cls, v):
        """Validate segmentation level."""
        valid_levels = {'word', 'sentence', 'paragraph', 'section'}
        if v not in valid_levels:
            raise ValueError(f"Invalid segmentation level: {v}")
        return v


class SourceDocumentMatch(BaseModel):
    """Schema for a source document match in plagiarism report."""
    
    document_id: str
    organization_id: str
    segmentation_level: str
    matched_segments: int
    total_leaves: int
    match_percentage: float
    confidence_score: float
    doc_metadata: Optional[Dict[str, Any]] = None


class HeatMapData(BaseModel):
    """Schema for heat map visualization data."""
    
    positions: List[Dict[str, Any]]
    total_segments: int
    matched_segments: int
    match_percentage: float


class PlagiarismDetectionResponse(BaseModel):
    """Response schema for plagiarism detection."""
    
    success: bool
    report_id: UUID
    target_document_id: Optional[str]
    total_segments: int
    matched_segments: int
    overall_match_percentage: float
    source_documents: List[SourceDocumentMatch]
    heat_map_data: Optional[HeatMapData]
    processing_time_ms: float
    scan_timestamp: datetime


# ============================================================================
# Error Schemas
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response schema."""
    
    success: bool = Field(False, description="Always false for errors")
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    
    class Config:
        schema_extra = {
            "example": {
                "success": False,
                "error": "ValidationError",
                "message": "Invalid segmentation level provided",
                "details": {"field": "segmentation_level", "value": "invalid"}
            }
        }
