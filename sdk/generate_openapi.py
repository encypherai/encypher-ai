#!/usr/bin/env python3
"""Generate OpenAPI specs from the Enterprise API.

This script extracts OpenAPI schemas from FastAPI without starting the server.
It sets minimal environment variables to satisfy config requirements.
"""
import copy
import json
import os
import subprocess
import sys
from pathlib import Path

from fastapi.openapi.utils import get_openapi

# Clear any existing env vars that might conflict, and set minimal required ones
# This must happen BEFORE any imports that load pydantic-settings
env_vars_to_set = {
    "DATABASE_URL": "postgresql://localhost/encypher",
    "KEY_ENCRYPTION_KEY": "0" * 64,  # 32 bytes hex
    "ENCRYPTION_NONCE": "0" * 24,  # 12 bytes hex
    "ENVIRONMENT": "development",
    "API_BASE_URL": "https://api.encypher.com",
}

# Remove conflicting vars that aren't in Settings
conflicting_vars = [
    "SECRET_KEY", "STRIPE_API_KEY", "STRIPE_WEBHOOK_SECRET",
    "STRIPE_CONNECT_WEBHOOK_SECRET", "STRIPE_PRICE_PROFESSIONAL_MONTHLY",
    "STRIPE_PRICE_PROFESSIONAL_ANNUAL", "STRIPE_PRICE_BUSINESS_MONTHLY",
    "STRIPE_PRICE_BUSINESS_ANNUAL", "NEXTAUTH_SECRET", "NEXTAUTH_URL",
]
for var in conflicting_vars:
    os.environ.pop(var, None)

for key, value in env_vars_to_set.items():
    os.environ[key] = value

# Prevent pydantic-settings from loading .env file
os.environ["_PYDANTIC_SETTINGS_SKIP_ENV_FILE"] = "1"

# Add enterprise_api to path
sys.path.insert(0, str(Path(__file__).parent.parent / "enterprise_api"))

# Monkey-patch Settings to ignore .env file for this script
from pydantic_settings import BaseSettings

original_init = BaseSettings.__init__

def patched_init(self, **kwargs):
    # Force _env_file to None to skip .env loading
    kwargs.setdefault("_env_file", None)
    original_init(self, **kwargs)

BaseSettings.__init__ = patched_init

from app.bootstrap.docs import _filter_openapi_for_public
from app.main import app


def _load_verification_service_openapi(*, api_base_url: str) -> dict:
    verification_service_root = Path(__file__).parent.parent / "services" / "verification-service"
    cmd = [
        "uv",
        "run",
        "python",
        "-c",
        (
            "import json, os; "
            "os.environ.setdefault('_PYDANTIC_SETTINGS_SKIP_ENV_FILE', '1'); "
            "os.environ.setdefault('DATABASE_URL', 'postgresql://localhost/encypher'); "
            "from fastapi import FastAPI; "
            "from fastapi.openapi.utils import get_openapi; "
            "from app.api.v1 import endpoints as v1_endpoints; "
            "app = FastAPI(title='Encypher Verification Service', version='1.0.2', description='Document verification microservice'); "
            "app.include_router(v1_endpoints.router, prefix='/api/v1/verify', tags=['verification']); "
            "spec = get_openapi(title=app.title, version=app.version, description=app.description, routes=app.routes); "
            "spec['servers'] = [{'url': os.environ.get('API_BASE_URL', 'https://api.encypher.com'), 'description': 'Production'}, {'url': 'http://localhost:8005', 'description': 'Local development'}]; "
            "print(json.dumps(spec))"
        ),
    ]
    env = os.environ.copy()
    env["API_BASE_URL"] = api_base_url
    payload = subprocess.check_output(cmd, env=env, text=True, cwd=verification_service_root)
    return json.loads(payload)


def _rewrite_refs(obj: object, mapping: dict[str, str]) -> object:
    if isinstance(obj, dict):
        out: dict = {}
        for k, v in obj.items():
            if k == "$ref" and isinstance(v, str):
                out[k] = mapping.get(v, v)
            else:
                out[k] = _rewrite_refs(v, mapping)
        return out
    if isinstance(obj, list):
        return [_rewrite_refs(v, mapping) for v in obj]
    return obj


