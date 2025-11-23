"""
Licensing Agreement Management Service.

Business logic for creating, managing, and tracking licensing agreements.
"""
from typing import List, Optional, Dict
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.licensing import (
    AICompany, LicensingAgreement, ContentAccessLog,
    RevenueDistribution, MemberRevenue,
    AgreementStatus, DistributionStatus, PayoutStatus
)
from app.schemas.licensing import (
    LicensingAgreementCreate, LicensingAgreementUpdate,
    RevenueDistributionCreate
)
from app.utils.api_key import generate_api_key, verify_api_key


class LicensingService:
    """Service for managing licensing agreements and revenue distribution."""

    @staticmethod
    async def create_agreement(
        db: AsyncSession,
        agreement_data: LicensingAgreementCreate
    ) -> tuple[LicensingAgreement, str]:
        """
        Create a new licensing agreement with AI company.

        Args:
            db: Database session
            agreement_data: Agreement creation data

        Returns:
            Tuple of (LicensingAgreement, api_key)
            The api_key is only returned once and should be shown to the user.
        """
        # Check if AI company already exists
        result = await db.execute(
            select(AICompany).where(
                AICompany.company_name == agreement_data.ai_company_name
            )
        )
        ai_company = result.scalar_one_or_none()

        # If not, create new AI company with API key
        api_key = None
        if not ai_company:
            api_key, api_key_hash, api_key_prefix = generate_api_key()
            ai_company = AICompany(
                company_name=agreement_data.ai_company_name,
                company_email=agreement_data.ai_company_email,
                api_key_hash=api_key_hash,
                api_key_prefix=api_key_prefix,
                status=AgreementStatus.ACTIVE
            )
            db.add(ai_company)
            await db.flush()  # Get the ID

        # Create licensing agreement
        agreement = LicensingAgreement(
            agreement_name=agreement_data.agreement_name,
            ai_company_id=ai_company.id,
            agreement_type=agreement_data.agreement_type,
            total_value=agreement_data.total_value,
            currency=agreement_data.currency,
            start_date=agreement_data.start_date,
            end_date=agreement_data.end_date,
            content_types=agreement_data.content_types,
            min_word_count=agreement_data.min_word_count,
            status=AgreementStatus.ACTIVE
        )
        db.add(agreement)
        await db.commit()
        await db.refresh(agreement)

        return agreement, api_key or ""

    @staticmethod
    async def get_agreement(
        db: AsyncSession,
        agreement_id: UUID
    ) -> Optional[LicensingAgreement]:
        """Get a licensing agreement by ID."""
        result = await db.execute(
            select(LicensingAgreement).where(LicensingAgreement.id == agreement_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_agreements(
        db: AsyncSession,
        status: Optional[AgreementStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[LicensingAgreement]:
        """List all licensing agreements with optional filtering."""
        query = select(LicensingAgreement)

        if status:
            query = query.where(LicensingAgreement.status == status)

        query = query.limit(limit).offset(offset).order_by(LicensingAgreement.created_at.desc())

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_agreement(
        db: AsyncSession,
        agreement_id: UUID,
        update_data: LicensingAgreementUpdate
    ) -> Optional[LicensingAgreement]:
        """Update a licensing agreement."""
        agreement = await LicensingService.get_agreement(db, agreement_id)
        if not agreement:
            return None

        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(agreement, field, value)

        agreement.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(agreement)

        return agreement

    @staticmethod
    async def terminate_agreement(
        db: AsyncSession,
        agreement_id: UUID
    ) -> Optional[LicensingAgreement]:
        """Terminate a licensing agreement."""
        agreement = await LicensingService.get_agreement(db, agreement_id)
        if not agreement:
            return None

        agreement.status = AgreementStatus.TERMINATED
        agreement.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(agreement)

        return agreement

    @staticmethod
    async def verify_ai_company_access(
        db: AsyncSession,
        api_key: str
    ) -> Optional[AICompany]:
        """
        Verify AI company API key and return company if valid.

        Args:
            db: Database session
            api_key: API key to verify

        Returns:
            AICompany if valid, None otherwise
        """
        # Get all active AI companies
        result = await db.execute(
            select(AICompany).where(AICompany.status == AgreementStatus.ACTIVE)
        )
        companies = result.scalars().all()

        # Check each company's API key hash
        for company in companies:
            if verify_api_key(api_key, company.api_key_hash):
                return company

        return None

    @staticmethod
    async def track_content_access(
        db: AsyncSession,
        agreement_id: UUID,
        content_id: UUID,
        member_id: UUID,
        ai_company_name: str,
        access_type: Optional[str] = "view"
    ) -> ContentAccessLog:
        """Track content access by AI company."""
        access_log = ContentAccessLog(
            agreement_id=agreement_id,
            content_id=content_id,
            member_id=member_id,
            ai_company_name=ai_company_name,
            access_type=access_type,
            accessed_at=datetime.utcnow()
        )
        db.add(access_log)
        await db.commit()
        await db.refresh(access_log)

        return access_log

    @staticmethod
    async def get_access_logs(
        db: AsyncSession,
        agreement_id: Optional[UUID] = None,
        period_start: Optional[date] = None,
        period_end: Optional[date] = None,
        limit: int = 1000,
        offset: int = 0
    ) -> List[ContentAccessLog]:
        """Get content access logs with optional filtering."""
        query = select(ContentAccessLog)

        filters = []
        if agreement_id:
            filters.append(ContentAccessLog.agreement_id == agreement_id)
        if period_start:
            filters.append(ContentAccessLog.accessed_at >= period_start)
        if period_end:
            filters.append(ContentAccessLog.accessed_at <= period_end)

        if filters:
            query = query.where(and_(*filters))

        query = query.limit(limit).offset(offset).order_by(ContentAccessLog.accessed_at.desc())

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def calculate_revenue_distribution(
        db: AsyncSession,
        distribution_data: RevenueDistributionCreate
    ) -> RevenueDistribution:
        """
        Calculate and create revenue distribution for a period.

        Implements the 70/30 split: 70% to members, 30% to Encypher.
        Distributes member pool based on content access count.
        """
        # Get the agreement
        agreement = await LicensingService.get_agreement(db, distribution_data.agreement_id)
        if not agreement:
            raise ValueError(f"Agreement {distribution_data.agreement_id} not found")

        # Calculate total revenue for the period
        total_revenue = agreement.get_monthly_value()

        # Calculate split (30% Encypher, 70% members)
        encypher_share = total_revenue * Decimal("0.30")
        member_pool = total_revenue * Decimal("0.70")

        # Create revenue distribution record
        distribution = RevenueDistribution(
            agreement_id=distribution_data.agreement_id,
            period_start=distribution_data.period_start,
            period_end=distribution_data.period_end,
            total_revenue=total_revenue,
            encypher_share=encypher_share,
            member_pool=member_pool,
            status=DistributionStatus.PENDING
        )
        db.add(distribution)
        await db.flush()

        # Get all content access logs for the period
        access_logs = await LicensingService.get_access_logs(
            db=db,
            agreement_id=distribution_data.agreement_id,
            period_start=distribution_data.period_start,
            period_end=distribution_data.period_end,
            limit=100000  # Get all logs
        )

        if not access_logs:
            # No access logs, nothing to distribute to members
            distribution.status = DistributionStatus.COMPLETED
            distribution.processed_at = datetime.utcnow()
            await db.commit()
            return distribution

        # Calculate member contributions
        member_contributions: Dict[UUID, Dict] = {}
        for log in access_logs:
            member_id = log.member_id
            if member_id not in member_contributions:
                member_contributions[member_id] = {
                    "access_count": 0,
                    "content_ids": set()
                }
            member_contributions[member_id]["access_count"] += 1
            member_contributions[member_id]["content_ids"].add(log.content_id)

        # Calculate total access count
        total_access_count = sum(
            contrib["access_count"] for contrib in member_contributions.values()
        )

        # Distribute member pool based on access count
        for member_id, contribution in member_contributions.items():
            contribution_percentage = Decimal(contribution["access_count"]) / Decimal(total_access_count)
            revenue_amount = member_pool * contribution_percentage

            member_revenue = MemberRevenue(
                distribution_id=distribution.id,
                member_id=member_id,
                content_count=len(contribution["content_ids"]),
                access_count=contribution["access_count"],
                revenue_amount=revenue_amount,
                status=PayoutStatus.PENDING
            )
            db.add(member_revenue)

        # Mark distribution as completed
        distribution.status = DistributionStatus.COMPLETED
        distribution.processed_at = datetime.utcnow()

        await db.commit()
        await db.refresh(distribution)

        return distribution

    @staticmethod
    async def get_distribution(
        db: AsyncSession,
        distribution_id: UUID
    ) -> Optional[RevenueDistribution]:
        """Get a revenue distribution by ID."""
        result = await db.execute(
            select(RevenueDistribution).where(RevenueDistribution.id == distribution_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_distributions(
        db: AsyncSession,
        agreement_id: Optional[UUID] = None,
        status: Optional[DistributionStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[RevenueDistribution]:
        """List revenue distributions with optional filtering."""
        query = select(RevenueDistribution)

        filters = []
        if agreement_id:
            filters.append(RevenueDistribution.agreement_id == agreement_id)
        if status:
            filters.append(RevenueDistribution.status == status)

        if filters:
            query = query.where(and_(*filters))

        query = query.limit(limit).offset(offset).order_by(RevenueDistribution.created_at.desc())

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_member_revenues(
        db: AsyncSession,
        distribution_id: UUID
    ) -> List[MemberRevenue]:
        """Get all member revenues for a distribution."""
        result = await db.execute(
            select(MemberRevenue).where(
                MemberRevenue.distribution_id == distribution_id
            ).order_by(MemberRevenue.revenue_amount.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def process_payouts(
        db: AsyncSession,
        distribution_id: UUID,
        payment_method: str = "stripe"
    ) -> Dict:
        """
        Process payouts for a distribution.

        This is a placeholder for actual payment processing integration.
        In production, this would integrate with Stripe or other payment processors.
        """
        distribution = await LicensingService.get_distribution(db, distribution_id)
        if not distribution:
            raise ValueError(f"Distribution {distribution_id} not found")

        if distribution.status != DistributionStatus.COMPLETED:
            raise ValueError("Distribution must be completed before processing payouts")

        member_revenues = await LicensingService.get_member_revenues(db, distribution_id)

        paid_count = 0
        total_paid = Decimal("0.00")
        failed_payments: List[UUID] = []

        for member_revenue in member_revenues:
            if member_revenue.status == PayoutStatus.PENDING:
                # TODO: Integrate with actual payment processor
                # For now, just mark as paid
                member_revenue.status = PayoutStatus.PAID
                member_revenue.paid_at = datetime.utcnow()
                member_revenue.payment_reference = f"{payment_method}_simulated_{member_revenue.id}"

                paid_count += 1
                total_paid += member_revenue.revenue_amount

        await db.commit()

        return {
            "distribution_id": distribution_id,
            "total_members_paid": paid_count,
            "total_amount_paid": total_paid,
            "failed_payments": failed_payments
        }
