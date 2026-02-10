# TEAM_158: Sign & Verify Test App

## Status: IN PROGRESS

## Goal
Local-only web app for testing the sign-existing-PDF flow:
drop an unsigned PDF → sign it → verify it → display results.

## Architecture
- **Frontend**: Vite + React + TailwindCSS (single page)
- **Backend**: FastAPI server wrapping `sign_existing_pdf` + verification proxy
- Location: `tools/sign-verify-app/`

## Tasks
- [ ] 1.0 Scaffold project (Vite + FastAPI)
- [ ] 2.0 Build FastAPI backend (sign + verify endpoints)
- [ ] 3.0 Build React frontend (drop zone + results)
- [ ] 4.0 E2E test
- [ ] 5.0 Update team file
