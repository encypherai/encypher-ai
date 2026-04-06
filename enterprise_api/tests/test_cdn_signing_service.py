"""Tests for CDN Edge Provenance Worker signing service.

Tests the service utilities, cross-channel org resolution, and signing flow
without requiring a live database (mocked async session).
"""

import hashlib
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.cdn_signing_service import (
    FREE_TIER_MONTHLY_QUOTA,
    _build_sign_options_for_org,
    _generate_cdn_org_id,
    _generate_prebid_org_id,
    extract_domain,
    hash_content,
)


# ---------------------------------------------------------------------------
# Unit tests: pure utility functions
# ---------------------------------------------------------------------------


class TestExtractDomain:
    def test_basic_url(self):
        assert extract_domain("https://example.com/article/1") == "example.com"

    def test_strips_www(self):
        assert extract_domain("https://www.nytimes.com/2026/04/article") == "nytimes.com"

    def test_preserves_subdomain(self):
        assert extract_domain("https://blog.example.com/post") == "blog.example.com"

    def test_lowercases(self):
        assert extract_domain("https://WWW.EXAMPLE.COM/Page") == "example.com"

    def test_no_path(self):
        assert extract_domain("https://example.com") == "example.com"

    def test_empty_string(self):
        assert extract_domain("") == ""

    def test_malformed_url(self):
        # urlparse handles gracefully
        result = extract_domain("not-a-url")
        assert result == ""


class TestHashContent:
    def test_returns_sha256_prefix(self):
        result = hash_content("hello world")
        assert result.startswith("sha256:")
        assert len(result) == 71  # "sha256:" (7) + 64 hex chars

    def test_deterministic(self):
        assert hash_content("test") == hash_content("test")

    def test_different_content_different_hash(self):
        assert hash_content("foo") != hash_content("bar")


class TestOrgIdGeneration:
    def test_cdn_org_id_format(self):
        org_id = _generate_cdn_org_id("example.com")
        assert org_id.startswith("org_cdn_")
        assert len(org_id) == len("org_cdn_") + 12

    def test_prebid_org_id_format(self):
        org_id = _generate_prebid_org_id("example.com")
        assert org_id.startswith("org_prebid_")
        assert len(org_id) == len("org_prebid_") + 12

    def test_deterministic(self):
        assert _generate_cdn_org_id("example.com") == _generate_cdn_org_id("example.com")

    def test_different_domains_different_ids(self):
        assert _generate_cdn_org_id("foo.com") != _generate_cdn_org_id("bar.com")

    def test_cdn_and_prebid_differ(self):
        assert _generate_cdn_org_id("example.com") != _generate_prebid_org_id("example.com")


class TestBuildSignOptions:
    def test_free_tier_defaults(self):
        opts = _build_sign_options_for_org(None)
        assert opts.manifest_mode == "micro"
        assert opts.ecc is True
        assert opts.embed_c2pa is True
        assert opts.segmentation_level == "sentence"
        assert opts.include_fingerprint is False
        assert opts.add_dual_binding is False

    def test_enterprise_tier_adds_features(self):
        mock_org = MagicMock()
        mock_org.tier = "enterprise"
        opts = _build_sign_options_for_org(mock_org)
        assert opts.include_fingerprint is True
        assert opts.add_dual_binding is True
        # Core signing config unchanged
        assert opts.manifest_mode == "micro"
        assert opts.ecc is True

    def test_free_tier_org(self):
        mock_org = MagicMock()
        mock_org.tier = "free"
        opts = _build_sign_options_for_org(mock_org)
        assert opts.include_fingerprint is False
        assert opts.add_dual_binding is False


# ---------------------------------------------------------------------------
# Schema tests
# ---------------------------------------------------------------------------


class TestCdnSchemas:
    def test_sign_request_validation(self):
        from app.schemas.cdn_content_schemas import CdnSignRequest

        req = CdnSignRequest(
            text="A" * 50,
            page_url="https://example.com/article",
        )
        assert req.text == "A" * 50
        assert req.page_url == "https://example.com/article"
        assert req.org_id is None

    def test_sign_request_min_length(self):
        from app.schemas.cdn_content_schemas import CdnSignRequest

        with pytest.raises(Exception):
            CdnSignRequest(text="short", page_url="https://example.com")

    def test_provision_request(self):
        from app.schemas.cdn_content_schemas import CdnProvisionRequest

        req = CdnProvisionRequest(domain="example.com", worker_version="1.0.0")
        assert req.domain == "example.com"

    def test_sign_response(self):
        from app.schemas.cdn_content_schemas import CdnSignResponse

        resp = CdnSignResponse(
            success=True,
            embedding_plan={"index_unit": "codepoint", "operations": []},
            document_id="doc_123",
            verification_url="https://api.encypher.com/verify/doc_123",
            content_hash="sha256:abc123",
            org_id="org_cdn_abc123def456",
            signer_tier="encypher_free",
            cached=False,
        )
        assert resp.success is True
        assert resp.embedding_plan is not None

    def test_sign_response_failure(self):
        from app.schemas.cdn_content_schemas import CdnSignResponse

        resp = CdnSignResponse(
            success=False,
            error="quota_exceeded",
            org_id="org_cdn_abc123def456",
            upgrade_url="https://encypher.com/enterprise?ref=cdn&domain=example.com",
        )
        assert resp.success is False
        assert resp.error == "quota_exceeded"


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------


class TestCdnContentRecordModel:
    def test_model_creation(self):
        from datetime import datetime

        from app.models.cdn_content_record import CdnContentRecord

        record = CdnContentRecord(
            organization_id="org_cdn_abc123def456",
            domain="example.com",
            canonical_url="https://example.com/article/1",
            content_hash="sha256:" + "a" * 64,
            embedding_plan={"index_unit": "codepoint", "operations": []},
            signer_tier="encypher_free",
            boundary_selector="article",
            signed_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
        )
        assert record.domain == "example.com"
        assert record.embedding_plan["index_unit"] == "codepoint"
        assert record.boundary_selector == "article"

    def test_repr(self):
        from app.models.cdn_content_record import CdnContentRecord

        record = CdnContentRecord(
            organization_id="org_cdn_test",
            domain="test.com",
            content_hash="sha256:" + "b" * 64,
        )
        repr_str = repr(record)
        assert "CdnContentRecord" in repr_str
        assert "test.com" in repr_str
