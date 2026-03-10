"""
Rights Management System Models.

SQLAlchemy ORM models for publisher rights profiles, formal notices,
licensing requests/agreements, audit logs, and content detection analytics.

All tables introduced by migration 20260221_120000_rights_management_system.
"""

import uuid
from datetime import datetime

from sqlalchemy import ARRAY, TIMESTAMP, BigInteger, Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID
from sqlalchemy.orm import relationship

from app.database import Base

# ============================================================================
# Publisher Rights Profiles
# ============================================================================


class PublisherRightsProfile(Base):
    """
    Versioned publisher-level rights profile.

    Each UPDATE to a publisher's rights creates a new row rather than
    overwriting the previous one (append-only versioning). The highest
    profile_version for a given organization_id is the current profile.
    """

    __tablename__ = "publisher_rights_profiles"
    __table_args__ = {"extend_existing": True}

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Ownership
    organization_id = Column(
        String(64),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    profile_version = Column(Integer, nullable=False, default=1)
    effective_date = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)
    updated_by = Column(UUID(as_uuid=True), nullable=True)

    # Publisher identity
    publisher_name = Column(Text, nullable=False)
    publisher_url = Column(Text, nullable=True)
    contact_email = Column(Text, nullable=True)
    contact_url = Column(Text, nullable=True)
    legal_entity = Column(Text, nullable=True)
    jurisdiction = Column(Text, nullable=False, default="US")

    # Default rights policy
    default_license_type = Column(Text, nullable=False, default="all_rights_reserved")

    # Tier-specific licensing terms (JSONB)
    bronze_tier = Column(JSONB, nullable=False, default=dict)
    silver_tier = Column(JSONB, nullable=False, default=dict)
    gold_tier = Column(JSONB, nullable=False, default=dict)

    # Formal notice embedded fields (denormalised for public API performance)
    notice_status = Column(Text, nullable=False, default="draft")
    notice_effective_date = Column(TIMESTAMP(timezone=True), nullable=True)
    notice_text = Column(Text, nullable=True)
    notice_hash = Column(Text, nullable=True)

    # Coalition membership
    coalition_member = Column(Boolean, nullable=False, default=True)
    coalition_joined_at = Column(TIMESTAMP(timezone=True), nullable=True)
    licensing_track = Column(Text, nullable=False, default="both")

    def __repr__(self) -> str:
        return f"<PublisherRightsProfile(id={self.id}, org={self.organization_id}, v{self.profile_version})>"


# ============================================================================
# Document Rights Overrides
# ============================================================================


class DocumentRightsOverride(Base):
    """
    Per-document, per-collection, or per-content-type rights override.

    When document_id is NULL the override applies to an entire collection
    or content type. Versioned append-only like PublisherRightsProfile.
    """

    __tablename__ = "document_rights_overrides"
    __table_args__ = {"extend_existing": True}

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Scope references
    document_id = Column(UUID(as_uuid=True), nullable=True)  # NULL for collection/type overrides
    organization_id = Column(
        String(64),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    override_version = Column(Integer, nullable=False, default=1)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)
    updated_by = Column(UUID(as_uuid=True), nullable=True)

    # Override scope
    override_type = Column(Text, nullable=False, default="document")  # document | collection | content_type
    collection_id = Column(UUID(as_uuid=True), nullable=True)
    content_type_filter = Column(Text, nullable=True)
    date_range_start = Column(TIMESTAMP(timezone=True), nullable=True)
    date_range_end = Column(TIMESTAMP(timezone=True), nullable=True)

    # Tier overrides (NULL means inherit from publisher profile)
    bronze_tier_override = Column(JSONB, nullable=True)
    silver_tier_override = Column(JSONB, nullable=True)
    gold_tier_override = Column(JSONB, nullable=True)

    # Special flags
    do_not_license = Column(Boolean, nullable=False, default=False)
    premium_content = Column(Boolean, nullable=False, default=False)
    embargo_until = Column(TIMESTAMP(timezone=True), nullable=True)
    syndication_rights = Column(JSONB, nullable=True)

    def __repr__(self) -> str:
        return f"<DocumentRightsOverride(id={self.id}, doc={self.document_id}, org={self.organization_id}, v{self.override_version})>"


# ============================================================================
# Formal Notices
# ============================================================================


