from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

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
async def test_sign_basic_embeds_status_list_assertion() -> None:
    request = SignRequest(text="Hello world.", document_type="article")

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
    content_db.execute = AsyncMock()
    content_db.commit = AsyncMock()

    core_db = AsyncMock()
    core_db.execute = AsyncMock()
    core_db.commit = AsyncMock()

    allocate_mock = AsyncMock(
        return_value=(3, 12, "https://status.encypherai.com/v1/org_business/list/3")
    )

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

    allocate_kwargs = allocate_mock.call_args.kwargs
    assert allocate_kwargs["organization_id"] == "org_business"
    assert allocate_kwargs["document_id"]

    called_assertions = mock_embed.call_args.kwargs.get("custom_assertions")
    assert called_assertions is not None
    assert any(
        assertion.get("label") == "org.encypher.status"
        and assertion.get("data", {}).get("statusListCredential") == "https://status.encypherai.com/v1/org_business/list/3"
        and str(assertion.get("data", {}).get("statusListIndex")) == "12"
        for assertion in called_assertions
    )
