"""
Service for coalition operations.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.coalition import (
    CoalitionMember,
    ContentItem,
    RevenueTransaction,
    ContentAccessLog
)
from app.models.user import User
from app.schemas.coalition import (
    ContentItemCreate,
    RevenueTransactionCreate,
    ContentAccessLogCreate,
    CoalitionStats,
    ContentStats,
    RevenueStats,
    RevenueHistoryItem,
    TopContentItem,
    RecentAccessItem,
    AdminCoalitionOverview,
    MemberListItem,
    MemberListResponse,
)


async def get_or_create_coalition_member(
    db: AsyncSession,
    user_id: int
) -> CoalitionMember:
    """
    Get or create a coalition member for a user.
    """
    # Check if member exists
    query = select(CoalitionMember).where(CoalitionMember.user_id == user_id)
    result = await db.execute(query)
    member = result.scalar_one_or_none()

    if not member:
        # Create new member
        member = CoalitionMember(
            user_id=user_id,
            status="active",
            total_documents=0,
            total_verifications=0,
            total_earned=0.0,
            pending_payout=0.0,
        )
        db.add(member)
        await db.commit()
        await db.refresh(member)

    return member


async def get_coalition_stats(
    db: AsyncSession,
    user_id: int
) -> CoalitionStats:
    """
    Get comprehensive coalition statistics for a user.
    """
    # Ensure member exists
    member = await get_or_create_coalition_member(db, user_id)

    # Get content stats
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    total_docs_query = select(func.count(ContentItem.id)).where(
        ContentItem.user_id == user_id
    )
    total_docs_result = await db.execute(total_docs_query)
    total_documents = total_docs_result.scalar() or 0

    recent_docs_query = select(func.count(ContentItem.id)).where(
        and_(
            ContentItem.user_id == user_id,
            ContentItem.signed_at >= thirty_days_ago
        )
    )
    recent_docs_result = await db.execute(recent_docs_query)
    recent_documents = recent_docs_result.scalar() or 0

    verification_query = select(func.sum(ContentItem.verification_count)).where(
        ContentItem.user_id == user_id
    )
    verification_result = await db.execute(verification_query)
    verification_count = verification_result.scalar() or 0

    # Calculate trend (simplified)
    trend_percentage = 12.0 if recent_documents > 0 else 0.0

    content_stats = ContentStats(
        total_documents=total_documents,
        verification_count=verification_count,
        recent_documents=recent_documents,
        trend_percentage=trend_percentage
    )

    # Get revenue stats
    paid_query = select(func.sum(RevenueTransaction.amount)).where(
        and_(
            RevenueTransaction.user_id == user_id,
            RevenueTransaction.transaction_type == "paid",
            RevenueTransaction.status == "completed"
        )
    )
    paid_result = await db.execute(paid_query)
    paid = paid_result.scalar() or 0.0

    # Calculate next payout date (first of next month)
    now = datetime.utcnow()
    if now.month == 12:
        next_payout = datetime(now.year + 1, 1, 1)
    else:
        next_payout = datetime(now.year, now.month + 1, 1)

    revenue_stats = RevenueStats(
        total_earned=member.total_earned,
        pending=member.pending_payout,
        paid=paid,
        next_payout_date=next_payout,
        monthly_average=paid / 12 if paid > 0 else 0.0
    )

    # Get revenue history (last 12 months)
    revenue_history = []
    for i in range(12):
        month_date = datetime.utcnow() - timedelta(days=30 * i)
        month_str = month_date.strftime("%b %Y")

        # Get earned for this month
        month_start = datetime(month_date.year, month_date.month, 1)
        if month_date.month == 12:
            month_end = datetime(month_date.year + 1, 1, 1)
        else:
            month_end = datetime(month_date.year, month_date.month + 1, 1)

        earned_query = select(func.sum(RevenueTransaction.amount)).where(
            and_(
                RevenueTransaction.user_id == user_id,
                RevenueTransaction.transaction_type == "earned",
                RevenueTransaction.created_at >= month_start,
                RevenueTransaction.created_at < month_end
            )
        )
        earned_result = await db.execute(earned_query)
        earned = earned_result.scalar() or 0.0

        paid_query = select(func.sum(RevenueTransaction.amount)).where(
            and_(
                RevenueTransaction.user_id == user_id,
                RevenueTransaction.transaction_type == "paid",
                RevenueTransaction.paid_at >= month_start,
                RevenueTransaction.paid_at < month_end
            )
        )
        paid_result = await db.execute(paid_query)
        paid_month = paid_result.scalar() or 0.0

        revenue_history.insert(0, RevenueHistoryItem(
            month=month_str,
            earned=earned,
            paid=paid_month
        ))

    # Get top performing content
    top_content_query = select(ContentItem).where(
        ContentItem.user_id == user_id
    ).order_by(desc(ContentItem.revenue_generated)).limit(10)

    top_content_result = await db.execute(top_content_query)
    top_content_items = top_content_result.scalars().all()

    top_content = [
        TopContentItem(
            id=item.id,
            title=item.title,
            content_type=item.content_type,
            word_count=item.word_count,
            verification_count=item.verification_count,
            access_count=item.access_count,
            revenue_generated=item.revenue_generated
        )
        for item in top_content_items
    ]

    # Get recent access logs
    recent_access_query = select(
        ContentAccessLog, ContentItem.title
    ).join(
        ContentItem, ContentAccessLog.content_id == ContentItem.id
    ).where(
        ContentAccessLog.user_id == user_id
    ).order_by(desc(ContentAccessLog.accessed_at)).limit(50)

    recent_access_result = await db.execute(recent_access_query)
    recent_access_rows = recent_access_result.all()

    recent_access = [
        RecentAccessItem(
            id=log.id,
            ai_company=log.ai_company,
            content_title=title,
            access_type=log.access_type,
            accessed_at=log.accessed_at,
            revenue_amount=log.revenue_amount
        )
        for log, title in recent_access_rows
    ]

    return CoalitionStats(
        content_stats=content_stats,
        revenue_stats=revenue_stats,
        revenue_history=revenue_history,
        top_content=top_content,
        recent_access=recent_access
    )


async def get_member_revenue(
    db: AsyncSession,
    user_id: int,
    period: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get revenue breakdown for a member.
    """
    # Determine date range based on period
    now = datetime.utcnow()
    if period == "week":
        start_date = now - timedelta(days=7)
    elif period == "month":
        start_date = now - timedelta(days=30)
    elif period == "year":
        start_date = now - timedelta(days=365)
    else:
        start_date = None

    query = select(RevenueTransaction).where(
        RevenueTransaction.user_id == user_id
    )

    if start_date:
        query = query.where(RevenueTransaction.created_at >= start_date)

    query = query.order_by(desc(RevenueTransaction.created_at))

    result = await db.execute(query)
    transactions = result.scalars().all()

    return {
        "transactions": transactions,
        "total_earned": sum(t.amount for t in transactions if t.transaction_type == "earned"),
        "total_paid": sum(t.amount for t in transactions if t.transaction_type == "paid"),
    }


