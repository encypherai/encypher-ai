"""HTTP client for the video watermarking microservice.

The video-watermark-service runs on settings.video_watermark_service_url
(port 8012) and exposes:
  POST /api/v1/video/watermark  -- embed spread-spectrum watermark (64-bit payload)
  POST /api/v1/video/detect     -- detect/extract spread-spectrum watermark
"""

from typing import Optional, Tuple

from app.services.watermark_client_base import (
    WatermarkClientBase,
    apply_watermark_to_signed_media,
    compute_watermark_key,
    compute_watermark_payload,
)

SOFT_BINDING_ASSERTION_VIDEO: dict = {
    "label": "c2pa.soft_binding.v1",
    "data": {
        "method": "encypher.spread_spectrum_video.v1",
        "payload_bits": 64,
        "ecc": "rs32_8_conv_r3_k7",
        "description": "Spread-spectrum video watermark embedded in luminance channel",
    },
}


class VideoWatermarkClient(WatermarkClientBase):
    _service_url_attr = "video_watermark_service_url"
    _api_prefix = "/api/v1/video"
    _media_key = "video_b64"
    _watermark_timeout = 300.0
    _detect_timeout = 120.0


def compute_video_watermark_payload(video_id: str, org_id: str) -> str:
    return compute_watermark_payload(video_id, org_id)


def compute_video_watermark_key(video_id: str, org_id: str) -> str:
    return compute_watermark_key("vwm", video_id, org_id)


async def apply_watermark_to_signed_video(
    signed_bytes: bytes,
    mime_type: str,
    video_id: str,
    org_id: str,
) -> Optional[Tuple[bytes, str, str]]:
    """Apply watermark to already-signed video bytes."""
    return await apply_watermark_to_signed_media(
        video_watermark_client,
        signed_bytes,
        mime_type,
        video_id,
        org_id,
        "vwm",
    )


video_watermark_client = VideoWatermarkClient()
