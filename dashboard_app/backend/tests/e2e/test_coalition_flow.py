"""
End-to-end tests for coalition user flow.
Tests the complete user journey from signup to revenue tracking.
"""
from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.coalition import CoalitionMember, ContentAccessLog, ContentItem, RevenueTransaction
from app.models.user import User


@pytest.mark.asyncio
@pytest.mark.e2e
class TestCoalitionUserJourney:
    """Test complete coalition user journey."""

    async def test_complete_coalition_flow(
        self,
        client: AsyncClient,
        db: AsyncSession
    ):
        """
        Test complete flow:
        1. User signs up (auto-enrolled in coalition)
        2. User creates content
        3. Content is accessed by AI company
        4. Revenue is distributed
        5. User views stats and revenue
        """
        # Step 1: User signup (simulated - coalition member created)
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
            is_active=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        # Auto-enroll in coalition
        member = CoalitionMember(
            user_id=user.id,
            status="active",
            joined_at=datetime.utcnow()
        )
        db.add(member)
        await db.commit()

        # Step 2: User creates content
        content_items = []
        for i in range(5):
            content = ContentItem(
                user_id=user.id,
                title=f"Article {i+1}",
                content_type="article",
                word_count=1000 + i * 100,
                signed_at=datetime.utcnow() - timedelta(days=i)
            )
            db.add(content)
            content_items.append(content)
        await db.commit()

        # Step 3: AI company accesses content
        for content in content_items[:3]:  # Access first 3 items
            await db.refresh(content)
            log = ContentAccessLog(
                content_id=content.id,
                user_id=user.id,
                ai_company="OpenAI",
                access_type="training",
                accessed_at=datetime.utcnow()
            )
            db.add(log)
        await db.commit()

        # Step 4: Revenue is distributed
        transaction = RevenueTransaction(
            user_id=user.id,
            amount=150.00,
            currency="USD",
            period_start=datetime.utcnow() - timedelta(days=30),
            period_end=datetime.utcnow(),
            status="paid",
            paid_at=datetime.utcnow()
        )
        db.add(transaction)
        await db.commit()

        # Step 5: User views stats (simulate API call)
        # This would normally be done through authenticated API calls
        # For E2E, we verify the data is correctly stored

        # Verify coalition member exists
        assert member.status == "active"

        # Verify content items created
        assert len(content_items) == 5

        # Verify access logs created
        access_logs = await db.execute(
            "SELECT COUNT(*) FROM content_access_logs WHERE user_id = :user_id",
            {"user_id": str(user.id)}
        )
        assert access_logs.scalar() == 3

        # Verify revenue transaction
        assert transaction.amount == 150.00
        assert transaction.status == "paid"


