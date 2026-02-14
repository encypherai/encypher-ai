"""Tests for the DiscoveryService business logic."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import Base, ContentDiscovery, DiscoveryDomainSummary, OwnedDomain
from app.models.schemas import DiscoveryEvent
from app.services.discovery_service import DiscoveryService, domain_matches_pattern


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def sample_event():
    """Sample discovery event."""
    return DiscoveryEvent(
        timestamp=datetime.now(timezone.utc),
        eventType="embedding_discovered",
        pageUrl="https://example.com/article/test",
        pageDomain="example.com",
        pageTitle="Test Article",
        signerId="signer_123",
        signerName="Test Publisher",
        organizationId="org_456",
        documentId="doc_789",
        verified=True,
        verificationStatus="verified",
        markerType="c2pa",
        embeddingCount=1,
        extensionVersion="1.0.0",
        sessionId="sess_abc123",
    )


class TestRecordDiscovery:
    """Tests for recording individual discovery events."""

    def test_record_basic_discovery(self, db_session, sample_event):
        """Test recording a basic discovery event."""
        result = DiscoveryService.record_discovery(db_session, sample_event)

        assert result.id is not None
        assert result.page_url == "https://example.com/article/test"
        assert result.page_domain == "example.com"
        assert result.page_title == "Test Article"
        assert result.signer_id == "signer_123"
        assert result.signer_name == "Test Publisher"
        assert result.organization_id == "org_456"
        assert result.document_id == "doc_789"
        assert result.verified == 1
        assert result.verification_status == "verified"
        assert result.marker_type == "c2pa"
        assert result.session_id == "sess_abc123"
        assert result.source == "chrome_extension"

    def test_record_unverified_discovery(self, db_session):
        """Test recording an unverified discovery."""
        event = DiscoveryEvent(
            timestamp=datetime.now(timezone.utc),
            pageUrl="https://example.com/page",
            pageDomain="example.com",
            verified=False,
            verificationStatus="invalid",
        )
        result = DiscoveryService.record_discovery(db_session, event)
        assert result.verified == 0
        assert result.verification_status == "invalid"

    def test_record_creates_domain_summary(self, db_session, sample_event):
        """Test that recording a discovery creates a domain summary."""
        DiscoveryService.record_discovery(db_session, sample_event)

        summaries = db_session.query(DiscoveryDomainSummary).all()
        assert len(summaries) == 1
        assert summaries[0].organization_id == "org_456"
        assert summaries[0].page_domain == "example.com"
        assert summaries[0].discovery_count == 1
        assert summaries[0].verified_count == 1
        assert summaries[0].invalid_count == 0

    def test_first_domain_marked_as_owned(self, db_session, sample_event):
        """Test that the first domain seen for an org is marked as owned."""
        DiscoveryService.record_discovery(db_session, sample_event)

        summary = db_session.query(DiscoveryDomainSummary).first()
        assert summary.is_owned_domain == 1

    def test_second_domain_marked_as_external(self, db_session, sample_event):
        """Test that a second domain is marked as external."""
        # First discovery on owned domain
        DiscoveryService.record_discovery(db_session, sample_event)

        # Second discovery on different domain
        external_event = DiscoveryEvent(
            timestamp=datetime.now(timezone.utc),
            pageUrl="https://copier-site.com/stolen-article",
            pageDomain="copier-site.com",
            signerId="signer_123",
            organizationId="org_456",
            verified=True,
            verificationStatus="verified",
        )
        result = DiscoveryService.record_discovery(db_session, external_event)

        assert result.is_external_domain == 1

        summaries = db_session.query(DiscoveryDomainSummary).all()
        assert len(summaries) == 2

        owned = [s for s in summaries if s.is_owned_domain == 1]
        external = [s for s in summaries if s.is_owned_domain == 0]
        assert len(owned) == 1
        assert owned[0].page_domain == "example.com"
        assert len(external) == 1
        assert external[0].page_domain == "copier-site.com"

    def test_same_domain_increments_count(self, db_session, sample_event):
        """Test that repeated discoveries on the same domain increment the count."""
        DiscoveryService.record_discovery(db_session, sample_event)
        DiscoveryService.record_discovery(db_session, sample_event)
        DiscoveryService.record_discovery(db_session, sample_event)

        summary = db_session.query(DiscoveryDomainSummary).first()
        assert summary.discovery_count == 3
        assert summary.verified_count == 3

    def test_no_org_id_skips_domain_summary(self, db_session):
        """Test that events without an org ID don't create domain summaries."""
        event = DiscoveryEvent(
            timestamp=datetime.now(timezone.utc),
            pageUrl="https://example.com/page",
            pageDomain="example.com",
            verified=True,
        )
        DiscoveryService.record_discovery(db_session, event)

        summaries = db_session.query(DiscoveryDomainSummary).all()
        assert len(summaries) == 0


