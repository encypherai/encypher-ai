"""
Detection Service -- async non-blocking detection event logging.

Wraps rights_service detection methods for use in public endpoints.
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def log_detection_event(
    db: AsyncSession,
    *,
    document_id: str | None = None,
    organization_id: str,
    detection_source: str,
    **kwargs,
) -> None:
    """Non-blocking detection event logger."""
    try:
        from app.services.rights_service import rights_service

        event_data = {
            "document_id": document_id,
            "organization_id": organization_id,
            "detection_source": detection_source,
            **kwargs,
        }
        await rights_service.log_detection_event(db=db, event_data=event_data)
    except Exception:
        logger.debug("Detection event logging failed (non-blocking)", exc_info=True)


detection_service = log_detection_event
