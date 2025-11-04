"""
Coalition Service API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import structlog

from ...db.session import get_db
from ...models.schemas import (
    CoalitionJoinRequest,
    CoalitionMemberResponse,
    CoalitionLeaveRequest,
    CoalitionStatsResponse,
    RevenueResponse,
    LicensingAgreementCreate,
    LicensingAgreementResponse,
    LicensingAgreementUpdate,
    ContentAccessTrack,
    ContentAccessResponse,
    CoalitionContentCreate,
    CoalitionContentResponse,
    SuccessResponse,
    ErrorResponse,
)
from ...services.coalition_service import CoalitionService
from ...db.models import (
    LicensingAgreement,
    ContentAccessLog,
    CoalitionContent,
)

logger = structlog.get_logger()
router = APIRouter()


# Coalition Member Endpoints
@router.post("/join", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def join_coalition(request: CoalitionJoinRequest, db: Session = Depends(get_db)):
    """
    Join the coalition (or auto-join on signup)
    """
    try:
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
async def leave_coalition(request: CoalitionLeaveRequest, db: Session = Depends(get_db)):
    """
    Leave the coalition (opt-out)
    """
    try:
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
async def get_coalition_status(user_id: UUID, db: Session = Depends(get_db)):
    """
    Get coalition membership status
    """
    try:
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
async def get_coalition_stats(user_id: UUID, db: Session = Depends(get_db)):
    """
    Get coalition statistics for a member
    """
    try:
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
async def get_member_revenue(user_id: UUID, db: Session = Depends(get_db)):
    """
    Get detailed revenue breakdown for a member
    """
    try:
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
    db: Session = Depends(get_db)
):
    """
    Get aggregated content pool (Admin only)
    """
    try:
        content_query = db.query(CoalitionContent).offset(offset).limit(limit).all()

        total_count = db.query(CoalitionContent).count()

        return SuccessResponse(
            success=True,
            data={
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "content": [
                    {
                        "id": str(c.id),
                        "member_id": str(c.member_id),
                        "document_id": str(c.document_id),
                        "content_type": c.content_type,
                        "word_count": c.word_count,
                        "signed_at": c.signed_at.isoformat(),
                        "verification_count": c.verification_count,
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
