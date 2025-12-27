from __future__ import annotations

import json
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_sign_advanced_template_requires_custom_assertions_feature(
    async_client: AsyncClient,
    professional_auth_headers: dict,
) -> None:
    response = await async_client.post(
        "/api/v1/sign/advanced",
        json={
            "document_id": "doc_adv_tpl_001",
            "text": "Hello world.",
            "template_id": "tmpl_does_not_matter",
        },
        headers=professional_auth_headers,
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_sign_advanced_applies_template_assertions(
    async_client: AsyncClient,
    db: AsyncSession,
    business_auth_headers: dict,
) -> None:
    schema_id = f"schema_{uuid.uuid4().hex[:12]}"
    schema_label = f"c2pa.training-mining.v1.{uuid.uuid4().hex[:8]}"
    template_id = f"tmpl_{uuid.uuid4().hex[:12]}"

    await db.execute(
        text(
            """
            INSERT INTO c2pa_assertion_schemas (
                id, organization_id, name, label, version, json_schema,
                is_active, is_public, description
            ) VALUES (
                :id, :org_id, :name, :label, :version, CAST(:json_schema AS jsonb),
                true, true, :description
            )
            """
        ),
        {
            "id": schema_id,
            "org_id": "org_demo",
            "name": "Training Mining",
            "label": schema_label,
            "version": "1.0",
            "json_schema": json.dumps(
                {
                    "type": "object",
                    "properties": {
                        "use": {
                            "type": "object",
                            "properties": {
                                "ai_training": {"type": "boolean"},
                                "ai_inference": {"type": "boolean"},
                                "data_mining": {"type": "boolean"},
                            },
                            "required": [
                                "ai_training",
                                "ai_inference",
                                "data_mining",
                            ],
                        }
                    },
                    "required": ["use"],
                }
            ),
            "description": "AI training and data mining permissions",
        },
    )

    await db.execute(
        text(
            """
            INSERT INTO c2pa_assertion_templates (
                id, organization_id, schema_id, name, template_data, category,
                is_default, is_active, is_public, description
            ) VALUES (
                :id, :org_id, :schema_id, :name, CAST(:template_data AS jsonb), :category,
                false, true, true, :description
            )
            """
        ),
        {
            "id": template_id,
            "org_id": "org_demo",
            "schema_id": schema_id,
            "name": "No AI Training",
            "template_data": json.dumps(
                {
                    "assertions": [
                        {
                            "label": schema_label,
                            "default_data": {
                                "use": {
                                    "ai_training": False,
                                    "ai_inference": False,
                                    "data_mining": False,
                                }
                            },
                        }
                    ]
                }
            ),
            "category": "publisher",
            "description": "Disable AI training/mining",
        },
    )
    await db.commit()

    mock_merkle_root = SimpleNamespace(id="mrk_1", root_hash="root", leaf_count=1, tree_depth=1)

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
        response = await async_client.post(
            "/api/v1/sign/advanced",
            json={
                "document_id": "doc_adv_tpl_002",
                "text": "Hello world.",
                "segmentation_level": "sentence",
                "template_id": template_id,
                "validate_assertions": True,
            },
            headers=business_auth_headers,
        )

    assert response.status_code == 201

    called_assertions = mock_create.call_args.kwargs.get("custom_assertions")
    assert called_assertions is not None
    assert any(
        assertion.get("label") == schema_label
        and assertion.get("data", {}).get("use", {}).get("ai_training") is False
        for assertion in called_assertions
    )


@pytest.mark.asyncio
async def test_sign_advanced_applies_builtin_template_assertions(
    async_client: AsyncClient,
    business_auth_headers: dict,
) -> None:
    mock_merkle_root = SimpleNamespace(id="mrk_2", root_hash="root", leaf_count=1, tree_depth=1)

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
        response = await async_client.post(
            "/api/v1/sign/advanced",
            json={
                "document_id": "doc_adv_tpl_builtin_001",
                "text": "Hello world.",
                "segmentation_level": "sentence",
                "template_id": "tmpl_builtin_no_ai_training_v1",
                "validate_assertions": True,
            },
            headers=business_auth_headers,
        )

    assert response.status_code == 201

    called_assertions = mock_create.call_args.kwargs.get("custom_assertions")
    assert called_assertions is not None
    assert any(
        assertion.get("label") == "c2pa.training-mining.v1"
        and assertion.get("data", {}).get("use", {}).get("ai_training") is False
        for assertion in called_assertions
    )
