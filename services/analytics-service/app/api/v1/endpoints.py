"""API endpoints for Analytics Service v1"""

import csv
import io
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, status
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy import distinct, func
from sqlalchemy.orm import Session

from ...core.config import settings
from ...db.models import ContentDiscovery as CDModel
from ...db.models import UsageMetric
from ...db.session import get_db
from ...models.schemas import (
    ActivityAlertSummary,
    ActivityFeedPage,
    ActivityItem,
    AnalyticsReport,
    ContentDiscoveryItem,
    ContentDiscoveryListResponse,
    DiscoveryBatchRequest,
    DiscoveryResponse,
    DiscoveryStats,
    DomainAlertItem,
    DomainAlertsResponse,
    DomainSummaryItem,
    DomainSummaryResponse,
    MetricCreate,
    MetricResponse,
    OwnedDomainCreate,
    OwnedDomainItem,
    OwnedDomainListResponse,
    OwnedDomainUpdate,
    PageviewEvent,
    ServiceMetrics,
    TimeSeriesData,
    UsageStats,
)
from ...services.analytics_service import AnalyticsService
from ...services.discovery_service import DiscoveryService

logger = logging.getLogger(__name__)

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


def _extract_bearer_token(authorization: str | None) -> Optional[str]:
    if not authorization:
        return None

    parts = authorization.strip().split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    token = parts[1].strip()
    return token or None


async def _resolve_reporter_organization_id(authorization: str | None) -> Optional[str]:
    """Resolve the reporter org from either JWT auth or API-key auth.

    This context is useful for telemetry and self-verification flows, but must not
    replace the owner-attribution fields derived from verified discovery payloads.
    """
    token = _extract_bearer_token(authorization)
    if not token:
        return None

    try:
        async with httpx.AsyncClient() as client:
            if _should_verify_auth_header(authorization):
                response = await client.post(
                    f"{settings.AUTH_SERVICE_URL}/api/v1/auth/verify",
                    headers={"Authorization": authorization},
                )
                if response.status_code == 200:
                    payload = response.json()
                    if isinstance(payload, dict) and payload.get("success"):
                        user_data = payload.get("data", {})
                        return user_data.get("organization_id")
                    if isinstance(payload, dict):
                        return payload.get("organization_id")
                return None

            response = await client.post(
                f"{settings.KEY_SERVICE_URL}/api/v1/keys/validate-minimal",
                json={"key": token},
            )
            if response.status_code == 200:
                payload = response.json()
                if isinstance(payload, dict) and payload.get("success"):
                    key_data = payload.get("data", {})
                    return key_data.get("organization_id")
    except Exception as exc:
        logger.debug("Reporter org lookup skipped for discovery event: %s", exc)

    return None


