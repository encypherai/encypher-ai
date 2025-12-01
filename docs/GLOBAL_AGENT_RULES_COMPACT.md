# Global Agent Directives (AI-Optimized)
## Rule 0 — Tests First (TDD)
**Tests are #1 priority. No exceptions.** Task NOT complete until: 1) Unit/Integration tests pass (`uv run pytest`/`npm test`) 2) Frontend: Puppeteer verification 3) Both automated AND manual for UI. TDD: Write tests BEFORE impl → red → green → refactor. Mark complete: `- [x] 2.1.3 Task — ✅ pytest ✅ puppeteer`
## Rule 1 — Quality Over Speed
Good > Fast. Always. Prefer clean designs over quick fixes. Avoid wrappers/shims. Leave codebase better than found. Choose debt-free solutions.
## Rule 2 — Team Identity
Each conversation = one team. On start: 1) Check `.teams/` for highest `TEAM_XXX` 2) Your ID = highest+1 3) Create `.teams/TEAM_XXX_<summary>.md` 4) ID permanent for session. Code comments: `# TEAM_XXX: Reason`
## Rule 3 — SSOT
| Artifact | Location |
|----------|----------|
| Active Work | `PRDs/CURRENT/<feature>.md` |
| Completed | `PRDs/ARCHIVE/` |
| Agent Rules | `agents.md` (per-project) |
| Session Logs | `.teams/TEAM_XXX_*.md` |
| Questions | `.questions/TEAM_XXX_*.md` |
**PRD Format**: Status + Current Goal + Overview (2-3 sentences) + Objectives (unnumbered) + Tasks (WBS: 1.0→1.1→1.1.1, checkboxes) + Success Criteria + Completion Notes. NO time estimates. One PRD per feature.
## Rule 4 — Continuous Work
**Work autonomously until PRD substantially complete.** Loop: task→test→verify→update PRD→next task. Do NOT stop to ask unless: PRD complete OR blocked OR critical decision needed. When finished: re-read PRD, verify all `[x]` with test markers, update status, move to ARCHIVE, THEN report.
## Rule 5 — Session Start
Before code: 1) Read README 2) Read active PRD 3) Read agents.md 4) Check .teams/ 5) Claim Team ID 6) Verify tests pass 7) Begin
## Rule 6 — Session End
Before concluding: [ ] Tests pass [ ] Builds clean [ ] PRD updated [ ] Team file updated [ ] Blockers documented [ ] Handoff notes
## Rule 7 — Change Protocol
1) Run tests (baseline) 2) Write new tests (TDD) 3) Minimal change 4) Run tests (no regression) 5) Fix before proceeding. Never modify fixtures without USER approval.
## Rule 8 — Context Efficiency
Maximize work while context loaded. Don't stop mid-PRD. Continue until complete or blocked. Batch changes. Use as many tool calls as needed.
## Rule 9 — Package Management (Python)
**UV ONLY.** ✅ `uv add pkg` / `uv add --dev pkg` / `uv remove pkg` / `uv sync` / `uv run cmd`. ❌ Never: `pip install` / `uv pip install` / `poetry add` / manual pyproject.toml deps. Manual edits OK for: version, metadata, tool configs. Security: `uv run pip-audit`
## Rule 10 — Code Quality
Python: `uv run ruff check .` / `ruff format .` / `mypy .` / `pytest` / `pip-audit`. JS: `npm run lint` / `format` / `test` / `audit`
## Rule 11 — Tool Usage
1) Search First: Fast Context, find_by_name, grep_search 2) Read Before Edit: MUST read_file before edit 3) Absolute paths 4) Case-insensitive grep default
## Rule 12 — Breaking Changes > Compatibility
Favor clean breaks. Move/rename → let compiler fail → fix sites → remove re-exports. No adapters for old code.
## Rule 13 — No Dead Code
Remove: unused functions, commented code, "kept for reference" logic. Use git history.
## Rule 14 — Ask Questions Early
If ambiguous/conflicting/incomplete → create `.questions/TEAM_XXX_<topic>.md`. Never guess major decisions.
## Rule 15 — TODO Tracking
Code: `# TODO(TEAM_XXX): what`. Global: add to `TODO.md` with file+line.
## Rule 16 — Verification Protocol
After edit: 1) Lint 2) Re-read file 3) Run tests immediately
## Rule 17 — Documentation
Update docs when: new component, breaking API, architecture change, config change.
## Priority Hierarchy
P0: Tests (nothing complete without passing) → P1: Security → P2: Correctness → P3: Quality → P4: Efficiency → P5: Documentation
## Quick Reference
Team ID: `TEAM_XXX` | SSOT: `PRDs/CURRENT/` | Team Files: `.teams/` | Questions: `.questions/` | Security: `pip-audit`/`npm audit` | Task Complete: requires test verification | Work Mode: continuous until PRD complete
