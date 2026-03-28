"""Incident fingerprinting, deduplication, and lifecycle management."""

import hashlib
import logging
import re
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from ..core.config import settings
from ..db.models import AlertEvent, Incident

logger = logging.getLogger(__name__)

# Path parameter patterns to normalize for fingerprinting
_PATH_PARAM_PATTERNS = [
    (re.compile(r"/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"), "/{uuid}"),
    (re.compile(r"/[0-9a-f]{24,64}"), "/{id}"),
    (re.compile(r"/\d+"), "/{n}"),
]

# Severity classification
_CRITICAL_CODES = {"E_INTERNAL", "E_SERVICE_UNAVAILABLE", "E_UNHANDLED"}
_WARNING_CODES = {"E_RATE_LIMIT", "E_RATE_SIGN", "E_RATE_VERIFY", "E_QUOTA_EXCEEDED"}


def normalize_endpoint(path: str) -> str:
    """Normalize path parameters for fingerprinting."""
    if not path:
        return ""
    for pattern, replacement in _PATH_PARAM_PATTERNS:
        path = pattern.sub(replacement, path)
    return path


def compute_fingerprint(service_name: str, endpoint: str, error_code: str, status_code: Optional[int] = None) -> str:
    """Compute a stable fingerprint for deduplication."""
    normalized = normalize_endpoint(endpoint or "")
    key = f"{service_name or 'unknown'}:{normalized}:{error_code or ''}:{status_code or ''}"
    return hashlib.sha256(key.encode()).hexdigest()[:32]


def classify_severity(error_code: str, status_code: Optional[int] = None) -> str:
    if error_code in _CRITICAL_CODES:
        return "critical"
    if status_code and status_code >= 500:
        return "critical"
    if error_code in _WARNING_CODES:
        return "warning"
    if status_code and status_code >= 400:
        return "warning"
    return "info"


def ingest_error_event(
    db: Session,
    source: str,
    service_name: str,
    endpoint: str,
    error_code: str,
    error_message: str,
    status_code: Optional[int] = None,
    organization_id: Optional[str] = None,
    user_id: Optional[str] = None,
    request_id: Optional[str] = None,
    stack_trace: Optional[str] = None,
    raw_payload: Optional[dict] = None,
) -> tuple[Incident, bool]:
    """Ingest an error event, creating or updating an incident.

    Returns (incident, is_new) where is_new indicates a new incident was created.
    """
    fingerprint = compute_fingerprint(service_name, endpoint, error_code, status_code)
    severity = classify_severity(error_code, status_code)
    now = datetime.utcnow()

    # Look for an existing open incident with the same fingerprint
    resolve_cutoff = now - timedelta(minutes=settings.AUTO_RESOLVE_AFTER_MINUTES)
    existing = (
        db.query(Incident)
        .filter(
            Incident.fingerprint == fingerprint,
            Incident.status.in_(["open", "acknowledged"]),
            Incident.last_seen_at >= resolve_cutoff,
        )
        .first()
    )

    is_new = existing is None

    if existing:
        existing.occurrence_count += 1
        existing.last_seen_at = now
        existing.sample_error = (error_message or "")[:2000]
        if stack_trace:
            existing.sample_stack = stack_trace[:5000]
        if request_id:
            existing.sample_request_id = request_id
        if organization_id:
            existing.sample_organization_id = organization_id
        # Escalate severity if needed
        if _severity_rank(severity) > _severity_rank(existing.severity):
            existing.severity = severity
        incident = existing
    else:
        normalized = normalize_endpoint(endpoint or "")
        title = f"[{severity.upper()}] {service_name}: {error_code or f'HTTP {status_code}'} on {normalized or 'unknown'}"
        incident = Incident(
            fingerprint=fingerprint,
            status="open",
            severity=severity,
            title=title[:500],
            service_name=service_name,
            endpoint=endpoint,
            error_code=error_code,
            first_seen_at=now,
            last_seen_at=now,
            occurrence_count=1,
            sample_error=(error_message or "")[:2000],
            sample_stack=(stack_trace or "")[:5000] if stack_trace else None,
            sample_request_id=request_id,
            sample_organization_id=organization_id,
        )
        db.add(incident)
        db.flush()

    # Store the raw event
    event = AlertEvent(
        incident_id=incident.id,
        source=source,
        raw_payload=raw_payload or {},
        status_code=status_code,
        endpoint=endpoint,
        error_code=error_code,
        error_message=(error_message or "")[:2000],
        service_name=service_name,
        organization_id=organization_id,
        user_id=user_id,
        request_id=request_id,
    )
    db.add(event)
    db.commit()

    return incident, is_new


