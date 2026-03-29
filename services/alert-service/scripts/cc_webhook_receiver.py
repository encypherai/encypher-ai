#!/usr/bin/env python3
"""Claude Code investigation webhook receiver.

Receives webhooks from the alert-service and launches investigation
sessions via AgentDesk (claude-chat-manager). Each investigation runs
as a managed tmux session visible in the AgentDesk UI.

Usage:
    # Set required env vars
    export CC_WEBHOOK_SECRET="your-shared-secret"  # pragma: allowlist secret
    export ALERT_SERVICE_URL="https://alert-service-production-8e3b.up.railway.app"
    export AGENTDESK_URL="https://localhost:2222"
    export AGENTDESK_USERNAME="developer"
    export AGENTDESK_PASSWORD="your-password"  # pragma: allowlist secret

    # Optional
    export CC_RECEIVER_PORT=2225
    export CC_MAX_CONCURRENT=2
    export AGENTDESK_COMPANY_ID="cd54680f-db82-437c-8902-6e7bea00d2c7"
    export AGENTDESK_AGENT_ID="db31e77d-015d-4376-a63f-c67ee1625057"

    # Run
    python cc_webhook_receiver.py
"""

import hashlib
import hmac
import json
import logging
import os
import ssl
import subprocess
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("cc-receiver")

WEBHOOK_SECRET = os.environ.get("CC_WEBHOOK_SECRET", "")
ALERT_SERVICE_URL = os.environ.get("ALERT_SERVICE_URL", "http://localhost:8011")
AGENTDESK_URL = os.environ.get("AGENTDESK_URL", "https://localhost:2222")
AGENTDESK_USERNAME = os.environ.get("AGENTDESK_USERNAME", "encypher-ops-bot")
AGENTDESK_PASSWORD = os.environ.get("AGENTDESK_PASSWORD", "")
AGENTDESK_COMPANY_ID = os.environ.get("AGENTDESK_COMPANY_ID", "cd54680f-db82-437c-8902-6e7bea00d2c7")
AGENTDESK_AGENT_ID = os.environ.get("AGENTDESK_AGENT_ID", "97843438-0f13-4464-8d60-b8df68a7698b")
RECEIVER_PORT = int(os.environ.get("CC_RECEIVER_PORT", "2225"))
MAX_CONCURRENT = int(os.environ.get("CC_MAX_CONCURRENT", "2"))

_active_investigations: dict[str, str] = {}  # incident_id -> agentdesk session_id
_lock = threading.Lock()
REAPER_INTERVAL = int(os.environ.get("CC_REAPER_INTERVAL", "30"))  # seconds

# Trust local self-signed certs from AgentDesk
_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode = ssl.CERT_NONE

_auth_cookie: str | None = None


def _agentdesk_login() -> str:
    """Authenticate with AgentDesk and return the JWT cookie value."""
    global _auth_cookie
    url = f"{AGENTDESK_URL}/api/auth/login"
    payload = json.dumps({"username": AGENTDESK_USERNAME, "password": AGENTDESK_PASSWORD}).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")

    resp = urllib.request.urlopen(req, timeout=10, context=_ssl_ctx)
    cookie_header = resp.headers.get("Set-Cookie", "")
    for part in cookie_header.split(";"):
        part = part.strip()
        if part.startswith("ccm-token="):
            _auth_cookie = part.split("=", 1)[1]
            logger.info("AgentDesk login successful")
            return _auth_cookie

    raise RuntimeError("AgentDesk login succeeded but no cookie returned")


def _get_cookie() -> str:
    """Get a valid auth cookie, logging in if needed."""
    global _auth_cookie
    if _auth_cookie:
        return _auth_cookie
    return _agentdesk_login()


def verify_signature(payload: bytes, signature: str) -> bool:
    """Verify HMAC-SHA256 signature from alert-service."""
    if not WEBHOOK_SECRET:
        logger.warning("CC_WEBHOOK_SECRET not set - accepting all webhooks")
        return True
    if not signature.startswith("sha256="):
        return False
    expected = hmac.new(WEBHOOK_SECRET.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature[7:], expected)


