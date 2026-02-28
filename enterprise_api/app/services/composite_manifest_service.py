"""Composite manifest service for article-level C2PA provenance.

Builds the article-level C2PA manifest that binds signed text and signed images
into a single provenance unit. Each image is referenced as an ingredient.
"""
import hashlib
import json
import uuid
from dataclasses import dataclass
from typing import List


@dataclass
class ImageIngredient:
    """Reference to a signed image to include as a C2PA ingredient."""

    image_id: str
    filename: str
    mime_type: str
    c2pa_instance_id: str  # URN UUID of the image's own C2PA manifest
    signed_hash: str  # "sha256:..." of the signed image binary
    position: int


@dataclass
class CompositeManifestResult:
    """Result of building a composite manifest."""

    instance_id: str  # "urn:uuid:..." for the composite manifest
    manifest_data: dict  # Full manifest JSON
    manifest_hash: str  # "sha256:..." of json.dumps(manifest_data)
    ingredient_count: int


def build_composite_manifest(
    *,
    document_id: str,
    org_id: str,
    document_title: str,
    text_merkle_root: str,  # from text signing result
    text_instance_id: str,  # C2PA instance_id of the text manifest
    images: List[ImageIngredient],
) -> CompositeManifestResult:
    """
    Build the article-level C2PA manifest that binds text + images.

    Each image is referenced as a c2pa.ingredient with:
    - title: image filename
    - format: MIME type
    - instanceId: the image's own C2PA manifest URN
    - hash: sha256 of signed image bytes
    - relationship: "componentOf"

    Args:
        document_id: Unique document identifier.
        org_id: Organization identifier.
        document_title: Human-readable document title.
        text_merkle_root: Merkle root hash from the text signing pipeline.
        text_instance_id: C2PA instance_id from the text signing result.
        images: List of ImageIngredient objects for each signed image.

    Returns:
        CompositeManifestResult with instance_id, manifest_data, manifest_hash,
        and ingredient_count.
    """
    composite_id = "urn:uuid:" + str(uuid.uuid4())

    # Build ingredient list, sorted by position for stable ordering
    ingredients = []
    for img in sorted(images, key=lambda x: x.position):
        ingredients.append({
            "title": img.filename or f"image_{img.position}",
            "format": img.mime_type,
            "instanceId": img.c2pa_instance_id,
            "relationship": "componentOf",
            "hash": img.signed_hash,
        })

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
                    "ingredient_count": len(images),
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
        ingredient_count=len(images),
    )
