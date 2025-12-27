from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.request_models import SignRequest
from app.schemas.embeddings import EncodeWithEmbeddingsRequest
from app.services.embedding_executor import encode_document_with_embeddings
from app.services.signing_executor import execute_signing


class _FakeSessionCtx:
    def __init__(self, session):
        self._session = session

    async def __aenter__(self):
        return self._session

    async def __aexit__(self, exc_type, exc, tb):
        return False


async def _ensure_default_template_column(db: AsyncSession) -> None:
    await db.execute(
        text(
            "ALTER TABLE organizations ADD COLUMN IF NOT EXISTS default_c2pa_template_id VARCHAR(64)"
        )
    )
    await db.commit()


@pytest.mark.asyncio
async def test_sign_basic_org_default_template_requires_business(
    db: AsyncSession,
) -> None:
    await _ensure_default_template_column(db)
    await db.execute(
        text(
            "UPDATE organizations SET default_c2pa_template_id = :template_id WHERE id = :org_id"
        ),
        {"template_id": "tmpl_builtin_no_ai_training_v1", "org_id": "org_starter"},
    )
    await db.commit()

    request = SignRequest(text="Hello world.", document_type="article")

    organization = {
        "organization_id": "org_starter",
        "organization_name": "Starter",
        "tier": "starter",
        "is_demo": True,
        "features": {"custom_assertions": False},
        "custom_assertions_enabled": False,
    }

    with patch("app.services.signing_executor._index_in_coalition", new=AsyncMock(return_value=None)):
        with pytest.raises(HTTPException) as exc_info:
            await execute_signing(request=request, organization=organization, db=db)

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_sign_basic_applies_org_default_template_assertions(
    db: AsyncSession,
) -> None:
    await _ensure_default_template_column(db)
    await db.execute(
        text(
            "UPDATE organizations SET default_c2pa_template_id = :template_id WHERE id = :org_id"
        ),
        {"template_id": "tmpl_builtin_no_ai_training_v1", "org_id": "org_business"},
    )
    await db.commit()

    request = SignRequest(text="Hello world.", document_type="article")

    organization = {
        "organization_id": "org_business",
        "organization_name": "Business",
        "tier": "business",
        "is_demo": True,
        "features": {"custom_assertions": True},
        "custom_assertions_enabled": True,
    }

    content_db = AsyncMock()
    core_db = AsyncMock()

    with (
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
        assertion.get("label") == "c2pa.training-mining.v1"
        and assertion.get("data", {}).get("use", {}).get("ai_training") is False
        for assertion in called_assertions
    )


@pytest.mark.asyncio
async def test_sign_advanced_applies_org_default_template_assertions(
    db: AsyncSession,
) -> None:
    await _ensure_default_template_column(db)
    await db.execute(
        text(
            "UPDATE organizations SET default_c2pa_template_id = :template_id WHERE id = :org_id"
        ),
        {"template_id": "tmpl_builtin_no_ai_training_v1", "org_id": "org_business"},
    )
    await db.commit()

    organization = {
        "organization_id": "org_business",
        "organization_name": "Business",
        "tier": "business",
        "is_demo": True,
        "features": {"custom_assertions": True},
        "custom_assertions_enabled": True,
    }

    request = EncodeWithEmbeddingsRequest(
        document_id="doc_adv_default_tpl_001",
        text="Hello world.",
        segmentation_level="sentence",
    )

    mock_merkle_root = SimpleNamespace(id="mrk_default_tpl", root_hash="root", leaf_count=1, tree_depth=1)

    class _FakeSegmenter:
        def __init__(self, text: str, include_words: bool = False):
            self._text = text

        def get_segments(self, level: str):
            return [self._text]

    with (
        patch(
            "app.services.embedding_executor.MerkleService.encode_document",
            new=AsyncMock(return_value={"sentence": mock_merkle_root}),
        ),
        patch("app.utils.segmentation.HierarchicalSegmenter", new=_FakeSegmenter),
        patch(
            "app.services.embedding_service.EmbeddingService.create_embeddings",
            new=AsyncMock(return_value=([], "signed")),
        ) as mock_create,
    ):
        await encode_document_with_embeddings(request=request, organization=organization, db=db)

    called_assertions = mock_create.call_args.kwargs.get("custom_assertions")
    assert called_assertions is not None
    assert any(
        assertion.get("label") == "c2pa.training-mining.v1"
        and assertion.get("data", {}).get("use", {}).get("ai_training") is False
        for assertion in called_assertions
    )
