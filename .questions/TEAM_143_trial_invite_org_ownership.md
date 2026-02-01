# Trial Invite Org Creation Clarification

## Context
We need to auto-create an organization when a super admin sends a trial invitation without selecting an existing org.

## Open Question
Should the newly created organization be owned by the invitee (so they become owner on accept), or is it acceptable for the super admin to be the initial owner and invite the user as admin/member?

## Options Considered
1. Create org with super admin as owner (using existing create_organization). Invitee joins as admin/member. Ownership could be transferred later (not currently supported).
2. Create org without an owner membership and allow trial invitation with role=owner so the invitee becomes owner on acceptance (requires backend changes).

## Recommendation
Please confirm desired ownership behavior before implementation.
