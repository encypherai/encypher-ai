"""
Single Source of Truth for pricing and revenue share constants.

TEAM_173: All rev share numbers in the enterprise API MUST import from
this module. Never hardcode publisher/encypher split percentages.

This file mirrors shared_commercial_libs/…/core/pricing_constants.py.
If you change values here, update the shared lib copy too.

Two-track licensing model (Feb 2026):
  - Coalition deals: Encypher negotiates on behalf of coalition → 60/40
  - Self-service deals: Publisher negotiates directly → 80/20
  - Both tracks available to ALL tiers. Split reflects who does the work.
"""

from __future__ import annotations

from typing import Dict


# ---------------------------------------------------------------------------
# Two-track licensing revenue share
# ---------------------------------------------------------------------------

COALITION_PUBLISHER_SHARE: int = 60
COALITION_ENCYPHER_SHARE: int = 40

SELF_SERVICE_PUBLISHER_SHARE: int = 80
SELF_SERVICE_ENCYPHER_SHARE: int = 20

LICENSING_REV_SHARE: Dict[str, Dict[str, int]] = {
    "coalition": {"publisher": COALITION_PUBLISHER_SHARE, "encypher": COALITION_ENCYPHER_SHARE},
    "self_service": {"publisher": SELF_SERVICE_PUBLISHER_SHARE, "encypher": SELF_SERVICE_ENCYPHER_SHARE},
}

# Default coalition rev share applied to all tiers (the "headline" number
# stored on organization rows and returned by the /coalition API).
DEFAULT_COALITION_REV_SHARE: Dict[str, int] = {
    "publisher": COALITION_PUBLISHER_SHARE,
    "encypher": COALITION_ENCYPHER_SHARE,
}

# Convenience: the integer stored in the DB `coalition_rev_share` column
DEFAULT_COALITION_PUBLISHER_PERCENT: int = COALITION_PUBLISHER_SHARE
