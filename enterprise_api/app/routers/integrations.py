"""
CMS Integration router for hosted webhook endpoints.

Provides a single webhook URL that Ghost users can point their webhooks at
to get automatic C2PA signing of published content.

Authentication: The webhook endpoint uses an opaque token (ghwh_...) scoped
to the integration — NOT the org's primary API key. The token is generated
on integration creation and can be regenerated independently.

Endpoints:
- POST   /integrations/ghost                — Save Ghost integration config
- GET    /integrations/ghost                — Get current config (key masked)
- DELETE /integrations/ghost                — Remove integration
- POST   /integrations/ghost/regenerate-token — Regenerate webhook token
- POST   /integrations/ghost/webhook        — Receive Ghost webhooks
- POST   /integrations/ghost/sign/{post_id} — Manual sign trigger
"""

import asyncio
import hashlib
import logging
import secrets
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_content_db, get_db
from app.dependencies import get_current_organization, require_sign_permission
from app.models.ghost_integration import GhostIntegration
from app.schemas.integration_schemas import (
    GhostIntegrationCreate,
    GhostIntegrationResponse,
    GhostManualSignRequest,
    GhostTokenRegenerateResponse,
    GhostWebhookPayload,
)
from app.utils.crypto_utils import decrypt_sensitive_value, encrypt_sensitive_value
from app.services.ghost_integration import (
    GhostAdminClient,
    clear_in_flight,
    is_in_flight,
    set_in_flight,
    sign_ghost_post,
)

logger = logging.getLogger(__name__)

router = APIRouter()

WEBHOOK_TOKEN_PREFIX = "ghwh_"
WEBHOOK_BASE_PATH = "/api/v1/integrations/ghost/webhook"


# =============================================================================
# Token helpers
# =============================================================================


def _generate_webhook_token() -> str:
    """Generate a new opaque webhook token with ghwh_ prefix."""
    return f"{WEBHOOK_TOKEN_PREFIX}{secrets.token_urlsafe(32)}"


def _hash_token(token: str) -> str:
    """SHA-256 hash of a webhook token for storage."""
    return hashlib.sha256(token.encode()).hexdigest()


def _build_webhook_url(token: str, *, request: Request | None = None) -> str:
    """Build the full webhook URL with the token as query param.

    Always use configured API base URL to avoid issuing webhook links that
    accidentally point at non-API hosts when requests are proxied through
    dashboard/marketing domains.
    """
    _ = request  # Kept for backward compatibility with existing call sites.
    base_url = settings.api_base_url.rstrip("/")
    return f"{base_url}{WEBHOOK_BASE_PATH}?token={token}"


# =============================================================================
# Helpers
# =============================================================================


async def _get_ghost_integration(org_id: str, db: AsyncSession) -> GhostIntegration:
    """Get the Ghost integration for an organization, or raise 404."""
    result = await db.execute(
        select(GhostIntegration).where(
            GhostIntegration.organization_id == org_id,
            GhostIntegration.is_active == True,
        )
    )
    integration = result.scalar_one_or_none()
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Ghost integration configured. POST /api/v1/integrations/ghost to set one up.",
        )
    return integration


async def _get_integration_by_token(token_hash: str, db: AsyncSession) -> GhostIntegration:
    """Look up an active Ghost integration by webhook token hash."""
    result = await db.execute(
        select(GhostIntegration).where(
            GhostIntegration.webhook_token_hash == token_hash,
            GhostIntegration.is_active == True,
        )
    )
    integration = result.scalar_one_or_none()
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired webhook token",
        )
    return integration


async def _get_org_context_for_integration(org_id: str) -> dict:
    """Resolve an organization context by org ID for internal signing."""
    from app.config import settings
    from app.dependencies import DEMO_KEYS, _normalize_org_context
    from app.services.key_service_client import key_service_client
    from app.services.auth_service_client import auth_service_client
    from app.core.pricing_constants import DEFAULT_COALITION_PUBLISHER_PERCENT

    if settings.compose_org_context_via_auth_service:
        org_data = await auth_service_client.get_organization_context(org_id)
        if org_data:
            return _normalize_org_context(
                {
                    "organization_id": org_id,
                    "organization_name": org_data.get("name"),
                    "tier": org_data.get("tier", "free"),
                    "features": org_data.get("features", {}),
                    "permissions": ["sign", "verify"],
                    "monthly_api_limit": org_data.get("monthly_api_limit"),
                    "monthly_api_usage": org_data.get("monthly_api_usage"),
                    "coalition_member": org_data.get("coalition_member", True),
                    "coalition_rev_share": org_data.get("coalition_rev_share", DEFAULT_COALITION_PUBLISHER_PERCENT),
                    "certificate_pem": org_data.get("certificate_pem"),
                }
            )

    # Fall back: check demo keys for matching org_id
    for _key, ctx in DEMO_KEYS.items():
        if ctx.get("organization_id") == org_id:
            return _normalize_org_context(ctx.copy())

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Could not resolve organization context for signing",
    )


