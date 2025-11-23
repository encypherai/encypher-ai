from typing import Any, List
from fastapi import APIRouter, Depends, Request, BackgroundTasks
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps

router = APIRouter()

@router.post("/", response_model=schemas.AnalyticsEventResponse)
def track_event(
    *,
    db: Session = Depends(deps.get_db),
    event_in: schemas.AnalyticsEventCreate,
    request: Request,
    background_tasks: BackgroundTasks,
) -> Any:
    """
    Track a new analytics event.
    """
    # Extract metadata from request if not provided in payload
    client_host = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    # Create event
    event = crud.analytics_event.create_with_metadata(
        db=db,
        obj_in=event_in,
        ip_address=client_host,
        user_agent=user_agent
    )
    
    return event

@router.get("/session/{session_id}", response_model=List[schemas.AnalyticsEventInDB])
def read_session_events(
    session_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    # current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get all events for a specific session.
    """
    events = crud.analytics_event.get_events_by_session(
        db=db, session_id=session_id, limit=limit
    )
    return events
