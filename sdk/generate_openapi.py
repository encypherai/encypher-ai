#!/usr/bin/env python3
"""
Generate OpenAPI spec from the Enterprise API.

This script extracts the OpenAPI schema from FastAPI without starting the server.
It sets minimal environment variables to satisfy config requirements.
"""
import json
import os
import sys
from pathlib import Path

# Clear any existing env vars that might conflict, and set minimal required ones
# This must happen BEFORE any imports that load pydantic-settings
env_vars_to_set = {
    "DATABASE_URL": "postgresql://localhost/encypher",
    "KEY_ENCRYPTION_KEY": "0" * 64,  # 32 bytes hex
    "ENCRYPTION_NONCE": "0" * 24,  # 12 bytes hex
    "ENVIRONMENT": "development",
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

from app.main import app


def main():
    """Generate and save OpenAPI spec."""
    schema = app.openapi()
    
    # Output path
    output_dir = Path(__file__).parent
    output_path = output_dir / "openapi.json"
    
    # Write spec
    with open(output_path, "w") as f:
        json.dump(schema, f, indent=2)
    
    # Stats
    paths = schema.get("paths", {})
    print(f"✅ Generated OpenAPI spec: {output_path}")
    print(f"   Version: {schema.get('info', {}).get('version', 'unknown')}")
    print(f"   Endpoints: {len(paths)}")
    print(f"   Schemas: {len(schema.get('components', {}).get('schemas', {}))}")
    
    # List endpoints by tag
    tags = {}
    for path, methods in paths.items():
        for method, details in methods.items():
            if method in ("get", "post", "put", "delete", "patch"):
                for tag in details.get("tags", ["Untagged"]):
                    tags.setdefault(tag, []).append(f"{method.upper()} {path}")
    
    print("\n📋 Endpoints by tag:")
    for tag, endpoints in sorted(tags.items()):
        print(f"   {tag}: {len(endpoints)}")


if __name__ == "__main__":
    main()
