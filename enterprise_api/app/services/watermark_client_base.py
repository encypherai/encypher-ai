"""Base class for spread-spectrum watermark microservice clients.

Provides the shared HTTP-over-httpx pattern used by both the audio and
video watermark clients. Each subclass supplies media-type-specific
configuration (service URL, API prefix, timeouts).

The httpx.AsyncClient is created once per singleton lifetime and reused
across requests, avoiding per-request TCP/TLS setup overhead.
"""

import base64
import hashlib
import hmac
import logging
from typing import Optional, Tuple

import httpx

from app.utils.hashing import compute_sha256

logger = logging.getLogger(__name__)


class WatermarkClientBase:
    """Base client for spread-spectrum watermark microservices.

    Subclasses must set:
        _service_url_attr: str  -- settings attribute name for the service URL
        _api_prefix: str        -- e.g. "/api/v1/audio" or "/api/v1/video"
        _media_key: str         -- JSON body key, e.g. "audio_b64" or "video_b64"
        _watermark_timeout: float
        _detect_timeout: float
    """

    _service_url_attr: str
    _api_prefix: str
    _media_key: str
    _watermark_timeout: float
    _detect_timeout: float

    def __init__(self) -> None:
        self._client: Optional[httpx.AsyncClient] = None

    def _get_service_url(self) -> str:
        from app.config import settings

        return getattr(settings, self._service_url_attr, "") or ""

    @property
    def is_configured(self) -> bool:
        return bool(self._get_service_url())

    def _get_client(self, timeout: float) -> httpx.AsyncClient:
        """Return a reusable httpx client, lazily created."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self._get_service_url(),
                timeout=max(self._watermark_timeout, self._detect_timeout),
            )
        return self._client

    async def apply_watermark(
        self,
        media_b64: str,
        mime_type: str,
        payload: str,
        snr_db: Optional[float] = None,
    ) -> Optional[Tuple[str, float]]:
        """Embed a spread-spectrum watermark.

        Returns (watermarked_b64, confidence) on success, None on failure.
        """
        if not self.is_configured:
            return None

        body: dict = {
            self._media_key: media_b64,
            "mime_type": mime_type,
            "payload": payload,
        }
        if snr_db is not None:
            body["snr_db"] = snr_db

        try:
            client = self._get_client(self._watermark_timeout)
            response = await client.post(
                f"{self._api_prefix}/watermark",
                json=body,
                timeout=self._watermark_timeout,
            )
        except httpx.RequestError as exc:
            logger.warning("%s watermark service unavailable: %s", self._media_key.split("_")[0].title(), exc)
            return None

        if response.status_code != 200:
            logger.warning(
                "%s watermark embed failed: %s %s",
                self._media_key.split("_")[0].title(),
                response.status_code,
                response.text[:200],
            )
            return None

        data = response.json()
        return data["watermarked_b64"], data.get("confidence", 1.0)

    async def detect_watermark(
        self,
        media_b64: str,
        mime_type: str,
    ) -> Optional[Tuple[bool, Optional[str], float]]:
        """Detect and extract a spread-spectrum watermark.

        Returns (detected, payload_or_None, confidence) on success, None on failure.
        """
        if not self.is_configured:
            return None

        try:
            client = self._get_client(self._detect_timeout)
            response = await client.post(
                f"{self._api_prefix}/detect",
                json={self._media_key: media_b64, "mime_type": mime_type},
                timeout=self._detect_timeout,
            )
        except httpx.RequestError as exc:
            logger.warning("%s watermark detect unavailable: %s", self._media_key.split("_")[0].title(), exc)
            return None

        if response.status_code != 200:
            logger.warning(
                "%s watermark detect failed: %s %s",
                self._media_key.split("_")[0].title(),
                response.status_code,
                response.text[:200],
            )
            return None

        data = response.json()
        return data["detected"], data.get("payload"), data.get("confidence", 0.0)

    async def close(self) -> None:
        """Close the underlying httpx client."""
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None


def compute_watermark_payload(asset_id: str, org_id: str) -> str:
    """Compute 64-bit watermark payload as 16-char hex string.

    Uses HMAC-SHA256(key=asset_id, msg=org_id) truncated to 64 bits.
    """
    return hmac.new(asset_id.encode(), org_id.encode(), hashlib.sha256).hexdigest()[:16]


def compute_watermark_key(prefix: str, asset_id: str, org_id: str) -> str:
    """Compute human-readable watermark key for DB storage."""
    org_hash = hashlib.sha256(org_id.encode()).hexdigest()[:8]
    return f"{prefix}_{asset_id}_{org_hash}"


async def apply_watermark_to_signed_media(
    client: WatermarkClientBase,
    signed_bytes: bytes,
    mime_type: str,
    asset_id: str,
    org_id: str,
    key_prefix: str,
) -> Optional[Tuple[bytes, str, str]]:
    """Apply watermark to already-signed media bytes.

    Shared post-signing watermark flow: base64 encode, call microservice,
    decode, recompute hash.

    Returns (watermarked_bytes, new_sha256_hash, watermark_key) or None.
    """
    if not client.is_configured:
        return None

    signed_b64 = base64.b64encode(signed_bytes).decode()
    payload_hex = compute_watermark_payload(asset_id, org_id)
    wm_result = await client.apply_watermark(signed_b64, mime_type, payload_hex)
    if wm_result is None:
        logger.warning("Watermark failed for asset_id=%s, continuing without watermark", asset_id)
        return None

    watermarked_b64, _confidence = wm_result
    watermarked_bytes = base64.b64decode(watermarked_b64)
    new_hash = compute_sha256(watermarked_bytes)
    wm_key = compute_watermark_key(key_prefix, asset_id, org_id)
    return watermarked_bytes, new_hash, wm_key
