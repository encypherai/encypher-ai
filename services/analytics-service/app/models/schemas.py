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
    total_keys_generated: int
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


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
