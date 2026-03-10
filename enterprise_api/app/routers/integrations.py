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
import json
import logging
import os
import secrets
import smtplib
import uuid
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import bindparam, select, text
from sqlalchemy.dialects.postgresql import JSONB
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
from app.services.ghost_integration import (
    GhostAdminClient,
    clear_in_flight,
    is_in_flight,
    set_in_flight,
    sign_ghost_post,
)
from app.services.provisioning_service import ProvisioningService
from app.services.session_service import session_service
from app.utils.crypto_utils import decrypt_sensitive_value, encrypt_sensitive_value

logger = logging.getLogger(__name__)

router = APIRouter()

WEBHOOK_TOKEN_PREFIX = "ghwh_"
WEBHOOK_BASE_PATH = "/api/v1/integrations/ghost/webhook"


class WordPressIntegrationStatusPayload(BaseModel):
    install_id: str | None = Field(default=None, description="Stable install ID for a WordPress property")
    connection_status: str = Field(..., description="Current plugin connection state")
    site_url: str | None = Field(default=None, description="Public WordPress site URL")
    admin_url: str | None = Field(default=None, description="WordPress admin settings URL")
    site_name: str | None = Field(default=None, description="Human-readable WordPress site name")
    environment: str | None = Field(default=None, description="Environment label such as production or staging")
    network_id: str | None = Field(default=None, description="Optional multisite network identifier")
    blog_id: int | None = Field(default=None, description="Optional WordPress blog/site ID")
    is_multisite: bool | None = Field(default=None, description="Whether the WordPress install is part of multisite")
    is_primary: bool | None = Field(default=None, description="Whether this install is the org's primary WordPress property")
    organization_id: str | None = Field(default=None, description="Organization ID resolved by the plugin")
    organization_name: str | None = Field(default=None, description="Organization name resolved by the plugin")
    plugin_version: str | None = Field(default=None, description="Installed WordPress plugin version")
    plugin_installed: bool | None = Field(default=None, description="Whether the plugin is installed and active")
    connection_tested: bool | None = Field(default=None, description="Whether WordPress successfully ran the connection test")
    last_connection_checked_at: str | None = Field(default=None, description="ISO timestamp of the last connection check")
    last_signed_at: str | None = Field(default=None, description="ISO timestamp of the last successful signed post")
    last_signed_post_id: int | None = Field(default=None, description="WordPress post ID for the last successful sign")
    last_signed_post_url: str | None = Field(default=None, description="Canonical URL of the last successfully signed post")
    signed_post_count: int | None = Field(default=None, description="Count of posts signed by the plugin")


class WordPressIntegrationStatusResponse(BaseModel):
    success: bool = True
    data: dict


class WordPressInstallRegistrationPayload(BaseModel):
    install_id: str | None = Field(default=None, description="Stable install ID for a WordPress property")
    site_url: str | None = Field(default=None, description="Public WordPress site URL")
    admin_url: str | None = Field(default=None, description="WordPress admin settings URL")
    site_name: str | None = Field(default=None, description="Human-readable WordPress site name")
    environment: str | None = Field(default=None, description="Environment label such as production or staging")
    network_id: str | None = Field(default=None, description="Optional multisite network identifier")
    blog_id: int | None = Field(default=None, description="Optional WordPress blog/site ID")
    is_multisite: bool | None = Field(default=None, description="Whether the WordPress install is part of multisite")
    is_primary: bool | None = Field(default=None, description="Whether this install is the org's primary WordPress property")
    plugin_version: str | None = Field(default=None, description="Installed WordPress plugin version")


class WordPressVerificationEventPayload(BaseModel):
    install_id: str = Field(..., description="Stable install ID for a WordPress property")
    post_id: int | None = Field(default=None, description="WordPress post ID that was verified")
    post_url: str | None = Field(default=None, description="Canonical post URL that was verified")
    valid: bool = Field(default=False, description="Whether verification succeeded")
    tampered: bool = Field(default=False, description="Whether content appeared tampered")
    status: str | None = Field(default=None, description="Normalized verification status from the plugin")
    verified_at: str | None = Field(default=None, description="ISO timestamp when verification ran")
    source: str = Field(default="wordpress_plugin", description="Event source")


