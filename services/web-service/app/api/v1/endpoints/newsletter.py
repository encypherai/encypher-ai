import logging
import secrets

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api import deps
from app.core.config import settings
from app.models.newsletter_subscriber import NewsletterSubscriber
from app.schemas.newsletter import (
    NewsletterBroadcastRequest,
    NewsletterSubscribeRequest,
    NewsletterUnsubscribeRequest,
)
from app.services.email import send_newsletter_broadcast, send_newsletter_welcome

logger = logging.getLogger(__name__)

router = APIRouter()


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
