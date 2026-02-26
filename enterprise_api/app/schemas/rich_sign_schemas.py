"""Pydantic schemas for rich article signing (text + embedded images)."""
import base64
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, model_validator

SUPPORTED_MIME_TYPES = frozenset({
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "image/tiff",
})


class RichContentImage(BaseModel):
    data: str = Field(..., description="Base64-encoded image bytes")
    filename: str = Field(..., description="Original filename e.g. photo1.jpg")
    mime_type: str = Field(..., description="MIME type of the image")
    position: int = Field(0, ge=0, description="Order of this image within the article")
    alt_text: Optional[str] = Field(None, max_length=500)
    metadata: Optional[dict] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_image_data(self) -> "RichContentImage":
        # Validate base64 decodes
        try:
            raw = base64.b64decode(self.data, validate=True)
        except Exception as e:
            raise ValueError(f"image data is not valid base64: {e}") from e
        # Validate size (10MB limit)
        if len(raw) > 10_485_760:
            raise ValueError(
                f"Image {self.filename!r} exceeds 10MB limit ({len(raw)} bytes)"
            )
        # Validate MIME type
        if self.mime_type.lower() not in SUPPORTED_MIME_TYPES:
            raise ValueError(
                f"Unsupported MIME type: {self.mime_type!r}. "
                f"Supported: {sorted(SUPPORTED_MIME_TYPES)}"
            )
        return self


class RichSignOptions(BaseModel):
    segmentation_level: str = "sentence"
    manifest_mode: str = "micro"
    action: str = "c2pa.created"
    enable_trustmark: bool = False  # Enterprise only
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
    images: List[RichContentImage] = Field(..., min_length=1, max_length=20)
    options: RichSignOptions = Field(default_factory=RichSignOptions)
    publisher_org_id: Optional[str] = None  # proxy signing


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


class CompositeManifestSummary(BaseModel):
    instance_id: str
    ingredient_count: int
    manifest_hash: str


class RichSignResponseData(BaseModel):
    document_id: str
    content_type: str = "rich_article"
    text: dict  # SignedDocumentResult as dict
    images: List[SignedImageResult]
    composite_manifest: CompositeManifestSummary
    total_images: int
    processing_time_ms: float


class RichSignResponse(BaseModel):
    success: bool = True
    data: RichSignResponseData
    error: Optional[str] = None
    correlation_id: str
