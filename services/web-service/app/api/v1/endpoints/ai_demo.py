"""
API endpoints for AI Demo feature.
Handles demo requests and analytics events from the ai-demo page.
"""

import hashlib
import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api import deps
from app.models.analytics_event import AnalyticsEvent
from app.models.demo_request import DemoRequest
from app.schemas.analytics_event import AnalyticsEventCreate, AnalyticsEventResponse
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


def send_emails_background(demo_request: DemoRequest) -> None:
    """Background task to send notification and confirmation emails."""
    try:
        send_demo_notification(demo_request, context="ai-demo")
    except Exception as e:
        logger.error(f"Failed to send notification email: {e}")

    try:
        send_demo_confirmation(demo_request.email, demo_request.name, context="ai-demo")
    except Exception as e:
        logger.error(f"Failed to send confirmation email: {e}")


@router.post("/demo-requests")
async def create_demo_request(
    request: Request,
    demo_request_in: DemoRequestCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Create a new demo request from the ai-demo page.
    """
    try:
        # Extract request metadata
        user_agent = request.headers.get("User-Agent")
        ip_address = hash_ip(get_client_ip(request))
        referrer = request.headers.get("Referer")

        # Create demo request record
        db_demo_request = DemoRequest(
            name=demo_request_in.name,
            email=demo_request_in.email,
            organization=demo_request_in.organization,
            role=demo_request_in.role,
            message=demo_request_in.message,
            consent=demo_request_in.consent,
            source=demo_request_in.source or "ai-demo",
            user_agent=user_agent,
            ip_address=ip_address,
            referrer=referrer,
        )

        db.add(db_demo_request)
        db.commit()
        db.refresh(db_demo_request)

        logger.info(f"AI Demo request created: {db_demo_request.uuid} from {demo_request_in.email}")

        # Send emails in background
        background_tasks.add_task(send_emails_background, db_demo_request)

        return {
            "success": True,
            "id": str(db_demo_request.uuid),
            "message": "Demo request received successfully. We'll contact you within 24 hours.",
        }

    except Exception as e:
        logger.error(f"Error creating AI demo request: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create demo request") from e


@router.post("/analytics/events", response_model=AnalyticsEventResponse)
async def track_analytics_event(
    request: Request,
    event: AnalyticsEventCreate,
    db: Session = Depends(deps.get_db),
) -> AnalyticsEventResponse:
    """
    Track an analytics event from the ai-demo page.
    """
    try:
        # Extract request metadata
        user_agent = request.headers.get("User-Agent")
        ip_address = hash_ip(get_client_ip(request))
        referrer = request.headers.get("Referer")

        # Get URL from properties if available
        url = None
        if event.properties:
            url = event.properties.get("url") or event.properties.get("page_url")

        # Create analytics event record
        db_event = AnalyticsEvent(
            session_id=event.session_id or "unknown",
            event_type=event.event_type or "custom",
            event_name=event.event_name,
            properties=event.properties or {},
            page_url=event.page_url or url,
            user_agent=user_agent,
            ip_address=ip_address,
            referrer=referrer,
        )

        db.add(db_event)
        db.commit()

        # Log significant events
        if event.event_name in [
            "ai_demo_loaded",
            "scroll_100_percent",
            "cta_clicked",
            "demo_form_submitted",
        ]:
            logger.info(f"AI Demo analytics: {event.event_name} (session: {event.session_id})")

        return AnalyticsEventResponse(success=True)

    except Exception as e:
        logger.error(f"Error tracking AI demo analytics event: {e}")
        db.rollback()
        # Don't raise exception for analytics - fail silently
        return AnalyticsEventResponse(success=False, message="Failed to track event")
