from typing import Optional

from pydantic import BaseModel, Field


class WatermarkRequest(BaseModel):
    video_b64: str = Field(..., description="Base64-encoded video bytes")
    mime_type: str = Field(
        ...,
        description="MIME type: video/mp4, video/quicktime, video/x-matroska, video/webm",
    )
    payload: str = Field(
        ...,
        description="64-bit payload as 16-char hex string [0-9a-fA-F].",
        min_length=16,
        max_length=16,
        pattern=r"^[0-9a-fA-F]{16}$",
    )
    wsr_db: Optional[float] = Field(
        None,
        description="Watermark-to-signal ratio in dB (negative). Defaults to -30 dB.",
    )


class WatermarkResponse(BaseModel):
    watermarked_b64: str
    confidence: float
    processing_time_ms: float


class DetectRequest(BaseModel):
    video_b64: str = Field(..., description="Base64-encoded video bytes")
    mime_type: str = Field(
        ...,
        description="MIME type: video/mp4, video/quicktime, video/x-matroska, video/webm",
    )


class DetectResponse(BaseModel):
    detected: bool
    payload: Optional[str] = None
    confidence: float
    processing_time_ms: float


class HealthResponse(BaseModel):
    status: str
    version: str = "0.1.0"
