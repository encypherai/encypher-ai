"""Background pattern detection: spike detection and auto-resolution."""

import asyncio
import logging
from datetime import datetime, timedelta

from sqlalchemy import func

from ..core.config import settings
from ..db.models import AlertEvent
from ..db.session import SessionLocal
from .discord_notifier import notify_spike
from .incident_service import auto_resolve_stale_incidents

logger = logging.getLogger(__name__)

_task: asyncio.Task = None


async def start_pattern_detector() -> None:
    global _task
    if _task is not None:
        return
    _task = asyncio.create_task(_detection_loop())
    logger.info("Pattern detector started (interval=%ds)", settings.PATTERN_CHECK_INTERVAL_SECONDS)


async def stop_pattern_detector() -> None:
    global _task
    if _task:
        _task.cancel()
        try:
            await _task
        except asyncio.CancelledError:
            pass
        _task = None
    logger.info("Pattern detector stopped")


async def _detection_loop() -> None:
    while True:
        try:
            await asyncio.sleep(settings.PATTERN_CHECK_INTERVAL_SECONDS)
            db = SessionLocal()
            try:
                await _check_for_spikes(db)
                auto_resolve_stale_incidents(db)
            finally:
                db.close()
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error("Error in pattern detection loop: %s", e)
            await asyncio.sleep(5)


async def _check_for_spikes(db) -> None:
    """Compare recent error rate to previous window and alert on spikes."""
    now = datetime.utcnow()
    window = timedelta(seconds=settings.SPIKE_WINDOW_SECONDS)
    recent_start = now - window
    prev_start = now - (window * 2)

    recent_count = db.query(func.count(AlertEvent.id)).filter(AlertEvent.created_at >= recent_start).scalar() or 0

    if recent_count < settings.SPIKE_MIN_EVENTS:
        return

    prev_count = db.query(func.count(AlertEvent.id)).filter(AlertEvent.created_at >= prev_start, AlertEvent.created_at < recent_start).scalar() or 0

    if prev_count == 0 and recent_count >= settings.SPIKE_MIN_EVENTS:
        # Went from zero to many errors
        top_errors = _get_top_errors(db, recent_start)
        await notify_spike("all services", recent_count, prev_count, top_errors, db)
        logger.warning("Error spike detected: 0 -> %d events", recent_count)
        return

    if prev_count > 0 and recent_count >= prev_count * settings.SPIKE_MULTIPLIER:
        top_errors = _get_top_errors(db, recent_start)
        await notify_spike("all services", recent_count, prev_count, top_errors, db)
        logger.warning("Error spike detected: %d -> %d events (%.1fx)", prev_count, recent_count, recent_count / prev_count)


def _get_top_errors(db, since: datetime) -> list[dict]:
    """Get top error codes in the recent window."""
    rows = (
        db.query(AlertEvent.error_code, func.count(AlertEvent.id).label("count"))
        .filter(AlertEvent.created_at >= since, AlertEvent.error_code.isnot(None))
        .group_by(AlertEvent.error_code)
        .order_by(func.count(AlertEvent.id).desc())
        .limit(5)
        .all()
    )
    return [{"error_code": code, "count": count} for code, count in rows]
