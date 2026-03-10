"""
Webhooks router for event notification management.

Provides endpoints for registering, listing, and managing webhooks.
"""

import hashlib
import logging
import secrets
from datetime import datetime, timezone
from typing import List, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_organization
from app.services.webhook_dispatcher import webhook_dispatcher
from app.utils.crypto_utils import decrypt_sensitive_value, encrypt_sensitive_value
from app.utils.outbound_url import validate_https_public_url

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])
logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

VALID_EVENTS = {
    "document.signed",
    "document.verified",
    "document.revoked",
    "document.reinstated",
    "quota.warning",
    "quota.exceeded",
    "key.created",
    "key.revoked",
    "key.rotated",
    "rights.profile.updated",
    "rights.notice.delivered",
    "rights.licensing.request_received",
    "rights.licensing.agreement_created",
    "rights.detection.event",
}


# =============================================================================
# Request/Response Models
# =============================================================================


class WebhookSummary(BaseModel):
    """Summary of a webhook."""

    id: str = Field(..., description="Webhook ID")
    url: str = Field(..., description="Webhook URL")
    events: List[str] = Field(..., description="Subscribed events")
    is_active: bool = Field(True, description="Whether webhook is active")
    is_verified: bool = Field(False, description="Whether webhook has been verified")
    created_at: str = Field(..., description="Creation timestamp")
    last_triggered_at: Optional[str] = Field(None, description="Last trigger timestamp")
    success_count: int = Field(0, description="Successful deliveries")
    failure_count: int = Field(0, description="Failed deliveries")


class WebhookCreateRequest(BaseModel):
    """Request to create a webhook."""

    url: str = Field(..., description="Webhook URL (must be HTTPS)", max_length=2048)
    events: List[str] = Field(..., description="Events to subscribe to", min_length=1)
    secret: Optional[str] = Field(
        None,
        description="Shared secret for HMAC signature verification",
        min_length=16,
        max_length=256,
    )


class WebhookCreateResponse(BaseModel):
    """Response after creating a webhook."""

    success: bool = True
    data: dict


class WebhookListResponse(BaseModel):
    """Response for webhook listing."""

    success: bool = True
    data: dict


class WebhookUpdateRequest(BaseModel):
    """Request to update a webhook."""

    url: Optional[str] = Field(None, description="New webhook URL")
    events: Optional[List[str]] = Field(None, description="New event subscriptions")
    is_active: Optional[bool] = Field(None, description="Enable/disable webhook")


class WebhookUpdateResponse(BaseModel):
    """Response after updating a webhook."""

    success: bool = True
    data: dict


class WebhookDeleteResponse(BaseModel):
    """Response after deleting a webhook."""

    success: bool = True
    data: dict


class WebhookTestResponse(BaseModel):
    """Response after testing a webhook."""

    success: bool = True
    data: dict


class WebhookDeliveryLog(BaseModel):
    """Single delivery log entry."""

    id: str
    event_type: str
    status: str
    attempts: int
    response_status_code: Optional[int] = None
    response_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    created_at: str
    delivered_at: Optional[str] = None


class WebhookDeliveriesResponse(BaseModel):
    """Response for webhook deliveries listing."""

    success: bool = True
    data: dict


# =============================================================================
# Helper Functions
# =============================================================================


def hash_secret(secret: str) -> str:
    """Hash a webhook secret for storage."""
    return hashlib.sha256(secret.encode()).hexdigest()


def validate_events(events: List[str]) -> List[str]:
    """Validate and filter events."""
    valid = [e for e in events if e in VALID_EVENTS]
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_EVENTS",
                "message": "No valid events provided",
                "valid_events": list(VALID_EVENTS),
            },
        )
    return valid


def require_webhooks_business_tier(
    organization: dict = Depends(get_current_organization),
) -> dict:
    tier = (organization.get("tier") or "free").lower().replace("-", "_")
    allowed_tiers = {"enterprise", "strategic_partner", "demo"}
    if tier not in allowed_tiers:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FEATURE_NOT_AVAILABLE",
                "message": "Webhooks require Enterprise tier",
                "upgrade_url": "/billing/upgrade",
            },
        )
    return organization


# =============================================================================
# Endpoints
# =============================================================================


