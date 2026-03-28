#!/usr/bin/env python3
"""Claude Code investigation webhook receiver.

Run this on a machine where Claude Code CLI is available.
It listens for webhooks from the alert-service and starts
CC sessions to investigate incidents.

Usage:
    # Set required env vars
    export CC_WEBHOOK_SECRET="your-shared-secret"  # pragma: allowlist secret
    export ALERT_SERVICE_URL="https://alert-service-production.up.railway.app"

    # Optional
    export CC_RECEIVER_PORT=9090
    export CC_PROJECT_DIR="/path/to/encypherai-commercial"
    export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."

    # Run
    python cc_webhook_receiver.py
"""

import hashlib
import hmac
import json
import logging
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("cc-receiver")

WEBHOOK_SECRET = os.environ.get("CC_WEBHOOK_SECRET", "")
ALERT_SERVICE_URL = os.environ.get("ALERT_SERVICE_URL", "http://localhost:8011")
PROJECT_DIR = os.environ.get("CC_PROJECT_DIR", os.getcwd())
RECEIVER_PORT = int(os.environ.get("CC_RECEIVER_PORT", "9090"))
MAX_CONCURRENT = int(os.environ.get("CC_MAX_CONCURRENT", "2"))

_active_investigations: dict[str, threading.Thread] = {}
_lock = threading.Lock()


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

    prompt = f"""You are investigating an incident detected by the Encypher alert-service.

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
If the issue is transient (e.g., a dependency timeout), note that and recommend monitoring.
"""
    return prompt


def run_investigation(data: dict) -> None:
    """Run a Claude Code investigation in a subprocess."""
    incident_id = data.get("incident_id", "unknown")
    short_id = incident_id[:8]

    logger.info("Starting CC investigation for %s", short_id)

    prompt = build_investigation_prompt(data)

    try:
        result = subprocess.run(
            ["claude", "--print", "--dangerously-skip-permissions", "-p", prompt],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        if result.returncode == 0:
            logger.info("CC investigation completed for %s", short_id)
            # Post the final result as an investigation update
            _post_update(
                data,
                f"Investigation complete.\n\n{result.stdout[-1500:] if len(result.stdout) > 1500 else result.stdout}",
            )
        else:
            logger.error("CC investigation failed for %s: %s", short_id, result.stderr[:500])
            _post_update(data, f"Investigation failed: {result.stderr[:500]}")

    except subprocess.TimeoutExpired:
        logger.warning("CC investigation timed out for %s", short_id)
        _post_update(data, "Investigation timed out after 5 minutes.")
    except FileNotFoundError:
        logger.error("Claude Code CLI not found. Install it: npm install -g @anthropic-ai/claude-code")
        _post_update(data, "Investigation failed: Claude Code CLI not found on this machine.")
    except Exception as exc:
        logger.error("CC investigation error for %s: %s", short_id, exc)
        _post_update(data, f"Investigation error: {str(exc)[:300]}")
    finally:
        with _lock:
            _active_investigations.pop(incident_id, None)


def _post_update(data: dict, message: str) -> None:
    """Post an investigation update back to the alert-service."""
    import urllib.request

    alert_url = data.get("alert_service_url", ALERT_SERVICE_URL)
    incident_id = data.get("incident_id", "unknown")
    url = f"{alert_url}/api/v1/alerts/incidents/{incident_id}/investigate"

    payload = json.dumps({"message": message}).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            logger.info("Posted update for %s: HTTP %d", incident_id[:8], resp.status)
    except Exception as exc:
        logger.error("Failed to post update for %s: %s", incident_id[:8], exc)


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
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "already_running"}).encode())
                return

            if len(_active_investigations) >= MAX_CONCURRENT:
                self.send_response(429)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "too_many_investigations"}).encode())
                return

            thread = threading.Thread(
                target=run_investigation,
                args=(data,),
                name=f"cc-{incident_id[:8]}",
                daemon=True,
            )
            _active_investigations[incident_id] = thread

        thread.start()

        self.send_response(202)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "accepted", "incident_id": incident_id}).encode())

    def do_GET(self):
        """Health check and active investigation status."""
        with _lock:
            active = list(_active_investigations.keys())

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(
            json.dumps(
                {
                    "status": "running",
                    "active_investigations": len(active),
                    "investigation_ids": [i[:8] for i in active],
                    "max_concurrent": MAX_CONCURRENT,
                }
            ).encode()
        )

    def log_message(self, format, *args):
        logger.info(format, *args)


def main():
    logger.info("CC Webhook Receiver starting on port %d", RECEIVER_PORT)
    logger.info("Project dir: %s", PROJECT_DIR)
    logger.info("Alert service: %s", ALERT_SERVICE_URL)
    logger.info("Max concurrent: %d", MAX_CONCURRENT)
    if not WEBHOOK_SECRET:
        logger.warning("CC_WEBHOOK_SECRET not set - webhooks will not be authenticated!")

    server = HTTPServer(("0.0.0.0", RECEIVER_PORT), WebhookHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        server.server_close()


if __name__ == "__main__":
    main()