def _mask_key(key: str) -> str:
    """Mask an API key, showing only the last 4 characters."""
    if len(key) <= 8:
        return "****"
    return f"{'*' * (len(key) - 4)}{key[-4:]}"


def _build_response(
    integration: GhostIntegration,
    *,
    webhook_token: str | None = None,
    request: Request | None = None,
) -> GhostIntegrationResponse:
    """Build a GhostIntegrationResponse from a model instance.

    Args:
        webhook_token: If provided, include the plaintext token and build
            the webhook URL from it. Only set on creation / regeneration.
    """
    if webhook_token:
        webhook_url = _build_webhook_url(webhook_token, request=request)
    else:
        webhook_url = _build_webhook_url("ghwh_••••••••", request=request)

    return GhostIntegrationResponse(
        id=integration.id,
        organization_id=integration.organization_id,
        ghost_url=integration.ghost_url,
        ghost_admin_api_key_masked=_mask_key(decrypt_sensitive_value(bytes(integration.ghost_admin_api_key_encrypted))),
        auto_sign_on_publish=integration.auto_sign_on_publish,
        auto_sign_on_update=integration.auto_sign_on_update,
        manifest_mode=integration.manifest_mode,
        segmentation_level=integration.segmentation_level,
        ecc=integration.ecc,
        embed_c2pa=integration.embed_c2pa,
        badge_enabled=integration.badge_enabled,
        is_active=integration.is_active,
        webhook_url=webhook_url,
        webhook_token=webhook_token,
        last_webhook_at=integration.last_webhook_at,
        last_sign_at=integration.last_sign_at,
        sign_count=integration.sign_count,
        created_at=integration.created_at,
        updated_at=integration.updated_at,
    )


# =============================================================================
# CRUD Endpoints
# =============================================================================


@router.post(
    "/integrations/ghost",
    status_code=status.HTTP_201_CREATED,
    summary="Configure Ghost integration",
    description=(
        "Save your Ghost instance URL and Admin API key to enable automatic signing via webhooks. "
        "Returns a webhook URL containing a scoped token — copy it into Ghost."
    ),
    response_model=GhostIntegrationResponse,
    tags=["Integrations"],
)
async def create_ghost_integration(
    request: Request,
    body: GhostIntegrationCreate,
    organization: dict = Depends(require_sign_permission),
    db: AsyncSession = Depends(get_db),
):
    org_id = organization["organization_id"]

    # Check if integration already exists
    result = await db.execute(select(GhostIntegration).where(GhostIntegration.organization_id == org_id))
    existing = result.scalar_one_or_none()

    if existing:
        # Update config but keep existing token
        existing.ghost_url = body.ghost_url
        existing.ghost_admin_api_key_encrypted = encrypt_sensitive_value(body.ghost_admin_api_key)
        existing.auto_sign_on_publish = body.auto_sign_on_publish
        existing.auto_sign_on_update = body.auto_sign_on_update
        existing.manifest_mode = body.manifest_mode
        existing.segmentation_level = body.segmentation_level
        existing.ecc = body.ecc
        existing.embed_c2pa = body.embed_c2pa
        existing.badge_enabled = body.badge_enabled
        existing.is_active = True
        await db.commit()
        await db.refresh(existing)
        # Don't return token on update — user must use regenerate-token to see it again
        return _build_response(existing, request=request)

    # Create new with a fresh webhook token
    plaintext_token = _generate_webhook_token()
    integration = GhostIntegration(
        id=f"gi_{uuid.uuid4().hex[:16]}",
        organization_id=org_id,
        ghost_url=body.ghost_url,
        ghost_admin_api_key_encrypted=encrypt_sensitive_value(body.ghost_admin_api_key),
        webhook_token_hash=_hash_token(plaintext_token),
        auto_sign_on_publish=body.auto_sign_on_publish,
        auto_sign_on_update=body.auto_sign_on_update,
        manifest_mode=body.manifest_mode,
        segmentation_level=body.segmentation_level,
        ecc=body.ecc,
        embed_c2pa=body.embed_c2pa,
        badge_enabled=body.badge_enabled,
    )
    db.add(integration)
    await db.commit()
    await db.refresh(integration)
    # Return plaintext token on first creation — user must store it
    return _build_response(integration, webhook_token=plaintext_token, request=request)


