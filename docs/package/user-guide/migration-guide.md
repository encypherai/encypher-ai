# Migration Guide: EncypherAI Core Package Refactoring

This guide helps users transition from the previous module structure to the new modular structure introduced in version 2.2.0.

## Overview of Changes

The EncypherAI core package has been refactored to improve code organization, clarity, and maintainability. The main changes include:

1. **Module Restructuring**: The `crypto_utils.py` module has been split into three specialized modules:
   - `keys.py`: Key generation, loading, and saving functions
   - `payloads.py`: Payload data structures and serialization
   - `signing.py`: Digital signature operations

2. **Backward Compatibility**: The original `crypto_utils.py` module is maintained as a compatibility layer that re-exports all functions and types from the new modules with deprecation warnings.

3. **Function Renaming**: Some functions have been renamed to better reflect their purpose and avoid naming conflicts:
   - `load_private_key` → `load_private_key_from_data`
   - `load_public_key` → `load_public_key_from_data`

## Recommended Import Updates

### Before (Old Imports)

```python
from encypher.core.crypto_utils import (
    generate_key_pair,
    load_private_key,
    load_public_key,
    sign_payload,
    verify_signature,
    BasicPayload,
    ManifestPayload
)
```

### After (New Imports)

```python
# Key management functions
from encypher.core.keys import (
    generate_ed25519_key_pair as generate_key_pair,
    load_private_key_from_data as load_private_key,
    load_public_key_from_data as load_public_key
)

# Payload data structures
from encypher.core.payloads import (
    BasicPayload,
    ManifestPayload,
    ManifestAction,
    ManifestAiInfo,
    OuterPayload,
    serialize_payload
)

# Signing operations
from encypher.core.signing import (
    sign_payload,
    verify_signature
)
```

## Deprecation Timeline

The compatibility layer in `crypto_utils.py` will be maintained for at least one minor version release cycle to allow for a smooth transition. However, we recommend updating your imports to use the new module structure as soon as possible.

Future releases may remove the compatibility layer, at which point direct imports from the new modules will be required.

## Benefits of the New Structure

1. **Better Code Organization**: Each module has a clear, focused responsibility.
2. **Improved Type Hints**: More specific type hints for better IDE support and static analysis.
3. **Enhanced Documentation**: More detailed docstrings and examples.
4. **Easier Maintenance**: Smaller, more focused modules are easier to maintain and extend.

## Example: Key Generation and Management

```python
# Old approach
from encypher.core.crypto_utils import generate_key_pair, load_private_key

# New approach (recommended)
from encypher.core.keys import generate_ed25519_key_pair, load_private_key_from_data

# Generate keys
private_key, public_key = generate_ed25519_key_pair()

# Save and load keys (using the new helper functions)
from encypher.core.keys import save_ed25519_key_pair_to_files
save_ed25519_key_pair_to_files(private_key, public_key, "private_key.pem", "public_key.pem")
```

## Example: Signing and Verification

```python
# Old approach
from encypher.core.crypto_utils import sign_payload, verify_signature, serialize_payload

# New approach (recommended)
from encypher.core.signing import sign_payload, verify_signature
from encypher.core.payloads import serialize_payload

# Sign and verify
payload_bytes = serialize_payload(payload_data)
signature = sign_payload(private_key, payload_bytes)
is_valid = verify_signature(public_key, payload_bytes, signature)
```

## Need Help?

If you encounter any issues during migration, please:
1. Check the [API documentation](https://docs.encypherai.com/package/api-reference/) for detailed information about each module and function.
2. Open an issue on our [GitHub repository](https://github.com/encypherai/encypher-ai/issues) if you need assistance.
