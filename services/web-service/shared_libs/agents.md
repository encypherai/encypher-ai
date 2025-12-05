# Shared Commercial Libraries - Agent Development Guide

## Overview
Internal Python library providing high-level APIs and utilities shared across all Encypher commercial tools. Acts as an abstraction layer over the core `encypher-ai` package.

## Current Status
✅ **Production Ready** - Stable API used by multiple tools
✅ **Well Tested** - Comprehensive test suite
✅ **Clean Architecture** - Clear separation of concerns

## Purpose

This library serves as:
1. **Abstraction Layer**: Simplifies `encypher-ai` core library usage
2. **Shared Utilities**: Common functions used across commercial tools
3. **Consistent API**: Standardized interfaces for all commercial tools
4. **Version Compatibility**: Handles `encypher-ai` version changes

## Architecture

### Tech Stack
- **Language**: Python 3.9+
- **Core Dependency**: `encypher-ai` (v2.2.0+)
- **Package Manager**: UV
- **Testing**: pytest, pytest-cov
- **Code Quality**: black, ruff, mypy

### Directory Structure
```
shared_commercial_libs/
├── encypher_commercial_shared/
│   ├── __init__.py          # Public API exports
│   ├── high_level.py        # Encypher high-level API
│   └── utils.py             # Utility functions
├── tests/
│   ├── run_tests.py
│   ├── test_high_level.py
│   └── test_utils.py
├── pyproject.toml
└── README.md
```

## Public API

### Encypher Class
High-level API for embedding and verifying metadata.

```python
from encypher_commercial_shared import Encypher, VerificationResult

# Initialize
ea = Encypher(
    trusted_signers={"signer1": "path/to/public_key.pem"},
    verbose=True
)

# Verify from text
result: VerificationResult = ea.verify_from_text("Text with metadata")

# Verify from file
result: VerificationResult = ea.verify_from_file("document.txt")
```

### VerificationResult Class
Standardized result object for all verification operations.

```python
@dataclass
class VerificationResult:
    verified: bool              # True if signature valid
    signer_id: Optional[str]    # ID of trusted signer (if matched)
    metadata: Dict[str, Any]    # Extracted metadata
    status: str                 # Verification status
    error: Optional[str]        # Error message (if any)
```

### Utility Functions

#### scan_directory()
Scan directory for files with Encypher metadata.

```python
from encypher_commercial_shared.utils import scan_directory

results = scan_directory(
    directory_path="./documents",
    encypher_ai=ea,
    file_extensions=[".txt", ".md", ".pdf"],
    recursive=True,
    show_progress=True
)
```

#### generate_report()
Generate CSV report from verification results.

```python
from encypher_commercial_shared.utils import generate_report

generate_report(
    results=results,
    output_file="report.csv"
)
```

## Development Constraints

### Package Management
**CRITICAL**: Always use UV for package management
```bash
# Navigate to directory
cd shared_commercial_libs

# Add dependency
uv add requests

# Add dev dependency
uv add --dev pytest

# Never edit pyproject.toml directly
# Never use pip commands
```

### Installation as Editable Package
For development, install as editable in consuming projects:

```bash
# From consuming project directory (e.g., audit_log_cli)
uv pip install -e ../shared_commercial_libs
```

### Running Tests
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=encypher_commercial_shared --cov-report=html

# Run specific test
uv run pytest tests/test_high_level.py -v

# Run test runner script
uv run python tests/run_tests.py
```

### Code Quality
```bash
# Linting
uv run ruff check encypher_commercial_shared/

# Formatting
uv run black encypher_commercial_shared/

# Type checking
uv run mypy encypher_commercial_shared/
```

## Integration Points

### Used By (Consumers)
- **audit_log_cli** - Primary consumer, uses all APIs
- **dashboard_app/backend** - Uses verification APIs
- Future commercial tools

### Dependencies (Upstream)
- **encypher-ai** - Core library (v2.2.0+)
- Standard library only (no other external deps)

### Design Philosophy
- **Minimal Dependencies**: Only depend on encypher-ai
- **Stable API**: Changes should be backward compatible
- **Version Pinning**: Pin encypher-ai version for stability
- **No Tool-Specific Logic**: Keep generic and reusable

## API Design Principles

### 1. Consistent Return Types
All verification functions return `VerificationResult`:
```python
# Consistent interface
result = ea.verify_from_text(text)
result = ea.verify_from_file(file_path)
# Both return VerificationResult
```

### 2. Error Handling
Errors are captured in result objects, not raised:
```python
result = ea.verify_from_text(text)
if result.error:
    print(f"Error: {result.error}")
