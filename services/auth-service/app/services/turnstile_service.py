"""Cloudflare Turnstile verification helper."""

from __future__ import annotations

import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


async def verify_turnstile_token(token: str | None, remote_ip: str | None = None) -> bool:
    """Verify a Turnstile token against Cloudflare.

    Returns True when Turnstile is disabled to avoid blocking local/dev flows.
    """
    if not settings.TURNSTILE_ENABLED:
        return True

    if not token:
        return False

    if not settings.TURNSTILE_SECRET_KEY:
        logger.warning("turnstile_enabled_but_secret_missing")
        return False

    payload: dict[str, str] = {
        "secret": settings.TURNSTILE_SECRET_KEY,
        "response": token,
    }
    if remote_ip:
        payload["remoteip"] = remote_ip

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(settings.TURNSTILE_VERIFY_URL, data=payload)
    except httpx.RequestError as exc:
        logger.warning("turnstile_request_failed", extra={"error": str(exc)})
        return False

    if response.status_code != 200:
        return False

    data = response.json()
    return bool(isinstance(data, dict) and data.get("success") is True)
