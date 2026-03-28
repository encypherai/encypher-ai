"""Claude Code investigation session trigger.

When a critical incident is detected, this module sends a signed webhook
to a configurable endpoint. The receiver starts a Claude Code session
that investigates the incident and posts updates back via the alert-service API.
"""

import hashlib
import hmac
import json
import logging
import time
from typing import Optional

import httpx

from ..core.config import settings
from ..db.models import Incident

logger = logging.getLogger(__name__)


def _sign_payload(payload: bytes, secret: str) -> str:
    """Compute HMAC-SHA256 signature for webhook authentication."""
    return hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()


async def trigger_investigation(incident: Incident, source: str = "auto") -> str:
    """Send a webhook to trigger a Claude Code investigation session.

    Args:
        incident: The incident to investigate.
        source: Who triggered it ("auto" for spike/critical, "discord" for slash command).

    Returns:
        "triggered", "no_webhook", or an error message.
    """
    if not settings.CC_WEBHOOK_URL:
        return "no_webhook"

    payload = {
        "event": "investigate",
        "incident_id": incident.id,
        "fingerprint": incident.fingerprint,
        "title": incident.title,
        "severity": incident.severity,
        "service_name": incident.service_name,
        "endpoint": incident.endpoint,
        "error_code": incident.error_code,
        "occurrence_count": incident.occurrence_count,
        "sample_error": (incident.sample_error or "")[:1000],
        "sample_stack": (incident.sample_stack or "")[:2000],
        "sample_request_id": incident.sample_request_id,
        "alert_service_url": settings.ALERT_SERVICE_URL,
        "source": source,
        "timestamp": int(time.time()),
    }

    payload_bytes = json.dumps(payload, sort_keys=True).encode()

    headers = {"Content-Type": "application/json"}
    if settings.CC_WEBHOOK_SECRET:
        signature = _sign_payload(payload_bytes, settings.CC_WEBHOOK_SECRET)
        headers["X-Signature-256"] = f"sha256={signature}"

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                settings.CC_WEBHOOK_URL,
                content=payload_bytes,
                headers=headers,
            )

        if response.status_code in (200, 201, 202):
            logger.info(
                "CC investigation triggered for incident %s (source=%s)",
                incident.id[:8],
                source,
            )
            return "triggered"
        else:
            msg = f"HTTP {response.status_code}: {response.text[:200]}"
            logger.warning("CC webhook failed: %s", msg)
            return msg

    except Exception as exc:
        msg = str(exc)[:200]
        logger.error("CC webhook error: %s", msg)
        return msg


async def trigger_if_critical(incident: Incident) -> Optional[str]:
    """Trigger CC investigation only for critical incidents.

    Called automatically when a new incident is created.
    Returns the trigger result or None if not critical.
    """
    if incident.severity != "critical":
        return None
    if not settings.CC_AUTO_INVESTIGATE:
        return None
    return await trigger_investigation(incident, source="auto")