def build_investigation_prompt(data: dict) -> str:
    """Build a Claude Code prompt for investigating an incident."""
    alert_url = data.get("alert_service_url", ALERT_SERVICE_URL)

    return f"""You are investigating a production incident detected by the Encypher alert-service.

INCIDENT DETAILS:
- ID: {data.get('incident_id', 'unknown')}
- Title: {data.get('title', 'unknown')}
- Severity: {data.get('severity', 'unknown')}
- Service: {data.get('service_name', 'unknown')}
- Endpoint: {data.get('endpoint', 'N/A')}
- Error Code: {data.get('error_code', 'N/A')}
- Occurrences: {data.get('occurrence_count', 0)}
- Source: {data.get('source', 'auto')}

SAMPLE ERROR:
{data.get('sample_error', 'No error message available')}

SAMPLE STACK TRACE:
{data.get('sample_stack', 'No stack trace available')}

REQUEST ID: {data.get('sample_request_id', 'N/A')}

INVESTIGATION STEPS:
1. Read the service code for {data.get('service_name', 'the affected service')} to understand the error path
2. Check if this is a code bug, configuration issue, or external dependency failure
3. Look at recent git commits for the affected service to see if a recent change caused this
4. Check the error pattern - is it a known issue type or something new?
5. Formulate a diagnosis and recommended fix

POST UPDATES:
Use curl to post investigation updates to Discord via the alert-service:
  curl -X POST {alert_url}/api/v1/alerts/incidents/{data.get('incident_id', 'INCIDENT_ID')}/investigate \\
    -H "Content-Type: application/json" \\
    -d '{{"message": "YOUR UPDATE HERE"}}'

Post at least two updates:
1. When you start and what you are looking at
2. Your diagnosis and recommended fix

If you determine a fix is needed, describe it clearly but do NOT apply it automatically.
If the issue is transient (e.g., a dependency timeout), note that and recommend monitoring."""


def launch_agentdesk_session(data: dict) -> str | None:
    """Launch an investigation session via AgentDesk API.

    Returns the session ID if successful, None otherwise.
    """
    incident_id = data.get("incident_id", "unknown")
    short_id = incident_id[:8]
    prompt = build_investigation_prompt(data)

    url = f"{AGENTDESK_URL}/api/companies/{AGENTDESK_COMPANY_ID}/agents/{AGENTDESK_AGENT_ID}/session"
    payload = json.dumps({"message": prompt}).encode()

    for attempt in range(2):
        cookie = _get_cookie()
        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Cookie": f"ccm-token={cookie}",
            },
            method="POST",
        )

        try:
            resp = urllib.request.urlopen(req, timeout=30, context=_ssl_ctx)
            # AgentDesk returns SSE stream - read the first few events to get session ID
            session_id = None
            for line in resp:
                line = line.decode("utf-8", errors="replace").strip()
                if line.startswith("data: "):
                    try:
                        event = json.loads(line[6:])
                        if event.get("type") == "session_id":
                            session_id = event.get("sessionId")
                            break
                        if "sessionId" in event:
                            session_id = event["sessionId"]
                            break
                    except json.JSONDecodeError:
                        continue
            resp.close()

            if session_id:
                logger.info("AgentDesk session started for %s: %s", short_id, session_id)
                return session_id
            else:
                logger.warning("AgentDesk session started for %s but no session ID returned", short_id)
                return "unknown"

        except urllib.error.HTTPError as e:
            if e.code == 401 and attempt == 0:
                logger.info("AgentDesk cookie expired, re-authenticating...")
                global _auth_cookie
                _auth_cookie = None
                continue
            logger.error("AgentDesk API error for %s: HTTP %d", short_id, e.code)
            return None
        except Exception as exc:
            logger.error("AgentDesk session launch error for %s: %s", short_id, exc)
            return None

    return None


def _post_alert_update(data: dict, message: str) -> None:
    """Post an investigation update back to the alert-service."""
    alert_url = data.get("alert_service_url", ALERT_SERVICE_URL)
    incident_id = data.get("incident_id", "unknown")
    url = f"{alert_url}/api/v1/alerts/incidents/{incident_id}/investigate"

    payload = json.dumps({"message": message}).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            logger.info("Posted alert update for %s: HTTP %d", incident_id[:8], resp.status)
    except Exception as exc:
        logger.error("Failed to post alert update for %s: %s", incident_id[:8], exc)


