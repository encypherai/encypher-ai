"""Pydantic schemas for Analytics Service"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class MetricCreate(BaseModel):
    """Schema for creating a metric"""

    metric_type: str = Field(..., min_length=1)
    service_name: str = Field(..., min_length=1)
    endpoint: Optional[str] = None
    count: int = Field(default=1, ge=1)
    value: Optional[float] = None
    response_time_ms: Optional[int] = None
    status_code: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class MetricResponse(BaseModel):
    """Schema for metric response"""

    id: str
    user_id: str
    metric_type: str
    service_name: str
    count: int
    value: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class UsageStats(BaseModel):
    """Schema for usage statistics"""

    total_api_calls: int
    total_documents_signed: int
    total_verifications: int
    success_rate: float
    avg_response_time_ms: float
    total_keys_generated: int = 0
    period_start: datetime
    period_end: datetime


class ServiceMetrics(BaseModel):
    """Schema for service-specific metrics"""

    service_name: str
    total_requests: int
    success_count: int
    error_count: int
    avg_response_time_ms: float
    endpoints: Dict[str, int]


class TimeSeriesData(BaseModel):
    """Schema for time series data"""

    timestamp: datetime
    value: float
    count: int


class AnalyticsReport(BaseModel):
    """Schema for analytics report"""

    user_id: str
    period_start: datetime
    period_end: datetime
    usage_stats: UsageStats
    service_metrics: List[ServiceMetrics]
    time_series: List[TimeSeriesData]


class ActivityItem(BaseModel):
    """Schema for activity feed entries"""

    id: str
    type: str
    description: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class ActivityFeedPage(BaseModel):
    """Paginated activity feed payload."""

    items: List[ActivityItem]
    total: int
    page: int
    limit: int


class ActivityAlertCodeCount(BaseModel):
    """Top error code aggregate for alerting summaries."""

    error_code: str
    count: int


class ActivityAlertSummary(BaseModel):
    """Aggregated alert-style metrics for audit visibility."""

    total_requests: int
    failure_requests: int
    critical_failures: int
    failure_rate: float
    top_error_codes: List[ActivityAlertCodeCount]
    period_start: datetime
    period_end: datetime


class MessageResponse(BaseModel):
    """Generic message response"""

    message: str


class PageviewEvent(BaseModel):
    """Schema for anonymous pageview events"""

    site_id: str = Field(..., min_length=1, max_length=100)
    path: str = Field(..., min_length=1, max_length=2048)
    referrer: Optional[str] = Field(default=None, max_length=2048)
    user_agent: Optional[str] = Field(default=None, max_length=512)


class DiscoveryEvent(BaseModel):
    """Schema for embedding discovery events from Chrome extension"""

    timestamp: datetime
    eventType: str = Field(default="embedding_discovered")
    pageUrl: str = Field(..., max_length=2048)
    pageDomain: str = Field(..., max_length=255)
    pageTitle: Optional[str] = Field(default=None, max_length=512)
    # Embedding owner info
    signerId: Optional[str] = Field(default=None, max_length=255)
    signerName: Optional[str] = Field(default=None, max_length=255)
    organizationId: Optional[str] = Field(default=None, max_length=255)
    documentId: Optional[str] = Field(default=None, max_length=255)
    originalDomain: Optional[str] = Field(default=None, max_length=255)
    # Verification result
    verified: bool = False
    verificationStatus: Optional[str] = Field(default=None, max_length=50)
    markerType: Optional[str] = Field(default=None, max_length=50)
    # Context
    embeddingCount: int = Field(default=1, ge=1)
    discoverySource: Optional[str] = Field(default=None, max_length=64)
    domainMismatch: Optional[bool] = None
    mismatchReason: Optional[str] = Field(default=None, max_length=64)
    contentLengthBucket: Optional[str] = Field(default=None, max_length=32)
    embeddingByteLength: Optional[int] = Field(default=None, ge=0)
    # Extension metadata
    extensionVersion: Optional[str] = Field(default=None, max_length=50)
    sessionId: Optional[str] = Field(default=None, max_length=100)


class DiscoveryBatchRequest(BaseModel):
    """Schema for batch discovery events from Chrome extension"""

    events: List[DiscoveryEvent]
    source: str = Field(default="chrome_extension", max_length=50)
    version: Optional[str] = Field(default=None, max_length=50)


class DiscoveryResponse(BaseModel):
    """Response for discovery event submission"""

    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class DiscoveryStats(BaseModel):
    """Statistics for embedding discoveries"""

    total_discoveries: int
    verified_count: int
    invalid_count: int
    unique_domains: int
    unique_signers: int = 0
    external_domain_count: int = 0
    top_domains: List[Dict[str, Any]]
    top_signers: List[Dict[str, Any]] = []
    period_start: datetime
    period_end: datetime


class DomainSummaryItem(BaseModel):
    """A single domain where an org's content was discovered"""

    id: str
    page_domain: str
    discovery_count: int
    verified_count: int
    invalid_count: int
    is_owned_domain: bool
    first_seen_at: datetime
    last_seen_at: datetime


class DomainSummaryResponse(BaseModel):
    """Response for domain summary queries"""

    success: bool
    data: List[DomainSummaryItem]
    total: int


class DomainAlertItem(BaseModel):
    """An external domain alert that hasn't been acknowledged"""

    id: str
    page_domain: str
    discovery_count: int
    first_seen_at: datetime
    last_seen_at: datetime


class DomainAlertsResponse(BaseModel):
    """Response for domain alert queries"""

    success: bool
    data: List[DomainAlertItem]
    total: int


class ContentDiscoveryItem(BaseModel):
    """A single content discovery event"""

    id: str
    page_url: str
    page_domain: str
    page_title: Optional[str] = None
    signer_name: Optional[str] = None
    document_id: Optional[str] = None
    original_domain: Optional[str] = None
    verified: bool
    verification_status: Optional[str] = None
    marker_type: Optional[str] = None
    is_external_domain: bool
    discovered_at: datetime


class ContentDiscoveryListResponse(BaseModel):
    """Response for content discovery list queries"""

    success: bool
    data: List[ContentDiscoveryItem]
    total: int
    limit: int
    offset: int


# ── Owned Domain Schemas ──


class OwnedDomainCreate(BaseModel):
    """Request to add a domain to an org's allowlist"""

    domain_pattern: str = Field(..., max_length=255, description="Exact domain or wildcard pattern (e.g. '*.example.com')")
    label: Optional[str] = Field(default=None, max_length=255, description="Human-readable label")


class OwnedDomainUpdate(BaseModel):
    """Request to update an owned domain entry"""

    domain_pattern: Optional[str] = Field(default=None, max_length=255)
    label: Optional[str] = Field(default=None, max_length=255)
    is_active: Optional[bool] = None


class OwnedDomainItem(BaseModel):
    """A single owned domain entry"""

    id: str
    organization_id: str
    domain_pattern: str
    label: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class OwnedDomainListResponse(BaseModel):
    """Response for owned domain list queries"""

    success: bool
    data: List[OwnedDomainItem]
    total: int
