# Policy Validator CLI - Agent Development Guide

## Overview
The Policy Validator CLI validates Encypher metadata against user-defined JSON policy schemas, ensuring compliance with organizational governance standards.

## Current Status
✅ **Functional** - Core functionality works well
✅ **Clean Code** - Well-structured, minimal issues
⚠️ **Needs Enhancement** - Could benefit from additional features

## Architecture

### Dependencies
- **Core**: `encypher-ai` (direct import, v2.1.0+)
- **CLI**: `typer` for command-line interface
- **UI**: `rich` for console output
- **No shared library dependency** - Uses encypher-ai directly

### File Structure
```
policy_validator_cli/
├── app/
│   ├── __init__.py
│   ├── main.py           # CLI entry point (246 lines)
│   ├── policy_parser.py  # Policy schema parsing
│   └── validator.py      # Metadata validation logic
├── tests/
│   ├── test_policy_parser.py
│   └── test_validator.py
├── sample.policy.json    # Example policy
├── pyproject.toml
└── README.md
```

## Key Features

### Policy Schema Support
- JSON-based policy definitions
- Required/optional field validation
- Data type checking (string, integer, boolean, number)
- Allowed values enforcement
- Custom field mapping

### Validation Rules
```json
{
  "policy_name": "Standard Document Policy",
  "description": "Policy description",
  "rules": [
    {
      "key": "document_id",
      "required": true,
      "type": "string",
      "description": "Unique identifier"
    },
    {
      "key": "sensitivity_level",
      "required": true,
      "type": "string",
      "allowed_values": ["public", "internal", "confidential"],
      "description": "Classification level"
    }
  ]
}
```

### Output Format
CSV report with columns:
- `source` - File path
- `is_verified` - Signature verification status
- `status` - Verification status (VERIFIED, UNVERIFIED, etc.)
- `policy_valid` - Policy compliance status
- `errors` - Validation errors (if any)
- Dynamic columns for each metadata key found

## Development Constraints

### Package Management
**CRITICAL**: Always use UV for package management
```bash
# Add dependencies
uv add package-name

# Add dev dependencies
uv add --dev pytest

# Never edit pyproject.toml directly
# Never use pip commands
```

### Testing
```bash
# Run all tests
uv run pytest

# Run specific test
uv run pytest tests/test_validator.py

# With coverage
uv run pytest --cov=app --cov-report=html
```

### Code Quality
```bash
# Linting
uv run ruff check .

# Formatting
uv run black .

# Type checking
uv run mypy app/
```

## Integration Points

### With encypher-ai (core)
- Direct import and usage
- Uses `Encypher()` class for verification
- Extracts metadata from verified content

### Standalone Usage
- Completely independent tool
- No dependencies on other commercial tools
- Can be distributed separately

### No Integration With
- `shared_commercial_libs` - Uses core library directly
- Other CLI tools - Standalone operation
- Web services - Offline tool

## Usage Patterns

### Validate Single File
```bash
uv run python -m policy_validator_cli.app.main validate-metadata \
  --input document.txt \
  --policy policy.json \
  --output report.csv
```

### Validate Directory
```bash
uv run python -m policy_validator_cli.app.main validate-metadata \
  --input ./documents/ \
  --policy policy.json \
  --output validation_report.csv \
  --verbose
```

### With Custom Policy
```bash
uv run python -m policy_validator_cli.app.main validate-metadata \
  --input ./documents/ \
  --policy ./policies/strict_policy.json \
  --output strict_validation.csv
```

## Known Issues

### None Critical
The code is well-structured with no major issues identified.

### Minor Enhancements Needed
1. **Add policy validation** - Validate policy schema before use
2. **Add more output formats** - JSON, HTML reports
3. **Add policy templates** - Common policy examples
4. **Add batch policy support** - Multiple policies at once

## Code Quality

### Strengths
- ✅ Clean separation of concerns (parser, validator, CLI)
- ✅ Good error handling with rich console output
- ✅ Proper use of type hints
- ✅ Clear function names and structure
- ✅ Good progress feedback with rich library

### Areas for Improvement
- ⚠️ Could add more comprehensive type hints
- ⚠️ Could extract file scanning to utility function
- ⚠️ Could add async support for large directories

## Module Breakdown

### main.py
**Purpose**: CLI entry point and orchestration
- Command-line argument parsing
- File discovery and scanning
- Progress reporting
- CSV report generation

**Key Functions**:
- `validate_metadata()` - Main command handler

### policy_parser.py
**Purpose**: Policy schema parsing and validation
- Load JSON policy files
- Validate policy structure
- Parse policy rules

**Key Functions**:
- `load_policy()` - Load and parse policy file
- `PolicySchemaError` - Custom exception

