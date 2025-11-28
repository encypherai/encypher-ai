from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.services.email import send_demo_confirmation, send_demo_notification

router = APIRouter()


@router.post("/", response_model=schemas.DemoRequest)
def create_demo_request(
    *,
    db: Session = Depends(deps.get_db),
    demo_request_in: schemas.DemoRequestCreate,
    background_tasks: BackgroundTasks,
) -> models.DemoRequest:
    """
    Create a new demo request.
    """
    # Create the demo request
    demo_request = crud.demo_request.create(db, obj_in=demo_request_in)

    # Send email notifications
    background_tasks.add_task(send_demo_notification, demo_request, "general")
    background_tasks.add_task(
        send_demo_confirmation, demo_request.email, demo_request.name, "general"
    )

    return demo_request

@router.get("/{request_id}", response_model=schemas.DemoRequest)
def read_demo_request(
    request_id: int,
    db: Session = Depends(deps.get_db),
    # TODO: Restore auth when auth-service integration is ready
    # current_user: models.User = Depends(deps.get_current_active_superuser),
) -> models.DemoRequest:
    """
    Get a specific demo request by ID. Admin only.
    """
    demo_request = crud.demo_request.get(db, id=request_id)
    if not demo_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demo request not found",
        )
    return demo_request

@router.get("/", response_model=List[schemas.DemoRequest])
def read_demo_requests(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    # TODO: Restore auth when auth-service integration is ready
    # current_user: models.User = Depends(deps.get_current_active_superuser),
) -> List[models.DemoRequest]:
    """
    Retrieve demo requests. Admin only.
    """
    demo_requests = crud.demo_request.get_multi(db, skip=skip, limit=limit)
    return demo_requests

@router.put("/{request_id}", response_model=schemas.DemoRequest)
def update_demo_request(
    *,
    db: Session = Depends(deps.get_db),
    request_id: int,
    demo_request_in: schemas.DemoRequestUpdate,
    # TODO: Restore auth when auth-service integration is ready
    # current_user: models.User = Depends(deps.get_current_active_superuser),
) -> models.DemoRequest:
    """
    Update a demo request. Admin only.
    """
    demo_request = crud.demo_request.get(db, id=request_id)
    if not demo_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demo request not found",
        )

    demo_request = crud.demo_request.update(db, db_obj=demo_request, obj_in=demo_request_in)
    return demo_request
