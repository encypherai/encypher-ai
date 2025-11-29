# Global Agent Directives (AI-Optimized)

> **Purpose**: Universal ruleset for AI coding assistants. Project-agnostic. Token-efficient.
> **Copy this entire file into your IDE's global AI rules/memories.**

---

## Rule 0 — Tests First (TDD)

**Tests are the #1 priority. No exceptions.**

A top-level task is NOT complete until:
1. **Unit/Integration tests pass** (`uv run pytest` / `npm test`)
2. **Frontend: Puppeteer verification** (visual + interaction)
3. **Both automated AND manual verification for UI work**

**TDD Workflow:**
1. Write/update tests BEFORE implementation
2. Run tests → confirm they fail (red)
3. Implement minimal code to pass
4. Run tests → confirm they pass (green)
5. Refactor if needed
6. Tests still pass → task complete

**Marking PRD Tasks Complete:**
```markdown
- [x] 2.1.3 Add login form — ✅ pytest ✅ puppeteer
- [ ] 2.1.4 Add validation — (cannot mark complete without test verification)
```

---

## Rule 1 — Quality Over Speed

Good > Fast. Always.
- Prefer clean designs over quick fixes
- Avoid wrappers/shims/indirection unless truly necessary
- Leave codebase better than found
- Choose debt-free solutions

---

## Rule 2 — Team Identity

Each AI conversation = one team.

**On Session Start:**
1. Check `.teams/` for highest existing `TEAM_XXX` number
2. Your Team ID = highest + 1 (e.g., `TEAM_042`)
3. Create `.teams/TEAM_XXX_<summary>.md` log file
4. Team ID is permanent for conversation lifetime

**Code Comments (when modifying code):**
```python
# TEAM_XXX: Reason for change
```

---

## Rule 3 — Single Source of Truth (SSOT)

| Artifact | Location |
|----------|----------|
| Active Work | `PRDs/CURRENT/<feature>.md` (WBS + checkboxes) |
| Completed PRDs | `PRDs/ARCHIVE/` |
| Architecture | `docs/architecture/` |
| Agent Rules | `agents.md` (per-project) |
| Session Logs | `.teams/TEAM_XXX_*.md` |
| Questions | `.questions/TEAM_XXX_*.md` |

**Rule**: One PRD per feature. Team files reference PRD, don't duplicate tasks.

**PRD Template:**
```markdown
# <Feature Name>

**Status:** 🔄 In Progress | ✅ Complete
**Current Goal:** Task X.X — <description>

## Overview
Brief problem statement and goals (2-3 sentences).

## Objectives
- Objective 1
- Objective 2

## Tasks

### 1.0 <Category>
- [ ] 1.1 Task description
- [ ] 1.2 Task description
  - [ ] 1.2.1 Sub-task if needed

### 2.0 <Category>
- [ ] 2.1 Task description — ✅ pytest ✅ puppeteer (when complete)

## Success Criteria
- Criterion 1
- Criterion 2

## Completion Notes
(Filled when PRD is complete)
```

**PRD Rules:**
- Tasks start at 1.0, sub-tasks 1.1, sub-sub-tasks 1.1.1
- NO time/date estimates (no "2 weeks", no deadlines)
- Update `Current Goal` as you progress
- Mark tasks complete ONLY with test verification

**Team File Format:**
```markdown
# TEAM_042: Dashboard UX Audit

**Active PRD**: `PRDs/CURRENT/PRD_Dashboard_UX_Audit.md`
**Working on**: Task 2.1.3

## Session Progress
- [x] 2.1.1 — ✅ pytest
- [x] 2.1.2 — ✅ pytest ✅ puppeteer
- [ ] 2.1.3 — in progress
```

---

## Rule 4 — Continuous Work Until PRD Complete

**Work autonomously until the PRD is substantially complete.**

1. Start working on the active PRD task
2. Complete task → run tests → verify
3. Update PRD: mark task `[x]` with test verification
4. Check PRD for next incomplete task
5. If more tasks remain → continue working (do NOT stop to ask)
6. Use as many tool calls and tokens as needed
7. Only check in with USER when:
   - PRD is fully complete, OR
   - Blocked by ambiguity/external dependency, OR
   - Critical decision requires USER input

**When you think you're finished:**
1. Re-read the PRD
2. Verify ALL tasks are marked `[x]` with test verification
3. Update `Status` to ✅ Complete
4. Update `Completion Notes`
5. Move PRD to `PRDs/ARCHIVE/`
6. THEN report completion to USER

---

## Rule 5 — Session Start Protocol

Before any code changes:
1. Read project `README.md`
2. Read active PRD in `PRDs/CURRENT/`
3. Read `agents.md` (project-specific rules)
4. Check `.teams/` for recent team logs
5. Claim Team ID and create team file
6. Verify tests pass: `uv run pytest` or `npm test`
7. Then begin implementation

---

## Rule 5 — Session End Protocol

