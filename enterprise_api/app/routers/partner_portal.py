"""Partner Portal router for platform partners to manage child publishers."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_organization_dep

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/partner/portal", tags=["Partner Portal"])


def _require_strategic_partner(org_context: Dict) -> str:
    tier = (org_context.get("tier") or "free").lower()
    if tier not in ("strategic_partner", "demo"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FEATURE_NOT_AVAILABLE",
                "message": "Partner portal requires Strategic Partner tier.",
                "required_tier": "strategic_partner",
            },
        )
    return org_context["organization_id"]


@router.get(
    "/publishers",
    summary="List partner publishers",
    description="List all child publisher organizations managed by the authenticated strategic partner.",
)
async def list_partner_publishers(
    db: AsyncSession = Depends(get_db),
    org_context: Dict = Depends(get_current_organization_dep),
) -> Dict[str, Any]:
    partner_org_id = _require_strategic_partner(org_context)
    from app.models.organization import Organization

    stmt = select(Organization).where(Organization.parent_org_id == partner_org_id)
    result = await db.execute(stmt)
    children = result.scalars().all()
    publishers = []
    for child in children:
        publishers.append(
            {
                "id": child.id,
                "name": child.name,
                "tier": child.tier,
                "created_at": child.created_at.isoformat() if child.created_at else None,
                "coalition_member": getattr(child, "coalition_member", False),
            }
        )
    return {"publishers": publishers, "total": len(publishers)}


@router.get("/aggregate", summary="Get partner aggregate stats", description="Return aggregated metrics across all child publisher organizations.")
async def get_partner_aggregate(
    db: AsyncSession = Depends(get_db),
    org_context: Dict = Depends(get_current_organization_dep),
) -> Dict[str, Any]:
    partner_org_id = _require_strategic_partner(org_context)
    from app.models.organization import Organization

    # Get child org IDs in one query
    child_ids_stmt = select(Organization.id).where(Organization.parent_org_id == partner_org_id)
    child_ids_result = await db.execute(child_ids_stmt)
    child_ids: List[str] = [row[0] for row in child_ids_result.all()]

    if not child_ids:
        return {
            "total_publishers": 0,
            "total_documents_signed": 0,
            "total_verifications": 0,
            "total_spread_detections": 0,
        }

    total_publishers = len(child_ids)

    # Aggregate documents_signed from Organization model
    docs_stmt = select(func.coalesce(func.sum(Organization.documents_signed), 0)).where(Organization.id.in_(child_ids))
    docs_result = await db.execute(docs_stmt)
    total_documents_signed = docs_result.scalar() or 0

    # Aggregate content detection events (spread detections)
    total_spread_detections = 0
    try:
        from app.models.rights import ContentDetectionEvent

        spread_stmt = select(func.count(ContentDetectionEvent.id)).where(ContentDetectionEvent.organization_id.in_(child_ids))
        spread_result = await db.execute(spread_stmt)
        total_spread_detections = spread_result.scalar() or 0
    except Exception:
        logger.debug("ContentDetectionEvent table not available for aggregate query")

    # Aggregate verifications from content_references (verified documents)
    total_verifications = 0
    try:
        from app.models.content_reference import ContentReference

        verify_stmt = select(func.count(ContentReference.id)).where(ContentReference.organization_id.in_(child_ids))
        verify_result = await db.execute(verify_stmt)
        total_verifications = verify_result.scalar() or 0
    except Exception:
        logger.debug("ContentReference table not available for aggregate query")

    return {
        "total_publishers": total_publishers,
        "total_documents_signed": total_documents_signed,
        "total_verifications": total_verifications,
        "total_spread_detections": total_spread_detections,
    }


@router.get(
    "/publishers/{pub_org_id}",
    summary="Get partner publisher detail",
    description="Retrieve detailed information about a specific child publisher organization.",
)
async def get_partner_publisher_detail(
    pub_org_id: str = Path(...),
    db: AsyncSession = Depends(get_db),
    org_context: Dict = Depends(get_current_organization_dep),
) -> Dict[str, Any]:
    partner_org_id = _require_strategic_partner(org_context)
    from app.models.organization import Organization

    stmt = select(Organization).where(
        Organization.id == pub_org_id,
        Organization.parent_org_id == partner_org_id,
    )
    result = await db.execute(stmt)
    child = result.scalar_one_or_none()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publisher not found or not a child of this partner",
        )
    return {
        "id": child.id,
        "name": child.name,
        "tier": child.tier,
        "created_at": child.created_at.isoformat() if child.created_at else None,
        "coalition_member": getattr(child, "coalition_member", False),
    }