### validator.py
**Purpose**: Metadata validation logic
- Validate metadata against policy rules
- Check required fields
- Validate data types
- Check allowed values

**Key Functions**:
- `validate_metadata()` - Validate metadata dict against policy
- Type checking functions
- Value validation functions

## Testing Strategy

### Unit Tests
- `test_policy_parser.py` - Policy parsing tests
- `test_validator.py` - Validation logic tests

### Test Coverage Goals
- Policy parsing: 100%
- Validation logic: 100%
- CLI commands: 80%+

### Test Data
- Sample policy files in `tests/`
- Mock metadata for validation
- Edge cases (missing fields, wrong types, etc.)

## Common Development Tasks

### Adding a New Validation Rule Type
1. Update policy schema in `policy_parser.py`
2. Add validation logic in `validator.py`
3. Add tests for new rule type
4. Update `sample.policy.json` with example
5. Update README.md

### Adding a New Output Format
1. Create new generator function in `main.py`
2. Add CLI option for format selection
3. Add tests for new format
4. Update documentation

### Modifying File Type Support
1. Update file extension list in `main.py` (line ~79-81)
2. Test with new file types
3. Update README.md with supported formats

## Performance Considerations

- Processes files sequentially (could parallelize)
- Memory usage scales with file count
- Policy parsing done once (cached)
- CSV output is streaming-friendly

## Security Considerations

- Policy files loaded from filesystem (validate paths)
- No network calls (offline operation)
- CSV output may contain sensitive metadata
- No credential storage required

## Future Enhancements

### High Priority
1. **Policy Schema Validation** - Validate policy JSON against schema
2. **Policy Templates** - Provide common policy templates
3. **Better Error Messages** - More detailed validation errors

### Medium Priority
4. **JSON Output Format** - Machine-readable reports
5. **HTML Report Generation** - Visual reports
6. **Policy Inheritance** - Base policies with overrides
7. **Custom Validators** - Plugin system for custom rules

### Low Priority
8. **Parallel Processing** - Speed up large scans
9. **Watch Mode** - Monitor directory for changes
10. **API Mode** - Run as HTTP service
11. **Database Output** - Store results in database

## Comparison with audit_log_cli

### Similarities
- Both scan files for Encypher metadata
- Both generate CSV reports
- Both use typer and rich for CLI

### Differences
- **Purpose**: Policy validation vs. audit reporting
- **Dependencies**: Direct encypher-ai vs. shared library
- **Output**: Policy compliance vs. verification status
- **Complexity**: More focused vs. more features

### When to Use Which
- **audit_log_cli**: General auditing, trusted signers, compliance reports
- **policy_validator_cli**: Policy enforcement, governance, compliance checking

## Dependencies on Other Components

### Required
- `encypher-ai` - Core verification library

### Optional
- None

### Incompatible
- None known

## Deployment Scenarios

### Standalone Binary
- Can be packaged with PyInstaller
- Distribute as single executable
- No external dependencies needed (bundled)

### CI/CD Integration
```yaml
# GitHub Actions example
- name: Validate Content Policy
  run: |
    uv run python -m policy_validator_cli.app.main validate-metadata \
      --input ./content/ \
      --policy ./policies/production.json \
      --output policy_report.csv
    
    # Fail if policy violations found
    if grep -q "False" policy_report.csv; then
      exit 1
    fi
```

### Docker Container
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install uv && uv sync
ENTRYPOINT ["uv", "run", "python", "-m", "policy_validator_cli.app.main"]
```

## Best Practices

### Policy Design
1. Start with minimal required fields
2. Add optional fields gradually
3. Use clear, descriptive field names
4. Document each rule's purpose
5. Test policies with sample data

### Validation Workflow
1. Develop policy in test environment
2. Validate against sample data
3. Review validation errors
4. Refine policy rules
5. Deploy to production

### Error Handling
- Graceful handling of missing files
- Clear error messages for policy issues
- Detailed validation error reporting
- Exit codes for automation

## Troubleshooting

### Policy File Not Found
```bash
# Check file path
ls -la policy.json

# Use absolute path
uv run python -m policy_validator_cli.app.main validate-metadata \
  --input ./docs \
  --policy /absolute/path/to/policy.json
```

### No Files Found to Scan
```bash
# Check directory exists
ls -la ./documents/

# Check file extensions
# Tool scans: .txt, .md, .json, .py, .js, .html, .css, .xml
```

### Policy Validation Errors
```bash
# Run with verbose flag
uv run python -m policy_validator_cli.app.main validate-metadata \
  --input ./docs \
  --policy policy.json \
  --verbose

# Check policy JSON syntax
python -m json.tool policy.json
```

## License
Proprietary - Encypher Commercial Suite
