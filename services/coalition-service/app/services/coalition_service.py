"""
Coalition Service - Business Logic
"""
import uuid
from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import structlog

from ..db.models import (
    CoalitionMember,
    CoalitionContent,
    LicensingAgreement,
    ContentAccessLog,
    RevenueDistribution,
    MemberRevenue,
    CoalitionSettings,
)
from ..models.schemas import (
    CoalitionJoinRequest,
    CoalitionMemberResponse,
    CoalitionStatsResponse,
    ContentStats,
    RevenueStats,
    CoalitionStats,
    RevenueResponse,
    RevenueDistributionDetail,
)

logger = structlog.get_logger()


class CoalitionService:
    """Service for managing coalition operations"""

    @staticmethod
    def join_coalition(db: Session, request: CoalitionJoinRequest) -> CoalitionMemberResponse:
        """
        Enroll a user in the coalition
        """
        # Check if user is already a member
        existing_member = (
            db.query(CoalitionMember).filter(CoalitionMember.user_id == request.user_id).first()
        )

        if existing_member:
            if existing_member.status == "opted_out":
                # Re-activate membership
                existing_member.status = "active"
                existing_member.opted_out_at = None
                existing_member.opt_out_reason = None
                existing_member.tier = request.tier
                existing_member.updated_at = datetime.utcnow()
                db.commit()
                db.refresh(existing_member)

                logger.info(
                    "coalition_member_reactivated",
                    user_id=str(request.user_id),
                    member_id=str(existing_member.id),
                )

                return CoalitionMemberResponse(
                    member_id=existing_member.id,
                    user_id=existing_member.user_id,
                    organization_id=existing_member.organization_id,
                    joined_at=existing_member.joined_at,
                    status=existing_member.status,
                    tier=existing_member.tier,
                )
            else:
                # Already an active member
                logger.info(
                    "coalition_member_already_exists",
                    user_id=str(request.user_id),
                    member_id=str(existing_member.id),
                )
                return CoalitionMemberResponse(
                    member_id=existing_member.id,
                    user_id=existing_member.user_id,
                    organization_id=existing_member.organization_id,
                    joined_at=existing_member.joined_at,
                    status=existing_member.status,
                    tier=existing_member.tier,
                )

        # Create new member
        new_member = CoalitionMember(
            id=uuid.uuid4(),
            user_id=request.user_id,
            organization_id=request.organization_id,
            joined_at=datetime.utcnow(),
            status="active",
            tier=request.tier,
            created_at=datetime.utcnow(),
        )

        db.add(new_member)
        db.commit()
        db.refresh(new_member)

        logger.info(
            "coalition_member_created",
            user_id=str(request.user_id),
            member_id=str(new_member.id),
            tier=request.tier,
        )

        return CoalitionMemberResponse(
            member_id=new_member.id,
            user_id=new_member.user_id,
            organization_id=new_member.organization_id,
            joined_at=new_member.joined_at,
            status=new_member.status,
            tier=new_member.tier,
        )

    @staticmethod
    def leave_coalition(db: Session, user_id: uuid.UUID, reason: Optional[str] = None) -> bool:
        """
        Opt-out from coalition
        """
        member = db.query(CoalitionMember).filter(CoalitionMember.user_id == user_id).first()

        if not member:
            logger.warning("coalition_member_not_found", user_id=str(user_id))
            return False

        if member.status == "opted_out":
            logger.info("coalition_member_already_opted_out", user_id=str(user_id))
            return True

        member.status = "opted_out"
        member.opted_out_at = datetime.utcnow()
        member.opt_out_reason = reason
        member.updated_at = datetime.utcnow()

        db.commit()

        logger.info(
            "coalition_member_opted_out",
            user_id=str(user_id),
            member_id=str(member.id),
            reason=reason,
        )

        return True

    @staticmethod
    def get_member_stats(db: Session, user_id: uuid.UUID) -> Optional[CoalitionStatsResponse]:
        """
        Get coalition statistics for a member
        """
        member = db.query(CoalitionMember).filter(CoalitionMember.user_id == user_id).first()

        if not member:
            logger.warning("coalition_member_not_found", user_id=str(user_id))
            return None

        # Content stats
        content_query = db.query(
            func.count(CoalitionContent.id).label("total_documents"),
            func.sum(CoalitionContent.word_count).label("total_word_count"),
            func.sum(CoalitionContent.verification_count).label("verification_count"),
            func.max(CoalitionContent.signed_at).label("last_signed"),
        ).filter(CoalitionContent.member_id == member.id)

        content_stats_data = content_query.first()

        content_stats = ContentStats(
            total_documents=content_stats_data.total_documents or 0,
            total_word_count=int(content_stats_data.total_word_count or 0),
            verification_count=int(content_stats_data.verification_count or 0),
            last_signed=content_stats_data.last_signed,
        )

        # Revenue stats
        revenue_query = db.query(
            func.sum(
                func.case((MemberRevenue.status == "paid", MemberRevenue.revenue_amount), else_=0)
            ).label("paid"),
            func.sum(
                func.case((MemberRevenue.status == "pending", MemberRevenue.revenue_amount), else_=0)
            ).label("pending"),
        ).filter(MemberRevenue.member_id == member.id)

        revenue_stats_data = revenue_query.first()

        paid = Decimal(str(revenue_stats_data.paid or 0))
        pending = Decimal(str(revenue_stats_data.pending or 0))
        total_earned = paid + pending

        # Get next payout date (first day of next month)
        today = date.today()
        if today.month == 12:
            next_payout_date = date(today.year + 1, 1, 1)
        else:
            next_payout_date = date(today.year, today.month + 1, 1)

        revenue_stats = RevenueStats(
            total_earned=total_earned,
            pending=pending,
            paid=paid,
            currency="USD",
            next_payout_date=next_payout_date,
        )

        # Coalition-wide stats
        total_members = db.query(func.count(CoalitionMember.id)).filter(
            CoalitionMember.status == "active"
        ).scalar()

        total_content_pool = db.query(func.count(CoalitionContent.id)).scalar()

        active_agreements = db.query(func.count(LicensingAgreement.id)).filter(
            LicensingAgreement.status == "active"
        ).scalar()

        coalition_stats = CoalitionStats(
            total_members=total_members or 0,
            total_content_pool=total_content_pool or 0,
            active_agreements=active_agreements or 0,
        )

        return CoalitionStatsResponse(
            member_id=member.id,
            status=member.status,
            joined_at=member.joined_at,
            content_stats=content_stats,
            revenue_stats=revenue_stats,
            coalition_stats=coalition_stats,
        )

    @staticmethod
    def get_member_revenue(db: Session, user_id: uuid.UUID) -> Optional[RevenueResponse]:
        """
        Get detailed revenue breakdown for a member
        """
        member = db.query(CoalitionMember).filter(CoalitionMember.user_id == user_id).first()

        if not member:
            logger.warning("coalition_member_not_found", user_id=str(user_id))
            return None

        # Get all revenue records
        revenue_records = (
            db.query(MemberRevenue, RevenueDistribution, LicensingAgreement)
            .join(RevenueDistribution, MemberRevenue.distribution_id == RevenueDistribution.id)
            .join(LicensingAgreement, RevenueDistribution.agreement_id == LicensingAgreement.id)
            .filter(MemberRevenue.member_id == member.id)
            .order_by(RevenueDistribution.period_start.desc())
            .all()
        )

        distributions = []
        total_earned = Decimal("0")

        for revenue, distribution, agreement in revenue_records:
            total_earned += revenue.revenue_amount

            period = f"{distribution.period_start.year}-{distribution.period_start.month:02d}"

            detail = RevenueDistributionDetail(
                period=period,
                amount=revenue.revenue_amount,
                status=revenue.status,
                agreement_name=agreement.agreement_name,
                content_accessed=revenue.content_count,
                access_count=revenue.access_count,
                paid_at=revenue.paid_at,
                payment_method=revenue.payment_method,
                payment_reference=revenue.payment_reference,
            )
            distributions.append(detail)

        return RevenueResponse(
            total_earned=total_earned,
            currency="USD",
            distributions=distributions,
        )

    @staticmethod
    def index_content(
        db: Session,
        member_id: uuid.UUID,
        document_id: uuid.UUID,
        content_hash: str,
        content_type: Optional[str] = None,
        word_count: Optional[int] = None,
        signed_at: Optional[datetime] = None,
    ) -> CoalitionContent:
        """
        Index signed content for coalition
        """
        # Check if content already indexed
        existing_content = (
            db.query(CoalitionContent)
            .filter(CoalitionContent.document_id == document_id)
            .first()
        )

        if existing_content:
            logger.info(
                "coalition_content_already_indexed",
                document_id=str(document_id),
                content_id=str(existing_content.id),
            )
            return existing_content

        # Create new content record
        new_content = CoalitionContent(
            id=uuid.uuid4(),
            member_id=member_id,
            document_id=document_id,
            content_hash=content_hash,
            content_type=content_type,
            word_count=word_count,
            signed_at=signed_at or datetime.utcnow(),
            indexed_at=datetime.utcnow(),
        )

        db.add(new_content)
        db.commit()
        db.refresh(new_content)

        logger.info(
            "coalition_content_indexed",
            member_id=str(member_id),
            document_id=str(document_id),
            content_id=str(new_content.id),
        )

        return new_content

    @staticmethod
    def get_setting(db: Session, setting_key: str) -> Optional[dict]:
        """
        Get coalition setting by key
        """
        setting = (
            db.query(CoalitionSettings)
            .filter(CoalitionSettings.setting_key == setting_key)
            .first()
        )

        if not setting:
            return None

        return setting.setting_value