class WordPressActionQueuePayload(BaseModel):
    action_type: str = Field(..., description="Queued action to execute on the install")
    note: str | None = Field(default=None, description="Optional reason or note shown to the install")


class WordPressActionAckPayload(BaseModel):
    status: str = Field(..., description="Acknowledged action status")
    result_message: str | None = Field(default=None, description="Optional result message")
    completed_at: str | None = Field(default=None, description="ISO timestamp when the action completed")


class WordPressConnectStartPayload(BaseModel):
    email: EmailStr
    install_id: str | None = Field(default=None, description="Stable install ID for the WordPress property")
    site_url: str | None = Field(default=None, description="Public WordPress site URL")
    admin_url: str | None = Field(default=None, description="WordPress admin settings URL")
    site_name: str | None = Field(default=None, description="Human-readable WordPress site name")
    environment: str | None = Field(default=None, description="Environment label such as production or staging")
    api_base_url: str | None = Field(default=None, description="Plugin-configured Encypher API base URL")


class WordPressConnectPollResponse(BaseModel):
    success: bool = True
    data: dict


class WordPressConnectCompletePayload(BaseModel):
    token: str = Field(..., description="Magic-link completion token")


def _parse_iso_datetime(value: str | None) -> str | None:
    if not value:
        return None
    try:
        normalized = value.replace("Z", "+00:00")
        return datetime.fromisoformat(normalized).astimezone(timezone.utc).isoformat()
    except ValueError:
        return None


WORDPRESS_CONNECT_SESSION_TTL_SECONDS = 15 * 60


def _wordpress_connect_session_key(session_id: str) -> str:
    return f"encypher:wordpress-connect:{session_id}"


def _wordpress_connect_token_key(token: str) -> str:
    return f"encypher:wordpress-connect-token:{token}"


def _email_config() -> dict:
    return {
        "smtp_host": os.getenv("SMTP_HOST", "smtp.zoho.com"),
        "smtp_port": int(os.getenv("SMTP_PORT", "587")),
        "smtp_user": os.getenv("SMTP_USER", ""),
        "smtp_pass": os.getenv("SMTP_PASS", ""),
        "smtp_tls": os.getenv("SMTP_TLS", "true").lower() == "true",
        "email_from": os.getenv("EMAIL_FROM", "noreply@encypherai.com"),
        "email_from_name": os.getenv("EMAIL_FROM_NAME", "Encypher"),
    }


async def _store_wordpress_connect_session(session_id: str, data: dict, ttl: int = WORDPRESS_CONNECT_SESSION_TTL_SECONDS) -> None:
    redis_client = session_service.redis_client
    if redis_client is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="WordPress connect sessions unavailable")
    await redis_client.setex(_wordpress_connect_session_key(session_id), ttl, json.dumps(data))


async def _load_wordpress_connect_session(session_id: str) -> dict | None:
    redis_client = session_service.redis_client
    if redis_client is None:
        return None
    payload = await redis_client.get(_wordpress_connect_session_key(session_id))
    if not payload:
        return None
    return json.loads(payload)


async def _store_wordpress_connect_token(token: str, session_id: str, ttl: int = WORDPRESS_CONNECT_SESSION_TTL_SECONDS) -> None:
    redis_client = session_service.redis_client
    if redis_client is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="WordPress connect sessions unavailable")
    await redis_client.setex(_wordpress_connect_token_key(token), ttl, session_id)


async def _resolve_wordpress_connect_token(token: str) -> str | None:
    redis_client = session_service.redis_client
    if redis_client is None:
        return None
    session_id = await redis_client.get(_wordpress_connect_token_key(token))
    return str(session_id) if session_id else None


