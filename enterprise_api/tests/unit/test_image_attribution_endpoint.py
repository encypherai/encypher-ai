"""Unit tests for the image attribution endpoint.

Tests tier gating and basic request handling using mocked DB and auth.
"""

import base64
import os
import sys
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Ensure enterprise_api root is on the path before app imports
_root = Path(__file__).resolve().parents[2]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

os.environ.setdefault("KEY_ENCRYPTION_KEY", "0" * 64)
os.environ.setdefault("ENCRYPTION_NONCE", "0" * 24)
os.environ.setdefault(
    "CORE_DATABASE_URL",
    "postgresql+asyncpg://encypher:encypher_dev_password@127.0.0.1:15432/encypher_content",
)
os.environ.setdefault(
    "CONTENT_DATABASE_URL",
    "postgresql+asyncpg://encypher:encypher_dev_password@127.0.0.1:15432/encypher_content",
)
os.environ.setdefault("DATABASE_URL", os.environ["CORE_DATABASE_URL"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _free_org() -> Dict[str, Any]:
    return {
        "organization_id": "org_free",
        "organization_name": "Free Org",
        "tier": "free",
        "features": {
            "image_fuzzy_search": False,
            "image_signing": True,
        },
        "can_sign": True,
        "can_verify": True,
        "can_lookup": True,
        "permissions": ["sign", "verify"],
    }


def _enterprise_org() -> Dict[str, Any]:
    return {
        "organization_id": "org_enterprise",
        "organization_name": "Enterprise Org",
        "tier": "enterprise",
        "features": {
            "image_fuzzy_search": True,
            "image_signing": True,
        },
        "can_sign": True,
        "can_verify": True,
        "can_lookup": True,
        "permissions": ["sign", "verify", "lookup"],
    }


# ---------------------------------------------------------------------------
# Tests for the endpoint handler function directly
# ---------------------------------------------------------------------------


class TestImageAttributionEndpointTierGating:
    """Tests for scope='all' Enterprise-only gating."""

    @pytest.mark.asyncio
    async def test_scope_all_free_tier_returns_403(self) -> None:
        """scope='all' with free tier features raises 403 HTTPException."""
        from fastapi import HTTPException

        from app.api.v1.enterprise.image_attribution import image_attribution
        from app.schemas.image_attribution_schemas import ImageAttributionRequest

        payload = ImageAttributionRequest(phash="a1b2c3d4e5f67890", scope="all", threshold=10)
        org = _free_org()

        mock_request = MagicMock()
        mock_content_db = AsyncMock()

        with pytest.raises(HTTPException) as exc_info:
            await image_attribution(
                payload=payload,
                request=mock_request,
                organization=org,
                content_db=mock_content_db,
            )

        assert exc_info.value.status_code == 403
        assert "Enterprise" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_scope_org_free_tier_returns_200(self) -> None:
        """scope='org' with free tier features is allowed."""
        from app.api.v1.enterprise.image_attribution import image_attribution
        from app.schemas.image_attribution_schemas import ImageAttributionRequest
        from app.services.image_fingerprint_service import ImageAttributionMatch

        payload = ImageAttributionRequest(phash="a1b2c3d4e5f67890", scope="org", threshold=10)
        org = _free_org()

        mock_request = MagicMock()
        mock_content_db = AsyncMock()

        with patch(
            "app.api.v1.enterprise.image_attribution.search_by_phash",
            new_callable=AsyncMock,
            return_value=[],
        ):
            result = await image_attribution(
                payload=payload,
                request=mock_request,
                organization=org,
                content_db=mock_content_db,
            )

        assert result.success is True
        assert result.scope == "org"
        assert result.match_count == 0

    @pytest.mark.asyncio
    async def test_scope_all_enterprise_tier_allowed(self) -> None:
        """scope='all' with Enterprise tier features is allowed."""
        from app.api.v1.enterprise.image_attribution import image_attribution
        from app.schemas.image_attribution_schemas import ImageAttributionRequest

        payload = ImageAttributionRequest(phash="a1b2c3d4e5f67890", scope="all", threshold=10)
        org = _enterprise_org()

        mock_request = MagicMock()
        mock_content_db = AsyncMock()

        with patch(
            "app.api.v1.enterprise.image_attribution.search_by_phash",
            new_callable=AsyncMock,
            return_value=[],
        ):
            result = await image_attribution(
                payload=payload,
                request=mock_request,
                organization=org,
                content_db=mock_content_db,
            )

        assert result.success is True
        assert result.scope == "all"

    @pytest.mark.asyncio
    async def test_invalid_phash_hex_returns_400(self) -> None:
        """Non-hex phash string raises 400 HTTPException."""
        from fastapi import HTTPException

        from app.api.v1.enterprise.image_attribution import image_attribution
        from app.schemas.image_attribution_schemas import ImageAttributionRequest

        payload = ImageAttributionRequest(phash="ZZZZZZZZZZZZZZZZ", scope="org", threshold=10)
        org = _free_org()

        mock_request = MagicMock()
        mock_content_db = AsyncMock()

        with pytest.raises(HTTPException) as exc_info:
            await image_attribution(
                payload=payload,
                request=mock_request,
                organization=org,
                content_db=mock_content_db,
            )

        assert exc_info.value.status_code == 400
        assert "phash" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_phash_hex_parsed_correctly(self) -> None:
        """Valid hex phash is parsed and passed to search_by_phash."""
        from app.api.v1.enterprise.image_attribution import image_attribution
        from app.schemas.image_attribution_schemas import ImageAttributionRequest

        phash_hex = "a1b2c3d4e5f67890"
        expected_int = int(phash_hex, 16)

        payload = ImageAttributionRequest(phash=phash_hex, scope="org", threshold=5)
        org = _free_org()

        mock_request = MagicMock()
        mock_content_db = AsyncMock()

        captured_args: Dict[str, Any] = {}

        async def mock_search(**kwargs: Any) -> List:
            captured_args.update(kwargs)
            return []

        with patch(
            "app.api.v1.enterprise.image_attribution.search_by_phash",
            side_effect=mock_search,
        ):
            await image_attribution(
                payload=payload,
                request=mock_request,
                organization=org,
                content_db=mock_content_db,
            )

        # The query phash should have been converted from hex to int
        # (may be signed or unsigned int64 depending on value)
        assert "phash_query" in captured_args
        # a1b2c3d4e5f67890 = 11617982470289072272 (> 2^63, so stored as signed negative)
        assert captured_args["phash_query"] == expected_int if expected_int < (1 << 63) else expected_int - (1 << 64)

    @pytest.mark.asyncio
    async def test_response_includes_query_phash_hex(self) -> None:
        """Response query_phash field reflects the hex representation."""
        from app.api.v1.enterprise.image_attribution import image_attribution
        from app.schemas.image_attribution_schemas import ImageAttributionRequest

        phash_hex = "0000000000000001"

        payload = ImageAttributionRequest(phash=phash_hex, scope="org", threshold=10)
        org = _free_org()

        mock_request = MagicMock()
        mock_content_db = AsyncMock()

        with patch(
            "app.api.v1.enterprise.image_attribution.search_by_phash",
            new_callable=AsyncMock,
            return_value=[],
        ):
            result = await image_attribution(
                payload=payload,
                request=mock_request,
                organization=org,
                content_db=mock_content_db,
            )

        assert result.query_phash == phash_hex
