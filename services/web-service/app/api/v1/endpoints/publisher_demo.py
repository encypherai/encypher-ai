"""
API endpoints for Publisher Demo feature.
Handles demo requests and analytics events from the publisher-demo page.
"""

import logging
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.api import deps
from app.api.utils import create_demo_record, get_client_ip, hash_ip, send_emails_background
from app.core.config import settings
from app.models.analytics_event import AnalyticsEvent
from app.models.demo_request import DemoRequest
from app.schemas.analytics_event import AnalyticsEventCreate, AnalyticsEventResponse
from app.schemas.demo_request import DemoRequestCreate

logger = logging.getLogger(__name__)
router = APIRouter(description="Demo requests and analytics for the Publisher Demo landing page.")

_SOURCE = "publisher-demo"


def _require_internal_token(internal_token: str | None) -> None:
    """Raise 401 if the request lacks a valid internal service token."""
    if not settings.INTERNAL_SERVICE_TOKEN:
        return
    if not internal_token or internal_token != settings.INTERNAL_SERVICE_TOKEN:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized. Supply a valid X-Internal-Token header.",
        )


@router.post("/demo-requests")
async def create_demo_request(
    request: Request,
    demo_request_in: DemoRequestCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
) -> dict:
    """Create a new demo request from the publisher-demo page."""
    try:
        db_demo_request = create_demo_record(db, request, demo_request_in, default_source=_SOURCE)
        logger.info(f"Publisher Demo request created: {db_demo_request.uuid} from {demo_request_in.email} at {demo_request_in.organization}")
        background_tasks.add_task(send_emails_background, db_demo_request, _SOURCE)

        return {
            "success": True,
            "id": str(db_demo_request.uuid),
            "message": "Demo request received successfully. We'll contact you within 24 hours.",
        }

    except Exception as e:
        logger.error(f"Error creating publisher demo request: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to submit demo request. Please contact demo@encypher.com if the problem persists.",
        ) from e


@router.post("/analytics/events", response_model=AnalyticsEventResponse)
async def track_analytics_event(
    request: Request,
    event: AnalyticsEventCreate,
    db: Session = Depends(deps.get_db),
) -> AnalyticsEventResponse:
    """Track an analytics event from the publisher-demo page."""
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
            "publisher_demo_loaded",
            "scroll_100_percent",
            "cta_button_clicked",
            "demo_form_submitted",
        ]:
            logger.info(f"Publisher Demo analytics: {event.event_name} (session: {event.session_id})")

        return AnalyticsEventResponse(success=True)

    except Exception as e:
        logger.error(f"Error tracking publisher demo analytics event: {e}")
        db.rollback()
        return AnalyticsEventResponse(success=False, message="Failed to track event")


@router.get("/demo-requests/{request_id}")
async def get_demo_request(
    request_id: UUID,
    db: Session = Depends(deps.get_db),
    internal_token: str | None = Header(None, alias="X-Internal-Token"),
) -> dict:
    """Get a publisher demo request by UUID. Requires X-Internal-Token header."""
    _require_internal_token(internal_token)

    demo_request = db.query(DemoRequest).filter(DemoRequest.uuid == request_id).first()

    if not demo_request:
        raise HTTPException(
            status_code=404,
            detail="Demo request not found. Verify the UUID and that the record originated from publisher-demo.",
        )

    return {
        "id": str(demo_request.uuid),
        "name": demo_request.name,
        "email": demo_request.email,
        "organization": demo_request.organization,
        "role": demo_request.role,
        "message": demo_request.message,
        "status": demo_request.status,
        "source": demo_request.source,
        "created_at": demo_request.created_at.isoformat(),
    }
