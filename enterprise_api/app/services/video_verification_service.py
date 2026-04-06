"""Video C2PA verification service using c2pa-python Reader.

Also supports spread-spectrum watermark detection via the video watermark
microservice when configured.
"""

import base64
import logging
from dataclasses import dataclass
from typing import Optional

from app.utils.c2pa_verifier_core import C2paVerificationResult, verify_c2pa
from app.utils.video_utils import canonicalize_mime_type

logger = logging.getLogger(__name__)

# Re-export for callers that import from this module
VideoVerificationResult = C2paVerificationResult


@dataclass
class VideoVerificationWithWatermark:
    """Combined C2PA + watermark verification result."""

    c2pa: C2paVerificationResult
    watermark_detected: bool = False
    watermark_payload: Optional[str] = None
    watermark_confidence: float = 0.0


def verify_video_c2pa(video_bytes: bytes, mime_type: str) -> C2paVerificationResult:
    """Verify C2PA manifest embedded in video bytes.

    Delegates to the shared verify_c2pa function with video MIME canonicalization.
    """
    return verify_c2pa(video_bytes, mime_type, canonicalize_fn=canonicalize_mime_type)


async def verify_video_with_watermark(
    video_bytes: bytes,
    mime_type: str,
) -> VideoVerificationWithWatermark:
    """Verify both C2PA manifest and spread-spectrum watermark.

    Args:
        video_bytes: Raw video bytes.
        mime_type: Video MIME type.

    Returns:
        Combined verification result.
    """
    c2pa_result = verify_video_c2pa(video_bytes, mime_type)

    result = VideoVerificationWithWatermark(c2pa=c2pa_result)

    from app.services.video_watermark_client import video_watermark_client

    if video_watermark_client.is_configured:
        video_b64 = base64.b64encode(video_bytes).decode()
        wm_result = await video_watermark_client.detect_watermark(video_b64, mime_type)
        if wm_result is not None:
            detected, payload, confidence = wm_result
            result.watermark_detected = detected
            result.watermark_payload = payload
            result.watermark_confidence = confidence
        else:
            logger.warning("Video watermark detection failed (service error)")

    return result