class FormalNotice(Base):
    """
    Immutable formal notice record.

    Once a notice is delivered its notice_text and notice_hash must not
    change. The evidence chain (NoticeEvidenceChain) tracks all lifecycle
    events for the notice.
    """

    __tablename__ = "formal_notices"
    __table_args__ = {"extend_existing": True}

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Ownership
    organization_id = Column(
        String(64),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)

    # Target entity
    target_entity_name = Column(Text, nullable=False)
    target_entity_domain = Column(Text, nullable=True)
    target_contact_email = Column(Text, nullable=True)
    target_entity_type = Column(Text, nullable=False, default="ai_company")

    # Scope
    scope_type = Column(Text, nullable=False)
    scope_document_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=True)
    scope_date_range_start = Column(TIMESTAMP(timezone=True), nullable=True)
    scope_date_range_end = Column(TIMESTAMP(timezone=True), nullable=True)

    # Notice content (immutable once delivered)
    notice_type = Column(Text, nullable=False)
    notice_text = Column(Text, nullable=False)
    notice_hash = Column(Text, nullable=False)  # SHA-256 of notice_text

    # Demands (structured JSON)
    demands = Column(JSONB, nullable=False, default=dict)

    # Lifecycle state
    status = Column(Text, nullable=False, default="created")
    delivered_at = Column(TIMESTAMP(timezone=True), nullable=True)
    delivery_method = Column(Text, nullable=True)
    delivery_receipt = Column(JSONB, nullable=True)
    delivery_receipt_hash = Column(Text, nullable=True)
    acknowledged_at = Column(TIMESTAMP(timezone=True), nullable=True)
    response = Column(JSONB, nullable=True)

    # Relationships
    evidence_chain = relationship(
        "NoticeEvidenceChain",
        back_populates="notice",
        order_by="NoticeEvidenceChain.created_at",
    )

    def __repr__(self) -> str:
        return f"<FormalNotice(id={self.id}, target={self.target_entity_name}, status={self.status})>"


# ============================================================================
# Notice Evidence Chain
# ============================================================================


