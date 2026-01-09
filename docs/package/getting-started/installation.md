# Installation

Encypher is available on PyPI and can be installed using uv.

## Requirements

- Python 3.9 or later
- uv (Python package installer)

## Basic Installation

```bash
uv pip install encypher-ai
```

This installs the core Encypher package with all required dependencies.

## Development Installation

For development purposes, you can install Encypher with additional development dependencies:

```bash
# Clone the repository
git clone https://github.com/encypherai/encypher-ai.git
cd encypher-ai

# Install with development dependencies
uv pip install -e ".[dev]"
```

## Dependencies

Encypher has the following core dependencies:

- `cryptography`: For Ed25519 digital signatures and key management.
- `cbor2`: For CBOR encoding/decoding of C2PA-inspired manifests.
- `pycose`: For COSE signing and verification, used in C2PA v2.2 manifests.

For development, additional dependencies include:

- `pytest`: For running tests
- `black`: For code formatting
- `isort`: For import sorting
- `ruff`: For linting and code formatting
- `mypy`: For static type checking

## Verifying Installation

You can verify that Encypher is installed correctly by running:

```python
import encypher
print(encypher.__version__)
```

If the installation was successful, this will print the version number of the installed package.

## Key Management

Encypher uses Ed25519 digital signatures for secure metadata verification. You will need a private key for signing and a corresponding public key for verification.

You can generate key pairs in several ways:

#### 1. Using the CLI (Recommended)

The easiest way to get started is with the built-in CLI command:

```bash
# Generate a new Ed25519 key pair
python -m encypher.examples.cli_example generate-keys --output-dir ./keys --signer-id my-first-signer
```
This will create `private_key.pem` and a public key file named `keys/my-first-signer.pem`.

#### 2. Programmatically

You can also generate keys directly in your code:
```python
from encypher.core.keys import generate_ed25519_key_pair

# Generate a key pair
private_key, public_key = generate_ed25519_key_pair()

# Store these securely in your application.
# The private key should be kept secret and used for signing.
# The public key can be distributed for verification.
```

For more information on key management, see the [Tamper Detection](../user-guide/tamper-detection.md) guide.



## Next Steps

Once you have Encypher installed, continue to the [Quick Start Guide](quickstart.md) to learn how to use the package.
