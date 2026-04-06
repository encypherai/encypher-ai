"""Pydantic schemas for rich article signing (text + embedded media).

Supports composite web content: text + images + audio + video. At least one
media item is required; each media type is independently optional.
"""

import base64
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, model_validator

from app.utils.audio_utils import SUPPORTED_AUDIO_MIME_TYPES
from app.utils.image_format_registry import SUPPORTED_IMAGE_MIME_TYPES as SUPPORTED_IMAGE_MIMES

# Re-export for backward compatibility with tests that import from this module
SUPPORTED_MIME_TYPES = SUPPORTED_IMAGE_MIMES
from app.utils.video_utils import SUPPORTED_VIDEO_MIME_TYPES


class RichContentImage(BaseModel):
    data: str = Field(..., description="Base64-encoded image bytes")
    filename: str = Field(..., description="Original filename e.g. photo1.jpg")
    mime_type: str = Field(..., description="MIME type of the image")
    position: int = Field(0, ge=0, description="Order of this image within the article")
    alt_text: Optional[str] = Field(None, max_length=500)
    metadata: Optional[dict] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_image_data(self) -> "RichContentImage":
        try:
            raw = base64.b64decode(self.data, validate=True)
        except Exception as e:
            raise ValueError(f"image data is not valid base64: {e}") from e
        if len(raw) > 10_485_760:
            raise ValueError(f"Image {self.filename!r} exceeds 10MB limit ({len(raw)} bytes)")
        if self.mime_type.lower() not in SUPPORTED_IMAGE_MIMES:
            raise ValueError(f"Unsupported image MIME type: {self.mime_type!r}. Supported: {sorted(SUPPORTED_IMAGE_MIMES)}")
        return self


class RichContentAudio(BaseModel):
    data: str = Field(..., description="Base64-encoded audio bytes")
    filename: str = Field(..., description="Original filename e.g. interview.mp3")
    mime_type: str = Field(..., description="MIME type of the audio")
    position: int = Field(0, ge=0, description="Order of this audio within the article")
    metadata: Optional[dict] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_audio_data(self) -> "RichContentAudio":
        try:
            raw = base64.b64decode(self.data, validate=True)
        except Exception as e:
            raise ValueError(f"audio data is not valid base64: {e}") from e
        if len(raw) > 52_428_800:
            raise ValueError(f"Audio {self.filename!r} exceeds 50MB limit ({len(raw)} bytes)")
        if self.mime_type.lower() not in SUPPORTED_AUDIO_MIME_TYPES:
            raise ValueError(f"Unsupported audio MIME type: {self.mime_type!r}. Supported: {sorted(SUPPORTED_AUDIO_MIME_TYPES)}")
        return self


class RichContentVideo(BaseModel):
    data: str = Field(..., description="Base64-encoded video bytes")
    filename: str = Field(..., description="Original filename e.g. clip.mp4")
    mime_type: str = Field(..., description="MIME type of the video")
    position: int = Field(0, ge=0, description="Order of this video within the article")
    metadata: Optional[dict] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_video_data(self) -> "RichContentVideo":
        try:
            raw = base64.b64decode(self.data, validate=True)
        except Exception as e:
            raise ValueError(f"video data is not valid base64: {e}") from e
        if len(raw) > 104_857_600:
            raise ValueError(f"Video {self.filename!r} exceeds 100MB limit ({len(raw)} bytes)")
        if self.mime_type.lower() not in SUPPORTED_VIDEO_MIME_TYPES:
            raise ValueError(f"Unsupported video MIME type: {self.mime_type!r}. Supported: {sorted(SUPPORTED_VIDEO_MIME_TYPES)}")
        return self


class RichSignOptions(BaseModel):
    segmentation_level: str = "sentence"
    manifest_mode: str = "micro"
    action: str = "c2pa.created"
    enable_trustmark: bool = False  # Enterprise only, images
    enable_audio_watermark: bool = False  # Enterprise only
    enable_video_watermark: bool = False  # Enterprise only
    image_quality: int = Field(95, ge=1, le=100)
    use_rights_profile: bool = True
    index_for_attribution: bool = True


class RichArticleSignRequest(BaseModel):
    content: str = Field(
        ...,
        min_length=1,
        max_length=5_242_880,
        description="Article text/HTML/Markdown",
    )
    content_format: Literal["html", "markdown", "plain"] = "html"
    document_id: Optional[str] = Field(None, max_length=255)
    document_title: Optional[str] = Field(None, max_length=500)
    document_url: Optional[str] = Field(None, max_length=1000)
    metadata: Optional[dict] = Field(default_factory=dict)
    images: List[RichContentImage] = Field(default_factory=list, max_length=20)
    audios: List[RichContentAudio] = Field(default_factory=list, max_length=10)
    videos: List[RichContentVideo] = Field(default_factory=list, max_length=5)
    options: RichSignOptions = Field(default_factory=RichSignOptions)
    publisher_org_id: Optional[str] = None  # proxy signing

    @model_validator(mode="after")
    def validate_at_least_one_media(self) -> "RichArticleSignRequest":
        if not self.images and not self.audios and not self.videos:
            raise ValueError("At least one media item (image, audio, or video) is required")
        return self


class SignedImageResult(BaseModel):
    image_id: str
    filename: str
    position: int
    signed_image_b64: str  # base64 encoded signed image bytes
    signed_image_hash: str  # "sha256:..."
    c2pa_manifest_instance_id: str
    size_bytes: int
    phash: Optional[str] = None  # hex string for client use
    trustmark_applied: bool = False
    mime_type: str
    c2pa_signed: bool = True  # False in passthrough mode (no CA cert configured)


class SignedAudioResult(BaseModel):
    audio_id: str
    filename: str
    position: int
    signed_audio_b64: str
    signed_audio_hash: str  # "sha256:..."
    c2pa_manifest_instance_id: str
    size_bytes: int
    watermark_applied: bool = False
    mime_type: str
    c2pa_signed: bool = True


class SignedVideoResult(BaseModel):
    video_id: str
    filename: str
    position: int
    signed_video_b64: str
    signed_video_hash: str  # "sha256:..."
    c2pa_manifest_instance_id: str
    size_bytes: int
    watermark_applied: bool = False
    mime_type: str
    c2pa_signed: bool = True


class CompositeManifestSummary(BaseModel):
    instance_id: str
    ingredient_count: int
    manifest_hash: str


class RichSignResponseData(BaseModel):
    document_id: str
    content_type: str = "rich_article"
    text: dict  # SignedDocumentResult as dict
    images: List[SignedImageResult] = []
    audios: List[SignedAudioResult] = []
    videos: List[SignedVideoResult] = []
    composite_manifest: CompositeManifestSummary
    total_images: int = 0
    total_audios: int = 0
    total_videos: int = 0
    processing_time_ms: float


class RichSignResponse(BaseModel):
    success: bool = True
    data: RichSignResponseData
    error: Optional[str] = None
    correlation_id: str
