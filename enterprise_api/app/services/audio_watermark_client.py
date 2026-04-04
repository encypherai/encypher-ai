"""HTTP client for the audio watermarking microservice.

Follows the TrustMarkClient pattern: httpx.AsyncClient with graceful
fallback on connection errors or non-200 responses.

The audio-watermark-service runs on settings.audio_watermark_service_url
(port 8011) and exposes:
  POST /api/v1/audio/watermark  -- embed spread-spectrum watermark (64-bit payload)
  POST /api/v1/audio/detect     -- detect/extract spread-spectrum watermark
"""

import hashlib
import hmac
import logging
from typing import Optional, Tuple

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

_WATERMARK_TIMEOUT = 30.0
_DETECT_TIMEOUT = 15.0


class AudioWatermarkClient:
    """Client for the audio watermarking microservice."""

    @property
    def is_configured(self) -> bool:
        return bool(settings.audio_watermark_service_url)

    async def apply_watermark(
        self,
        audio_b64: str,
        mime_type: str,
        payload: str,
        snr_db: Optional[float] = None,
    ) -> Optional[Tuple[str, float]]:
        """Embed a spread-spectrum watermark into audio.

        Args:
            audio_b64: Base64-encoded audio bytes.
            mime_type: Audio MIME type (audio/wav, audio/mpeg, etc.).
            payload: 16-char hex string (64-bit payload).
            snr_db: Optional SNR override (-20 for speech, -30 for music).

        Returns:
            Tuple of (watermarked_b64, confidence) on success, or None on failure.
        """
        if not self.is_configured:
            return None

        body: dict = {
            "audio_b64": audio_b64,
            "mime_type": mime_type,
            "payload": payload,
        }
        if snr_db is not None:
            body["snr_db"] = snr_db

        try:
            async with httpx.AsyncClient(timeout=_WATERMARK_TIMEOUT) as client:
                response = await client.post(
                    f"{settings.audio_watermark_service_url}/api/v1/audio/watermark",
                    json=body,
                )
        except httpx.RequestError as exc:
            logger.warning("Audio watermark service unavailable: %s", exc)
            return None

        if response.status_code != 200:
            logger.warning(
                "Audio watermark embed failed: %s %s",
                response.status_code,
                response.text[:200],
            )
            return None

        data = response.json()
        return data["watermarked_b64"], data.get("confidence", 1.0)

    async def detect_watermark(
        self,
        audio_b64: str,
        mime_type: str,
    ) -> Optional[Tuple[bool, Optional[str], float]]:
        """Detect and extract a spread-spectrum watermark from audio.

        Args:
            audio_b64: Base64-encoded audio bytes.
            mime_type: Audio MIME type.

        Returns:
            Tuple of (detected, payload_or_None, confidence) on success,
            or None on failure.
        """
        if not self.is_configured:
            return None

        try:
            async with httpx.AsyncClient(timeout=_DETECT_TIMEOUT) as client:
                response = await client.post(
                    f"{settings.audio_watermark_service_url}/api/v1/audio/detect",
                    json={"audio_b64": audio_b64, "mime_type": mime_type},
                )
        except httpx.RequestError as exc:
            logger.warning("Audio watermark detect unavailable: %s", exc)
            return None

        if response.status_code != 200:
            logger.warning(
                "Audio watermark detect failed: %s %s",
                response.status_code,
                response.text[:200],
            )
            return None

        data = response.json()
        return data["detected"], data.get("payload"), data.get("confidence", 0.0)


def compute_audio_watermark_payload(audio_id: str, org_id: str) -> str:
    """Compute the 64-bit audio watermark payload as a 16-char hex string.

    Uses HMAC-SHA256(key=audio_id, msg=org_id) truncated to 64 bits.
    This ties the watermark to both the specific audio and the org.
    """
    digest = hmac.new(audio_id.encode(), org_id.encode(), hashlib.sha256).hexdigest()
    return digest[:16]


def compute_audio_watermark_key(audio_id: str, org_id: str) -> str:
    """Compute the human-readable watermark key for DB storage."""
    org_hash = hashlib.sha256(org_id.encode()).hexdigest()[:8]
    return f"awm_{audio_id}_{org_hash}"


# Module-level singleton
audio_watermark_client = AudioWatermarkClient()