class TestRecordBatch:
    """Tests for batch recording."""

    def test_record_batch(self, db_session, sample_event):
        """Test recording a batch of events."""
        events = [sample_event, sample_event, sample_event]
        count = DiscoveryService.record_batch(db_session, events)
        assert count == 3

        discoveries = db_session.query(ContentDiscovery).all()
        assert len(discoveries) == 3

    def test_record_empty_batch(self, db_session):
        """Test recording an empty batch."""
        count = DiscoveryService.record_batch(db_session, [])
        assert count == 0


class TestDomainMismatchDetection:
    """Tests for domain-mismatch detection logic."""

    def test_first_domain_is_not_external(self, db_session, sample_event):
        """First domain for an org should not be flagged as external."""
        result = DiscoveryService.record_discovery(db_session, sample_event)
        assert result.is_external_domain == 0

    def test_same_domain_is_not_external(self, db_session, sample_event):
        """Repeated discoveries on the owned domain should not be external."""
        DiscoveryService.record_discovery(db_session, sample_event)
        result = DiscoveryService.record_discovery(db_session, sample_event)
        assert result.is_external_domain == 0

    def test_different_domain_is_external(self, db_session, sample_event):
        """Content found on a different domain should be flagged as external."""
        DiscoveryService.record_discovery(db_session, sample_event)

        external_event = DiscoveryEvent(
            timestamp=datetime.now(timezone.utc),
            pageUrl="https://other-site.org/repost",
            pageDomain="other-site.org",
            signerId="signer_123",
            organizationId="org_456",
            verified=True,
        )
        result = DiscoveryService.record_discovery(db_session, external_event)
        assert result.is_external_domain == 1

    def test_multiple_external_domains(self, db_session, sample_event):
        """Multiple different external domains should all be flagged."""
        DiscoveryService.record_discovery(db_session, sample_event)

        for domain in ["site-a.com", "site-b.com", "site-c.com"]:
            event = DiscoveryEvent(
                timestamp=datetime.now(timezone.utc),
                pageUrl=f"https://{domain}/article",
                pageDomain=domain,
                signerId="signer_123",
                organizationId="org_456",
                verified=True,
            )
            result = DiscoveryService.record_discovery(db_session, event)
            assert result.is_external_domain == 1

        summaries = db_session.query(DiscoveryDomainSummary).all()
        assert len(summaries) == 4  # 1 owned + 3 external

    def test_no_signer_id_skips_mismatch_check(self, db_session):
        """Events without a signer_id should skip domain-mismatch detection."""
        event = DiscoveryEvent(
            timestamp=datetime.now(timezone.utc),
            pageUrl="https://example.com/page",
            pageDomain="example.com",
            organizationId="org_456",
            verified=True,
        )
        result = DiscoveryService.record_discovery(db_session, event)
        assert result.is_external_domain == 0

    def test_original_domain_stored(self, db_session):
        """original_domain should be stored when provided."""
        event = DiscoveryEvent(
            timestamp=datetime.now(timezone.utc),
            pageUrl="https://copier.com/stolen",
            pageDomain="copier.com",
            signerId="signer_123",
            organizationId="org_456",
            originalDomain="publisher.com",
            verified=True,
        )
        result = DiscoveryService.record_discovery(db_session, event)
        assert result.original_domain == "publisher.com"

    def test_original_domain_direct_mismatch(self, db_session):
        """When originalDomain is provided, use direct comparison instead of heuristic."""
        event = DiscoveryEvent(
            timestamp=datetime.now(timezone.utc),
            pageUrl="https://copier.com/stolen",
            pageDomain="copier.com",
            signerId="signer_123",
            organizationId="org_456",
            originalDomain="publisher.com",
            verified=True,
        )
        result = DiscoveryService.record_discovery(db_session, event)
        assert result.is_external_domain == 1

    def test_original_domain_same_not_external(self, db_session):
        """When originalDomain matches pageDomain, should NOT be external."""
        event = DiscoveryEvent(
            timestamp=datetime.now(timezone.utc),
            pageUrl="https://publisher.com/article",
            pageDomain="publisher.com",
            signerId="signer_123",
            organizationId="org_456",
            originalDomain="publisher.com",
            verified=True,
        )
        result = DiscoveryService.record_discovery(db_session, event)
        assert result.is_external_domain == 0

    def test_original_domain_bypasses_heuristic(self, db_session):
        """With originalDomain, detection should work even without prior discoveries."""
        # No prior discoveries for this org — heuristic would say "not external"
        # But originalDomain says it IS external
        event = DiscoveryEvent(
            timestamp=datetime.now(timezone.utc),
            pageUrl="https://copier.com/stolen",
            pageDomain="copier.com",
            signerId="signer_123",
            organizationId="org_new",
            originalDomain="real-publisher.com",
            verified=True,
        )
        result = DiscoveryService.record_discovery(db_session, event)
        assert result.is_external_domain == 1


