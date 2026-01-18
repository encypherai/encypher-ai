"""
Revenue Distribution Service
"""

import uuid
from datetime import datetime, date
from typing import Optional, List, Dict
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import structlog

from ..db.models import (
    LicensingAgreement,
    ContentAccessLog,
    RevenueDistribution,
    MemberRevenue,
    CoalitionContent,
)

logger = structlog.get_logger()


class RevenueService:
    """Service for revenue distribution calculations"""

    @staticmethod
    def get_revenue_split(db: Session) -> Dict[str, int]:
        """Get revenue split from settings"""
        from ..services.coalition_service import CoalitionService

        split_setting = CoalitionService.get_setting(db, "revenue_split")
        if split_setting:
            return {
                "encypher": split_setting.get("encypher", 30),
                "members": split_setting.get("members", 70),
            }
        return {"encypher": 30, "members": 70}

    @staticmethod
    def calculate_distribution(
        db: Session,
        agreement_id: uuid.UUID,
        period_start: date,
        period_end: date,
        calculation_method: str = "usage_based",
    ) -> RevenueDistribution:
        """
        Calculate revenue distribution for an agreement period

        Args:
            db: Database session
            agreement_id: Licensing agreement ID
            period_start: Start of distribution period
            period_end: End of distribution period
            calculation_method: Method to use (usage_based, equal_split, weighted)

        Returns:
            RevenueDistribution record
        """
        # Get agreement
        agreement = db.query(LicensingAgreement).filter(LicensingAgreement.id == agreement_id).first()

        if not agreement:
            raise ValueError(f"Agreement {agreement_id} not found")

        if agreement.status != "active":
            raise ValueError(f"Agreement {agreement_id} is not active")

        # Calculate total revenue for this period
        total_revenue = RevenueService._calculate_period_revenue(agreement, period_start, period_end)

        # Get revenue split
        split = RevenueService.get_revenue_split(db)
        encypher_share = total_revenue * Decimal(split["encypher"]) / Decimal(100)
        member_pool = total_revenue * Decimal(split["members"]) / Decimal(100)

        # Get content access in this period
        access_logs = (
            db.query(ContentAccessLog)
            .filter(
                and_(
                    ContentAccessLog.agreement_id == agreement_id,
                    ContentAccessLog.accessed_at >= period_start,
                    ContentAccessLog.accessed_at < period_end,
                )
            )
            .all()
        )

        # Count unique content and total accesses
        unique_content = set()
        for log in access_logs:
            unique_content.add(log.content_id)

        # Create distribution record
        distribution = RevenueDistribution(
            id=uuid.uuid4(),
            agreement_id=agreement_id,
            period_start=period_start,
            period_end=period_end,
            total_revenue=total_revenue,
            encypher_share=encypher_share,
            member_pool=member_pool,
            total_content_count=len(unique_content),
            total_access_count=len(access_logs),
            calculation_method=calculation_method,
            status="pending",
            created_at=datetime.utcnow(),
        )

        db.add(distribution)
        db.commit()
        db.refresh(distribution)

        logger.info(
            "revenue_distribution_created",
            distribution_id=str(distribution.id),
            agreement_id=str(agreement_id),
            total_revenue=float(total_revenue),
            member_pool=float(member_pool),
        )

        # Calculate member distributions
        if calculation_method == "usage_based":
            RevenueService._distribute_usage_based(db, distribution, access_logs)
        elif calculation_method == "equal_split":
            RevenueService._distribute_equal_split(db, distribution, list(unique_content))
        elif calculation_method == "weighted":
            RevenueService._distribute_weighted(db, distribution, access_logs)
        else:
            raise ValueError(f"Unknown calculation method: {calculation_method}")

        # Mark as calculated
        distribution.status = "calculated"
        distribution.calculated_at = datetime.utcnow()
        db.commit()

        logger.info(
            "revenue_distribution_calculated",
            distribution_id=str(distribution.id),
            method=calculation_method,
        )

        return distribution

    @staticmethod
    def _calculate_period_revenue(
        agreement: LicensingAgreement,
        period_start: date,
        period_end: date,
    ) -> Decimal:
        """
        Calculate revenue for a specific period based on agreement terms

        For simplicity, we'll divide total value by number of periods
        In production, this would be more sophisticated based on payment_frequency
        """
        if agreement.payment_frequency == "one_time":
            # One-time payment counts for the first period only
            if period_start <= agreement.start_date <= period_end:
                return Decimal(str(agreement.total_value))
            else:
                return Decimal("0")

        # Calculate number of periods in agreement
        days_in_agreement = (agreement.end_date - agreement.start_date).days
        days_in_period = (period_end - period_start).days

        if days_in_agreement <= 0 or days_in_period <= 0:
            return Decimal("0")

        # Pro-rate the revenue
        period_revenue = Decimal(str(agreement.total_value)) * Decimal(days_in_period) / Decimal(days_in_agreement)

        return period_revenue.quantize(Decimal("0.01"))

    @staticmethod
    def _distribute_usage_based(
        db: Session,
        distribution: RevenueDistribution,
        access_logs: List[ContentAccessLog],
    ):
        """
        Distribute revenue based on usage (number of accesses per member)
        """
        if not access_logs:
            logger.warning(
                "no_access_logs_for_distribution",
                distribution_id=str(distribution.id),
            )
            return

        # Count accesses per member
        member_access_count = {}
        member_content_count = {}

        for log in access_logs:
            if log.member_id not in member_access_count:
                member_access_count[log.member_id] = 0
                member_content_count[log.member_id] = set()

            member_access_count[log.member_id] += 1
            member_content_count[log.member_id].add(log.content_id)

        total_accesses = len(access_logs)

        # Create member revenue records
        for member_id, access_count in member_access_count.items():
            contribution_pct = Decimal(access_count) / Decimal(total_accesses) * Decimal(100)
            revenue_amount = distribution.member_pool * Decimal(access_count) / Decimal(total_accesses)

            member_rev = MemberRevenue(
                id=uuid.uuid4(),
                distribution_id=distribution.id,
                member_id=member_id,
                content_count=len(member_content_count[member_id]),
                access_count=access_count,
                contribution_percentage=contribution_pct.quantize(Decimal("0.01")),
                revenue_amount=revenue_amount.quantize(Decimal("0.01")),
                currency="USD",
                status="pending",
                created_at=datetime.utcnow(),
            )

            db.add(member_rev)

            logger.info(
                "member_revenue_calculated",
                member_id=str(member_id),
                access_count=access_count,
                revenue_amount=float(revenue_amount),
            )

        db.commit()

    @staticmethod
    def _distribute_equal_split(
        db: Session,
        distribution: RevenueDistribution,
        content_ids: List[uuid.UUID],
    ):
        """
        Distribute revenue equally among all members who contributed content
        """
        if not content_ids:
            logger.warning(
                "no_content_for_distribution",
                distribution_id=str(distribution.id),
            )
            return

        # Get unique members from content
        members = set()
        for content_id in content_ids:
            content = db.query(CoalitionContent).filter(CoalitionContent.id == content_id).first()
            if content:
                members.add(content.member_id)

        if not members:
            return

        # Equal split
        per_member_amount = distribution.member_pool / Decimal(len(members))
        contribution_pct = Decimal(100) / Decimal(len(members))

        for member_id in members:
            # Count this member's content
            member_content = [
                cid
                for cid in content_ids
                if db.query(CoalitionContent)
                .filter(
                    and_(
                        CoalitionContent.id == cid,
                        CoalitionContent.member_id == member_id,
                    )
                )
                .first()
            ]

            member_rev = MemberRevenue(
                id=uuid.uuid4(),
                distribution_id=distribution.id,
                member_id=member_id,
                content_count=len(member_content),
                access_count=0,  # Not tracked in equal split
                contribution_percentage=contribution_pct.quantize(Decimal("0.01")),
                revenue_amount=per_member_amount.quantize(Decimal("0.01")),
                currency="USD",
                status="pending",
                created_at=datetime.utcnow(),
            )

            db.add(member_rev)

        db.commit()

    @staticmethod
    def _distribute_weighted(
        db: Session,
        distribution: RevenueDistribution,
        access_logs: List[ContentAccessLog],
    ):
        """
        Distribute revenue weighted by content quality metrics

        Currently uses word count as weight, but could be extended to include:
        - Verification count
        - Content age
        - Engagement metrics
        """
        if not access_logs:
            return

        # Get member weights (word count)
        member_weights = {}
        member_access_count = {}
        member_content_count = {}

        for log in access_logs:
            content = db.query(CoalitionContent).filter(CoalitionContent.id == log.content_id).first()

            if not content:
                continue

            if log.member_id not in member_weights:
                member_weights[log.member_id] = 0
                member_access_count[log.member_id] = 0
                member_content_count[log.member_id] = set()

            # Weight by word count (or default to 1)
            weight = content.word_count or 1
            member_weights[log.member_id] += weight
            member_access_count[log.member_id] += 1
            member_content_count[log.member_id].add(log.content_id)

        total_weight = sum(member_weights.values())

        if total_weight == 0:
            return

        # Distribute based on weights
        for member_id, weight in member_weights.items():
            contribution_pct = Decimal(weight) / Decimal(total_weight) * Decimal(100)
            revenue_amount = distribution.member_pool * Decimal(weight) / Decimal(total_weight)

            member_rev = MemberRevenue(
                id=uuid.uuid4(),
                distribution_id=distribution.id,
                member_id=member_id,
                content_count=len(member_content_count[member_id]),
                access_count=member_access_count[member_id],
                contribution_percentage=contribution_pct.quantize(Decimal("0.01")),
                revenue_amount=revenue_amount.quantize(Decimal("0.01")),
                currency="USD",
                status="pending",
                created_at=datetime.utcnow(),
            )

            db.add(member_rev)

        db.commit()

    @staticmethod
    def mark_distribution_paid(
        db: Session,
        distribution_id: uuid.UUID,
        payment_method: str = "stripe",
    ) -> bool:
        """
        Mark a distribution as paid and update member revenue records
        """
        distribution = db.query(RevenueDistribution).filter(RevenueDistribution.id == distribution_id).first()

        if not distribution:
            return False

        if distribution.status == "paid":
            logger.warning(
                "distribution_already_paid",
                distribution_id=str(distribution_id),
            )
            return True

        # Get member revenues
        member_revenues = db.query(MemberRevenue).filter(MemberRevenue.distribution_id == distribution_id).all()

        # Mark each as paid
        for member_rev in member_revenues:
            if member_rev.status != "paid":
                member_rev.status = "paid"
                member_rev.payment_method = payment_method
                member_rev.paid_at = datetime.utcnow()
                # In production, set payment_reference from payment processor
                member_rev.payment_reference = f"DIST-{distribution_id}-{member_rev.id}"

        # Mark distribution as paid
        distribution.status = "paid"
        distribution.paid_at = datetime.utcnow()

        db.commit()

        logger.info(
            "distribution_marked_paid",
            distribution_id=str(distribution_id),
            member_count=len(member_revenues),
        )

        return True

    @staticmethod
    def get_pending_payouts(db: Session, min_amount: Optional[Decimal] = None) -> List[MemberRevenue]:
        """
        Get all pending payouts, optionally filtered by minimum amount
        """
        query = db.query(MemberRevenue).filter(MemberRevenue.status == "pending")

        if min_amount:
            query = query.filter(MemberRevenue.revenue_amount >= min_amount)

        return query.all()

    @staticmethod
    def get_member_total_earnings(db: Session, member_id: uuid.UUID) -> Dict[str, Decimal]:
        """
        Get total earnings for a member
        """
        result = (
            db.query(
                func.sum(func.case((MemberRevenue.status == "paid", MemberRevenue.revenue_amount), else_=0)).label("paid"),
                func.sum(func.case((MemberRevenue.status == "pending", MemberRevenue.revenue_amount), else_=0)).label("pending"),
            )
            .filter(MemberRevenue.member_id == member_id)
            .first()
        )

        return {
            "paid": Decimal(str(result.paid or 0)),
            "pending": Decimal(str(result.pending or 0)),
            "total": Decimal(str((result.paid or 0) + (result.pending or 0))),
        }
