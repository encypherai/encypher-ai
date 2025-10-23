"""
Backward compatibility module for crypto_utils.py.

This module re-exports functions and types from the new modular structure
to maintain backward compatibility with existing code.

DEPRECATED: This module is maintained for backward compatibility only.
New code should import directly from the appropriate modules:
- encypher.core.keys
- encypher.core.payloads
- encypher.core.signing
"""

import warnings

# Import from new modules
from .keys import generate_ed25519_key_pair as generate_key_pair
from .keys import load_private_key_from_data as load_private_key
from .keys import load_public_key_from_data as load_public_key
from .payloads import BasicPayload, ManifestAction, ManifestAiInfo, ManifestPayload, OuterPayload, serialize_payload
from .signing import sign_payload, verify_signature

# Issue deprecation warning
warnings.warn(
    "The crypto_utils module is deprecated and will be removed in a future version. "
    "Please update your imports to use the new module structure: "
    "encypher.core.keys, encypher.core.payloads, and encypher.core.signing.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export all relevant types and functions for backward compatibility
__all__ = [
    # From keys.py
    "generate_key_pair",
    "load_private_key",
    "load_public_key",
    # From payloads.py
    "BasicPayload",
    "ManifestAction",
    "ManifestAiInfo",
    "ManifestPayload",
    "OuterPayload",
    "serialize_payload",
    # From signing.py
    "sign_payload",
    "verify_signature",
]