class TestDomainAlerts:
    """Tests for domain alert functionality."""

    def test_new_external_domain_creates_alert(self, db_session, sample_event):
        """External domains should be available as alerts."""
        DiscoveryService.record_discovery(db_session, sample_event)

        external_event = DiscoveryEvent(
            timestamp=datetime.now(timezone.utc),
            pageUrl="https://copier.com/stolen",
            pageDomain="copier.com",
            signerId="signer_123",
            organizationId="org_456",
            verified=True,
        )
        DiscoveryService.record_discovery(db_session, external_event)

        alerts = DiscoveryService.get_new_domain_alerts(db_session, "org_456")
        assert len(alerts) == 1
        assert alerts[0].page_domain == "copier.com"

    def test_mark_alert_sent(self, db_session, sample_event):
        """Marking an alert as sent should remove it from the alerts list."""
        DiscoveryService.record_discovery(db_session, sample_event)

        external_event = DiscoveryEvent(
            timestamp=datetime.now(timezone.utc),
            pageUrl="https://copier.com/stolen",
            pageDomain="copier.com",
            signerId="signer_123",
            organizationId="org_456",
            verified=True,
        )
        DiscoveryService.record_discovery(db_session, external_event)

        alerts = DiscoveryService.get_new_domain_alerts(db_session, "org_456")
        assert len(alerts) == 1

        DiscoveryService.mark_alert_sent(db_session, alerts[0].id)

        alerts_after = DiscoveryService.get_new_domain_alerts(db_session, "org_456")
        assert len(alerts_after) == 0

    def test_owned_domain_no_alert(self, db_session, sample_event):
        """Owned domains should not generate alerts."""
        DiscoveryService.record_discovery(db_session, sample_event)

        alerts = DiscoveryService.get_new_domain_alerts(db_session, "org_456")
        assert len(alerts) == 0


