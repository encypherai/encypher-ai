"""
Admin endpoints for managing demo requests.

All read/write endpoints require a valid X-Internal-Token header.
"""

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
from app.services.email import send_demo_confirmation, send_demo_notification

router = APIRouter(description="CRUD endpoints for demo request records. Admin/internal use only.")


def _require_internal_token(internal_token: str | None) -> None:
    """Raise 401 if the request lacks a valid internal service token."""
    if not settings.INTERNAL_SERVICE_TOKEN:
        return
    if not internal_token or internal_token != settings.INTERNAL_SERVICE_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized. Supply a valid X-Internal-Token header to access this endpoint.",
        )


@router.post("/", response_model=schemas.DemoRequest)
def create_demo_request(
    *,
    db: Session = Depends(deps.get_db),
    demo_request_in: schemas.DemoRequestCreate,
    background_tasks: BackgroundTasks,
) -> models.DemoRequest:
    """Create a new demo request."""
    demo_request = crud.demo_request.create(db, obj_in=demo_request_in)

    background_tasks.add_task(send_demo_notification, demo_request, "general")
    background_tasks.add_task(send_demo_confirmation, demo_request.email, demo_request.name, "general")

    return demo_request


@router.get("/{request_id}", response_model=schemas.DemoRequest)
def read_demo_request(
    request_id: int,
    db: Session = Depends(deps.get_db),
    internal_token: str | None = Header(None, alias="X-Internal-Token"),
) -> models.DemoRequest:
    """Get a specific demo request by ID. Admin only."""
    _require_internal_token(internal_token)

    demo_request = crud.demo_request.get(db, id=request_id)
    if not demo_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demo request not found. Check that the ID is correct.",
        )
    return demo_request


@router.get("/")
def read_demo_requests(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    internal_token: str | None = Header(None, alias="X-Internal-Token"),
) -> dict:
    """List demo requests with pagination. Admin only."""
    _require_internal_token(internal_token)

    total = db.query(crud.demo_request.model).count()
    demo_requests = crud.demo_request.get_multi(db, skip=skip, limit=limit)

    return {
        "items": [schemas.DemoRequest.model_validate(dr) for dr in demo_requests],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.put("/{request_id}", response_model=schemas.DemoRequest)
def update_demo_request(
    *,
    db: Session = Depends(deps.get_db),
    request_id: int,
    demo_request_in: schemas.DemoRequestUpdate,
    internal_token: str | None = Header(None, alias="X-Internal-Token"),
) -> models.DemoRequest:
    """Update a demo request. Admin only."""
    _require_internal_token(internal_token)

    demo_request = crud.demo_request.get(db, id=request_id)
    if not demo_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demo request not found. Check that the ID is correct.",
        )

    demo_request = crud.demo_request.update(db, db_obj=demo_request, obj_in=demo_request_in)
    return demo_request