@router.get("", response_model=WebhookListResponse)
async def list_webhooks(
    organization: dict = Depends(require_webhooks_business_tier),
    db: AsyncSession = Depends(get_db),
) -> WebhookListResponse:
    """
    List all webhooks for the organization.
    """
    org_id = organization.get("organization_id")

    result = await db.execute(
        text(
            """
            SELECT
                id, url, events, is_active, is_verified,
                created_at, last_triggered_at,
                success_count, failure_count
            FROM webhooks
            WHERE organization_id = :org_id
            ORDER BY created_at DESC
        """
        ),
        {"org_id": org_id},
    )
    rows = result.fetchall()

    webhooks = []
    for row in rows:
        events = row.events if isinstance(row.events, list) else []
        webhooks.append(
            WebhookSummary(
                id=row.id,
                url=row.url,
                events=events,
                is_active=row.is_active,
                is_verified=row.is_verified,
                created_at=row.created_at.isoformat() if row.created_at else "",
                last_triggered_at=(row.last_triggered_at.isoformat() if row.last_triggered_at else None),
                success_count=row.success_count or 0,
                failure_count=row.failure_count or 0,
            ).model_dump()
        )

    return WebhookListResponse(
        data={
            "webhooks": webhooks,
            "total": len(webhooks),
        }
    )


@router.post("", response_model=WebhookCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_webhook(
    request: WebhookCreateRequest,
    organization: dict = Depends(require_webhooks_business_tier),
    db: AsyncSession = Depends(get_db),
) -> WebhookCreateResponse:
    """
    Register a new webhook.

    The webhook URL must be HTTPS. You can optionally provide a shared secret
    for HMAC signature verification of webhook payloads.
    """
    org_id = organization.get("organization_id")

    try:
        validate_https_public_url(request.url)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_URL", "message": "Webhook URL must use HTTPS"},
        )

    # Validate events
    events = validate_events(request.events)

    # Check webhook limit (max 10 per org)
    count_result = await db.execute(
        text("SELECT COUNT(*) FROM webhooks WHERE organization_id = :org_id"),
        {"org_id": org_id},
    )
    current_count = count_result.scalar() or 0

    if current_count >= 10:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "WEBHOOK_LIMIT_REACHED",
                "message": "Maximum 10 webhooks per organization",
            },
        )

    # Generate webhook ID
    webhook_id = f"wh_{secrets.token_hex(12)}"

    # Hash secret if provided
    secret_hash = hash_secret(request.secret) if request.secret else None
    secret_encrypted = encrypt_sensitive_value(request.secret) if request.secret else None

    # Insert webhook
    params = {
        "id": webhook_id,
        "org_id": org_id,
        "url": request.url,
        "events": events,
        "secret_hash": secret_hash,
        "secret_encrypted": secret_encrypted,
        "created_at": datetime.now(timezone.utc),
    }
    try:
        await db.execute(
            text(
                """
                INSERT INTO webhooks (
                    id, organization_id, url, events, secret_hash, secret_encrypted,
                    is_active, is_verified, success_count, failure_count, created_at
                ) VALUES (
                    :id, :org_id, :url, :events, :secret_hash, :secret_encrypted,
                    true, false, 0, 0, :created_at
                )
            """
            ),
            params,
        )
    except ProgrammingError:
        await db.rollback()
        await db.execute(
            text(
                """
                INSERT INTO webhooks (
                    id, organization_id, url, events, secret_hash,
                    is_active, is_verified, success_count, failure_count, created_at
                ) VALUES (
                    :id, :org_id, :url, :events, :secret_hash,
                    true, false, 0, 0, :created_at
                )
            """
            ),
            {key: value for key, value in params.items() if key != "secret_encrypted"},
        )
    await db.commit()

    logger.info(f"Created webhook {webhook_id} for organization {org_id}")

    return WebhookCreateResponse(
        data={
            "id": webhook_id,
            "url": request.url,
            "events": events,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    )


@router.get("/{webhook_id}", response_model=WebhookListResponse)
async def get_webhook(
    webhook_id: str,
    organization: dict = Depends(require_webhooks_business_tier),
    db: AsyncSession = Depends(get_db),
) -> WebhookListResponse:
    """
    Get details of a specific webhook.
    """
    org_id = organization.get("organization_id")

    result = await db.execute(
        text(
            """
            SELECT
                id, url, events, is_active, is_verified,
                created_at, last_triggered_at,
                success_count, failure_count
            FROM webhooks
            WHERE id = :webhook_id AND organization_id = :org_id
        """
        ),
        {"webhook_id": webhook_id, "org_id": org_id},
    )
    row = result.fetchone()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "WEBHOOK_NOT_FOUND", "message": "Webhook not found"},
        )

    try:
        validate_https_public_url(row.url, resolve_dns=True)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_URL", "message": "Webhook URL must use HTTPS"},
        )

    events = row.events if isinstance(row.events, list) else []

    return WebhookListResponse(
        data={
            "webhook": WebhookSummary(
                id=row.id,
                url=row.url,
                events=events,
                is_active=row.is_active,
                is_verified=row.is_verified,
                created_at=row.created_at.isoformat() if row.created_at else "",
                last_triggered_at=(row.last_triggered_at.isoformat() if row.last_triggered_at else None),
                success_count=row.success_count or 0,
                failure_count=row.failure_count or 0,
            ).model_dump()
        }
    )