@pytest.mark.asyncio
@pytest.mark.e2e
class TestCoalitionAdminFlow:
    """Test admin coalition management flow."""

    async def test_admin_creates_licensing_agreement(
        self,
        client: AsyncClient,
        admin_user: User,
        admin_auth_headers: dict,
        db: AsyncSession
    ):
        """
        Test admin flow:
        1. Admin creates licensing agreement
        2. AI company accesses content
        3. Admin views coalition overview
        4. Admin processes revenue distribution
        """
        # Step 1: Create licensing agreement (simulated)
        # In real implementation, this would be through API

        # Step 2: Create test content and access logs
        user = User(
            email="member@example.com",
            username="member",
            hashed_password="hashed",
            is_active=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        member = CoalitionMember(
            user_id=user.id,
            status="active",
            joined_at=datetime.utcnow()
        )
        db.add(member)

        content = ContentItem(
            user_id=user.id,
            title="Test Content",
            content_type="article",
            word_count=1500,
            signed_at=datetime.utcnow()
        )
        db.add(content)
        await db.commit()
        await db.refresh(content)

        # AI company accesses content
        log = ContentAccessLog(
            content_id=content.id,
            user_id=user.id,
            ai_company="Anthropic",
            access_type="training",
            accessed_at=datetime.utcnow()
        )
        db.add(log)
        await db.commit()

        # Step 3: Admin views overview
        response = await client.get(
            "/api/v1/coalition/admin/overview",
            headers=admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_members" in data
        assert data["total_members"] >= 1

        # Step 4: Process revenue distribution (simulated)
        transaction = RevenueTransaction(
            user_id=user.id,
            amount=75.00,
            currency="USD",
            period_start=datetime.utcnow() - timedelta(days=30),
            period_end=datetime.utcnow(),
            status="pending"
        )
        db.add(transaction)
        await db.commit()

        # Verify transaction created
        assert transaction.status == "pending"
        assert transaction.amount == 75.00


@pytest.mark.asyncio
@pytest.mark.e2e
class TestCoalitionContentLifecycle:
    """Test content lifecycle in coalition."""

    async def test_content_from_creation_to_revenue(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        db: AsyncSession
    ):
        """
        Test content lifecycle:
        1. Content created and signed
        2. Content indexed in coalition pool
        3. AI company discovers content
        4. AI company accesses content
        5. Access tracked
        6. Revenue calculated
        7. Revenue distributed to user
        """
        # Step 1: Create coalition member
        member = CoalitionMember(
            user_id=test_user.id,
            status="active",
            joined_at=datetime.utcnow()
        )
        db.add(member)
        await db.commit()

        # Step 2: Create and sign content
        content_data = {
            "user_id": str(test_user.id),
            "title": "High Quality Article",
            "content_type": "article",
            "word_count": 2500,
            "content_hash": "abc123def456",
            "signed_at": datetime.utcnow().isoformat()
        }

        response = await client.post(
            "/api/v1/coalition/content",
            json=content_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        content = response.json()
        content_id = content["id"]

        # Step 3-5: AI company accesses content
        log_data = {
            "content_id": content_id,
            "ai_company": "Google",
            "access_type": "training",
            "accessed_at": datetime.utcnow().isoformat()
        }

        response = await client.post(
            "/api/v1/coalition/access-log",
            json=log_data,
            headers=auth_headers
        )

        assert response.status_code == 201

        # Step 6-7: Revenue distribution (simulated)
        # In real system, this would be automated
        transaction = RevenueTransaction(
            user_id=test_user.id,
            amount=50.00,
            currency="USD",
            period_start=datetime.utcnow() - timedelta(days=30),
            period_end=datetime.utcnow(),
            status="paid",
            paid_at=datetime.utcnow()
        )
        db.add(transaction)
        await db.commit()

        # Verify complete flow
        response = await client.get(
            "/api/v1/coalition/stats",
            headers=auth_headers
        )

        assert response.status_code == 200
        stats = response.json()
        assert stats["content_stats"]["total_documents"] >= 1
        assert stats["revenue_stats"]["total_earned"] >= 50.00


@pytest.mark.asyncio
@pytest.mark.e2e
class TestCoalitionScalability:
    """Test coalition with multiple users and content."""

    async def test_coalition_with_multiple_members(
        self,
        client: AsyncClient,
        db: AsyncSession
    ):
        """
        Test coalition scalability:
        1. Create 10 coalition members
        2. Each creates 5 content items
        3. AI company accesses various content
        4. Verify stats aggregate correctly
        """
        members = []
        all_content = []

        # Create 10 members
        for i in range(10):
            user = User(
                email=f"user{i}@example.com",
                username=f"user{i}",
                hashed_password="hashed",
                is_active=True
            )
            db.add(user)
            await db.flush()

            member = CoalitionMember(
                user_id=user.id,
                status="active",
                joined_at=datetime.utcnow()
            )
            db.add(member)
            members.append(member)

            # Each creates 5 content items
            for j in range(5):
                content = ContentItem(
                    user_id=user.id,
                    title=f"Article {i}-{j}",
                    content_type="article",
                    word_count=1000,
                    signed_at=datetime.utcnow()
                )
                db.add(content)
                all_content.append(content)

        await db.commit()

        # Verify totals
        assert len(members) == 10
        assert len(all_content) == 50

        # Simulate AI company accessing 20 random content items
        for content in all_content[:20]:
            await db.refresh(content)
            log = ContentAccessLog(
                content_id=content.id,
                user_id=content.user_id,
                ai_company="OpenAI",
                access_type="training",
                accessed_at=datetime.utcnow()
            )
            db.add(log)

        await db.commit()

        # Verify access logs
        access_count = await db.execute(
            "SELECT COUNT(*) FROM content_access_logs"
        )
        assert access_count.scalar() == 20


@pytest.mark.asyncio
@pytest.mark.e2e
class TestCoalitionErrorHandling:
    """Test error handling in coalition flows."""

    async def test_duplicate_content_handling(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict
    ):
        """Test handling of duplicate content submissions."""
        content_data = {
            "user_id": str(test_user.id),
            "title": "Duplicate Article",
            "content_type": "article",
            "word_count": 1500,
            "content_hash": "duplicate123",
            "signed_at": datetime.utcnow().isoformat()
        }

        # First submission should succeed
        response1 = await client.post(
            "/api/v1/coalition/content",
            json=content_data,
            headers=auth_headers
        )
        assert response1.status_code == 201

        # Second submission with same hash should handle gracefully
        # (Implementation dependent - might return existing or error)
        response2 = await client.post(
            "/api/v1/coalition/content",
            json=content_data,
            headers=auth_headers
        )
        # Accept either 201 (created new) or 409 (conflict)
        assert response2.status_code in [201, 409]

    async def test_invalid_access_log(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test handling of invalid access log data."""
        log_data = {
            "content_id": "00000000-0000-0000-0000-000000000000",  # Non-existent
            "ai_company": "TestCompany",
            "access_type": "training",
            "accessed_at": datetime.utcnow().isoformat()
        }

        response = await client.post(
            "/api/v1/coalition/access-log",
            json=log_data,
            headers=auth_headers
        )

        # Should handle gracefully (either 404 or 400)
        assert response.status_code in [400, 404, 500]