async def get_current_user(authorization: str = Header(...)) -> dict:
    """Verify user token with auth service and return user dict from Standard Response Format."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{settings.AUTH_SERVICE_URL}/api/v1/auth/verify", headers={"Authorization": authorization})
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "code": "INVALID_CREDENTIALS",
                        "detail": "Invalid authentication credentials",
                        "next_action": "Obtain a valid JWT via POST /api/v1/auth/login and include it as Authorization: Bearer <token>",
                    },
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
                detail={
                    "code": "AUTH_SERVICE_ERROR",
                    "detail": "Invalid response from auth service",
                    "next_action": "Retry the request. If the error persists, contact support.",
                },
            )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "AUTH_SERVICE_UNAVAILABLE",
                "detail": "Auth service unavailable",
                "next_action": "Retry after a short delay. If the error persists, contact support.",
            },
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
            detail={
                "code": "METRIC_RECORD_ERROR",
                "detail": "Failed to record metric",
                "next_action": "Retry the request. Check GET /api/v1/analytics/health for service status.",
            },
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

    _EXPORT_ROW_CAP = 10_000

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

    # Overflow protection: cap at _EXPORT_ROW_CAP rows
    truncated = len(rows) > _EXPORT_ROW_CAP
    if truncated:
        rows = rows[:_EXPORT_ROW_CAP]

    extra_headers: dict = {}
    if truncated:
        extra_headers["X-Truncated"] = "true"
        extra_headers["X-Row-Cap"] = str(_EXPORT_ROW_CAP)
        extra_headers["X-Next-Action"] = "Result set was truncated. Use start_at/end_at or add filters to narrow the query."

    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    if format == "json":
        payload = [
            {
                **{k: _sanitize_string(v) for k, v in row.items()},
                "timestamp": row["timestamp"].isoformat() if isinstance(row.get("timestamp"), datetime) else row.get("timestamp"),
            }
            for row in rows
        ]
        resp_body: dict = {"data": payload, "row_count": len(payload)}
        if truncated:
            resp_body["truncated"] = True
            resp_body["next_action"] = extra_headers["X-Next-Action"]
        return Response(
            content=json.dumps(resp_body),
            media_type="application/json",
            headers={
                "Content-Disposition": f'attachment; filename="audit-events-{timestamp}.json"',
                **extra_headers,
            },
        )

    csv_field_names = [
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
    writer = csv.DictWriter(output, fieldnames=csv_field_names)
    writer.writeheader()
    for row in rows:
        csv_row = {k: _sanitize_string(v) for k, v in dict(row).items()}
        ts_value = csv_row.get("timestamp")
        if isinstance(ts_value, datetime):
            csv_row["timestamp"] = ts_value.isoformat()
        writer.writerow(csv_row)

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="audit-events-{timestamp}.csv"',
            **extra_headers,
        },
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

# Single in-process rate-limit store keyed by (route, ip).
# NOTE: This is process-local and resets on restart; suitable for low-traffic
# deployments only. For multi-instance setups, replace with Redis-backed limits.
_rl_store: Dict[tuple, list] = {}


def _client_ip(request: Request) -> str:
    """Extract real client IP from X-Forwarded-For (rightmost entry).

    Behind a reverse proxy, the proxy appends the real client IP as the last
    entry in X-Forwarded-For. Earlier entries may be spoofed by the client.
    """
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        ips = [ip.strip() for ip in forwarded.split(",") if ip.strip()]
        if ips:
            return ips[-1]
    return request.client.host if request.client else "unknown"


def _rate_limit(ip: str, route: str, limit: int = 60, window_sec: int = 60) -> None:
    """Sliding-window in-process rate limiter. Raises HTTP 429 when limit is exceeded."""
    now = time.time()
    key = (route, ip)
    timestamps = _rl_store.get(key, [])
    cutoff = now - window_sec
    timestamps = [t for t in timestamps if t >= cutoff]
    if len(timestamps) >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={"Retry-After": str(window_sec)},
        )
    timestamps.append(now)
    _rl_store[key] = timestamps


def _make_error(detail: str, next_action: str, code: str = "ERROR", request_id: str | None = None) -> dict:
    """Build a uniform error response body with navigation hint and optional request_id."""
    body: dict = {
        "success": False,
        "error": {
            "code": code,
            "detail": detail,
            "next_action": next_action,
        },
        "data": None,
    }
    if request_id:
        body["error"]["request_id"] = request_id
    return body


def _sanitize_string(value: object) -> object:
    """Strip null bytes and non-printable control characters from string values.

    Used to guard CSV/JSON export rows against binary or malformed content
    originating from the meta JSON field.
    """
    if not isinstance(value, str):
        return value
    # Remove null bytes and ASCII control characters (except tab, newline, CR)
    return "".join(ch for ch in value if ch == "\t" or ch == "\n" or ch == "\r" or (ord(ch) >= 32))


@router.post("/pageview", status_code=status.HTTP_202_ACCEPTED)
async def record_pageview(event: PageviewEvent, request: Request, db: Session = Depends(get_db)):
    """Record anonymous pageview with basic rate limiting."""
    ip = _client_ip(request)
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "PAGEVIEW_RECORD_ERROR",
                "detail": "Failed to record pageview",
                "next_action": "Retry the request. Check GET /health for service status.",
            },
        )


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
        .filter((UsageMetric.organization_id == identity) | (UsageMetric.user_id == identity))
        .order_by(UsageMetric.created_at.asc())
        .all()
    )

    if not events:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "TRACE_NOT_FOUND",
                "detail": f"No events found for request_id: {request_id}",
                "next_action": (
                    "Verify the request_id value from the X-Request-ID response header. "
                    "Use GET /api/v1/analytics/activity/audit-events to browse recent events."
                ),
            },
        )

    items = []
    for m in events:
        items.append(
            {
                "id": str(m.id),
                "metric_type": m.metric_type,
                "endpoint": m.endpoint,
                "method": m.meta.get("method") if isinstance(m.meta, dict) else None,
                "status_code": m.status_code,
                "response_time_ms": m.response_time_ms,
                "organization_id": m.organization_id,
                "user_id": m.user_id,
                "timestamp": m.created_at.isoformat() if m.created_at else None,
                "metadata": m.meta,
            }
        )

    return {
        "request_id": request_id,
        "event_count": len(items),
        "events": items,
    }


# ============================================
# Public Discovery Analytics Endpoints
# ============================================


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
    ip = _client_ip(request)
    _rate_limit(ip, "discovery", limit=100, window_sec=60)

    reporter_organization_id = await _resolve_reporter_organization_id(authorization)

    # Trust model:
    # - reporter_organization_id comes from server-side auth/key validation for the sender.
    # - event.organizationId is treated as owner attribution from verified content metadata.
    #   We preserve it so the original signer can see discoveries even when the reporter is
    #   anonymous or authenticated as a different org.
    # - if owner attribution is absent, fall back to the reporter org for self-verification.
    sanitized_events = []
    for event in batch.events:
        owner_org_id = _sanitize_string(event.organizationId)
        if not owner_org_id and reporter_organization_id:
            owner_org_id = reporter_organization_id
        sanitized_events.append(event.model_copy(update={"organizationId": owner_org_id}))

    try:
        # Record into dedicated content_discoveries table
        events_recorded = DiscoveryService.record_batch(
            db=db,
            events=sanitized_events,
            source=batch.source,
            extension_version=batch.version,
        )

        # Also record into legacy UsageMetric for backward compatibility
        for event in sanitized_events:
            try:
                metric_org_id = _sanitize_string(event.organizationId)
                AnalyticsService.record_metric(
                    db=db,
                    user_id=reporter_organization_id or "anonymous",
                    metric_data=MetricCreate(
                        metric_type="embedding_discovery",
                        service_name="chrome_extension",
                        endpoint=event.pageDomain,
                        count=event.embeddingCount,
                        value=1 if event.verified else 0,
                        response_time_ms=None,
                        status_code=200 if event.verified else 400,
                        metadata={
                            "page_url": _sanitize_string(event.pageUrl),
                            "page_domain": _sanitize_string(event.pageDomain),
                            "page_title": _sanitize_string(event.pageTitle),
                            "signer_id": _sanitize_string(event.signerId),
                            "signer_name": _sanitize_string(event.signerName),
                            "organization_id": _sanitize_string(event.organizationId),
                            "document_id": _sanitize_string(event.documentId),
                            "original_domain": _sanitize_string(event.originalDomain),
                            "verified": event.verified,
                            "verification_status": _sanitize_string(event.verificationStatus),
                            "marker_type": _sanitize_string(event.markerType),
                            "domain_mismatch": event.domainMismatch,
                            "mismatch_reason": _sanitize_string(event.mismatchReason),
                            "discovery_source": _sanitize_string(event.discoverySource),
                            "content_length_bucket": _sanitize_string(event.contentLengthBucket),
                            "embedding_byte_length": event.embeddingByteLength,
                            "extension_version": _sanitize_string(event.extensionVersion or batch.version),
                            "session_id": _sanitize_string(event.sessionId),
                            "source": _sanitize_string(batch.source),
                        },
                    ),
                    organization_id=metric_org_id,
                )
            except Exception as exc:
                logger.warning("Legacy metric recording failed for discovery event: %s", exc)

        return DiscoveryResponse(
            success=True, data={"events_recorded": events_recorded, "message": "Discovery events recorded successfully"}, error=None
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "DISCOVERY_RECORD_ERROR",
                "detail": "Failed to process discovery events",
                "next_action": "Retry the request. Check GET /health for service status.",
            },
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
        base_query = base_query.filter(UsageMetric.meta["organization_id"].astext == identity)

    # Get total counts
    total_discoveries = base_query.count()
    verified_count = base_query.filter(UsageMetric.meta["verified"].astext == "true").count()
    invalid_count = total_discoveries - verified_count

    # Get unique domains
    unique_domains = base_query.with_entities(func.count(distinct(UsageMetric.endpoint))).scalar() or 0

    # Get unique signers
    unique_signers = (
        base_query.filter(UsageMetric.meta["signer_id"].astext.isnot(None))
        .with_entities(func.count(distinct(UsageMetric.meta["signer_id"].astext)))
        .scalar()
        or 0
    )

    # Get top domains
    top_domains_query = (
        base_query.with_entities(UsageMetric.endpoint, func.count(UsageMetric.id).label("count"))
        .group_by(UsageMetric.endpoint)
        .order_by(func.count(UsageMetric.id).desc())
        .limit(10)
        .all()
    )

    top_domains = [{"domain": d[0], "count": d[1]} for d in top_domains_query if d[0]]

    # Get top signers
    top_signers_query = (
        base_query.filter(UsageMetric.meta["signer_id"].astext.isnot(None))
        .with_entities(
            UsageMetric.meta["signer_id"].astext.label("signer_id"),
            UsageMetric.meta["signer_name"].astext.label("signer_name"),
            func.count(UsageMetric.id).label("count"),
        )
        .group_by(UsageMetric.meta["signer_id"].astext, UsageMetric.meta["signer_name"].astext)
        .order_by(func.count(UsageMetric.id).desc())
        .limit(10)
        .all()
    )

    top_signers = [{"signer_id": s[0], "signer_name": s[1], "count": s[2]} for s in top_signers_query if s[0]]

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
            detail={
                "code": "ORG_ID_REQUIRED",
                "detail": "Organization ID required",
                "next_action": "Ensure your JWT token includes an organization_id claim.",
            },
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
            detail={
                "code": "ORG_ID_REQUIRED",
                "detail": "Organization ID required",
                "next_action": "Ensure your JWT token includes an organization_id claim.",
            },
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
            detail={
                "code": "DOMAIN_CONFLICT",
                "detail": str(exc),
                "next_action": "Use GET /api/v1/analytics/discovery/owned-domains to list existing patterns.",
            },
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
            detail={
                "code": "ORG_ID_REQUIRED",
                "detail": "Organization ID required",
                "next_action": "Ensure your JWT token includes an organization_id claim.",
            },
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
            detail={
                "code": "DOMAIN_NOT_FOUND",
                "detail": "Owned domain not found",
                "next_action": "Use GET /api/v1/analytics/discovery/owned-domains to retrieve valid domain IDs.",
            },
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
            detail={
                "code": "ORG_ID_REQUIRED",
                "detail": "Organization ID required",
                "next_action": "Ensure your JWT token includes an organization_id claim.",
            },
        )

    deleted = DiscoveryService.delete_owned_domain(db, domain_id=domain_id, organization_id=org_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "DOMAIN_NOT_FOUND",
                "detail": "Owned domain not found",
                "next_action": "Use GET /api/v1/analytics/discovery/owned-domains to retrieve valid domain IDs.",
            },
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
            detail={
                "code": "ADMIN_REQUIRED",
                "detail": "Admin access required",
                "next_action": "This endpoint is restricted to admin users. Contact your administrator.",
            },
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
            detail={
                "code": "ACCESS_DENIED",
                "detail": "Access denied",
                "next_action": "You can only view your own activity. Admins can view any user's activity.",
            },
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
    metrics = query.order_by(UsageMetric.created_at.desc()).offset(offset).limit(limit).all()

    # Transform to activity items
    activities = []
    for m in metrics:
        method = None
        if isinstance(m.meta, dict):
            method = m.meta.get("method")
        activities.append(
            {
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
            }
        )

    return UserActivityResponse(
        activities=activities,
        total=total,
        limit=limit,
        offset=offset,
        has_more=(offset + limit) < total,
    )
