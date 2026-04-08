# PR #2058 Response Draft

## Strategy

**Approach: One comprehensive PR comment + updated PR description. Do NOT reply to each of the 26 inline comments individually.**

Rationale:
- 26 individual replies would create noise and fragment the conversation
- A single structured comment is easier for lrosenthol and dcondrey to review
- The comment maps every inline comment to its resolution, so nothing is missed
- The updated PR description replaces the stale one that still references removed features

**After posting the comment, resolve all 26 inline threads** to signal that each has been addressed. GitHub's "resolved" state lets the reviewer re-open any they disagree with.

---

## Draft: Updated PR Description

```markdown
## Summary

Adds a section to the C2PA Technical Specification addressing provenance for **distributed compound content**, where constituent assets are served, stored, or distributed as separate resources across different origins.

### The gap

When constituent assets are *distributed* (externally-hosted images in an HTML article, podcast enclosures in an RSS feed, media referenced by a CMS template), existing mechanisms are insufficient:

1. **No child-to-parent discovery.** The `componentOf` ingredient expresses the parent's claim over the child, but provides no reverse discovery path when a child is encountered in isolation.
2. **Signing order constraint.** The parent manifest needs child manifest hashes for `componentOf` ingredients, while each child needs the parent manifest URI.
3. **No implicit structural context.** Unlike PDF or ZIP containers, distributed assets have no container to provide structural context.

### Proposed solution

**One new assertion:**

- **`c2pa.compound.membership`** - placed in each child manifest. Contains a `parentManifestURI` for discovery and an optional `parentManifestHash` (`hashed-uri-map`) for hash-verified integrity. The hash may be added via Update Manifest after the parent has been signed.

**One optional assertion:**

- **`c2pa.compound.content`** - may be placed in the parent manifest to describe editorial structure (component roles, display order, required/optional status). Extends the structural metadata tradition of the XMP Ingredients model for the C2PA manifest architecture.

**Reuses existing mechanisms without modification:**

- `componentOf` ingredient relationship for parent-to-child direction (hash-verified, authenticated)
- `c2pa.placed` action requirements for `componentOf` ingredients
- Standard and Update Manifest types for child signing
- Standard ingredient validation for the parent manifest

**Generation process** (resolves the signing order constraint):

1. Determine parent manifest URI
2. Sign each child with membership assertion (Standard Manifest for new assets, Update Manifest for already-signed assets)
3. Create parent manifest with `componentOf` ingredients referencing signed children
4. Optionally, upgrade child membership via Update Manifest to add `parentManifestHash`

**Structural placement:**

- Security threats in `CompoundContentThreats.adoc` (included by Threats_Harms.adoc)
- Validation procedures in `CompoundContentValidation.adoc` (included by Validation.adoc)
- 6 status codes added to consolidated validation tables

### Files changed

| File | Purpose |
|------|---------|
| `compound-content.adoc` | Distributed compound content section: gap analysis, architecture, assertions, generation process |
| `CompoundContent.puml` | Architecture diagram |
| `compound-membership.cddl` | CDDL schema: `parentManifestURI` + optional `parentManifestHash` + extensibility |
| `compound-content.cddl` | CDDL schema: `components` array with `ingredientRef`, `role`, `displayOrder`, `required` |
| `compound-membership.cbordiag` | Minimal CBOR example |
| `compound-content.cbordiag` | CBOR example with three components |
| `CompoundContentValidation.adoc` | Validation: parent manifest, child in isolation, assertion-specific checks |
| `CompoundContentThreats.adoc` | Threats: spoofed parent, stale URI, manifest inflation |
| `Validation.adoc` | 6 status codes in consolidated tables, assertion validation list entries |
| `Threats_Harms.adoc` | Include directive for compound content threats |
```

---

## Draft: PR Comment

