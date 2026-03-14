"""
API endpoints for AI Demo feature.
Handles demo requests and analytics events from the ai-demo page.
"""

import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api import deps
from app.api.utils import create_demo_record, get_client_ip, hash_ip, send_emails_background
from app.models.analytics_event import AnalyticsEvent
from app.schemas.analytics_event import AnalyticsEventCreate, AnalyticsEventResponse
from app.schemas.demo_request import DemoRequestCreate

logger = logging.getLogger(__name__)
router = APIRouter()

_SOURCE = "ai-demo"


@router.post("/demo-requests")
async def create_demo_request(
    request: Request,
    demo_request_in: DemoRequestCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
) -> dict:
    """Create a new demo request from the ai-demo page."""
    try:
        db_demo_request = create_demo_record(db, request, demo_request_in, default_source=_SOURCE)
        logger.info(f"AI Demo request created: {db_demo_request.uuid} from {demo_request_in.email}")
        background_tasks.add_task(send_emails_background, db_demo_request, _SOURCE)

        return {
            "success": True,
            "id": str(db_demo_request.uuid),
            "message": "Demo request received successfully. We'll contact you within 24 hours.",
        }

    except Exception as e:
        logger.error(f"Error creating AI demo request: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to create demo request. Please contact demo@encypher.com if the problem persists.",
        ) from e


@router.post("/analytics/events", response_model=AnalyticsEventResponse)
async def track_analytics_event(
    request: Request,
    event: AnalyticsEventCreate,
    db: Session = Depends(deps.get_db),
) -> AnalyticsEventResponse:
    """Track an analytics event from the ai-demo page."""
    try:
        user_agent = request.headers.get("User-Agent")
        ip_address = hash_ip(get_client_ip(request))
        referrer = request.headers.get("Referer")

        url = None
        if event.properties:
            url = event.properties.get("url") or event.properties.get("page_url")

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
        return AnalyticsEventResponse(success=False, message="Failed to track event")
