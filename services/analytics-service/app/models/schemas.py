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
    # Verification result
    verified: bool = False
    verificationStatus: Optional[str] = Field(default=None, max_length=50)
    markerType: Optional[str] = Field(default=None, max_length=50)
    # Context
    embeddingCount: int = Field(default=1, ge=1)
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
    unique_signers: int
    top_domains: List[Dict[str, Any]]
    top_signers: List[Dict[str, Any]]
    period_start: datetime
    period_end: datetime
