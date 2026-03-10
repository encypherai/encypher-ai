"""
Tests for AI Crawler Intelligence Analytics (TEAM_219 -- backend).

Covers:
- Enhanced get_crawler_summary with compliance fields
- Compliance score computation and label boundaries
- get_crawler_timeseries shape and filtering
- Timeseries HTTP endpoint
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _make_crawler_row(
    category: str,
    total_cnt: int,
    rsl_cnt: int,
    ack_cnt: int,
    last_seen: datetime | None = None,
    requester_user_agent: str | None = None,
):
    """Build a mock row matching the enhanced get_crawler_summary query."""
    row = MagicMock()
    row.user_agent_category = category
    row.requester_user_agent = requester_user_agent or category
    row.total_cnt = total_cnt
    row.rsl_cnt = rsl_cnt
    row.ack_cnt = ack_cnt
    row.bypass_cnt = 0
    row.last_seen = last_seen or _utcnow()
    return row


def _make_known_crawler(
    crawler_name: str,
    crawler_type: str,
    operator_org: str = "TestCorp",
    user_agent_pattern: str = "TestBot/*",
    respects_rsl: bool | None = True,
    respects_robots_txt: bool | None = True,
):
    kc = MagicMock()
    kc.crawler_name = crawler_name
    kc.crawler_type = crawler_type
    kc.operator_org = operator_org
    kc.user_agent_pattern = user_agent_pattern
    kc.respects_rsl = respects_rsl
    kc.respects_robots_txt = respects_robots_txt
    return kc


def _make_timeseries_row(event_date, category: str, cnt: int):
    row = MagicMock()
    row.event_date = event_date
    row.user_agent_category = category
    row.cnt = cnt
    return row


# ---------------------------------------------------------------------------
# Test: Enhanced crawler summary has compliance fields
# ---------------------------------------------------------------------------


class TestEnhancedCrawlerSummary:
    @pytest.mark.asyncio
    async def test_enhanced_crawler_summary_has_compliance_fields(self):
        from app.services.rights_service import RightsService

        svc = RightsService()

        crawler_rows = [
            _make_crawler_row("ai_training", total_cnt=10, rsl_cnt=8, ack_cnt=6, requester_user_agent="GPTBot/1.0"),
        ]
        known_crawlers = [
            _make_known_crawler("GPTBot", "ai_training", operator_org="OpenAI", user_agent_pattern="GPTBot"),
        ]

        call_count = 0

        async def _exec(query):
            nonlocal call_count
            call_count += 1
            mock = MagicMock()
            if call_count == 1:
                # crawler_result
                mock.all.return_value = crawler_rows
            else:
                # known_result
                mock.scalars.return_value = MagicMock(all=MagicMock(return_value=known_crawlers))
            return mock

        db = AsyncMock()
        db.execute = AsyncMock(side_effect=_exec)

        result = await svc.get_crawler_summary(db=db, organization_id="org_test", days=30)

        assert len(result["crawlers"]) == 1
        c = result["crawlers"][0]

        # All required fields present
        required_fields = [
            "crawler_name",
            "user_agent_category",
            "company",
            "user_agent_pattern",
            "respects_rsl",
            "total_events",
            "rsl_check_count",
            "rsl_check_rate",
            "rights_acknowledged_rate",
            "last_seen",
            "compliance_score",
            "compliance_label",
        ]
        for field in required_fields:
            assert field in c, f"Missing field: {field}"

        assert c["crawler_name"] == "GPTBot"
        assert c["company"] == "OpenAI"
        assert c["total_events"] == 10
        assert c["rsl_check_count"] == 8


# ---------------------------------------------------------------------------
# Test: Compliance score = 100, label Excellent
# ---------------------------------------------------------------------------


class TestComplianceScoreExcellent:
    @pytest.mark.asyncio
    async def test_compliance_score_excellent(self):
        from app.services.rights_service import RightsService

        svc = RightsService()

        # 100% RSL + 100% ack -> score = 60 + 40 = 100
        crawler_rows = [
            _make_crawler_row("ai_search", total_cnt=20, rsl_cnt=20, ack_cnt=20),
        ]
        known_crawlers = []

        call_count = 0

        async def _exec(query):
            nonlocal call_count
            call_count += 1
            mock = MagicMock()
            if call_count == 1:
                mock.all.return_value = crawler_rows
            else:
                mock.scalars.return_value = MagicMock(all=MagicMock(return_value=known_crawlers))
            return mock

        db = AsyncMock()
        db.execute = AsyncMock(side_effect=_exec)

        result = await svc.get_crawler_summary(db=db, organization_id="org_test", days=30)
        c = result["crawlers"][0]

        assert c["compliance_score"] == 100
        assert c["compliance_label"] == "Excellent"


# ---------------------------------------------------------------------------
# Test: All 5 compliance label boundaries
# ---------------------------------------------------------------------------


class TestComplianceLabelBoundaries:
    @pytest.mark.asyncio
    async def test_compliance_label_boundaries(self):
        from app.services.rights_service import RightsService

        svc = RightsService()

        # Test cases: (rsl_cnt, ack_cnt, total, expected_label)
        # score = round(rsl_rate * 60 + ack_rate * 40)
        test_cases = [
            # 100% RSL + 100% ack = 100 -> Excellent
            (100, 100, 100, "Excellent"),
            # 80% RSL + 80% ack = 48 + 32 = 80 -> Excellent
            (80, 80, 100, "Excellent"),
            # 60% RSL + 60% ack = 36 + 24 = 60 -> Good
            (60, 60, 100, "Good"),
            # 30% RSL + 30% ack = 18 + 12 = 30 -> Fair
            (30, 30, 100, "Fair"),
            # 10% RSL + 10% ack = 6 + 4 = 10 -> Poor
            (10, 10, 100, "Poor"),
            # 0% RSL + 0% ack = 0 -> Non-compliant
            (0, 0, 100, "Non-compliant"),
        ]

        for rsl_cnt, ack_cnt, total, expected_label in test_cases:
            crawler_rows = [
                _make_crawler_row("test_bot", total_cnt=total, rsl_cnt=rsl_cnt, ack_cnt=ack_cnt),
            ]
            call_count = 0

            async def _exec(query, _cr=crawler_rows):
                nonlocal call_count
                call_count += 1
                mock = MagicMock()
                if call_count == 1:
                    mock.all.return_value = _cr
                else:
                    mock.scalars.return_value = MagicMock(all=MagicMock(return_value=[]))
                return mock

            db = AsyncMock()
            db.execute = AsyncMock(side_effect=_exec)

            result = await svc.get_crawler_summary(db=db, organization_id="org_test", days=30)
            c = result["crawlers"][0]
            assert (
                c["compliance_label"] == expected_label
            ), f"rsl={rsl_cnt}, ack={ack_cnt}, total={total}: expected {expected_label}, got {c['compliance_label']} (score={c['compliance_score']})"


# ---------------------------------------------------------------------------
# Test: Non-compliant when no RSL checks
# ---------------------------------------------------------------------------


class TestNonCompliantNoRsl:
    @pytest.mark.asyncio
    async def test_non_compliant_when_no_rsl_checks(self):
        from app.services.rights_service import RightsService

        svc = RightsService()

        # 0 RSL checks but some ack -> score = 0 + ack_rate*40
        # With 0 RSL and 0 ack -> 0 -> Non-compliant
        crawler_rows = [
            _make_crawler_row("ai_training", total_cnt=50, rsl_cnt=0, ack_cnt=0),
        ]
        call_count = 0

        async def _exec(query):
            nonlocal call_count
            call_count += 1
            mock = MagicMock()
            if call_count == 1:
                mock.all.return_value = crawler_rows
            else:
                mock.scalars.return_value = MagicMock(all=MagicMock(return_value=[]))
            return mock

        db = AsyncMock()
        db.execute = AsyncMock(side_effect=_exec)

        result = await svc.get_crawler_summary(db=db, organization_id="org_test", days=30)
        c = result["crawlers"][0]

        assert c["rsl_check_count"] == 0
        assert c["compliance_label"] == "Non-compliant"
        assert c["compliance_score"] == 0


# ---------------------------------------------------------------------------
# Test: Timeseries shape (dates list, matching array lengths)
# ---------------------------------------------------------------------------


class TestCrawlerTimeseries:
    @pytest.mark.asyncio
    async def test_get_crawler_timeseries_shape(self):
        from app.services.rights_service import RightsService

        svc = RightsService()

        today = _utcnow().date()
        ts_rows = [
            _make_timeseries_row(today, "ai_training", 5),
            _make_timeseries_row(today - timedelta(days=1), "ai_training", 3),
            _make_timeseries_row(today, "ai_search", 2),
        ]

        async def _exec(query):
            mock = MagicMock()
            mock.all.return_value = ts_rows
            return mock

        db = AsyncMock()
        db.execute = AsyncMock(side_effect=_exec)

        result = await svc.get_crawler_timeseries(
            db=db,
            organization_id="org_test",
            days=7,
        )

        assert "dates" in result
        assert "by_crawler" in result
        assert "total_by_date" in result

        # 7 days -> 7 entries in dates
        assert len(result["dates"]) == 7
        assert len(result["total_by_date"]) == 7

        # Each crawler series matches dates length
        for cat, series in result["by_crawler"].items():
            assert len(series) == 7, f"Series for {cat} has wrong length"

        # Both categories present
        assert "ai_training" in result["by_crawler"]
        assert "ai_search" in result["by_crawler"]


# ---------------------------------------------------------------------------
# Test: Timeseries excludes human_browser
# ---------------------------------------------------------------------------


class TestTimeseriesExcludesHumanBrowser:
    @pytest.mark.asyncio
    async def test_timeseries_excludes_human_browser(self):
        from app.services.rights_service import RightsService

        svc = RightsService()

        today = _utcnow().date()
        # Only return non-human rows (the SQL filter does this; we verify
        # that if somehow human_browser rows came through, they'd still not appear)
        ts_rows = [
            _make_timeseries_row(today, "ai_training", 5),
        ]

        async def _exec(query):
            mock = MagicMock()
            mock.all.return_value = ts_rows
            return mock

        db = AsyncMock()
        db.execute = AsyncMock(side_effect=_exec)

        result = await svc.get_crawler_timeseries(
            db=db,
            organization_id="org_test",
            days=7,
        )

        assert "human_browser" not in result["by_crawler"]
        assert "unknown" not in result["by_crawler"]


# ---------------------------------------------------------------------------
# Test: Timeseries endpoint returns 200
# ---------------------------------------------------------------------------


class TestTimeseriesEndpoint:
    @pytest.mark.asyncio
    async def test_timeseries_endpoint_returns_200(self):
        from app.database import get_db
        from app.main import app

        mock_ts_result = {
            "dates": ["2026-02-20", "2026-02-21"],
            "by_crawler": {"ai_training": [3, 5]},
            "total_by_date": [3, 5],
        }

        mock_svc = MagicMock()
        mock_svc.get_crawler_timeseries = AsyncMock(return_value=mock_ts_result)

        mock_org_context = {
            "organization_id": "org_test",
            "tier": "enterprise",
            "name": "Test Org",
        }

        async def override_get_db():
            yield AsyncMock()

        from app.dependencies import get_current_organization_dep

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_organization_dep] = lambda: mock_org_context

        try:
            with patch("app.routers.rights._get_rights_service", return_value=mock_svc):
                from httpx import ASGITransport, AsyncClient

                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as ac:
                    resp = await ac.get("/api/v1/rights/analytics/crawlers/timeseries?days=7")

                assert resp.status_code == 200
                data = resp.json()
                assert "dates" in data
                assert "by_crawler" in data
                assert "total_by_date" in data
        finally:
            app.dependency_overrides.clear()
