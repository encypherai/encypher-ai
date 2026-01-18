"""Coalition revenue tracking router."""

from datetime import date, datetime, timezone
from typing import List, Optional
from uuid import uuid4

from dateutil.relativedelta import relativedelta  # type: ignore[import-untyped]
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_content_db, get_db
from app.dependencies import require_read_permission

router = APIRouter(prefix="/coalition", tags=["Coalition"])


# Tier-based revenue share configuration
TIER_REV_SHARE = {
    "starter": {"publisher": 65, "encypher": 35},
    "professional": {"publisher": 70, "encypher": 30},
    "business": {"publisher": 80, "encypher": 20},
    "enterprise": {"publisher": 85, "encypher": 15},
    "strategic_partner": {"publisher": 85, "encypher": 15},
}


class ContentStats(BaseModel):
    """Content corpus statistics."""

    period_start: str
    period_end: str
    documents_count: int
    sentences_count: int
    total_characters: int
    unique_content_hash_count: int
    content_categories: Optional[dict] = None


class EarningsSummary(BaseModel):
    """Earnings summary for a period."""

    period_start: str
    period_end: str
    gross_revenue_cents: int
    publisher_share_percent: int
    publisher_earnings_cents: int
    status: str
    deal_count: int


class PayoutSummary(BaseModel):
    """Payout summary."""

    id: str
    period_start: str
    period_end: str
    total_earnings_cents: int
    payout_amount_cents: int
    currency: str
    status: str
    paid_at: Optional[str] = None


class CoalitionDashboardResponse(BaseModel):
    """Coalition dashboard data."""

    organization_id: str
    tier: str
    publisher_share_percent: int
    coalition_member: bool
    opted_out: bool

    # Current period stats
    current_period: ContentStats

    # Earnings
    lifetime_earnings_cents: int
    pending_earnings_cents: int
    paid_earnings_cents: int

    # Recent earnings
    recent_earnings: List[EarningsSummary]

    # Recent payouts
    recent_payouts: List[PayoutSummary]


