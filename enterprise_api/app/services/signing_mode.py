"""Signing mode resolution helpers."""

from __future__ import annotations

from typing import Any

from app.config import settings

SIGNING_MODE_MANAGED = "managed"
SIGNING_MODE_BYOK = "byok"
SIGNING_MODE_MANAGED_TENANT_CERT = "managed_tenant_cert"
SIGNING_MODE_ORGANIZATION = "organization"

_ALLOWED_SIGNING_MODES = {
    SIGNING_MODE_MANAGED,
    SIGNING_MODE_BYOK,
    SIGNING_MODE_MANAGED_TENANT_CERT,
    SIGNING_MODE_ORGANIZATION,
}


def normalize_signing_mode(mode: str | None) -> str:
    """Normalize a potentially user-provided signing mode."""
    normalized = (mode or "").strip().lower().replace("-", "_")
    if normalized in _ALLOWED_SIGNING_MODES:
        return normalized
    return settings.default_signing_mode_normalized


def resolve_signing_mode(organization: dict[str, Any]) -> str:
    """Resolve effective signing mode for an organization context."""
    org_mode = organization.get("signing_mode")
    if isinstance(org_mode, str) and org_mode.strip():
        return normalize_signing_mode(org_mode)

    features = organization.get("features")
    if isinstance(features, dict):
        feature_mode = features.get("signing_mode")
        if isinstance(feature_mode, str) and feature_mode.strip():
            return normalize_signing_mode(feature_mode)

    return settings.default_signing_mode_normalized
