# Shared Commercial Libraries

This directory is intended to house proprietary Python libraries that are shared among the commercial tools in the `encypherai-commercial` monorepo (e.g., `audit_log_cli`, `policy_validator_cli`, `dashboard_app/backend`).

## Structure

Each shared library should be developed as an installable Python package (e.g., `encypher_commercial_shared`).

## Installation (as an editable local package)

To make these shared libraries available to other projects within this monorepo during development, you can install them in editable mode into the virtual environments of the consuming projects.

For example, from the `audit_log_cli` directory, after activating its virtual environment:

```bash
uv pip install -e ../shared_commercial_libs/encypher_commercial_shared
```

(Assuming `encypher_commercial_shared` is the name of your package within `shared_commercial_libs`.)

Alternatively, if you configure UV workspaces at the root `pyproject.toml`, UV might handle this more automatically.