@router.get(
    "/integrations/ghost",
    summary="Get Ghost integration config",
    description="Returns the current Ghost integration configuration with the API key masked.",
    response_model=GhostIntegrationResponse,
    tags=["Integrations"],
)
async def get_ghost_integration(
    request: Request,
    organization: dict = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
):
    org_id = organization["organization_id"]
    integration = await _get_ghost_integration(org_id, db)
    return _build_response(integration, request=request)


@router.delete(
    "/integrations/ghost",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove Ghost integration",
    description="Deactivate the Ghost integration for this organization.",
    tags=["Integrations"],
)
async def delete_ghost_integration(
    organization: dict = Depends(require_sign_permission),
    db: AsyncSession = Depends(get_db),
):
    org_id = organization["organization_id"]
    result = await db.execute(select(GhostIntegration).where(GhostIntegration.organization_id == org_id))
    integration = result.scalar_one_or_none()
    if integration:
        integration.is_active = False
        await db.commit()
    return None


# =============================================================================
# Token Regeneration
# =============================================================================


@router.post(
    "/integrations/ghost/regenerate-token",
    summary="Regenerate webhook token",
    description=("Invalidate the current webhook token and generate a new one. " "You must update the webhook URL in Ghost after regenerating."),
    response_model=GhostTokenRegenerateResponse,
    tags=["Integrations"],
)
async def regenerate_ghost_token(
    request: Request,
    organization: dict = Depends(require_sign_permission),
    db: AsyncSession = Depends(get_db),
):
    org_id = organization["organization_id"]
    integration = await _get_ghost_integration(org_id, db)

    plaintext_token = _generate_webhook_token()
    integration.webhook_token_hash = _hash_token(plaintext_token)
    await db.commit()

    logger.info("Regenerated webhook token for org %s", org_id)

    return GhostTokenRegenerateResponse(
        webhook_url=_build_webhook_url(plaintext_token, request=request),
        webhook_token=plaintext_token,
    )


# =============================================================================
# Webhook Endpoint
# =============================================================================


