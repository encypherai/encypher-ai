# TEAM_071 — encypher-ai @context compat release

## Summary
Prepare an `encypher-ai` patch release to fix production verification failures caused by strict C2PA `@context` validation (v2.2 expected vs v2.3 emitted).

## Context
Production verification logs show COSE signature verification succeeds, but verification fails with `SIGNATURE_INVALID` due to `@context` mismatch.

## Decisions
- Keep changelog policy: no `Unreleased` section; changes recorded under `3.0.2`.
- Publish fix as `3.0.2.post1` to avoid inventing a new changelog section while shipping a new artifact.

## Work Items
- [ ] Update `encypher-ai` version to `3.0.2.post1`
- [ ] Add regression test asserting `@context` v2.3 verifies successfully
- [ ] Run `uv run pytest` for `encypher-ai`
- [ ] Update downstream services to use the new published version
