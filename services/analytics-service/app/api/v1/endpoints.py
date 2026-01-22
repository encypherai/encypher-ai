"""API endpoints for Analytics Service v1"""

from fastapi import APIRouter, Depends, HTTPException, status, Header, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict
from pydantic import BaseModel
from datetime import datetime, timedelta
import httpx

from ...db.session import get_db
from ...db.models import UsageMetric
from ...models.schemas import (
    MetricCreate,
    MetricResponse,
    UsageStats,
    ServiceMetrics,
    TimeSeriesData,
    AnalyticsReport,
    PageviewEvent,
    ActivityItem,
)
from ...services.analytics_service import AnalyticsService
from ...core.config import settings

router = APIRouter()


async def get_current_user(authorization: str = Header(...)) -> dict:
    """Verify user token with auth service and return user dict from Standard Response Format."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{settings.AUTH_SERVICE_URL}/api/v1/auth/verify", headers={"Authorization": authorization})
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                )
            payload = response.json()
            # Expect { success: bool, data: { user fields }, error: null }
            if isinstance(payload, dict) and payload.get("success") and isinstance(payload.get("data"), dict):
                return payload["data"]
            # Fallback for legacy direct user payloads
            if isinstance(payload, dict) and "id" in payload:
                return payload
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Invalid response from auth service",
            )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth service unavailable",
        )


@router.post("/metrics", response_model=MetricResponse, status_code=status.HTTP_201_CREATED)
async def record_metric(
    metric_data: MetricCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Record a usage metric

    - **metric_type**: Type of metric (api_call, document_signed, verification, etc.)
    - **service_name**: Service name
    - **endpoint**: Optional endpoint
    - **count**: Count (default: 1)
    - **value**: Optional numeric value
    - **response_time_ms**: Optional response time
    - **status_code**: Optional HTTP status code
    """
    try:
        user_id = current_user.get("id") or current_user.get("user_id")
        org_id = current_user.get("organization_id") or (f"user_{user_id}" if user_id else None)

        metric = AnalyticsService.record_metric(
            db=db,
            user_id=org_id or user_id,
            metric_data=metric_data,
        )
        return metric
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record metric: {str(e)}",
        )


