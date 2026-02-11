"""
API endpoints for coalition management.
"""

import logging
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

logger = logging.getLogger(__name__)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.schemas.coalition import (
    AdminCoalitionOverview,
    CoalitionMember,
    CoalitionStats,
    ContentAccessLog,
    ContentAccessLogCreate,
    ContentItem,
    ContentItemCreate,
    MemberListResponse,
    RevenueTransaction,
    RevenueTransactionCreate,
)
from app.services.coalition_service import (
    create_access_log,
    create_content_item,
    create_revenue_transaction,
    get_admin_coalition_overview,
    get_coalition_members,
    get_coalition_stats,
    get_member_revenue,
    get_or_create_coalition_member,
    get_top_content,
)
from app.services.user import get_current_user

router = APIRouter()


@router.get("/stats", response_model=CoalitionStats)
async def get_stats(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    """
    Get coalition stats for current user.
    """
    try:
        stats = await get_coalition_stats(db, current_user.id)
        return stats
    except Exception as e:
        logger.exception("Failed to fetch coalition stats")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch coalition stats")


@router.get("/revenue")
async def get_revenue(
    period: Optional[str] = Query(None, description="Filter by period: week, month, year"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get revenue breakdown for current user.
    """
    try:
        revenue = await get_member_revenue(db, current_user.id, period)
        return {"success": True, "data": revenue}
    except Exception as e:
        logger.exception("Failed to fetch revenue")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch revenue")


@router.get("/content/performance", response_model=List[ContentItem])
async def get_content_performance(
    limit: int = Query(10, ge=1, le=100, description="Number of top items to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get top performing content for current user.
    """
    try:
        content = await get_top_content(db, current_user.id, limit)
        return content
    except Exception as e:
        logger.exception("Failed to fetch content performance")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch content performance")


@router.post("/content", response_model=ContentItem, status_code=status.HTTP_201_CREATED)
async def create_content(content_data: ContentItemCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    """
    Create a new content item.
    """
    # Ensure content is created for current user
    if content_data.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create content for other users")

    try:
        content = await create_content_item(db, content_data)
        return content
    except Exception as e:
        logger.exception("Failed to create content")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create content")


@router.post("/revenue", response_model=RevenueTransaction, status_code=status.HTTP_201_CREATED)
async def create_revenue(
    transaction_data: RevenueTransactionCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create a new revenue transaction (admin only).
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can create revenue transactions")

    try:
        transaction = await create_revenue_transaction(db, transaction_data)
        return transaction
    except Exception as e:
        logger.exception("Failed to create revenue transaction")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create revenue transaction")


@router.post("/access-log", response_model=ContentAccessLog, status_code=status.HTTP_201_CREATED)
async def create_access_log_endpoint(
    log_data: ContentAccessLogCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create a new content access log.
    """
    try:
        log = await create_access_log(db, log_data)
        return log
    except Exception as e:
        logger.exception("Failed to create access log")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create access log")


@router.get("/member", response_model=CoalitionMember)
async def get_member_info(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    """
    Get coalition member info for current user.
    """
    try:
        member = await get_or_create_coalition_member(db, current_user.id)
        return member
    except Exception as e:
        logger.exception("Failed to fetch member info")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch member info")


# Admin endpoints
@router.get("/admin/overview", response_model=AdminCoalitionOverview)
async def get_admin_overview(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    """
    Get coalition overview statistics (admin only).
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can access this endpoint")

    try:
        overview = await get_admin_coalition_overview(db)
        return overview
    except Exception as e:
        logger.exception("Failed to fetch admin overview")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch admin overview")


@router.get("/admin/members", response_model=MemberListResponse)
async def get_members_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get list of coalition members (admin only).
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can access this endpoint")

    try:
        members = await get_coalition_members(db, skip, limit)
        return members
    except Exception as e:
        logger.exception("Failed to fetch members")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch members")
