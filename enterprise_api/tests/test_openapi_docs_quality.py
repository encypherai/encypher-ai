import json
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_public_openapi() -> dict:
    repo_root = _repo_root()
    path = repo_root / "sdk" / "openapi.public.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_public_openapi_does_not_include_internal_endpoints() -> None:
    openapi = _load_public_openapi()
    paths = openapi.get("paths", {})

    assert "/api/v1/usage/reset" not in paths
    assert "/api/v1/stream/health" not in paths


def test_public_openapi_operations_have_summary_and_description() -> None:
    openapi = _load_public_openapi()
    paths = openapi.get("paths", {})

    missing: list[tuple[str, str]] = []
    for path, ops in paths.items():
        if not isinstance(ops, dict):
            continue
        for method, op in ops.items():
            if method.startswith("x-") or not isinstance(op, dict):
                continue
            summary = op.get("summary")
            description = op.get("description")
            if not (isinstance(summary, str) and summary.strip()):
                missing.append((path, f"{method}:summary"))
            if not (isinstance(description, str) and description.strip()):
                missing.append((path, f"{method}:description"))

    assert missing == []
