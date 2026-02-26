"""Unit tests for image_attribution_schemas.py.

Tests Pydantic validation for ImageAttributionRequest.
"""

import os
import sys
from pathlib import Path

import pytest

# Ensure enterprise_api root is on the path before app imports
_root = Path(__file__).resolve().parents[2]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

os.environ.setdefault("KEY_ENCRYPTION_KEY", "0" * 64)
os.environ.setdefault("ENCRYPTION_NONCE", "0" * 24)
os.environ.setdefault(
    "CORE_DATABASE_URL",
    "postgresql+asyncpg://encypher:encypher_dev_password@127.0.0.1:15432/encypher_content",
)
os.environ.setdefault(
    "CONTENT_DATABASE_URL",
    "postgresql+asyncpg://encypher:encypher_dev_password@127.0.0.1:15432/encypher_content",
)
os.environ.setdefault("DATABASE_URL", os.environ["CORE_DATABASE_URL"])

from pydantic import ValidationError

from app.schemas.image_attribution_schemas import (
    ImageAttributionMatchResponse,
    ImageAttributionRequest,
    ImageAttributionResponse,
)


class TestImageAttributionRequestValidation:
    """Tests for ImageAttributionRequest mutual exclusion and field constraints."""

    def test_both_image_data_and_phash_raises(self) -> None:
        """Providing both image_data and phash raises ValidationError."""
        with pytest.raises(ValidationError):
            ImageAttributionRequest(
                image_data="aGVsbG8=",
                phash="a1b2c3d4e5f67890",
                threshold=10,
                scope="org",
            )

    def test_neither_image_data_nor_phash_raises(self) -> None:
        """Providing neither image_data nor phash raises ValidationError."""
        with pytest.raises(ValidationError):
            ImageAttributionRequest(
                threshold=10,
                scope="org",
            )

    def test_only_image_data_valid(self) -> None:
        """Providing only image_data is valid."""
        req = ImageAttributionRequest(image_data="aGVsbG8=")
        assert req.image_data == "aGVsbG8="
        assert req.phash is None

    def test_only_phash_valid(self) -> None:
        """Providing only phash is valid."""
        req = ImageAttributionRequest(phash="a1b2c3d4e5f67890")
        assert req.phash == "a1b2c3d4e5f67890"
        assert req.image_data is None

    def test_threshold_default_is_10(self) -> None:
        """Default threshold is 10."""
        req = ImageAttributionRequest(phash="a1b2c3d4e5f67890")
        assert req.threshold == 10

    def test_threshold_zero_valid(self) -> None:
        """threshold=0 is valid (exact match only)."""
        req = ImageAttributionRequest(phash="a1b2c3d4e5f67890", threshold=0)
        assert req.threshold == 0

    def test_threshold_32_valid(self) -> None:
        """threshold=32 is the maximum valid value."""
        req = ImageAttributionRequest(phash="a1b2c3d4e5f67890", threshold=32)
        assert req.threshold == 32

    def test_threshold_33_invalid(self) -> None:
        """threshold=33 exceeds maximum of 32 and raises ValidationError."""
        with pytest.raises(ValidationError):
            ImageAttributionRequest(phash="a1b2c3d4e5f67890", threshold=33)

    def test_threshold_negative_invalid(self) -> None:
        """Negative threshold raises ValidationError."""
        with pytest.raises(ValidationError):
            ImageAttributionRequest(phash="a1b2c3d4e5f67890", threshold=-1)

    def test_scope_org_valid(self) -> None:
        """scope='org' is valid."""
        req = ImageAttributionRequest(phash="a1b2c3d4e5f67890", scope="org")
        assert req.scope == "org"

    def test_scope_all_valid(self) -> None:
        """scope='all' is valid."""
        req = ImageAttributionRequest(phash="a1b2c3d4e5f67890", scope="all")
        assert req.scope == "all"

    def test_scope_invalid_raises(self) -> None:
        """An unknown scope value raises ValidationError."""
        with pytest.raises(ValidationError):
            ImageAttributionRequest(phash="a1b2c3d4e5f67890", scope="bad")

    def test_scope_default_is_org(self) -> None:
        """Default scope is 'org'."""
        req = ImageAttributionRequest(phash="a1b2c3d4e5f67890")
        assert req.scope == "org"


class TestImageAttributionMatchResponse:
    """Tests for ImageAttributionMatchResponse schema."""

    def test_valid_match_response(self) -> None:
        """ImageAttributionMatchResponse accepts all required fields."""
        resp = ImageAttributionMatchResponse(
            image_id="img_001",
            document_id="doc_001",
            organization_id="org_001",
            filename="photo.jpg",
            hamming_distance=5,
            similarity_score=0.9219,
            signed_hash="sha256:deadbeef",
            created_at="2026-01-01T12:00:00",
        )
        assert resp.image_id == "img_001"
        assert resp.filename == "photo.jpg"
        assert resp.hamming_distance == 5

    def test_filename_can_be_none(self) -> None:
        """filename is Optional and can be None."""
        resp = ImageAttributionMatchResponse(
            image_id="img_002",
            document_id="doc_002",
            organization_id="org_002",
            filename=None,
            hamming_distance=0,
            similarity_score=1.0,
            signed_hash="sha256:aabbcc",
            created_at="2026-01-01T00:00:00",
        )
        assert resp.filename is None


class TestImageAttributionResponse:
    """Tests for the top-level ImageAttributionResponse schema."""

    def test_valid_response_with_matches(self) -> None:
        """ImageAttributionResponse serializes a list of matches."""
        match = ImageAttributionMatchResponse(
            image_id="img_001",
            document_id="doc_001",
            organization_id="org_001",
            filename=None,
            hamming_distance=3,
            similarity_score=0.9531,
            signed_hash="sha256:abc123",
            created_at="2026-01-01T00:00:00",
        )
        resp = ImageAttributionResponse(
            success=True,
            query_phash="a1b2c3d4e5f67890",
            match_count=1,
            matches=[match],
            scope="org",
            threshold=10,
        )
        assert resp.success is True
        assert resp.match_count == 1
        assert resp.query_phash == "a1b2c3d4e5f67890"
        assert len(resp.matches) == 1

    def test_empty_matches_response(self) -> None:
        """ImageAttributionResponse with no matches is valid."""
        resp = ImageAttributionResponse(
            success=True,
            query_phash="0000000000000000",
            match_count=0,
            matches=[],
            scope="all",
            threshold=8,
        )
        assert resp.match_count == 0
        assert resp.matches == []
