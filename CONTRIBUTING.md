# Contributing to EncypherAI Core

Thank you for your interest in contributing to EncypherAI Core! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please be respectful and considerate of others.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with the following information:

1. A clear, descriptive title
2. A detailed description of the issue
3. Steps to reproduce the bug
4. Expected behavior
5. Actual behavior
6. Any relevant logs or screenshots
7. Your environment (OS, Python version, package version)

### Suggesting Enhancements

We welcome suggestions for enhancements! Please create an issue with:

1. A clear, descriptive title
2. A detailed description of the enhancement
3. The motivation for the enhancement
4. Any examples or use cases

### Pull Requests

1. Fork the repository
2. Create a new branch for your feature or bugfix
3. Make your changes
4. Add or update tests as necessary
5. Update documentation as necessary
6. Submit a pull request

#### Pull Request Guidelines

- Follow the existing code style
- Include tests for new features or bug fixes
- Update documentation for any changes
- Keep pull requests focused on a single change
- Reference any related issues in your PR description

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/encypher-ai.git
   cd encypher-ai
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   uv pip install -e ".[dev]"
   ```

4. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

5. Run tests:
   ```bash
   pytest
   ```

## Code Style

We follow PEP 8 style guidelines with Black as our code formatter. All code must pass Black formatting checks before being merged.

### Automated Formatting with Pre-commit

We use pre-commit hooks to automatically format code and check for issues before committing. The hooks will:

1. Format code with Black (including Jupyter notebooks)
2. Sort imports with isort
3. Check for common issues with flake8 and ruff
4. Perform type checking with mypy

After installing the pre-commit hooks (step 4 in Development Setup), they will run automatically on each commit.

### Manual Code Formatting

You can also run the formatting tools manually:

```bash
# Format all Python files
black encypher

# Format Python files including Jupyter notebooks
black --jupyter encypher

# Sort imports
isort encypher

# Run all pre-commit hooks on all files
pre-commit run --all-files
```

## Testing

Please write tests for any new features or bug fixes. We use pytest for testing.

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=encypher
```

## Documentation

Please update documentation for any changes. We use docstrings for function and class documentation.

## Versioning

We use [Semantic Versioning](https://semver.org/). Please ensure that your changes are compatible with the versioning scheme.

## License

By contributing to this project, you agree that your contributions will be licensed under the project's license.

## Questions?

If you have any questions, please feel free to create an issue or contact the maintainers.

Thank you for your contributions!
