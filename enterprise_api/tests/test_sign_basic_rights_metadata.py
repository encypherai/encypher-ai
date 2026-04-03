from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.models.request_models import SignRequest
from app.services.signing_executor import execute_signing


class _FakeScalarResult:
    def scalar_one_or_none(self):
        return None


class _FakeSessionCtx:
    def __init__(self, session):
        self._session = session

    async def __aenter__(self):
        return self._session

    async def __aexit__(self, exc_type, exc, tb):
        return False


@pytest.mark.asyncio
async def test_sign_basic_rights_requires_business() -> None:
    request = SignRequest(
        text="Hello world.",
        document_type="article",
        rights={
            "copyright_holder": "Example Publisher",
            "license_url": "https://example.com/license",
        },
    )

    organization = {
        "organization_id": "org_starter",
        "organization_name": "Starter",
        "tier": "starter",
        "is_demo": True,
        "features": {"custom_assertions": False},
        "custom_assertions_enabled": False,
    }

    db = AsyncMock()

    with patch("app.services.signing_executor._index_in_coalition", new=AsyncMock(return_value=None)):
        with pytest.raises(HTTPException) as exc_info:
            await execute_signing(request=request, organization=organization, db=db)

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_sign_basic_embeds_rights_assertion() -> None:
    request = SignRequest(
        text="Hello world.",
        document_type="article",
        rights={
            "copyright_holder": "Example Publisher",
            "license_url": "https://example.com/license",
            "usage_terms": "RAG allowed with attribution.",
            "syndication_allowed": True,
            "contact_email": "licensing@example.com",
        },
    )

    organization = {
        "organization_id": "org_business",
        "organization_name": "Business",
        "tier": "business",
        "is_demo": True,
        "features": {"custom_assertions": True},
        "custom_assertions_enabled": True,
    }

    db = AsyncMock()
    db.execute = AsyncMock(return_value=_FakeScalarResult())

    content_db = AsyncMock()
    core_db = AsyncMock()
    allocate_mock = AsyncMock(return_value=(0, 2, "https://verify.encypher.com/status/v1/lists/00000000-0000-0000-0000-000000000b01"))

    with (
        patch(
            "app.services.signing_executor.status_service.allocate_status_index",
            new=allocate_mock,
        ),
        patch("app.services.signing_executor._index_in_coalition", new=AsyncMock(return_value=None)),
        patch("app.services.signing_executor.content_session_factory", new=lambda: _FakeSessionCtx(content_db)),
        patch("app.services.signing_executor.core_session_factory", new=lambda: _FakeSessionCtx(core_db)),
        patch("app.services.signing_executor.UnicodeMetadata.embed_metadata", return_value="signed") as mock_embed,
    ):
        result = await execute_signing(request=request, organization=organization, db=db)

    assert result.success is True

    called_assertions = mock_embed.call_args.kwargs.get("custom_assertions")
    assert called_assertions is not None
    assert any(
        assertion.get("label") == "com.encypher.rights.v1"
        and assertion.get("data", {}).get("copyright_holder") == "Example Publisher"
        and assertion.get("data", {}).get("license_url") == "https://example.com/license"
        for assertion in called_assertions
    )
