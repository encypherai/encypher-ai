# Contributing to c2pa-text

Thank you for your interest in contributing to the C2PA Text Reference Implementation! We welcome contributions from the community to help make text provenance a universal standard.

## How to Contribute

1.  **Fork the repository** and create your branch from `main`.
2.  **Install dependencies** for the specific language implementation you are working on (see `README.md`).
3.  **Add tests** for any new functionality.
4.  **Ensure all tests pass** before submitting.
5.  **Lint your code**:
    *   Python: `uv run ruff check .`
    *   TypeScript: `npm run lint` (if applicable) / `tsc`
    *   Rust: `cargo fmt` / `cargo clippy`
    *   Go: `go fmt`

## Pull Request Process

1.  Update the `README.md` with details of changes if applicable.
2.  The PR title should follow the [Conventional Commits](https://www.conventionalcommits.org/) specification (e.g., `feat: add support for ...`, `fix: resolve embedding issue`).
3.  You may merge the Pull Request in once you have the sign-off of two other developers, or if you do not have permission to do that, you may request the second reviewer to merge it for you.

## License

By contributing, you agree that your contributions will be licensed under its MIT License.
