# Product Requirements Documents (PRDs)

**Last Updated:** March 7, 2026

This folder contains Product Requirements Documents for Encypher Commercial.

## Folder Structure

```
PRDs/
|- README.md           # This file
|- CURRENT/            # Active PRDs being worked on
|- ARCHIVE/            # Completed PRDs (historical reference)
`- *.md                # Legacy root-level PRDs retained for reference and transition
```

## Active Work

Active PRDs live in [`CURRENT/`](./CURRENT/). That directory is the only maintained source of truth for in-progress work.

Root-level PRD files still exist for historical continuity and transition work, but they should not be treated as the canonical inventory of active initiatives.

### How to find current work

- Review [`CURRENT/`](./CURRENT/) for actively maintained PRDs.
- Use the status inside each PRD as the authoritative state.
- Treat root-level PRDs as legacy or exceptional unless they are explicitly referenced by current work.

### Root-level legacy PRDs

Examples of root-level PRDs currently retained in this folder include:

- `dashboard_enhancements.md`
- `railway_database_migration_fix.md`
- `team_management_feature.md`
- `ux_ui_design_system_audit.md`

## Archived PRDs

Completed PRDs are moved to [`ARCHIVE/`](./ARCHIVE/) for historical reference. These include:

- Phase 1 implementation guides
- Production hardening plans
- Streaming features PRDs
- WordPress plugin PRDs
- Initial task breakdowns

## PRD Template

When creating a new PRD, include:

1. **Title & Metadata** - Name, date, status, owner
2. **Overview** - Problem statement and goals
3. **Requirements** - Functional and non-functional
4. **Task List** - WBS with checkboxes
5. **Notes** - Constraints, dependencies
6. **Status Updates** - Progress tracking

## Conventions

- Use WBS numbering (1.0, 1.1, 1.1.1)
- Mark tasks with `- [ ]` (pending) or `- [x]` (complete)
- **Tasks require test verification to be marked complete:**
  ```markdown
- [x] 2.1.3 Add login form - pytest passed, puppeteer passed
- [ ] 2.1.4 Add validation - cannot mark complete without tests
```
- Update status section when completing major milestones
- Move to ARCHIVE when fully complete

## Single Source of Truth

PRDs in `CURRENT/` are the **only** source of truth for active work.
- No separate `plan.md` - all planning lives in PRDs
- Team files (`.teams/TEAM_XXX_*.md`) reference PRD tasks, don't duplicate them
- One PRD per feature/initiative
