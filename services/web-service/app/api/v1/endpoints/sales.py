"""
API endpoints for Sales Contact forms.
Handles enterprise and general sales inquiries.
"""

import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api import deps
from app.api.utils import create_demo_record, send_emails_background
from app.schemas.demo_request import DemoRequestCreate

logger = logging.getLogger(__name__)
router = APIRouter()


async def _create_sales_contact(
    contact_request: DemoRequestCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session,
    context: str,
) -> dict:
    """Internal helper to handle sales contact creation for a given context."""
    try:
        db_request = create_demo_record(db, request, contact_request, default_source=f"sales-{context}")
        background_tasks.add_task(send_emails_background, db_request, context)
        logger.info(f"Sales contact request created: {db_request.uuid} (context: {context})")

        return {
            "success": True,
            "id": str(db_request.uuid),
            "message": "Contact request received successfully. We'll be in touch within 24 hours.",
        }

    except Exception as e:
        logger.error(f"Error creating sales contact ({context}): {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to submit contact request") from e


@router.post("/enterprise-requests")
async def create_enterprise_contact(
    contact_request: DemoRequestCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(deps.get_db),
) -> dict:
    """Create a new enterprise sales contact request."""
    return await _create_sales_contact(contact_request, background_tasks, request, db, "enterprise")


@router.post("/general-requests")
async def create_general_contact(
    contact_request: DemoRequestCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(deps.get_db),
) -> dict:
    """Create a new general sales contact request."""
    return await _create_sales_contact(contact_request, background_tasks, request, db, "general")