else:
    print(f"Verified: {result.verified}")
```

### 3. Optional Features
Optional features use keyword arguments:
```python
ea = Encypher(
    trusted_signers=signers,  # Optional
    verbose=True              # Optional
)
```

### 4. Sensible Defaults
All parameters have sensible defaults:
```python
# Minimal usage
ea = Encypher()
result = ea.verify_from_text(text)
```

## Common Development Tasks

### Adding a New Utility Function
1. Add function to `encypher_commercial_shared/utils.py`
2. Add docstring with examples
3. Export in `__init__.py` if public
4. Add tests in `tests/test_utils.py`
5. Update README.md with usage example

### Modifying Encypher Class
1. Update `encypher_commercial_shared/high_level.py`
2. Maintain backward compatibility
3. Add tests in `tests/test_high_level.py`
4. Update README.md
5. Update version in `pyproject.toml`
6. Notify consuming projects of changes

### Upgrading encypher-ai Version
1. Test compatibility with new version
2. Update version constraint in `pyproject.toml`
3. Run full test suite
4. Update consuming projects
5. Document breaking changes (if any)

### Adding a New Result Type
1. Define dataclass in `high_level.py`
2. Add to `__init__.py` exports
3. Add tests
4. Update documentation

## Testing Strategy

### Unit Tests
- Test individual functions in isolation
- Mock encypher-ai dependencies
- Fast execution (<1s per test)

### Integration Tests
- Test with real encypher-ai library
- Test file I/O operations
- Test trusted signer validation

### Test Coverage Goals
- high_level.py: 90%+
- utils.py: 85%+
- Overall: 85%+

### Test Data
```
tests/
├── fixtures/
│   ├── sample_signed.txt
│   ├── sample_unsigned.txt
│   └── trusted_signers/
│       └── test_signer.pem
└── test_*.py
```

## Version Compatibility

### encypher-ai Compatibility Matrix
| Shared Lib Version | encypher-ai Version | Status |
|-------------------|---------------------|--------|
| 0.1.x | 2.2.0 - 2.2.x | ✅ Supported |
| 0.2.x | 2.3.0+ | 🚧 In Development |

### Breaking Changes Policy
- **Major Version**: Breaking API changes
- **Minor Version**: New features, backward compatible
- **Patch Version**: Bug fixes only

### Deprecation Policy
1. Mark as deprecated in docstring
2. Add deprecation warning
3. Maintain for 2 minor versions
4. Remove in next major version

## Performance Considerations

### Benchmarks (Target)
| Operation | Time | Notes |
|-----------|------|-------|
| verify_from_text | <50ms | Small text (<1KB) |
| verify_from_file | <100ms | Small file (<10KB) |
| scan_directory | ~50ms/file | Depends on file size |

### Optimization Strategies
- **Lazy Loading**: Load encypher-ai only when needed
- **Caching**: Cache trusted signer keys
- **Batch Operations**: Process multiple files efficiently
- **Async Support**: Consider async APIs for I/O operations

## Known Issues

### None Critical
The library is stable with no major known issues.

### Minor Enhancements
1. **Add async support** - Async versions of APIs
2. **Add batch verification** - Verify multiple texts at once
3. **Add streaming support** - Process large files in chunks
4. **Add caching layer** - Cache verification results

## Future Enhancements

### High Priority
1. **Async APIs** - `async def verify_from_text_async()`
2. **Batch Operations** - `verify_batch(texts: List[str])`
3. **Streaming Support** - `verify_stream(stream: IO)`
4. **Result Caching** - Cache verification results

### Medium Priority
5. **More Output Formats** - JSON, XML report generation
6. **Progress Callbacks** - Custom progress handlers
7. **Validation Schemas** - Pydantic models for metadata
8. **Plugin System** - Custom verification logic

### Low Priority
9. **CLI Tool** - Standalone CLI for testing
10. **Web UI** - Simple web interface for testing
11. **Metrics Collection** - Usage statistics

## Usage Examples

### Basic Verification
```python
from encypher_commercial_shared import Encypher

ea = Encypher()
result = ea.verify_from_text("Text with metadata")