def auto_resolve_stale_incidents(db: Session) -> int:
    """Resolve incidents that haven't recurred within the auto-resolve window."""
    cutoff = datetime.utcnow() - timedelta(minutes=settings.AUTO_RESOLVE_AFTER_MINUTES)
    now = datetime.utcnow()
    count = (
        db.query(Incident)
        .filter(
            Incident.status == "open",
            Incident.last_seen_at < cutoff,
        )
        .update({"status": "resolved", "resolved_at": now})
    )
    db.commit()
    if count:
        logger.info("Auto-resolved %d stale incidents", count)
    return count


def get_summary(db: Session) -> dict:
    """Build a structured summary of current system health."""
    open_incidents = db.query(Incident).filter(Incident.status == "open").all()
    acknowledged = db.query(Incident).filter(Incident.status == "acknowledged").all()

    # Error rate: events in last 5 minutes vs previous 5 minutes
    now = datetime.utcnow()
    recent_window = now - timedelta(minutes=5)
    prev_window = now - timedelta(minutes=10)
    recent_count = db.query(func.count(AlertEvent.id)).filter(AlertEvent.created_at >= recent_window).scalar() or 0
    prev_count = db.query(func.count(AlertEvent.id)).filter(AlertEvent.created_at >= prev_window, AlertEvent.created_at < recent_window).scalar() or 0

    # New error types in last hour
    one_hour_ago = now - timedelta(hours=1)
    new_types = db.query(Incident).filter(Incident.first_seen_at >= one_hour_ago, Incident.status == "open").count()

    # Top services by open incidents
    top_services = (
        db.query(Incident.service_name, func.count(Incident.id).label("count"))
        .filter(Incident.status.in_(["open", "acknowledged"]))
        .group_by(Incident.service_name)
        .order_by(desc("count"))
        .limit(5)
        .all()
    )

    # Top errors by occurrence
    top_errors = db.query(Incident).filter(Incident.status.in_(["open", "acknowledged"])).order_by(desc(Incident.occurrence_count)).limit(10).all()

    return {
        "status": "critical" if any(i.severity == "critical" for i in open_incidents) else ("warning" if open_incidents else "healthy"),
        "open_count": len(open_incidents),
        "acknowledged_count": len(acknowledged),
        "critical_count": sum(1 for i in open_incidents if i.severity == "critical"),
        "warning_count": sum(1 for i in open_incidents if i.severity == "warning"),
        "error_rate_last_5m": recent_count,
        "error_rate_prev_5m": prev_count,
        "error_rate_trend": "rising" if recent_count > prev_count * 1.5 else ("falling" if recent_count < prev_count * 0.5 else "stable"),
        "new_error_types_last_hour": new_types,
        "top_services": [{"service": s, "count": c} for s, c in top_services],
        "top_errors": [
            {
                "id": i.id,
                "title": i.title,
                "service": i.service_name,
                "error_code": i.error_code,
                "occurrences": i.occurrence_count,
                "first_seen": i.first_seen_at.isoformat() if i.first_seen_at else None,
                "last_seen": i.last_seen_at.isoformat() if i.last_seen_at else None,
                "sample_error": i.sample_error[:200] if i.sample_error else None,
            }
            for i in top_errors
        ],
        "checked_at": now.isoformat(),
    }


def get_patterns(db: Session) -> dict:
    """Analyze error patterns for recurring issues."""
    now = datetime.utcnow()
    one_day_ago = now - timedelta(days=1)

    # Recurring errors (most occurrences in last 24h)
    recurring = db.query(Incident).filter(Incident.last_seen_at >= one_day_ago).order_by(desc(Incident.occurrence_count)).limit(20).all()

    # Service error rates (events per service in last hour)
    one_hour_ago = now - timedelta(hours=1)
    service_rates = (
        db.query(AlertEvent.service_name, func.count(AlertEvent.id).label("count"))
        .filter(AlertEvent.created_at >= one_hour_ago)
        .group_by(AlertEvent.service_name)
        .order_by(desc("count"))
        .all()
    )

    return {
        "recurring_errors": [
            {
                "id": i.id,
                "fingerprint": i.fingerprint,
                "title": i.title,
                "service": i.service_name,
                "endpoint": i.endpoint,
                "error_code": i.error_code,
                "occurrences": i.occurrence_count,
                "status": i.status,
                "first_seen": i.first_seen_at.isoformat() if i.first_seen_at else None,
                "last_seen": i.last_seen_at.isoformat() if i.last_seen_at else None,
            }
            for i in recurring
        ],
        "services_by_error_rate": [{"service": s, "errors_last_hour": c} for s, c in service_rates],
        "checked_at": now.isoformat(),
    }


def _severity_rank(severity: str) -> int:
    return {"info": 0, "warning": 1, "critical": 2}.get(severity, 0)
