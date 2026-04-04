from typing import Optional

from pydantic import BaseModel, Field


class AudioWatermarkRequest(BaseModel):
    audio_b64: str = Field(..., description="Base64-encoded audio bytes")
    mime_type: str = Field(
        ...,
        description="MIME type: audio/wav, audio/mpeg, audio/mp4, audio/x-m4a",
    )
    payload: str = Field(
        ...,
        description="64-bit payload as 16-char hex string [0-9a-fA-F].",
        min_length=16,
        max_length=16,
        pattern=r"^[0-9a-fA-F]{16}$",
    )
    snr_db: Optional[float] = Field(
        None,
        description="SNR threshold in dB (negative). Defaults to -20 for speech. Use -30 for music.",
    )


class AudioWatermarkResponse(BaseModel):
    watermarked_b64: str
    payload: str
    confidence: float
    processing_time_ms: float


class AudioDetectRequest(BaseModel):
    audio_b64: str = Field(..., description="Base64-encoded audio bytes")
    mime_type: str = Field(
        ...,
        description="MIME type: audio/wav, audio/mpeg, audio/mp4, audio/x-m4a",
    )


class AudioDetectResponse(BaseModel):
    detected: bool
    payload: Optional[str] = None
    confidence: float
    processing_time_ms: float


class HealthResponse(BaseModel):
    status: str
    version: str = "0.1.0"