if result.verified:
    print(f"✓ Verified by {result.signer_id}")
    print(f"Metadata: {result.metadata}")
else:
    print(f"✗ Not verified: {result.error}")
```

### With Trusted Signers
```python
from encypher_commercial_shared import Encypher

ea = Encypher(
    trusted_signers={
        "org1": "/path/to/org1_public.pem",
        "org2": "/path/to/org2_public.pem"
    },
    verbose=True
)

result = ea.verify_from_file("document.txt")
if result.signer_id:
    print(f"Signed by trusted signer: {result.signer_id}")
```

### Directory Scanning
```python
from encypher_commercial_shared import Encypher
from encypher_commercial_shared.utils import scan_directory, generate_report

ea = Encypher(verbose=True)

# Scan directory
results = scan_directory(
    directory_path="./documents",
    encypher_ai=ea,
    file_extensions=[".txt", ".md"],
    recursive=True,
    show_progress=True
)

# Generate report
generate_report(results, "verification_report.csv")

# Print summary
verified = sum(1 for r in results.values() if r.verified)
print(f"Verified: {verified}/{len(results)}")
```

### Custom Error Handling
```python
from encypher_commercial_shared import Encypher

ea = Encypher()

try:
    result = ea.verify_from_file("document.txt")
    if result.error:
        # Handle verification error
        if "file not found" in result.error.lower():
            print("File does not exist")
        elif "no metadata" in result.error.lower():
            print("File has no Encypher metadata")
        else:
            print(f"Verification error: {result.error}")
    elif result.verified:
        print("✓ Verification successful")
    else:
        print("✗ Verification failed (invalid signature)")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Troubleshooting

### Import Errors
```bash
# Ensure package is installed
uv pip list | grep encypher-commercial-shared

# Reinstall as editable
cd shared_commercial_libs
uv pip install -e .
```

### Version Conflicts
```bash
# Check encypher-ai version
uv pip show encypher-ai

# Ensure compatible version
uv add 'encypher-ai>=2.2.0,<3.0.0'
```

### Test Failures
```bash
# Run with verbose output
uv run pytest -vv

# Run specific failing test
uv run pytest tests/test_high_level.py::test_verify_from_text -vv

# Check test data
ls tests/fixtures/
```

### Trusted Signer Issues
```bash
# Verify PEM file format
openssl rsa -pubin -in signer.pem -text -noout

# Check file permissions
ls -la trusted_signers/

# Test with absolute paths
ea = Encypher(trusted_signers={
    "signer": "/absolute/path/to/signer.pem"
})
```

## Best Practices

### For Library Developers
1. **Maintain Backward Compatibility**: Don't break existing APIs
2. **Document Everything**: Docstrings for all public functions
3. **Test Thoroughly**: High test coverage required
4. **Version Carefully**: Follow semantic versioning
5. **Communicate Changes**: Notify consuming projects

### For Library Consumers
1. **Pin Version**: Use specific version in pyproject.toml
2. **Test Upgrades**: Test before upgrading versions
3. **Report Issues**: File issues for bugs/features
4. **Use Public API**: Don't import private functions
5. **Handle Errors**: Check result.error field

### Code Style
```python
# Good: Use public API
from encypher_commercial_shared import Encypher
ea = Encypher()

# Bad: Import private modules
from encypher_commercial_shared.high_level import _internal_function

# Good: Check errors
result = ea.verify_from_text(text)
if result.error:
    handle_error(result.error)

# Bad: Assume success
result = ea.verify_from_text(text)
print(result.metadata["key"])  # May fail if error occurred
```

## Contributing

### Adding Features
1. Discuss feature in issue/PR
2. Implement with tests
3. Update documentation
4. Ensure backward compatibility
5. Update version number

### Reporting Bugs
1. Check existing issues
2. Provide minimal reproduction
3. Include version information
4. Include error messages/stack traces

### Code Review Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Backward compatible
- [ ] Type hints added
- [ ] Code formatted (black)
- [ ] Linting passes (ruff)
- [ ] Type checking passes (mypy)

## License
Proprietary - Encypher Commercial Suite

## Related Documentation
- [audit_log_cli](../audit_log_cli/README.md) - Primary consumer
- [encypher-ai](https://github.com/encypher-ai/encypher-ai) - Core library
- [Enterprise API](../enterprise_api/README.md) - Alternative API approach
