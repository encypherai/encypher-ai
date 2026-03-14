"""
Shared API utilities for the web-service.

Functions here are used across multiple endpoint modules to avoid duplication.
"""

import hashlib
import logging

from fastapi import Request
from sqlalchemy.orm import Session

from app.models.demo_request import DemoRequest
from app.schemas.demo_request import DemoRequestCreate
from app.services.email import send_demo_confirmation, send_demo_notification

logger = logging.getLogger(__name__)


def get_client_ip(request: Request) -> str | None:
    """Extract client IP address from request headers or socket."""
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
    """Hash IP address for privacy (truncated SHA-256, hex, 16 chars)."""
    if not ip:
        return None
    return hashlib.sha256(ip.encode()).hexdigest()[:16]


def send_emails_background(demo_request: DemoRequest, context: str) -> None:
    """Background task to send notification and confirmation emails.

    Args:
        demo_request: The saved DemoRequest ORM instance.
        context: String label identifying the originating source (e.g. 'ai-demo').
    """
    try:
        send_demo_notification(demo_request, context=context)
    except Exception as e:
        logger.error(f"Failed to send notification email: {e}")

    try:
        send_demo_confirmation(demo_request.email, demo_request.name, context=context)
    except Exception as e:
        logger.error(f"Failed to send confirmation email: {e}")


def create_demo_record(
    db: Session,
    request: Request,
    demo_request_in: DemoRequestCreate,
    default_source: str,
) -> DemoRequest:
    """Create and persist a DemoRequest record with request metadata.

    Args:
        db: SQLAlchemy session.
        request: The incoming FastAPI Request (used for IP, UA, referrer).
        demo_request_in: Validated input schema.
        default_source: Source label used when none is supplied in the payload.

    Returns:
        The committed and refreshed DemoRequest ORM instance.
    """
    user_agent = request.headers.get("User-Agent")
    ip_address = hash_ip(get_client_ip(request))
    referrer = request.headers.get("Referer")

    db_demo_request = DemoRequest(
        name=demo_request_in.name,
        email=demo_request_in.email,
        organization=demo_request_in.organization,
        role=demo_request_in.role,
        message=demo_request_in.message,
        consent=demo_request_in.consent,
        source=demo_request_in.source or default_source,
        user_agent=user_agent,
        ip_address=ip_address,
        referrer=referrer,
    )

    db.add(db_demo_request)
    db.commit()
    db.refresh(db_demo_request)
    return db_demo_request