class TestQueryMethods:
    """Tests for query methods."""

    def test_get_discoveries_for_org(self, db_session, sample_event):
        """Test getting discoveries for an org."""
        DiscoveryService.record_discovery(db_session, sample_event)
        DiscoveryService.record_discovery(db_session, sample_event)

        results = DiscoveryService.get_discoveries_for_org(db_session, "org_456")
        assert len(results) == 2

    def test_get_discoveries_external_only(self, db_session, sample_event):
        """Test filtering for external-only discoveries."""
        DiscoveryService.record_discovery(db_session, sample_event)

        external_event = DiscoveryEvent(
            timestamp=datetime.now(timezone.utc),
            pageUrl="https://copier.com/stolen",
            pageDomain="copier.com",
            signerId="signer_123",
            organizationId="org_456",
            verified=True,
        )
        DiscoveryService.record_discovery(db_session, external_event)

        all_results = DiscoveryService.get_discoveries_for_org(db_session, "org_456")
        assert len(all_results) == 2

        external_results = DiscoveryService.get_discoveries_for_org(
            db_session, "org_456", external_only=True
        )
        assert len(external_results) == 1
        assert external_results[0].page_domain == "copier.com"

    def test_get_domain_summaries(self, db_session, sample_event):
        """Test getting domain summaries."""
        DiscoveryService.record_discovery(db_session, sample_event)

        summaries = DiscoveryService.get_domain_summaries(db_session, "org_456")
        assert len(summaries) == 1
        assert summaries[0].page_domain == "example.com"

    def test_get_domain_summaries_external_only(self, db_session, sample_event):
        """Test filtering domain summaries for external only."""
        DiscoveryService.record_discovery(db_session, sample_event)

        external_event = DiscoveryEvent(
            timestamp=datetime.now(timezone.utc),
            pageUrl="https://copier.com/stolen",
            pageDomain="copier.com",
            signerId="signer_123",
            organizationId="org_456",
            verified=True,
        )
        DiscoveryService.record_discovery(db_session, external_event)

        all_summaries = DiscoveryService.get_domain_summaries(db_session, "org_456")
        assert len(all_summaries) == 2

        external_summaries = DiscoveryService.get_domain_summaries(
            db_session, "org_456", external_only=True
        )
        assert len(external_summaries) == 1
        assert external_summaries[0].page_domain == "copier.com"

    def test_get_stats_for_org(self, db_session, sample_event):
        """Test getting stats for an org."""
        DiscoveryService.record_discovery(db_session, sample_event)

        external_event = DiscoveryEvent(
            timestamp=datetime.now(timezone.utc),
            pageUrl="https://copier.com/stolen",
            pageDomain="copier.com",
            signerId="signer_123",
            organizationId="org_456",
            verified=True,
        )
        DiscoveryService.record_discovery(db_session, external_event)

        stats = DiscoveryService.get_stats_for_org(db_session, "org_456")
        assert stats["total_discoveries"] == 2
        assert stats["verified_count"] == 2
        assert stats["invalid_count"] == 0
        assert stats["external_domain_count"] == 1
        assert stats["unique_domains"] == 2
        assert len(stats["top_domains"]) == 2

    def test_get_discoveries_pagination(self, db_session, sample_event):
        """Test pagination of discovery results."""
        for _ in range(5):
            DiscoveryService.record_discovery(db_session, sample_event)

        page1 = DiscoveryService.get_discoveries_for_org(
            db_session, "org_456", limit=2, offset=0
        )
        assert len(page1) == 2

        page2 = DiscoveryService.get_discoveries_for_org(
            db_session, "org_456", limit=2, offset=2
        )
        assert len(page2) == 2

        page3 = DiscoveryService.get_discoveries_for_org(
            db_session, "org_456", limit=2, offset=4
        )
        assert len(page3) == 1


