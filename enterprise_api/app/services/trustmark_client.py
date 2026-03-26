"""HTTP client for the TrustMark image watermarking microservice.

Follows the KeyServiceClient/AuthServiceClient pattern: httpx.AsyncClient
with graceful fallback on connection errors or non-200 responses.

The image-service runs on settings.image_service_url (port 8010) and exposes:
  POST /api/v1/watermark  -- embed TrustMark watermark (100-bit payload)
  POST /api/v1/detect     -- detect/extract TrustMark watermark
"""

import hashlib
import hmac
import logging
from typing import Optional, Tuple

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

# Timeout for TrustMark operations (neural network inference can be slow)
_WATERMARK_TIMEOUT = 30.0
_DETECT_TIMEOUT = 15.0


class TrustMarkClient:
    """Client for the TrustMark image watermarking microservice."""

    @property
    def is_configured(self) -> bool:
        return bool(settings.image_service_url)

    async def apply_watermark(
        self,
        image_b64: str,
        mime_type: str,
        message_bits: str,
    ) -> Optional[Tuple[str, float]]:
        """Embed a TrustMark watermark into an image.

        Args:
            image_b64: Base64-encoded image bytes.
            mime_type: Image MIME type (image/jpeg, image/png, image/webp).
            message_bits: 25-char hex string (100-bit payload).

        Returns:
            Tuple of (watermarked_b64, confidence) on success, or None on failure.
        """
        if not self.is_configured:
            return None

        try:
            async with httpx.AsyncClient(timeout=_WATERMARK_TIMEOUT) as client:
                response = await client.post(
                    f"{settings.image_service_url}/api/v1/watermark",
                    json={
                        "image_b64": image_b64,
                        "mime_type": mime_type,
                        "message_bits": message_bits,
                    },
                )
        except httpx.RequestError as exc:
            logger.warning("TrustMark service unavailable: %s", exc)
            return None

        if response.status_code != 200:
            logger.warning(
                "TrustMark watermark failed: %s %s",
                response.status_code,
                response.text[:200],
            )
            return None

        data = response.json()
        return data["watermarked_b64"], data.get("confidence", 1.0)

    async def detect_watermark(
        self,
        image_b64: str,
    ) -> Optional[Tuple[bool, Optional[str], float]]:
        """Detect and extract a TrustMark watermark from an image.

        Args:
            image_b64: Base64-encoded image bytes.

        Returns:
            Tuple of (detected, message_bits_or_None, confidence) on success,
            or None on failure.
        """
        if not self.is_configured:
            return None

        try:
            async with httpx.AsyncClient(timeout=_DETECT_TIMEOUT) as client:
                response = await client.post(
                    f"{settings.image_service_url}/api/v1/detect",
                    json={"image_b64": image_b64},
                )
        except httpx.RequestError as exc:
            logger.warning("TrustMark detect unavailable: %s", exc)
            return None

        if response.status_code != 200:
            logger.warning(
                "TrustMark detect failed: %s %s",
                response.status_code,
                response.text[:200],
            )
            return None

        data = response.json()
        return data["detected"], data.get("message_bits"), data.get("confidence", 0.0)


def compute_trustmark_payload(image_id: str, org_id: str) -> str:
    """Compute the 100-bit TrustMark payload as a 25-char hex string.

    Uses HMAC-SHA256(key=image_id, msg=org_id) truncated to 100 bits.
    This ties the watermark to both the specific image and the org.
    """
    digest = hmac.new(image_id.encode(), org_id.encode(), hashlib.sha256).hexdigest()
    # 100 bits = 25 hex chars (each hex char = 4 bits)
    return digest[:25]


def compute_trustmark_key(image_id: str, org_id: str) -> str:
    """Compute the human-readable trustmark_key for DB storage."""
    org_hash = hashlib.sha256(org_id.encode()).hexdigest()[:8]
    return f"tm_{image_id}_{org_hash}"


# Module-level singleton
trustmark_client = TrustMarkClient()