Before concluding:
- [ ] All tests pass (unit, integration, puppeteer if frontend)
- [ ] Code builds/lints clean
- [ ] PRD updated (completed items checked with test verification)
- [ ] Team file updated with progress
- [ ] Blockers/next steps documented
- [ ] Handoff notes written

---

## Rule 6 — Change Protocol (Regression Protection)

1. Run tests (baseline) — must pass
2. Write new tests for the change (TDD)
3. Make minimal change
4. Run tests (verify no regression + new tests pass)
5. If tests fail → fix before proceeding

Never modify test fixtures/golden files unless USER explicitly approves.

---

## Rule 7 — Context Efficiency

- Maximize work while context is loaded
- Don't stop mid-task or mid-PRD if next step is obvious
- Continue working until PRD complete or blocked (see Rule 4)
- Batch related changes to minimize re-reads
- Use as many tool calls as needed — do not artificially limit yourself

---

## Rule 8 — Package Management (Python)

**UV ONLY. Never pip.**

```bash
# ✅ CORRECT
uv add package-name          # Add dependency
uv add --dev pytest          # Add dev dependency
uv remove package-name       # Remove dependency
uv sync                      # Sync environment
uv run <command>             # Run in venv

# ❌ WRONG - Never use
pip install anything
uv pip install anything      # Wrong! Use uv add
poetry add anything
# Manual pyproject.toml edits for dependencies
```

**Manual pyproject.toml edits allowed for:**
- Project version
- Project metadata (name, description, authors)
- Tool configurations (ruff, pytest, etc.)

**Security Scanning:**
```bash
uv run pip-audit             # Scan for vulnerabilities
uv add --dev pip-audit       # Install scanner
```

---

## Rule 9 — Code Quality

```bash
# Python
uv run ruff check .          # Lint
uv run ruff format .         # Format (or black)
uv run mypy .                # Type check
uv run pytest                # Test
uv run pip-audit             # Security scan

# JavaScript/TypeScript
npm run lint                 # ESLint
npm run format               # Prettier
npm test                     # Jest/Vitest
npm audit                    # Security scan
```

---

## Rule 10 — Tool Usage

1. **Search First**: Use Fast Context, `find_by_name`, or `grep_search` before asking user
2. **Read Before Edit**: MUST `read_file` before `edit` or `write_to_file`
3. **Absolute Paths**: Always use absolute paths in tool calls
4. **Case-Insensitive Search**: Default `grep_search` to `CaseSensitive: false`

---

## Rule 11 — Breaking Changes > Fragile Compatibility

Favor clean breaks over compatibility hacks.

**Workflow:**
1. Move or rename the type/function
2. Let the compiler/linter fail
3. Fix import sites one by one
4. Remove temporary re-exports

If writing adapters to "keep old code working" → stop → fix actual call sites.

---

## Rule 12 — No Dead Code

Remove:
- Unused functions/modules
- Commented-out code
- "Kept for reference" logic (use git history)

Repository contains only living, active code.

---

## Rule 13 — Ask Questions Early

If ANY occur:
- Decision is ambiguous
- Requirements conflict
- Plans seem incomplete
- Something feels "off"

Create `.questions/TEAM_XXX_<topic>.md` and ask USER.
Never guess on major decisions.

---

## Rule 14 — TODO Tracking

**In Code:**
```python
# TODO(TEAM_XXX): what is missing
```

**In Global TODO List:**
Add to `TODO.md` with file + line + description.

---

## Rule 15 — Verification Protocol

After editing a file:
1. **Syntactic**: Run linter (`uv run ruff check .`)
2. **Semantic**: Read file again to verify logic
3. **Test**: Run relevant tests immediately

---

## Rule 16 — Documentation Updates

Update docs when:
- Adding new component/service
- Making breaking API changes
- Changing architecture/dependencies
- Modifying configuration requirements

---

## Quick Reference

| Concept | Description |
|---------|-------------|
| Team ID | `TEAM_XXX` — unique per conversation |
| SSOT | `PRDs/CURRENT/` for plans, `agents.md` for rules |
| Team Files | `.teams/TEAM_XXX_*.md` (reference PRD, log progress) |
| Questions | `.questions/TEAM_XXX_*.md` |
| TODO | `TODO.md` global tracking |
| Security | `uv run pip-audit` / `npm audit` |
| Task Complete | Requires test verification (pytest/puppeteer) |
| Work Mode | Continuous until PRD complete or blocked |

---

## Priority Hierarchy

When rules conflict, follow this order:
1. **P0**: Tests (TDD — nothing is complete without passing tests)
2. **P1**: Security (never expose secrets, always sanitize)
3. **P2**: Correctness (no regressions, fix root cause)
4. **P3**: Quality (clean code, no dead code)
5. **P4**: Efficiency (minimize tokens, batch operations)
6. **P5**: Documentation (keep updated)

---

## Frontend Verification Commands

```bash
# Puppeteer via MCP (preferred)
mcp1_puppeteer_navigate → mcp1_puppeteer_screenshot → verify
```

**Frontend task completion requires BOTH:**
1. `npm test` passing (unit/integration)
2. Puppeteer visual/interaction verification

---

*Last Updated: November 2025*
