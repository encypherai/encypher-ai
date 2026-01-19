"""
Unit tests for LicensingService.

Tests the licensing service business logic including:
- Agreement creation, update, termination
- AI company API key verification
- Content access tracking
- Revenue distribution calculations
- Payout processing
"""

from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.models.licensing import (
    AgreementStatus,
    AgreementType,
    AICompany,
    DistributionStatus,
    LicensingAgreement,
    MemberRevenue,
    PayoutStatus,
    RevenueDistribution,
)
from app.schemas.licensing import (
    LicensingAgreementCreate,
    LicensingAgreementUpdate,
    RevenueDistributionCreate,
)
from app.services.licensing_service import LicensingService


class TestAgreementCreation:
    """Test agreement creation flow."""

    @pytest.mark.asyncio
    async def test_create_agreement_new_company(self):
        """Test creating agreement with new AI company."""
        db = AsyncMock()
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None)))
        db.get = AsyncMock(return_value=MagicMock(api_key_prefix="lic_abc1"))
        db.flush = AsyncMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()

        agreement_data = LicensingAgreementCreate(
            agreement_name="Test Agreement",
            ai_company_name="Test AI Corp",
            ai_company_email="test@aicorp.com",
            agreement_type=AgreementType.SUBSCRIPTION,
            total_value=Decimal("120000.00"),
            currency="USD",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365),
            content_types=["article", "blog"],
            min_word_count=100,
        )

        agreement, api_key = await LicensingService.create_agreement(db, agreement_data)

        # Verify API key was generated
        assert api_key.startswith("lic_")
        assert len(api_key) == 68  # lic_ + 64 hex chars

        # Verify db operations
        assert db.add.call_count >= 2  # AI company + agreement
        db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_agreement_existing_company(self):
        """Test creating agreement with existing AI company."""
        db = AsyncMock()
        existing_company = MagicMock(spec=AICompany)
        existing_company.id = uuid4()
        existing_company.api_key_prefix = "lic_xyz1"
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=existing_company)))
        db.get = AsyncMock(return_value=existing_company)
        db.flush = AsyncMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()

        agreement_data = LicensingAgreementCreate(
            agreement_name="Second Agreement",
            ai_company_name="Existing AI Corp",
            ai_company_email="existing@aicorp.com",
            agreement_type=AgreementType.SUBSCRIPTION,
            total_value=Decimal("60000.00"),
            currency="USD",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=180),
        )

        agreement, api_key = await LicensingService.create_agreement(db, agreement_data)

        # No new API key for existing company
        assert api_key == ""

        # Only agreement added, not new company
        assert db.add.call_count == 1


class TestAgreementLifecycle:
    """Test agreement update and termination."""

    @pytest.mark.asyncio
    async def test_update_agreement(self):
        """Test updating agreement fields."""
        db = AsyncMock()
        existing_agreement = MagicMock(spec=LicensingAgreement)
        existing_agreement.id = uuid4()
        existing_agreement.agreement_name = "Old Name"
        existing_agreement.total_value = Decimal("100000.00")

        with patch.object(LicensingService, "get_agreement", return_value=existing_agreement):
            update_data = LicensingAgreementUpdate(
                agreement_name="New Name",
                total_value=Decimal("150000.00"),
            )

            result = await LicensingService.update_agreement(db, existing_agreement.id, update_data)

            assert result.agreement_name == "New Name"
            assert result.total_value == Decimal("150000.00")
            db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_terminate_agreement(self):
        """Test terminating an agreement."""
        db = AsyncMock()
        existing_agreement = MagicMock(spec=LicensingAgreement)
        existing_agreement.id = uuid4()
        existing_agreement.status = AgreementStatus.ACTIVE

        with patch.object(LicensingService, "get_agreement", return_value=existing_agreement):
            result = await LicensingService.terminate_agreement(db, existing_agreement.id)

            assert result.status == AgreementStatus.TERMINATED
            db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_terminate_nonexistent_agreement(self):
        """Test terminating non-existent agreement returns None."""
        db = AsyncMock()

        with patch.object(LicensingService, "get_agreement", return_value=None):
            result = await LicensingService.terminate_agreement(db, uuid4())

            assert result is None


