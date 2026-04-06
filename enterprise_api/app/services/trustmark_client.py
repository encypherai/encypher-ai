"""HTTP client for the TrustMark image watermarking microservice.

TrustMark is Adobe Research's neural watermarking library (Apache 2.0).
GitHub: https://github.com/adobe/trustmark

The image-service runs on settings.image_service_url (port 8010) and exposes:
  POST /api/v1/watermark  -- embed TrustMark watermark (100-bit payload)
  POST /api/v1/detect     -- detect/extract TrustMark watermark
"""

import base64
import hashlib
import hmac
import logging
from typing import Optional, Tuple

import httpx

from app.services.watermark_client_base import WatermarkClientBase
from app.utils.hashing import compute_sha256

logger = logging.getLogger(__name__)

# TrustMark uses a 100-bit payload (25 hex chars), unlike the 64-bit
# spread-spectrum payload used by the audio/video services.
_PAYLOAD_HEX_LEN = 25

SOFT_BINDING_ASSERTION_IMAGE: dict = {
    "label": "c2pa.soft_binding.v1",
    "data": {
        "method": "encypher.trustmark_neural.v1",
        "payload_bits": 100,
        "description": "TrustMark neural image watermark (Adobe Research, Apache 2.0)",
    },
}


class TrustMarkClient(WatermarkClientBase):
    """Client for the TrustMark image watermarking microservice.

    Inherits connection pooling and lifecycle from WatermarkClientBase.
    Overrides apply_watermark and detect_watermark because the TrustMark
    microservice uses different JSON keys (message_bits vs payload) and
    a 100-bit payload instead of 64-bit.
    """

    _service_url_attr = "image_service_url"
    _api_prefix = "/api/v1"
    _media_key = "image_b64"
    _watermark_timeout = 30.0
    _detect_timeout = 15.0

    async def apply_watermark(
        self,
        image_b64: str,
        mime_type: str,
        message_bits: str,
        snr_db: Optional[float] = None,
    ) -> Optional[Tuple[str, float]]:
        """Embed a TrustMark watermark into an image.

        Args:
            image_b64: Base64-encoded image bytes.
            mime_type: Image MIME type (image/jpeg, image/png, image/webp).
            message_bits: 25-char hex string (100-bit payload).
            snr_db: Ignored (TrustMark controls its own strength).

        Returns:
            Tuple of (watermarked_b64, confidence) on success, or None on failure.
        """
        if not self.is_configured:
            return None

        try:
            client = self._get_client(self._watermark_timeout)
            response = await client.post(
                f"{self._api_prefix}/watermark",
                json={
                    "image_b64": image_b64,
                    "mime_type": mime_type,
                    "message_bits": message_bits,
                },
                timeout=self._watermark_timeout,
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
        mime_type: str = "",
    ) -> Optional[Tuple[bool, Optional[str], float]]:
        """Detect and extract a TrustMark watermark from an image.

        Args:
            image_b64: Base64-encoded image bytes.
            mime_type: Ignored (TrustMark detects from raw pixels).

        Returns:
            Tuple of (detected, message_bits_or_None, confidence) on success,
            or None on failure.
        """
        if not self.is_configured:
            return None

        try:
            client = self._get_client(self._detect_timeout)
            response = await client.post(
                f"{self._api_prefix}/detect",
                json={"image_b64": image_b64},
                timeout=self._detect_timeout,
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
    return digest[:_PAYLOAD_HEX_LEN]


def compute_trustmark_key(image_id: str, org_id: str) -> str:
    """Compute the human-readable trustmark_key for DB storage."""
    org_hash = hashlib.sha256(org_id.encode()).hexdigest()[:8]
    return f"tm_{image_id}_{org_hash}"


async def apply_watermark_to_signed_image(
    signed_bytes: bytes,
    mime_type: str,
    image_id: str,
    org_id: str,
) -> Optional[Tuple[bytes, str, str]]:
    """Apply TrustMark watermark to already-signed image bytes.

    Post-signing watermark flow: base64 encode, call TrustMark microservice,
    decode, recompute hash.

    Returns (watermarked_bytes, new_sha256_hash, watermark_key) or None.
    """
    if not trustmark_client.is_configured:
        return None

    signed_b64 = base64.b64encode(signed_bytes).decode()
    payload_hex = compute_trustmark_payload(image_id, org_id)
    wm_result = await trustmark_client.apply_watermark(signed_b64, mime_type, payload_hex)
    if wm_result is None:
        logger.warning("TrustMark watermark failed for image_id=%s, continuing without watermark", image_id)
        return None

    watermarked_b64, _confidence = wm_result
    watermarked_bytes = base64.b64decode(watermarked_b64)
    new_hash = compute_sha256(watermarked_bytes)
    wm_key = compute_trustmark_key(image_id, org_id)
    return watermarked_bytes, new_hash, wm_key


# Module-level singleton
trustmark_client = TrustMarkClient()
