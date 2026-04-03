---
name: stop-require-team-update
enabled: true
event: stop
action: warn
conditions:
  - field: transcript
    operator: regex_match
    pattern: file_path
  - field: transcript
    operator: not_contains
    pattern: .teams/TEAM_
---

File changes detected but no team file update found (Rule 6).

Before ending this session, update `.teams/TEAM_XXX_<summary>.md` with:
- What was completed (reference PRD task numbers)
- Current status of in-progress work
- Any blockers or decisions that need follow-up
- Suggested git commit message

If no TEAM file exists yet for this session, create one by incrementing from the highest existing TEAM number in `.teams/`.
