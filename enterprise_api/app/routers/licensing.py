"""
Licensing Agreement Management API Router.

Endpoints for managing licensing agreements, content access, and revenue distribution.
"""

import logging
from typing import List, Optional, cast
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

logger = logging.getLogger(__name__)
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_content_db, get_db
from app.middleware.licensing_auth import verify_licensing_api_key
from app.models.licensing import AgreementStatus, AICompany, DistributionStatus
from app.schemas.licensing import (
    ContentAccessLogResponse,
    ContentAccessTrack,
    ContentListResponse,
    LicensingAgreementCreate,
    LicensingAgreementCreateResponse,
    LicensingAgreementResponse,
    LicensingAgreementUpdate,
    MemberRevenueDetail,
    PayoutCreate,
    PayoutResponse,
    RevenueDistributionCreate,
    RevenueDistributionResponse,
    SuccessResponse,
)
from app.services.licensing_service import LicensingService

router = APIRouter(prefix="/licensing", tags=["Licensing"])


# ============================================================================
# Agreement Management (Admin only)
# ============================================================================


@router.post("/agreements", response_model=LicensingAgreementCreateResponse)
async def create_agreement(agreement_data: LicensingAgreementCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new licensing agreement with an AI company.

    **Admin only** - Creates agreement and generates API key for AI company.

    Returns:
        Agreement details including the API key (only shown once)
    """
    try:
        agreement, api_key = await LicensingService.create_agreement(db, agreement_data)

        # Get AI company details for response
        ai_company_result = await db.get(AICompany, agreement.ai_company_id)
        if not ai_company_result:
            raise HTTPException(status_code=404, detail="AI company not found")

        return LicensingAgreementCreateResponse(
            id=agreement.id,
            agreement_name=agreement.agreement_name,
            api_key=api_key,
            api_key_prefix=ai_company_result.api_key_prefix,
            status=agreement.status,
            created_at=agreement.created_at,
        )
    except Exception:
        logger.exception("Failed to create licensing agreement")
        raise HTTPException(status_code=400, detail="Failed to create licensing agreement")


@router.get("/agreements", response_model=List[LicensingAgreementResponse])
async def list_agreements(
    status: Optional[AgreementStatus] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=1000, description="Results per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: AsyncSession = Depends(get_db),
):
    """
    List all licensing agreements.

    **Admin only** - Returns all agreements with optional filtering.
    """
    agreements = await LicensingService.list_agreements(db=db, status=status, limit=limit, offset=offset)
    return agreements


@router.get("/agreements/{agreement_id}", response_model=LicensingAgreementResponse)
async def get_agreement(agreement_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Get details of a specific licensing agreement.

    **Admin only**
    """
    agreement = await LicensingService.get_agreement(db, agreement_id)
    if not agreement:
        raise HTTPException(status_code=404, detail="Agreement not found")
    return agreement


@router.patch("/agreements/{agreement_id}", response_model=LicensingAgreementResponse)
async def update_agreement(agreement_id: UUID, update_data: LicensingAgreementUpdate, db: AsyncSession = Depends(get_db)):
    """
    Update a licensing agreement.

    **Admin only** - Allows updating agreement terms and status.
    """
    agreement = await LicensingService.update_agreement(db, agreement_id, update_data)
    if not agreement:
        raise HTTPException(status_code=404, detail="Agreement not found")
    return agreement


@router.delete("/agreements/{agreement_id}", response_model=SuccessResponse)
async def terminate_agreement(agreement_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Terminate a licensing agreement.

    **Admin only** - Sets agreement status to terminated.
    """
    agreement = await LicensingService.terminate_agreement(db, agreement_id)
    if not agreement:
        raise HTTPException(status_code=404, detail="Agreement not found")
    return SuccessResponse(message="Agreement terminated successfully")


# ============================================================================
# AI Company Content Access
# ============================================================================


@router.get("/content", response_model=ContentListResponse)
async def list_available_content(
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    min_word_count: Optional[int] = Query(None, ge=0, description="Minimum word count"),
    include_rights_signals: bool = Query(False, description="Include rights_signals extracted from manifest_data"),
    limit: int = Query(100, ge=1, le=1000, description="Results per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    ai_company: AICompany = Depends(verify_licensing_api_key),
    db: AsyncSession = Depends(get_db),
    content_db: AsyncSession = Depends(get_content_db),
):
    """
    List available content for licensed AI company.

    **Requires AI company API key** - Returns content metadata that matches
    the terms of active licensing agreements.
    """
    # Get active agreement for this AI company
    ai_company_id = cast(UUID, ai_company.id)
    agreement = await LicensingService.get_active_agreement_for_company(db=db, ai_company_id=ai_company_id)

    if not agreement:
        raise HTTPException(status_code=403, detail="No active agreement found for this AI company")

    # Query content matching agreement terms
    content_list, total = await LicensingService.list_available_content(
        db=content_db,
        agreement=agreement,
        content_type=content_type,
        min_word_count=min_word_count,
        include_rights_signals=include_rights_signals,
        limit=limit,
        offset=offset,
    )

    if include_rights_signals and content_list:
        content_id = content_list[0].id
        owner_id = await LicensingService.get_content_owner(content_db, content_id)
        await LicensingService.track_content_access(
            db=db,
            agreement_id=cast(UUID, agreement.id),
            content_id=content_id,
            member_id=owner_id or "unknown",
            ai_company_name=cast(str, ai_company.company_name),
            access_type="list",
        )

    quota_remaining = None
    agreement_max = getattr(agreement, "max_monthly_calls", None) or getattr(agreement, "monthly_call_limit", None)
    if agreement_max:
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_count = await LicensingService.count_accesses_since(
            db=db,
            agreement_id=cast(UUID, agreement.id),
            since=month_start,
        )
        quota_remaining = max(0, agreement_max - monthly_count)
    return ContentListResponse(content=content_list, total=total, quota_remaining=quota_remaining)


@router.post("/track-access", response_model=ContentAccessLogResponse)
async def track_content_access(
    access_data: ContentAccessTrack,
    ai_company: AICompany = Depends(verify_licensing_api_key),
    db: AsyncSession = Depends(get_db),
    content_db: AsyncSession = Depends(get_content_db),
):
    """
    Track content access by AI company.

    **Requires AI company API key** - Logs when content is accessed for
    revenue attribution.
    """
    # Get the active agreement for this AI company
    ai_company_id = cast(UUID, ai_company.id)
    agreement = await LicensingService.get_active_agreement_for_company(db=db, ai_company_id=ai_company_id)

    if not agreement:
        raise HTTPException(status_code=403, detail="No active agreement found for this AI company")

    # Look up the content owner (member_id) from the content reference
    member_id = await LicensingService.get_content_owner(content_db, access_data.content_id)

    if not member_id:
        raise HTTPException(status_code=404, detail=f"Content {access_data.content_id} not found")

    # Track the access
    access_log = await LicensingService.track_content_access(
        db=db,
        agreement_id=cast(UUID, agreement.id),
        content_id=access_data.content_id,
        member_id=member_id,
        ai_company_name=cast(str, ai_company.company_name),
        access_type=access_data.access_type,
    )

    return access_log


# ============================================================================
# Revenue Distribution (Admin only)
# ============================================================================


@router.post("/distributions", response_model=RevenueDistributionResponse)
async def create_revenue_distribution(distribution_data: RevenueDistributionCreate, db: AsyncSession = Depends(get_db)):
    """
    Create revenue distribution for a period.

    **Admin only** - Calculates and creates revenue distribution based on
    content access during the specified period. Implements 70/30 split.
    """
    try:
        distribution = await LicensingService.calculate_revenue_distribution(db, distribution_data)

        # Load member revenues
        member_revenues = await LicensingService.get_member_revenues(db, cast(UUID, distribution.id))

        return RevenueDistributionResponse(
            id=distribution.id,
            agreement_id=distribution.agreement_id,
            period_start=distribution.period_start,
            period_end=distribution.period_end,
            total_revenue=distribution.total_revenue,
            encypher_share=distribution.encypher_share,
            member_pool=distribution.member_pool,
            status=distribution.status,
            created_at=distribution.created_at,
            processed_at=distribution.processed_at,
            member_revenues=[
                MemberRevenueDetail(
                    id=mr.id,
                    member_id=mr.member_id,
                    content_count=mr.content_count,
                    access_count=mr.access_count,
                    revenue_amount=mr.revenue_amount,
                    status=mr.status,
                    paid_at=mr.paid_at,
                    payment_reference=mr.payment_reference,
                )
                for mr in member_revenues
            ],
        )
    except ValueError:
        logger.exception("Invalid revenue distribution request")
        raise HTTPException(status_code=400, detail="Invalid distribution parameters")
    except Exception:
        logger.exception("Failed to create revenue distribution")
        raise HTTPException(status_code=500, detail="Failed to create revenue distribution")


@router.get("/distributions", response_model=List[RevenueDistributionResponse])
async def list_distributions(
    agreement_id: Optional[UUID] = Query(None, description="Filter by agreement"),
    status: Optional[DistributionStatus] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=1000, description="Results per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: AsyncSession = Depends(get_db),
):
    """
    List revenue distributions.

    **Admin only** - Returns all distributions with optional filtering.
    """
    distributions = await LicensingService.list_distributions(db=db, agreement_id=agreement_id, status=status, limit=limit, offset=offset)
    return distributions


@router.get("/distributions/{distribution_id}", response_model=RevenueDistributionResponse)
async def get_distribution(distribution_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Get details of a revenue distribution.

    **Admin only** - Includes breakdown of member revenues.
    """
    distribution = await LicensingService.get_distribution(db, distribution_id)
    if not distribution:
        raise HTTPException(status_code=404, detail="Distribution not found")

    # Load member revenues
    member_revenues = await LicensingService.get_member_revenues(db, distribution_id)

    return RevenueDistributionResponse(
        id=distribution.id,
        agreement_id=distribution.agreement_id,
        period_start=distribution.period_start,
        period_end=distribution.period_end,
        total_revenue=distribution.total_revenue,
        encypher_share=distribution.encypher_share,
        member_pool=distribution.member_pool,
        status=distribution.status,
        created_at=distribution.created_at,
        processed_at=distribution.processed_at,
        member_revenues=[
            MemberRevenueDetail(
                id=mr.id,
                member_id=mr.member_id,
                content_count=mr.content_count,
                access_count=mr.access_count,
                revenue_amount=mr.revenue_amount,
                status=mr.status,
                paid_at=mr.paid_at,
                payment_reference=mr.payment_reference,
            )
            for mr in member_revenues
        ],
    )


@router.post("/payouts", response_model=PayoutResponse)
async def process_payouts(payout_data: PayoutCreate, db: AsyncSession = Depends(get_db)):
    """
    Process payouts for a revenue distribution.

    **Admin only** - Initiates payment processing for all members in a distribution.

    Note: This is currently a simulation. In production, this would integrate
    with Stripe or other payment processors.
    """
    try:
        result = await LicensingService.process_payouts(db=db, distribution_id=payout_data.distribution_id, payment_method=payout_data.payment_method)

        return PayoutResponse(**result)
    except ValueError:
        logger.exception("Invalid payout request")
        raise HTTPException(status_code=400, detail="Invalid payout parameters")
    except Exception:
        logger.exception("Failed to process payouts")
        raise HTTPException(status_code=500, detail="Failed to process payouts")
