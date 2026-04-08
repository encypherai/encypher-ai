# TEAM_296 - Compound Content PR #2058 Review Response

## Session: 2026-04-06

### Context
Responding to lrosenthol's CHANGES_REQUESTED review on upstream PR c2pa-org/specs-core#2058.
26 inline comments + 3 issue-level comments. Review requests architectural and structural changes.
Local branch: `code/specs-core` on `feat/compound-content-provenance` (HEAD: 03e2fc75).

### Status: IMPLEMENTATION COMPLETE (uncommitted, pending human review)

All changes are local and uncommitted on `feat/compound-content-provenance`. No commits made to the public branch.

### What was done

1. **Research phase:** Deep dives into SoftBinding API, XMP Ingredient/Pantry model, Update Manifest constraints, ingredient relationship types. All 5 design decisions resolved.

2. **PRD creation:** Full WBS PRD mapping all 26 comments to specific code changes, with design decision analysis.

3. **Implementation:** All PRD tasks implemented locally:
   - Rewrote compound-content.adoc (from ~348 lines to ~204 lines)
   - Stripped membership assertion to `parentManifestURI` + optional `parentManifestHash`
   - Added soft binding relationship subsection
   - Added XMP comparison NOTEs for compound content assertion
   - Added recommended role values with namespacing conventions
   - Created CompoundContentValidation.adoc (validation content relocated)
   - Created CompoundContentThreats.adoc (security content relocated)
   - Added 6 status codes to consolidated tables in Validation.adoc
   - Added assertion validation entries to Validation.adoc
   - Added includes in Threats_Harms.adoc and Validation.adoc
   - Simplified CDDL schema and CBOR examples

4. **Rosenthal-style review:** Created and ran a simulated review with lrosenthol's editorial standards. Found 5 BLOCKING and 6 SHOULD-FIX issues.

5. **Fix pass:** Resolved all BLOCKING and SHOULD-FIX issues:
   - B1: Added optional `parentManifestHash` (`$hashed-uri-map`) for hash-verified child-to-parent reference via Update Manifest upgrade
   - B2: Fixed heading levels in CompoundContentValidation.adoc (`###` to match Validation.adoc convention)
   - B3: Removed normative "shall" from CompoundContentThreats.adoc (Threats section has zero "shall")
   - B4: Added all 6 status codes to consolidated tables (success/informational/failure) in Validation.adoc
   - B5: Added assertion validation clauses for both new assertions in Validation.adoc
   - SF6-SF11: Various normative language, cross-reference, and consistency fixes

6. **Skill creation:** Created reusable `/c2pa-spec-review` skill at `~/.claude/skills/c2pa-spec-review/SKILL.md`

### File changes (uncommitted)

```
Modified:
  compound-content.adoc         | 220 ++++-----------------
  CompoundContent.puml          |   5 +-
  Threats_Harms.adoc            |   2 +
  Validation.adoc               |  10 +
  compound-membership.cbordiag  |   5 +-
  compound-membership.cddl      |  10 +-

New:
  CompoundContentThreats.adoc
  CompoundContentValidation.adoc
```

### Design Decision Summary
| ID | Decision | Resolution |
|----|----------|-----------|
| D1 | Authenticated child-to-parent binding | REMOVE entirely. Added `parentManifestHash` for optional hash-verified upgrade via Update Manifest. |
| D2 | SoftBinding API | HYBRID - keep URI, added soft binding coexistence subsection |
| D3 | c2pa.compound.content assertion | RETAIN - reframed with XMP heritage NOTE, justified vs c2pa.metadata |
| D4 | role in membership | REMOVE from spec. Commercial opportunity: `com.encypher.compound.membership` |
| D5 | Update manifests for membership | YES - two-path approach (Update Manifest for existing children, Standard for first-time) |

### Commercial opportunity identified
Removed spec fields (`role`, `parentTitle`, `parentClaimGenerator`) graduate to `com.encypher.compound.membership` proprietary assertion. Two-tier model: standard discovery (open C2PA) + rich editorial context (Encypher commercial). Separate PRD needed.

### Next steps
1. Human review of all local changes in specs-core
2. Decide when to commit and push to upstream PR
3. Optional: run `/c2pa-spec-review` skill against final changes for one more validation pass
4. Create internal PRD for `com.encypher.compound.membership` commercial assertion

### Suggested commit message
```
feat: address lrosenthol review on compound content PR #2058

Rewrite distributed compound content section based on 26 inline review
comments from lrosenthol (Adobe VP, C2PA co-chair).

Architecture changes:
- Remove authenticated child-to-parent binding (circular dependency)
- Add optional parentManifestHash for hash-verified upgrade via Update Manifest
- Add soft binding relationship subsection
- Present two-path generation: Update Manifest for existing children,
  Standard Manifest for first-time signing

Structural changes:
- Relocate validation to CompoundContentValidation.adoc
- Relocate security threats to CompoundContentThreats.adoc
- Add 6 status codes to consolidated validation tables
- Add assertion validation clauses for both new assertions

Schema changes:
- Strip parentTitle, role, parentClaimGenerator from membership assertion
- Add optional parentManifestHash ($hashed-uri-map) to membership CDDL
- Simplify CBOR example to parentManifestURI only

Content changes:
- Add XMP Ingredients heritage NOTE to compound content assertion
- Add recommended role values with namespacing conventions
- Ensure all normative language follows RFC 2119 conventions
- Remove guidance sections (manifest size, compound content updates)
- Remove IMPORTANT blocks
```
