import base64
import logging
import time

from fastapi import APIRouter, HTTPException, status

from app.config import settings
from app.schemas.watermark_schemas import (
    AudioDetectRequest,
    AudioDetectResponse,
    AudioWatermarkRequest,
    AudioWatermarkResponse,
)
from app.services.spread_spectrum import decode_audio, embed, detect, encode_audio

router = APIRouter()
logger = logging.getLogger(__name__)

_SUPPORTED_MIMES = {"audio/wav", "audio/wave", "audio/x-wav", "audio/mpeg", "audio/mp4", "audio/x-m4a", "audio/aac"}

# Cache the seed bytes at module level (settings are immutable after startup)
_SEED: bytes = settings.WATERMARK_SECRET.encode() or b"encypher-audio-wm-default"


def _decode_b64(audio_b64: str, mime_type: str) -> bytes:
    """Decode base64 audio, validate size and mime type."""
    if mime_type not in _SUPPORTED_MIMES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported MIME type: {mime_type}. Supported: {', '.join(sorted(_SUPPORTED_MIMES))}",
        )
    try:
        audio_bytes = base64.b64decode(audio_b64, validate=True)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid base64 audio data.") from exc

    if len(audio_bytes) > settings.MAX_AUDIO_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Audio exceeds maximum size of {settings.MAX_AUDIO_SIZE_BYTES // 1_048_576} MB.",
        )
    return audio_bytes


@router.post("/audio/watermark", response_model=AudioWatermarkResponse)
async def watermark_audio(payload: AudioWatermarkRequest) -> AudioWatermarkResponse:
    """Embed a spread-spectrum watermark into audio."""
    audio_bytes = _decode_b64(payload.audio_b64, payload.mime_type)

    snr_db = payload.snr_db if payload.snr_db is not None else settings.DEFAULT_SNR_DB

    t0 = time.perf_counter()
    try:
        samples, sr = decode_audio(audio_bytes)
        watermarked, confidence = embed(
            samples=samples,
            sample_rate=sr,
            payload=payload.payload,
            seed=_SEED,
            snr_db=snr_db,
        )
        output_bytes = encode_audio(watermarked, sr)
    except Exception as e:
        logger.exception("Audio watermark embed failed: %s", e)
        raise HTTPException(status_code=500, detail="Audio watermark embedding failed.")

    elapsed_ms = (time.perf_counter() - t0) * 1000
    return AudioWatermarkResponse(
        watermarked_b64=base64.b64encode(output_bytes).decode(),
        payload=payload.payload,
        confidence=confidence,
        processing_time_ms=round(elapsed_ms, 2),
    )


@router.post("/audio/detect", response_model=AudioDetectResponse)
async def detect_watermark(payload: AudioDetectRequest) -> AudioDetectResponse:
    """Detect a spread-spectrum watermark in audio."""
    audio_bytes = _decode_b64(payload.audio_b64, payload.mime_type)

    t0 = time.perf_counter()
    try:
        samples, sr = decode_audio(audio_bytes)
        detected, extracted_payload, confidence = detect(
            samples=samples,
            sample_rate=sr,
            seed=_SEED,
        )
    except Exception as e:
        logger.exception("Audio watermark detect failed: %s", e)
        raise HTTPException(status_code=500, detail="Audio watermark detection failed.")

    elapsed_ms = (time.perf_counter() - t0) * 1000
    return AudioDetectResponse(
        detected=detected,
        payload=extracted_payload,
        confidence=confidence,
        processing_time_ms=round(elapsed_ms, 2),
    )
