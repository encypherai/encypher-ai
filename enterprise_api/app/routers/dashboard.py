"""
Dashboard router for basic organization statistics.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.database import get_db
from app.dependencies import get_current_organization

router = APIRouter()


@router.get("/stats")
async def get_organization_stats(
    organization: dict = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """
    Get organization statistics.

    Args:
        organization: Organization details from authentication
        db: Database session

    Returns:
        dict: Organization usage statistics
    """
    result = await db.execute(
        text("""
            SELECT
                documents_signed,
                sentences_signed,
                api_calls_this_month,
                monthly_quota,
                tier
            FROM organizations
            WHERE organization_id = :org_id
        """),
        {"org_id": organization['organization_id']}
    )

    row = result.fetchone()

    return {
        "success": True,
        "organization_id": organization['organization_id'],
        "organization_name": organization['organization_name'],
        "tier": row.tier if row else "free",
        "usage": {
            "documents_signed": row.documents_signed if row else 0,
            "sentences_signed": row.sentences_signed if row else 0,
            "api_calls_this_month": row.api_calls_this_month if row else 0,
            "monthly_quota": row.monthly_quota if row else 1000,
            "quota_remaining": (row.monthly_quota - row.api_calls_this_month) if row else 1000
        }
    }