class NoticeEvidenceChain(Base):
    """
    Append-only cryptographic evidence chain for a formal notice.

    Each event is linked to the previous via previous_hash, forming a
    tamper-evident linked list of lifecycle events.
    """

    __tablename__ = "notice_evidence_chain"
    __table_args__ = {"extend_existing": True}

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Parent notice
    notice_id = Column(
        UUID(as_uuid=True),
        ForeignKey("formal_notices.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Event payload
    event_type = Column(Text, nullable=False)
    event_data = Column(JSONB, nullable=False, default=dict)
    event_hash = Column(Text, nullable=False)  # SHA-256(event_data + previous_hash)
    previous_hash = Column(Text, nullable=True)  # NULL for first event in chain

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)

    # Relationships
    notice = relationship("FormalNotice", back_populates="evidence_chain")

    def __repr__(self) -> str:
        return f"<NoticeEvidenceChain(id={self.id}, notice={self.notice_id}, event={self.event_type})>"


# ============================================================================
# Rights Licensing Requests
# ============================================================================


class RightsLicensingRequest(Base):
    """
    Inbound licensing request and negotiation record.

    Distinct from the existing LicensingAgreement model which covers
    Encypher-managed AI company agreements. This model covers the
    publisher-initiated or AI-company-initiated rights licensing flow.
    """

    __tablename__ = "rights_licensing_requests"
    __table_args__ = {"extend_existing": True}

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Parties
    publisher_org_id = Column(
        String(64),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
    )
    requester_org_id = Column(
        String(64),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Request details
    tier = Column(Text, nullable=False)  # bronze | silver | gold
    scope = Column(JSONB, nullable=False, default=dict)
    proposed_terms = Column(JSONB, nullable=False, default=dict)
    requester_info = Column(JSONB, nullable=False, default=dict)

    # Status and response
    status = Column(Text, nullable=False, default="pending")
    response = Column(JSONB, nullable=True)
    responded_at = Column(TIMESTAMP(timezone=True), nullable=True)

    # If approved, links to the resulting agreement
    agreement_id = Column(UUID(as_uuid=True), nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<RightsLicensingRequest(id={self.id}, tier={self.tier}, status={self.status})>"


# ============================================================================
# Rights Licensing Agreements
# ============================================================================


class RightsLicensingAgreement(Base):
    """
    Active licensing agreement created after a RightsLicensingRequest is approved.

    Tracks ongoing rights grants with tier, scope, terms, and usage metrics.
    """

    __tablename__ = "rights_licensing_agreements"
    __table_args__ = {"extend_existing": True}

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Back-reference to originating request
    request_id = Column(
        UUID(as_uuid=True),
        ForeignKey("rights_licensing_requests.id"),
        nullable=True,
    )

    # Parties
    publisher_org_id = Column(
        String(64),
        ForeignKey("organizations.id"),
        nullable=False,
    )
    licensee_org_id = Column(
        String(64),
        ForeignKey("organizations.id"),
        nullable=True,
    )
    licensee_name = Column(Text, nullable=True)  # For non-org licensees

    # Agreement terms
    tier = Column(Text, nullable=False)
    scope = Column(JSONB, nullable=False, default=dict)
    terms = Column(JSONB, nullable=False, default=dict)

    # Duration
    effective_date = Column(TIMESTAMP(timezone=True), nullable=False)
    expiry_date = Column(TIMESTAMP(timezone=True), nullable=True)
    auto_renew = Column(Boolean, nullable=False, default=False)

    # Status and usage
    status = Column(Text, nullable=False, default="active")
    usage_metrics = Column(JSONB, nullable=False, default=dict)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<RightsLicensingAgreement(id={self.id}, tier={self.tier}, status={self.status})>"


# ============================================================================
# Rights Audit Log
# ============================================================================


class RightsAuditLog(Base):
    """
    Append-only audit trail for all rights-related changes.

    Uses BigInteger primary key (auto-increment sequence) rather than UUID
    for insert performance on a high-volume log table.
    """

    __tablename__ = "rights_audit_log"
    __table_args__ = {"extend_existing": True}

    # Primary key (sequence, not UUID — migration spec)
    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # Context
    organization_id = Column(String(64), nullable=False)
    action = Column(Text, nullable=False)
    resource_type = Column(Text, nullable=False)
    resource_id = Column(UUID(as_uuid=True), nullable=True)

    # Change values
    old_value = Column(JSONB, nullable=True)
    new_value = Column(JSONB, nullable=True)

    # Actor
    performed_by = Column(UUID(as_uuid=True), nullable=True)
    performed_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)
    ip_address = Column(INET, nullable=True)

    def __repr__(self) -> str:
        return f"<RightsAuditLog(id={self.id}, action={self.action}, resource={self.resource_type}/{self.resource_id})>"


# ============================================================================
# Content Detection Events
# ============================================================================


class ContentDetectionEvent(Base):
    """
    Phone-home analytics event recorded when Encypher-signed content is detected.

    High-volume, append-only table. Uses BigInteger primary key for insert
    throughput. Intended to be partitioned by month in production.
    """

    __tablename__ = "content_detection_events"
    __table_args__ = {"extend_existing": True}

    # Primary key (sequence)
    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # Content reference
    document_id = Column(UUID(as_uuid=True), nullable=True)
    organization_id = Column(String(64), nullable=False)

    # Detection source
    # Possible values: chrome_extension, api_verification, rsl_olp_check,
    # http_header_lookup, rights_api_lookup, crawl_detected
    detection_source = Column(Text, nullable=False)

    # Location where content was detected
    detected_on_url = Column(Text, nullable=True)
    detected_on_domain = Column(Text, nullable=True)

    # Requester metadata
    requester_ip = Column(INET, nullable=True)
    requester_org_id = Column(String(64), nullable=True)
    requester_user_agent = Column(Text, nullable=True)
    # Possible values: human_browser, ai_crawler, search_crawler, aggregator, unknown
    user_agent_category = Column(Text, nullable=True)

    # Content integrity
    segments_found = Column(Integer, nullable=True)
    # Possible values: intact, partial_tampering, significant_tampering, stripped
    integrity_status = Column(Text, nullable=True)

    # Rights signal outcomes
    rights_served = Column(Boolean, nullable=False, default=False)
    rights_acknowledged = Column(Boolean, nullable=False, default=False)

    # Set True when a bot that claims robots.txt/RSL compliance accessed content
    # without a prior RSL OLP token check (detected via CDN log ingestion).
    # NULL = not applicable (event did not come from log ingestion).
    robots_txt_bypassed = Column(Boolean, nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<ContentDetectionEvent(id={self.id}, source={self.detection_source}, domain={self.detected_on_domain})>"


# ============================================================================
# Known Crawlers
# ============================================================================


class KnownCrawler(Base):
    """
    User-agent classification registry for detection analytics.

    Seeded at migration time with major AI and search crawlers.
    """

    __tablename__ = "known_crawlers"
    __table_args__ = {"extend_existing": True}

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Identification
    user_agent_pattern = Column(Text, nullable=False)
    crawler_name = Column(Text, nullable=False)
    operator_org = Column(Text, nullable=False)

    # Classification
    # Possible values: ai_training, ai_search, search_engine, aggregator, monitoring
    crawler_type = Column(Text, nullable=False)

    # Compliance signals
    respects_robots_txt = Column(Boolean, nullable=True)
    respects_rsl = Column(Boolean, nullable=True)  # Respects Robots.txt for LLMs spec

    # Known IP ranges (CIDR blocks)
    known_ip_ranges = Column(ARRAY(INET), nullable=True)

    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<KnownCrawler(id={self.id}, name={self.crawler_name}, type={self.crawler_type})>"
