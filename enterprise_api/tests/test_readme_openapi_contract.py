import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.encoders import jsonable_encoder
from fastapi.openapi.utils import get_openapi

from app.main import _filter_openapi_for_public, app


_HTTP_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}

_GHOST_INTEGRATION_ENDPOINTS = {
    ("POST", "/api/v1/integrations/ghost"),
    ("GET", "/api/v1/integrations/ghost"),
    ("DELETE", "/api/v1/integrations/ghost"),
    ("POST", "/api/v1/integrations/ghost/regenerate-token"),
    ("POST", "/api/v1/integrations/ghost/webhook"),
    ("POST", "/api/v1/integrations/ghost/sign/{post_id}"),
}


def _extract_backticked_value(cell: str) -> str | None:
    match = re.search(r"`([^`]+)`", cell)
    if not match:
        return None
    return match.group(1).strip()


def _extract_methods_from_cell(cell: str) -> set[str]:
    tokens = [t for t in re.split(r"[^A-Z]+", cell.upper()) if t]
    return {t for t in tokens if t in _HTTP_METHODS}


def _extract_readme_endpoints(readme_text: str) -> set[tuple[str, str]]:
    endpoints: set[tuple[str, str]] = set()

    for raw_line in readme_text.splitlines():
        line = raw_line.strip()
        if not line.startswith("|"):
            continue

        # Ignore header separators like: |---|---|
        if set(line.replace("|", "").strip()) <= {"-", ":"}:
            continue

        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 1:
            continue

        if any(cell.strip().lower() == "internal" for cell in cells):
            continue

        # Skip table header rows
        if any(cell.lower() == "endpoint" for cell in cells[:2]):
            continue

        endpoint_cell = cells[0]
        method_cell = cells[1] if len(cells) > 1 else ""

        endpoint_value = _extract_backticked_value(endpoint_cell)
        if not endpoint_value:
            continue

        # Case A: `POST /api/v1/foo`
        parts = endpoint_value.split()
        if len(parts) >= 2 and parts[0].upper() in _HTTP_METHODS:
            method = parts[0].upper()
            path = parts[1].strip()
            endpoints.add((method, path))
            continue

        # Case B: `/api/v1/foo` + method in separate column
        path = endpoint_value
        methods = _extract_methods_from_cell(method_cell)

        # WS-only endpoints can't be represented in OpenAPI; ignore them.
        if not methods:
            continue

        for method in methods:
            endpoints.add((method, path))

    return endpoints


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


def _extract_openapi_endpoints() -> set[tuple[str, str]]:
    base = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    spec = jsonable_encoder(_filter_openapi_for_public(base))
    verification_spec = _load_verification_service_openapi(api_base_url="https://api.encypherai.com")
    spec = _merge_openapi_specs(base=spec, extra=verification_spec)
    endpoints: set[tuple[str, str]] = set()

    for path, methods in (spec.get("paths") or {}).items():
        if not isinstance(methods, dict):
            continue
        for method, operation in methods.items():
            if method.lower() not in {m.lower() for m in _HTTP_METHODS}:
                continue
            if not isinstance(operation, dict):
                continue
            endpoints.add((method.upper(), path))

    return endpoints


@pytest.mark.asyncio
async def test_readme_endpoint_tables_match_openapi_schema() -> None:
    readme_path = Path(__file__).resolve().parents[1] / "README.md"
    readme_text = readme_path.read_text(encoding="utf-8")

    readme_endpoints = _extract_readme_endpoints(readme_text)
    openapi_endpoints = _extract_openapi_endpoints()

    missing_in_readme = sorted(openapi_endpoints - readme_endpoints)
    extra_in_readme = sorted(readme_endpoints - openapi_endpoints)

    if missing_in_readme or extra_in_readme:
        missing_block = "\n".join(f"- {method} {path}" for method, path in missing_in_readme[:200])
        extra_block = "\n".join(f"- {method} {path}" for method, path in extra_in_readme[:200])
        raise AssertionError(
            "README/OpenAPI endpoint drift detected.\n\n"
            f"Missing in README (OpenAPI -> README): {len(missing_in_readme)}\n"
            + (missing_block + "\n\n" if missing_block else "\n")
            + f"Extra in README (README -> OpenAPI): {len(extra_in_readme)}\n"
            + (extra_block if extra_block else "")
        )


def test_readme_documents_ghost_integration_endpoints() -> None:
    readme_path = Path(__file__).resolve().parents[1] / "README.md"
    readme_text = readme_path.read_text(encoding="utf-8")

    readme_endpoints = _extract_readme_endpoints(readme_text)
    missing_ghost_endpoints = sorted(_GHOST_INTEGRATION_ENDPOINTS - readme_endpoints)

    assert not missing_ghost_endpoints, (
        "README is missing Ghost integration endpoints:\n"
        + "\n".join(f"- {method} {path}" for method, path in missing_ghost_endpoints)
    )
