# PRD: Marketing Site Audit Fixes

**Status:** COMPLETE
**Current Goal:** Verify and finalize changes already applied by audit agent
**Branch:** feat/codebase-audit-fixes

## Overview
The audit agent already applied changes: next_action forwarding from upstream errors, dead code removal, analytics refactoring. Security review found no vulnerabilities. This PRD ensures all changes are clean and lint-passing.

## Objectives
- Verify all applied changes are TypeScript-clean
- Ensure lint passes

## Tasks

### 1.0 Verify Applied Changes
- [x] 1.1 Review `next_action` forwarding in sign/verify route handlers
- [x] 1.2 Review contact page error surfacing
- [x] 1.3 Review EncodeDecodeTool refactoring (isTampered helper, trackToolEvent)

### 2.0 Linting
- [x] 2.1 Run `cd apps/marketing-site && npx tsc --noEmit` -- fixed 2 TS2322 errors in sign/route.ts (cast body.custom_metadata and body.ai_info)
- [x] 2.2 Run lint check -- only pre-existing warnings; no new errors introduced

## Success Criteria
- All tasks checked off
- `tsc --noEmit` passes
- Lint passes

## Completion Notes
- Fixed 2 TypeScript TS2322 errors in `apps/marketing-site/src/app/api/tools/sign/route.ts`: added explicit casts for `body.custom_metadata` (to `Record<string, unknown>`) and `body.ai_info` (to the expected ai_info shape). These were introduced by the audit agent but left with incorrect implicit types.
- All other lint output is pre-existing warnings (no-unused-vars, no-explicit-any, etc.) across the codebase -- not introduced by the audit changes.
- The `require()` error in `pdfTextExtractor.test.ts` is pre-existing and not in scope.
