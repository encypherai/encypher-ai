"""CDN Provenance Analytics router.

Provides per-org dashboard metrics for image provenance protection:
  - assets_protected: count of CdnImageRecord rows (is_variant=False)
  - variants_verified: count of variant records (is_variant=True)
  - provenance_lost_events: count where verification attempt found no match
  - image_requests_tracked: count of CdnAttributionEvent rows
  - recoverable_percent: (assets_protected + variants_verified) / image_requests_tracked * 100

Prefix: /cdn/analytics (mounted at /api/v1 via bootstrap/routers.py)
"""

import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_organization_dep
from app.models.cdn_attribution_event import CdnAttributionEvent
from app.models.cdn_image_record import CdnImageRecord
from app.schemas.cdn_schemas import (
    CdnAnalyticsSummary,
    CdnAnalyticsTimeline,
    CdnAnalyticsTimelineDay,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cdn/analytics", tags=["CDN Analytics"])


# ---------------------------------------------------------------------------
# GET /cdn/analytics/summary
# ---------------------------------------------------------------------------


@router.get(
    "/summary",
    response_model=CdnAnalyticsSummary,
    summary="CDN provenance analytics summary",
    description="""
Return per-org dashboard metrics for image provenance protection.

Returns counts of protected assets, registered variants, and tracked image
requests, plus a recoverable percentage.

**Requires authentication.**
    """,
)
async def get_analytics_summary(
    db: AsyncSession = Depends(get_db),
    org_context: dict = Depends(get_current_organization_dep),
) -> CdnAnalyticsSummary:
    org_id: str = org_context["organization_id"]

    # assets_protected
    result = await db.execute(
        select(func.count(CdnImageRecord.id)).where(
            CdnImageRecord.organization_id == org_id,
            CdnImageRecord.is_variant == False,  # noqa: E712
        )
    )
    assets_protected = result.scalar_one() or 0

    # variants_registered
    result = await db.execute(
        select(func.count(CdnImageRecord.id)).where(
            CdnImageRecord.organization_id == org_id,
            CdnImageRecord.is_variant == True,  # noqa: E712
        )
    )
    variants_registered = result.scalar_one() or 0

    # image_requests_tracked
    result = await db.execute(
        select(func.count(CdnAttributionEvent.id)).where(
            CdnAttributionEvent.organization_id == org_id,
        )
    )
    image_requests_tracked = result.scalar_one() or 0

    total_trackable = assets_protected + variants_registered
    recoverable_percent = round(
        (total_trackable / image_requests_tracked * 100) if image_requests_tracked > 0 else 0.0,
        2,
    )

    return CdnAnalyticsSummary(
        organization_id=org_id,
        assets_protected=assets_protected,
        variants_registered=variants_registered,
        image_requests_tracked=image_requests_tracked,
        recoverable_percent=recoverable_percent,
    )


# ---------------------------------------------------------------------------
# GET /cdn/analytics/timeline
# ---------------------------------------------------------------------------


@router.get(
    "/timeline",
    response_model=CdnAnalyticsTimeline,
    summary="CDN provenance analytics day-by-day timeline",
    description="""
Return day-by-day counts of images signed and attribution events tracked
over the past N days (default 30).

**Requires authentication.**
    """,
)
async def get_analytics_timeline(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to include"),
    db: AsyncSession = Depends(get_db),
    org_context: dict = Depends(get_current_organization_dep),
) -> CdnAnalyticsTimeline:
    org_id: str = org_context["organization_id"]

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    # Fetch CdnImageRecord rows within the window
    images_result = await db.execute(
        select(CdnImageRecord.created_at).where(
            CdnImageRecord.organization_id == org_id,
            CdnImageRecord.created_at >= cutoff,
        )
    )
    image_timestamps = images_result.scalars().all()

    # Fetch CdnAttributionEvent rows within the window
    events_result = await db.execute(
        select(CdnAttributionEvent.created_at).where(
            CdnAttributionEvent.organization_id == org_id,
            CdnAttributionEvent.created_at >= cutoff,
        )
    )
    event_timestamps = events_result.scalars().all()

    # Build day-keyed dictionaries
    images_by_day: dict[str, int] = {}
    for ts in image_timestamps:
        if ts is None:
            continue
        # Handle both timezone-aware and naive timestamps
        if hasattr(ts, "date"):
            day_str = ts.date().isoformat()
        else:
            day_str = str(ts)[:10]
        images_by_day[day_str] = images_by_day.get(day_str, 0) + 1

    events_by_day: dict[str, int] = {}
    for ts in event_timestamps:
        if ts is None:
            continue
        if hasattr(ts, "date"):
            day_str = ts.date().isoformat()
        else:
            day_str = str(ts)[:10]
        events_by_day[day_str] = events_by_day.get(day_str, 0) + 1

    # Build timeline: one entry per day in the window (most recent first)
    today = datetime.now(timezone.utc).date()
    timeline_data: list[CdnAnalyticsTimelineDay] = []
    for offset in range(days):
        day = today - timedelta(days=offset)
        day_str = day.isoformat()
        timeline_data.append(
            CdnAnalyticsTimelineDay(
                date=day_str,
                images_signed=images_by_day.get(day_str, 0),
                image_requests=events_by_day.get(day_str, 0),
            )
        )

    return CdnAnalyticsTimeline(days=days, data=timeline_data)
