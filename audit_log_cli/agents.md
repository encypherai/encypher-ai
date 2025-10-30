# Audit Log CLI - Agent Development Guide

## Overview
The Audit Log CLI is a command-line tool for scanning text assets, validating EncypherAI metadata, and generating compliance reports in CSV format.

## Current Status
✅ **Functional** - Core functionality works
⚠️ **Needs Refactoring** - Code has duplicate imports and incomplete migration

## Architecture

### Dependencies
- **Primary**: `encypher_commercial_shared` (shared high-level API)
- **Fallback**: Direct `encypher-ai` imports for backward compatibility
- **CLI**: `typer` for command-line interface
- **UI**: `rich` for console output and progress bars

### File Structure
```
audit_log_cli/
├── app/
│   ├── __init__.py
│   └── main.py          # Main CLI logic (407 lines)
├── tests/
│   ├── test_main.py
│   ├── test_shared_library.py
│   └── test_pdf_unicode.py
├── pyproject.toml       # Dependencies (has duplicates!)
└── README.md
```

## Known Issues

### 1. Duplicate Dependencies in pyproject.toml
**Problem**: Lines 8-10 and 11-15 have duplicate/conflicting dependencies
```toml
# Duplicates found:
"typer>=0.12.0,<1.0.0"  # Line 8
"typer>=0.16.0"         # Line 11
```

**Fix Required**: Clean up pyproject.toml to have single, consistent dependency versions

### 2. Duplicate Imports in main.py
**Problem**: Lines 1-6 and 14-42 have duplicate/conflicting imports
```python
# Line 1-6: First import block
from encypher_commercial_shared import EncypherAI, VerificationResult

# Line 14-42: Second import block with fallback
try:
    from encypher_ai import EncypherAI, VerificationResult
except ImportError:
    # Fallback stub
```

**Fix Required**: Consolidate imports, use shared library as primary

### 3. Incomplete Function Definition
**Problem**: Lines 72-105 show incomplete function signature
- Function starts at line 72 but parameters continue beyond line 100
- Missing proper function structure

**Fix Required**: Review and fix function definition structure

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
uv run pytest tests/test_main.py

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

### With shared_commercial_libs
- Uses `EncypherAI` high-level API
- Uses `scan_directory` utility
- Uses `generate_report` utility

### With encypher-ai (core)
- Fallback for direct verification
- Used when shared library unavailable

### Standalone Usage
- Can be run independently
- No dependencies on other commercial tools
- Outputs standard CSV format

## Usage Patterns

### Scan Directory
```bash
uv run python app/main.py generate-report \
  --target /path/to/files \
  --output report.csv \
  --verbose
```

### Scan with Trusted Signers
```bash
uv run python app/main.py generate-report \
  --target /path/to/files \
  --trusted-signers ./trusted_signers \
  --output report.csv
```

### Process Text Directly
```bash
uv run python app/main.py generate-report \
  --text "Sample text 1" \
  --text "Sample text 2" \
  --output report.csv
```

## Refactoring Priorities

### High Priority
1. **Fix pyproject.toml duplicates** - Blocks clean installs
2. **Consolidate imports in main.py** - Causes confusion
3. **Fix function definition structure** - Code quality issue

### Medium Priority
4. **Add type hints throughout** - Improve maintainability
5. **Extract verification logic** - Separate concerns
6. **Improve error handling** - Better user experience

### Low Priority
7. **Add more output formats** - JSON, HTML reports
8. **Add filtering options** - By status, metadata fields
9. **Add summary statistics** - Count verified/unverified

## Testing Strategy

### Unit Tests
- `test_main.py` - CLI command tests
- `test_shared_library.py` - Integration with shared lib

### Integration Tests
- `test_pdf_unicode.py` - PDF handling
- Test with various file types
- Test with trusted signers

### Test Data
- `tests/example_files/` - Sample files for testing
- `tests/simple_tampered_examples/` - Tampered content tests

## Common Development Tasks

### Adding a New File Type
1. Update file extension list in `main.py` (line ~240)
2. Add test cases in `tests/`
3. Update README.md with supported formats

### Adding a New Output Format
1. Create new generator function (e.g., `generate_json_report`)
2. Add CLI option for format selection
3. Update documentation

### Modifying Verification Logic
1. Changes should go in `shared_commercial_libs` first
2. Update this CLI to use new shared library version
3. Add tests for new functionality

## Dependencies on Other Components

### Required
- `shared_commercial_libs` - Core verification logic
- `encypher-ai` - Underlying crypto/verification

### Optional
- None (standalone tool)

### Incompatible
- None known

## Performance Considerations

- Uses `rich.progress` for large directory scans
- Processes files sequentially (could parallelize)
- Memory usage scales with file count
- CSV output is streaming-friendly

## Security Considerations

- Trusted signer keys must be in PEM format
- Keys loaded from filesystem (validate paths)
- No network calls (offline operation)
- CSV output may contain sensitive metadata

## Future Enhancements

1. **Parallel Processing** - Speed up large scans
2. **Database Output** - SQLite/PostgreSQL support
3. **Watch Mode** - Monitor directory for changes
4. **API Mode** - Run as HTTP service
5. **Plugin System** - Custom validators/reporters
