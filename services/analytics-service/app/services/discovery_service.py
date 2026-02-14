"""Discovery service for tracking where signed content appears across the web.

Records discovery events in a dedicated table and maintains per-org domain
summaries.  Detects domain mismatches (content found outside the signer's
known domain) and flags them for alerting.
"""

import fnmatch
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, distinct, func
from sqlalchemy.orm import Session

from ..db.models import ContentDiscovery, DiscoveryDomainSummary, OwnedDomain
from ..models.schemas import DiscoveryEvent

logger = logging.getLogger(__name__)


def domain_matches_pattern(domain: str, pattern: str) -> bool:
    """Check if a domain matches a pattern (exact or wildcard).

    Supported patterns:
        - ``example.com``        — exact match
        - ``*.example.com``      — matches any subdomain (blog.example.com)
        - ``**.example.com``     — same as ``*.example.com``

    Matching is case-insensitive.
    """
    domain = domain.lower().strip()
    pattern = pattern.lower().strip()

    if not pattern or not domain:
        return False

    # Exact match
    if domain == pattern:
        return True

    # Wildcard match using fnmatch
    if "*" in pattern:
        return fnmatch.fnmatch(domain, pattern)

    return False


class DiscoveryService:
    """Handles content discovery event recording and querying."""

    @staticmethod
    def record_discovery(
        db: Session,
        event: DiscoveryEvent,
        source: str = "chrome_extension",
        extension_version: Optional[str] = None,
    ) -> ContentDiscovery:
        """Record a single content discovery event.

        Creates a ContentDiscovery row and upserts the corresponding
        DiscoveryDomainSummary for the org+domain pair.
        """
        now = datetime.now(timezone.utc)

        discovery = ContentDiscovery(
            page_url=event.pageUrl,
            page_domain=event.pageDomain,
            page_title=event.pageTitle,
            signer_id=event.signerId,
            signer_name=event.signerName,
            organization_id=event.organizationId,
            document_id=event.documentId,
            original_domain=event.originalDomain,
            verified=1 if event.verified else 0,
            verification_status=event.verificationStatus,
            marker_type=event.markerType,
            is_external_domain=0,  # Updated below if applicable
            session_id=event.sessionId,
            extension_version=extension_version or event.extensionVersion,
            source=source,
            date=now.strftime("%Y-%m-%d"),
        )

        # Domain-mismatch detection.  Priority order:
        # 1. Org's configured owned_domains allowlist (deterministic)
        # 2. originalDomain from the event (direct comparison)
        # 3. Domain-summary heuristic (first domain seen = owned)
        if event.organizationId and event.signerId:
            is_external = DiscoveryService._is_external_domain(
                db,
                organization_id=event.organizationId,
                page_domain=event.pageDomain,
                original_domain=event.originalDomain,
            )
            discovery.is_external_domain = 1 if is_external else 0

        db.add(discovery)

        # Upsert domain summary
        if event.organizationId:
            DiscoveryService._upsert_domain_summary(
                db,
                organization_id=event.organizationId,
                page_domain=event.pageDomain,
                verified=event.verified,
                is_external=bool(discovery.is_external_domain),
                now=now,
            )

        db.commit()
        db.refresh(discovery)
        return discovery

    @staticmethod
    def record_batch(
        db: Session,
        events: List[DiscoveryEvent],
        source: str = "chrome_extension",
        extension_version: Optional[str] = None,
    ) -> int:
        """Record a batch of discovery events. Returns count recorded."""
        count = 0
        for event in events:
            try:
                DiscoveryService.record_discovery(
                    db, event, source=source, extension_version=extension_version
                )
                count += 1
            except Exception as exc:
                logger.warning("Failed to record discovery event: %s", exc)
                db.rollback()
        return count

    @staticmethod
    def _is_external_domain(
        db: Session,
        organization_id: str,
        page_domain: str,
        original_domain: Optional[str] = None,
    ) -> bool:
        """Determine if page_domain is external to the org.

        Priority:
        1. Org's configured owned_domains allowlist (deterministic, with wildcards)
        2. originalDomain from the discovery event (direct comparison)
        3. Domain-summary heuristic (first domain seen = owned)
        """
        # 1. Check configured owned domains allowlist
        owned_domains = DiscoveryService.get_owned_domains(db, organization_id)
        if owned_domains:
            for od in owned_domains:
                if domain_matches_pattern(page_domain, od.domain_pattern):
                    return False
            return True  # No pattern matched → external

        # 2. Check originalDomain from the event
        if original_domain:
            return page_domain != original_domain

        # 3. Fall back to domain-summary heuristic
        return DiscoveryService._check_domain_mismatch_heuristic(
            db, organization_id, page_domain
        )

    @staticmethod
    def _check_domain_mismatch_heuristic(
        db: Session,
        organization_id: str,
        page_domain: str,
    ) -> bool:
        """Heuristic fallback: first domain seen for an org is assumed owned."""
        owned = (
            db.query(DiscoveryDomainSummary)
            .filter(
                DiscoveryDomainSummary.organization_id == organization_id,
                DiscoveryDomainSummary.is_owned_domain == 1,
            )
            .first()
        )

        if owned is None:
            return False

        this_domain = (
            db.query(DiscoveryDomainSummary)
            .filter(
                DiscoveryDomainSummary.organization_id == organization_id,
                DiscoveryDomainSummary.page_domain == page_domain,
                DiscoveryDomainSummary.is_owned_domain == 1,
            )
            .first()
        )

        return this_domain is None

    # ── Owned Domain CRUD ──

    @staticmethod
    def get_owned_domains(
        db: Session,
        organization_id: str,
        active_only: bool = True,
    ) -> List[OwnedDomain]:
        """Get all owned domain patterns for an organization."""
        query = db.query(OwnedDomain).filter(
            OwnedDomain.organization_id == organization_id,
        )
        if active_only:
            query = query.filter(OwnedDomain.is_active == 1)
        return query.order_by(OwnedDomain.created_at.asc()).all()

    @staticmethod
    def add_owned_domain(
        db: Session,
        organization_id: str,
        domain_pattern: str,
        label: Optional[str] = None,
    ) -> OwnedDomain:
        """Add a domain pattern to an org's allowlist.

        Raises ValueError if the pattern already exists for this org.
        """
        existing = (
            db.query(OwnedDomain)
            .filter(
                OwnedDomain.organization_id == organization_id,
                OwnedDomain.domain_pattern == domain_pattern.lower().strip(),
            )
            .first()
        )
        if existing:
            raise ValueError(f"Domain pattern '{domain_pattern}' already exists for this organization")

        owned = OwnedDomain(
            organization_id=organization_id,
            domain_pattern=domain_pattern.lower().strip(),
            label=label,
        )
        db.add(owned)
        db.commit()
        db.refresh(owned)
        return owned

    @staticmethod
    def update_owned_domain(
        db: Session,
        domain_id: str,
        organization_id: str,
        domain_pattern: Optional[str] = None,
        label: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[OwnedDomain]:
        """Update an owned domain entry. Returns None if not found."""
        owned = (
            db.query(OwnedDomain)
            .filter(
                OwnedDomain.id == domain_id,
                OwnedDomain.organization_id == organization_id,
            )
            .first()
        )
        if not owned:
            return None

        if domain_pattern is not None:
            owned.domain_pattern = domain_pattern.lower().strip()
        if label is not None:
            owned.label = label
        if is_active is not None:
            owned.is_active = 1 if is_active else 0
        owned.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(owned)
        return owned

    @staticmethod
    def delete_owned_domain(
        db: Session,
        domain_id: str,
        organization_id: str,
    ) -> bool:
        """Delete an owned domain entry. Returns True if deleted."""
        owned = (
            db.query(OwnedDomain)
            .filter(
                OwnedDomain.id == domain_id,
                OwnedDomain.organization_id == organization_id,
            )
            .first()
        )
        if not owned:
            return False
        db.delete(owned)
        db.commit()
        return True

    @staticmethod
    def _upsert_domain_summary(
        db: Session,
        organization_id: str,
        page_domain: str,
        verified: bool,
        is_external: bool,
        now: datetime,
    ) -> DiscoveryDomainSummary:
        """Create or update the domain summary for an org+domain pair."""
        summary = (
            db.query(DiscoveryDomainSummary)
            .filter(
                DiscoveryDomainSummary.organization_id == organization_id,
                DiscoveryDomainSummary.page_domain == page_domain,
            )
            .first()
        )

        if summary is None:
            # First discovery on this domain for this org
            # If no owned domains exist yet, mark this as owned
            has_owned = (
                db.query(DiscoveryDomainSummary)
                .filter(
                    DiscoveryDomainSummary.organization_id == organization_id,
                    DiscoveryDomainSummary.is_owned_domain == 1,
                )
                .first()
            )

            summary = DiscoveryDomainSummary(
                organization_id=organization_id,
                page_domain=page_domain,
                discovery_count=1,
                verified_count=1 if verified else 0,
                invalid_count=0 if verified else 1,
                is_owned_domain=0 if has_owned else 1,  # First domain = owned
                first_seen_at=now,
                last_seen_at=now,
            )
            db.add(summary)
        else:
            summary.discovery_count += 1
            if verified:
                summary.verified_count += 1
            else:
                summary.invalid_count += 1
            summary.last_seen_at = now

        return summary

    # ── Query Methods ──

    @staticmethod
    def get_discoveries_for_org(
        db: Session,
        organization_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        external_only: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> List[ContentDiscovery]:
        """Get discovery events for an organization."""
        query = db.query(ContentDiscovery).filter(
            ContentDiscovery.organization_id == organization_id,
        )
        if start_date:
            query = query.filter(ContentDiscovery.discovered_at >= start_date)
        if end_date:
            query = query.filter(ContentDiscovery.discovered_at <= end_date)
        if external_only:
            query = query.filter(ContentDiscovery.is_external_domain == 1)

        return (
            query.order_by(ContentDiscovery.discovered_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_domain_summaries(
        db: Session,
        organization_id: str,
        external_only: bool = False,
    ) -> List[DiscoveryDomainSummary]:
        """Get domain summaries for an organization."""
        query = db.query(DiscoveryDomainSummary).filter(
            DiscoveryDomainSummary.organization_id == organization_id,
        )
        if external_only:
            query = query.filter(DiscoveryDomainSummary.is_owned_domain == 0)

        return query.order_by(DiscoveryDomainSummary.last_seen_at.desc()).all()

    @staticmethod
    def get_new_domain_alerts(
        db: Session,
        organization_id: str,
    ) -> List[DiscoveryDomainSummary]:
        """Get external domains that haven't been alerted yet."""
        return (
            db.query(DiscoveryDomainSummary)
            .filter(
                DiscoveryDomainSummary.organization_id == organization_id,
                DiscoveryDomainSummary.is_owned_domain == 0,
                DiscoveryDomainSummary.alert_sent == 0,
            )
            .order_by(DiscoveryDomainSummary.first_seen_at.desc())
            .all()
        )

    @staticmethod
    def mark_alert_sent(
        db: Session,
        summary_id: str,
    ) -> None:
        """Mark a domain summary alert as sent."""
        now = datetime.now(timezone.utc)
        summary = db.query(DiscoveryDomainSummary).get(summary_id)
        if summary:
            summary.alert_sent = 1
            summary.alert_sent_at = now
            db.commit()

    @staticmethod
    def get_stats_for_org(
        db: Session,
        organization_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get discovery statistics for an organization."""
        now = datetime.now(timezone.utc)
        if not end_date:
            end_date = now
        if not start_date:
            from datetime import timedelta
            start_date = end_date - timedelta(days=30)

        base = db.query(ContentDiscovery).filter(
            ContentDiscovery.organization_id == organization_id,
            ContentDiscovery.discovered_at >= start_date,
            ContentDiscovery.discovered_at <= end_date,
        )

        total = base.count()
        verified = base.filter(ContentDiscovery.verified == 1).count()
        external = base.filter(ContentDiscovery.is_external_domain == 1).count()

        unique_domains = (
            db.query(func.count(distinct(ContentDiscovery.page_domain)))
            .filter(
                ContentDiscovery.organization_id == organization_id,
                ContentDiscovery.discovered_at >= start_date,
                ContentDiscovery.discovered_at <= end_date,
            )
            .scalar()
            or 0
        )

        # Top domains
        top_domains_q = (
            db.query(
                ContentDiscovery.page_domain,
                func.count(ContentDiscovery.id).label("count"),
            )
            .filter(
                ContentDiscovery.organization_id == organization_id,
                ContentDiscovery.discovered_at >= start_date,
                ContentDiscovery.discovered_at <= end_date,
            )
            .group_by(ContentDiscovery.page_domain)
            .order_by(func.count(ContentDiscovery.id).desc())
            .limit(10)
            .all()
        )

        return {
            "total_discoveries": total,
            "verified_count": verified,
            "invalid_count": total - verified,
            "external_domain_count": external,
            "unique_domains": unique_domains,
            "top_domains": [
                {"domain": d, "count": c} for d, c in top_domains_q if d
            ],
            "period_start": start_date,
            "period_end": end_date,
        }
