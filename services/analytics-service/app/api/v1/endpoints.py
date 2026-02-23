"""API endpoints for Analytics Service v1"""

from fastapi import APIRouter, Depends, HTTPException, status, Header, Query, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict
from pydantic import BaseModel
from datetime import datetime, timedelta
import csv
import httpx
import io
import json

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
    ActivityFeedPage,
    ActivityAlertSummary,
    DiscoveryBatchRequest,
    DiscoveryResponse,
    DiscoveryStats,
    DomainSummaryItem,
    DomainSummaryResponse,
    DomainAlertItem,
    DomainAlertsResponse,
    ContentDiscoveryItem,
    ContentDiscoveryListResponse,
    OwnedDomainCreate,
    OwnedDomainUpdate,
    OwnedDomainItem,
    OwnedDomainListResponse,
)
from ...services.analytics_service import AnalyticsService
from ...services.discovery_service import DiscoveryService
from ...core.config import settings

router = APIRouter()


def _resolve_activity_window(
    days: int,
    start_at: datetime | None,
    end_at: datetime | None,
) -> tuple[datetime, datetime]:
    computed_end = end_at or datetime.utcnow()
    computed_start = start_at or (computed_end - timedelta(days=days))
    return computed_start, computed_end


def _activity_filters(
    api_key_prefix: str | None,
    endpoint: str | None,
    status: str | None,
    error_code: str | None,
    request_id: str | None,
    event_type: str | None,
    actor_id: str | None,
    query: str | None,
    event_types: list[str] | None,
    severities: list[str] | None,
    has_stack: bool | None,
) -> Dict[str, object]:
    return {
        "api_key_prefix": api_key_prefix,
        "endpoint": endpoint,
        "status": status,
        "error_code": error_code,
        "request_id": request_id,
        "event_type": event_type,
        "actor_id": actor_id,
        "query": query,
        "event_types": event_types,
        "severities": severities,
        "has_stack": has_stack,
    }


def _resolve_identity(current_user: dict) -> str:
    """Extract the best identifier for analytics queries.

    Returns the organization_id if present (org-scoped metrics),
    otherwise the raw user_id. The service layer's user_or_org_filter
    checks both UsageMetric.user_id and UsageMetric.organization_id
    columns, so the raw UUID will match whichever column was written.
    """
    user_id = current_user.get("id") or current_user.get("user_id")
    org_id = current_user.get("organization_id")
    return org_id or user_id


