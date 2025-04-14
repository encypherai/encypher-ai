# Installation

EncypherAI is available on PyPI and can be installed using uv.

## Requirements

- Python 3.9 or later
- uv (Python package installer)

## Basic Installation

```bash
uv pip install encypher-ai
```

This installs the core EncypherAI package with all required dependencies.

## Development Installation

For development purposes, you can install EncypherAI with additional development dependencies:

```bash
# Clone the repository
git clone https://github.com/encypherai/encypher-ai.git
cd encypher-ai

# Install with development dependencies
uv pip install -e ".[dev]"
```

## Dependencies

EncypherAI has the following core dependencies:

- `cryptography`: For Ed25519 digital signatures and key management
- `rich`: For formatted terminal output in demo scripts
- `requests`: For HTTP client functionality in API examples
- `python-dotenv`: For environment variable management

For development, additional dependencies include:

- `pytest`: For running tests
- `black`: For code formatting
- `isort`: For import sorting
- `flake8`: For linting
- `mypy`: For static type checking

## Verifying Installation

You can verify that EncypherAI is installed correctly by running:

```python
import encypher
print(encypher.__version__)
```

If the installation was successful, this will print the version number of the installed package.

## Key Management

EncypherAI uses Ed25519 digital signatures for secure metadata verification. You can generate key pairs using the built-in functions:

```python
from encypher.core.keys import generate_key_pair

# Generate a key pair
private_key, public_key = generate_key_pair()

# Store these securely in your application
# The private key should be kept secure and used for signing
# The public key can be distributed for verification
Alternatively, you can use the provided helper script `encypher/examples/generate_keys.py` to generate your initial key pair and get detailed usage instructions.

For more information on key management, see the [Tamper Detection](../user-guide/tamper-detection.md) guide.

## Next Steps

Once you have EncypherAI installed, continue to the [Quick Start Guide](quickstart.md) to learn how to use the package.
