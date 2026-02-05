from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_sign_advanced_uses_content_db_for_embedding_persistence(
    async_client: AsyncClient,
    professional_auth_headers: dict,
    db,
    content_db,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Ensure tier gate passes even if auth fixture data differs.
    monkeypatch.setenv("EMBEDDING_SIGNATURE_SECRET", "test")

    async def _fake_create_embeddings(*, db: Any, **_kwargs):
        assert db is content_db
        return ([], "hello world")

    with patch(
        "app.services.embedding_service.EmbeddingService.create_embeddings",
        new=AsyncMock(side_effect=_fake_create_embeddings),
    ):
        response = await async_client.post(
            "/api/v1/sign",
            json={
                "text": "Hello world.",
                "options": {
                    "segmentation_level": "sentence",
                    "manifest_mode": "minimal_uuid",
                    "disable_c2pa": True,
                },
            },
            headers=professional_auth_headers,
        )

    assert response.status_code == 201
