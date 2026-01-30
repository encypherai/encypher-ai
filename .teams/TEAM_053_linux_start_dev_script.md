# TEAM_053 — Linux start-dev/stop-dev parity

## Status

- **Goal:** Ensure Linux local dev environment has parity scripts (`start-dev.sh`, `stop-dev.sh`) and that the repo can be set up and tested on Linux via UV.
- **State:** Implemented scripts + added pytest coverage for `--help`; updated root deps to be Linux-compatible; verified basic checks.

## Work Completed

- Added `start-dev.sh` (bash) equivalent to `start-dev.ps1`.
- Added `stop-dev.sh` (bash) equivalent to `stop-dev.ps1`.
- Added tests:
  - `enterprise_api/tests/test_start_dev_sh.py`
  - `enterprise_api/tests/test_stop_dev_sh.py`
- Fixed Linux dependency resolution:
  - Scoped `pywin32` to Windows only.
  - Scoped `comtypes` to Windows only.
- Installed/verified dev tooling via UV:
  - `uv sync --all-packages`
  - `uv run pytest enterprise_api/tests/test_start_dev_sh.py enterprise_api/tests/test_stop_dev_sh.py`
  - `uv run ruff check .`

## Notes / Handoff

- On Linux, use `uv sync --all-packages` (workspace-wide) so member deps like `enterprise_api` are available from repo root when running pytest.
- If you want to run the scripts directly: `chmod +x start-dev.sh stop-dev.sh`.