@router.patch("/{webhook_id}", response_model=WebhookUpdateResponse)
async def update_webhook(
    webhook_id: str,
    request: WebhookUpdateRequest,
    organization: dict = Depends(require_webhooks_business_tier),
    db: AsyncSession = Depends(get_db),
) -> WebhookUpdateResponse:
    """
    Update a webhook's URL, events, or active status.
    """
    org_id = organization.get("organization_id")

    # Verify webhook exists
    result = await db.execute(
        text("SELECT id FROM webhooks WHERE id = :webhook_id AND organization_id = :org_id"),
        {"webhook_id": webhook_id, "org_id": org_id},
    )
    if not result.fetchone():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "WEBHOOK_NOT_FOUND", "message": "Webhook not found"},
        )

    # Build update
    updates = []
    params = {"webhook_id": webhook_id, "org_id": org_id}

    if request.url is not None:
        try:
            validate_https_public_url(request.url)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_URL", "message": "Webhook URL must use HTTPS"},
            )
        updates.append("url = :url")
        params["url"] = request.url

    if request.events is not None:
        events = validate_events(request.events)
        updates.append("events = :events")
        params["events"] = events

    if request.is_active is not None:
        updates.append("is_active = :is_active")
        params["is_active"] = request.is_active

    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No updates provided",
        )

    updates.append("updated_at = :updated_at")
    params["updated_at"] = datetime.now(timezone.utc)

    await db.execute(
        text(f"UPDATE webhooks SET {', '.join(updates)} WHERE id = :webhook_id AND organization_id = :org_id"),
        params,
    )
    await db.commit()

    return WebhookUpdateResponse(
        data={
            "id": webhook_id,
            "updated": True,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
    )


@router.delete("/{webhook_id}", response_model=WebhookDeleteResponse)
async def delete_webhook(
    webhook_id: str,
    organization: dict = Depends(require_webhooks_business_tier),
    db: AsyncSession = Depends(get_db),
) -> WebhookDeleteResponse:
    """
    Delete a webhook.
    """
    org_id = organization.get("organization_id")

    # Verify webhook exists
    result = await db.execute(
        text("SELECT id FROM webhooks WHERE id = :webhook_id AND organization_id = :org_id"),
        {"webhook_id": webhook_id, "org_id": org_id},
    )
    if not result.fetchone():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "WEBHOOK_NOT_FOUND", "message": "Webhook not found"},
        )

    # Delete webhook and its deliveries
    await db.execute(
        text("DELETE FROM webhook_deliveries WHERE webhook_id = :webhook_id"),
        {"webhook_id": webhook_id},
    )
    await db.execute(
        text("DELETE FROM webhooks WHERE id = :webhook_id AND organization_id = :org_id"),
        {"webhook_id": webhook_id, "org_id": org_id},
    )
    await db.commit()

    logger.info(f"Deleted webhook {webhook_id} for organization {org_id}")

    return WebhookDeleteResponse(
        data={
            "id": webhook_id,
            "deleted": True,
            "deleted_at": datetime.now(timezone.utc).isoformat(),
        }
    )


