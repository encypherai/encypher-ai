# PRD: Linux Start Dev Script

**Status**: in_progress
**Current Goal**: Provide a Linux-optimized `start-dev.sh` that starts the full local stack and streams readable logs for both `apps/marketing-site` and `apps/dashboard`.

## Overview
Local development currently relies on `start-dev.ps1`, which is Windows-oriented. Linux developers need an equivalent script that is aligned with the repo’s Docker Compose full-stack setup and makes frontend logs easy to monitor.

## Objectives
- Provide a Linux `start-dev.sh` that mirrors `start-dev.ps1` behavior.
- Stream/prefix logs for both frontends in a single terminal.
- Support common flags (`--skip-docker`, `--skip-frontend`, `--clean-start`).
- Add a lightweight automated check ensuring the script exists and includes expected behaviors.

## Tasks
- [ ] 1.0 Baseline verification
- [ ] 1.1 Add tests for Linux dev script
- [ ] 1.2 Implement `start-dev.sh`
- [ ] 1.3 Verification (lint/tests) and documentation update

### 1.0 Baseline verification
- [x] 1.0.1 Run `uv run pytest` — ✅ pytest

### 1.1 Add tests for Linux dev script
- [x] 1.1.1 Add pytest asserting `start-dev.sh` exists and contains expected startup commands — ✅ pytest

### 1.2 Implement `start-dev.sh`
- [x] 1.2.1 Create `start-dev.sh` with prerequisite checks, Docker Compose startup, and multiplexed/prefixed frontend logs — ✅ pytest

### 1.3 Verification (lint/tests) and documentation update
- [x] 1.3.1 Run `uv run ruff check .` and `uv run pytest` — ✅ pytest
- [ ] 1.3.2 Run dashboard Puppeteer test suite (if runnable in CI/dev env) — ✅ puppeteer
- [x] 1.3.3 Update root `README.md` to mention `start-dev.sh` for Linux dev workflow — ✅ pytest

## Success Criteria
- `start-dev.sh` starts Docker Compose full-stack and both Next.js apps on ports 3000/3001.
- Frontend logs are visible concurrently with clear per-app prefixes.
- Automated test coverage verifies script presence and key behaviors.

## Completion Notes
- (Fill in once complete)
