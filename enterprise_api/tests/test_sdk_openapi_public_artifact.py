import json
from pathlib import Path

import pytest


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