@router.post("/{webhook_id}/test", response_model=WebhookTestResponse)
async def test_webhook(
    webhook_id: str,
    organization: dict = Depends(require_webhooks_business_tier),
    db: AsyncSession = Depends(get_db),
) -> WebhookTestResponse:
    """
    Send a test event to the webhook.

    This sends a test payload to verify the webhook is configured correctly.
    """
    org_id = organization.get("organization_id")

    # Get webhook
    try:
        result = await db.execute(
            text("SELECT id, url, secret_hash, secret_encrypted FROM webhooks WHERE id = :webhook_id AND organization_id = :org_id"),
            {"webhook_id": webhook_id, "org_id": org_id},
        )
    except ProgrammingError:
        await db.rollback()
        result = await db.execute(
            text("SELECT id, url, secret_hash FROM webhooks WHERE id = :webhook_id AND organization_id = :org_id"),
            {"webhook_id": webhook_id, "org_id": org_id},
        )
    row = result.fetchone()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "WEBHOOK_NOT_FOUND", "message": "Webhook not found"},
        )

    try:
        validate_https_public_url(row.url, resolve_dns=True)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_URL", "message": "Webhook URL must use HTTPS"},
        )

    # Build test payload
    import json

    test_payload = {
        "event": "test",
        "webhook_id": webhook_id,
        "organization_id": org_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": {
            "message": "This is a test webhook delivery from Encypher",
        },
    }
    payload_json = json.dumps(test_payload)
    secret = None
    secret_encrypted = getattr(row, "secret_encrypted", None)
    if secret_encrypted:
        try:
            secret = decrypt_sensitive_value(bytes(secret_encrypted))
        except ValueError as exc:
            logger.warning("webhook_secret_decrypt_failed", extra={"webhook_id": webhook_id, "error": str(exc)})

    # Send test request
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=False) as client:
            delivery_id = f"test_{secrets.token_hex(8)}"
            headers = webhook_dispatcher.build_headers(
                event_type="test",
                delivery_id=delivery_id,
                payload_json=payload_json,
                secret=secret,
            )

            response = await client.post(
                row.url,
                content=payload_json,
                headers=headers,
            )

            success = 200 <= response.status_code < 300

            # Update webhook verification status
            if success:
                await db.execute(
                    text("UPDATE webhooks SET is_verified = true WHERE id = :webhook_id"),
                    {"webhook_id": webhook_id},
                )
                await db.commit()

            return WebhookTestResponse(
                data={
                    "webhook_id": webhook_id,
                    "url": row.url,
                    "success": success,
                    "status_code": response.status_code,
                    "response_time_ms": int(response.elapsed.total_seconds() * 1000),
                    "message": ("Webhook test successful" if success else f"Webhook returned {response.status_code}"),
                }
            )

    except httpx.TimeoutException:
        return WebhookTestResponse(
            data={
                "webhook_id": webhook_id,
                "url": row.url,
                "success": False,
                "error": "Request timed out after 10 seconds",
            }
        )
    except httpx.RequestError as e:
        return WebhookTestResponse(
            data={
                "webhook_id": webhook_id,
                "url": row.url,
                "success": False,
                "error": str(e),
            }
        )


@router.get("/{webhook_id}/deliveries", response_model=WebhookDeliveriesResponse)
async def get_webhook_deliveries(
    webhook_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    organization: dict = Depends(require_webhooks_business_tier),
    db: AsyncSession = Depends(get_db),
) -> WebhookDeliveriesResponse:
    """
    Get delivery history for a webhook.
    """
    org_id = organization.get("organization_id")
    offset = (page - 1) * page_size

    # Verify webhook exists
    result = await db.execute(
        text("SELECT id FROM webhooks WHERE id = :webhook_id AND organization_id = :org_id"),
        {"webhook_id": webhook_id, "org_id": org_id},
    )
    if not result.fetchone():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "WEBHOOK_NOT_FOUND", "message": "Webhook not found"},
        )

    # Get total count
    count_result = await db.execute(
        text("SELECT COUNT(*) FROM webhook_deliveries WHERE webhook_id = :webhook_id"),
        {"webhook_id": webhook_id},
    )
    total = count_result.scalar() or 0

    # Get deliveries
    result = await db.execute(
        text(
            """
            SELECT
                id, event_type, status, attempts,
                response_status_code, response_time_ms, error_message,
                created_at, delivered_at
            FROM webhook_deliveries
            WHERE webhook_id = :webhook_id
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
        """
        ),
        {"webhook_id": webhook_id, "limit": page_size, "offset": offset},
    )
    rows = result.fetchall()

    deliveries = []
    for row in rows:
        deliveries.append(
            WebhookDeliveryLog(
                id=row.id,
                event_type=row.event_type,
                status=row.status,
                attempts=row.attempts,
                response_status_code=row.response_status_code,
                response_time_ms=row.response_time_ms,
                error_message=row.error_message,
                created_at=row.created_at.isoformat() if row.created_at else "",
                delivered_at=row.delivered_at.isoformat() if row.delivered_at else None,
            ).model_dump()
        )

    return WebhookDeliveriesResponse(
        data={
            "deliveries": deliveries,
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    )
