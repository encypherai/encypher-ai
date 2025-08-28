"""C2PA interoperability helpers for EncypherAI.

This package groups utilities that allow EncypherAI to produce and consume
strictly-compliant C2PA artefacts. Sub-modules are organised by media type.

Exports:
  - Low-level text wrapper helpers from ``text_wrapper``
  - Conversion helpers from the sibling module file ``encypher/interp/c2pa.py``
"""

# Conversion helpers (re-exported for convenience and for tests)
# Note: There's a name collision between this package (c2pa/) and the sibling module file (c2pa.py).
# To avoid circular imports, we dynamically load the sibling module by file path and re-export its symbols.
import importlib.util
import os
from types import ModuleType
from typing import Any, Optional

# Text manifest wrapper utilities
from .text_wrapper import ALGORITHM_IDS, MAGIC, VERSION, encode_wrapper, find_and_decode  # noqa: F401

_sibling_module: Optional[ModuleType] = None
_sibling_path = os.path.normpath(os.path.join(os.path.dirname(__file__), os.pardir, "c2pa.py"))


def _load_sibling_module() -> ModuleType:
    global _sibling_module
    if _sibling_module is None:
        spec = importlib.util.spec_from_file_location("_encypher_interop_c2pa_sibling", _sibling_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Unable to load sibling module at {_sibling_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _sibling_module = module
    return _sibling_module  # type: ignore[return-value]


# Re-exported callables
def encypher_manifest_to_c2pa_like_dict(*args: Any, **kwargs: Any) -> Any:  # noqa: D401
    """Proxy to sibling module function of the same name."""
    return _load_sibling_module().encypher_manifest_to_c2pa_like_dict(*args, **kwargs)


def c2pa_like_dict_to_encypher_manifest(*args: Any, **kwargs: Any) -> Any:  # noqa: D401
    """Proxy to sibling module function of the same name."""
    return _load_sibling_module().c2pa_like_dict_to_encypher_manifest(*args, **kwargs)


def get_c2pa_manifest_schema(*args: Any, **kwargs: Any) -> Any:  # noqa: D401
    """Proxy to sibling module function of the same name."""
    return _load_sibling_module().get_c2pa_manifest_schema(*args, **kwargs)
