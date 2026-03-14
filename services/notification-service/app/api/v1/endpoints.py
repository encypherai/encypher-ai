"""API endpoints for Notification Service v1"""

import time
from collections import defaultdict
from threading import Lock
from typing import List

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from ...core.config import settings
from ...db.session import get_db
from ...models.schemas import NotificationCreate, NotificationResponse
from ...services.notification_service import NotificationService

router = APIRouter()

# Reuse a single AsyncClient across requests for connection pooling.
_auth_client = httpx.AsyncClient()

# ---------------------------------------------------------------------------
# Task 1.4: Simple in-process sliding-window rate limiter for /send.
# Limit: RATE_LIMIT_SEND_PER_MINUTE requests per user_id per 60-second window.
# This is intentionally lightweight (no Redis dependency for the limiter itself).
# A Redis-backed implementation can replace this without changing the API.
# ---------------------------------------------------------------------------
_RATE_LIMIT_WINDOW = 60  # seconds
_RATE_LIMIT_MAX = 10  # max calls per user per window
_rate_limit_lock = Lock()
# Maps user_id -> list of timestamps (float) of recent send calls.
_rate_limit_store: dict = defaultdict(list)


def _check_rate_limit(user_id: str) -> None:
    """Raise HTTP 429 if the user has exceeded the send rate limit."""
    now = time.time()
    window_start = now - _RATE_LIMIT_WINDOW
    with _rate_limit_lock:
        timestamps = _rate_limit_store[user_id]
        # Evict old entries outside the current window
        timestamps = [t for t in timestamps if t >= window_start]
        if len(timestamps) >= _RATE_LIMIT_MAX:
            _rate_limit_store[user_id] = timestamps
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "rate_limit_exceeded",
                    "message": f"Maximum {_RATE_LIMIT_MAX} send requests per {_RATE_LIMIT_WINDOW}s window.",
                    "hint": "Wait before retrying. GET /api/v1/notifications/notifications to check existing notifications.",
                },
            )
        timestamps.append(now)
        _rate_limit_store[user_id] = timestamps


# ---------------------------------------------------------------------------


async def get_current_user(authorization: str = Header(...)) -> dict:
    """Verify user token with auth service"""
    try:
        response = await _auth_client.post(
            f"{settings.AUTH_SERVICE_URL}/api/v1/auth/verify",
            headers={"Authorization": authorization},
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "invalid_credentials",
                    "message": "Token verification failed.",
                    # Task 2.1: navigation hint
                    "hint": "Obtain a valid token from POST /api/v1/auth/login on the auth service.",
                },
            )
        return response.json()
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "auth_service_unavailable",
                "message": "Auth service could not be reached.",
                "hint": "Retry after a brief delay. If the problem persists contact support.",
            },
        ) from e


@router.post("/send", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def send_notification(
    notification_data: NotificationCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Send a notification

    The recipient must match the authenticated user's own email address.
    This prevents the endpoint from being used as an open relay.
    """
    t_start = time.time()

    # Task 1.4: rate limit before any work
    _check_rate_limit(current_user["id"])

    # Task 1.1: restrict recipient -- must equal the authenticated user's email.
    # Compare lowercase to be case-insensitive (email local-part is case-insensitive
    # in practice even though RFC 5321 technically allows case-sensitive local-parts).
    user_email: str = current_user.get("email", "")
    if notification_data.recipient.lower() != user_email.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "recipient_not_authorized",
                "message": "You may only send notifications to your own email address.",
                "hint": "Set recipient to your account email or omit it; the service will use your account email.",
            },
        )

    notification = NotificationService.create_notification(db, current_user["id"], notification_data)

    # Task 2.2: attach request-ID and wall-clock duration to the response
    request_id = getattr(request.state, "request_id", None)
    duration_ms = round((time.time() - t_start) * 1000, 2)

    # NotificationResponse has request_id / duration_ms fields but ORM model
    # does not; build a dict and override.
    response_data = NotificationResponse.model_validate(notification)
    response_data.request_id = request_id
    response_data.duration_ms = duration_ms
    return response_data


@router.get("/notifications", response_model=List[NotificationResponse])
async def get_notifications(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get user notifications (max 100 per page)"""
    notifications = NotificationService.get_user_notifications(db, current_user["id"], limit)
    return notifications
