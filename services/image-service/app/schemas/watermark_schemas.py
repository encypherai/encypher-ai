from typing import Optional
from pydantic import BaseModel, Field


class WatermarkRequest(BaseModel):
    image_b64: str = Field(..., description="Base64-encoded image bytes")
    mime_type: str = Field(..., description="MIME type: image/jpeg, image/png, image/webp")
    message_bits: str = Field(
        ...,
        description=(
            "100-bit message as 26-char hex string "
            "(100 bits = 12.5 bytes, use 13 bytes = 26 hex chars, padded). "
            "Must be exactly 26 hex chars."
        ),
        min_length=26,
        max_length=26,
    )


class WatermarkResponse(BaseModel):
    watermarked_b64: str
    message_bits: str
    confidence: float
    processing_time_ms: float


class DetectRequest(BaseModel):
    image_b64: str
    mime_type: str


class DetectResponse(BaseModel):
    detected: bool
    message_bits: Optional[str] = None
    confidence: float
    processing_time_ms: float


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    version: str = "0.1.0"