async def _send_wordpress_connect_email(email: str, token: str, site_name: str | None, site_url: str | None) -> bool:
    dashboard_base = settings.dashboard_url.rstrip("/")
    link = f"{dashboard_base}/wordpress/connect?token={token}"
    site_label = site_name or site_url or "your WordPress site"
    html_content = (
        f"<html><body><h2>Connect {site_label} to Encypher</h2>"
        f"<p>Click the secure link below to approve this WordPress site and provision its API key.</p>"
        f'<p><a href="{link}">Approve WordPress connection</a></p>'
        f"<p>If you did not request this, you can ignore this email.</p></body></html>"
    )
    plain_content = (
        f"Connect {site_label} to Encypher\n\n"
        f"Open this secure link to approve the WordPress connection:\n{link}\n\n"
        "If you did not request this, you can ignore this email."
    )
    config = _email_config()
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Approve your WordPress connection - Encypher"
        msg["From"] = f"{config['email_from_name']} <{config['email_from']}>"
        msg["To"] = email
        msg.attach(MIMEText(plain_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(config["smtp_host"], config["smtp_port"]) as server:
            if config["smtp_tls"]:
                server.starttls()
            if config["smtp_user"] and config["smtp_pass"]:
                server.login(config["smtp_user"], config["smtp_pass"])
            server.sendmail(config["email_from"], [email], msg.as_string())
        return True
    except Exception as exc:
        logger.error("wordpress_connect_email_failed", extra={"email": email, "error": str(exc)})
        return False


async def _create_wordpress_connect_session(payload: WordPressConnectStartPayload) -> dict:
    session_id = f"wpcs_{uuid.uuid4().hex[:24]}"
    approve_token = secrets.token_urlsafe(32)
    session_data = {
        "session_id": session_id,
        "status": "pending_email_verification",
        "email": str(payload.email),
        "install_id": _resolve_install_id(payload.install_id),
        "site_url": payload.site_url,
        "admin_url": payload.admin_url,
        "site_name": payload.site_name,
        "environment": payload.environment,
        "api_base_url": payload.api_base_url,
        "organization_id": None,
        "organization_name": None,
        "api_key": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
    }
    await _store_wordpress_connect_session(session_id, session_data)
    await _store_wordpress_connect_token(approve_token, session_id)
    email_sent = await _send_wordpress_connect_email(str(payload.email), approve_token, payload.site_name, payload.site_url)
    return {
        "session_id": session_id,
        "status": session_data["status"],
        "email": session_data["email"],
        "email_sent": email_sent,
        "install_id": session_data["install_id"],
    }


async def _complete_wordpress_connect_session(token: str, db: AsyncSession) -> dict:
    session_id = await _resolve_wordpress_connect_token(token)
    if not session_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="WordPress connect session not found")
    session_data = await _load_wordpress_connect_session(session_id)
    if not session_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="WordPress connect session expired")
    if session_data.get("status") == "completed":
        return session_data

    org, api_key, _user_id = await ProvisioningService.auto_provision(
        db=db,
        email=session_data["email"],
        organization_name=session_data.get("site_name") or None,
        source="wordpress_magic_link",
        source_metadata={
            "install_id": session_data.get("install_id"),
            "site_url": session_data.get("site_url"),
            "admin_url": session_data.get("admin_url"),
            "environment": session_data.get("environment"),
        },
        tier="free",
        auto_activate=True,
    )

    session_data.update(
        {
            "status": "completed",
            "organization_id": org.organization_id,
            "organization_name": org.name,
            "api_key": api_key,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    await _store_wordpress_connect_session(session_id, session_data)
    return session_data


async def _poll_wordpress_connect_session(session_id: str) -> dict:
    session_data = await _load_wordpress_connect_session(session_id)
    if not session_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="WordPress connect session not found")
    return {
        "session_id": session_data.get("session_id"),
        "status": session_data.get("status"),
        "email": session_data.get("email"),
        "install_id": session_data.get("install_id"),
        "organization_id": session_data.get("organization_id"),
        "organization_name": session_data.get("organization_name"),
        "api_key": session_data.get("api_key") if session_data.get("status") == "completed" else None,
        "api_base_url": session_data.get("api_base_url") or settings.api_base_url.rstrip("/"),
        "completed_at": session_data.get("completed_at"),
    }


def _normalize_wordpress_store(raw: dict | None) -> dict:
    store = raw if isinstance(raw, dict) else {}
    installs = store.get("installs") if isinstance(store.get("installs"), list) else []
    recent_events = store.get("recent_events") if isinstance(store.get("recent_events"), list) else []
    remote_actions = store.get("remote_actions") if isinstance(store.get("remote_actions"), list) else []
    return {
        "version": 2,
        "installs": [item for item in installs if isinstance(item, dict)],
        "recent_events": [item for item in recent_events if isinstance(item, dict)],
        "remote_actions": [item for item in remote_actions if isinstance(item, dict)],
    }


def _resolve_install_id(install_id: str | None) -> str:
    if install_id and install_id.strip():
        return install_id.strip()
    return f"wpi_{uuid.uuid4().hex[:16]}"


def _trim_wordpress_store(store: dict) -> dict:
    store["recent_events"] = store["recent_events"][-100:]
    store["remote_actions"] = store["remote_actions"][-100:]
    return store


def _select_primary_install(installs: list[dict]) -> dict | None:
    if not installs:
        return None
    primary = next((install for install in installs if install.get("is_primary")), None)
    if primary is not None:
        return primary
    return max(installs, key=lambda install: install.get("updated_at") or install.get("created_at") or "")


def _build_wordpress_summary(store: dict) -> dict:
    installs = store.get("installs", [])
    primary = _select_primary_install(installs)
    queued_actions = [action for action in store.get("remote_actions", []) if action.get("status") == "queued"]
    summary = {
        "version": store.get("version", 2),
        "install_count": len(installs),
        "installs": installs,
        "recent_events": store.get("recent_events", []),
        "remote_actions": store.get("remote_actions", []),
        "queued_action_count": len(queued_actions),
    }
    if primary is not None:
        summary.update(
            {
                "install_id": primary.get("install_id"),
                "connection_status": primary.get("connection_status"),
                "site_url": primary.get("site_url"),
                "admin_url": primary.get("admin_url"),
                "site_name": primary.get("site_name"),
                "environment": primary.get("environment"),
                "organization_id": primary.get("organization_id"),
                "organization_name": primary.get("organization_name"),
                "plugin_version": primary.get("plugin_version"),
                "plugin_installed": primary.get("plugin_installed"),
                "connection_tested": primary.get("connection_tested"),
                "last_connection_checked_at": primary.get("last_connection_checked_at"),
                "last_signed_at": primary.get("last_signed_at"),
                "last_signed_post_id": primary.get("last_signed_post_id"),
                "last_signed_post_url": primary.get("last_signed_post_url"),
                "signed_post_count": primary.get("signed_post_count"),
                "last_verified_at": primary.get("last_verified_at"),
                "verified_post_count": primary.get("verified_post_count"),
                "last_verification_status": primary.get("last_verification_status"),
                "updated_at": primary.get("updated_at"),
            }
        )
    return summary


async def _get_org_add_ons(org_id: str, db: AsyncSession) -> dict:
    result = await db.execute(
        text("SELECT add_ons FROM organizations WHERE id = :org_id"),
        {"org_id": org_id},
    )
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    return row.add_ons if isinstance(row.add_ons, dict) else {}


async def _write_org_add_ons(org_id: str, db: AsyncSession, add_ons: dict) -> None:
    statement = text("UPDATE organizations SET add_ons = :add_ons WHERE id = :org_id").bindparams(
        bindparam("add_ons", type_=JSONB),
    )
    await db.execute(
        statement,
        {"org_id": org_id, "add_ons": add_ons},
    )
    await db.commit()


async def _get_wordpress_store(org_id: str, db: AsyncSession) -> dict:
    add_ons = await _get_org_add_ons(org_id, db)
    return _normalize_wordpress_store(add_ons.get("wordpress") if isinstance(add_ons.get("wordpress"), dict) else {})


async def _save_wordpress_store(org_id: str, db: AsyncSession, store: dict) -> dict:
    add_ons = await _get_org_add_ons(org_id, db)
    updated_add_ons = dict(add_ons)
    updated_add_ons["wordpress"] = _trim_wordpress_store(store)
    await _write_org_add_ons(org_id, db, updated_add_ons)
    return updated_add_ons["wordpress"]


def _upsert_install(store: dict, install_id: str, updates: dict) -> dict:
    installs = list(store.get("installs", []))
    existing_index = next((index for index, install in enumerate(installs) if install.get("install_id") == install_id), None)
    now = datetime.now(timezone.utc).isoformat()
    current = installs[existing_index] if existing_index is not None else {"install_id": install_id, "created_at": now}
    next_install = dict(current)
    next_install.update({key: value for key, value in updates.items() if value is not None})
    next_install["install_id"] = install_id
    next_install.setdefault("created_at", now)
    next_install["updated_at"] = now
    next_install.setdefault("signed_post_count", 0)
    next_install.setdefault("verified_post_count", 0)

    if next_install.get("is_primary"):
        installs = [{**install, "is_primary": False} for install in installs if install.get("install_id") != install_id]

    if existing_index is None:
        installs.append(next_install)
    else:
        installs[existing_index] = next_install

    store["installs"] = installs
    return next_install


async def _register_wordpress_install(org_id: str, db: AsyncSession, payload: WordPressInstallRegistrationPayload) -> dict:
    store = await _get_wordpress_store(org_id, db)
    install_id = _resolve_install_id(payload.install_id)
    install = _upsert_install(
        store,
        install_id,
        {
            "site_url": payload.site_url,
            "admin_url": payload.admin_url,
            "site_name": payload.site_name,
            "environment": payload.environment,
            "network_id": payload.network_id,
            "blog_id": payload.blog_id,
            "is_multisite": payload.is_multisite,
            "is_primary": payload.is_primary if payload.is_primary is not None else len(store.get("installs", [])) == 0,
            "plugin_version": payload.plugin_version,
            "plugin_installed": True,
            "organization_id": org_id,
        },
    )
    saved = await _save_wordpress_store(org_id, db, store)
    return _build_wordpress_summary(saved | {"installs": saved.get("installs", [])}) | {"registered_install": install}


async def _get_wordpress_status(org_id: str, db: AsyncSession) -> dict:
    store = await _get_wordpress_store(org_id, db)
    return _build_wordpress_summary(store)


async def _write_wordpress_status(org_id: str, db: AsyncSession, payload: WordPressIntegrationStatusPayload) -> dict:
    store = await _get_wordpress_store(org_id, db)
    install_id = _resolve_install_id(payload.install_id)
    _upsert_install(
        store,
        install_id,
        {
            "connection_status": payload.connection_status,
            "site_url": payload.site_url,
            "admin_url": payload.admin_url,
            "site_name": payload.site_name,
            "environment": payload.environment,
            "network_id": payload.network_id,
            "blog_id": payload.blog_id,
            "is_multisite": payload.is_multisite,
            "is_primary": payload.is_primary,
            "organization_id": payload.organization_id or org_id,
            "organization_name": payload.organization_name,
            "plugin_version": payload.plugin_version,
            "plugin_installed": payload.plugin_installed,
            "connection_tested": payload.connection_tested,
            "last_connection_checked_at": _parse_iso_datetime(payload.last_connection_checked_at),
            "last_signed_at": _parse_iso_datetime(payload.last_signed_at),
            "last_signed_post_id": payload.last_signed_post_id,
            "last_signed_post_url": payload.last_signed_post_url,
            "signed_post_count": payload.signed_post_count,
        },
    )
    saved = await _save_wordpress_store(org_id, db, store)
    return _build_wordpress_summary(saved)


async def _record_wordpress_verification_event(org_id: str, db: AsyncSession, payload: WordPressVerificationEventPayload) -> dict:
    store = await _get_wordpress_store(org_id, db)
    install = _upsert_install(
        store,
        payload.install_id,
        {
            "last_verified_at": _parse_iso_datetime(payload.verified_at) or datetime.now(timezone.utc).isoformat(),
            "last_verification_status": payload.status or ("verified" if payload.valid else "tampered" if payload.tampered else "failed"),
            "verified_post_count": next(
                (item.get("verified_post_count", 0) for item in store.get("installs", []) if item.get("install_id") == payload.install_id), 0
            )
            + 1,
        },
    )
    store.setdefault("recent_events", []).append(
        {
            "event_id": f"wpev_{uuid.uuid4().hex[:16]}",
            "type": "verification",
            "install_id": payload.install_id,
            "post_id": payload.post_id,
            "post_url": payload.post_url,
            "valid": payload.valid,
            "tampered": payload.tampered,
            "status": payload.status or install.get("last_verification_status"),
            "verified_at": _parse_iso_datetime(payload.verified_at) or datetime.now(timezone.utc).isoformat(),
            "source": payload.source,
        }
    )
    saved = await _save_wordpress_store(org_id, db, store)
    return _build_wordpress_summary(saved)


async def _queue_wordpress_action(org_id: str, db: AsyncSession, install_id: str, payload: WordPressActionQueuePayload, requested_by: str) -> dict:
    store = await _get_wordpress_store(org_id, db)
    if not any(install.get("install_id") == install_id for install in store.get("installs", [])):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="WordPress install not found")
    action = {
        "action_id": f"wpa_{uuid.uuid4().hex[:16]}",
        "install_id": install_id,
        "action_type": payload.action_type,
        "note": payload.note,
        "status": "queued",
        "requested_by": requested_by,
        "requested_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
        "result_message": None,
    }
    store.setdefault("remote_actions", []).append(action)
    saved = await _save_wordpress_store(org_id, db, store)
    return {"queued_action": action, **_build_wordpress_summary(saved)}