async def get_top_content(
    db: AsyncSession,
    user_id: int,
    limit: int = 10
) -> List[ContentItem]:
    """
    Get top performing content for a user.
    """
    query = select(ContentItem).where(
        ContentItem.user_id == user_id
    ).order_by(desc(ContentItem.revenue_generated)).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


async def create_content_item(
    db: AsyncSession,
    content_data: ContentItemCreate
) -> ContentItem:
    """
    Create a new content item.
    """
    content = ContentItem(**content_data.model_dump())
    db.add(content)
    await db.commit()
    await db.refresh(content)

    # Update member stats
    await update_member_stats(db, content_data.user_id)

    return content


async def create_revenue_transaction(
    db: AsyncSession,
    transaction_data: RevenueTransactionCreate
) -> RevenueTransaction:
    """
    Create a new revenue transaction.
    """
    transaction = RevenueTransaction(**transaction_data.model_dump())
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)

    # Update member stats
    await update_member_stats(db, transaction_data.user_id)

    return transaction


async def create_access_log(
    db: AsyncSession,
    log_data: ContentAccessLogCreate
) -> ContentAccessLog:
    """
    Create a new content access log.
    """
    log = ContentAccessLog(**log_data.model_dump())
    db.add(log)

    # Update content item stats
    content_query = select(ContentItem).where(ContentItem.id == log_data.content_id)
    content_result = await db.execute(content_query)
    content = content_result.scalar_one_or_none()

    if content:
        content.access_count += 1
        content.last_accessed = datetime.utcnow()
        if log_data.revenue_amount > 0:
            content.revenue_generated += log_data.revenue_amount

    await db.commit()
    await db.refresh(log)

    # Update member stats
    await update_member_stats(db, log_data.user_id)

    return log


