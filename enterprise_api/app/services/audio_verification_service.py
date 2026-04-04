"""Audio C2PA verification service using c2pa-python Reader.

Also supports spread-spectrum watermark detection via the audio watermark
microservice when configured.
"""

import logging
from dataclasses import dataclass
from typing import Optional

from app.utils.audio_utils import canonicalize_mime_type
from app.utils.c2pa_verifier_core import C2paVerificationResult, verify_c2pa

logger = logging.getLogger(__name__)

# Re-export for callers that import from this module
AudioVerificationResult = C2paVerificationResult


@dataclass
class AudioVerificationWithWatermark:
    """Combined C2PA + watermark verification result."""

    c2pa: C2paVerificationResult
    watermark_detected: bool = False
    watermark_payload: Optional[str] = None
    watermark_confidence: float = 0.0


def verify_audio_c2pa(audio_bytes: bytes, mime_type: str) -> C2paVerificationResult:
    """Verify C2PA manifest embedded in audio bytes.

    Delegates to the shared verify_c2pa function with audio MIME canonicalization.
    """
    return verify_c2pa(audio_bytes, mime_type, canonicalize_fn=canonicalize_mime_type)


async def verify_audio_with_watermark(
    audio_bytes: bytes,
    mime_type: str,
    audio_b64: str,
) -> AudioVerificationWithWatermark:
    """Verify both C2PA manifest and spread-spectrum watermark.

    Args:
        audio_bytes: Raw audio bytes.
        mime_type: Audio MIME type.
        audio_b64: Base64-encoded audio (avoids re-encoding).

    Returns:
        Combined verification result.
    """
    c2pa_result = verify_c2pa(audio_bytes, mime_type, canonicalize_fn=canonicalize_mime_type)

    result = AudioVerificationWithWatermark(c2pa=c2pa_result)

    from app.services.audio_watermark_client import audio_watermark_client

    if audio_watermark_client.is_configured:
        wm_result = await audio_watermark_client.detect_watermark(audio_b64, mime_type)
        if wm_result is not None:
            detected, payload, confidence = wm_result
            result.watermark_detected = detected
            result.watermark_payload = payload
            result.watermark_confidence = confidence
        else:
            logger.warning("Audio watermark detection failed (service error)")

    return result