class TestAPIKeyVerification:
    """Test AI company API key verification."""

    @pytest.mark.asyncio
    async def test_verify_valid_api_key(self):
        """Test verifying a valid API key."""
        db = AsyncMock()

        # Create a real API key and hash for testing
        from app.utils.api_key import generate_api_key

        api_key, api_key_hash, prefix = generate_api_key()

        company = MagicMock(spec=AICompany)
        company.id = uuid4()
        company.api_key_hash = api_key_hash
        company.status = AgreementStatus.ACTIVE

        db.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[company])))))

        result = await LicensingService.verify_ai_company_access(db, api_key)

        assert result is not None
        assert result.id == company.id

    @pytest.mark.asyncio
    async def test_verify_invalid_api_key(self):
        """Test verifying an invalid API key."""
        db = AsyncMock()

        company = MagicMock(spec=AICompany)
        company.api_key_hash = "invalid_hash"
        company.status = AgreementStatus.ACTIVE

        db.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[company])))))

        result = await LicensingService.verify_ai_company_access(db, "lic_invalid_key_here_1234567890abcdef1234567890abcdef1234567890abcdef12345678")

        assert result is None

    @pytest.mark.asyncio
    async def test_verify_api_key_no_companies(self):
        """Test verifying API key when no companies exist."""
        db = AsyncMock()
        db.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))))

        result = await LicensingService.verify_ai_company_access(db, "lic_any_key_1234567890abcdef1234567890abcdef1234567890abcdef1234567890")

        assert result is None


class TestContentAccessTracking:
    """Test content access tracking."""

    @pytest.mark.asyncio
    async def test_track_content_access(self):
        """Test tracking content access creates log entry."""
        db = AsyncMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()

        agreement_id = uuid4()
        content_id = uuid4()
        member_id = uuid4()

        await LicensingService.track_content_access(
            db=db,
            agreement_id=agreement_id,
            content_id=content_id,
            member_id=member_id,
            ai_company_name="Test AI Corp",
            access_type="train",
        )

        # Verify log was added
        db.add.assert_called_once()
        db.commit.assert_called_once()

        # Verify the added object
        added_log = db.add.call_args[0][0]
        assert added_log.agreement_id == agreement_id
        assert added_log.content_id == content_id
        assert added_log.member_id == member_id
        assert added_log.ai_company_name == "Test AI Corp"
        assert added_log.access_type == "train"


class TestRevenueDistribution:
    """Test revenue distribution calculations."""

    @pytest.mark.asyncio
    async def test_calculate_distribution_70_30_split(self):
        """Test 70/30 revenue split calculation."""
        db = AsyncMock()

        # Mock agreement with $120,000 annual value
        agreement = MagicMock(spec=LicensingAgreement)
        agreement.id = uuid4()
        agreement.total_value = Decimal("120000.00")
        agreement.start_date = date.today()
        agreement.end_date = date.today() + timedelta(days=365)
        agreement.agreement_type = AgreementType.SUBSCRIPTION
        agreement.get_monthly_value = MagicMock(return_value=Decimal("10000.00"))

        with patch.object(LicensingService, "get_agreement", return_value=agreement):
            with patch.object(LicensingService, "get_access_logs", return_value=[]):
                db.flush = AsyncMock()
                db.commit = AsyncMock()
                db.refresh = AsyncMock()

                distribution_data = RevenueDistributionCreate(
                    agreement_id=agreement.id,
                    period_start=date.today() - timedelta(days=30),
                    period_end=date.today(),
                )

                await LicensingService.calculate_revenue_distribution(db, distribution_data)

                # Verify the distribution was added
                added_dist = db.add.call_args[0][0]
                assert added_dist.total_revenue == Decimal("10000.00")
                assert added_dist.encypher_share == Decimal("3000.00")  # 30%
                assert added_dist.member_pool == Decimal("7000.00")  # 70%

    @pytest.mark.asyncio
    async def test_calculate_distribution_with_access_logs(self):
        """Test distribution with content access logs."""
        db = AsyncMock()

        agreement = MagicMock(spec=LicensingAgreement)
        agreement.id = uuid4()
        agreement.get_monthly_value = MagicMock(return_value=Decimal("10000.00"))

        member1_id = uuid4()
        member2_id = uuid4()
        content1_id = uuid4()
        content2_id = uuid4()

        # Member 1: 3 accesses, Member 2: 1 access
        access_logs = [
            MagicMock(member_id=member1_id, content_id=content1_id),
            MagicMock(member_id=member1_id, content_id=content1_id),
            MagicMock(member_id=member1_id, content_id=content2_id),
            MagicMock(member_id=member2_id, content_id=content1_id),
        ]

        with patch.object(LicensingService, "get_agreement", return_value=agreement):
            with patch.object(LicensingService, "get_access_logs", return_value=access_logs):
                db.flush = AsyncMock()
                db.commit = AsyncMock()
                db.refresh = AsyncMock()

                distribution_data = RevenueDistributionCreate(
                    agreement_id=agreement.id,
                    period_start=date.today() - timedelta(days=30),
                    period_end=date.today(),
                )

                await LicensingService.calculate_revenue_distribution(db, distribution_data)

                # Should have added distribution + 2 member revenues
                assert db.add.call_count == 3

    @pytest.mark.asyncio
    async def test_calculate_distribution_no_agreement(self):
        """Test distribution fails for non-existent agreement."""
        db = AsyncMock()

        with patch.object(LicensingService, "get_agreement", return_value=None):
            distribution_data = RevenueDistributionCreate(
                agreement_id=uuid4(),
                period_start=date.today() - timedelta(days=30),
                period_end=date.today(),
            )

            with pytest.raises(ValueError, match="not found"):
                await LicensingService.calculate_revenue_distribution(db, distribution_data)