async def _pull_wordpress_actions(org_id: str, db: AsyncSession, install_id: str) -> dict:
    store = await _get_wordpress_store(org_id, db)
    actions = [action for action in store.get("remote_actions", []) if action.get("install_id") == install_id and action.get("status") == "queued"]
    return {"install_id": install_id, "actions": actions}


async def _ack_wordpress_action(org_id: str, db: AsyncSession, install_id: str, action_id: str, payload: WordPressActionAckPayload) -> dict:
    store = await _get_wordpress_store(org_id, db)
    updated_actions = []
    found = False
    for action in store.get("remote_actions", []):
        if action.get("install_id") == install_id and action.get("action_id") == action_id:
            found = True
            next_action = dict(action)
            next_action["status"] = payload.status
            next_action["result_message"] = payload.result_message
            next_action["completed_at"] = _parse_iso_datetime(payload.completed_at) or datetime.now(timezone.utc).isoformat()
            updated_actions.append(next_action)
        else:
            updated_actions.append(action)
    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="WordPress action not found")
    store["remote_actions"] = updated_actions
    saved = await _save_wordpress_store(org_id, db, store)
    return _build_wordpress_summary(saved)


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
    from app.core.pricing_constants import DEFAULT_COALITION_PUBLISHER_PERCENT
    from app.dependencies import DEMO_KEYS, _normalize_org_context
    from app.services.auth_service_client import auth_service_client

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


