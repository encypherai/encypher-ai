"""SQLAlchemy database models for Analytics Service"""

from sqlalchemy import Column, String, Integer, DateTime, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


def generate_uuid():
    return str(uuid.uuid4())


class UsageMetric(Base):
    """Usage metrics model"""

    __tablename__ = "usage_metrics"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False, index=True)
    organization_id = Column(String, nullable=True, index=True)

    # Metric details
    metric_type = Column(String, nullable=False, index=True)  # api_call, document_signed, verification, etc.
    service_name = Column(String, nullable=False, index=True)
    endpoint = Column(String, nullable=True)

    # Counts and values
    count = Column(Integer, nullable=False, default=1)
    value = Column(Float, nullable=True)

    # Performance
    response_time_ms = Column(Integer, nullable=True)
    status_code = Column(Integer, nullable=True)

    # Metadata (renamed to avoid SQLAlchemy reserved attribute name)
    meta = Column(JSON, nullable=True)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    date = Column(String, nullable=False, index=True)  # YYYY-MM-DD for aggregation
    hour = Column(Integer, nullable=False, index=True)  # 0-23 for hourly aggregation

    def __repr__(self):
        return f"<UsageMetric(id={self.id}, metric_type={self.metric_type}, user_id={self.user_id})>"


class AggregatedMetric(Base):
    """Pre-aggregated metrics for performance"""

    __tablename__ = "aggregated_metrics"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=True, index=True)
    organization_id = Column(String, nullable=True, index=True)

    # Aggregation details
    metric_type = Column(String, nullable=False, index=True)
    service_name = Column(String, nullable=False, index=True)
    aggregation_period = Column(String, nullable=False, index=True)  # hourly, daily, weekly, monthly
    period_start = Column(DateTime(timezone=True), nullable=False, index=True)
    period_end = Column(DateTime(timezone=True), nullable=False)

    # Aggregated values
    total_count = Column(Integer, nullable=False, default=0)
    total_value = Column(Float, nullable=True)
    avg_response_time_ms = Column(Float, nullable=True)
    min_response_time_ms = Column(Integer, nullable=True)
    max_response_time_ms = Column(Integer, nullable=True)
    success_count = Column(Integer, nullable=False, default=0)
    error_count = Column(Integer, nullable=False, default=0)

    # Metadata (renamed to avoid SQLAlchemy reserved attribute name)
    meta = Column(JSON, nullable=True)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<AggregatedMetric(id={self.id}, metric_type={self.metric_type}, period={self.aggregation_period})>"


class ContentDiscovery(Base):
    """Records where signed/embedded content is discovered across the web.

    Each row represents a single verification event reported by a Chrome
    extension user.  The *reporter* is fully anonymized (ephemeral session
    ID only).  The *signer* (organization that signed the content) is
    identified so they can be notified when their content appears on new
    domains.
    """

    __tablename__ = "content_discoveries"

    id = Column(String, primary_key=True, default=generate_uuid)

    # Where the content was found
    page_url = Column(String(2048), nullable=False)
    page_domain = Column(String(255), nullable=False, index=True)
    page_title = Column(String(512), nullable=True)

    # Who signed the content (the content owner)
    signer_id = Column(String(255), nullable=True, index=True)
    signer_name = Column(String(255), nullable=True)
    organization_id = Column(String(255), nullable=True, index=True)
    document_id = Column(String(255), nullable=True, index=True)

    # The domain where the content was originally signed/published
    original_domain = Column(String(255), nullable=True, index=True)

    # Verification outcome
    verified = Column(Integer, nullable=False, default=0)  # 1=verified, 0=invalid
    verification_status = Column(String(50), nullable=True)  # verified, invalid, revoked
    marker_type = Column(String(50), nullable=True)  # c2pa, encypher, micro

    # Domain-mismatch flag: True when page_domain != signer's known domain
    is_external_domain = Column(Integer, nullable=False, default=0)

    # Anonymized reporter context (no PII)
    session_id = Column(String(100), nullable=True)
    extension_version = Column(String(50), nullable=True)
    source = Column(String(50), nullable=False, default="chrome_extension")

    # Timestamps
    discovered_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    date = Column(String, nullable=False, index=True)  # YYYY-MM-DD for aggregation

    def __repr__(self):
        return (
            f"<ContentDiscovery(id={self.id}, domain={self.page_domain}, "
            f"signer={self.signer_id}, external={self.is_external_domain})>"
        )


class DiscoveryDomainSummary(Base):
    """Aggregated view of unique domains where an org's content was found.

    Updated on each new discovery.  Enables fast "where is my content?"
    queries without scanning the full content_discoveries table.
    """

    __tablename__ = "discovery_domain_summaries"

    id = Column(String, primary_key=True, default=generate_uuid)

    # The org whose content was found
    organization_id = Column(String(255), nullable=False, index=True)

    # The domain where content was found
    page_domain = Column(String(255), nullable=False)

    # Counts
    discovery_count = Column(Integer, nullable=False, default=1)
    verified_count = Column(Integer, nullable=False, default=0)
    invalid_count = Column(Integer, nullable=False, default=0)

    # Whether this domain belongs to the org (False = external / copy-paste)
    is_owned_domain = Column(Integer, nullable=False, default=0)

    # Alert tracking
    alert_sent = Column(Integer, nullable=False, default=0)
    alert_sent_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    first_seen_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_seen_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return (
            f"<DiscoveryDomainSummary(org={self.organization_id}, "
            f"domain={self.page_domain}, count={self.discovery_count})>"
        )


class OwnedDomain(Base):
    """Organization-configured domain allowlist for discovery tracking.

    Orgs can register domains they own so that domain-mismatch detection
    is deterministic rather than heuristic-based.  Supports wildcard
    patterns (e.g. ``*.example.com``) to match all subdomains.

    When an org has at least one OwnedDomain row, the mismatch check
    uses this list exclusively.  Otherwise it falls back to the
    originalDomain field or the first-domain-seen heuristic.
    """

    __tablename__ = "owned_domains"

    id = Column(String, primary_key=True, default=generate_uuid)

    organization_id = Column(String(255), nullable=False, index=True)

    # Domain pattern — exact domain or wildcard (e.g. "*.example.com")
    domain_pattern = Column(String(255), nullable=False)

    # Human-readable label (e.g. "Main website", "CDN")
    label = Column(String(255), nullable=True)

    # Whether this entry is currently active
    is_active = Column(Integer, nullable=False, default=1)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return (
            f"<OwnedDomain(org={self.organization_id}, "
            f"pattern={self.domain_pattern})>"
        )
