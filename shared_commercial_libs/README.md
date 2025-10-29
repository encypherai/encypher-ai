# Shared Commercial Libraries

This directory houses proprietary Python libraries that are shared among the commercial tools in the `encypherai-commercial` monorepo (e.g., `audit_log_cli`, `policy_validator_cli`, `dashboard_app/backend`).

## EncypherAI Commercial Shared Library

The `encypher_commercial_shared` package provides a high-level API for working with the EncypherAI package (v2.2.0+) across all commercial tools. It builds on top of the core EncypherAI functionality while adding commercial-specific features.

### Features

- **High-level API**: Simplified interface for embedding and verifying metadata
- **Consistent Results**: Standardized `VerificationResult` class for all verification operations
- **Utility Functions**: Common utilities for scanning directories, generating reports, etc.
- **Rich Console Output**: Improved user experience with progress bars and colored output

### Usage Example

```python
from encypher_commercial_shared import EncypherAI, VerificationResult
from encypher_commercial_shared.utils import scan_directory, generate_report

# Initialize the EncypherAI high-level API
encypher = EncypherAI(
    trusted_signers={"signer1": "path/to/public_key.pem"},
    verbose=True
)

# Verify metadata from text
result = encypher.verify_from_text("Text with embedded metadata")
print(f"Verified: {result.verified}, Signer: {result.signer_id}")

# Scan a directory for files with embedded metadata
results = scan_directory("path/to/directory", encypher)

# Generate a CSV report
generate_report(results, "report.csv")
```

## Installation (as an editable local package)

To make these shared libraries available to other projects within this monorepo during development, install them in editable mode into the virtual environments of the consuming projects.

For example, from the `audit_log_cli` directory, after activating its virtual environment:

```bash
uv pip install -e ../shared_commercial_libs
```

Alternatively, if you configure UV workspaces at the root `pyproject.toml`, UV might handle this more automatically.

## Compatibility

This shared library is compatible with EncypherAI v2.2.0 and later. It provides a stable API that abstracts away the underlying implementation details of the EncypherAI package, making it easier to maintain compatibility across commercial tools as the core package evolves.

## Development and Testing

### Managing Dependencies

This project uses UV for package management. UV manages dependencies through the `pyproject.toml` file and maintains a lockfile (`uv.lock`) for reproducible environments.

```bash
# Navigate to the shared_commercial_libs directory
cd shared_commercial_libs

# Add a regular dependency
uv add requests

# Add a dependency with version constraint
uv add 'rich>=13.0.0'

# Add a development dependency
uv add --dev pytest

# Remove a dependency
uv remove some-package

# Upgrade a specific package
uv lock --upgrade-package rich
```

After adding dependencies, UV automatically updates both the `pyproject.toml` and `uv.lock` files, and installs the packages in your virtual environment.

The development dependencies are specified in the `[project.optional-dependencies.dev]` section of `pyproject.toml`, including:

- `pytest` and `pytest-cov` for testing and code coverage
- `black` and `isort` for code formatting
- `mypy` for type checking
- `ruff` for linting

### Running Tests

The library includes a comprehensive test suite to ensure functionality and compatibility. To run the tests:

```bash
# Run all tests using the test runner
uv run tests/run_tests.py

# Or run tests with pytest directly
uv run -m pytest tests/

# Run individual test modules
uv run -m pytest tests/test_high_level.py
uv run -m pytest tests/test_utils.py

# Run tests with coverage report
uv run -m pytest --cov=encypher_commercial_shared tests/
```

The test suite includes:

- Unit tests for the high-level API (`EncypherAI` class)
- Unit tests for utility functions (scanning, report generation)
- Mock-based tests to avoid dependencies on actual EncypherAI functionality during testing

When implementing new features or fixing bugs, please ensure that appropriate tests are added or updated.
