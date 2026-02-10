# TEAM_153: Enterprise API signing integration
"""Sign document text using the EncypherAI enterprise API."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Optional

import httpx

# Default API URL — override with ENCYPHER_API_URL env var
DEFAULT_API_URL = "http://localhost:8000"
SIGN_ENDPOINT = "/api/v1/sign"

# Embedding modes we support
EMBEDDING_MODES = {
    "c2pa_full": {
        "label": "Default C2PA (full manifest)",
        "manifest_mode": "full",
        "segmentation_level": "document",
    },
    "lightweight": {
        "label": "Lightweight UUID manifest",
        "manifest_mode": "lightweight_uuid",
        "segmentation_level": "sentence",
    },
    "minimal": {
        "label": "Minimal UUID per-sentence",
        "manifest_mode": "minimal_uuid",
        "segmentation_level": "sentence",
    },
    "zw_sentence": {
        "label": "ZW embedding (sentence-level)",
        "manifest_mode": "zw_embedding",
        "segmentation_level": "sentence",
    },
    "zw_document": {
        "label": "ZW embedding (document-level)",
        "manifest_mode": "zw_embedding",
        "segmentation_level": "document",
    },
}


@dataclass
class SignResult:
    """Result of a signing operation."""

    mode: str
    signed_text: str
    document_id: str
    verification_url: str
    total_segments: int
    merkle_root: Optional[str] = None
    instance_id: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None
    raw_response: Optional[dict[str, Any]] = None


class SigningError(Exception):
    """Raised when the enterprise API returns an error."""


def get_api_url() -> str:
    return os.environ.get("ENCYPHER_API_URL", DEFAULT_API_URL)


def get_api_key() -> str:
    key = os.environ.get("ENCYPHER_API_KEY", "")
    if not key:
        raise SigningError(
            "ENCYPHER_API_KEY environment variable is required. "
            "Set it to your enterprise API key."
        )
    return key


def sign_text(
    text: str,
    document_title: str,
    mode: str,
    *,
    api_url: str | None = None,
    api_key: str | None = None,
    timeout: float = 60.0,
) -> SignResult:
    """
    Sign text using the enterprise API with the specified embedding mode.

    Args:
        text: Plain text content to sign.
        document_title: Title for the document.
        mode: One of the EMBEDDING_MODES keys.
        api_url: Override API base URL.
        api_key: Override API key.
        timeout: Request timeout in seconds.

    Returns:
        SignResult with signed text and metadata.
    """
    if mode not in EMBEDDING_MODES:
        raise SigningError(
            f"Unknown mode '{mode}'. Valid modes: {', '.join(EMBEDDING_MODES)}"
        )

    mode_config = EMBEDDING_MODES[mode]
    url = (api_url or get_api_url()).rstrip("/") + SIGN_ENDPOINT
    key = api_key or get_api_key()

    payload = {
        "text": text,
        "document_title": document_title,
        "options": {
            "document_type": "article",
            "manifest_mode": mode_config["manifest_mode"],
            "segmentation_level": mode_config["segmentation_level"],
            "embedding_strategy": "single_point",
            "action": "c2pa.created",
        },
    }

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

    with httpx.Client(timeout=timeout) as client:
        resp = client.post(url, json=payload, headers=headers)

    if resp.status_code != 201:
        raise SigningError(
            f"API returned {resp.status_code}: {resp.text}"
        )

    data = resp.json()

    # Navigate response: {"success": true, "data": {"document": {...}}}
    doc = _extract_document(data)

    return SignResult(
        mode=mode,
        signed_text=doc.get("signed_text", ""),
        document_id=doc.get("document_id", ""),
        verification_url=doc.get("verification_url", ""),
        total_segments=doc.get("total_segments", 0),
        merkle_root=doc.get("merkle_root"),
        instance_id=doc.get("instance_id"),
        metadata=doc.get("metadata"),
        raw_response=data,
    )


def sign_all_modes(
    text: str,
    document_title: str,
    *,
    api_url: str | None = None,
    api_key: str | None = None,
    modes: list[str] | None = None,
) -> dict[str, SignResult]:
    """
    Sign text with all (or specified) embedding modes.

    Returns a dict mapping mode name to SignResult.
    Failed modes are logged but don't stop other modes.
    """
    target_modes = modes or list(EMBEDDING_MODES.keys())
    results: dict[str, SignResult] = {}

    for mode in target_modes:
        try:
            result = sign_text(
                text,
                document_title,
                mode,
                api_url=api_url,
                api_key=api_key,
            )
            results[mode] = result
        except SigningError as e:
            print(f"  Warning: mode '{mode}' failed: {e}")

    return results


def _extract_document(data: dict[str, Any]) -> dict[str, Any]:
    """Extract the document result from the API response, handling nesting."""
    # Try data.data.document (double-nested)
    if "data" in data and isinstance(data["data"], dict):
        inner = data["data"]
        if "document" in inner and isinstance(inner["document"], dict):
            return inner["document"]
        # Flat data.data with signed_text directly
        if "signed_text" in inner:
            return inner

    # Try data.document
    if "document" in data and isinstance(data["document"], dict):
        return data["document"]

    # Flat response with signed_text
    if "signed_text" in data:
        return data

    raise SigningError(
        f"Could not find signed document in API response. Keys: {list(data.keys())}"
    )
