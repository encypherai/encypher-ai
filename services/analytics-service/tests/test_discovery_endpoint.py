"""Tests for the discovery analytics schemas and endpoint logic."""

import sys
import os

# Add the analytics-service directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test-safe defaults for pydantic settings used by endpoint imports
os.environ.setdefault("DATABASE_URL", "sqlite:///./analytics_service_test.db")
os.environ.setdefault("AUTH_SERVICE_URL", "http://auth-service:8001")

import pytest  # noqa: E402
from datetime import datetime  # noqa: E402
from pydantic import ValidationError  # noqa: E402
from pathlib import Path  # noqa: E402

# Import schemas directly for unit tests
from app.models.schemas import DiscoveryEvent, DiscoveryBatchRequest, DiscoveryResponse, DiscoveryStats  # noqa: E402
from app.api.v1.endpoints import _should_verify_auth_header  # noqa: E402


@pytest.fixture
def sample_discovery_event_data():
    """Sample discovery event data."""
    return {
        "timestamp": datetime.utcnow(),
        "eventType": "embedding_discovered",
        "pageUrl": "https://example.com/article/test-article",
        "pageDomain": "example.com",
        "pageTitle": "Test Article",
        "signerId": "org_123",
        "signerName": "Test Organization",
        "organizationId": "org_123",
        "documentId": "doc_456",
        "verified": True,
        "verificationStatus": "verified",
        "markerType": "c2pa",
        "embeddingCount": 1,
        "extensionVersion": "1.0.0",
        "sessionId": "sess_abc123",
    }


class TestDiscoveryEventSchema:
    """Tests for DiscoveryEvent schema validation."""

    def test_valid_event(self, sample_discovery_event_data):
        """Test valid event passes validation."""
        event = DiscoveryEvent(**sample_discovery_event_data)
        assert event.pageUrl == sample_discovery_event_data["pageUrl"]
        assert event.verified is True

    def test_minimal_event(self):
        """Test minimal required fields."""
        event = DiscoveryEvent(timestamp=datetime.utcnow(), pageUrl="https://example.com", pageDomain="example.com")
        assert event.verified is False
        assert event.embeddingCount == 1

    def test_event_defaults(self):
        """Test default values are applied."""
        event = DiscoveryEvent(timestamp=datetime.utcnow(), pageUrl="https://example.com", pageDomain="example.com")
        assert event.eventType == "embedding_discovered"
        assert event.verified is False
        assert event.embeddingCount == 1

    def test_event_with_all_fields(self, sample_discovery_event_data):
        """Test event with all fields populated."""
        event = DiscoveryEvent(**sample_discovery_event_data)
        assert event.signerId == "org_123"
        assert event.signerName == "Test Organization"
        assert event.organizationId == "org_123"
        assert event.documentId == "doc_456"
        assert event.markerType == "c2pa"

    def test_event_accepts_privacy_safe_context_fields(self, sample_discovery_event_data):
        """Discovery schema should allow non-PII context fields used for mismatch analytics."""
        enriched = {
            **sample_discovery_event_data,
            "domainMismatch": True,
            "mismatchReason": "original_domain_mismatch",
            "discoverySource": "page_scan",
            "contentLengthBucket": "medium",
            "embeddingByteLength": 256,
        }

        event = DiscoveryEvent(**enriched)
        assert event.domainMismatch is True
        assert event.mismatchReason == "original_domain_mismatch"
        assert event.discoverySource == "page_scan"
        assert event.contentLengthBucket == "medium"
        assert event.embeddingByteLength == 256

    def test_invalid_event_missing_required(self):
        """Test event fails without required fields."""
        with pytest.raises(ValidationError):
            DiscoveryEvent(
                timestamp=datetime.utcnow(),
                # Missing pageUrl and pageDomain
            )


class TestDiscoveryBatchRequest:
    """Tests for DiscoveryBatchRequest schema."""

    def test_valid_batch(self, sample_discovery_event_data):
        """Test valid batch request."""
        batch = DiscoveryBatchRequest(events=[DiscoveryEvent(**sample_discovery_event_data)], source="chrome_extension", version="1.0.0")
        assert len(batch.events) == 1
        assert batch.source == "chrome_extension"

    def test_batch_defaults(self, sample_discovery_event_data):
        """Test batch default values."""
        batch = DiscoveryBatchRequest(events=[DiscoveryEvent(**sample_discovery_event_data)])
        assert batch.source == "chrome_extension"
        assert batch.version is None

    def test_batch_multiple_events(self, sample_discovery_event_data):
        """Test batch with multiple events."""
        events = [DiscoveryEvent(**sample_discovery_event_data) for _ in range(5)]
        batch = DiscoveryBatchRequest(events=events)
        assert len(batch.events) == 5

    def test_empty_batch(self):
        """Test batch with empty events list."""
        batch = DiscoveryBatchRequest(events=[])
        assert len(batch.events) == 0


class TestDiscoveryResponse:
    """Tests for DiscoveryResponse schema."""

    def test_success_response(self):
        """Test successful response."""
        response = DiscoveryResponse(success=True, data={"events_recorded": 5, "message": "Success"}, error=None)
        assert response.success is True
        assert response.data["events_recorded"] == 5

    def test_error_response(self):
        """Test error response."""
        response = DiscoveryResponse(success=False, data=None, error="Rate limit exceeded")
        assert response.success is False
        assert response.error == "Rate limit exceeded"


class TestDiscoveryStats:
    """Tests for DiscoveryStats schema."""

    def test_stats_schema(self):
        """Test stats schema with sample data."""
        stats = DiscoveryStats(
            total_discoveries=100,
            verified_count=85,
            invalid_count=15,
            unique_domains=25,
            unique_signers=10,
            top_domains=[{"domain": "example.com", "count": 50}],
            top_signers=[{"signer_id": "org_123", "signer_name": "Test Org", "count": 30}],
            period_start=datetime.utcnow(),
            period_end=datetime.utcnow(),
        )
        assert stats.total_discoveries == 100
        assert stats.verified_count == 85
        assert len(stats.top_domains) == 1
        assert len(stats.top_signers) == 1


class TestDiscoveryAuthHeaderVerification:
    """Tests for auth header verification gating on discovery endpoint."""

    def test_skips_non_jwt_bearer_api_key(self):
        """Bearer API keys should not be sent to auth verify endpoint."""
        assert _should_verify_auth_header("Bearer enc_live_test_key") is False

    def test_accepts_bearer_jwt(self):
        """JWT-shaped bearer tokens should be verified."""
        assert _should_verify_auth_header("Bearer header.payload.signature") is True

    def test_rejects_missing_bearer_prefix(self):
        """Headers without Bearer prefix should be ignored for verification."""
        assert _should_verify_auth_header("enc_live_test_key") is False

    def test_rejects_empty_value(self):
        """Empty headers should be ignored for verification."""
        assert _should_verify_auth_header("") is False


class TestDiscoveryPrivacyMetadata:
    """Privacy guardrails for discovery metadata persistence."""

    def test_endpoint_does_not_persist_client_ip_in_metric_metadata(self):
        """IP may be used for rate limiting but should not be stored in metric metadata."""
        endpoints_path = Path(__file__).resolve().parents[1] / "app" / "api" / "v1" / "endpoints.py"
        endpoints_code = endpoints_path.read_text(encoding="utf-8")
        assert '"client_ip"' not in endpoints_code
