---
name: block-no-verify
enabled: true
event: bash
action: block
pattern: "git commit.*(--no-verify|-n\\s)"
---

Blocked: --no-verify bypasses pre-commit hooks.

Pre-commit hooks in this repo enforce ruff linting, detect-secrets scanning, and production build verification. Skipping them hides quality and security issues.

Diagnose the hook failure and fix the underlying problem. If the failure is a false positive, explain it to the user so they can make an informed decision.
