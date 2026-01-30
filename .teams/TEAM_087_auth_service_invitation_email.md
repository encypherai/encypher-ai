# TEAM_087 Auth Service Invitation Email

## Summary
- Focus: Auth-service invitation email delivery via notification service.
- PRD: PRD_Dashboard_Org_Management_Gaps_Fix.md (Task 3.x).

## Notes
- Start state: invitation email template + helper already added.
- Done: exported build_invitation_email, wired notification-service dispatch for create/resend invitation, added tests.
- Tests: `uv run pytest tests/test_organization_invitation_emails.py` ✅ (ruff missing locally: `uv run ruff check app tests` failed with missing binary).
