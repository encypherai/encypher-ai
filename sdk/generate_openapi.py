#!/usr/bin/env python3
"""Generate OpenAPI specs from the Enterprise API.

This script extracts OpenAPI schemas from FastAPI without starting the server.
It sets minimal environment variables to satisfy config requirements.
"""
import copy
import json
import os
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
    "API_BASE_URL": "https://api.encypherai.com",
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

from app.main import _filter_openapi_for_public, app


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

    api_base_url = os.environ.get("API_BASE_URL", "https://api.encypherai.com")

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

    internal_schema = get_openapi(
        title=f"{app.title} (Internal)",
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    internal_schema = _with_servers(internal_schema, api_base_url=api_base_url)

    with open(public_path, "w") as f:
        json.dump(public_schema, f, indent=2)

    with open(internal_path, "w") as f:
        json.dump(internal_schema, f, indent=2)

    print(f"✅ Generated OpenAPI specs:")
    print(f"   Public:   {public_path}")
    print(f"   Internal: {internal_path}")

    for label, schema in (("Public", public_schema), ("Internal", internal_schema)):
        paths = schema.get("paths", {})
        print(f"\n{label} Stats")
        print(f"   Version: {schema.get('info', {}).get('version', 'unknown')}")
        print(f"   Endpoints: {len(paths)}")
        print(f"   Schemas: {len(schema.get('components', {}).get('schemas', {}))}")


if __name__ == "__main__":
    main()
