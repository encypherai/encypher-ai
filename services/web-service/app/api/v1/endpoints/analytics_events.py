"""
Marketing analytics event tracking endpoints.
"""

from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, Query, Request
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps

router = APIRouter(description="Track and retrieve marketing analytics events.")


@router.post("/", response_model=schemas.AnalyticsEventResponse)
def track_event(
    *,
    db: Session = Depends(deps.get_db),
    event_in: schemas.AnalyticsEventCreate,
    request: Request,
    background_tasks: BackgroundTasks,
) -> Any:
    """Track a new analytics event."""
    client_host = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    event = crud.analytics_event.create_with_metadata(db=db, obj_in=event_in, ip_address=client_host, user_agent=user_agent)

    return schemas.AnalyticsEventResponse(success=True, event_id=event.event_id)


@router.get("/session/{session_id}", response_model=list[schemas.AnalyticsEventInDB])
def read_session_events(
    session_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(deps.get_db),
) -> Any:
    """Get all events for a specific session (up to 500)."""
    events = crud.analytics_event.get_events_by_session(db=db, session_id=session_id, limit=limit)
    return events
