"""
Licensing Agreement Management Service.

Business logic for creating, managing, and tracking licensing agreements.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, cast
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content_reference import ContentReference
from app.models.licensing import (
    AgreementStatus,
    AICompany,
    ContentAccessLog,
    DistributionStatus,
    LicensingAgreement,
    MemberRevenue,
    PayoutStatus,
    RevenueDistribution,
)
from app.schemas.licensing import (
    ContentMetadata,
    LicensingAgreementCreate,
    LicensingAgreementUpdate,
    RevenueDistributionCreate,
)
from app.utils.api_key import generate_api_key, verify_api_key


class LicensingService:
    """Service for managing licensing agreements and revenue distribution."""

    @staticmethod
    async def create_agreement(db: AsyncSession, agreement_data: LicensingAgreementCreate) -> tuple[LicensingAgreement, str]:
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
        result = await db.execute(select(AICompany).where(AICompany.company_name == agreement_data.ai_company_name))
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
                status=AgreementStatus.ACTIVE,
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
            status=AgreementStatus.ACTIVE,
        )
        db.add(agreement)
        await db.commit()
        await db.refresh(agreement)

        return agreement, api_key or ""

    @staticmethod
    async def get_agreement(db: AsyncSession, agreement_id: UUID) -> Optional[LicensingAgreement]:
        """Get a licensing agreement by ID."""
        result = await db.execute(select(LicensingAgreement).where(LicensingAgreement.id == agreement_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_agreements(
        db: AsyncSession, status: Optional[AgreementStatus] = None, ai_company_id: Optional[UUID] = None, limit: int = 100, offset: int = 0
    ) -> List[LicensingAgreement]:
        """List all licensing agreements with optional filtering."""
        query = select(LicensingAgreement)

        if status:
            query = query.where(LicensingAgreement.status == status)

        if ai_company_id:
            query = query.where(LicensingAgreement.ai_company_id == ai_company_id)

        query = query.limit(limit).offset(offset).order_by(LicensingAgreement.created_at.desc())

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_active_agreement_for_company(db: AsyncSession, ai_company_id: UUID) -> Optional[LicensingAgreement]:
        """Get the active agreement for an AI company."""
        agreements = await LicensingService.list_agreements(db=db, status=AgreementStatus.ACTIVE, ai_company_id=ai_company_id, limit=1)
        # Return first active agreement that is within date range
        for agreement in agreements:
            if agreement.is_active():
                return agreement
        return None

    @staticmethod
    async def list_available_content(
        db: AsyncSession,
        agreement: LicensingAgreement,
        content_type: Optional[str] = None,
        min_word_count: Optional[int] = None,
        include_rights_signals: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[List[ContentMetadata], int]:
        """
        List content available under a licensing agreement.

        Queries ContentReference table for content from coalition members
        that matches the agreement terms.

        Args:
            db: Database session
            agreement: The licensing agreement
            content_type: Optional filter by content type
            min_word_count: Optional minimum word count filter
            limit: Results per page
            offset: Pagination offset

        Returns:
            Tuple of (list of ContentMetadata, total count)
        """
        from sqlalchemy import func

        # Build base query for content references
        created_at_date = func.date(ContentReference.created_at)
        query = select(ContentReference).where(
            created_at_date >= agreement.start_date,
            created_at_date <= agreement.end_date,
        )

        if include_rights_signals:
            query = query.where(ContentReference.manifest_data.is_not(None))

        # Apply agreement content type filters if specified
        # Note: ContentReference doesn't have content_type directly,
        # but we can filter by license_type or other metadata
        if agreement.content_types:
            # Filter by license_type if it matches content_types
            query = query.where(ContentReference.license_type.in_(agreement.content_types))

        # Apply request-level content_type filter
        if content_type:
            query = query.where(ContentReference.license_type == content_type)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        # Apply pagination
        query = query.limit(limit).offset(offset).order_by(ContentReference.created_at.desc())

        result = await db.execute(query)
        references = list(result.scalars().all())

        extractor = None
        if include_rights_signals:
            from app.services.verification_logic import _extract_rights_signals

            extractor = _extract_rights_signals

        content_list: List[ContentMetadata] = []
        for ref in references:
            rights_signals = None
            if extractor and ref.manifest_data is not None:
                candidate_manifest = ref.manifest_data
                if isinstance(candidate_manifest, str):
                    import json

                    try:
                        candidate_manifest = json.loads(candidate_manifest)
                    except json.JSONDecodeError:
                        candidate_manifest = None

                if isinstance(candidate_manifest, dict):
                    rights_signals = extractor(candidate_manifest)

            content_list.append(
                ContentMetadata(
                    id=ref.id,
                    content_type=ref.license_type or "unknown",
                    word_count=None,
                    signed_at=ref.created_at,
                    content_hash=ref.signature_hash,
                    verification_url=ref.to_verification_url(),
                    rights_signals=rights_signals,
                )
            )

        return content_list, total

    @staticmethod
    async def get_content_owner(db: AsyncSession, content_id: int) -> Optional[str]:
        """
        Get the organization_id (member_id) that owns a piece of content.

        Args:
            db: Database session
            content_id: The content reference ID (BigInteger)

        Returns:
            Organization ID if found, None otherwise
        """
        result = await db.execute(select(ContentReference.organization_id).where(ContentReference.id == content_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_agreement(db: AsyncSession, agreement_id: UUID, update_data: LicensingAgreementUpdate) -> Optional[LicensingAgreement]:
        """Update a licensing agreement."""
        agreement = await LicensingService.get_agreement(db, agreement_id)
        if not agreement:
            return None

        agreement_any = cast(Any, agreement)

        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(agreement_any, field, value)

        agreement_any.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(agreement)

        return agreement

    @staticmethod
    async def terminate_agreement(db: AsyncSession, agreement_id: UUID) -> Optional[LicensingAgreement]:
        """Terminate a licensing agreement."""
        agreement = await LicensingService.get_agreement(db, agreement_id)
        if not agreement:
            return None

        agreement_any = cast(Any, agreement)
        agreement_any.status = AgreementStatus.TERMINATED
        agreement_any.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(agreement)

        return agreement

    @staticmethod
    async def verify_ai_company_access(db: AsyncSession, api_key: str) -> Optional[AICompany]:
        """
        Verify AI company API key and return company if valid.

        Args:
            db: Database session
            api_key: API key to verify

        Returns:
            AICompany if valid, None otherwise
        """
        # Get all active AI companies
        result = await db.execute(select(AICompany).where(AICompany.status == AgreementStatus.ACTIVE.value))
        companies = result.scalars().all()

        # Check each company's API key hash
        for company in companies:
            if verify_api_key(api_key, cast(str, company.api_key_hash)):
                return company

        return None

    @staticmethod
    async def track_content_access(
        db: AsyncSession, agreement_id: UUID, content_id: int, member_id: str, ai_company_name: str, access_type: Optional[str] = "view"
    ) -> ContentAccessLog:
        """Track content access by AI company."""
        access_log = ContentAccessLog(
            agreement_id=agreement_id,
            content_id=content_id,
            member_id=member_id,
            ai_company_name=ai_company_name,
            access_type=access_type,
            accessed_at=datetime.utcnow(),
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
        offset: int = 0,
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
    async def calculate_revenue_distribution(db: AsyncSession, distribution_data: RevenueDistributionCreate) -> RevenueDistribution:
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
            status=DistributionStatus.PENDING,
        )
        db.add(distribution)
        await db.flush()
        distribution_any = cast(Any, distribution)

        # Get all content access logs for the period
        access_logs = await LicensingService.get_access_logs(
            db=db,
            agreement_id=distribution_data.agreement_id,
            period_start=distribution_data.period_start,
            period_end=distribution_data.period_end,
            limit=100000,  # Get all logs
        )

        if not access_logs:
            # No access logs, nothing to distribute to members
            distribution_any.status = DistributionStatus.COMPLETED
            distribution_any.processed_at = datetime.utcnow()
            await db.commit()
            return distribution

        # Calculate member contributions
        member_contributions: Dict[str, Dict[str, Any]] = {}
        for log in access_logs:
            member_id = cast(str, log.member_id)
            if member_id not in member_contributions:
                member_contributions[member_id] = {"access_count": 0, "content_ids": set()}
            member_contributions[member_id]["access_count"] += 1
            member_contributions[member_id]["content_ids"].add(int(log.content_id))

        # Calculate total access count
        total_access_count = sum(contrib["access_count"] for contrib in member_contributions.values())

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
                status=PayoutStatus.PENDING,
            )
            db.add(member_revenue)

        # Mark distribution as completed
        distribution_any.status = DistributionStatus.COMPLETED
        distribution_any.processed_at = datetime.utcnow()

        await db.commit()
        await db.refresh(distribution)

        return distribution

    @staticmethod
    async def get_distribution(db: AsyncSession, distribution_id: UUID) -> Optional[RevenueDistribution]:
        """Get a revenue distribution by ID."""
        result = await db.execute(select(RevenueDistribution).where(RevenueDistribution.id == distribution_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_distributions(
        db: AsyncSession, agreement_id: Optional[UUID] = None, status: Optional[DistributionStatus] = None, limit: int = 100, offset: int = 0
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
    async def get_member_revenues(db: AsyncSession, distribution_id: UUID) -> List[MemberRevenue]:
        """Get all member revenues for a distribution."""
        result = await db.execute(
            select(MemberRevenue).where(MemberRevenue.distribution_id == distribution_id).order_by(MemberRevenue.revenue_amount.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def count_accesses_since(db: AsyncSession, agreement_id: UUID, since: datetime) -> int:
        """Count content access log entries for an agreement since a given timestamp."""
        from sqlalchemy import func

        result = await db.execute(
            select(func.count()).where(
                ContentAccessLog.agreement_id == agreement_id,
                ContentAccessLog.accessed_at >= since,
            )
        )
        return result.scalar() or 0

    @staticmethod
    async def process_payouts(db: AsyncSession, distribution_id: UUID, payment_method: str = "stripe") -> Dict:
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
                member_revenue_any = cast(Any, member_revenue)
                # TODO: Integrate with actual payment processor
                # For now, just mark as paid
                member_revenue_any.status = PayoutStatus.PAID
                member_revenue_any.paid_at = datetime.utcnow()
                member_revenue_any.payment_reference = f"{payment_method}_simulated_{member_revenue.id}"

                paid_count += 1
                total_paid += cast(Decimal, member_revenue.revenue_amount)

        await db.commit()

        return {
            "distribution_id": distribution_id,
            "total_members_paid": paid_count,
            "total_amount_paid": total_paid,
            "failed_payments": failed_payments,
        }