def _should_verify_auth_header(authorization: str | None) -> bool:
    """Return True when Authorization looks like a JWT bearer token.

    Discovery events may include API-key bearer headers from browser clients.
    Those should not be sent to auth-service `/auth/verify`, which expects JWTs.
    """
    if not authorization:
        return False

    parts = authorization.strip().split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return False

    token = parts[1].strip()
    if not token:
        return False

    # JWT shape: header.payload.signature
    return token.count(".") == 2


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
        identity = _resolve_identity(current_user)

        metric = AnalyticsService.record_metric(
            db=db,
            user_id=identity,
            metric_data=metric_data,
        )
        return metric
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record metric",
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

    identity = _resolve_identity(current_user)

    stats = AnalyticsService.get_usage_stats(
        db=db,
        user_id=identity,
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

    identity = _resolve_identity(current_user)

    metrics = AnalyticsService.get_service_metrics(
        db=db,
        user_id=identity,
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

    identity = _resolve_identity(current_user)

    time_series = AnalyticsService.get_time_series(
        db=db,
        user_id=identity,
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

    identity = _resolve_identity(current_user)

    metrics = AnalyticsService.get_activity_feed(
        db=db,
        user_id=identity,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )

    return [ActivityItem(**AnalyticsService.describe_activity(metric)) for metric in metrics]


@router.get("/activity/audit-events", response_model=ActivityFeedPage)
async def get_activity_audit_events(
    days: int = Query(default=30, ge=1, le=90),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=200),
    api_key_prefix: str | None = Query(default=None),
    endpoint: str | None = Query(default=None),
    status: str | None = Query(default=None, pattern="^(success|failure)$"),
    error_code: str | None = Query(default=None),
    request_id: str | None = Query(default=None),
    event_type: str | None = Query(default=None),
    actor_id: str | None = Query(default=None),
    query: str | None = Query(default=None),
    event_types: list[str] | None = Query(default=None),
    severities: list[str] | None = Query(default=None),
    has_stack: bool | None = Query(default=None),
    start_at: datetime | None = Query(default=None),
    end_at: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get paginated audit-focused activity events with advanced filtering."""
    computed_start, computed_end = _resolve_activity_window(days, start_at, end_at)
    filters = _activity_filters(
        api_key_prefix,
        endpoint,
        status,
        error_code,
        request_id,
        event_type,
        actor_id,
        query,
        event_types,
        severities,
        has_stack,
    )

    identity = _resolve_identity(current_user)
    result = AnalyticsService.get_activity_events(
        db=db,
        user_id=identity,
        start_date=computed_start,
        end_date=computed_end,
        page=page,
        limit=limit,
        api_key_prefix=filters["api_key_prefix"],
        endpoint=filters["endpoint"],
        status=filters["status"],
        error_code=filters["error_code"],
        request_id=filters["request_id"],
        event_type=filters["event_type"],
        actor_id=filters["actor_id"],
        query=filters["query"],
        event_types=filters["event_types"],
        severities=filters["severities"],
        has_stack=filters["has_stack"],
    )

    return ActivityFeedPage(
        items=[ActivityItem(**AnalyticsService.describe_activity(metric)) for metric in result["items"]],
        total=result["total"],
        page=result["page"],
        limit=result["limit"],
    )


@router.get("/activity/audit-events/export")
async def export_activity_audit_events(
    format: str = Query(default="csv", pattern="^(csv|json)$"),
    days: int = Query(default=30, ge=1, le=90),
    api_key_prefix: str | None = Query(default=None),
    endpoint: str | None = Query(default=None),
    status: str | None = Query(default=None, pattern="^(success|failure)$"),
    error_code: str | None = Query(default=None),
    request_id: str | None = Query(default=None),
    event_type: str | None = Query(default=None),
    actor_id: str | None = Query(default=None),
    query: str | None = Query(default=None),
    event_types: list[str] | None = Query(default=None),
    severities: list[str] | None = Query(default=None),
    has_stack: bool | None = Query(default=None),
    start_at: datetime | None = Query(default=None),
    end_at: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Export filtered audit activity events as CSV or JSON."""
    computed_start, computed_end = _resolve_activity_window(days, start_at, end_at)
    filters = _activity_filters(
        api_key_prefix,
        endpoint,
        status,
        error_code,
        request_id,
        event_type,
        actor_id,
        query,
        event_types,
        severities,
        has_stack,
    )

    identity = _resolve_identity(current_user)
    rows = AnalyticsService.get_activity_export_rows(
        db=db,
        user_id=identity,
        start_date=computed_start,
        end_date=computed_end,
        api_key_prefix=filters["api_key_prefix"],
        endpoint=filters["endpoint"],
        status=filters["status"],
        error_code=filters["error_code"],
        request_id=filters["request_id"],
        event_type=filters["event_type"],
        actor_id=filters["actor_id"],
        query=filters["query"],
        event_types=filters["event_types"],
        severities=filters["severities"],
        has_stack=filters["has_stack"],
    )

    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    if format == "json":
        payload = [
            {
                **row,
                "timestamp": row["timestamp"].isoformat() if isinstance(row.get("timestamp"), datetime) else row.get("timestamp"),
            }
            for row in rows
        ]
        return Response(
            content=json.dumps(payload),
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="audit-events-{timestamp}.json"'},
        )

    headers = [
        "id",
        "timestamp",
        "type",
        "description",
        "status",
        "severity",
        "endpoint",
        "method",
        "request_id",
        "api_key",
        "error_code",
        "error_message",
        "error_details",
        "error_stack",
        "event_type",
        "actor_type",
        "actor_id",
        "resource_type",
        "resource_id",
        "organization_id",
    ]
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    for row in rows:
        csv_row = dict(row)
        ts_value = csv_row.get("timestamp")
        if isinstance(ts_value, datetime):
            csv_row["timestamp"] = ts_value.isoformat()
        writer.writerow(csv_row)

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="audit-events-{timestamp}.csv"'},
    )


@router.get("/activity/audit-events/alerts", response_model=ActivityAlertSummary)
async def get_activity_audit_alert_summary(
    days: int = Query(default=7, ge=1, le=90),
    start_at: datetime | None = Query(default=None),
    end_at: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get audit alert summary for visibility widgets and incident triage."""
    computed_start, computed_end = _resolve_activity_window(days, start_at, end_at)
    identity = _resolve_identity(current_user)

    summary = AnalyticsService.get_activity_alert_summary(
        db=db,
        user_id=identity,
        start_date=computed_start,
        end_date=computed_end,
    )
    return ActivityAlertSummary(**summary)


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
    identity = _resolve_identity(current_user)

    usage_stats = AnalyticsService.get_usage_stats(
        db=db,
        user_id=identity,
        start_date=start_date,
        end_date=end_date,
    )

    # Get service metrics
    service_metrics = AnalyticsService.get_service_metrics(
        db=db,
        user_id=identity,
        start_date=start_date,
        end_date=end_date,
    )

    # Get time series for API calls
    time_series = AnalyticsService.get_time_series(
        db=db,
        user_id=identity,
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
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to record pageview")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "analytics-service"}


@router.get("/trace/{request_id}")
async def get_request_trace(
    request_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Return all metric events recorded for a single request ID.

    Enables full stack-trace reconstruction for any API call by correlating
    every event emitted while handling the request (sign, verify, rights, etc.).
    Events are sorted oldest-first for chronological replay.

    - **request_id**: The X-Request-ID value returned in the response header
    """
    identity = _resolve_identity(current_user)

    events = (
        db.query(UsageMetric)
        .filter(UsageMetric.meta["request_id"].astext == request_id)
        .filter(
            (UsageMetric.organization_id == identity) | (UsageMetric.user_id == identity)
        )
        .order_by(UsageMetric.created_at.asc())
        .all()
    )

    if not events:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No events found for request_id: {request_id}",
        )

    items = []
    for m in events:
        items.append({
            "id": str(m.id),
            "metric_type": m.metric_type,
            "endpoint": m.endpoint,
            "method": m.meta.get("method") if isinstance(m.meta, dict) else None,
            "status_code": m.status_code,
            "response_time_ms": m.response_time_ms,
            "organization_id": m.organization_id,
            "user_id": m.user_id,
            "api_key_id": m.api_key_id,
            "timestamp": m.created_at.isoformat() if m.created_at else None,
            "metadata": m.meta,
        })

    return {
        "request_id": request_id,
        "event_count": len(items),
        "events": items,
    }


# ============================================
# Public Discovery Analytics Endpoints
# ============================================

_discovery_rl_store = {}


def _discovery_rate_limit(ip: str, limit: int = 100, window_sec: int = 60):
    """Rate limit for discovery endpoint - more permissive than pageview"""
    import time

    now = time.time()
    key = ("discovery", ip)
    timestamps = _discovery_rl_store.get(key, [])
    cutoff = now - window_sec
    timestamps = [t for t in timestamps if t >= cutoff]
    if len(timestamps) >= limit:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")
    timestamps.append(now)
    _discovery_rl_store[key] = timestamps


@router.post("/discovery", response_model=DiscoveryResponse, status_code=status.HTTP_202_ACCEPTED)
async def record_discovery_events(
    batch: DiscoveryBatchRequest,
    request: Request,
    db: Session = Depends(get_db),
    authorization: str = Header(default=None),
):
    """
    Record embedding discovery events from Chrome extension.
    
    This is a public endpoint that accepts anonymous discovery reports.
    If an API key is provided, events are associated with the organization.
    
    - **events**: List of discovery events
    - **source**: Source of events (e.g., "chrome_extension")
    - **version**: Extension version
    """
    # Determine client IP for rate limiting
    ip = request.headers.get("x-forwarded-for")
    if ip:
        ip = ip.split(",")[0].strip()
    else:
        ip = request.client.host if request.client else "unknown"
    
    _discovery_rate_limit(ip, limit=100, window_sec=60)
    
    # Try to get organization from auth if token provided
    organization_id = None
    if _should_verify_auth_header(authorization):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.AUTH_SERVICE_URL}/api/v1/auth/verify",
                    headers={"Authorization": authorization}
                )
                if response.status_code == 200:
                    payload = response.json()
                    if isinstance(payload, dict) and payload.get("success"):
                        user_data = payload.get("data", {})
                        organization_id = user_data.get("organization_id")
        except Exception:
            pass  # Continue without org association
    
    try:
        # Record into dedicated content_discoveries table
        events_recorded = DiscoveryService.record_batch(
            db=db,
            events=batch.events,
            source=batch.source,
            extension_version=batch.version,
        )

        # Also record into legacy UsageMetric for backward compatibility
        for event in batch.events:
            try:
                AnalyticsService.record_metric(
                    db=db,
                    user_id=organization_id or "anonymous",
                    metric_data=MetricCreate(
                        metric_type="embedding_discovery",
                        service_name="chrome_extension",
                        endpoint=event.pageDomain,
                        count=event.embeddingCount,
                        value=1 if event.verified else 0,
                        response_time_ms=None,
                        status_code=200 if event.verified else 400,
                        metadata={
                            "page_url": event.pageUrl,
                            "page_domain": event.pageDomain,
                            "page_title": event.pageTitle,
                            "signer_id": event.signerId,
                            "signer_name": event.signerName,
                            "organization_id": event.organizationId,
                            "document_id": event.documentId,
                            "original_domain": event.originalDomain,
                            "verified": event.verified,
                            "verification_status": event.verificationStatus,
                            "marker_type": event.markerType,
                            "domain_mismatch": event.domainMismatch,
                            "mismatch_reason": event.mismatchReason,
                            "discovery_source": event.discoverySource,
                            "content_length_bucket": event.contentLengthBucket,
                            "embedding_byte_length": event.embeddingByteLength,
                            "extension_version": event.extensionVersion or batch.version,
                            "session_id": event.sessionId,
                            "source": batch.source,
                        },
                    ),
                    organization_id=organization_id,
                )
            except Exception:
                pass  # Legacy metric recording is best-effort
        
        return DiscoveryResponse(
            success=True,
            data={
                "events_recorded": events_recorded,
                "message": "Discovery events recorded successfully"
            },
            error=None
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process discovery events",
        )