@router.post(
    "/integrations/ghost/webhook",
    summary="Receive Ghost CMS webhooks",
    description="""
Webhook endpoint for Ghost CMS. Configure in Ghost Admin → Integrations → Webhooks.

Use the `webhook_url` returned when you created the integration — it contains a scoped token.

Supported events: `post.published`, `post.published.edited`, `page.published`, `page.published.edited`
""",
    tags=["Integrations"],
)
async def ghost_webhook(
    request: Request,
    token: str = Query(..., description="Webhook token (ghwh_...) from integration setup"),
    db: AsyncSession = Depends(get_db),
    content_db: AsyncSession = Depends(get_content_db),
):
    # 1. Authenticate via webhook token
    if not token.startswith(WEBHOOK_TOKEN_PREFIX):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Invalid webhook token format"},
        )

    token_hash = _hash_token(token)
    try:
        integration = await _get_integration_by_token(token_hash, db)
    except HTTPException:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Invalid or expired webhook token"},
        )

    # 3. Parse webhook payload
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Invalid JSON payload"},
        )

    payload = GhostWebhookPayload(**body)
    resource_type = payload.get_resource_type()
    current = payload.get_current()

    if not resource_type or not current:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "ignored", "reason": "No post/page data in payload"},
        )

    post_id = current.get("id")
    post_status = current.get("status", "")

    if not post_id:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "ignored", "reason": "No post ID in payload"},
        )

    # Only sign published content
    if post_status and post_status != "published":
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "ignored", "reason": f"Post status is '{post_status}', not 'published'"},
        )

    # Check auto-sign settings
    if not integration.auto_sign_on_publish and not integration.auto_sign_on_update:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "ignored", "reason": "Auto-signing is disabled"},
        )

    # 4. Loop prevention
    if is_in_flight(post_id):
        logger.debug("Post %s is in-flight, skipping (loop prevention)", post_id)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "skipped", "reason": "Post is currently being signed"},
        )

    # 5. Accept webhook and process async
    set_in_flight(post_id)

    # Update last_webhook_at
    from datetime import datetime, timezone

    integration.last_webhook_at = datetime.now(timezone.utc)
    await db.commit()

    # Capture config values before the request scope closes
    org_id = integration.organization_id
    ghost_url = integration.ghost_url
    ghost_admin_api_key = decrypt_sensitive_value(bytes(integration.ghost_admin_api_key_encrypted))
    manifest_mode = integration.manifest_mode
    segmentation_level = integration.segmentation_level
    ecc = integration.ecc
    embed_c2pa = integration.embed_c2pa
    badge_enabled = integration.badge_enabled

    # Fire-and-forget signing task with fresh DB sessions
    from app.database import core_session_factory, content_session_factory

    async def _do_sign():
        try:
            organization = await _get_org_context_for_integration(org_id)
            ghost_client = GhostAdminClient(
                ghost_url=ghost_url,
                admin_api_key=ghost_admin_api_key,
            )
            async with core_session_factory() as task_core_db, content_session_factory() as task_content_db:
                result = await sign_ghost_post(
                    ghost_client=ghost_client,
                    post_id=post_id,
                    post_type=resource_type,
                    organization=organization,
                    core_db=task_core_db,
                    content_db=task_content_db,
                    manifest_mode=manifest_mode,
                    segmentation_level=segmentation_level,
                    ecc=ecc,
                    embed_c2pa=embed_c2pa,
                    badge_enabled=badge_enabled,
                )
                if result.get("success"):
                    logger.info(
                        "Ghost %s %s signed via webhook (doc=%s, segments=%d)",
                        resource_type,
                        post_id,
                        result.get("document_id"),
                        result.get("total_segments", 0),
                    )
                else:
                    logger.error(
                        "Ghost %s %s signing failed via webhook: %s",
                        resource_type,
                        post_id,
                        result.get("error"),
                    )
        except Exception as e:
            logger.error("Ghost webhook signing error for %s %s: %s", resource_type, post_id, e, exc_info=True)
        finally:
            clear_in_flight(post_id)

    asyncio.create_task(_do_sign())

    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={
            "status": "accepted",
            "post_id": post_id,
            "post_type": resource_type,
        },
    )


# =============================================================================
# Manual Sign Endpoint
# =============================================================================


@router.post(
    "/integrations/ghost/sign/{post_id}",
    summary="Manually sign a Ghost post",
    description="Trigger signing for a specific Ghost post or page.",
    tags=["Integrations"],
)
async def manual_sign_ghost_post(
    post_id: str,
    body: GhostManualSignRequest = GhostManualSignRequest(),
    organization: dict = Depends(require_sign_permission),
    db: AsyncSession = Depends(get_db),
    content_db: AsyncSession = Depends(get_content_db),
):
    org_id = organization["organization_id"]
    integration = await _get_ghost_integration(org_id, db)

    if is_in_flight(post_id):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"error": "Post is currently being signed"},
        )

    set_in_flight(post_id)
    try:
        ghost_client = GhostAdminClient(
            ghost_url=integration.ghost_url,
            admin_api_key=decrypt_sensitive_value(bytes(integration.ghost_admin_api_key_encrypted)),
        )

        result = await sign_ghost_post(
            ghost_client=ghost_client,
            post_id=post_id,
            post_type=body.post_type,
            organization=organization,
            core_db=db,
            content_db=content_db,
            manifest_mode=integration.manifest_mode,
            segmentation_level=integration.segmentation_level,
            ecc=integration.ecc,
            embed_c2pa=integration.embed_c2pa,
            badge_enabled=integration.badge_enabled,
        )

        if result.get("success"):
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": True,
                    "document_id": result.get("document_id"),
                    "instance_id": result.get("instance_id"),
                    "total_segments": result.get("total_segments"),
                    "action_type": result.get("action_type"),
                },
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "success": False,
                    "error": result.get("error", "Unknown error"),
                },
            )
    finally:
        clear_in_flight(post_id)