class WebhookHandler(BaseHTTPRequestHandler):
    """HTTP handler for incoming investigation webhooks."""

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 100_000:
            self.send_error(413, "Payload too large")
            return

        body = self.rfile.read(content_length)

        # Verify signature
        signature = self.headers.get("X-Signature-256", "")
        if WEBHOOK_SECRET and not verify_signature(body, signature):
            logger.warning("Invalid webhook signature from %s", self.client_address[0])
            self.send_error(401, "Invalid signature")
            return

        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return

        event = data.get("event")
        if event != "investigate":
            self.send_error(400, f"Unknown event: {event}")
            return

        incident_id = data.get("incident_id", "unknown")

        with _lock:
            if incident_id in _active_investigations:
                self._json_response(200, {"status": "already_running", "session_id": _active_investigations[incident_id]})
                return

            if len(_active_investigations) >= MAX_CONCURRENT:
                self._json_response(429, {"status": "too_many_investigations"})
                return

        # Launch session via AgentDesk (blocking but fast - just starts the session)
        session_id = launch_agentdesk_session(data)

        if session_id:
            with _lock:
                _active_investigations[incident_id] = session_id
            _post_alert_update(data, f"Investigation session launched (AgentDesk: {session_id[:12] if len(session_id) > 12 else session_id})")
            self._json_response(202, {"status": "accepted", "incident_id": incident_id, "session_id": session_id})
        else:
            self._json_response(500, {"status": "failed", "error": "Could not start AgentDesk session"})

    def do_GET(self):
        """Health check and active investigation status."""
        with _lock:
            active = dict(_active_investigations)

        self._json_response(
            200,
            {
                "status": "running",
                "active_investigations": len(active),
                "investigations": {k[:8]: v for k, v in active.items()},
                "max_concurrent": MAX_CONCURRENT,
            },
        )

    def do_DELETE(self):
        """Clear a completed investigation from tracking."""
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length else b"{}"
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return

        incident_id = data.get("incident_id", "")
        with _lock:
            removed = _active_investigations.pop(incident_id, None)

        if removed:
            self._json_response(200, {"status": "removed", "incident_id": incident_id})
        else:
            self._json_response(404, {"status": "not_found"})

    def _json_response(self, code: int, data: dict) -> None:
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        logger.info(format, *args)


def _get_live_ccm_sessions() -> set[str]:
    """Return the set of active ccm-* tmux session names."""
    try:
        result = subprocess.run(
            ["tmux", "list-sessions", "-F", "#{session_name}"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return {s for s in result.stdout.strip().splitlines() if s.startswith("ccm-")}
    except Exception:
        return set()


def _reaper_loop() -> None:
    """Periodically remove finished investigations from the tracking dict."""
    while True:
        time.sleep(REAPER_INTERVAL)
        try:
            live_sessions = _get_live_ccm_sessions()
            with _lock:
                to_remove = []
                for incident_id, session_id in _active_investigations.items():
                    # AgentDesk session IDs match tmux session names (ccm-<timestamp>)
                    tmux_name = f"ccm-{session_id}" if not session_id.startswith("ccm-") else session_id
                    if tmux_name not in live_sessions and session_id != "unknown":
                        to_remove.append(incident_id)
                    elif session_id == "unknown" and not live_sessions:
                        to_remove.append(incident_id)

                for incident_id in to_remove:
                    removed = _active_investigations.pop(incident_id, None)
                    logger.info("Reaped finished investigation: %s (session: %s)", incident_id[:8], removed)
        except Exception as exc:
            logger.error("Reaper error: %s", exc)


def main():
    logger.info("CC Webhook Receiver starting on port %d", RECEIVER_PORT)
    logger.info("AgentDesk: %s (agent: %s)", AGENTDESK_URL, AGENTDESK_AGENT_ID)
    logger.info("Alert service: %s", ALERT_SERVICE_URL)
    logger.info("Max concurrent: %d", MAX_CONCURRENT)
    if not WEBHOOK_SECRET:
        logger.warning("CC_WEBHOOK_SECRET not set - webhooks will not be authenticated!")
    if not AGENTDESK_PASSWORD:
        logger.error("AGENTDESK_PASSWORD not set - cannot authenticate with AgentDesk!")

    # Pre-authenticate
    try:
        _agentdesk_login()
    except Exception as exc:
        logger.error("Initial AgentDesk login failed: %s (will retry on first webhook)", exc)

    # Start reaper thread to clean up finished investigations
    reaper = threading.Thread(target=_reaper_loop, daemon=True)
    reaper.start()
    logger.info("Investigation reaper started (interval=%ds)", REAPER_INTERVAL)

    server = HTTPServer(("0.0.0.0", RECEIVER_PORT), WebhookHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        server.server_close()


if __name__ == "__main__":
    main()
