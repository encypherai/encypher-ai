# Audit Log & Report Generation Utility (CLI)

This CLI tool scans text assets, validates Encypher metadata, and generates auditable reports.

## Compatibility

This tool is compatible with Encypher v2.2.0 and uses the shared commercial library (`encypher_commercial_shared`) which provides a stable high-level API. The dependencies are specified in `pyproject.toml` to ensure version compatibility.

## Setup

1.  Ensure Python and UV are installed.
2.  Navigate to this directory (`audit_log_cli`).
3.  Create and activate a virtual environment:
    ```bash
    uv venv
    source .venv/bin/activate  # Linux/macOS
    # .\.venv\Scripts\activate # Windows PowerShell
    ```
4.  Install dependencies:
    ```bash
    uv pip sync
    ```

## Usage

The primary command is `generate-report`. You can get help with:
```bash
uv run python app/main.py generate-report --help
```

### Scanning Files or Directories

To scan a specific file or an entire directory for text-based files (`.txt`, `.md`, `.json`, etc.) and generate a CSV report:

```bash
# Scan a single file
uv run python app/main.py generate-report --target path/to/your/file.txt --output report.csv

# Scan an entire directory (recursively)
uv run python app/main.py generate-report --target path/to/your/directory/ --output detailed_report.csv
```

### Processing Direct Text Inputs

To process one or more strings directly:

```bash
# Process a single text string
uv run python app/main.py generate-report --text "This is a sample text with <EA-METADATA>...</EA-METADATA>" --output text_report.csv

# Process multiple text strings
uv run python app/main.py generate-report --text "First string" --text "Second string with metadata" --output multi_text_report.csv
```

### Using Trusted Signers for Verification

To verify metadata signatures using trusted signers:

1. First, create a directory to store public key files (in PEM format):

```bash
mkdir -p trusted_signers
```

2. Place your trusted signers' public key files in this directory. The filename (without extension) will be used as the signer ID:

```
trusted_signers/
├── signer1.pem
├── signer2.pem
└── organization-name.pem
```

3. Run the CLI with the `--trusted-signers` option:

```bash
uv run python app/main.py generate-report --target path/to/files --trusted-signers ./trusted_signers --verbose
```

This will verify the metadata signatures against the trusted signers' public keys and include the verification status in the report.

### Options

-   `--target TEXT`: Path to the directory or file to scan. Mutually exclusive with `--text`.
-   `--text TEXT`: List of text strings to process. Can be specified multiple times. Mutually exclusive with `--target`.
-   `--output TEXT`: Path to save the generated CSV report. Defaults to `report.csv`.
-   `--trusted-signers TEXT`: Directory containing trusted signer public keys (.pem files). The filename (without extension) is used as the signer ID.
-   `--verbose, -v`: Enable verbose output with detailed information about the verification process.
-   `--help`: Show help message and exit.

## Development and Testing

### Managing Dependencies

This project uses UV for package management. UV manages dependencies through the `pyproject.toml` file and maintains a lockfile (`uv.lock`) for reproducible environments.

```bash
# Navigate to the audit_log_cli directory
cd audit_log_cli

# Add a regular dependency
uv add typer[all]

# Add a dependency with version constraint
uv add 'rich>=13.0.0'

# Add a development dependency
uv add --dev pytest

# Remove a dependency
uv remove some-package

# Upgrade a specific package
uv lock --upgrade-package rich

# Sync environment with lockfile
uv sync
```

After adding dependencies, UV automatically updates both the `pyproject.toml` and `uv.lock` files, and installs the packages in your virtual environment.

The development dependencies are specified in the `[project.optional-dependencies.dev]` section of `pyproject.toml`, including:

- `pytest` and `pytest-cov` for testing and code coverage
- `black` and `isort` for code formatting
- `mypy` for type checking
- `ruff` for linting
- `typer-cli` for generating shell completions

### Running Tests

The CLI includes tests to verify functionality and integration with the shared commercial library:

```bash
# Run all tests using the test runner
uv run tests/run_tests.py

# Or run tests with pytest directly
uv run -m pytest tests/

# Run the shared library integration test
uv run tests/test_shared_library.py

# Run tests with coverage report
uv run -m pytest --cov=audit_log_cli tests/
```

The `test_shared_library.py` script demonstrates how to use the shared commercial library's functionality from the CLI tool.
