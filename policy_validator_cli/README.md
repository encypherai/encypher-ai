# Metadata Policy Validation Tool (CLI)

This CLI tool validates EncypherAI metadata in text assets against user-defined policies.

## Setup

1.  Ensure Python and UV are installed.
2.  Navigate to this directory (`policy_validator_cli`).
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

```bash
# Example (details to be defined)
uv run python app/main.py --input <path_to_scan> --policy <path_to_policy.json> --output validation_report.csv
```
