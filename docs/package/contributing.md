# Contributing to Encypher

We welcome contributions to Encypher! This document outlines the process for contributing to the project and guidelines to follow.

## Code of Conduct

All contributors are expected to adhere to our Code of Conduct. Please read it before participating.

## Getting Started

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/your-username/encypher-ai.git
   cd encypher-ai
   ```
3. **Set up the development environment**
   ```bash
   uv sync --all-extras
   ```
4. **Create a new branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Guidelines

### Code Style

We follow PEP 8 guidelines for Python code. We use the following tools to enforce code style:

- **ruff**: For linting and formatting
- **mypy**: For static type checking

Run these tools before submitting a pull request:

```bash
# Lint
uv run ruff check .

# Format
uv run ruff format .

# Type check
uv run mypy .
```

### Testing

All code changes should include appropriate tests. We use pytest for testing:

```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=encypher
```

### Documentation

- Update documentation when changing code
- Document all public functions, classes, and methods
- Follow Google style docstrings

## Pull Request Process

1. **Update the README.md or documentation** with details of changes if applicable
2. **Add tests** for new functionality
3. **Ensure all tests pass** before submitting the PR
4. **Update the version numbers** if applicable following [Semantic Versioning](https://semver.org/)
5. **Submit a pull request** to the main repository

## Feature Requests and Bug Reports

- Use the GitHub issue tracker to report bugs or request features
- Check existing issues before creating a new one
- Provide as much information as possible when reporting bugs

## Releasing

Only project maintainers can release new versions. The release process is:

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Tag the release commit
4. Push the tag to GitHub
5. The CI/CD pipeline will automatically build and publish to PyPI

## License

By contributing, you agree that your contributions will be licensed under the project's GNU Affero General Public License v3.0 (AGPL-3.0).