@router.get("/dashboard", response_model=CoalitionDashboardResponse)
async def get_coalition_dashboard(
    organization: dict = Depends(require_read_permission),
    db: AsyncSession = Depends(get_db),
    content_db: AsyncSession = Depends(get_content_db),
) -> CoalitionDashboardResponse:
    """
    Get coalition dashboard data for the organization.

    Returns content stats, earnings, and payout information.
    """
    org_id = organization["organization_id"]
    tier = organization.get("tier", "starter")
    rev_share = TIER_REV_SHARE.get(tier, TIER_REV_SHARE["starter"])

    # Get coalition membership status
    coalition_member = organization.get("coalition_member", True)
    opted_out = organization.get("coalition_opted_out", False)

    # Calculate current period (current month)
    today = date.today()
    period_start = today.replace(day=1)
    period_end = (period_start + relativedelta(months=1)) - relativedelta(days=1)

    # Get current period content stats
    stats_result = await db.execute(
        text("""
            SELECT documents_count, sentences_count, total_characters, 
                   unique_content_hash_count, content_categories
            FROM coalition_content_stats
            WHERE organization_id = :org_id
              AND period_start = :period_start
              AND period_end = :period_end
        """),
        {"org_id": org_id, "period_start": period_start, "period_end": period_end},
    )
    stats_row = stats_result.fetchone()

    # If no stats exist, calculate from documents table (in content database)
    if not stats_row:
        doc_stats = await content_db.execute(
            text("""
                SELECT 
                    COUNT(*) as doc_count,
                    COALESCE(SUM(total_sentences), 0) as sentence_count,
                    COUNT(DISTINCT text_hash) as unique_hashes
                FROM documents
                WHERE organization_id = :org_id
            """),
            {"org_id": org_id},
        )
        doc_row = doc_stats.fetchone()
        current_stats = ContentStats(
            period_start=period_start.isoformat(),
            period_end=period_end.isoformat(),
            documents_count=doc_row.doc_count if doc_row else 0,
            sentences_count=doc_row.sentence_count if doc_row else 0,
            total_characters=0,  # Would need to calculate
            unique_content_hash_count=doc_row.unique_hashes if doc_row else 0,
            content_categories=None,
        )
    else:
        current_stats = ContentStats(
            period_start=period_start.isoformat(),
            period_end=period_end.isoformat(),
            documents_count=stats_row.documents_count,
            sentences_count=stats_row.sentences_count,
            total_characters=stats_row.total_characters,
            unique_content_hash_count=stats_row.unique_content_hash_count,
            content_categories=stats_row.content_categories,
        )

    # Get earnings summary
    earnings_result = await db.execute(
        text("""
            SELECT 
                COALESCE(SUM(publisher_earnings_cents), 0) as lifetime,
                COALESCE(SUM(CASE WHEN status = 'pending' THEN publisher_earnings_cents ELSE 0 END), 0) as pending,
                COALESCE(SUM(CASE WHEN status = 'paid' THEN publisher_earnings_cents ELSE 0 END), 0) as paid
            FROM coalition_earnings
            WHERE organization_id = :org_id
        """),
        {"org_id": org_id},
    )
    earnings_row = earnings_result.fetchone()

    # Get recent earnings (last 6 months)
    recent_earnings_result = await db.execute(
        text("""
            SELECT 
                period_start, period_end,
                SUM(gross_revenue_cents) as gross,
                AVG(publisher_share_percent)::int as share_percent,
                SUM(publisher_earnings_cents) as earnings,
                MAX(status) as status,
                COUNT(*) as deal_count
            FROM coalition_earnings
            WHERE organization_id = :org_id
            GROUP BY period_start, period_end
            ORDER BY period_start DESC
            LIMIT 6
        """),
        {"org_id": org_id},
    )
    recent_earnings = [
        EarningsSummary(
            period_start=row.period_start.isoformat() if row.period_start else "",
            period_end=row.period_end.isoformat() if row.period_end else "",
            gross_revenue_cents=row.gross or 0,
            publisher_share_percent=row.share_percent or rev_share["publisher"],
            publisher_earnings_cents=row.earnings or 0,
            status=row.status or "pending",
            deal_count=row.deal_count or 0,
        )
        for row in recent_earnings_result.fetchall()
    ]

    # Get recent payouts
    payouts_result = await db.execute(
        text("""
            SELECT id, period_start, period_end, total_earnings_cents,
                   payout_amount_cents, currency, status, paid_at
            FROM coalition_payouts
            WHERE organization_id = :org_id
            ORDER BY created_at DESC
            LIMIT 5
        """),
        {"org_id": org_id},
    )
    recent_payouts = [
        PayoutSummary(
            id=row.id,
            period_start=row.period_start.isoformat() if row.period_start else "",
            period_end=row.period_end.isoformat() if row.period_end else "",
            total_earnings_cents=row.total_earnings_cents or 0,
            payout_amount_cents=row.payout_amount_cents or 0,
            currency=row.currency or "USD",
            status=row.status or "pending",
            paid_at=row.paid_at.isoformat() if row.paid_at else None,
        )
        for row in payouts_result.fetchall()
    ]

    return CoalitionDashboardResponse(
        organization_id=org_id,
        tier=tier,
        publisher_share_percent=rev_share["publisher"],
        coalition_member=coalition_member,
        opted_out=opted_out,
        current_period=current_stats,
        lifetime_earnings_cents=earnings_row.lifetime if earnings_row else 0,
        pending_earnings_cents=earnings_row.pending if earnings_row else 0,
        paid_earnings_cents=earnings_row.paid if earnings_row else 0,
        recent_earnings=recent_earnings,
        recent_payouts=recent_payouts,
    )


@router.get("/content-stats")
async def get_content_stats(
    months: int = Query(12, ge=1, le=24),
    organization: dict = Depends(require_read_permission),
    db: AsyncSession = Depends(get_db),
):
    """
    Get historical content corpus statistics.
    """
    org_id = organization["organization_id"]

    result = await db.execute(
        text("""
            SELECT period_start, period_end, documents_count, sentences_count,
                   total_characters, unique_content_hash_count, content_categories
            FROM coalition_content_stats
            WHERE organization_id = :org_id
            ORDER BY period_start DESC
            LIMIT :limit
        """),
        {"org_id": org_id, "limit": months},
    )

    stats = [
        {
            "period_start": row.period_start.isoformat() if row.period_start else "",
            "period_end": row.period_end.isoformat() if row.period_end else "",
            "documents_count": row.documents_count,
            "sentences_count": row.sentences_count,
            "total_characters": row.total_characters,
            "unique_content_hash_count": row.unique_content_hash_count,
            "content_categories": row.content_categories,
        }
        for row in result.fetchall()
    ]

    return {
        "organization_id": org_id,
        "stats": stats,
    }