class TestPayoutProcessing:
    """Test payout processing."""

    @pytest.mark.asyncio
    async def test_process_payouts_success(self):
        """Test successful payout processing."""
        db = AsyncMock()

        distribution = MagicMock(spec=RevenueDistribution)
        distribution.id = uuid4()
        distribution.status = DistributionStatus.COMPLETED

        member_revenue1 = MagicMock(spec=MemberRevenue)
        member_revenue1.id = uuid4()
        member_revenue1.status = PayoutStatus.PENDING
        member_revenue1.revenue_amount = Decimal("5000.00")

        member_revenue2 = MagicMock(spec=MemberRevenue)
        member_revenue2.id = uuid4()
        member_revenue2.status = PayoutStatus.PENDING
        member_revenue2.revenue_amount = Decimal("2000.00")

        with patch.object(LicensingService, "get_distribution", return_value=distribution):
            with patch.object(LicensingService, "get_member_revenues", return_value=[member_revenue1, member_revenue2]):
                db.commit = AsyncMock()

                result = await LicensingService.process_payouts(db, distribution.id)

                assert result["total_members_paid"] == 2
                assert result["total_amount_paid"] == Decimal("7000.00")
                assert result["failed_payments"] == []

                # Verify status updates
                assert member_revenue1.status == PayoutStatus.PAID
                assert member_revenue2.status == PayoutStatus.PAID

    @pytest.mark.asyncio
    async def test_process_payouts_distribution_not_completed(self):
        """Test payout fails if distribution not completed."""
        db = AsyncMock()

        distribution = MagicMock(spec=RevenueDistribution)
        distribution.id = uuid4()
        distribution.status = DistributionStatus.PENDING

        with patch.object(LicensingService, "get_distribution", return_value=distribution):
            with pytest.raises(ValueError, match="must be completed"):
                await LicensingService.process_payouts(db, distribution.id)

    @pytest.mark.asyncio
    async def test_process_payouts_distribution_not_found(self):
        """Test payout fails if distribution not found."""
        db = AsyncMock()

        with patch.object(LicensingService, "get_distribution", return_value=None):
            with pytest.raises(ValueError, match="not found"):
                await LicensingService.process_payouts(db, uuid4())


class TestAgreementHelpers:
    """Test agreement helper methods."""

    def test_agreement_is_active(self):
        """Test is_active() method."""
        agreement = LicensingAgreement()
        agreement.status = AgreementStatus.ACTIVE
        agreement.start_date = date.today() - timedelta(days=10)
        agreement.end_date = date.today() + timedelta(days=10)

        assert agreement.is_active() is True

    def test_agreement_is_active_expired(self):
        """Test is_active() returns False for expired agreement."""
        agreement = LicensingAgreement()
        agreement.status = AgreementStatus.ACTIVE
        agreement.start_date = date.today() - timedelta(days=100)
        agreement.end_date = date.today() - timedelta(days=10)

        assert agreement.is_active() is False

    def test_agreement_is_active_not_started(self):
        """Test is_active() returns False for future agreement."""
        agreement = LicensingAgreement()
        agreement.status = AgreementStatus.ACTIVE
        agreement.start_date = date.today() + timedelta(days=10)
        agreement.end_date = date.today() + timedelta(days=100)

        assert agreement.is_active() is False

    def test_agreement_is_active_terminated(self):
        """Test is_active() returns False for terminated agreement."""
        agreement = LicensingAgreement()
        agreement.status = AgreementStatus.TERMINATED
        agreement.start_date = date.today() - timedelta(days=10)
        agreement.end_date = date.today() + timedelta(days=10)

        assert agreement.is_active() is False

    def test_get_monthly_value_subscription(self):
        """Test monthly value calculation for subscription."""
        agreement = LicensingAgreement()
        agreement.agreement_type = AgreementType.SUBSCRIPTION
        agreement.total_value = Decimal("120000.00")
        agreement.start_date = date(2025, 1, 1)
        agreement.end_date = date(2026, 1, 1)  # Exactly 12 months

        monthly = agreement.get_monthly_value()
        assert monthly == Decimal("10000.00")

    def test_get_monthly_value_one_time(self):
        """Test monthly value for one-time agreement."""
        agreement = LicensingAgreement()
        agreement.agreement_type = AgreementType.ONE_TIME
        agreement.total_value = Decimal("50000.00")
        agreement.start_date = date(2025, 1, 1)
        agreement.end_date = date(2025, 6, 30)

        monthly = agreement.get_monthly_value()
        assert monthly == Decimal("50000.00")  # Full value for one-time