@router.get(
    "/integrations/wordpress/status",
    response_model=WordPressIntegrationStatusResponse,
    tags=["Integrations"],
    summary="Get WordPress integration status",
)
async def get_wordpress_integration_status(
    organization: dict = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
):
    org_id = organization["organization_id"]
    status_data = await _get_wordpress_status(org_id, db)
    return WordPressIntegrationStatusResponse(data=status_data)


@router.post(
    "/integrations/wordpress/status-sync",
    response_model=WordPressIntegrationStatusResponse,
    tags=["Integrations"],
    summary="Sync WordPress integration status",
)
async def sync_wordpress_integration_status(
    body: WordPressIntegrationStatusPayload,
    organization: dict = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
):
    org_id = organization["organization_id"]
    status_data = await _write_wordpress_status(org_id, db, body)
    return WordPressIntegrationStatusResponse(data=status_data)


@router.post(
    "/integrations/wordpress/register-install",
    response_model=WordPressIntegrationStatusResponse,
    tags=["Integrations"],
    summary="Register or update a WordPress install",
)
async def register_wordpress_install(
    body: WordPressInstallRegistrationPayload,
    organization: dict = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
):
    org_id = organization["organization_id"]
    status_data = await _register_wordpress_install(org_id, db, body)
    return WordPressIntegrationStatusResponse(data=status_data)


