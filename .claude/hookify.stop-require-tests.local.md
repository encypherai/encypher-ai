---
name: stop-require-tests
enabled: true
event: stop
action: warn
conditions:
  - field: transcript
    operator: not_contains
    pattern: pytest
  - field: transcript
    operator: not_contains
    pattern: npm test
---

No test execution detected in this session (Rule 0).

If you made code changes, verify tests pass before completing:
- Python: `uv run pytest` or `pytest`
- JavaScript: `npm test`
- Full stack: `uv run pytest && npm test`

Mark completed tasks with test evidence: `- [x] 2.1.3 Task name -- ✅ pytest ✅ puppeteer`

If this session involved no code changes, disregard this reminder.
