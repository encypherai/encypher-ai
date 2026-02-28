"""Schemas for image attribution (pHash fuzzy search) endpoint."""
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, model_validator


class ImageAttributionRequest(BaseModel):
    image_data: Optional[str] = Field(
        None,
        description=(
            "Base64-encoded image bytes. Mutually exclusive with phash."
        ),
    )
    phash: Optional[str] = Field(
        None,
        description=(
            "Pre-computed pHash as 16-char hex string. "
            "Mutually exclusive with image_data."
        ),
    )
    threshold: int = Field(
        10,
        ge=0,
        le=32,
        description="Max Hamming distance (0=exact, 10=default, 32=very loose)",
    )
    scope: Literal["org", "all"] = Field(
        "org",
        description=(
            "'org' = search within your organization (all tiers). "
            "'all' = cross-organization search (Enterprise only)."
        ),
    )

    @model_validator(mode="after")
    def check_image_data_or_phash(self) -> "ImageAttributionRequest":
        has_image_data = self.image_data is not None
        has_phash = self.phash is not None
        if not has_image_data and not has_phash:
            raise ValueError("Provide either image_data or phash")
        if has_image_data and has_phash:
            raise ValueError("Provide either image_data or phash, not both")
        return self


class ImageAttributionMatchResponse(BaseModel):
    image_id: str
    document_id: str
    organization_id: str
    filename: Optional[str]
    hamming_distance: int
    similarity_score: float
    signed_hash: str
    created_at: str


class ImageAttributionResponse(BaseModel):
    success: bool = True
    query_phash: str  # hex string of the queried pHash
    match_count: int
    matches: List[ImageAttributionMatchResponse]
    scope: str
    threshold: int
