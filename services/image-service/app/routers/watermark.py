import base64
import logging
import time

from fastapi import APIRouter, HTTPException, Request, status

from app.schemas.watermark_schemas import (
    DetectRequest,
    DetectResponse,
    WatermarkRequest,
    WatermarkResponse,
)
from app.services.trustmark_service import ServiceUnavailableError

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/watermark", response_model=WatermarkResponse)
async def watermark_image(payload: WatermarkRequest, request: Request) -> WatermarkResponse:
    """Embed a TrustMark neural watermark into an image.

    Requires TrustMark model loaded at startup. Returns 503 when model
    is not available (trustmark/torch not installed in this environment).
    """
    svc = getattr(request.app.state, "trustmark_service", None)
    if svc is None or not svc.is_available:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="TrustMark model not available",
        )

    try:
        image_bytes = base64.b64decode(payload.image_b64, validate=True)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 image data")

    t0 = time.perf_counter()
    try:
        watermarked_bytes, confidence = svc.encode(image_bytes, payload.mime_type, payload.message_bits)
    except ServiceUnavailableError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except Exception as e:
        logger.exception("Watermark encode failed: %s", e)
        raise HTTPException(status_code=500, detail="Watermark encoding failed")

    elapsed_ms = (time.perf_counter() - t0) * 1000
    return WatermarkResponse(
        watermarked_b64=base64.b64encode(watermarked_bytes).decode(),
        message_bits=payload.message_bits,
        confidence=confidence,
        processing_time_ms=round(elapsed_ms, 2),
    )


@router.post("/detect", response_model=DetectResponse)
async def detect_watermark(payload: DetectRequest, request: Request) -> DetectResponse:
    """Detect a TrustMark neural watermark in an image.

    Returns 503 when model is not available.
    """
    svc = getattr(request.app.state, "trustmark_service", None)
    if svc is None or not svc.is_available:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="TrustMark model not available",
        )

    try:
        image_bytes = base64.b64decode(payload.image_b64, validate=True)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 image data")

    t0 = time.perf_counter()
    try:
        detected, msg_hex, confidence = svc.decode(image_bytes)
    except ServiceUnavailableError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except Exception as e:
        logger.exception("Watermark detect failed: %s", e)
        raise HTTPException(status_code=500, detail="Watermark detection failed")

    elapsed_ms = (time.perf_counter() - t0) * 1000
    return DetectResponse(
        detected=detected,
        message_bits=msg_hex,
        confidence=confidence,
        processing_time_ms=round(elapsed_ms, 2),
    )
