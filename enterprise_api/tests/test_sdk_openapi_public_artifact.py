import json
from pathlib import Path

import pytest
from fastapi.encoders import jsonable_encoder
from fastapi.openapi.utils import get_openapi

from app.main import _filter_openapi_for_public, app


def _load_public_openapi_artifact() -> dict:
    artifact_path = Path(__file__).resolve().parents[2] / "sdk" / "openapi.public.json"
    payload = artifact_path.read_text(encoding="utf-8")
    return json.loads(payload)


def _iter_operations(spec: dict):
    paths = spec.get("paths") or {}
    for path, methods in paths.items():
        if not isinstance(methods, dict):
            continue
        for method, op in methods.items():
            if not isinstance(op, dict):
                continue
            yield path, method, op


def _iter_http_operation_keys(spec: dict) -> set[tuple[str, str]]:
    operations: set[tuple[str, str]] = set()
    for path, method, op in _iter_operations(spec):
        _ = op
        if method.lower() in {"get", "post", "put", "patch", "delete"}:
            operations.add((path, method.lower()))
    return operations


def _is_auth_required(op: dict) -> bool:
    security = op.get("security")
    return security is not None


@pytest.mark.asyncio
async def test_sdk_public_openapi_artifact_has_production_servers_first() -> None:
    spec = _load_public_openapi_artifact()
    servers = spec.get("servers")
    assert isinstance(servers, list)
    assert servers

    first = servers[0]
    assert first.get("url") == "https://api.encypherai.com"


@pytest.mark.asyncio
async def test_sdk_public_openapi_artifact_excludes_internal_only_paths_and_tags() -> None:
    spec = _load_public_openapi_artifact()

    internal_tags = {"Admin", "Licensing", "Kafka", "Provisioning", "Audit", "Team Management"}

    tags = spec.get("tags") or []
    tag_names = {t.get("name") for t in tags if isinstance(t, dict)}
    assert not (tag_names & internal_tags)

    for path, _, op in _iter_operations(spec):
        assert not path.startswith("/api/v1/admin")
        assert not path.startswith("/api/v1/licensing")
        assert not path.startswith("/api/v1/org/members")

        op_tags = op.get("tags") or []
        assert not (set(op_tags) & internal_tags)


@pytest.mark.asyncio
async def test_sdk_public_openapi_artifact_matches_runtime_paths_and_security() -> None:
    artifact = _load_public_openapi_artifact()

    base = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    runtime = jsonable_encoder(_filter_openapi_for_public(base))

    assert _iter_http_operation_keys(artifact) == _iter_http_operation_keys(runtime)

    for path, method, op in _iter_operations(artifact):
        if method.lower() not in {"get", "post", "put", "patch", "delete"}:
            continue

        runtime_op = runtime.get("paths", {}).get(path, {}).get(method)
        assert isinstance(runtime_op, dict)

        assert _is_auth_required(op) == _is_auth_required(runtime_op)


@pytest.mark.asyncio
async def test_sdk_public_openapi_legacy_embeddings_endpoints_removed() -> None:
    """Verify legacy embeddings endpoints are removed from public OpenAPI (cleaned up for 1.0)."""
    spec = _load_public_openapi_artifact()
    paths = spec.get("paths") or {}

    # These legacy endpoints should NOT be present (removed in 1.0 cleanup)
    legacy_endpoints = [
        "/api/v1/enterprise/embeddings/encode-with-embeddings",
        "/api/v1/enterprise/embeddings/sign/advanced",
    ]

    for path in legacy_endpoints:
        assert path not in paths, f"Legacy endpoint {path} should be removed"

    # /sign/advanced should be present as the canonical endpoint
    assert "/api/v1/sign/advanced" in paths
