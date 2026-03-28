"""Alert service API endpoints."""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import desc
from sqlalchemy.orm import Session

from ...db.models import AlertEvent, Incident
from ...db.session import get_db
from ...services import cc_trigger, discord_notifier, incident_service

logger = logging.getLogger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class DirectEventRequest(BaseModel):
    service_name: str
    endpoint: str = ""
    error_code: str
    error_message: str = ""
    severity: str = "warning"
    status_code: Optional[int] = None
    organization_id: Optional[str] = None
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    stack_trace: Optional[str] = None
    metadata: Optional[dict] = None


class AlertmanagerAlert(BaseModel):
    status: str = "firing"
    labels: dict = Field(default_factory=dict)
    annotations: dict = Field(default_factory=dict)
    startsAt: Optional[str] = None
    endsAt: Optional[str] = None
    generatorURL: Optional[str] = None
    fingerprint: Optional[str] = None


class AlertmanagerPayload(BaseModel):
    version: str = "4"
    status: str = "firing"
    receiver: str = ""
    alerts: list[AlertmanagerAlert] = Field(default_factory=list)


class IncidentResponse(BaseModel):
    id: str
    fingerprint: str
    status: str
    severity: str
    title: str
    service_name: Optional[str]
    endpoint: Optional[str]
    error_code: Optional[str]
    first_seen_at: Optional[str]
    last_seen_at: Optional[str]
    occurrence_count: int
    sample_error: Optional[str]
    sample_request_id: Optional[str]
    sample_organization_id: Optional[str]


class InvestigationUpdateRequest(BaseModel):
    message: str


# ---------------------------------------------------------------------------
# Summary + Patterns (AI-optimized)
# ---------------------------------------------------------------------------


@router.get("/summary")
async def get_summary(db: Session = Depends(get_db)):
    """Current system health summary. Designed for AI assistant consumption."""
    return incident_service.get_summary(db)


@router.get("/patterns")
async def get_patterns(db: Session = Depends(get_db)):
    """Error pattern analysis: recurring errors, service error rates."""
    return incident_service.get_patterns(db)


# ---------------------------------------------------------------------------
# Incidents CRUD
# ---------------------------------------------------------------------------


@router.get("/incidents")
async def list_incidents(
    status_filter: Optional[str] = Query(None, alias="status"),
    severity: Optional[str] = None,
    service: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """List incidents with optional filters."""
    q = db.query(Incident)
    if status_filter:
        q = q.filter(Incident.status == status_filter)
    if severity:
        q = q.filter(Incident.severity == severity)
    if service:
        q = q.filter(Incident.service_name == service)
    total = q.count()
    incidents = q.order_by(desc(Incident.last_seen_at)).offset(offset).limit(limit).all()
    return {
        "total": total,
        "incidents": [_incident_to_dict(i) for i in incidents],
    }


@router.get("/incidents/{incident_id}")
async def get_incident(incident_id: str, db: Session = Depends(get_db)):
    """Get incident detail with recent events."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    recent_events = db.query(AlertEvent).filter(AlertEvent.incident_id == incident_id).order_by(desc(AlertEvent.created_at)).limit(20).all()

    result = _incident_to_dict(incident)
    result["sample_stack"] = incident.sample_stack
    result["events"] = [
        {
            "id": e.id,
            "source": e.source,
            "status_code": e.status_code,
            "endpoint": e.endpoint,
            "error_code": e.error_code,
            "error_message": e.error_message,
            "service_name": e.service_name,
            "organization_id": e.organization_id,
            "request_id": e.request_id,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in recent_events
    ]
    return result


@router.post("/incidents/{incident_id}/ack")
async def acknowledge_incident(incident_id: str, db: Session = Depends(get_db)):
    """Acknowledge an incident."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident.status = "acknowledged"
    db.commit()
    return {"status": "acknowledged", "incident_id": incident_id}


@router.post("/incidents/{incident_id}/resolve")
async def resolve_incident(incident_id: str, db: Session = Depends(get_db)):
    """Manually resolve an incident."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident.status = "resolved"
    incident.resolved_at = datetime.utcnow()
    db.commit()
    return {"status": "resolved", "incident_id": incident_id}


@router.post("/incidents/{incident_id}/investigate")
async def post_investigation_update(incident_id: str, body: InvestigationUpdateRequest, db: Session = Depends(get_db)):
    """Post an investigation update to Discord for this incident."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    result = await discord_notifier.notify_investigation_update(incident_id, body.message, db)
    return {"status": result or "skipped", "incident_id": incident_id}


# ---------------------------------------------------------------------------
# Ingestion endpoints
# ---------------------------------------------------------------------------


@router.post("/alertmanager", status_code=status.HTTP_200_OK)
async def receive_alertmanager(payload: AlertmanagerPayload, db: Session = Depends(get_db)):
    """Receive alerts from Prometheus Alertmanager."""
    processed = 0
    for alert in payload.alerts:
        if alert.status != "firing":
            continue

        alert_name = alert.labels.get("alertname", "UnknownAlert")
        severity = alert.labels.get("severity", "warning")
        summary = alert.annotations.get("summary", alert_name)
        description = alert.annotations.get("description", "")
        service = alert.labels.get("job", "unknown")

        incident, is_new = incident_service.ingest_error_event(
            db=db,
            source="alertmanager",
            service_name=service,
            endpoint="",
            error_code=alert_name,
            error_message=summary,
            raw_payload={"alert": alert.model_dump(), "receiver": payload.receiver},
        )

        if is_new:
            await discord_notifier.notify_alertmanager(alert_name, severity, summary, description, alert.labels, db)
            await cc_trigger.trigger_if_critical(incident)

        processed += 1

    return {"processed": processed}


@router.post("/events", status_code=status.HTTP_201_CREATED)
async def receive_direct_event(event: DirectEventRequest, db: Session = Depends(get_db)):
    """Receive a direct error/event push from a service."""
    incident, is_new = incident_service.ingest_error_event(
        db=db,
        source="direct_push",
        service_name=event.service_name,
        endpoint=event.endpoint,
        error_code=event.error_code,
        error_message=event.error_message,
        status_code=event.status_code,
        organization_id=event.organization_id,
        user_id=event.user_id,
        request_id=event.request_id,
        stack_trace=event.stack_trace,
        raw_payload=event.metadata,
    )

    if is_new:
        await discord_notifier.notify_new_incident(incident, db)
        await cc_trigger.trigger_if_critical(incident)

    return {
        "incident_id": incident.id,
        "is_new": is_new,
        "status": incident.status,
        "occurrence_count": incident.occurrence_count,
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _incident_to_dict(i: Incident) -> dict:
    return {
        "id": i.id,
        "fingerprint": i.fingerprint,
        "status": i.status,
        "severity": i.severity,
        "title": i.title,
        "service_name": i.service_name,
        "endpoint": i.endpoint,
        "error_code": i.error_code,
        "first_seen_at": i.first_seen_at.isoformat() if i.first_seen_at else None,
        "last_seen_at": i.last_seen_at.isoformat() if i.last_seen_at else None,
        "occurrence_count": i.occurrence_count,
        "sample_error": i.sample_error,
        "sample_request_id": i.sample_request_id,
        "sample_organization_id": i.sample_organization_id,
    }
