# TEAM_064: Linux start-dev.sh

**Active PRD**: `PRDs/CURRENT/PRD_Linux_Start_Dev_Script.md`
**Working on**: Task 1.3.2
**Started**: 2026-01-14 19:23 UTC
**Status**: in_progress

## Session Progress
Reference PRD task numbers. Mark with test verification:
- [x] 1.0.1 — ✅ pytest
- [x] 1.1.1 — ✅ pytest
- [x] 1.2.1 — ✅ pytest
- [x] 1.3.1 — ✅ pytest
- [ ] 1.3.2 — (pending)
- [x] 1.3.3 — ✅ pytest

## Changes Made
- `start-dev.sh`: Linux dev startup script (Docker Compose full-stack + prefixed frontend log streaming)
- `stop-dev.sh`: Linux dev shutdown script (Docker Compose down + kill dev ports)
- `enterprise_api/tests/test_linux_start_dev_script.py`: Test asserting `start-dev.sh` contract
- `README.md`: Added Linux/macOS Quick Start section for `start-dev.sh`
- `apps/dashboard/src/app/layout.tsx`: Switched from `@encypher/design-system/styles` to `@encypher/design-system/theme` to avoid mid-bundle CSS `@import` warnings and reduce chunk/HMR instability

## Blockers
- None

## Handoff Notes
- If Puppeteer e2e tests require services running, run `start-dev.sh` first then execute dashboard e2e.
- If dashboard shows `ChunkLoadError`, hard refresh / clear site data after restarting `next dev`.
