import logging
import secrets
from math import ceil

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.api import deps
from app.core.config import settings
from app.models.newsletter_subscriber import NewsletterSubscriber
from app.schemas.newsletter import (
    NewsletterBroadcastRequest,
    NewsletterSubscribeRequest,
    NewsletterSubscriberStatusUpdateRequest,
    NewsletterUnsubscribeRequest,
)
from app.services.email import send_newsletter_broadcast, send_newsletter_welcome

logger = logging.getLogger(__name__)

router = APIRouter(description="Newsletter subscription, broadcast, and subscriber management endpoints.")


def _require_internal_token(internal_token: str | None) -> None:
    """Raise 401 if the request lacks a valid internal service token."""
    if not settings.INTERNAL_SERVICE_TOKEN:
        return
    if not internal_token or internal_token != settings.INTERNAL_SERVICE_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized. Supply a valid X-Internal-Token header to access this endpoint.",
        )


def _status_to_active(status_value: str) -> bool:
    return status_value == "active"


@router.post("/subscribe")
def subscribe(
    *,
    db: Session = Depends(deps.get_db),
    payload: NewsletterSubscribeRequest,
    request: Request,
    background_tasks: BackgroundTasks,
):
    """Subscribe an email to the newsletter."""
    existing = db.query(NewsletterSubscriber).filter(NewsletterSubscriber.email == payload.email).first()
    if existing:
        return {"success": True}

    subscriber = NewsletterSubscriber(
        email=payload.email,
        unsubscribe_token=secrets.token_urlsafe(32),
        source=payload.source,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    db.add(subscriber)
    db.commit()

    background_tasks.add_task(send_newsletter_welcome, payload.email)

    return {"success": True}


@router.post("/unsubscribe")
def unsubscribe(
    *,
    db: Session = Depends(deps.get_db),
    payload: NewsletterUnsubscribeRequest,
):
    """Unsubscribe from the newsletter using an unsubscribe token."""
    subscriber = db.query(NewsletterSubscriber).filter(NewsletterSubscriber.unsubscribe_token == payload.token).first()
    if subscriber:
        subscriber.active = False
        subscriber.status = "unsubscribed"
        subscriber.status_reason = None
        db.commit()

    return {"success": True}


@router.post("/broadcast")
def broadcast(
    *,
    db: Session = Depends(deps.get_db),
    payload: NewsletterBroadcastRequest,
    background_tasks: BackgroundTasks,
):
    """Broadcast a new blog post to all active newsletter subscribers."""
    if not payload.secret or payload.secret != settings.NEWSLETTER_BROADCAST_SECRET:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid broadcast secret",
        )

    subscribers = db.query(NewsletterSubscriber).filter(NewsletterSubscriber.active.is_(True)).all()

    for subscriber in subscribers:
        background_tasks.add_task(
            send_newsletter_broadcast,
            subscriber.email,
            subscriber.unsubscribe_token,
            payload.title,
            payload.excerpt,
            payload.post_url,
            payload.image_url,
        )

    return {"success": True, "recipient_count": len(subscribers)}


@router.post("/subscribers/{subscriber_id}/status")
def update_subscriber_status(
    subscriber_id: int,
    *,
    payload: NewsletterSubscriberStatusUpdateRequest,
    db: Session = Depends(deps.get_db),
    internal_token: str | None = Header(None, alias="X-Internal-Token"),
):
    _require_internal_token(internal_token)

    subscriber = db.query(NewsletterSubscriber).filter(NewsletterSubscriber.id == subscriber_id).first()
    if not subscriber:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscriber not found")

    subscriber.status = payload.status
    subscriber.status_reason = payload.reason
    subscriber.active = _status_to_active(payload.status)
    db.commit()

    return {
        "success": True,
        "data": {
            "id": subscriber.id,
            "email": subscriber.email,
            "active": subscriber.active,
            "status": subscriber.status,
            "status_reason": subscriber.status_reason,
        },
        "error": None,
    }


@router.delete("/subscribers/{subscriber_id}")
def delete_subscriber(
    subscriber_id: int,
    *,
    db: Session = Depends(deps.get_db),
    internal_token: str | None = Header(None, alias="X-Internal-Token"),
):
    _require_internal_token(internal_token)

    subscriber = db.query(NewsletterSubscriber).filter(NewsletterSubscriber.id == subscriber_id).first()
    if not subscriber:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscriber not found")

    db.delete(subscriber)
    db.commit()

    return {"success": True, "data": {"deleted": True, "id": subscriber_id}, "error": None}


@router.get("/subscribers")
def list_subscribers(
    *,
    db: Session = Depends(deps.get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    active_only: bool = Query(False),
    internal_token: str | None = Header(None, alias="X-Internal-Token"),
):
    """Internal-only listing endpoint for newsletter subscribers."""
    _require_internal_token(internal_token)

    query = db.query(NewsletterSubscriber)
    if active_only:
        query = query.filter(NewsletterSubscriber.active.is_(True))

    total = query.count()
    offset = (page - 1) * page_size
    rows = query.order_by(NewsletterSubscriber.subscribed_at.desc()).offset(offset).limit(page_size).all()

    return {
        "success": True,
        "data": {
            "subscribers": [
                {
                    "id": subscriber.id,
                    "email": subscriber.email,
                    "active": subscriber.active,
                    "status": subscriber.status,
                    "status_reason": subscriber.status_reason,
                    "source": subscriber.source,
                    "subscribed_at": subscriber.subscribed_at.isoformat() if subscriber.subscribed_at else None,
                }
                for subscriber in rows
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": ceil(total / page_size) if total else 0,
        },
        "error": None,
    }
