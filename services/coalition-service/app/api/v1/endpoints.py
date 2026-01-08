"""
Coalition Service API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from datetime import datetime, date
import structlog
import httpx

from ...db.session import get_db
from ...core.config import settings
from ...models.schemas import (
    CoalitionJoinRequest,
    CoalitionLeaveRequest,
    LicensingAgreementCreate,
    LicensingAgreementUpdate,
    ContentAccessTrack,
    CoalitionContentCreate,
    SuccessResponse,
)
from ...services.coalition_service import CoalitionService
from ...db.models import (
    LicensingAgreement,
    ContentAccessLog,
    CoalitionContent,
)

logger = structlog.get_logger()
router = APIRouter()


async def get_current_context(authorization: str = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    api_key = authorization.split(" ", 1)[1].strip()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.KEY_SERVICE_URL}/api/v1/keys/validate",
                json={"key": api_key},
                timeout=5.0,
            )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Key service unavailable",
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = response.json()
    data = payload.get("data")
    if not payload.get("success") or not isinstance(data, dict):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return data


def _enforce_user_match(*, context: dict, user_id: UUID) -> None:
    context_user_id = context.get("user_id")
    if not context_user_id or str(context_user_id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )


# Coalition Member Endpoints
@router.post("/join", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def join_coalition(
    request: CoalitionJoinRequest,
    db: Session = Depends(get_db),
    context: dict = Depends(get_current_context),
):
    """
    Join the coalition (or auto-join on signup)
    """
    try:
        _enforce_user_match(context=context, user_id=request.user_id)
        member = CoalitionService.join_coalition(db, request)

        return SuccessResponse(
            success=True,
            message="Successfully joined coalition",
            data={
                "member_id": str(member.member_id),
                "joined_at": member.joined_at.isoformat(),
                "status": member.status,
                "tier": member.tier,
            },
        )
    except Exception as e:
        logger.error("join_coalition_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to join coalition: {str(e)}",
        )


@router.post("/leave", response_model=SuccessResponse)
async def leave_coalition(
    request: CoalitionLeaveRequest,
    db: Session = Depends(get_db),
    context: dict = Depends(get_current_context),
):
    """
    Leave the coalition (opt-out)
    """
    try:
        _enforce_user_match(context=context, user_id=request.user_id)
        success = CoalitionService.leave_coalition(db, request.user_id, request.reason)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coalition member not found",
            )

        return SuccessResponse(
            success=True,
            message="Successfully left coalition",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("leave_coalition_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to leave coalition: {str(e)}",
        )


@router.get("/status/{user_id}", response_model=SuccessResponse)
async def get_coalition_status(
    user_id: UUID,
    db: Session = Depends(get_db),
    context: dict = Depends(get_current_context),
):
    """
    Get coalition membership status
    """
    try:
        _enforce_user_match(context=context, user_id=user_id)
        from ...db.models import CoalitionMember

        member = db.query(CoalitionMember).filter(CoalitionMember.user_id == user_id).first()

        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coalition member not found",
            )

        return SuccessResponse(
            success=True,
            data={
                "member_id": str(member.id),
                "user_id": str(member.user_id),
                "status": member.status,
                "tier": member.tier,
                "joined_at": member.joined_at.isoformat(),
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_coalition_status_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get coalition status: {str(e)}",
        )


@router.get("/stats/{user_id}", response_model=SuccessResponse)
async def get_coalition_stats(
    user_id: UUID,
    db: Session = Depends(get_db),
    context: dict = Depends(get_current_context),
):
    """
    Get coalition statistics for a member
    """
    try:
        _enforce_user_match(context=context, user_id=user_id)
        stats = CoalitionService.get_member_stats(db, user_id)

        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coalition member not found",
            )

        return SuccessResponse(
            success=True,
            data=stats.model_dump(),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_coalition_stats_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get coalition stats: {str(e)}",
        )


@router.get("/revenue/{user_id}", response_model=SuccessResponse)
async def get_member_revenue(
    user_id: UUID,
    db: Session = Depends(get_db),
    context: dict = Depends(get_current_context),
):
    """
    Get detailed revenue breakdown for a member
    """
    try:
        _enforce_user_match(context=context, user_id=user_id)
        revenue = CoalitionService.get_member_revenue(db, user_id)

        if not revenue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coalition member not found",
            )

        return SuccessResponse(
            success=True,
            data=revenue.model_dump(),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_member_revenue_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get member revenue: {str(e)}",
        )


# Licensing Agreement Endpoints (Admin)
@router.post("/agreements", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def create_licensing_agreement(
    agreement: LicensingAgreementCreate, db: Session = Depends(get_db)
):
    """
    Create a licensing agreement (Admin only)
    """
    try:
        import uuid as uuid_lib

        new_agreement = LicensingAgreement(
            id=uuid_lib.uuid4(),
            agreement_name=agreement.agreement_name,
            ai_company_name=agreement.ai_company_name,
            ai_company_id=agreement.ai_company_id,
            agreement_type=agreement.agreement_type,
            total_value=agreement.total_value,
            currency=agreement.currency,
            payment_frequency=agreement.payment_frequency,
            content_types=agreement.content_types,
            min_word_count=agreement.min_word_count,
            date_range_start=agreement.date_range_start,
            date_range_end=agreement.date_range_end,
            start_date=agreement.start_date,
            end_date=agreement.end_date,
            signed_date=agreement.signed_date,
            created_by=agreement.created_by,
        )

        db.add(new_agreement)
        db.commit()
        db.refresh(new_agreement)

        logger.info("licensing_agreement_created", agreement_id=str(new_agreement.id))

        return SuccessResponse(
            success=True,
            message="Licensing agreement created successfully",
            data={"agreement_id": str(new_agreement.id)},
        )
    except Exception as e:
        logger.error("create_licensing_agreement_failed", error=str(e))
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create licensing agreement: {str(e)}",
        )


@router.get("/agreements", response_model=SuccessResponse)
async def list_licensing_agreements(db: Session = Depends(get_db)):
    """
    List all licensing agreements (Admin only)
    """
    try:
        agreements = db.query(LicensingAgreement).all()

        return SuccessResponse(
            success=True,
            data={
                "agreements": [
                    {
                        "id": str(a.id),
                        "agreement_name": a.agreement_name,
                        "ai_company_name": a.ai_company_name,
                        "status": a.status,
                        "total_value": float(a.total_value),
                        "currency": a.currency,
                        "start_date": a.start_date.isoformat(),
                        "end_date": a.end_date.isoformat(),
                    }
                    for a in agreements
                ]
            },
        )
    except Exception as e:
        logger.error("list_licensing_agreements_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list licensing agreements: {str(e)}",
        )


# Content Access Tracking
@router.post("/track-access", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def track_content_access(access: ContentAccessTrack, db: Session = Depends(get_db)):
    """
    Track content access by AI company
    """
    try:
        import uuid as uuid_lib
        from datetime import datetime

        access_log = ContentAccessLog(
            id=uuid_lib.uuid4(),
            agreement_id=access.agreement_id,
            content_id=access.content_id,
            member_id=access.member_id,
            accessed_at=datetime.utcnow(),
            access_type=access.access_type,
            ai_company_name=access.ai_company_name,
            metadata=access.metadata,
        )

        db.add(access_log)
        db.commit()
        db.refresh(access_log)

        # Update verification count
        content = db.query(CoalitionContent).filter(CoalitionContent.id == access.content_id).first()
        if content:
            content.verification_count += 1
            content.last_verified_at = datetime.utcnow()
            db.commit()

        logger.info("content_access_tracked", access_log_id=str(access_log.id))

        return SuccessResponse(
            success=True,
            message="Content access tracked successfully",
            data={"access_log_id": str(access_log.id)},
        )
    except Exception as e:
        logger.error("track_content_access_failed", error=str(e))
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to track content access: {str(e)}",
        )


# Content Indexing
@router.post("/content", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def index_content(content: CoalitionContentCreate, db: Session = Depends(get_db)):
    """
    Index signed content for coalition
    """
    try:
        indexed_content = CoalitionService.index_content(
            db=db,
            member_id=content.member_id,
            document_id=content.document_id,
            content_hash=content.content_hash,
            content_type=content.content_type,
            word_count=content.word_count,
            signed_at=content.signed_at,
        )

        return SuccessResponse(
            success=True,
            message="Content indexed successfully",
            data={"content_id": str(indexed_content.id)},
        )
    except Exception as e:
        logger.error("index_content_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to index content: {str(e)}",
        )


@router.get("/content-pool", response_model=SuccessResponse)
async def get_content_pool(
    limit: int = 100,
    offset: int = 0,
    content_type: Optional[str] = None,
    min_word_count: Optional[int] = None,
    member_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
):
    """
    Get aggregated content pool with filtering (Admin only)

    Filters:
    - content_type: Filter by content type (article, blog, social_post)
    - min_word_count: Minimum word count
    - member_id: Filter by specific member
    """
    try:
        from sqlalchemy import and_

        # Build query with filters
        query = db.query(CoalitionContent)

        filters = []
        if content_type:
            filters.append(CoalitionContent.content_type == content_type)
        if min_word_count:
            filters.append(CoalitionContent.word_count >= min_word_count)
        if member_id:
            filters.append(CoalitionContent.member_id == member_id)

        if filters:
            query = query.filter(and_(*filters))

        # Get total count with filters
        total_count = query.count()

        # Get paginated results
        content_query = query.order_by(CoalitionContent.indexed_at.desc()).offset(offset).limit(limit).all()

        return SuccessResponse(
            success=True,
            data={
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "filters": {
                    "content_type": content_type,
                    "min_word_count": min_word_count,
                    "member_id": str(member_id) if member_id else None,
                },
                "content": [
                    {
                        "id": str(c.id),
                        "member_id": str(c.member_id),
                        "document_id": str(c.document_id),
                        "content_hash": c.content_hash,
                        "content_type": c.content_type,
                        "word_count": c.word_count,
                        "signed_at": c.signed_at.isoformat(),
                        "verification_count": c.verification_count,
                        "last_verified_at": c.last_verified_at.isoformat() if c.last_verified_at else None,
                        "indexed_at": c.indexed_at.isoformat(),
                    }
                    for c in content_query
                ],
            },
        )
    except Exception as e:
        logger.error("get_content_pool_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get content pool: {str(e)}",
        )


@router.get("/content-pool/stats", response_model=SuccessResponse)
async def get_content_pool_stats(db: Session = Depends(get_db)):
    """
    Get content pool statistics (Admin only)
    """
    try:
        from sqlalchemy import func

        # Overall stats
        total_content = db.query(func.count(CoalitionContent.id)).scalar()
        total_words = db.query(func.sum(CoalitionContent.word_count)).scalar() or 0
        total_verifications = db.query(func.sum(CoalitionContent.verification_count)).scalar() or 0

        # By content type
        type_stats = db.query(
            CoalitionContent.content_type,
            func.count(CoalitionContent.id).label("count"),
            func.sum(CoalitionContent.word_count).label("total_words"),
        ).group_by(CoalitionContent.content_type).all()

        # Recent activity
        from datetime import datetime, timedelta
        last_24h = datetime.utcnow() - timedelta(hours=24)
        recent_content = db.query(func.count(CoalitionContent.id)).filter(
            CoalitionContent.indexed_at >= last_24h
        ).scalar()

        return SuccessResponse(
            success=True,
            data={
                "overall": {
                    "total_content": total_content or 0,
                    "total_words": int(total_words),
                    "total_verifications": int(total_verifications),
                    "avg_word_count": int(total_words / total_content) if total_content > 0 else 0,
                },
                "by_type": [
                    {
                        "content_type": t.content_type or "unknown",
                        "count": t.count,
                        "total_words": int(t.total_words or 0),
                    }
                    for t in type_stats
                ],
                "recent_activity": {
                    "last_24_hours": recent_content or 0,
                },
            },
        )
    except Exception as e:
        logger.error("get_content_pool_stats_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get content pool stats: {str(e)}",
        )
# Revenue Distribution Endpoints (Admin)
@router.post("/distributions/calculate", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def calculate_distribution(
    agreement_id: UUID,
    period_start: date,
    period_end: date,
    calculation_method: str = "usage_based",
    db: Session = Depends(get_db)
):
    """
    Calculate revenue distribution for an agreement period (Admin only)

    calculation_method options:
    - usage_based: Distribute based on content access count
    - equal_split: Equal distribution among contributors
    - weighted: Weighted by content quality (word count)
    """
    try:
        from ...services.revenue_service import RevenueService

        distribution = RevenueService.calculate_distribution(
            db=db,
            agreement_id=agreement_id,
            period_start=period_start,
            period_end=period_end,
            calculation_method=calculation_method,
        )

        logger.info("distribution_calculated", distribution_id=str(distribution.id))

        return SuccessResponse(
            success=True,
            message="Distribution calculated successfully",
            data={
                "distribution_id": str(distribution.id),
                "total_revenue": float(distribution.total_revenue),
                "encypher_share": float(distribution.encypher_share),
                "member_pool": float(distribution.member_pool),
                "content_count": distribution.total_content_count,
                "access_count": distribution.total_access_count,
                "calculation_method": distribution.calculation_method,
                "status": distribution.status,
            },
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error("calculate_distribution_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate distribution: {str(e)}",
        )


@router.get("/distributions", response_model=SuccessResponse)
async def list_distributions(
    agreement_id: Optional[UUID] = None,
    status_filter: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    List revenue distributions (Admin only)
    """
    try:
        from ...db.models import RevenueDistribution

        query = db.query(RevenueDistribution)

        if agreement_id:
            query = query.filter(RevenueDistribution.agreement_id == agreement_id)
        if status_filter:
            query = query.filter(RevenueDistribution.status == status_filter)

        total_count = query.count()
        distributions = query.order_by(RevenueDistribution.created_at.desc()).offset(offset).limit(limit).all()

        return SuccessResponse(
            success=True,
            data={
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "distributions": [
                    {
                        "id": str(d.id),
                        "agreement_id": str(d.agreement_id),
                        "period_start": d.period_start.isoformat(),
                        "period_end": d.period_end.isoformat(),
                        "total_revenue": float(d.total_revenue),
                        "encypher_share": float(d.encypher_share),
                        "member_pool": float(d.member_pool),
                        "content_count": d.total_content_count,
                        "access_count": d.total_access_count,
                        "calculation_method": d.calculation_method,
                        "status": d.status,
                        "calculated_at": d.calculated_at.isoformat() if d.calculated_at else None,
                        "paid_at": d.paid_at.isoformat() if d.paid_at else None,
                    }
                    for d in distributions
                ],
            },
        )
    except Exception as e:
        logger.error("list_distributions_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list distributions: {str(e)}",
        )


