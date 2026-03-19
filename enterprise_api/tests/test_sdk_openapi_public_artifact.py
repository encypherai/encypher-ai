import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.encoders import jsonable_encoder
from fastapi.openapi.utils import get_openapi

from app.bootstrap.docs import _filter_openapi_for_public
from app.main import app


def _load_public_openapi_artifact() -> dict:
    artifact_path = Path(__file__).resolve().parents[2] / "sdk" / "openapi.public.json"
    payload = artifact_path.read_text(encoding="utf-8")
    return json.loads(payload)


def _load_verification_service_openapi(*, api_base_url: str) -> dict:
    verification_service_root = Path(__file__).resolve().parents[2] / "services" / "verification-service"
    cmd = [
        sys.executable,
        "-c",
        (
            "import json, os, sys; "
            f"sys.path.insert(0, {json.dumps(str(verification_service_root))}); "
            "os.environ.setdefault('_PYDANTIC_SETTINGS_SKIP_ENV_FILE', '1'); "
            "os.environ.setdefault('DATABASE_URL', 'postgresql://localhost/encypher'); "
            "from fastapi import FastAPI; "
            "from fastapi.openapi.utils import get_openapi; "
            "from app.api.v1 import endpoints as v1_endpoints; "
            "app = FastAPI(title='Encypher Verification Service', version='1.0.0', description='Document verification microservice'); "
            "app.include_router(v1_endpoints.router, prefix='/api/v1/verify', tags=['verification']); "
            "spec = get_openapi(title=app.title, version=app.version, description=app.description, routes=app.routes); "
            "print(json.dumps(spec))"
        ),
    ]
    env = dict(**os.environ)
    env["API_BASE_URL"] = api_base_url
    payload = subprocess.check_output(cmd, env=env, text=True)
    return json.loads(payload)


def _merge_openapi_specs(*, base: dict, extra: dict) -> dict:
    merged = json.loads(json.dumps(base))
    merged.setdefault("paths", {})
    for path, methods in (extra.get("paths") or {}).items():
        if path in merged["paths"]:
            continue
        merged["paths"][path] = methods
    return merged


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

    verification_runtime = _load_verification_service_openapi(api_base_url="https://api.encypherai.com")
    runtime = _merge_openapi_specs(base=runtime, extra=verification_runtime)

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
