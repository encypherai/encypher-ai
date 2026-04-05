import base64
import logging
import time
from typing import Iterator

import numpy as np
from fastapi import APIRouter, HTTPException, status

from app.config import settings
from app.schemas.watermark_schemas import (
    DetectRequest,
    DetectResponse,
    WatermarkRequest,
    WatermarkResponse,
)
from app.services.spread_spectrum import detect, embed
from app.services.video_codec import (
    VideoMeta,
    _av_available,
    decode_video_blocks,
    encode_video_streaming,
)

router = APIRouter()
logger = logging.getLogger(__name__)

_SUPPORTED_MIMES = {
    "video/mp4",
    "video/quicktime",
    "video/x-matroska",
    "video/webm",
    "video/avi",
    "video/x-msvideo",
}

# Cache the seed bytes at module level (settings are immutable after startup)
_SEED: bytes = settings.WATERMARK_SECRET.encode()


def _decode_b64(video_b64: str, mime_type: str) -> bytes:
    """Decode base64 video, validate size and mime type."""
    if mime_type not in _SUPPORTED_MIMES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported MIME type: {mime_type}. Supported: {', '.join(sorted(_SUPPORTED_MIMES))}",
        )
    try:
        video_bytes = base64.b64decode(video_b64, validate=True)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid base64 video data.") from exc

    if len(video_bytes) > settings.MAX_VIDEO_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Video exceeds maximum size of {settings.MAX_VIDEO_SIZE_BYTES // 1_048_576} MB.",
        )
    return video_bytes


def _embed_stream(
    video_bytes: bytes,
    payload_hex: str,
    wsr_db: float,
    block_frames: int,
) -> "tuple[Iterator[tuple[np.ndarray, np.ndarray, np.ndarray]], VideoMeta, float]":
    """Embed watermark block-by-block via the streaming decoder.

    Fully consumes decode_video_blocks() so that the generator is exhausted and
    all blocks are processed before encode_video_streaming() is called. This
    lets us report mean_confidence without a two-pass decode, at the cost of
    holding one block at a time in memory during the embed phase.

    Returns:
        (embedded_blocks, meta, mean_confidence) where embedded_blocks is a
        list of (y_block, cb_block, cr_block) tuples ready for the encoder.
    """
    embedded: list[tuple[np.ndarray, np.ndarray, np.ndarray]] = []
    confidences: list[float] = []
    meta_out: VideoMeta | None = None

    for y_block, cb_block, cr_block, meta in decode_video_blocks(video_bytes, block_frames):
        if meta_out is None:
            meta_out = meta

        flat = y_block.ravel()
        wm_flat, conf = embed(flat, payload_hex, _SEED, wsr_db=wsr_db)
        watermarked_y = wm_flat.reshape(y_block.shape)
        embedded.append((watermarked_y, cb_block, cr_block))
        confidences.append(conf)

    if meta_out is None:
        raise ValueError("No video frames decoded from input bytes.")

    mean_confidence = float(np.mean(confidences)) if confidences else 0.0
    return iter(embedded), meta_out, mean_confidence


def _detect_stream(
    video_bytes: bytes,
    block_frames: int,
) -> "tuple[bool, str | None, float]":
    """Detect watermark block-by-block via the streaming decoder.

    Runs detection on each block and returns the result with the highest
    confidence across all blocks.

    Returns:
        (detected, payload_hex_or_None, confidence)
    """
    block_results: list[tuple[bool, str | None, float]] = []

    for y_block, _cb, _cr, _meta in decode_video_blocks(video_bytes, block_frames):
        flat = y_block.ravel()
        result = detect(flat, _SEED)
        block_results.append(result)

    if not block_results:
        return False, None, 0.0

    best = max(block_results, key=lambda r: r[2])
    return best


@router.post("/video/watermark", response_model=WatermarkResponse)
async def watermark_video(payload: WatermarkRequest) -> WatermarkResponse:
    """Embed a spread-spectrum watermark into video Y-channel."""
    if not _av_available:
        raise HTTPException(status_code=503, detail="PyAV/ffmpeg not available on this server.")

    video_bytes = _decode_b64(payload.video_b64, payload.mime_type)
    wsr_db = payload.wsr_db if payload.wsr_db is not None else settings.DEFAULT_WSR_DB

    t0 = time.perf_counter()
    try:
        blocks_iter, meta, confidence = _embed_stream(
            video_bytes,
            payload.payload,
            wsr_db,
            settings.BLOCK_FRAMES,
        )
        output_format = "mp4" if "mp4" in payload.mime_type or "quicktime" in payload.mime_type else "matroska"
        output_bytes = encode_video_streaming(blocks_iter, meta, output_format=output_format)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Video watermark embed failed: %s", e)
        raise HTTPException(status_code=500, detail="Video watermark embedding failed.")

    elapsed_ms = (time.perf_counter() - t0) * 1000
    return WatermarkResponse(
        watermarked_b64=base64.b64encode(output_bytes).decode(),
        confidence=confidence,
        processing_time_ms=round(elapsed_ms, 2),
    )


@router.post("/video/detect", response_model=DetectResponse)
async def detect_watermark(payload: DetectRequest) -> DetectResponse:
    """Detect a spread-spectrum watermark in video Y-channel."""
    if not _av_available:
        raise HTTPException(status_code=503, detail="PyAV/ffmpeg not available on this server.")

    video_bytes = _decode_b64(payload.video_b64, payload.mime_type)

    t0 = time.perf_counter()
    try:
        detected, extracted_payload, confidence = _detect_stream(
            video_bytes,
            settings.BLOCK_FRAMES,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Video watermark detect failed: %s", e)
        raise HTTPException(status_code=500, detail="Video watermark detection failed.")

    elapsed_ms = (time.perf_counter() - t0) * 1000
    return DetectResponse(
        detected=detected,
        payload=extracted_payload,
        confidence=confidence,
        processing_time_ms=round(elapsed_ms, 2),
    )