@router.get("/earnings")
async def get_earnings_history(
    months: int = Query(12, ge=1, le=24),
    organization: dict = Depends(require_read_permission),
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed earnings history.
    """
    org_id = organization["organization_id"]

    result = await db.execute(
        text("""
            SELECT id, deal_id, deal_name, ai_company, period_start, period_end,
                   gross_revenue_cents, publisher_share_percent, publisher_earnings_cents,
                   attribution_method, attribution_weight, status, created_at
            FROM coalition_earnings
            WHERE organization_id = :org_id
            ORDER BY period_start DESC
            LIMIT :limit
        """),
        {"org_id": org_id, "limit": months * 10},  # Assume up to 10 deals per month
    )

    earnings = [
        {
            "id": row.id,
            "deal_id": row.deal_id,
            "deal_name": row.deal_name,
            "ai_company": row.ai_company,
            "period_start": row.period_start.isoformat() if row.period_start else "",
            "period_end": row.period_end.isoformat() if row.period_end else "",
            "gross_revenue_cents": row.gross_revenue_cents,
            "publisher_share_percent": row.publisher_share_percent,
            "publisher_earnings_cents": row.publisher_earnings_cents,
            "attribution_method": row.attribution_method,
            "attribution_weight": row.attribution_weight,
            "status": row.status,
            "created_at": row.created_at.isoformat() if row.created_at else "",
        }
        for row in result.fetchall()
    ]

    return {
        "organization_id": org_id,
        "earnings": earnings,
    }


@router.post("/opt-out")
async def opt_out_of_coalition(
    organization: dict = Depends(require_read_permission),
    db: AsyncSession = Depends(get_db),
):
    """
    Opt out of the coalition revenue sharing program.

    Note: This will stop future earnings but won't affect pending payouts.
    """
    org_id = organization["organization_id"]
    now = datetime.now(timezone.utc)

    await db.execute(
        text("""
            UPDATE organizations
            SET coalition_member = FALSE,
                updated_at = :now
            WHERE id = :org_id
        """),
        {"org_id": org_id, "now": now},
    )
    await db.commit()

    return {
        "success": True,
        "message": "You have opted out of the coalition. Pending earnings will still be paid.",
        "opted_out_at": now.isoformat(),
    }


@router.post("/opt-in")
async def opt_in_to_coalition(
    organization: dict = Depends(require_read_permission),
    db: AsyncSession = Depends(get_db),
):
    """
    Opt back into the coalition revenue sharing program.
    """
    org_id = organization["organization_id"]
    now = datetime.now(timezone.utc)

    await db.execute(
        text("""
            UPDATE organizations
            SET coalition_member = TRUE,
                updated_at = :now
            WHERE id = :org_id
        """),
        {"org_id": org_id, "now": now},
    )
    await db.commit()

    return {
        "success": True,
        "message": "You have opted back into the coalition. Earnings will resume.",
    }


async def calculate_content_stats(
    db: AsyncSession,
    content_db: AsyncSession,
    organization_id: str,
    period_start: date,
    period_end: date,
) -> str:
    """
    Calculate and store content stats for a period.

    This is typically called by a scheduled job.
    Returns the stats ID.

    Args:
        db: Core database session (for storing stats)
        content_db: Content database session (for querying documents)
    """
    # Calculate stats from documents table (in content database)
    result = await content_db.execute(
        text("""
            SELECT 
                COUNT(*) as doc_count,
                COALESCE(SUM(total_sentences), 0) as sentence_count,
                COUNT(DISTINCT text_hash) as unique_hashes
            FROM documents
            WHERE organization_id = :org_id
              AND created_at >= :start
              AND created_at < :end
        """),
        {
            "org_id": organization_id,
            "start": period_start,
            "end": period_end,
        },
    )
    row = result.fetchone()

    stats_id = f"stats_{uuid4().hex[:16]}"
    now = datetime.now(timezone.utc)

    # Upsert stats
    await db.execute(
        text("""
            INSERT INTO coalition_content_stats (
                id, organization_id, period_start, period_end,
                documents_count, sentences_count, unique_content_hash_count,
                created_at
            )
            VALUES (
                :id, :org_id, :start, :end,
                :docs, :sentences, :hashes,
                :now
            )
            ON CONFLICT (organization_id, period_start, period_end)
            DO UPDATE SET
                documents_count = EXCLUDED.documents_count,
                sentences_count = EXCLUDED.sentences_count,
                unique_content_hash_count = EXCLUDED.unique_content_hash_count,
                updated_at = :now
        """),
        {
            "id": stats_id,
            "org_id": organization_id,
            "start": period_start,
            "end": period_end,
            "docs": row.doc_count if row else 0,
            "sentences": row.sentence_count if row else 0,
            "hashes": row.unique_hashes if row else 0,
            "now": now,
        },
    )

    return stats_id


async def attribute_deal_revenue(
    db: AsyncSession,
    deal_id: str,
    deal_name: str,
    ai_company: str,
    gross_revenue_cents: int,
    period_start: date,
    period_end: date,
) -> List[str]:
    """
    Attribute revenue from an AI deal to coalition members.

    Uses corpus size-based attribution by default.
    Returns list of earnings IDs created.
    """
    # Get all coalition members with their content stats
    result = await db.execute(
        text("""
            SELECT 
                o.organization_id,
                o.tier,
                o.coalition_rev_share_publisher,
                COALESCE(cs.sentences_count, 0) as sentences
            FROM organizations o
            LEFT JOIN coalition_content_stats cs ON 
                cs.organization_id = o.organization_id
                AND cs.period_start = :start
                AND cs.period_end = :end
            WHERE o.coalition_member = TRUE
              AND o.coalition_opted_out = FALSE
        """),
        {"start": period_start, "end": period_end},
    )
    members = result.fetchall()

    if not members:
        return []

    # Calculate total corpus size
    total_sentences = sum(m.sentences for m in members)
    if total_sentences == 0:
        return []

    earnings_ids = []
    now = datetime.now(timezone.utc)

    for member in members:
        if member.sentences == 0:
            continue

        # Calculate attribution weight
        weight = member.sentences / total_sentences

        # Get tier-based rev share (or use org override)
        rev_share = TIER_REV_SHARE.get(member.tier, TIER_REV_SHARE["starter"])
        publisher_percent = member.coalition_rev_share_publisher or rev_share["publisher"]

        # Calculate earnings
        attributed_gross = int(gross_revenue_cents * weight)
        publisher_earnings = int(attributed_gross * publisher_percent / 100)
        encypher_share = attributed_gross - publisher_earnings

        earnings_id = f"earn_{uuid4().hex[:16]}"

        await db.execute(
            text("""
                INSERT INTO coalition_earnings (
                    id, organization_id, deal_id, deal_name, ai_company,
                    period_start, period_end, gross_revenue_cents,
                    publisher_share_percent, publisher_earnings_cents,
                    encypher_share_cents, attribution_method, attribution_weight,
                    status, created_at
                )
                VALUES (
                    :id, :org_id, :deal_id, :deal_name, :ai_company,
                    :start, :end, :gross,
                    :share_percent, :publisher_earnings,
                    :encypher_share, 'corpus_size', :weight,
                    'pending', :now
                )
            """),
            {
                "id": earnings_id,
                "org_id": member.organization_id,
                "deal_id": deal_id,
                "deal_name": deal_name,
                "ai_company": ai_company,
                "start": period_start,
                "end": period_end,
                "gross": attributed_gross,
                "share_percent": publisher_percent,
                "publisher_earnings": publisher_earnings,
                "encypher_share": encypher_share,
                "weight": weight,
                "now": now,
            },
        )

        earnings_ids.append(earnings_id)

    return earnings_ids
