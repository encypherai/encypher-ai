"""API endpoints for Analytics Service v1"""
from fastapi import APIRouter, Depends, HTTPException, status, Header, Query, Request
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
import httpx

from ...db.session import get_db
from ...models.schemas import (
    MetricCreate,
    MetricResponse,
    UsageStats,
    ServiceMetrics,
    TimeSeriesData,
    AnalyticsReport,
    PageviewEvent,
)
from ...services.analytics_service import AnalyticsService
from ...core.config import settings

router = APIRouter()


async def get_current_user(authorization: str = Header(...)) -> dict:
    """Verify user token with auth service and return user dict from Standard Response Format."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.AUTH_SERVICE_URL}/api/v1/auth/verify",
                headers={"Authorization": authorization}
            )
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
        metric = AnalyticsService.record_metric(
            db=db,
            user_id=current_user["id"],
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

    stats = AnalyticsService.get_usage_stats(
        db=db,
        user_id=current_user["id"],
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

    metrics = AnalyticsService.get_service_metrics(
        db=db,
        user_id=current_user["id"],
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

    time_series = AnalyticsService.get_time_series(
        db=db,
        user_id=current_user["id"],
        metric_type=metric_type,
        start_date=start_date,
        end_date=end_date,
        interval=interval,
    )

    return [TimeSeriesData(**ts) for ts in time_series]


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
    usage_stats = AnalyticsService.get_usage_stats(
        db=db,
        user_id=current_user["id"],
        start_date=start_date,
        end_date=end_date,
    )

    # Get service metrics
    service_metrics = AnalyticsService.get_service_metrics(
        db=db,
        user_id=current_user["id"],
        start_date=start_date,
        end_date=end_date,
    )

    # Get time series for API calls
    time_series = AnalyticsService.get_time_series(
        db=db,
        user_id=current_user["id"],
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