def _merge_openapi_specs(*, base: dict, extra: dict) -> dict:
    merged = copy.deepcopy(base)

    merged.setdefault("paths", {})
    added_paths: dict[str, object] = {}
    for path, methods in (extra.get("paths") or {}).items():
        if path in merged["paths"]:
            # Skip paths already present in the base spec (base is authoritative)
            continue
        merged["paths"][path] = methods
        added_paths[path] = methods

    merged.setdefault("tags", [])
    seen_tags = {t.get("name") for t in merged["tags"] if isinstance(t, dict)}
    for tag in extra.get("tags") or []:
        name = tag.get("name") if isinstance(tag, dict) else None
        if name and name not in seen_tags:
            merged["tags"].append(tag)
            seen_tags.add(name)

    merged.setdefault("components", {})
    extra_components = extra.get("components") or {}

    schema_map: dict[str, str] = {}
    base_schemas = merged["components"].setdefault("schemas", {})
    extra_schemas = extra_components.get("schemas") or {}
    for name, schema in extra_schemas.items():
        if name not in base_schemas:
            base_schemas[name] = schema
            continue
        if base_schemas[name] == schema:
            continue
        new_name = f"VerificationService__{name}"
        while new_name in base_schemas:
            new_name = f"{new_name}_"
        schema_map[f"#/components/schemas/{name}"] = f"#/components/schemas/{new_name}"
        base_schemas[new_name] = schema

    if schema_map:
        # Only rewrite $ref pointers in the newly-added extra paths
        for path in added_paths:
            merged["paths"][path] = _rewrite_refs(merged["paths"][path], schema_map)
        # Also rewrite refs inside the renamed schemas themselves
        for new_ref in schema_map.values():
            ref_name = new_ref.split("/")[-1]
            if ref_name in base_schemas:
                base_schemas[ref_name] = _rewrite_refs(
                    base_schemas[ref_name], schema_map
                )

    return merged


def _with_servers(schema: dict, *, api_base_url: str) -> dict:
    schema["servers"] = [
        {"url": api_base_url, "description": "Production"},
        {"url": "http://localhost:8007", "description": "Local development"},
    ]
    return schema


def main():
    """Generate and save OpenAPI specs."""
    output_dir = Path(__file__).parent
    public_path = output_dir / "openapi.public.json"
    internal_path = output_dir / "openapi.internal.json"
    legacy_path = output_dir / "openapi.json"

    api_base_url = os.environ.get("API_BASE_URL", "https://api.encypher.com")

    base_public = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    public_schema = _with_servers(
        _filter_openapi_for_public(copy.deepcopy(base_public)),
        api_base_url=api_base_url,
    )

    verification_public = _load_verification_service_openapi(api_base_url=api_base_url)
    public_schema = _merge_openapi_specs(base=public_schema, extra=verification_public)

    internal_schema = get_openapi(
        title=f"{app.title} (Internal)",
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    internal_schema = _with_servers(internal_schema, api_base_url=api_base_url)

    verification_internal = _load_verification_service_openapi(api_base_url=api_base_url)
    internal_schema = _merge_openapi_specs(base=internal_schema, extra=verification_internal)

    with open(public_path, "w") as f:
        json.dump(public_schema, f, indent=2)

    with open(legacy_path, "w") as f:
        json.dump(public_schema, f, indent=2)

    with open(internal_path, "w") as f:
        json.dump(internal_schema, f, indent=2)

    print("✅ Generated OpenAPI specs:")
    print(f"   Public:   {public_path}")
    print(f"   Internal: {internal_path}")
    print(f"   Legacy:   {legacy_path}")

    for label, schema in (("Public", public_schema), ("Internal", internal_schema)):
        paths = schema.get("paths", {})
        print(f"\n{label} Stats")
        print(f"   Version: {schema.get('info', {}).get('version', 'unknown')}")
        print(f"   Endpoints: {len(paths)}")
        print(f"   Schemas: {len(schema.get('components', {}).get('schemas', {}))}")


if __name__ == "__main__":
    main()
