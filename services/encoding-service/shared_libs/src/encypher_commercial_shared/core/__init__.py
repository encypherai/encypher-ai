"""
Core Encypher wrapper functionality.

Provides high-level API for embedding and verifying metadata,
plus utility functions for scanning and reporting.
"""

from .api import (
    Encypher,
    VerificationResult,
    load_public_key_from_pem,
)
from .utils import (
    debug_unicode,
    generate_report,
    scan_directory,
)
from .pricing_constants import (
    COALITION_ENCYPHER_SHARE,
    COALITION_PUBLISHER_SHARE,
    DEFAULT_COALITION_PUBLISHER_PERCENT,
    DEFAULT_COALITION_REV_SHARE,
    LICENSING_REV_SHARE,
    SELF_SERVICE_ENCYPHER_SHARE,
    SELF_SERVICE_PUBLISHER_SHARE,
    get_licensing_rev_share,
)

__all__ = [
    "Encypher",
    "VerificationResult",
    "load_public_key_from_pem",
    "scan_directory",
    "generate_report",
    "debug_unicode",
    "COALITION_PUBLISHER_SHARE",
    "COALITION_ENCYPHER_SHARE",
    "SELF_SERVICE_PUBLISHER_SHARE",
    "SELF_SERVICE_ENCYPHER_SHARE",
    "LICENSING_REV_SHARE",
    "DEFAULT_COALITION_REV_SHARE",
    "DEFAULT_COALITION_PUBLISHER_PERCENT",
    "get_licensing_rev_share",
]
