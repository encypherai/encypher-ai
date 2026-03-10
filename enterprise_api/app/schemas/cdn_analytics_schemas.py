"""
Pydantic schemas for CDN analytics endpoints.
"""

from pydantic import BaseModel


class CdnAnalyticsSummary(BaseModel):
    organization_id: str
    assets_protected: int
    variants_registered: int
    image_requests_tracked: int
    recoverable_percent: float  # 0-100


class CdnAnalyticsTimelineDay(BaseModel):
    date: str  # YYYY-MM-DD
    images_signed: int
    image_requests: int


class CdnAnalyticsTimeline(BaseModel):
    days: int
    data: list[CdnAnalyticsTimelineDay]
