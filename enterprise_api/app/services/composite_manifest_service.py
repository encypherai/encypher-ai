"""Composite manifest service for article-level C2PA provenance.

Builds the article-level C2PA manifest that binds signed text and signed media
(images, audio, video) into a single provenance unit. Each media file is
referenced as an ingredient.
"""

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from typing import List


@dataclass
class MediaIngredient:
    """Reference to a signed media file to include as a C2PA ingredient."""

    asset_id: str  # image_id, audio_id, or video_id
    filename: str
    mime_type: str
    media_type: str  # "image", "audio", or "video"
    c2pa_instance_id: str  # URN UUID of the media's own C2PA manifest
    signed_hash: str  # "sha256:..." of the signed binary
    position: int


# Keep ImageIngredient as an alias for backward compatibility with callers
# that haven't migrated yet (e.g. CDN provenance service).
ImageIngredient = MediaIngredient


@dataclass
class CompositeManifestResult:
    """Result of building a composite manifest."""

    instance_id: str  # "urn:uuid:..." for the composite manifest
    manifest_data: dict  # Full manifest JSON
    manifest_hash: str  # "sha256:..." of json.dumps(manifest_data)
    ingredient_count: int
    image_count: int = 0
    audio_count: int = 0
    video_count: int = 0


def build_composite_manifest(
    *,
    document_id: str,
    org_id: str,
    document_title: str,
    text_merkle_root: str,
    text_instance_id: str,
    images: List[MediaIngredient] | None = None,
    audios: List[MediaIngredient] | None = None,
    videos: List[MediaIngredient] | None = None,
) -> CompositeManifestResult:
    """Build the article-level C2PA manifest that binds text + media.

    Each media file is referenced as a c2pa.ingredient with:
    - title: filename
    - format: MIME type
    - instanceId: the media's own C2PA manifest URN
    - hash: sha256 of signed bytes
    - relationship: "componentOf"
    - mediaType: "image", "audio", or "video"

    Args:
        document_id: Unique document identifier.
        org_id: Organization identifier.
        document_title: Human-readable document title.
        text_merkle_root: Merkle root hash from the text signing pipeline.
        text_instance_id: C2PA instance_id from the text signing result.
        images: Signed image ingredients.
        audios: Signed audio ingredients.
        videos: Signed video ingredients.

    Returns:
        CompositeManifestResult with instance_id, manifest_data, manifest_hash,
        ingredient counts by type, and total ingredient_count.
    """
    images = images or []
    audios = audios or []
    videos = videos or []

    composite_id = "urn:uuid:" + str(uuid.uuid4())

    # Build ingredient list: images first, then audios, then videos,
    # each group sorted by position for stable ordering.
    all_media: List[MediaIngredient] = []
    all_media.extend(sorted(images, key=lambda x: x.position))
    all_media.extend(sorted(audios, key=lambda x: x.position))
    all_media.extend(sorted(videos, key=lambda x: x.position))

    ingredients = []
    for item in all_media:
        fallback_name = f"{item.media_type}_{item.position}"
        ingredients.append(
            {
                "title": item.filename or fallback_name,
                "format": item.mime_type,
                "instanceId": item.c2pa_instance_id,
                "relationship": "componentOf",
                "hash": item.signed_hash,
                "mediaType": item.media_type,
            }
        )

    total_count = len(all_media)

    manifest_data = {
        "claim_generator": "encypher-ai/1.0",
        "instance_id": composite_id,
        "title": document_title,
        "document_id": document_id,
        "assertions": [
            {
                "label": "c2pa.actions",
                "data": {
                    "actions": [{"action": "c2pa.created"}],
                },
            },
            {
                "label": "com.encypher.article",
                "data": {
                    "text_merkle_root": text_merkle_root,
                    "text_instance_id": text_instance_id,
                    "ingredient_count": total_count,
                    "image_count": len(images),
                    "audio_count": len(audios),
                    "video_count": len(videos),
                    "document_id": document_id,
                    "organization_id": org_id,
                },
            },
        ],
        "ingredients": ingredients,
    }

    manifest_json = json.dumps(manifest_data, sort_keys=True, separators=(",", ":"))
    manifest_hash = "sha256:" + hashlib.sha256(manifest_json.encode()).hexdigest()

    return CompositeManifestResult(
        instance_id=composite_id,
        manifest_data=manifest_data,
        manifest_hash=manifest_hash,
        ingredient_count=total_count,
        image_count=len(images),
        audio_count=len(audios),
        video_count=len(videos),
    )
