"""
Pydantic schemas for batch signing and verification endpoints.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

from app.models.response_models import ErrorDetail, VerifyVerdict
from app.schemas.sign_schemas import validate_text_content

BatchMode = Literal["c2pa", "embeddings"]
SegmentationLevel = Literal["document", "paragraph", "sentence"]
BatchItemStatusLiteral = Literal["ok", "error", "skipped"]
BatchStatusLiteral = Literal["pending", "running", "completed", "failed", "canceled"]


class BatchItemPayload(BaseModel):
    """Single document payload within a batch request."""

    document_id: str = Field(..., description="Unique document identifier", min_length=1, max_length=255)
    text: str = Field(..., description="Raw document text to process", min_length=1)

    @field_validator("text")
    @classmethod
    def validate_text_is_not_binary(cls, v: str) -> str:
        return validate_text_content(v)

    title: Optional[str] = Field(None, description="Optional title metadata", max_length=255)
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional metadata dictionary forwarded to signing pipeline",
    )


class BatchRequestBase(BaseModel):
    """Shared fields between batch sign and verify requests."""

    mode: BatchMode = Field(..., description="Processing mode: 'c2pa' or 'embeddings'")
    segmentation_level: Optional[SegmentationLevel] = Field(
        "sentence",
        description="Segmentation level (embeddings mode only)",
    )
    idempotency_key: str = Field(
        ...,
        description="Caller-supplied key used to deduplicate retries",
        min_length=8,
        max_length=128,
    )
    items: List[BatchItemPayload] = Field(
        ...,
        description="Documents to process (max 100)",
        min_length=1,
        max_length=100,
    )
    fail_fast: bool = Field(
        False,
        description="Abort remaining items upon the first error when set to true",
    )


class BatchSignRequest(BatchRequestBase):
    """Batch signing request."""

    pass


class BatchVerifyRequest(BatchRequestBase):
    """Batch verification request (shares schema for now)."""

    pass


class BatchItemResult(BaseModel):
    """Per-item response object emitted in batch responses."""

    document_id: str = Field(..., description="Document identifier from request")
    status: BatchItemStatusLiteral = Field(..., description="Processing outcome for the document")
    signed_text: Optional[str] = Field(
        None,
        description="Signed text output (C2PA mode)",
    )
    embedded_content: Optional[str] = Field(
        None,
        description="Document containing invisible embeddings (embeddings mode)",
    )
    verdict: Optional[VerifyVerdict] = Field(
        None,
        description="Verification verdict (verify mode)",
    )
    error_code: Optional[str] = Field(None, description="Error code when status is error")
    error_message: Optional[str] = Field(None, description="Human readable error message")
    statistics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Timing and segmentation statistics for the item",
    )


class BatchSummary(BaseModel):
    """Aggregated stats for the batch."""

    total_items: int = Field(..., description="Total number of documents in the batch")
    success_count: int = Field(..., description="How many items succeeded")
    failure_count: int = Field(..., description="How many items failed")
    mode: BatchMode = Field(..., description="Batch mode")
    status: BatchStatusLiteral = Field(
        ...,
        description="Batch lifecycle status",
    )
    duration_ms: int = Field(..., description="Total processing time for the batch")
    started_at: Optional[str] = Field(None, description="ISO timestamp when processing began")
    completed_at: Optional[str] = Field(None, description="ISO timestamp when processing finished")


class BatchResponseData(BaseModel):
    """Top-level data payload for batch responses."""

    results: List[BatchItemResult] = Field(..., description="Per-item results")
    summary: BatchSummary = Field(..., description="Aggregate stats for the batch")


class BatchResponseEnvelope(BaseModel):
    """Envelope returned by batch endpoints."""

    success: bool = Field(..., description="Indicates whether the batch request succeeded")
    batch_id: str = Field(..., description="Batch request identifier")
    data: Optional[BatchResponseData] = Field(None, description="Result payload when success is true")
    error: Optional[ErrorDetail] = Field(None, description="Error payload when success is false")
    correlation_id: str = Field(..., description="Request correlation identifier for tracing")