@router.get("/usage", response_model=UsageStats)
async def get_usage_stats(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get usage statistics

    - **days**: Number of days to look back (default: 30)
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Use organization_id if available, fall back to user_id
    # For user-level API keys, organization_id is "user_{user_id}"
    user_id = current_user.get("id") or current_user.get("user_id")
    org_id = current_user.get("organization_id") or (f"user_{user_id}" if user_id else None)

    # Query by organization_id first (new metrics), then user_id (legacy)
    stats = AnalyticsService.get_usage_stats(
        db=db,
        user_id=org_id or user_id,
        start_date=start_date,
        end_date=end_date,
    )

    return UsageStats(**stats)


@router.get("/services", response_model=List[ServiceMetrics])
async def get_service_metrics(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get metrics grouped by service

    - **days**: Number of days to look back (default: 30)
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    user_id = current_user.get("id") or current_user.get("user_id")
    org_id = current_user.get("organization_id") or (f"user_{user_id}" if user_id else None)

    metrics = AnalyticsService.get_service_metrics(
        db=db,
        user_id=org_id or user_id,
        start_date=start_date,
        end_date=end_date,
    )

    return [ServiceMetrics(**m) for m in metrics]


@router.get("/timeseries", response_model=List[TimeSeriesData])
async def get_time_series(
    metric_type: str = Query(..., description="Metric type to query"),
    days: int = Query(default=7, ge=1, le=90),
    interval: str = Query(default="hour", pattern="^(hour|day)$"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get time series data

    - **metric_type**: Type of metric
    - **days**: Number of days to look back (default: 7)
    - **interval**: Aggregation interval (hour or day)
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    user_id = current_user.get("id") or current_user.get("user_id")
    org_id = current_user.get("organization_id") or (f"user_{user_id}" if user_id else None)

    time_series = AnalyticsService.get_time_series(
        db=db,
        user_id=org_id or user_id,
        metric_type=metric_type,
        start_date=start_date,
        end_date=end_date,
        interval=interval,
    )

    return [TimeSeriesData(**ts) for ts in time_series]


@router.get("/activity", response_model=List[ActivityItem])
async def get_activity_feed(
    days: int = Query(default=7, ge=1, le=90),
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get recent activity feed entries.

    - **days**: Number of days to look back (default: 7)
    - **limit**: Maximum number of items to return (default: 10)
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    user_id = current_user.get("id") or current_user.get("user_id")
    org_id = current_user.get("organization_id") or (f"user_{user_id}" if user_id else None)

    metrics = AnalyticsService.get_activity_feed(
        db=db,
        user_id=org_id or user_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )

    return [ActivityItem(**AnalyticsService.describe_activity(metric)) for metric in metrics]


@router.get("/report", response_model=AnalyticsReport)
async def get_analytics_report(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get comprehensive analytics report

    - **days**: Number of days to look back (default: 30)
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Get usage stats
    user_id = current_user.get("id") or current_user.get("user_id")
    org_id = current_user.get("organization_id") or (f"user_{user_id}" if user_id else None)

    usage_stats = AnalyticsService.get_usage_stats(
        db=db,
        user_id=org_id or user_id,
        start_date=start_date,
        end_date=end_date,
    )

    # Get service metrics
    service_metrics = AnalyticsService.get_service_metrics(
        db=db,
        user_id=org_id or user_id,
        start_date=start_date,
        end_date=end_date,
    )

    # Get time series for API calls
    time_series = AnalyticsService.get_time_series(
        db=db,
        user_id=org_id or user_id,
        metric_type="api_call",
        start_date=start_date,
        end_date=end_date,
        interval="day",
    )

    return AnalyticsReport(
        user_id=current_user["id"],
        period_start=start_date,
        period_end=end_date,
        usage_stats=UsageStats(**usage_stats),
        service_metrics=[ServiceMetrics(**m) for m in service_metrics],
        time_series=[TimeSeriesData(**ts) for ts in time_series],
    )


# --- Public Anonymous Pageview Endpoint ---
_rl_store = {}


def _rate_limit(ip: str, route: str, limit: int = 60, window_sec: int = 60):
    import time

    now = time.time()
    key = (ip, route)
    timestamps = _rl_store.get(key, [])
    cutoff = now - window_sec
    timestamps = [t for t in timestamps if t >= cutoff]
    if len(timestamps) >= limit:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")
    timestamps.append(now)
    _rl_store[key] = timestamps


@router.post("/pageview", status_code=status.HTTP_202_ACCEPTED)
async def record_pageview(event: PageviewEvent, request: Request, db: Session = Depends(get_db)):
    """Record anonymous pageview with basic rate limiting."""
    # Determine client IP
    ip = request.headers.get("x-forwarded-for")
    if ip:
        ip = ip.split(",")[0].strip()
    else:
        ip = request.client.host if request.client else "unknown"
    _rate_limit(ip, "analytics_pageview", limit=60, window_sec=60)

    try:
        # Persist minimal event as a metric for aggregation
        AnalyticsService.record_metric(
            db=db,
            user_id="anonymous",
            metric_data=MetricCreate(
                metric_type="pageview",
                service_name="website",
                endpoint=event.path,
                count=1,
                value=None,
                response_time_ms=None,
                status_code=200,
                metadata={
                    "site_id": event.site_id,
                    "referrer": event.referrer,
                    "user_agent": event.user_agent,
                    "ip": ip,
                },
            ),
            organization_id=None,
        )
        return {"success": True, "data": {"message": "accepted"}, "error": None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record pageview: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "analytics-service"}


# ============================================
# Admin Analytics Endpoints
# ============================================


class AdminUsageCountsRequest(BaseModel):
    user_ids: List[str]
    days: int = 30


class AdminUsageCountsResponse(BaseModel):
    usage_counts: Dict[str, int]


@router.post("/admin/usage-counts", response_model=AdminUsageCountsResponse)
async def get_admin_usage_counts(
    request: AdminUsageCountsRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get usage counts for multiple users (admin only).
    Returns a dict mapping user_id -> total API calls in the specified period.
    """
    # Check if user is admin/super_admin
    user_role = current_user.get("role", "").lower()
    is_super_admin = bool(current_user.get("is_super_admin"))
    if not is_super_admin and user_role not in ("admin", "super_admin", "superadmin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    cutoff = datetime.utcnow() - timedelta(days=request.days)

    # Query usage counts grouped by user_id
    results = (
        db.query(UsageMetric.user_id, func.count(UsageMetric.id).label("count"))
        .filter(
            UsageMetric.user_id.in_(request.user_ids),
            UsageMetric.created_at >= cutoff,
        )
        .group_by(UsageMetric.user_id)
        .all()
    )

    # Build response dict, defaulting to 0 for users with no activity
    usage_counts = {uid: 0 for uid in request.user_ids}
    for user_id, count in results:
        if user_id:
            usage_counts[user_id] = count

    return AdminUsageCountsResponse(usage_counts=usage_counts)


class UserActivityResponse(BaseModel):
    activities: List[Dict]
    total: int
    limit: int
    offset: int
    has_more: bool


@router.get("/user/{user_id}/activity", response_model=UserActivityResponse)
async def get_user_activity(
    user_id: str,
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    metric_type: str = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get activity logs for a specific user (admin only).
    Supports filtering by metric_type and pagination.
    """
    # Check if user is admin or requesting their own data
    user_role = current_user.get("role", "").lower()
    current_user_id = str(current_user.get("id", ""))
    is_admin = bool(current_user.get("is_super_admin")) or user_role in ("admin", "super_admin", "superadmin")
    is_self = current_user_id == user_id

    if not is_admin and not is_self:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    cutoff = datetime.utcnow() - timedelta(days=days)

    # Build query
    query = db.query(UsageMetric).filter(
        UsageMetric.user_id == user_id,
        UsageMetric.created_at >= cutoff,
    )

    if metric_type:
        query = query.filter(UsageMetric.metric_type == metric_type)

    # Get total count
    total = query.count()

    # Get paginated results
    metrics = (
        query.order_by(UsageMetric.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    # Transform to activity items
    activities = []
    for m in metrics:
        method = None
        if isinstance(m.meta, dict):
            method = m.meta.get("method")
        activities.append({
            "id": str(m.id),
            "type": m.metric_type or "api_call",
            "description": f"{method or 'API'} {m.endpoint or 'request'}",
            "timestamp": m.created_at.isoformat() if m.created_at else None,
            "metadata": {
                "endpoint": m.endpoint,
                "method": method,
                "status": m.status_code,
                "latency_ms": m.response_time_ms,
            },
        })

    return UserActivityResponse(
        activities=activities,
        total=total,
        limit=limit,
        offset=offset,
        has_more=(offset + limit) < total,
    )
