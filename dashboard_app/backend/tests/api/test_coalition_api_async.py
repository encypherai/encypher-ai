"""
Tests for coalition API endpoints.
"""

from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.coalition import CoalitionMember, ContentItem, RevenueTransaction
from app.models.user import User


@pytest.mark.asyncio
class TestCoalitionStatsEndpoint:
    """Tests for GET /api/v1/coalition/stats endpoint."""

    async def test_get_stats_success(self, client: AsyncClient, test_user: User, auth_headers: dict, db: AsyncSession):
        """Test successful retrieval of coalition stats."""
        # Create coalition member
        member = CoalitionMember(user_id=test_user.id, status="active", joined_at=datetime.utcnow() - timedelta(days=30))
        db.add(member)
        await db.commit()
        await db.refresh(member)

        # Create content items
        for i in range(5):
            content = ContentItem(
                user_id=test_user.id,
                title=f"Test Content {i}",
                content_type="article",
                word_count=1000 + i * 100,
                signed_at=datetime.utcnow() - timedelta(days=i),
            )
            db.add(content)
        await db.commit()

        response = await client.get("/api/v1/coalition/stats", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "content_stats" in data
        assert "revenue_stats" in data
        assert data["content_stats"]["total_documents"] == 5

    async def test_get_stats_unauthorized(self, client: AsyncClient):
        """Test stats endpoint without authentication."""
        response = await client.get("/api/v1/coalition/stats")
        assert response.status_code == 401

    async def test_get_stats_no_member_record(self, client: AsyncClient, test_user: User, auth_headers: dict, db: AsyncSession):
        """Test stats endpoint when user has no coalition member record."""
        response = await client.get("/api/v1/coalition/stats", headers=auth_headers)

        # Should still return stats (with zeros)
        assert response.status_code == 200
        data = response.json()
        assert data["content_stats"]["total_documents"] == 0


@pytest.mark.asyncio
class TestCoalitionRevenueEndpoint:
    """Tests for GET /api/v1/coalition/revenue endpoint."""

    async def test_get_revenue_success(self, client: AsyncClient, test_user: User, auth_headers: dict, db: AsyncSession):
        """Test successful retrieval of revenue data."""
        # Create revenue transactions
        for i in range(3):
            transaction = RevenueTransaction(
                user_id=test_user.id,
                amount=100.00 + i * 50,
                currency="USD",
                period_start=datetime.utcnow() - timedelta(days=30 * (i + 1)),
                period_end=datetime.utcnow() - timedelta(days=30 * i),
                status="paid" if i < 2 else "pending",
            )
            db.add(transaction)
        await db.commit()

        response = await client.get("/api/v1/coalition/revenue", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert len(data["data"]) == 3

    async def test_get_revenue_with_period_filter(self, client: AsyncClient, test_user: User, auth_headers: dict, db: AsyncSession):
        """Test revenue endpoint with period filter."""
        response = await client.get("/api/v1/coalition/revenue?period=month", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


@pytest.mark.asyncio
class TestContentPerformanceEndpoint:
    """Tests for GET /api/v1/coalition/content/performance endpoint."""

    async def test_get_top_content_success(self, client: AsyncClient, test_user: User, auth_headers: dict, db: AsyncSession):
        """Test successful retrieval of top performing content."""
        # Create content items with varying access counts
        for i in range(10):
            content = ContentItem(
                user_id=test_user.id,
                title=f"Content {i}",
                content_type="article",
                word_count=1000,
                signed_at=datetime.utcnow() - timedelta(days=i),
                access_count=10 - i,  # Descending access count
            )
            db.add(content)
        await db.commit()

        response = await client.get("/api/v1/coalition/content/performance?limit=5", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5
        # Should be sorted by access count descending
        assert data[0]["access_count"] >= data[1]["access_count"]

    async def test_get_top_content_invalid_limit(self, client: AsyncClient, auth_headers: dict):
        """Test content performance with invalid limit."""
        response = await client.get("/api/v1/coalition/content/performance?limit=0", headers=auth_headers)

        assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
class TestCreateContentEndpoint:
    """Tests for POST /api/v1/coalition/content endpoint."""

    async def test_create_content_success(self, client: AsyncClient, test_user: User, auth_headers: dict):
        """Test successful content creation."""
        content_data = {
            "user_id": str(test_user.id),
            "title": "Test Article",
            "content_type": "article",
            "word_count": 1500,
            "content_hash": "abc123def456",
            "signed_at": datetime.utcnow().isoformat(),
        }

        response = await client.post("/api/v1/coalition/content", json=content_data, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Article"
        assert data["word_count"] == 1500

    async def test_create_content_for_other_user_forbidden(self, client: AsyncClient, test_user: User, auth_headers: dict):
        """Test that non-admin cannot create content for other users."""
        content_data = {
            "user_id": "00000000-0000-0000-0000-000000000000",  # Different user
            "title": "Test Article",
            "content_type": "article",
            "word_count": 1500,
            "content_hash": "abc123",
            "signed_at": datetime.utcnow().isoformat(),
        }

        response = await client.post("/api/v1/coalition/content", json=content_data, headers=auth_headers)

        assert response.status_code == 403


@pytest.mark.asyncio
class TestAdminEndpoints:
    """Tests for admin-only coalition endpoints."""

    async def test_admin_overview_success(self, client: AsyncClient, admin_user: User, admin_auth_headers: dict, db: AsyncSession):
        """Test admin overview endpoint."""
        # Create some test data
        member = CoalitionMember(user_id=admin_user.id, status="active", joined_at=datetime.utcnow())
        db.add(member)
        await db.commit()

        response = await client.get("/api/v1/coalition/admin/overview", headers=admin_auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "total_members" in data
        assert "total_content" in data
        assert "total_revenue" in data

    async def test_admin_overview_non_admin_forbidden(self, client: AsyncClient, auth_headers: dict):
        """Test that non-admin cannot access admin overview."""
        response = await client.get("/api/v1/coalition/admin/overview", headers=auth_headers)

        assert response.status_code == 403

    async def test_get_members_list_success(self, client: AsyncClient, admin_auth_headers: dict, db: AsyncSession):
        """Test getting list of coalition members."""
        response = await client.get("/api/v1/coalition/admin/members?skip=0&limit=50", headers=admin_auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "members" in data
        assert "total" in data

    async def test_get_members_list_non_admin_forbidden(self, client: AsyncClient, auth_headers: dict):
        """Test that non-admin cannot access members list."""
        response = await client.get("/api/v1/coalition/admin/members", headers=auth_headers)

        assert response.status_code == 403


@pytest.mark.asyncio
class TestAccessLogEndpoint:
    """Tests for POST /api/v1/coalition/access-log endpoint."""

    async def test_create_access_log_success(self, client: AsyncClient, test_user: User, auth_headers: dict, db: AsyncSession):
        """Test successful creation of access log."""
        # Create content item first
        content = ContentItem(user_id=test_user.id, title="Test Content", content_type="article", word_count=1000, signed_at=datetime.utcnow())
        db.add(content)
        await db.commit()
        await db.refresh(content)

        log_data = {"content_id": str(content.id), "ai_company": "OpenAI", "access_type": "training", "accessed_at": datetime.utcnow().isoformat()}

        response = await client.post("/api/v1/coalition/access-log", json=log_data, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["ai_company"] == "OpenAI"
        assert data["access_type"] == "training"


@pytest.mark.asyncio
class TestMemberInfoEndpoint:
    """Tests for GET /api/v1/coalition/member endpoint."""

    async def test_get_member_info_success(self, client: AsyncClient, test_user: User, auth_headers: dict, db: AsyncSession):
        """Test successful retrieval of member info."""
        # Create coalition member
        member = CoalitionMember(user_id=test_user.id, status="active", joined_at=datetime.utcnow() - timedelta(days=30))
        db.add(member)
        await db.commit()

        response = await client.get("/api/v1/coalition/member", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"
        assert "joined_at" in data

    async def test_get_member_info_creates_if_not_exists(self, client: AsyncClient, test_user: User, auth_headers: dict):
        """Test that member info endpoint creates member if not exists."""
        response = await client.get("/api/v1/coalition/member", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"
