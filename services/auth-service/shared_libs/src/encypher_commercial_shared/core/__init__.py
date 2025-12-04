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
    scan_directory,
    generate_report,
    debug_unicode,
)

__all__ = [
    "Encypher",
    "VerificationResult",
    "load_public_key_from_pem",
    "scan_directory",
    "generate_report",
    "debug_unicode",
]
