# Team Logs

This directory contains session logs from AI agent conversations (teams).

**IMPORTANT**: Team files reference PRDs — they do NOT duplicate task lists.

## Naming Convention

```
TEAM_XXX_<summary>.md
```

- `XXX` = 3-digit team number (e.g., `001`, `042`)
- `<summary>` = brief description of work (e.g., `auth_refactor`, `dashboard_ux`)

## Template

```markdown
# TEAM_XXX: <Summary>

**Active PRD**: `PRDs/CURRENT/<feature>.md`
**Working on**: Task X.X.X
**Started**: YYYY-MM-DD HH:MM
**Status**: in_progress | completed | blocked

## Session Progress
Reference PRD task numbers. Mark with test verification:
- [x] 2.1.1 — ✅ pytest
- [x] 2.1.2 — ✅ pytest ✅ puppeteer
- [ ] 2.1.3 — in progress

## Changes Made
- `path/to/file.py`: Description of change

## Blockers
- None | Description of blocker

## Handoff Notes
Notes for the next team/session.
```

## Rules
1. Each AI conversation creates ONE team file
2. Team ID is permanent for conversation lifetime
3. Reference PRD tasks — don't duplicate the task list
4. Mark tasks complete ONLY with test verification (✅ pytest, ✅ puppeteer)
5. Update PRD checkboxes when tasks complete
6. Update team file before session ends
7. Document blockers and next steps