@router.post(
    "/integrations/wordpress/verification-event",
    response_model=WordPressIntegrationStatusResponse,
    tags=["Integrations"],
    summary="Record a WordPress verification event",
)
async def record_wordpress_verification_event(
    body: WordPressVerificationEventPayload,
    organization: dict = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
):
    org_id = organization["organization_id"]
    status_data = await _record_wordpress_verification_event(org_id, db, body)
    return WordPressIntegrationStatusResponse(data=status_data)


@router.post(
    "/integrations/wordpress/{install_id}/actions",
    response_model=WordPressIntegrationStatusResponse,
    tags=["Integrations"],
    summary="Queue a remote action for a WordPress install",
)
async def queue_wordpress_install_action(
    install_id: str,
    body: WordPressActionQueuePayload,
    organization: dict = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
):
    org_id = organization["organization_id"]
    requested_by = organization.get("organization_name") or org_id
    status_data = await _queue_wordpress_action(org_id, db, install_id, body, requested_by)
    return WordPressIntegrationStatusResponse(data=status_data)


@router.post(
    "/integrations/wordpress/{install_id}/actions/pull",
    response_model=WordPressIntegrationStatusResponse,
    tags=["Integrations"],
    summary="Pull queued remote actions for a WordPress install",
)
async def pull_wordpress_install_actions(
    install_id: str,
    organization: dict = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
):
    org_id = organization["organization_id"]
    action_data = await _pull_wordpress_actions(org_id, db, install_id)
    return WordPressIntegrationStatusResponse(data=action_data)