@router.get("/discovery/stats", response_model=DiscoveryStats)
async def get_discovery_stats(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get discovery statistics for the authenticated organization.
    
    - **days**: Number of days to look back (default: 30)
    """
    from sqlalchemy import func, distinct
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    identity = _resolve_identity(current_user)
    
    # Query discovery metrics
    base_query = db.query(UsageMetric).filter(
        UsageMetric.metric_type == "embedding_discovery",
        UsageMetric.created_at >= start_date,
        UsageMetric.created_at <= end_date,
    )
    
    # Filter by organization if not admin
    user_role = current_user.get("role", "").lower()
    is_admin = bool(current_user.get("is_super_admin")) or user_role in ("admin", "super_admin")
    
    if not is_admin:
        # Show discoveries where this org's content was found
        base_query = base_query.filter(
            UsageMetric.meta["organization_id"].astext == identity
        )
    
    # Get total counts
    total_discoveries = base_query.count()
    verified_count = base_query.filter(UsageMetric.meta["verified"].astext == "true").count()
    invalid_count = total_discoveries - verified_count
    
    # Get unique domains
    unique_domains = db.query(func.count(distinct(UsageMetric.endpoint))).filter(
        UsageMetric.metric_type == "embedding_discovery",
        UsageMetric.created_at >= start_date,
    ).scalar() or 0
    
    # Get unique signers
    unique_signers = db.query(func.count(distinct(UsageMetric.meta["signer_id"].astext))).filter(
        UsageMetric.metric_type == "embedding_discovery",
        UsageMetric.created_at >= start_date,
        UsageMetric.meta["signer_id"].astext.isnot(None),
    ).scalar() or 0
    
    # Get top domains
    top_domains_query = db.query(
        UsageMetric.endpoint,
        func.count(UsageMetric.id).label("count")
    ).filter(
        UsageMetric.metric_type == "embedding_discovery",
        UsageMetric.created_at >= start_date,
    ).group_by(UsageMetric.endpoint).order_by(func.count(UsageMetric.id).desc()).limit(10).all()
    
    top_domains = [{"domain": d[0], "count": d[1]} for d in top_domains_query if d[0]]
    
    # Get top signers
    top_signers_query = db.query(
        UsageMetric.meta["signer_id"].astext.label("signer_id"),
        UsageMetric.meta["signer_name"].astext.label("signer_name"),
        func.count(UsageMetric.id).label("count")
    ).filter(
        UsageMetric.metric_type == "embedding_discovery",
        UsageMetric.created_at >= start_date,
        UsageMetric.meta["signer_id"].astext.isnot(None),
    ).group_by(
        UsageMetric.meta["signer_id"].astext,
        UsageMetric.meta["signer_name"].astext
    ).order_by(func.count(UsageMetric.id).desc()).limit(10).all()
    
    top_signers = [
        {"signer_id": s[0], "signer_name": s[1], "count": s[2]} 
        for s in top_signers_query if s[0]
    ]
    
    return DiscoveryStats(
        total_discoveries=total_discoveries,
        verified_count=verified_count,
        invalid_count=invalid_count,
        unique_domains=unique_domains,
        unique_signers=unique_signers,
        top_domains=top_domains,
        top_signers=top_signers,
        period_start=start_date,
        period_end=end_date,
    )


@router.get("/discovery/domains", response_model=DomainSummaryResponse)
async def get_discovery_domains(
    external_only: bool = Query(default=False, description="Only show external (non-owned) domains"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get domain summaries showing where the organization's content was discovered.

    Each item represents a unique domain where signed content was found,
    with counts and ownership status.
    """
    identity = _resolve_identity(current_user)

    summaries = DiscoveryService.get_domain_summaries(
        db=db,
        organization_id=identity,
        external_only=external_only,
    )

    items = [
        DomainSummaryItem(
            id=s.id,
            page_domain=s.page_domain,
            discovery_count=s.discovery_count,
            verified_count=s.verified_count,
            invalid_count=s.invalid_count,
            is_owned_domain=bool(s.is_owned_domain),
            first_seen_at=s.first_seen_at,
            last_seen_at=s.last_seen_at,
        )
        for s in summaries
    ]

    return DomainSummaryResponse(success=True, data=items, total=len(items))


@router.get("/discovery/alerts", response_model=DomainAlertsResponse)
async def get_discovery_alerts(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get unacknowledged alerts for external domains where the org's content
    was found.  These represent potential copy-paste or syndication events.
    """
    identity = _resolve_identity(current_user)

    alerts = DiscoveryService.get_new_domain_alerts(
        db=db,
        organization_id=identity,
    )

    items = [
        DomainAlertItem(
            id=a.id,
            page_domain=a.page_domain,
            discovery_count=a.discovery_count,
            first_seen_at=a.first_seen_at,
            last_seen_at=a.last_seen_at,
        )
        for a in alerts
    ]

    return DomainAlertsResponse(success=True, data=items, total=len(items))


@router.post("/discovery/alerts/{alert_id}/ack", response_model=DiscoveryResponse)
async def acknowledge_discovery_alert(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Acknowledge a domain discovery alert so it no longer appears in the alerts list."""
    DiscoveryService.mark_alert_sent(db=db, summary_id=alert_id)
    return DiscoveryResponse(
        success=True,
        data={"message": "Alert acknowledged"},
        error=None,
    )


@router.get("/discovery/events", response_model=ContentDiscoveryListResponse)
async def get_discovery_events(
    days: int = Query(default=30, ge=1, le=365),
    external_only: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get paginated content discovery events for the authenticated organization.
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    identity = _resolve_identity(current_user)

    discoveries = DiscoveryService.get_discoveries_for_org(
        db=db,
        organization_id=identity,
        start_date=start_date,
        end_date=end_date,
        external_only=external_only,
        limit=limit,
        offset=offset,
    )

    items = [
        ContentDiscoveryItem(
            id=d.id,
            page_url=d.page_url,
            page_domain=d.page_domain,
            page_title=d.page_title,
            signer_name=d.signer_name,
            document_id=d.document_id,
            original_domain=d.original_domain,
            verified=bool(d.verified),
            verification_status=d.verification_status,
            marker_type=d.marker_type,
            is_external_domain=bool(d.is_external_domain),
            discovered_at=d.discovered_at,
        )
        for d in discoveries
    ]

    # Get total count for pagination
    from ...db.models import ContentDiscovery as CDModel
    total_query = db.query(func.count(CDModel.id)).filter(
        CDModel.organization_id == identity,
        CDModel.discovered_at >= start_date,
        CDModel.discovered_at <= end_date,
    )
    if external_only:
        total_query = total_query.filter(CDModel.is_external_domain == 1)
    total = total_query.scalar() or 0

    return ContentDiscoveryListResponse(
        success=True,
        data=items,
        total=total,
        limit=limit,
        offset=offset,
    )


# ============================================
# Owned Domain Management Endpoints
# ============================================


@router.get("/discovery/owned-domains", response_model=OwnedDomainListResponse)
async def list_owned_domains(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List all owned domain patterns for the current organization."""
    org_id = current_user.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization ID required",
        )

    domains = DiscoveryService.get_owned_domains(db, org_id, active_only=False)
    items = [
        OwnedDomainItem(
            id=d.id,
            organization_id=d.organization_id,
            domain_pattern=d.domain_pattern,
            label=d.label,
            is_active=bool(d.is_active),
            created_at=d.created_at,
            updated_at=d.updated_at,
        )
        for d in domains
    ]
    return OwnedDomainListResponse(success=True, data=items, total=len(items))


@router.post("/discovery/owned-domains", response_model=OwnedDomainItem, status_code=status.HTTP_201_CREATED)
async def add_owned_domain(
    body: OwnedDomainCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Add a domain pattern to the organization's allowlist.

    Supports exact domains (``example.com``) and wildcard patterns
    (``*.example.com``) for subdomain matching.
    """
    org_id = current_user.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization ID required",
        )

    try:
        owned = DiscoveryService.add_owned_domain(
            db,
            organization_id=org_id,
            domain_pattern=body.domain_pattern,
            label=body.label,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    return OwnedDomainItem(
        id=owned.id,
        organization_id=owned.organization_id,
        domain_pattern=owned.domain_pattern,
        label=owned.label,
        is_active=bool(owned.is_active),
        created_at=owned.created_at,
        updated_at=owned.updated_at,
    )


@router.patch("/discovery/owned-domains/{domain_id}", response_model=OwnedDomainItem)
async def update_owned_domain(
    domain_id: str,
    body: OwnedDomainUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Update an owned domain entry (pattern, label, or active status)."""
    org_id = current_user.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization ID required",
        )

    owned = DiscoveryService.update_owned_domain(
        db,
        domain_id=domain_id,
        organization_id=org_id,
        domain_pattern=body.domain_pattern,
        label=body.label,
        is_active=body.is_active,
    )
    if not owned:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Owned domain not found",
        )

    return OwnedDomainItem(
        id=owned.id,
        organization_id=owned.organization_id,
        domain_pattern=owned.domain_pattern,
        label=owned.label,
        is_active=bool(owned.is_active),
        created_at=owned.created_at,
        updated_at=owned.updated_at,
    )


@router.delete("/discovery/owned-domains/{domain_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_owned_domain(
    domain_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Remove a domain pattern from the organization's allowlist."""
    org_id = current_user.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization ID required",
        )

    deleted = DiscoveryService.delete_owned_domain(db, domain_id=domain_id, organization_id=org_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Owned domain not found",
        )


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
