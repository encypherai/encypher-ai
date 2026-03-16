"""Tests for EU AI Act Compliance readiness endpoint."""

import pytest
from httpx import AsyncClient


class TestComplianceReadiness:
    """Test suite for /api/v1/compliance/readiness endpoint."""

    @pytest.mark.asyncio
    async def test_readiness_returns_valid_structure(self, async_client: AsyncClient, business_auth_headers: dict):
        """Test that the readiness endpoint returns the expected JSON shape."""
        response = await async_client.get(
            "/api/v1/compliance/readiness",
            headers=business_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Top-level keys
        assert "readiness_score" in data
        assert "compliant_count" in data
        assert "total_count" in data
        assert "items" in data
        assert "eu_ai_act_deadline" in data
        assert data["eu_ai_act_deadline"] == "2026-08-02"

        # Score is a number between 0 and 100
        assert isinstance(data["readiness_score"], (int, float))
        assert 0 <= data["readiness_score"] <= 100

        # Items is a non-empty list
        assert isinstance(data["items"], list)
        assert len(data["items"]) > 0

    @pytest.mark.asyncio
    async def test_readiness_item_structure(self, async_client: AsyncClient, business_auth_headers: dict):
        """Test that each checklist item has the required fields."""
        response = await async_client.get(
            "/api/v1/compliance/readiness",
            headers=business_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        required_keys = {
            "id",
            "label",
            "description",
            "status",
            "eu_ai_act_article",
            "action_href",
            "category",
        }

        for item in data["items"]:
            assert required_keys.issubset(item.keys()), f"Item {item.get('id', '?')} missing keys: {required_keys - item.keys()}"
            assert item["status"] in ("compliant", "action_needed", "unknown")

    @pytest.mark.asyncio
    async def test_readiness_score_matches_counts(self, async_client: AsyncClient, business_auth_headers: dict):
        """Test that the readiness score is consistent with compliant/total counts."""
        response = await async_client.get(
            "/api/v1/compliance/readiness",
            headers=business_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        compliant = data["compliant_count"]
        total = data["total_count"]

        assert total == len(data["items"])
        assert compliant <= total

        # Score should equal compliant / total * 100 (rounded to 1 decimal)
        expected_score = round(compliant / total * 100, 1) if total > 0 else 0
        assert data["readiness_score"] == expected_score

    @pytest.mark.asyncio
    async def test_readiness_requires_auth(self, async_client: AsyncClient):
        """Test that the compliance endpoint requires authentication."""
        response = await async_client.get("/api/v1/compliance/readiness")
        assert response.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_readiness_enterprise_has_more_compliant(self, async_client: AsyncClient, enterprise_auth_headers: dict):
        """Enterprise orgs should have formal_notice and team_management compliant."""
        response = await async_client.get(
            "/api/v1/compliance/readiness",
            headers=enterprise_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        items_by_id = {item["id"]: item for item in data["items"]}

        # Enterprise tier should have formal notice capability
        assert items_by_id["formal_notice"]["status"] == "compliant"
        # Enterprise tier should have team management
        assert items_by_id["team_management"]["status"] == "compliant"

    @pytest.mark.asyncio
    async def test_readiness_has_expected_categories(self, async_client: AsyncClient, business_auth_headers: dict):
        """Test that all expected categories are present."""
        response = await async_client.get(
            "/api/v1/compliance/readiness",
            headers=business_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        categories = {item["category"] for item in data["items"]}
        assert "Content Provenance" in categories
        assert "Rights Management" in categories
        assert "Governance" in categories
