"""HTTP client for the audio watermarking microservice.

The audio-watermark-service runs on settings.audio_watermark_service_url
(port 8011) and exposes:
  POST /api/v1/audio/watermark  -- embed spread-spectrum watermark (64-bit payload)
  POST /api/v1/audio/detect     -- detect/extract spread-spectrum watermark
"""

from typing import Optional, Tuple

from app.services.watermark_client_base import (
    WatermarkClientBase,
    apply_watermark_to_signed_media,
    compute_watermark_key,
    compute_watermark_payload,
)

SOFT_BINDING_ASSERTION: dict = {
    "label": "c2pa.soft_binding.v1",
    "data": {
        "method": "encypher.spread_spectrum_audio.v1",
        "payload_bits": 64,
        "ecc": "rs32_8_conv_r3_k7",
        "description": "Spread-spectrum audio watermark embedded in signal domain",
    },
}


class AudioWatermarkClient(WatermarkClientBase):
    _service_url_attr = "audio_watermark_service_url"
    _api_prefix = "/api/v1/audio"
    _media_key = "audio_b64"
    _watermark_timeout = 30.0
    _detect_timeout = 15.0


def compute_audio_watermark_payload(audio_id: str, org_id: str) -> str:
    return compute_watermark_payload(audio_id, org_id)


def compute_audio_watermark_key(audio_id: str, org_id: str) -> str:
    return compute_watermark_key("awm", audio_id, org_id)


async def apply_watermark_to_signed_audio(
    signed_bytes: bytes,
    mime_type: str,
    audio_id: str,
    org_id: str,
) -> Optional[Tuple[bytes, str, str]]:
    """Apply watermark to already-signed audio bytes."""
    return await apply_watermark_to_signed_media(
        audio_watermark_client,
        signed_bytes,
        mime_type,
        audio_id,
        org_id,
        "awm",
    )


audio_watermark_client = AudioWatermarkClient()
