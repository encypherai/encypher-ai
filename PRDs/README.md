# Product Requirements Documents (PRDs)

**Last Updated:** November 27, 2025

This folder contains Product Requirements Documents for EncypherAI Commercial.

## Folder Structure

```
PRDs/
├── README.md           # This file
├── CURRENT/            # Active PRDs being worked on
├── ARCHIVE/            # Completed PRDs (historical reference)
└── *.md                # Active PRDs at root level
```

## Active PRDs

| PRD | Status | Description |
|-----|--------|-------------|
| `email_verification_system.md` | ✅ Implemented | Email verification flow |
| `enterprise_api_launch_audit.md` | 🔄 In Progress | Launch readiness audit |
| `enterprise_sdk_production_readiness.md` | ✅ Complete | SDK production checklist |
| `test_fixes_v1_launch.md` | ✅ Complete | Test fixes for v1 |
| `unified_auth_architecture.md` | ✅ Implemented | Auth architecture design |

### CURRENT/ Folder

| PRD | Status | Description |
|-----|--------|-------------|
| `PRD_JavaScript_SDK.md` | 📋 Pending | JavaScript/TypeScript SDK |

## Archived PRDs

Completed PRDs are moved to `ARCHIVE/` for historical reference. These include:

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
- Update status section when completing major milestones
- Move to ARCHIVE when fully complete
