"""
Internal endpoints for usage/overage billing and quota resets.

Protected by X-Internal-Token. Not included in public API schema.
"""

import hmac
import logging
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.services.usage_record_service import UsageRecordService
from app.utils.quota import QuotaManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/internal", tags=["Internal"])


def _require_internal_token(internal_token: Optional[str]) -> None:
    expected = (settings.internal_service_token or "").strip()
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Internal token not configured",
        )
    if not internal_token or not hmac.compare_digest(internal_token.strip(), expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid internal token",
        )


# -- Request / Response schemas --


class MarkBilledRequest(BaseModel):
    record_ids: list[str]
    invoice_id: str


class UsageRecordOut(BaseModel):
    id: str
    organization_id: str
    metric: str
    count: int
    overage_count: int
    overage_amount_cents: int
    rate_cents: int
    period_start: str
    period_end: str


# -- Endpoints --


@router.post("/usage/unbilled", include_in_schema=False)
async def get_unbilled_usage(
    db: AsyncSession = Depends(get_db),
    x_internal_token: Optional[str] = Header(None, alias="X-Internal-Token"),
):
    """Return all unbilled overage records."""
    _require_internal_token(x_internal_token)

    records = await UsageRecordService.get_unbilled_records(db)
    return {
        "records": [
            {
                "id": r.id,
                "organization_id": r.organization_id,
                "metric": r.metric,
                "count": r.count or 0,
                "overage_count": r.overage_count or 0,
                "overage_amount_cents": r.overage_amount_cents or 0,
                "rate_cents": r.rate_cents or 0,
                "period_start": r.period_start.isoformat() if r.period_start else "",
                "period_end": r.period_end.isoformat() if r.period_end else "",
            }
            for r in records
        ]
    }


@router.post("/usage/mark-billed", include_in_schema=False)
async def mark_usage_billed(
    request: MarkBilledRequest,
    db: AsyncSession = Depends(get_db),
    x_internal_token: Optional[str] = Header(None, alias="X-Internal-Token"),
):
    """Mark usage records as billed."""
    _require_internal_token(x_internal_token)

    await UsageRecordService.mark_billed(db, request.record_ids, request.invoice_id)
    await db.commit()
    return {"success": True, "marked": len(request.record_ids)}


@router.post("/quotas/reset", include_in_schema=False)
async def reset_quotas(
    db: AsyncSession = Depends(get_db),
    x_internal_token: Optional[str] = Header(None, alias="X-Internal-Token"),
):
    """Reset monthly quotas for all organizations."""
    _require_internal_token(x_internal_token)

    await QuotaManager.reset_monthly_quotas(db)
    return {"success": True, "message": "Monthly quotas reset"}
