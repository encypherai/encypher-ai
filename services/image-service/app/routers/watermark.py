import base64
import logging
import time

from fastapi import APIRouter, HTTPException, Request, status

from app.config import settings
from app.schemas.watermark_schemas import (
    DetectRequest,
    DetectResponse,
    WatermarkRequest,
    WatermarkResponse,
)
from app.services.trustmark_service import ServiceUnavailableError, TrustMarkService

router = APIRouter()
logger = logging.getLogger(__name__)

# Magic-byte signatures for supported image formats.
_MAGIC_JPEG = b"\xff\xd8\xff"
_MAGIC_PNG = b"\x89PNG"
_MAGIC_RIFF = b"RIFF"
_MAGIC_WEBP_TAG = b"WEBP"


def _get_service(request: Request) -> TrustMarkService:
    """Return the TrustMarkService from app state, or raise 503."""
    svc = getattr(request.app.state, "trustmark_service", None)
    if svc is None or not svc.is_available:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=("TrustMark model not available. Check GET /health for model status."),
        )
    return svc  # type: ignore[return-value]


def _check_magic_bytes(image_bytes: bytes) -> None:
    """Raise HTTP 400 if image_bytes does not start with a known image signature."""
    is_jpeg = image_bytes[:3] == _MAGIC_JPEG
    is_png = image_bytes[:4] == _MAGIC_PNG
    is_webp = image_bytes[:4] == _MAGIC_RIFF and image_bytes[8:12] == _MAGIC_WEBP_TAG
    if not (is_jpeg or is_png or is_webp):
        raise HTTPException(
            status_code=400,
            detail=("Unsupported image format. Send JPEG, PNG, or WEBP. Check GET /health for service status."),
        )


def _decode_image_b64(image_b64: str) -> bytes:
    """Decode a base64 image payload, raising 400 on invalid input or 413 if too large."""
    try:
        image_bytes = base64.b64decode(image_b64, validate=True)
    except Exception as exc:
        logger.debug("base64 decode failed: %s", exc)
        raise HTTPException(
            status_code=400,
            detail=("Invalid base64 image data. Send standard base64-encoded bytes of a JPEG, PNG, or WEBP image."),
        ) from exc
    if len(image_bytes) > settings.MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                f"Image exceeds maximum allowed size of {settings.MAX_IMAGE_SIZE_BYTES} bytes "
                f"({settings.MAX_IMAGE_SIZE_BYTES // 1_048_576} MB). Reduce image dimensions or quality."
            ),
        )
    _check_magic_bytes(image_bytes)
    return image_bytes


@router.post("/watermark", response_model=WatermarkResponse)
async def watermark_image(payload: WatermarkRequest, request: Request) -> WatermarkResponse:
    """Embed a TrustMark neural watermark into an image.

    Requires TrustMark model loaded at startup. Returns 503 when model
    is not available (trustmark/torch not installed in this environment).

    Errors:
      400 - Invalid base64 input or unsupported image format.
      503 - Model not loaded; check GET /health.
      500 - Unexpected encoding failure.
    """
    svc = _get_service(request)
    image_bytes = _decode_image_b64(payload.image_b64)

    t0 = time.perf_counter()
    try:
        watermarked_bytes, confidence = svc.encode(image_bytes, payload.mime_type, payload.message_bits)
    except ServiceUnavailableError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except Exception as e:
        logger.exception("Watermark encode failed: %s", e)
        raise HTTPException(status_code=500, detail="Watermark encoding failed. Check server logs.")

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

    Returns 503 when model is not available; check GET /health for status.

    Errors:
      400 - Invalid base64 input or unsupported image format.
      503 - Model not loaded; check GET /health.
      500 - Unexpected detection failure.
    """
    svc = _get_service(request)
    image_bytes = _decode_image_b64(payload.image_b64)

    t0 = time.perf_counter()
    try:
        detected, msg_hex, confidence = svc.decode(image_bytes)
    except ServiceUnavailableError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except Exception as e:
        logger.exception("Watermark detect failed: %s", e)
        raise HTTPException(status_code=500, detail="Watermark detection failed. Check server logs.")

    elapsed_ms = (time.perf_counter() - t0) * 1000
    return DetectResponse(
        detected=detected,
        message_bits=msg_hex,
        confidence=confidence,
        processing_time_ms=round(elapsed_ms, 2),
    )
