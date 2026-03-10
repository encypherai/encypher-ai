"""
Cloudflare Logpush ingestion service.

Parses NDJSON Cloudflare HTTP access logs, classifies bot user-agents,
detects robots.txt/RSL bypass, and writes ContentDetectionEvent rows.

Cloudflare Logpush HTTP request log fields used:
    ClientIP                 - visitor IP
    ClientRequestHost        - hostname
    ClientRequestURI         - path + query string
    ClientRequestMethod      - HTTP method
    ClientRequestUserAgent   - User-Agent header
    EdgeStartTimestamp       - Unix nanoseconds (int) or ISO-8601 string
    EdgeResponseStatus       - HTTP response status code
    ZoneName                 - Cloudflare zone (domain)

The webhook endpoint receives a POST body containing one JSON object per
newline (NDJSON). Each line is parsed independently; malformed lines are
counted as errors and skipped.
"""

import json
import logging
import re
from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cdn_attribution_event import CdnAttributionEvent
from app.models.cdn_image_record import CdnImageRecord  # noqa: F401  (used for future URL lookup)
from app.models.rights import ContentDetectionEvent, KnownCrawler
from app.schemas.cdn_schemas import LogpushIngestResult
from app.services.metrics_service import classify_bot

logger = logging.getLogger(__name__)

# Paths we skip because they are not content access events.
_SKIP_PATH_PREFIXES = (
    "/robots.txt",
    "/sitemap",
    "/favicon",
    "/.well-known",
    "/api/",
    "/_next/",
    "/static/",
    "/assets/",
)

# HTTP methods that indicate a scrape (not just a preflight or resource fetch)
_CONTENT_METHODS = {"GET", "HEAD"}

# Window used when checking for prior RSL OLP token requests
_BYPASS_WINDOW_HOURS = 24


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _parse_timestamp(raw: str | int | None) -> datetime | None:
    """Convert Cloudflare EdgeStartTimestamp to a UTC datetime.

    Cloudflare sends either a Unix nanosecond integer or an ISO-8601 string
    depending on the Logpush job format configuration.
    """
    if raw is None:
        return None
    try:
        if isinstance(raw, int):
            # Nanoseconds -> seconds
            return datetime.fromtimestamp(raw / 1e9, tz=timezone.utc)
        # Try ISO-8601 string
        return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except (ValueError, OSError, OverflowError):
        return None


def parse_logpush_line(line: str) -> dict | None:
    """Parse a single Cloudflare Logpush NDJSON line.

    Returns a normalised dict with keys:
        client_ip, host, uri, method, user_agent, status, timestamp, domain

    Returns None if the line is empty, malformed, or should be skipped.
    """
    line = line.strip()
    if not line:
        return None
    try:
        record = json.loads(line)
    except json.JSONDecodeError:
        return None

    method = record.get("ClientRequestMethod", "").upper()
    if method not in _CONTENT_METHODS:
        return None

    uri = record.get("ClientRequestURI", "")
    for prefix in _SKIP_PATH_PREFIXES:
        if uri.startswith(prefix):
            return None

    host = record.get("ClientRequestHost") or record.get("ZoneName") or ""
    timestamp = _parse_timestamp(record.get("EdgeStartTimestamp"))

    return {
        "client_ip": record.get("ClientIP"),
        "host": host,
        "uri": uri,
        "method": method,
        "user_agent": record.get("ClientRequestUserAgent", ""),
        "status": record.get("EdgeResponseStatus"),
        "timestamp": timestamp,
        "domain": host,
    }


async def _has_recent_rsl_check(
    db: AsyncSession,
    organization_id: str,
    bot_category: str,
    window_hours: int = _BYPASS_WINDOW_HOURS,
) -> bool:
    """Return True if this bot category has an RSL OLP check event in the
    last *window_hours* for *organization_id*.

    An RSL OLP check is represented by a ContentDetectionEvent with
    detection_source == 'rsl_olp_check'.
    """
    cutoff = _utcnow() - timedelta(hours=window_hours)
    result = await db.execute(
        select(func.count(ContentDetectionEvent.id)).where(
            and_(
                ContentDetectionEvent.organization_id == organization_id,
                ContentDetectionEvent.user_agent_category == bot_category,
                ContentDetectionEvent.detection_source == "rsl_olp_check",
                ContentDetectionEvent.created_at >= cutoff,
            )
        )
    )
    count: int = result.scalar_one() or 0
    return count > 0


async def _get_rsl_respecting_categories(db: AsyncSession) -> set[str]:
    """Return the set of crawler_type values where respects_rsl is True.

    These are the crawlers that *claim* to follow robots.txt / RSL, so a
    bypass is meaningful for them. Bots that never claimed compliance are
    not flagged as bypass events.
    """
    result = await db.execute(select(KnownCrawler.crawler_type).where(KnownCrawler.respects_rsl.is_(True)))
    return {row[0] for row in result.all()}