@router.post(
    "/integrations/wordpress/{install_id}/actions/{action_id}/ack",
    response_model=WordPressIntegrationStatusResponse,
    tags=["Integrations"],
    summary="Acknowledge a WordPress remote action result",
)
async def ack_wordpress_install_action(
    install_id: str,
    action_id: str,
    body: WordPressActionAckPayload,
    organization: dict = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
):
    org_id = organization["organization_id"]
    status_data = await _ack_wordpress_action(org_id, db, install_id, action_id, body)
    return WordPressIntegrationStatusResponse(data=status_data)


@router.post(
    "/integrations/wordpress/connect/start",
    response_model=WordPressConnectPollResponse,
    tags=["Integrations"],
    summary="Start a WordPress magic-link connect session",
)
async def start_wordpress_connect_session(
    body: WordPressConnectStartPayload,
):
    session_data = await _create_wordpress_connect_session(body)
    return WordPressConnectPollResponse(data=session_data)


@router.get(
    "/integrations/wordpress/connect/session/{session_id}",
    response_model=WordPressConnectPollResponse,
    tags=["Integrations"],
    summary="Poll a WordPress magic-link connect session",
)
async def poll_wordpress_connect_session(
    session_id: str,
):
    session_data = await _poll_wordpress_connect_session(session_id)
    return WordPressConnectPollResponse(data=session_data)


@router.post(
    "/integrations/wordpress/connect/complete",
    response_model=WordPressConnectPollResponse,
    tags=["Integrations"],
    summary="Complete a WordPress magic-link connect session",
)
async def complete_wordpress_connect_session(
    body: WordPressConnectCompletePayload,
    db: AsyncSession = Depends(get_db),
):
    session_data = await _complete_wordpress_connect_session(body.token, db)
    return WordPressConnectPollResponse(data=session_data)


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
    description=("Invalidate the current webhook token and generate a new one. You must update the webhook URL in Ghost after regenerating."),
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
    from app.database import content_session_factory, core_session_factory

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
