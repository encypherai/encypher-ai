"""Discovery service for tracking where signed content appears across the web.

Records discovery events in a dedicated table and maintains per-org domain
summaries.  Detects domain mismatches (content found outside the signer's
known domain) and flags them for alerting.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, distinct, func
from sqlalchemy.orm import Session

from ..db.models import ContentDiscovery, DiscoveryDomainSummary
from ..models.schemas import DiscoveryEvent

logger = logging.getLogger(__name__)


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

        # Domain-mismatch detection.
        # If the extension provides the original signing domain, compare
        # directly.  Otherwise fall back to the domain-summary heuristic
        # (first domain seen for an org is assumed to be owned).
        if event.organizationId and event.signerId:
            if event.originalDomain:
                is_external = event.pageDomain != event.originalDomain
            else:
                is_external = DiscoveryService._check_domain_mismatch(
                    db,
                    organization_id=event.organizationId,
                    page_domain=event.pageDomain,
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
    def _check_domain_mismatch(
        db: Session,
        organization_id: str,
        page_domain: str,
    ) -> bool:
        """Return True if page_domain is NOT a known owned domain for the org.

        An owned domain is one that was first seen with is_owned_domain=1
        in the summary table.  If no summary exists yet for this org, the
        first domain seen is assumed to be owned.
        """
        # Check if any owned domains exist for this org
        owned = (
            db.query(DiscoveryDomainSummary)
            .filter(
                DiscoveryDomainSummary.organization_id == organization_id,
                DiscoveryDomainSummary.is_owned_domain == 1,
            )
            .first()
        )

        if owned is None:
            # No owned domains yet — this is the first discovery for this org.
            # Assume the first domain is the org's own domain.
            return False

        # Check if this specific domain is owned
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