async def _maybe_record_image_attribution(
    db: AsyncSession,
    organization_id: str,
    host: str,
    uri: str,
    status: int | None,
    client_ip: str | None,
) -> None:
    """Best-effort: record image attribution event if URI looks like an image."""
    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif", ".tiff"}
    IMAGE_PATH_HINTS = ("/images/", "/img/", "/photos/", "/media/", "/cdn-cgi/image/")

    lower_uri = uri.lower()
    is_image = any(lower_uri.endswith(ext) for ext in IMAGE_EXTENSIONS) or any(hint in lower_uri for hint in IMAGE_PATH_HINTS)
    if not is_image:
        return

    # Strip /cdn-cgi/image/{opts}/ prefix
    canonical_uri = re.sub(r"^/cdn-cgi/image/[^/]+/", "/", uri)
    canonical_url = f"https://{host}{canonical_uri}" if host else canonical_uri
    full_url = f"https://{host}{uri}" if host else uri

    event = CdnAttributionEvent(
        organization_id=organization_id,
        image_url=full_url[:2048],
        canonical_url=canonical_url[:2048],
        http_status=status,
        client_ip=client_ip[:64] if client_ip else None,
    )
    db.add(event)


async def ingest_logpush_batch(
    organization_id: str,
    body: bytes,
    db: AsyncSession,
) -> LogpushIngestResult:
    """Parse a Cloudflare Logpush NDJSON body and write detection events.

    For each log line:
    1. Parse the record (skip non-content methods, static assets, API calls)
    2. Classify the user-agent via classify_bot()
    3. Skip non-bot traffic (unknown or human_browser categories)
    4. If the bot category claims RSL compliance, check for a prior RSL OLP
       token request within the last 24 h. Absence = bypass.
    5. Write a ContentDetectionEvent row.

    Returns a LogpushIngestResult summary.
    """
    lines_received = 0
    bots_detected = 0
    bypass_flags = 0
    events_created = 0
    errors = 0

    try:
        text_body = body.decode("utf-8", errors="replace")
    except Exception:
        logger.warning("logpush: could not decode body for org=%s", organization_id)
        return LogpushIngestResult(
            lines_received=0,
            bots_detected=0,
            bypass_flags=0,
            events_created=0,
            errors=1,
        )

    lines = text_body.splitlines()
    lines_received = len(lines)

    if not lines:
        return LogpushIngestResult(
            lines_received=0,
            bots_detected=0,
            bypass_flags=0,
            events_created=0,
            errors=0,
        )

    # Pre-fetch the set of RSL-respecting crawler categories once per batch
    rsl_respecting = await _get_rsl_respecting_categories(db)
    # Cache RSL check results per category within this batch to avoid N+1 queries
    rsl_check_cache: dict[str, bool] = {}

    for line in lines:
        try:
            parsed = parse_logpush_line(line)
            if parsed is None:
                continue

            user_agent = parsed["user_agent"]
            bot_category = classify_bot(user_agent)

            # Skip non-bot / human traffic
            if bot_category == "unknown":
                continue

            bots_detected += 1

            # Bypass detection: only meaningful for bots claiming RSL compliance
            robots_txt_bypassed: bool | None = None
            if bot_category in rsl_respecting:
                if bot_category not in rsl_check_cache:
                    rsl_check_cache[bot_category] = await _has_recent_rsl_check(db, organization_id, bot_category)
                had_rsl_check = rsl_check_cache[bot_category]
                robots_txt_bypassed = not had_rsl_check
                if robots_txt_bypassed:
                    bypass_flags += 1

            # Build detected_on_url from host + URI
            host = parsed["domain"] or ""
            uri = parsed["uri"] or ""
            detected_url = f"https://{host}{uri}" if host else uri

            event = ContentDetectionEvent(
                organization_id=organization_id,
                detection_source="cloudflare_logpush",
                detected_on_url=detected_url[:2048] if detected_url else None,
                detected_on_domain=host or None,
                requester_ip=parsed["client_ip"],
                requester_user_agent=user_agent[:512] if user_agent else None,
                user_agent_category=bot_category,
                rights_served=False,
                rights_acknowledged=False,
                robots_txt_bypassed=robots_txt_bypassed,
                created_at=parsed["timestamp"] or _utcnow(),
            )
            db.add(event)
            events_created += 1

            # Best-effort image attribution tracking for 2xx responses
            status_code = parsed.get("status")
            if status_code is not None and 200 <= int(status_code) < 300:
                try:
                    await _maybe_record_image_attribution(
                        db=db,
                        organization_id=organization_id,
                        host=parsed["domain"] or "",
                        uri=parsed["uri"] or "",
                        status=status_code,
                        client_ip=parsed.get("client_ip"),
                    )
                except Exception:
                    logger.debug(
                        "logpush: image attribution error for org=%s",
                        organization_id,
                        exc_info=True,
                    )

        except Exception:
            logger.debug(
                "logpush: error processing line for org=%s",
                organization_id,
                exc_info=True,
            )
            errors += 1

    if events_created:
        await db.flush()

    return LogpushIngestResult(
        lines_received=lines_received,
        bots_detected=bots_detected,
        bypass_flags=bypass_flags,
        events_created=events_created,
        errors=errors,
    )