```markdown
@lrosenthol @dcondrey Thank you both for the thorough review. I have pushed a revision that addresses all 26 inline comments and the issue-level feedback. The changes are in a single commit: `2812c773`.

### Architectural changes

**Removed authenticated child-to-parent binding.** The re-signing approach created an unresolvable circular dependency (re-signing a child changes its `activeManifest`, invalidating the parent's `componentOf` hash). The parent's `componentOf` ingredient provides authentication in the parent-to-child direction; the child's membership assertion provides discovery in the reverse direction. This separation is clean and avoids the `componentOf` directionality errors that appeared in three places.

**Added optional `parentManifestHash`.** The membership assertion now accepts an optional `hashed-uri-map` field. Because the parent manifest does not exist at child signing time, this field is absent initially and may be added via Update Manifest after the parent has been signed. This gives claim generators a path to hash-verified child-to-parent integrity without re-signing (which would break the parent's references).

**Two-path child signing.** For children without an existing manifest: Standard Manifest with hard binding + membership assertion. For already-signed children: Update Manifest with `parentOf` ingredient + membership assertion + `c2pa.edited.metadata` action. This directly addresses the question of why a full sign is needed when an Update Manifest suffices.

**Soft binding relationship.** Added a subsection explaining the coexistence of `c2pa.compound.membership` (relationship-based discovery) and `c2pa.soft-binding` (content-identity-based recovery). They serve different use cases and may coexist: soft binding recovers a child's own manifest when metadata has been stripped, and the membership assertion within that manifest leads to the parent.

### Structural changes

**Security content relocated** to `CompoundContentThreats.adoc`, included by `Threats_Harms.adoc`. Three threats (spoofed parent, stale URI, manifest inflation) described without normative "shall" statements, consistent with the existing Threats section.

**Validation content relocated** to `CompoundContentValidation.adoc`, included by `Validation.adoc`. Six status codes added to the consolidated tables. Assertion validation clauses added for both `c2pa.compound.membership` and `c2pa.compound.content`.

**Removed guidance sections.** "Manifest size considerations" and "Compound Content Updates" were guidance, not normative requirements. Removed entirely. The standard C2PA manifest update patterns (using `parentOf` ingredients) apply without restating them here.

**Removed `[IMPORTANT]` blocks and redundant requirements.** No IMPORTANT blocks remain. The paragraph restating standard ingredient validation requirements has been removed.

### Schema changes

**Stripped metadata fields from membership assertion.** Removed `parentTitle`, `role`, and `parentClaimGenerator`. These were plain-text metadata fields that do not belong in C2PA assertions. The `role` field is retained in the parent's `c2pa.compound.content` assertion (where it describes the parent's editorial structure), with recommended values and namespacing conventions for entity-specific extensions.

**XMP heritage acknowledged.** Added NOTEs explaining the relationship between `c2pa.compound.content` and the XMP Ingredients/Pantry model. The assertion provides capabilities beyond `xmpMM:Ingredients`: `hashed-uri` linking to C2PA ingredient assertions, presentation ordering, and required/optional component semantics. This justifies the new assertion rather than relying on pass-through XMP fields in `c2pa.metadata`.

### Comment-by-comment mapping

| # | Comment | Resolution |
|---|---------|-----------|
| 1 | Unresolvable dependency loop | Removed authenticated binding. Generation process signs children first, then parent references them. |
| 2 | Requires cloud-hosted manifests | All retrieval is optional. "may attempt." Explicit: "Network access is always optional." |
| 3 | `componentOf` is parent->child | Fixed. All 15 uses verified parent-to-child. |
| 4 | Not requiring manifest repos | See #2. URI is a discovery hint, not a validation requirement. |
| 5 | `activeManifest` field breaks this | Removed re-signing. `parentManifestHash` via Update Manifest avoids invalidating parent references. |
| 6 | Why not SoftBinding API? | Added "Relationship to soft binding" subsection. Both mechanisms coexist for different use cases. |
| 7 | Don't like plain text in assertions | Removed `parentTitle` from membership assertion. |
| 8 | Free form text or enum? | `role` removed from membership; retained in parent's `c2pa.compound.content` with recommended values + namespacing. |
| 9 | Wrong format for claim generators | Removed `parentClaimGenerator` entirely. |
| 10 | No IMPORTANT blocks | All removed. |
| 11 | XMP Ingredient & Pantry model | Added two NOTEs acknowledging heritage and justifying why `c2pa.compound.content` is needed beyond `xmpMM:Ingredients`. |
| 12 | Re-signing breaks parent references | Removed re-signing. `parentManifestHash` upgrade via Update Manifest does not affect parent's `componentOf` references. |
| 13 | Why not Update Manifest? | Two-path approach: Update Manifest for existing children, Standard Manifest for first-time signing. |
| 14 | Can't mandate c2pa.created | Changed to "the appropriate action for the workflow (e.g., `c2pa.created`, `c2pa.opened`, or `c2pa.edited`)." |
| 15 | Standard requirement, why repeat? | Removed the redundant paragraph. |
| 16 | `componentOf` is parent->child | Fixed. See #3. |
| 17 | Guidance, not core spec | Removed "Manifest size considerations" section. |
| 18 | Reads like guidance | Removed "Compound Content Updates" section. |
| 19 | Security section, not here | Relocated to `CompoundContentThreats.adoc`. |
| 20 | Validation section, not here | Relocated to `CompoundContentValidation.adoc`. |
| 21 | Don't need actual child asset | Clarified in validation: parent's ingredient assertions are self-contained. |
| 22 | "should attempt" -> "may attempt" | Applied. |
| 23 | Network access is ALWAYS OPTIONAL | Explicit statement added to validation. All retrieval uses "may." |
| 24 | "cannot be retrieved" -> "is not retrieved" | Applied. Covers both non-attempt and failure. |
| 25 | `componentOf` direction wrong | Fixed. See #3. |
| 26 | Status codes go in validation | Relocated. 6 codes in consolidated tables. |

I have also updated the PR description to reflect the revised scope.
```

---

## Post-Comment Actions

After the comment is posted and PR description updated:
1. Resolve all 26 inline comment threads
2. Do NOT request a new review yet - let lrosenthol read the summary first
