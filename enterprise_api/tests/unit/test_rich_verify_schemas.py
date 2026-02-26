"""Unit tests for rich_verify_schemas.py.

Tests Pydantic schema validation, field defaults, and required field enforcement.
No database or network calls.
"""
import os
import sys
from pathlib import Path

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

import pytest
from pydantic import ValidationError

from app.schemas.rich_verify_schemas import (
    ImageVerificationResult,
    ImageVerifyRequest,
    ImageVerifyResponse,
    RichVerifyRequest,
    RichVerifyResponse,
    SignerIdentity,
    TextVerificationResult,
)


class TestRichVerifyRequest:
    """RichVerifyRequest schema validation."""

    def test_requires_document_id(self) -> None:
        """document_id is required; omitting it raises ValidationError."""
        with pytest.raises(ValidationError):
            RichVerifyRequest()  # type: ignore[call-arg]

    def test_accepts_document_id(self) -> None:
        """Valid document_id is accepted."""
        req = RichVerifyRequest(document_id="doc_abc123")
        assert req.document_id == "doc_abc123"


class TestImageVerifyRequest:
    """ImageVerifyRequest schema validation."""

    def test_requires_image_data(self) -> None:
        """image_data is required; omitting it raises ValidationError."""
        with pytest.raises(ValidationError):
            ImageVerifyRequest()  # type: ignore[call-arg]

    def test_default_mime_type(self) -> None:
        """mime_type defaults to image/jpeg."""
        req = ImageVerifyRequest(image_data="dGVzdA==")
        assert req.mime_type == "image/jpeg"

    def test_custom_mime_type(self) -> None:
        """mime_type can be overridden."""
        req = ImageVerifyRequest(image_data="dGVzdA==", mime_type="image/png")
        assert req.mime_type == "image/png"


class TestImageVerificationResult:
    """ImageVerificationResult schema defaults and construction."""

    def test_required_fields(self) -> None:
        """valid, c2pa_manifest_valid, and hash_matches are required."""
        result = ImageVerificationResult(
            valid=True,
            c2pa_manifest_valid=True,
            hash_matches=True,
        )
        assert result.valid is True
        assert result.c2pa_manifest_valid is True
        assert result.hash_matches is True

    def test_optional_fields_default_to_none(self) -> None:
        """Optional fields default to None."""
        result = ImageVerificationResult(
            valid=False,
            c2pa_manifest_valid=False,
            hash_matches=False,
        )
        assert result.image_id is None
        assert result.filename is None
        assert result.trustmark_valid is None
        assert result.c2pa_instance_id is None
        assert result.signer is None
        assert result.signed_at is None
        assert result.error is None

    def test_with_all_fields(self) -> None:
        """All optional fields can be populated."""
        result = ImageVerificationResult(
            image_id="img_deadbeef",
            filename="photo.jpg",
            valid=True,
            c2pa_manifest_valid=True,
            hash_matches=True,
            trustmark_valid=True,
            c2pa_instance_id="urn:uuid:1234",
            signer="Encypher Test Publisher",
            signed_at="2026-02-26T00:00:00Z",
            error=None,
        )
        assert result.image_id == "img_deadbeef"
        assert result.filename == "photo.jpg"
        assert result.trustmark_valid is True
        assert result.c2pa_instance_id == "urn:uuid:1234"

    def test_valid_false_with_error(self) -> None:
        """A failed verification carries an error message."""
        result = ImageVerificationResult(
            valid=False,
            c2pa_manifest_valid=False,
            hash_matches=False,
            error="No C2PA manifest found in image",
        )
        assert result.valid is False
        assert result.error == "No C2PA manifest found in image"


class TestTextVerificationResult:
    """TextVerificationResult schema defaults."""

    def test_valid_field_required(self) -> None:
        """valid is required."""
        with pytest.raises(ValidationError):
            TextVerificationResult()  # type: ignore[call-arg]

    def test_tampered_segments_defaults_to_empty(self) -> None:
        """tampered_segments defaults to an empty list."""
        result = TextVerificationResult(valid=True)
        assert result.tampered_segments == []

    def test_optional_fields(self) -> None:
        """Optional fields are None when not provided."""
        result = TextVerificationResult(valid=True)
        assert result.total_segments is None
        assert result.merkle_root_verified is None
        assert result.error is None


class TestSignerIdentity:
    """SignerIdentity schema defaults."""

    def test_defaults(self) -> None:
        """All fields have sensible defaults."""
        identity = SignerIdentity()
        assert identity.organization_id is None
        assert identity.organization_name is None
        assert identity.trust_level == "unknown"

    def test_with_values(self) -> None:
        """Values are accepted and stored."""
        identity = SignerIdentity(
            organization_id="org_abc",
            organization_name="Test Publisher",
            trust_level="signed",
        )
        assert identity.organization_id == "org_abc"
        assert identity.trust_level == "signed"


class TestRichVerifyResponse:
    """RichVerifyResponse schema construction."""

    def test_required_fields(self) -> None:
        """Required fields must be present."""
        resp = RichVerifyResponse(
            valid=True,
            verified_at="2026-02-26T00:00:00+00:00",
            document_id="doc_abc123",
            composite_manifest_valid=True,
            all_ingredients_verified=True,
            correlation_id="corr-1234",
        )
        assert resp.success is True
        assert resp.valid is True
        assert resp.document_id == "doc_abc123"
        assert resp.content_type == "rich_article"
        assert resp.image_verifications == []

    def test_missing_required_fields_raises(self) -> None:
        """Missing required fields raise ValidationError."""
        with pytest.raises(ValidationError):
            RichVerifyResponse()  # type: ignore[call-arg]


class TestImageVerifyResponse:
    """ImageVerifyResponse schema construction."""

    def test_required_fields(self) -> None:
        """Required fields must be present."""
        resp = ImageVerifyResponse(
            valid=False,
            verified_at="2026-02-26T00:00:00+00:00",
            correlation_id="corr-5678",
        )
        assert resp.success is True
        assert resp.valid is False
        assert resp.c2pa_manifest is None
        assert resp.image_id is None
        assert resp.hash is None
        assert resp.phash is None
        assert resp.error is None

    def test_missing_required_fields_raises(self) -> None:
        """Missing required fields raise ValidationError."""
        with pytest.raises(ValidationError):
            ImageVerifyResponse()  # type: ignore[call-arg]
