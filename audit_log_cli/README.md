# Audit Log & Report Generation Utility (CLI)

This CLI tool scans text assets, validates EncypherAI metadata, and generates auditable reports.

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

### Options

-   `--target TEXT`: Path to the directory or file to scan. Mutually exclusive with `--text`.
-   `--text TEXT`: List of text strings to process. Can be specified multiple times. Mutually exclusive with `--target`.
-   `--output TEXT`: Path to save the generated CSV report. Defaults to `report.csv`.
-   `--help`: Show help message and exit.