async def update_member_stats(
    db: AsyncSession,
    user_id: int
) -> None:
    """
    Update coalition member statistics.
    """
    member = await get_or_create_coalition_member(db, user_id)

    # Count total documents
    docs_query = select(func.count(ContentItem.id)).where(ContentItem.user_id == user_id)
    docs_result = await db.execute(docs_query)
    member.total_documents = docs_result.scalar() or 0

    # Sum verifications
    verify_query = select(func.sum(ContentItem.verification_count)).where(ContentItem.user_id == user_id)
    verify_result = await db.execute(verify_query)
    member.total_verifications = verify_result.scalar() or 0

    # Sum earned revenue
    earned_query = select(func.sum(RevenueTransaction.amount)).where(
        and_(
            RevenueTransaction.user_id == user_id,
            RevenueTransaction.transaction_type == "earned"
        )
    )
    earned_result = await db.execute(earned_query)
    member.total_earned = earned_result.scalar() or 0.0

    # Sum pending revenue
    pending_query = select(func.sum(RevenueTransaction.amount)).where(
        and_(
            RevenueTransaction.user_id == user_id,
            RevenueTransaction.transaction_type == "earned",
            RevenueTransaction.status == "pending"
        )
    )
    pending_result = await db.execute(pending_query)
    member.pending_payout = pending_result.scalar() or 0.0

    await db.commit()


# Admin functions
async def get_admin_coalition_overview(
    db: AsyncSession
) -> AdminCoalitionOverview:
    """
    Get coalition overview statistics for admin.
    """
    # Total members
    total_members_query = select(func.count(CoalitionMember.id))
    total_members_result = await db.execute(total_members_query)
    total_members = total_members_result.scalar() or 0

    # Active members
    active_members_query = select(func.count(CoalitionMember.id)).where(
        CoalitionMember.status == "active"
    )
    active_members_result = await db.execute(active_members_query)
    active_members = active_members_result.scalar() or 0

    # Total content
    total_content_query = select(func.count(ContentItem.id))
    total_content_result = await db.execute(total_content_query)
    total_content = total_content_result.scalar() or 0

    # Total revenue MTD
    now = datetime.utcnow()
    month_start = datetime(now.year, now.month, 1)

    revenue_mtd_query = select(func.sum(RevenueTransaction.amount)).where(
        and_(
            RevenueTransaction.transaction_type == "earned",
            RevenueTransaction.created_at >= month_start
        )
    )
    revenue_mtd_result = await db.execute(revenue_mtd_query)
    total_revenue_mtd = revenue_mtd_result.scalar() or 0.0

    # Total verifications
    total_verifications_query = select(func.sum(ContentItem.verification_count))
    total_verifications_result = await db.execute(total_verifications_query)
    total_verifications = total_verifications_result.scalar() or 0

    return AdminCoalitionOverview(
        total_members=total_members,
        active_members=active_members,
        total_content=total_content,
        total_revenue_mtd=total_revenue_mtd,
        total_verifications=total_verifications
    )


async def get_coalition_members(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50
) -> MemberListResponse:
    """
    Get list of coalition members for admin.
    """
    # Get members with user info
    query = select(CoalitionMember, User).join(
        User, CoalitionMember.user_id == User.id
    ).order_by(desc(CoalitionMember.total_earned)).offset(skip).limit(limit)

    result = await db.execute(query)
    rows = result.all()

    # Count total members
    count_query = select(func.count(CoalitionMember.id))
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    items = [
        MemberListItem(
            id=member.id,
            user_id=member.user_id,
            email=user.email,
            full_name=user.full_name or "",
            status=member.status,
            total_documents=member.total_documents,
            total_verifications=member.total_verifications,
            total_earned=member.total_earned,
            pending_payout=member.pending_payout,
            joined_date=member.joined_date
        )
        for member, user in rows
    ]

    return MemberListResponse(
        items=items,
        total=total,
        page=skip // limit + 1 if limit > 0 else 1,
        limit=limit
    )
