"""
Core EncypherAI wrapper functionality.

Provides high-level API for embedding and verifying metadata,
plus utility functions for scanning and reporting.
"""

from .api import (
    EncypherAI,
    VerificationResult,
    load_public_key_from_pem,
)
from .utils import (
    debug_unicode,
    generate_report,
    scan_directory,
)

__all__ = [
    "EncypherAI",
    "VerificationResult",
    "load_public_key_from_pem",
    "scan_directory",
    "generate_report",
    "debug_unicode",
]
