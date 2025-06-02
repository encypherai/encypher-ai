# Metadata Policy Validation Tool (CLI)

This CLI tool validates EncypherAI metadata in text assets against user-defined policies. It scans files for EncypherAI metadata and checks if they comply with specified policy rules regarding required fields, data types, and allowed values.

## Setup

1.  Ensure Python and UV are installed.
2.  Navigate to this directory (`policy_validator_cli`).
3.  Create and activate a virtual environment:
    ```bash
    uv venv
    .venv\Scripts\activate  # Windows PowerShell
    # source .venv/bin/activate  # Linux/macOS
    ```
4.  Install dependencies:
    ```bash
    uv add typer rich encypher-ai
    ```

## Usage

```bash
python -m policy_validator_cli.app.main validate-metadata --input <path_to_scan> --policy <path_to_policy.json> [--output <output_file.csv>] [--verbose]
```

Or using UV:

```bash
uv run python -m policy_validator_cli.app.main validate-metadata --input <path_to_scan> --policy <path_to_policy.json> [--output <output_file.csv>] [--verbose]
```

### Command Options

- `--input`, `-i`: Path to the directory or file to scan for EncypherAI metadata.
- `--policy`, `-p`: Path to the JSON policy file defining validation rules.
- `--output`, `-o`: Path to save the validation CSV report (default: `validation_report.csv`).
- `--verbose`, `-v`: Show detailed validation results in console output.
- `--help`: Show help message and exit.

### Examples

#### Validate a single file against a policy

```bash
python -m policy_validator_cli.app.main validate-metadata --input ./documents/example.txt --policy ./sample.policy.json
```

#### Scan a directory recursively

```bash
python -m policy_validator_cli.app.main validate-metadata --input ./documents/ --policy ./sample.policy.json --output ./reports/validation_results.csv
```

#### Show detailed validation results

```bash
python -m policy_validator_cli.app.main validate-metadata --input ./documents/ --policy ./sample.policy.json --verbose
```

## Policy File Format

The policy file is a JSON document that defines the rules for validating EncypherAI metadata. Here's an example:

```json
{
  "policy_name": "Standard Document Policy",
  "description": "Ensures all documents have essential tracking and classification metadata.",
  "rules": [
    {
      "key": "document_id",
      "required": true,
      "type": "string",
      "description": "Unique identifier for the document."
    },
    {
      "key": "sensitivity_level",
      "required": true,
      "type": "string",
      "allowed_values": ["public", "internal", "confidential", "highly_confidential"],
      "description": "Classification of the document's sensitivity."
    },
    {
      "key": "department_id",
      "required": false,
      "type": "string",
      "description": "Department responsible for the document."
    }
  ]
}
```

### Policy Schema

- `policy_name`: Name of the policy (required)
- `description`: Description of the policy (optional)
- `rules`: Array of rule objects (required)

### Rule Schema

- `key`: The metadata key to validate (required)
- `required`: Boolean indicating if the key must be present (required)
- `type`: Expected data type - "string", "integer", "boolean", or "number" (optional)
- `allowed_values`: Array of allowed values for the key (optional)
- `description`: Description of the rule (optional)

## Output Format

The tool generates a CSV report with the following columns:

- `source`: Path to the file
- `is_verified`: Whether the EncypherAI signature is verified
- `status`: Status of the verification (e.g., VERIFIED, UNVERIFIED)
- `policy_valid`: Whether the metadata complies with the policy
- `errors`: List of validation errors (if any)
- Additional columns for each metadata key found in the scanned files