@router.post("/distributions/{distribution_id}/mark-paid", response_model=SuccessResponse)
async def mark_distribution_paid(
    distribution_id: UUID,
    payment_method: str = "stripe",
    db: Session = Depends(get_db)
):
    """
    Mark a distribution as paid (Admin only)
    """
    try:
        from ...services.revenue_service import RevenueService

        success = RevenueService.mark_distribution_paid(
            db=db,
            distribution_id=distribution_id,
            payment_method=payment_method,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Distribution not found",
            )

        return SuccessResponse(
            success=True,
            message="Distribution marked as paid",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("mark_distribution_paid_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark distribution as paid: {str(e)}",
        )


@router.get("/distributions/{distribution_id}/payouts", response_model=SuccessResponse)
async def get_distribution_payouts(
    distribution_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get member payouts for a distribution (Admin only)
    """
    try:
        from ...db.models import MemberRevenue, CoalitionMember

        payouts = db.query(MemberRevenue, CoalitionMember).join(
            CoalitionMember, MemberRevenue.member_id == CoalitionMember.id
        ).filter(
            MemberRevenue.distribution_id == distribution_id
        ).all()

        return SuccessResponse(
            success=True,
            data={
                "distribution_id": str(distribution_id),
                "payouts": [
                    {
                        "id": str(p.MemberRevenue.id),
                        "member_id": str(p.MemberRevenue.member_id),
                        "user_id": str(p.CoalitionMember.user_id),
                        "tier": p.CoalitionMember.tier,
                        "content_count": p.MemberRevenue.content_count,
                        "access_count": p.MemberRevenue.access_count,
                        "contribution_percentage": float(p.MemberRevenue.contribution_percentage),
                        "revenue_amount": float(p.MemberRevenue.revenue_amount),
                        "currency": p.MemberRevenue.currency,
                        "status": p.MemberRevenue.status,
                        "payment_method": p.MemberRevenue.payment_method,
                        "payment_reference": p.MemberRevenue.payment_reference,
                        "paid_at": p.MemberRevenue.paid_at.isoformat() if p.MemberRevenue.paid_at else None,
                    }
                    for p in payouts
                ],
            },
        )
    except Exception as e:
        logger.error("get_distribution_payouts_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get distribution payouts: {str(e)}",
        )


@router.get("/payouts/pending", response_model=SuccessResponse)
async def get_pending_payouts(
    min_amount: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """
    Get all pending payouts (Admin only)
    """
    try:
        from ...services.revenue_service import RevenueService
        from decimal import Decimal

        min_decimal = Decimal(str(min_amount)) if min_amount else None
        payouts = RevenueService.get_pending_payouts(db, min_decimal)

        return SuccessResponse(
            success=True,
            data={
                "total_count": len(payouts),
                "total_amount": float(sum(p.revenue_amount for p in payouts)),
                "payouts": [
                    {
                        "id": str(p.id),
                        "member_id": str(p.member_id),
                        "distribution_id": str(p.distribution_id),
                        "revenue_amount": float(p.revenue_amount),
                        "currency": p.currency,
                        "created_at": p.created_at.isoformat(),
                    }
                    for p in payouts
                ],
            },
        )
    except Exception as e:
        logger.error("get_pending_payouts_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pending payouts: {str(e)}",
        )


# Licensing Agreement Management Endpoints (Admin)
@router.patch("/agreements/{agreement_id}", response_model=SuccessResponse)
async def update_licensing_agreement(
    agreement_id: UUID,
    update: LicensingAgreementUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a licensing agreement (Admin only)
    """
    try:
        agreement = db.query(LicensingAgreement).filter(
            LicensingAgreement.id == agreement_id
        ).first()

        if not agreement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agreement not found",
            )

        # Update fields
        if update.agreement_name:
            agreement.agreement_name = update.agreement_name
        if update.status:
            agreement.status = update.status
        if update.total_value:
            agreement.total_value = update.total_value
        if update.payment_frequency:
            agreement.payment_frequency = update.payment_frequency
        if update.signed_date:
            agreement.signed_date = update.signed_date

        agreement.updated_at = datetime.utcnow()

        db.commit()

        logger.info("licensing_agreement_updated", agreement_id=str(agreement_id))

        return SuccessResponse(
            success=True,
            message="Agreement updated successfully",
            data={"agreement_id": str(agreement_id)},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("update_licensing_agreement_failed", error=str(e))
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update agreement: {str(e)}",
        )


@router.post("/agreements/{agreement_id}/activate", response_model=SuccessResponse)
async def activate_licensing_agreement(
    agreement_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Activate a licensing agreement (Admin only)

    Validates that:
    - Agreement is in draft status
    - Has valid date range
    - Has content scope defined
    """
    try:
        agreement = db.query(LicensingAgreement).filter(
            LicensingAgreement.id == agreement_id
        ).first()

        if not agreement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agreement not found",
            )

        # Validate can be activated
        if agreement.status == "active":
            return SuccessResponse(
                success=True,
                message="Agreement is already active",
            )

        if agreement.status not in ["draft"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot activate agreement with status: {agreement.status}",
            )

        # Validate date range
        if agreement.start_date > agreement.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start date must be before end date",
            )

        # Activate
        agreement.status = "active"
        agreement.updated_at = datetime.utcnow()

        db.commit()

        logger.info("licensing_agreement_activated", agreement_id=str(agreement_id))

        return SuccessResponse(
            success=True,
            message="Agreement activated successfully",
            data={
                "agreement_id": str(agreement_id),
                "status": "active",
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("activate_licensing_agreement_failed", error=str(e))
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate agreement: {str(e)}",
        )


@router.get("/agreements/{agreement_id}/eligible-content", response_model=SuccessResponse)
async def get_eligible_content(
    agreement_id: UUID,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get content eligible for a licensing agreement based on its scope (Admin only)
    """
    try:
        agreement = db.query(LicensingAgreement).filter(
            LicensingAgreement.id == agreement_id
        ).first()

        if not agreement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agreement not found",
            )

        # Build query based on agreement scope
        query = db.query(CoalitionContent)

        # Filter by content types if specified
        if agreement.content_types:
            query = query.filter(CoalitionContent.content_type.in_(agreement.content_types))

        # Filter by minimum word count if specified
        if agreement.min_word_count:
            query = query.filter(CoalitionContent.word_count >= agreement.min_word_count)

        # Filter by date range if specified
        if agreement.date_range_start:
            query = query.filter(CoalitionContent.signed_at >= agreement.date_range_start)
        if agreement.date_range_end:
            query = query.filter(CoalitionContent.signed_at <= agreement.date_range_end)

        total_count = query.count()
        content = query.offset(offset).limit(limit).all()

        return SuccessResponse(
            success=True,
            data={
                "agreement_id": str(agreement_id),
                "total_eligible": total_count,
                "limit": limit,
                "offset": offset,
                "content": [
                    {
                        "id": str(c.id),
                        "document_id": str(c.document_id),
                        "content_type": c.content_type,
                        "word_count": c.word_count,
                        "signed_at": c.signed_at.isoformat(),
                    }
                    for c in content
                ],
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_eligible_content_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get eligible content: {str(e)}",
        )
