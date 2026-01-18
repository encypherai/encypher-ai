"""Schemas for streaming endpoints."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class StreamSignRequest(BaseModel):
    """Request payload for streaming signing run."""

    text: str = Field(..., description="Content to sign while streaming progress")
    document_id: Optional[str] = Field(None, description="Optional document identifier")
    document_title: Optional[str] = Field(None, description="Optional title")
    document_type: str = Field("article", description="Document type metadata")
    run_id: Optional[str] = Field(None, description="Client-supplied run identifier for retries")


# === Streaming Merkle Tree Construction (TEAM_044 - Patent FIG. 5) ===


class StreamMerkleStartRequest(BaseModel):
    """
    Request to start a streaming Merkle tree construction session.

    Patent Reference: FIG. 5 - Streaming Merkle Tree Construction

    This initiates a session that allows segments to be added incrementally,
    ideal for real-time LLM output signing where content is generated token-by-token.
    """

    document_id: str = Field(..., description="Unique document identifier")
    segmentation_level: str = Field(default="sentence", description="Segmentation level: sentence, paragraph, section")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional document metadata (title, author, etc.)")
    buffer_size: int = Field(default=100, description="Maximum number of segments to buffer before forcing a flush", ge=1, le=10000)
    auto_finalize_timeout_seconds: int = Field(
        default=300, description="Timeout in seconds after which session auto-finalizes if idle", ge=30, le=3600
    )

    @validator("segmentation_level")
    def validate_segmentation_level(cls, v):
        allowed = ["sentence", "paragraph", "section"]
        if v not in allowed:
            raise ValueError(f"Segmentation level must be one of: {', '.join(allowed)}")
        return v


class StreamMerkleStartResponse(BaseModel):
    """Response after starting a streaming Merkle session."""

    success: bool = Field(..., description="Whether session was created successfully")
    session_id: str = Field(..., description="Unique session identifier for subsequent calls")
    document_id: str = Field(..., description="Document identifier")
    expires_at: datetime = Field(..., description="When the session will expire if idle")
    buffer_size: int = Field(..., description="Maximum buffer size before auto-flush")
    message: str = Field(..., description="Status message")


class StreamMerkleSegmentRequest(BaseModel):
    """
    Request to add a segment to an active streaming Merkle session.

    Segments are buffered and combined into the Merkle tree incrementally.
    The tree is constructed using a bounded buffer approach for memory efficiency.
    """

    session_id: str = Field(..., description="Session ID from StreamMerkleStartResponse")
    segment_text: str = Field(..., description="Text segment to add to the tree")
    segment_index: Optional[int] = Field(default=None, description="Optional explicit segment index (auto-incremented if not provided)")
    is_final: bool = Field(default=False, description="If true, this is the last segment and session should finalize")
    flush_buffer: bool = Field(default=False, description="If true, flush the current buffer to compute intermediate hashes")


class StreamMerkleSegmentResponse(BaseModel):
    """Response after adding a segment to the streaming Merkle tree."""

    success: bool = Field(..., description="Whether segment was added successfully")
    session_id: str = Field(..., description="Session identifier")
    segment_index: int = Field(..., description="Index of the added segment")
    segment_hash: str = Field(..., description="SHA-256 hash of the segment")
    buffer_count: int = Field(..., description="Current number of segments in buffer")
    total_segments: int = Field(..., description="Total segments added to session")
    intermediate_root: Optional[str] = Field(default=None, description="Intermediate root hash (available after flush)")
    message: str = Field(..., description="Status message")


class StreamMerkleFinalizeRequest(BaseModel):
    """
    Request to finalize a streaming Merkle session and compute the final root.

    This completes the tree construction, computes the final root hash,
    and optionally embeds a C2PA manifest into the full document.
    """

    session_id: str = Field(..., description="Session ID to finalize")
    embed_manifest: bool = Field(default=True, description="Whether to embed C2PA manifest into the final document")
    manifest_mode: str = Field(default="full", description="Manifest mode: full, lightweight_uuid, hybrid")
    action: str = Field(default="c2pa.created", description="C2PA action type: c2pa.created or c2pa.edited")

    @validator("manifest_mode")
    def validate_manifest_mode(cls, v):
        allowed = ["full", "lightweight_uuid", "hybrid"]
        if v not in allowed:
            raise ValueError(f"Manifest mode must be one of: {', '.join(allowed)}")
        return v


class StreamMerkleFinalizeResponse(BaseModel):
    """Response after finalizing a streaming Merkle session."""

    success: bool = Field(..., description="Whether finalization was successful")
    session_id: str = Field(..., description="Session identifier")
    document_id: str = Field(..., description="Document identifier")
    root_hash: str = Field(..., description="Final Merkle root hash")
    tree_depth: int = Field(..., description="Depth of the Merkle tree")
    total_segments: int = Field(..., description="Total number of segments in tree")
    embedded_content: Optional[str] = Field(default=None, description="Full document with embedded manifest (if embed_manifest=true)")
    instance_id: Optional[str] = Field(default=None, description="C2PA manifest instance ID (if embedded)")
    processing_time_ms: float = Field(..., description="Total processing time in milliseconds")
    message: str = Field(..., description="Status message")


class StreamMerkleStatusRequest(BaseModel):
    """Request to check status of a streaming Merkle session."""

    session_id: str = Field(..., description="Session ID to check")


class StreamMerkleStatusResponse(BaseModel):
    """Response with streaming Merkle session status."""

    success: bool = Field(..., description="Whether status check was successful")
    session_id: str = Field(..., description="Session identifier")
    document_id: str = Field(..., description="Document identifier")
    status: str = Field(..., description="Session status: active, finalized, expired")
    total_segments: int = Field(..., description="Total segments added")
    buffer_count: int = Field(..., description="Segments currently in buffer")
    intermediate_root: Optional[str] = Field(default=None, description="Current intermediate root hash")
    created_at: datetime = Field(..., description="When session was created")
    expires_at: datetime = Field(..., description="When session will expire")
    last_activity: datetime = Field(..., description="Last activity timestamp")