class TestDomainMatchesPattern:
    """Tests for the domain_matches_pattern utility function."""

    def test_exact_match(self):
        assert domain_matches_pattern("example.com", "example.com") is True

    def test_exact_match_case_insensitive(self):
        assert domain_matches_pattern("Example.COM", "example.com") is True

    def test_exact_no_match(self):
        assert domain_matches_pattern("other.com", "example.com") is False

    def test_wildcard_subdomain(self):
        assert domain_matches_pattern("blog.example.com", "*.example.com") is True

    def test_wildcard_deep_subdomain(self):
        """fnmatch * matches any chars including dots — multi-level subdomains match."""
        assert domain_matches_pattern("a.b.example.com", "*.example.com") is True

    def test_wildcard_root_no_match(self):
        """*.example.com should NOT match example.com itself."""
        assert domain_matches_pattern("example.com", "*.example.com") is False

    def test_wildcard_different_domain(self):
        assert domain_matches_pattern("blog.other.com", "*.example.com") is False

    def test_wildcard_case_insensitive(self):
        assert domain_matches_pattern("Blog.Example.COM", "*.example.com") is True

    def test_empty_domain(self):
        assert domain_matches_pattern("", "example.com") is False

    def test_empty_pattern(self):
        assert domain_matches_pattern("example.com", "") is False

    def test_both_empty(self):
        assert domain_matches_pattern("", "") is False

    def test_whitespace_handling(self):
        assert domain_matches_pattern("  example.com  ", "example.com") is True

    def test_double_star_wildcard(self):
        """**.example.com should work like *.example.com for single level."""
        assert domain_matches_pattern("blog.example.com", "**.example.com") is True


class TestOwnedDomainCRUD:
    """Tests for owned domain CRUD operations."""

    def test_add_owned_domain(self, db_session):
        owned = DiscoveryService.add_owned_domain(
            db_session, organization_id="org_1", domain_pattern="example.com", label="Main site"
        )
        assert owned.organization_id == "org_1"
        assert owned.domain_pattern == "example.com"
        assert owned.label == "Main site"
        assert owned.is_active == 1

    def test_add_wildcard_domain(self, db_session):
        owned = DiscoveryService.add_owned_domain(
            db_session, organization_id="org_1", domain_pattern="*.example.com", label="Subdomains"
        )
        assert owned.domain_pattern == "*.example.com"

    def test_add_duplicate_raises(self, db_session):
        DiscoveryService.add_owned_domain(db_session, "org_1", "example.com")
        with pytest.raises(ValueError, match="already exists"):
            DiscoveryService.add_owned_domain(db_session, "org_1", "example.com")

    def test_add_normalizes_case(self, db_session):
        owned = DiscoveryService.add_owned_domain(db_session, "org_1", "Example.COM")
        assert owned.domain_pattern == "example.com"

    def test_get_owned_domains(self, db_session):
        DiscoveryService.add_owned_domain(db_session, "org_1", "a.com")
        DiscoveryService.add_owned_domain(db_session, "org_1", "b.com")
        DiscoveryService.add_owned_domain(db_session, "org_2", "c.com")

        result = DiscoveryService.get_owned_domains(db_session, "org_1")
        assert len(result) == 2
        patterns = [d.domain_pattern for d in result]
        assert "a.com" in patterns
        assert "b.com" in patterns

    def test_get_owned_domains_active_only(self, db_session):
        d1 = DiscoveryService.add_owned_domain(db_session, "org_1", "active.com")
        d2 = DiscoveryService.add_owned_domain(db_session, "org_1", "inactive.com")
        DiscoveryService.update_owned_domain(db_session, d2.id, "org_1", is_active=False)

        active = DiscoveryService.get_owned_domains(db_session, "org_1", active_only=True)
        assert len(active) == 1
        assert active[0].domain_pattern == "active.com"

        all_domains = DiscoveryService.get_owned_domains(db_session, "org_1", active_only=False)
        assert len(all_domains) == 2

    def test_update_owned_domain(self, db_session):
        owned = DiscoveryService.add_owned_domain(db_session, "org_1", "old.com")
        updated = DiscoveryService.update_owned_domain(
            db_session, owned.id, "org_1", domain_pattern="new.com", label="Updated"
        )
        assert updated.domain_pattern == "new.com"
        assert updated.label == "Updated"

    def test_update_nonexistent_returns_none(self, db_session):
        result = DiscoveryService.update_owned_domain(db_session, "fake_id", "org_1", label="x")
        assert result is None

    def test_update_wrong_org_returns_none(self, db_session):
        owned = DiscoveryService.add_owned_domain(db_session, "org_1", "example.com")
        result = DiscoveryService.update_owned_domain(db_session, owned.id, "org_2", label="x")
        assert result is None

    def test_deactivate_owned_domain(self, db_session):
        owned = DiscoveryService.add_owned_domain(db_session, "org_1", "example.com")
        updated = DiscoveryService.update_owned_domain(db_session, owned.id, "org_1", is_active=False)
        assert updated.is_active == 0

    def test_delete_owned_domain(self, db_session):
        owned = DiscoveryService.add_owned_domain(db_session, "org_1", "example.com")
        assert DiscoveryService.delete_owned_domain(db_session, owned.id, "org_1") is True
        assert DiscoveryService.get_owned_domains(db_session, "org_1") == []

    def test_delete_nonexistent_returns_false(self, db_session):
        assert DiscoveryService.delete_owned_domain(db_session, "fake_id", "org_1") is False

    def test_delete_wrong_org_returns_false(self, db_session):
        owned = DiscoveryService.add_owned_domain(db_session, "org_1", "example.com")
        assert DiscoveryService.delete_owned_domain(db_session, owned.id, "org_2") is False


