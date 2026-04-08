"""C2PA interoperability helpers for Encypher.

This package groups utilities that allow Encypher to produce and consume
strictly-compliant C2PA artefacts. Sub-modules are organised by media type.

Exports:
  - Low-level text wrapper helpers from ``text_wrapper``
  - Conversion helpers from ``c2pa_core`` (module previously named ``c2pa.py``)
"""

from typing import Any  # noqa: F401  (kept for public API type hints, if needed)

# Conversion helpers (public re-exports)
from ..c2pa_core import (
    c2pa_like_dict_to_encypher_manifest as c2pa_like_dict_to_encypher_manifest,
)
from ..c2pa_core import (
    encypher_manifest_to_c2pa_like_dict as encypher_manifest_to_c2pa_like_dict,
)
from ..c2pa_core import (
    get_c2pa_manifest_schema as get_c2pa_manifest_schema,
)

# C2PA claim v2 builder
from .c2pa_claim import build_claim_cbor  # noqa: F401

# JUMBF builder/parser (ISO 19566-5)
from .jumbf import (  # noqa: F401
    build_assertion_box,
    build_manifest,
    build_manifest_store,
    generate_manifest_label,
    parse_manifest_store,
    parse_superbox,
)

# Normalisation + hashing helpers
from .text_hashing import (  # noqa: F401
    NormalizedHashResult,
    compute_normalized_hash,
    normalize_text,
)

# Text manifest wrapper utilities (public re-exports)
from .text_wrapper import MAGIC, VERSION, encode_wrapper, find_and_decode, find_wrapper_info_bytes  # noqa: F401
