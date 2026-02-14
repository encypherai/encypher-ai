"""
Publisher Attribution Builder

TEAM_191: Builds the publisher attribution string that appears in:
- Sign/verify API responses (via build_publisher_attribution)
- C2PA manifest JSON-LD publisher field (via build_publisher_identity_base)
- X.509 certificate ORGANIZATION_NAME (via build_publisher_identity_base)

Attribution logic:
- Anonymous:   org_id only (e.g., "org_a1b2c3d4")
- Individual:  display_name (e.g., "Sarah Chen")
- Org member:  display_name (e.g., "The Verge")
- Free tier:   append " · Powered by Encypher"
- Whitelabel:  no Encypher suffix
"""

from typing import Any, Dict, Optional


def build_publisher_identity_base(
    *,
    organization_id: str,
    organization_name: Optional[str] = None,
    display_name: Optional[str] = None,
    account_type: Optional[str] = None,
    anonymous_publisher: bool = False,
) -> str:
    """Build the base publisher identity without any branding suffix."""
    del account_type  # Reserved for future branching; current base naming is display_name-first.

    if anonymous_publisher:
        return organization_id
    if display_name:
        return display_name
    if organization_name:
        return organization_name
    return organization_id


def build_publisher_attribution(
    *,
    organization_id: str,
    organization_name: Optional[str] = None,
    display_name: Optional[str] = None,
    account_type: Optional[str] = None,
    anonymous_publisher: bool = False,
    whitelabel: bool = False,
) -> str:
    """
    Build the publisher attribution string for signed content.

    Args:
        organization_id: The org ID (always available)
        organization_name: The org.name field
        display_name: Human-readable publisher name set during onboarding
        account_type: "individual" or "organization" (None if not set)
        anonymous_publisher: If True, show org_id instead of name
        whitelabel: If True, suppress "Powered by Encypher" suffix

    Returns:
        Attribution string for API responses
    """
    if anonymous_publisher:
        return organization_id

    base = build_publisher_identity_base(
        organization_id=organization_id,
        organization_name=organization_name,
        display_name=display_name,
        account_type=account_type,
        anonymous_publisher=anonymous_publisher,
    )

    if whitelabel:
        return base

    return f"{base} · Powered by Encypher"


def build_publisher_attribution_from_org_context(organization: Dict[str, Any]) -> str:
    """
    Convenience wrapper that extracts fields from the org context dict
    used throughout the enterprise API.
    """
    features = organization.get("features", {})
    if not isinstance(features, dict):
        features = {}

    return build_publisher_attribution(
        organization_id=organization.get("organization_id", ""),
        organization_name=organization.get("organization_name"),
        display_name=organization.get("display_name"),
        account_type=organization.get("account_type"),
        anonymous_publisher=organization.get("anonymous_publisher", False),
        whitelabel=features.get("whitelabel", False),
    )


def build_publisher_identity_base_from_org_context(organization: Dict[str, Any]) -> str:
    """Convenience wrapper to derive base publisher identity from org context."""
    return build_publisher_identity_base(
        organization_id=organization.get("organization_id", ""),
        organization_name=organization.get("organization_name"),
        display_name=organization.get("display_name"),
        account_type=organization.get("account_type"),
        anonymous_publisher=organization.get("anonymous_publisher", False),
    )
