"""Discord webhook notification sender."""

import logging
from datetime import datetime
from typing import Optional

import httpx

from ..core.config import settings
from ..db.models import Incident, NotificationLog

logger = logging.getLogger(__name__)

_SEVERITY_COLORS = {
    "critical": 0xFF0000,  # Red
    "warning": 0xFFA500,  # Orange
    "info": 0x3498DB,  # Blue
}

_SEVERITY_EMOJI = {
    "critical": "RED CIRCLE",
    "warning": "WARNING",
    "info": "INFO",
}


async def notify_new_incident(incident: Incident, db_session) -> Optional[str]:
    """Send a Discord embed for a new incident."""
    if not settings.DISCORD_WEBHOOK_URL:
        return None

    color = _SEVERITY_COLORS.get(incident.severity, 0x808080)

    embed = {
        "title": incident.title[:256],
        "color": color,
        "fields": [
            {"name": "Service", "value": incident.service_name or "unknown", "inline": True},
            {"name": "Severity", "value": incident.severity.upper(), "inline": True},
            {"name": "Error Code", "value": incident.error_code or "N/A", "inline": True},
            {"name": "Endpoint", "value": incident.endpoint or "N/A", "inline": False},
        ],
        "timestamp": datetime.utcnow().isoformat(),
        "footer": {"text": f"Incident {incident.id}"},
    }

    if incident.sample_error:
        error_preview = incident.sample_error[:500]
        embed["fields"].append({"name": "Error", "value": f"```\n{error_preview}\n```", "inline": False})

    if incident.sample_request_id:
        embed["fields"].append({"name": "Request ID", "value": incident.sample_request_id, "inline": True})

    if incident.sample_organization_id:
        embed["fields"].append({"name": "Org ID", "value": incident.sample_organization_id, "inline": True})

    payload = {"embeds": [embed]}
    return await _send_discord(payload, incident.id, "new_incident", db_session)


async def notify_spike(
    service_name: str,
    recent_count: int,
    prev_count: int,
    top_errors: list[dict],
    db_session,
) -> Optional[str]:
    """Send a Discord embed for an error rate spike."""
    if not settings.DISCORD_WEBHOOK_URL:
        return None

    multiplier = recent_count / max(prev_count, 1)
    top_list = "\n".join(f"- {e.get('error_code', 'unknown')}: {e.get('count', 0)}x" for e in top_errors[:5])

    embed = {
        "title": f"Error Spike Detected: {service_name or 'all services'}",
        "color": 0xFF4500,
        "fields": [
            {"name": "Last 5 min", "value": str(recent_count), "inline": True},
            {"name": "Previous 5 min", "value": str(prev_count), "inline": True},
            {"name": "Increase", "value": f"{multiplier:.1f}x", "inline": True},
        ],
        "timestamp": datetime.utcnow().isoformat(),
        "footer": {"text": "alert-service spike detector"},
    }

    if top_list:
        embed["fields"].append({"name": "Top Errors", "value": top_list, "inline": False})

    payload = {"embeds": [embed]}
    return await _send_discord(payload, None, "spike", db_session)


async def notify_alertmanager(alert_name: str, severity: str, summary: str, description: str, labels: dict, db_session) -> Optional[str]:
    """Send a Discord embed for a Prometheus/Alertmanager alert."""
    if not settings.DISCORD_WEBHOOK_URL:
        return None

    color = _SEVERITY_COLORS.get(severity, 0x808080)
    service = labels.get("job", labels.get("instance", "unknown"))

    embed = {
        "title": f"[Prometheus] {alert_name}",
        "description": summary,
        "color": color,
        "fields": [
            {"name": "Service", "value": service, "inline": True},
            {"name": "Severity", "value": severity.upper(), "inline": True},
        ],
        "timestamp": datetime.utcnow().isoformat(),
        "footer": {"text": "Prometheus Alertmanager"},
    }

    if description and description != summary:
        embed["fields"].append({"name": "Details", "value": description[:500], "inline": False})

    payload = {"embeds": [embed]}
    return await _send_discord(payload, None, "alertmanager", db_session)


async def notify_investigation_update(incident_id: str, message: str, db_session) -> Optional[str]:
    """Post an investigation progress update to Discord."""
    if not settings.DISCORD_WEBHOOK_URL:
        return None

    payload = {"content": f"**Investigation Update** (`{incident_id}`)\n{message}"}
    return await _send_discord(payload, incident_id, "investigation_update", db_session)


async def _send_discord(payload: dict, incident_id: Optional[str], event_type: str, db_session) -> Optional[str]:
    """Send a payload to the Discord webhook."""
    log_entry = NotificationLog(
        incident_id=incident_id,
        channel="discord",
        status="pending",
        payload=payload,
    )

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(settings.DISCORD_WEBHOOK_URL, json=payload)

        if response.status_code in (200, 204):
            log_entry.status = "sent"
            logger.info("Discord notification sent: %s (incident=%s)", event_type, incident_id)
        else:
            log_entry.status = "failed"
            log_entry.error_message = f"HTTP {response.status_code}: {response.text[:500]}"
            logger.warning("Discord notification failed: HTTP %d", response.status_code)
    except Exception as exc:
        log_entry.status = "failed"
        log_entry.error_message = str(exc)[:500]
        logger.error("Discord notification error: %s", exc)

    if db_session:
        db_session.add(log_entry)
        db_session.commit()

    return log_entry.status