class TestOwnedDomainMismatchDetection:
    """Tests for domain-mismatch detection using the owned_domains allowlist."""

    def test_allowlist_exact_match_not_external(self, db_session):
        """Page domain matching an owned domain should NOT be external."""
        DiscoveryService.add_owned_domain(db_session, "org_1", "publisher.com")

        event = DiscoveryEvent(
            timestamp=datetime.now(timezone.utc),
            pageUrl="https://publisher.com/article",
            pageDomain="publisher.com",
            signerId="signer_1",
            organizationId="org_1",
            verified=True,
        )
        result = DiscoveryService.record_discovery(db_session, event)
        assert result.is_external_domain == 0

    def test_allowlist_wildcard_match_not_external(self, db_session):
        """Subdomain matching a wildcard pattern should NOT be external."""
        DiscoveryService.add_owned_domain(db_session, "org_1", "publisher.com")
        DiscoveryService.add_owned_domain(db_session, "org_1", "*.publisher.com")

        event = DiscoveryEvent(
            timestamp=datetime.now(timezone.utc),
            pageUrl="https://blog.publisher.com/post",
            pageDomain="blog.publisher.com",
            signerId="signer_1",
            organizationId="org_1",
            verified=True,
        )
        result = DiscoveryService.record_discovery(db_session, event)
        assert result.is_external_domain == 0

    def test_allowlist_no_match_is_external(self, db_session):
        """Page domain NOT in allowlist should be external."""
        DiscoveryService.add_owned_domain(db_session, "org_1", "publisher.com")
        DiscoveryService.add_owned_domain(db_session, "org_1", "*.publisher.com")

        event = DiscoveryEvent(
            timestamp=datetime.now(timezone.utc),
            pageUrl="https://copier.com/stolen",
            pageDomain="copier.com",
            signerId="signer_1",
            organizationId="org_1",
            verified=True,
        )
        result = DiscoveryService.record_discovery(db_session, event)
        assert result.is_external_domain == 1

    def test_allowlist_takes_priority_over_original_domain(self, db_session):
        """Allowlist should override originalDomain when configured."""
        DiscoveryService.add_owned_domain(db_session, "org_1", "publisher.com")
        DiscoveryService.add_owned_domain(db_session, "org_1", "cdn.publisher.com")

        # originalDomain says "publisher.com" but page is on cdn.publisher.com
        # Without allowlist this would be external; with allowlist it's owned
        event = DiscoveryEvent(
            timestamp=datetime.now(timezone.utc),
            pageUrl="https://cdn.publisher.com/article",
            pageDomain="cdn.publisher.com",
            signerId="signer_1",
            organizationId="org_1",
            originalDomain="publisher.com",
            verified=True,
        )
        result = DiscoveryService.record_discovery(db_session, event)
        assert result.is_external_domain == 0

    def test_allowlist_takes_priority_over_heuristic(self, db_session):
        """Allowlist should override the first-domain-seen heuristic."""
        DiscoveryService.add_owned_domain(db_session, "org_1", "publisher.com")

        # First discovery on a different domain — heuristic would say "not external"
        # but allowlist says it IS external
        event = DiscoveryEvent(
            timestamp=datetime.now(timezone.utc),
            pageUrl="https://copier.com/stolen",
            pageDomain="copier.com",
            signerId="signer_1",
            organizationId="org_1",
            verified=True,
        )
        result = DiscoveryService.record_discovery(db_session, event)
        assert result.is_external_domain == 1

    def test_inactive_domain_not_checked(self, db_session):
        """Deactivated owned domains should not be used for matching."""
        owned = DiscoveryService.add_owned_domain(db_session, "org_1", "publisher.com")
        DiscoveryService.update_owned_domain(db_session, owned.id, "org_1", is_active=False)

        # With no active owned domains, falls back to heuristic (first = owned)
        event = DiscoveryEvent(
            timestamp=datetime.now(timezone.utc),
            pageUrl="https://publisher.com/article",
            pageDomain="publisher.com",
            signerId="signer_1",
            organizationId="org_1",
            verified=True,
        )
        result = DiscoveryService.record_discovery(db_session, event)
        # First domain via heuristic → not external
        assert result.is_external_domain == 0

    def test_multiple_owned_domains(self, db_session):
        """Org with multiple owned domains — all should be recognized."""
        DiscoveryService.add_owned_domain(db_session, "org_1", "publisher.com")
        DiscoveryService.add_owned_domain(db_session, "org_1", "publisher-cdn.net")
        DiscoveryService.add_owned_domain(db_session, "org_1", "*.publisher.com")

        for domain, expected_external in [
            ("publisher.com", 0),
            ("publisher-cdn.net", 0),
            ("blog.publisher.com", 0),
            ("evil-copier.com", 1),
        ]:
            event = DiscoveryEvent(
                timestamp=datetime.now(timezone.utc),
                pageUrl=f"https://{domain}/page",
                pageDomain=domain,
                signerId="signer_1",
                organizationId="org_1",
                verified=True,
            )
            result = DiscoveryService.record_discovery(db_session, event)
            assert result.is_external_domain == expected_external, f"Failed for {domain}"

    def test_no_allowlist_falls_back_to_original_domain(self, db_session):
        """Without owned domains configured, should use originalDomain."""
        event = DiscoveryEvent(
            timestamp=datetime.now(timezone.utc),
            pageUrl="https://copier.com/stolen",
            pageDomain="copier.com",
            signerId="signer_1",
            organizationId="org_no_allowlist",
            originalDomain="publisher.com",
            verified=True,
        )
        result = DiscoveryService.record_discovery(db_session, event)
        assert result.is_external_domain == 1

    def test_no_allowlist_no_original_falls_back_to_heuristic(self, db_session):
        """Without owned domains or originalDomain, should use heuristic."""
        # First discovery → heuristic says "owned"
        event1 = DiscoveryEvent(
            timestamp=datetime.now(timezone.utc),
            pageUrl="https://first-domain.com/page",
            pageDomain="first-domain.com",
            signerId="signer_1",
            organizationId="org_heuristic",
            verified=True,
        )
        result1 = DiscoveryService.record_discovery(db_session, event1)
        assert result1.is_external_domain == 0

        # Second domain → heuristic says "external"
        event2 = DiscoveryEvent(
            timestamp=datetime.now(timezone.utc),
            pageUrl="https://second-domain.com/page",
            pageDomain="second-domain.com",
            signerId="signer_1",
            organizationId="org_heuristic",
            verified=True,
        )
        result2 = DiscoveryService.record_discovery(db_session, event2)
        assert result2.is_external_domain == 1
