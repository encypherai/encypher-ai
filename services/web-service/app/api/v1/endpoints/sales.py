"""
API endpoints for Sales Contact forms.
Handles enterprise, general, AI, and publisher sales inquiries.
"""

import hashlib
import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api import deps
from app.models.demo_request import DemoRequest
from app.schemas.demo_request import DemoRequestCreate
from app.services.email import send_demo_confirmation, send_demo_notification

logger = logging.getLogger(__name__)
router = APIRouter()


def get_client_ip(request: Request) -> str | None:
    """Extract client IP address from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    if request.client:
        return request.client.host

    return None


def hash_ip(ip: str | None) -> str | None:
    """Hash IP address for privacy."""
    if not ip:
        return None
    return hashlib.sha256(ip.encode()).hexdigest()[:16]


def send_emails_background(demo_request: DemoRequest, context: str) -> None:
    """Background task to send notification and confirmation emails."""
    try:
        send_demo_notification(demo_request, context=context)
    except Exception as e:
        logger.error(f"Failed to send sales notification email: {e}")

    try:
        send_demo_confirmation(demo_request.email, demo_request.name, context=context)
    except Exception as e:
        logger.error(f"Failed to send sales confirmation email: {e}")


async def _create_sales_contact(
    contact_request: DemoRequestCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session,
    context: str,
) -> dict:
    """Internal function to handle sales contact creation."""
    try:
        # Get and hash IP
        client_ip = get_client_ip(request)
        hashed_ip = hash_ip(client_ip)
        user_agent = request.headers.get("User-Agent")
        referrer = request.headers.get("Referer")

        # Create database record (reusing DemoRequest model)
        db_request = DemoRequest(
            name=contact_request.name,
            email=contact_request.email,
            organization=contact_request.organization,
            role=contact_request.role,
            message=contact_request.message,
            consent=contact_request.consent,
            source=contact_request.source or f"sales-{context}",
            ip_address=hashed_ip,
            user_agent=user_agent,
            referrer=referrer,
        )

        db.add(db_request)
        db.commit()
        db.refresh(db_request)

        # Send emails in background
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
