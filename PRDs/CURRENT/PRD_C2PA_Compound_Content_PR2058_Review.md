# PRD: C2PA Compound Content PR #2058 - Review Response Plan

## Status: IMPLEMENTATION COMPLETE (uncommitted, pending human review)

## Current Goal
Address all 26 inline review comments and 3 issue-level comments from lrosenthol (and dcondrey) on upstream PR c2pa-org/specs-core#2058, producing a revised commit on `feat/compound-content-provenance`.

## Overview
lrosenthol reviewed PR #2058 on 2026-04-05 and requested changes across 26 inline comments. The comments cluster into 6 root causes: incorrect `componentOf` directionality, a circular dependency in the re-signing workflow, cloud/network dependency assumptions that violate C2PA's offline-first principle, spec structure violations (security/validation/guidance in the wrong sections), non-conforming assertion fields, and an overly prescriptive generation process. This PRD maps every comment to a specific code change with WBS task tracking.

## Key References
- PR: https://github.com/c2pa-org/specs-core/pull/2058
- Local branch: `/home/developer/code/specs-core` on `feat/compound-content-provenance`
- Primary file: `docs/modules/specs/partials/Compound-Content/compound-content.adoc`
- CDDL schemas: `partials/schemas/cddl/compound-membership.cddl`, `compound-content.cddl`
- CBOR examples: `partials/examples/cbordiag/compound-membership.cbordiag`, `compound-content.cbordiag`

---

## Comment Inventory

Each comment below is numbered as it appears chronologically in the review. The "RC" column maps to the root cause. The "Task" column maps to the WBS task that addresses it.

| # | Line | lrosenthol Comment (verbatim summary) | RC | Task |
|---|------|---------------------------------------|-----|------|
| 1 | 48 | "If the child asset doesn't exist, then you can't reference its manifest in the `activeManifest` field... You have an unresolvable loop here of dependencies" | RC2 | 1.1.1 |
| 2 | 69 | "This requires the use of cloud-hosted manifest & manifest repositories = not something we want to require." | RC3 | 2.1.1 |
| 3 | 71 | "This is backwards - `componentOf` is parent->child, not child->parent" | RC1 | 1.2.1 |
| 4 | 77 | "See previous comment about not requiring manifest repos or cloud hosting." | RC3 | 2.1.2 |
| 5 | 79 | "This won't work, due to the `activeManifest` field in the ingredient assertion." | RC2 | 1.1.2 |
| 6 | 95 | "Why wouldn't this be via our SoftBinding API?" | RC3 | 2.2.1 |
| 7 | 99 | "We don't like this type of stuff in C2PA assertions" | RC5 | 4.1.1 |
| 8 | 101 | "Is this a free form text field or is there an enum?" | RC5 | 4.1.2 |
| 9 | 103 | "We don't use single strings for claim generators - we use a `claim_generator_info` field. Also, again, plain text fields are bad!" | RC5 | 4.1.3 |
| 10 | 107 | "We don't use IMPORTANT blocks in our spec" | RC4 | 3.1.1 |
| 11 | 136 | "There are well established standards for this - no reason to reinvent the wheel. Check out the original XMP Ingredient & Pantry model on which our current ingredient model is based." | RC5 | 4.2.1 |
| 12 | 178 | "Which will now break item #2" (re-signing children breaks parent's componentOf references) | RC2 | 1.1.3 |
| 13 | 182 | "Why not just do this as an update manifest with containing the new assertion? Why a full sign?" | RC6 | 5.1.1 |
| 14 | 196 | "But what if it wasn't created, but opened? What about when one of these is edited? You can't mandate this particular flow" | RC6 | 5.1.2 |
| 15 | 199 | "That's standard C2PA requirement - why repeat it here?" | RC4 | 3.2.1 |
| 16 | 220 | "This is not correct. `componentOf` is parent->child" | RC1 | 1.2.2 |
| 17 | 231 | "This is guidance and doesn't belong in the core spec" | RC4 | 3.3.1 |
| 18 | 248 | "This all reads like guidance..." | RC4 | 3.3.2 |
| 19 | 279 | "This would go into the Security section - not here." | RC4 | 3.4.1 |
| 20 | 310 | "This would go into the Validation section, not here." | RC4 | 3.4.2 |
| 21 | 316 | "You don't need the actual child asset - since you have the ingredient assertion and its manifest." | RC4 | 3.5.1 |
| 22 | 320 | CODE SUGGESTION: "should attempt" -> "may attempt" | RC3 | 2.3.1 |
| 23 | 320 | "Network access is *ALWAYS OPTIONAL*" | RC3 | 2.3.2 |
| 24 | 324 | CODE SUGGESTION: "cannot be retrieved" -> "is not retrieved" | RC3 | 2.3.3 |
| 25 | 326 | "Again, this is wrong" (componentOf in child->parent direction) | RC1 | 1.2.3 |
| 26 | 332 | "these would go into validation" | RC4 | 3.4.3 |

### Issue-Level Comments

| Author | Date | Summary | Task |
|--------|------|---------|------|
| lrosenthol | Mar 24 | "take a look at the work we've done with PDF, which is a rich compound format" | 0.1.1 |
| dcondrey | Mar 28 | "document specific scenarios where the current ingredient model fails" | 0.1.2 |

---

## Tasks (WBS)

### 0.0 Pre-Implementation Research

Research tasks that must complete before code changes begin. These inform design decisions for P0 items.

- [ ] 0.1 Research existing C2PA mechanisms
  - [ ] 0.1.1 Study PDF object-level manifests and how compound content is handled in the PDF section of the spec. Determine which patterns can be reused for distributed content. (Responds to lrosenthol issue comment, Mar 24)
  - [ ] 0.1.2 Study the SoftBinding API in the C2PA spec. Determine whether soft binding can serve as the child-to-parent discovery mechanism instead of a raw URI field. (Responds to Comment #6, line 95: "Why wouldn't this be via our SoftBinding API?")
  - [ ] 0.1.3 Study the XMP Ingredient & Pantry model referenced by lrosenthol. Determine whether `c2pa.compound.content` should be replaced by or aligned with this existing model. (Responds to Comment #11, line 136: "Check out the original XMP Ingredient & Pantry model")
  - [ ] 0.1.4 Study the `claim_generator_info` field structure in the existing spec. Understand the correct format for referencing claim generators. (Responds to Comment #9, line 103)
  - [ ] 0.1.5 Study Update Manifest constraints. Determine whether an update manifest with a new assertion (without additional ingredients) is viable for child signing. (Responds to Comment #13, line 182)
  - [ ] 0.1.6 Prepare specific failure scenarios where the existing ingredient model is insufficient for distributed content, as requested by dcondrey. (Responds to dcondrey issue comment, Mar 28)

### 1.0 P0: Fix Blocking Architectural Errors

#### 1.1 Resolve Circular Dependency (RC2)

The re-signing workflow creates an unresolvable loop: re-signing a child changes its `activeManifest`, which invalidates the parent's `componentOf` ingredient hash.

- [ ] 1.1.1 Rewrite compound content model (lines 41-55) to remove the assumption that the parent can reference child manifests that don't yet exist at model description time. The model description at line 48 states the parent "Contains one or more `c2pa.ingredient.v3` assertions with a `componentOf` relationship for each child asset" - this is correct for the parent, but the reviewer's point is that the generation ordering must be explicit here, not implied.
  - **Current code (line 48):**
    ```
    - Contains one or more xref:ingredient_assertion[`c2pa.ingredient.v3`] assertions with a `componentOf` relationship for each child asset.
    ```
  - **Action:** Add a forward reference to the generation process section clarifying that children are signed first, then the parent references them. The model description itself is correct (it describes the final state), but needs a note that the ordering is resolved in the generation process.

- [ ] 1.1.2 Remove or rework "Authenticated binding" (line 79) to acknowledge the `activeManifest` invalidation problem.
  - **Current code (line 79):**
    ```
    Authenticated binding (recommended):: After the parent manifest has been created and signed, the claim generator may re-sign each child asset with a new xref:_standard_manifests[standard manifest] that includes a `componentOf` ingredient referencing the parent manifest. This provides a hash-verified, cryptographically authenticated reference from the child to the parent.
    ```
  - **Problem:** Re-signing a child changes its active manifest, breaking the parent's `componentOf` ingredient hash that was computed against the child's previous manifest.
  - **Action:** DECIDED - Remove "Authenticated binding" entirely (D1, Option A). The membership assertion provides discovery; the parent's `componentOf` ingredients provide authentication in the parent-to-child direction. Delete the entire "Authenticated binding (recommended)" definition list entry at line 79. Replace "Binding strength" subsection with a single paragraph explaining that child-to-parent binding is URI-based discovery, while authentication flows through the parent's `componentOf` ingredients.

- [ ] 1.1.3 Rewrite generation process step 4 (line 178) based on the decision from 1.1.2.
  - **Current code (line 178):**
    ```
    . Optionally, re-sign child assets with authenticated parent binding.
    ```
  - **Action:** DECIDED - Remove step 4 entirely. The generation process becomes three steps: (1) determine parent URI, (2) sign children with membership, (3) sign parent with `componentOf` ingredients.

#### 1.2 Fix `componentOf` Directionality (RC1)

`componentOf` is a parent-to-child relationship. The PR incorrectly uses it in the child-to-parent direction in three locations.

- [ ] 1.2.1 Fix line 71 - Bidirectional provenance references NOTE.
  - **Current code (line 71):**
    ```
    NOTE: For an authenticated child-to-parent binding, a new standard manifest with a `componentOf` ingredient referencing the parent manifest may be applied to the child asset after the parent manifest has been created, as described in <<_authenticated_child_to_parent_binding>>.
    ```
  - **Action:** DECIDED - Delete this NOTE entirely. Authenticated binding is removed (D1).

- [ ] 1.2.2 Fix line 220 - Authenticated binding section uses `componentOf` backwards.
  - **Current code (line 220):**
    ```
    - A `c2pa.ingredient.v3` assertion with a `componentOf` relationship, whose `activeManifest` field references the parent manifest. When the parent manifest is external, a `hashed-ext-uri-map` may be used. This is the authenticated back-reference.
    ```
  - **Action:** DECIDED - Delete entire "Authenticated child-to-parent binding" section (lines 211-229) including both `[IMPORTANT]` blocks. Authenticated binding is removed (D1).

- [ ] 1.2.3 Fix line 326 - Validation section references `componentOf` in child manifest.
  - **Current code (line 326):**
    ```
    If the child manifest contains a `componentOf` ingredient that directly references the parent manifest (established via the authenticated binding described in <<_authenticated_child_to_parent_binding>>), the validator shall validate that ingredient, including hash verification, as described in <<_ingredient_assertion_validation>>.
    ```
  - **Action:** DECIDED - Delete this paragraph. Authenticated binding is removed (D1), so no child manifest will contain a `componentOf` ingredient referencing the parent.

### 2.0 P1: Remove Network/Cloud Dependency (RC3)

C2PA validation must work offline. The current design requires cloud-hosted manifest repositories.

#### 2.1 Remove "Required" Network Access

- [ ] 2.1.1 Rewrite line 69 to remove the implication that a URI must be resolvable at validation time.
  - **Current code (line 69):**
    ```
    The child-to-parent direction uses a `c2pa.compound.membership` assertion in the child's manifest. This assertion provides a URI at which the parent manifest can be retrieved. It is not an ingredient assertion and does not provide hash-verified integrity; it is a discovery mechanism.
    ```
  - **Action:** Reframe as: the URI is an optional discovery hint. Validators are not required to resolve it. Emphasize that the child's own manifest is independently valid regardless.

- [ ] 2.1.2 Downgrade "Discovery binding" from required to optional (line 77).
  - **Current code (line 77):**
    ```
    Discovery binding (required):: Every child manifest shall contain a `c2pa.compound.membership` assertion with a `parentManifestURI`. This provides URI-based discovery of the parent manifest. The URI is not hash-verified within the child's claim; a validator shall perform full validation on any manifest retrieved from it before trusting its contents.
    ```
  - **Action:** Change "shall" to "should" or "may" for the validator retrieval requirement. The assertion itself can remain required (it is the new thing this PR adds), but the validator's obligation to resolve the URI must be optional.

#### 2.2 Investigate SoftBinding Alternative

- [ ] 2.2.1 Based on research from 0.1.2, determine whether `parentManifestURI` should be replaced by or supplemented with a soft binding reference (line 95).
  - **Current code (line 95):**
    ```
    `parentManifestURI`:: A URI at which the parent asset's C2PA Manifest Store can be retrieved. This URI should resolve to a resource served with the IANA Media Type `application/c2pa`. The URI may be an HTTPS URL or any other URI scheme that the claim generator expects validators to be able to resolve.
    ```
  - **Action:** DECIDED - Hybrid approach (D2). Keep `parentManifestURI` as the primary discovery field. Add a NOTE explaining the relationship to soft binding: when a child asset has a `c2pa.soft-binding` assertion, validators may also use the Soft Binding Resolution API as an alternative discovery path. Reframe the URI as an optional discovery hint. Add a subsection to the architecture explaining why both mechanisms serve different use cases (soft binding = content-identity recovery when metadata stripped; membership URI = editorial-context discovery for compound works). Ask lrosenthol for clarification on whether he envisioned full replacement or coexistence.

#### 2.3 Apply Direct Code Suggestions (Trivial)

These are lrosenthol's two explicit code suggestions. Mechanically simple.

- [ ] 2.3.1 Apply Comment #22: line 320, change "should attempt" to "may attempt".
  - **Current code (line 320):**
    ```
    When a validator encounters a child manifest that contains a `c2pa.compound.membership` assertion, the validator may attempt to retrieve the parent manifest from the `parentManifestURI`.
    ```
  - **Note:** Already "may" in our local working copy from initial analysis; confirm this survives the full rewrite.

- [ ] 2.3.2 Ensure all validation language is consistent with "network access is ALWAYS OPTIONAL" (Comment #23). Audit every "shall" and "should" in the validation section that implies network retrieval.

- [ ] 2.3.3 Apply Comment #24: line 324, change "cannot be retrieved" to "is not retrieved".
  - **Current code (line 324):**
    ```
    If the parent manifest cannot be retrieved, the validator shall report a `compound.membership.parentUnavailable` informational code.
    ```
  - **Change to:**
    ```
    If the parent manifest is not retrieved, the validator shall report a `compound.membership.parentUnavailable` informational code.
    ```

### 3.0 P2: Fix Spec Structure (RC4)

The C2PA spec has established sections for security, validation, and guidance. This PR puts all three inline. Move them to the correct locations.

#### 3.1 Remove Non-Standard Formatting

- [ ] 3.1.1 Remove all `[IMPORTANT]` blocks (Comment #10, lines 107-110 and lines 226-229).
  - **Current code (lines 107-110):**
    ```
    [IMPORTANT]
    ====
    The `parentManifestURI` may become stale if the parent manifest is moved or removed. Claim generators should use stable, long-lived URIs (such as those served from a manifest repository) to minimize the risk of broken references.
    ====
    ```
  - **Current code (lines 226-229):**
    ```
    [IMPORTANT]
    ====
    If a claim generator elects not to re-sign child assets, the child-to-parent reference remains limited to the unauthenticated URI in the `c2pa.compound.membership` assertion. Claim generators should re-sign child assets whenever practical, particularly when the compound content will be distributed through channels where child assets may be extracted from their parent context.
    ====
    ```
  - **Action:** Convert to `NOTE:` blocks or integrate the content into normative prose. If the content is pure guidance, it may be removed entirely (see 3.3).

#### 3.2 Remove Redundant Requirements

- [ ] 3.2.1 Remove line 199 which restates standard C2PA validation requirements (Comment #15).
  - **Current code (line 199):**
    ```
    When adding child assets as `componentOf` ingredients, the claim generator shall validate each child asset's manifest and record the results in the `validationResults` field of the ingredient assertion, as described in <<_ingredient_assertion_validation>>.
    ```
  - **Action:** Delete this paragraph. It restates an existing requirement. A cross-reference in the generation overview is sufficient.

#### 3.3 Remove or Relocate Guidance Content

- [ ] 3.3.1 Remove "Manifest size considerations" section (lines 231-241) from core spec (Comment #17).
  - **Current code (lines 231-241):** Entire subsection with 3 bullet points of implementation guidance about external manifests, `hashed-ext-uri-map`, and decorative assets.
  - **Action:** Delete from the core spec section. If this guidance is valuable, it belongs in an informational annex or implementer's guide, not the normative spec.

- [ ] 3.3.2 Remove "Compound Content Updates" section (lines 244-276) from core spec (Comment #18).
  - **Current code (lines 244-276):** Entire section covering replacing/adding/removing children and editing the parent.
  - **Action:** Delete from the core spec section. The update process follows standard C2PA manifest update patterns (parentOf ingredients). Restating them here for the compound content case is guidance, not new normative requirements.

#### 3.4 Relocate Security and Validation Content

- [ ] 3.4.1 Move "Security Considerations" (lines 279-307) to the existing Security section of the spec (Comment #19).
  - **Current code (lines 279-307):** Three threat subsections - spoofed parent manifest, stale/removed parent manifest, manifest inflation attack.
  - **Action:** Extract this content and prepare it as additions to the existing Security Considerations section of `C2PA_Specification.adoc`. The content itself is valid but lives in the wrong place.

- [ ] 3.4.2 Move "Validation" (lines 310-347) to the existing Validation section of the spec (Comment #20).
  - **Current code (lines 310-347):** Parent manifest validation, child manifest validation in isolation, status codes table.
  - **Action:** Extract and prepare as additions to the existing Validation section. This includes the status codes table (Comment #26).

- [ ] 3.4.3 Move status codes table (lines 332-347) to the validation section (Comment #26).
  - **Note:** This is part of task 3.4.2 - the status codes move together with the validation content.

#### 3.5 Fix Incorrect Validation Assumptions

- [ ] 3.5.1 Fix line 316 NOTE about child asset availability (Comment #21).
  - **Current code (line 316):**
    ```
    NOTE: Not all child assets may be available at validation time, particularly for distributed content. A validator should report the absence of unretrievable child manifests as an informational status rather than a validation failure.
    ```
  - **lrosenthol's point:** "You don't need the actual child asset - since you have the ingredient assertion and its manifest." The parent manifest contains the child's ingredient assertion with its manifest data. The actual child binary is not needed for validating the parent's provenance chain.
  - **Action:** Rewrite to clarify that the parent's ingredient assertions are self-contained. The child asset binary may be unavailable, but the ingredient assertion (including the child's manifest) is already in the parent's manifest store.

### 4.0 P2: Fix Non-Conforming Fields (RC5)

#### 4.1 Strip Membership Assertion Fields

- [ ] 4.1.1 Remove `parentTitle` field from `c2pa.compound.membership` (Comment #7, line 99).
  - **Current code (line 99):**
    ```
    `parentTitle`:: A human-readable title for the parent compound work, to assist validators in presenting context when the parent manifest cannot be retrieved.
    ```
  - **Current CDDL (compound-membership.cddl line 6):**
    ```
    ? "parentTitle": tstr .size (1..max-tstr-length),
    ```
  - **Current CBOR example (compound-membership.cbordiag line 3):**
    ```
    "parentTitle": "Climate Report: Arctic Ice Coverage 2026",
    ```
  - **Action:** Remove from spec text, CDDL schema, and CBOR example.

- [ ] 4.1.2 Decide on `role` field: enum or remove (Comment #8, line 101).
  - **Current code (line 101):**
    ```
    `role`:: A string describing the role of this child asset within the compound work, such as `"hero-image"`, `"body-text"`, `"background-audio"`, or `"inline-video"`. The value of this field is not constrained by this specification but should be human-readable and meaningful in the context of the compound work.
    ```
  - **Current CDDL (compound-membership.cddl line 7):**
    ```
    ? "role": tstr .size (1..max-tstr-length),
    ```
  - **Action:** DECIDED - Remove `role` from membership assertion (D4, Option B). The role is editorial metadata about the parent's composition. It belongs in the parent's `c2pa.compound.content` assertion (which is retained per D3), not in the child's self-description. Functionality lost: a validator encountering a child in isolation without network access cannot display the child's role. This is a minor UX loss that trades against spec cleanliness and lrosenthol's principle against plain-text metadata in assertions.
  - **Files to change:** Remove `role` from compound-membership.cddl (line 7), compound-membership.cbordiag (line 4), and the spec text at line 101. Retain `role` in the `c2pa.compound.content` assertion's `component-map` (compound-content.cddl line 11).

- [ ] 4.1.3 Remove `parentClaimGenerator` field (Comment #9, line 103).
  - **Current code (line 103):**
    ```
    `parentClaimGenerator`:: A string identifying the claim generator of the parent manifest, to assist validators in determining provenance context.
    ```
  - **Current CDDL (compound-membership.cddl line 8):**
    ```
    ? "parentClaimGenerator": tstr .size (1..max-tstr-length),
    ```
  - **Current CBOR example (compound-membership.cbordiag line 5):**
    ```
    "parentClaimGenerator": "ExampleNews/2.1"
    ```
  - **Action:** Remove from spec text, CDDL schema, and CBOR example. C2PA uses `claim_generator_info` (a structured object), not plain strings. And per Comment #7's principle, metadata about the parent doesn't belong in the child's assertion.

#### 4.2 Rework or Remove Compound Content Assertion

- [ ] 4.2.1 Based on research from 0.1.3, determine whether `c2pa.compound.content` should be replaced by the XMP Ingredient & Pantry model (Comment #11, line 136).
  - **Current code (lines 129-166):** Entire "Compound Content Assertion (Optional)" section with `components` array, `ingredientRef`, `role`, `displayOrder`, `required` fields.
  - **Action:** DECIDED - Retain and reframe as XMP Ingredients heritage (D3, Option C). Research confirms `xmpMM:Ingredients` and `xmpMM:Pantry` are permitted in `c2pa.metadata` assertions (valid_metadata_fields.yml lines 22-23) but carry no C2PA-specific semantic or validation logic. The XMP fields lack `ingredientRef` linking, `displayOrder`, and `required` semantics needed for compound content. The `c2pa.compound.content` assertion is therefore justified as a necessary extension, but must be reframed:
    1. Add explicit reference to XMP Ingredients heritage in the description: "This assertion extends the structural metadata tradition of the XMP Ingredients model for the C2PA manifest architecture."
    2. Explain why `c2pa.metadata` with `xmpMM:Ingredients` is insufficient (no hashed-uri linking to C2PA ingredient assertions, no display ordering, no required/optional semantics).
    3. Consider whether `role` should use the same vocabulary conventions as XMP ingredient roles.
    4. Keep the assertion optional, as currently specified.

### 5.0 P3: Fix Overly Prescriptive Generation Process (RC6)

#### 5.1 Relax Action Requirements

- [ ] 5.1.1 Investigate update manifest viability for child signing (Comment #13, line 182).
  - **Current code (lines 182-186):**
    ```
    Each child asset shall be signed with its own C2PA Manifest, following the standard process for the child asset's format as described in <<embedding_annex>>. The child asset's manifest shall include:

    - A hard binding assertion appropriate for the asset's format.
    - A `c2pa.compound.membership` assertion containing the predetermined `parentManifestURI` and, optionally, the child's `role` within the compound work.
    - A `c2pa.actions` assertion with a `c2pa.created` action (or other appropriate action) describing the provenance of the child asset.
    ```
  - **lrosenthol's point:** Why require a full new manifest for the child? If the child already has a manifest, an update manifest with the membership assertion could suffice.
  - **Action:** DECIDED - Present two paths (D5). Research confirms Update Manifests can carry `c2pa.compound.membership` (it is not on the prohibited list: not a hard binding, not a thumbnail, not a multi-asset hash, not an ingredient). The `parentOf` ingredient in the Update Manifest preserves the child's provenance chain.
    - **Path 1 (Update Manifest):** For already-signed children where content is unchanged. Update Manifest with `parentOf` ingredient referencing current active manifest + `c2pa.compound.membership` assertion + `c2pa.edited.metadata` action.
    - **Path 2 (Standard Manifest):** For first-time signing or when content changes accompany membership. Full manifest with hard binding + membership assertion + appropriate actions.
    - Rewrite lines 180-188 to present both paths. Remove the current text's assumption that children are always being signed for the first time.
    - Also remove the two notes at lines 81 and 224 that say "Update Manifests are not suitable" - those were written for the authenticated binding path (which required a `componentOf` ingredient). With authenticated binding removed (D1), the constraint no longer applies.

- [ ] 5.1.2 Remove mandated action sequence (Comment #14, line 196).
  - **Current code (line 196):**
    ```
    - A `c2pa.actions` assertion with a `c2pa.created` action and a `c2pa.placed` action for each child ingredient, as required by the xref:ingredient_assertion[ingredient assertion] specification.
    ```
  - **lrosenthol's point:** "What if it wasn't created, but opened? What about when one of these is edited? You can't mandate this particular flow."
  - **Action:** Replace `c2pa.created` with "the appropriate action for the workflow" (e.g., `c2pa.created`, `c2pa.opened`, `c2pa.edited`). The `c2pa.placed` requirement for `componentOf` ingredients is already specified elsewhere and does not need restating (see 3.2.1).

---

## File Change Summary

After all tasks are complete, the following files will be modified:

| File | Changes |
|------|---------|
| `compound-content.adoc` | Major rewrite: remove authenticated binding section (lines 73-81, 211-229), remove guidance sections (lines 231-276), extract security/validation to separate includes, strip membership fields, relax generation process, add soft binding relationship note, add XMP heritage framing for content assertion, present Update Manifest path for child signing |
| `compound-membership.cddl` | Remove `parentTitle`, `role`, `parentClaimGenerator` fields. Keep `parentManifestURI` + extensibility map only. |
| `compound-membership.cbordiag` | Simplify to `parentManifestURI` only. |
| `compound-content.cddl` | Retain. Add XMP heritage comment. No structural changes needed. |
| `compound-content.cbordiag` | Retain. No changes needed. |
| `C2PA_Specification.adoc` | Add includes for security additions in Security section and validation additions in Validation section. |
| `CompoundContent.puml` | Remove authenticated binding arrow. Simplify to show URI-based discovery only. |
| Security section partial (new or existing) | Receive relocated security content from lines 279-307. |
| Validation section partial (new or existing) | Receive relocated validation content from lines 310-347, including status codes table. |

---

## Design Decisions - Research Findings and Recommendations

### D1: Should authenticated child-to-parent binding be retained?

**Context:** The "Authenticated binding" mechanism (lines 79, 211-229) proposes re-signing child assets with a `componentOf` ingredient referencing the parent manifest. Three problems: (1) `componentOf` is parent-to-child, not child-to-parent, (2) re-signing children changes their `activeManifest`, invalidating the parent's `componentOf` ingredient hashes, (3) the circular dependency has no clean resolution.

**Analysis of benefit:** Authenticated binding would provide hash-verified, cryptographic proof that a child belongs to a specific parent. Without it, the child-to-parent link is URI-only (unauthenticated). The question is whether this authentication adds value beyond what the parent-to-child direction already provides.

The parent manifest already contains hash-verified `componentOf` ingredients for every child. If a validator retrieves the parent (via the membership URI), it can verify the parent's claim signature, then verify that this child's manifest hash matches the `componentOf` ingredient. The authentication chain is: child URI -> parent manifest -> parent's `componentOf` ingredient -> hash match against child. The parent-to-child direction authenticates the relationship. Duplicating that authentication in the reverse direction adds implementation complexity without adding trust: if the parent is authentic and contains the child as an ingredient, the relationship is proven.

**Recommendation: Remove entirely (Option A).** The membership assertion provides discovery. The parent's `componentOf` ingredients provide authentication. Bidirectional authentication is redundant. This eliminates all three blocking errors (RC1 directionality + RC2 circular dependency) in one stroke.

**Commercial angle:** If a future use case demands cryptographic child-to-parent proof without retrieving the parent (an offline verifier encountering just the child), that could be explored as Encypher proprietary technology. It is not a spec-level requirement.

**Blocking tasks:** 1.1.2, 1.1.3, 1.2.1, 1.2.2, 1.2.3

---

### D2: Should `parentManifestURI` use the SoftBinding API?

**Research findings:** The Soft Binding API (`c2pa.soft-binding` assertion + Soft Binding Resolution API) is a content-identity-based discovery mechanism. It works by:
1. Embedding a watermark or computing a fingerprint of the asset's digital content
2. Recording the algorithm + value in a `c2pa.soft-binding` assertion
3. At validation time, extracting the watermark/fingerprint from the content
4. Querying a Soft Binding Resolution API endpoint (registered in the algorithm list) with the extracted value
5. Receiving manifest identifiers that resolve to full manifests in a repository

**Key findings from the spec (SoftBinding.adoc, softbinding-resolution-api.adoc):**

- Soft binding is **content-identity matching** ("this content matches that content"), not **relationship declaration** ("this content is part of that compound work"). These are semantically different.
- The `url` field in soft binding was deprecated and "never used" - replaced by the asset reference assertion. The spec explicitly moved away from putting URI references in soft binding.
- Soft binding requires an algorithm-based extraction from the asset's digital content. Not all child assets will have watermarks. Text content, structured data, and many image formats in distributed workflows will lack soft bindings.
- The resolution API routes through an external registry (the algorithm list) and separately-operated API endpoints. The `parentManifestURI` is a direct reference from a publisher who knows the parent manifest location at signing time.
- `bindingMetadata` allows custom fields but is explicitly "not used for validation" (SoftBinding.adoc line 42).

**What lrosenthol likely means:** Rosenthal may be suggesting that the child-to-parent discovery should work through the soft binding infrastructure (watermark the child, store the parent manifest in a repository, let the resolution API connect them) rather than inventing a new assertion with a raw URI. This would leverage existing infrastructure rather than adding new spec surface area.

**The problem with full replacement:** Soft binding solves a different problem (recover a manifest when metadata is stripped). It requires watermarking infrastructure that most distributed content workflows lack. A news article's hero image may not be watermarked. The compound membership assertion addresses a structural relationship (editorial context), not content identity.

**Recommended approach: Hybrid.** Keep `parentManifestURI` in the membership assertion but integrate with soft binding where available:
1. The `parentManifestURI` remains the primary discovery field (direct, works offline if cached, no watermark dependency).
2. Add a note that when the child asset has a `c2pa.soft-binding` assertion, validators may also use the Soft Binding Resolution API to discover the parent manifest.
3. Reframe the URI as optional discovery hint rather than a required network call. Align with "network access is ALWAYS OPTIONAL."
4. Consider whether the membership assertion should reference the soft binding resolution path as an alternative discovery mechanism.

**Important:** We should ask lrosenthol directly what he envisioned. The comment "Why wouldn't this be via our SoftBinding API?" could mean (a) replace the URI entirely with soft binding, (b) route through soft binding infrastructure, or (c) acknowledge soft binding as the existing discovery mechanism and explain why a new one is needed. Option (c) is safest: add a subsection explaining the relationship between membership discovery and soft binding discovery, and why both serve different use cases.

**Blocking tasks:** 2.2.1

---

### D3: Should `c2pa.compound.content` assertion be retained?

**Research findings on XMP Ingredient & Pantry:**

The "XMP Ingredient & Pantry model" that lrosenthol references is the pre-C2PA Adobe mechanism for compound content metadata. Key findings:
- `xmpMM:Ingredients` and `xmpMM:Pantry` appear in the C2PA spec only as permitted XMP metadata fields (in `valid_metadata_fields.yml` lines 22-23), listed under the XMP Media Management namespace.
- C2PA's own ingredient model (`c2pa.ingredient.v3`) replaced the XMP Pantry approach with JUMBF/CBOR-based manifest stores.
- The C2PA spec has no normative logic built around `xmpMM:Ingredients` or `xmpMM:Pantry` - they are pass-through metadata.

**What lrosenthol likely means:** The XMP Ingredient & Pantry model provided structural metadata about how ingredients relate to a compound document (roles, ordering, relationships) without inventing a parallel data structure. lrosenthol is saying: the C2PA ingredient model already descends from this pattern, and the `c2pa.compound.content` assertion reinvents structural metadata that could be expressed through extensions to the existing ingredient model or through the existing `c2pa.metadata` assertion carrying XMP fields.

**Analysis of the current `c2pa.compound.content` design:**

The assertion adds `role`, `displayOrder`, and `required` fields per component, linking to ingredients via `ingredientRef`. The research confirms that adding these fields directly to `ingredient-map-v3` was considered and rejected (it would pollute all ingredient uses). The `c2pa.compound.content` assertion is a pointer layer over ingredients.

**Recommended approach: Retain but reframe as leveraging the ingredient model (Option C).**

The user wants both parts (membership + content) based on XMP alignment. The path forward:
1. Keep the `c2pa.compound.content` assertion as an optional parent-side structural overlay.
2. In the description, explicitly reference the XMP Ingredient & Pantry heritage: "This assertion provides structural metadata in the tradition of the XMP Ingredients model, adapted for the C2PA manifest architecture."
3. Consider whether the `c2pa.metadata` assertion (which already permits `xmpMM:Ingredients` and `xmpMM:Pantry` fields) could carry this data instead. If the XMP fields are sufficient, use them via `c2pa.metadata` rather than inventing `c2pa.compound.content`.
4. If `c2pa.metadata` with XMP fields is insufficient (lacks `displayOrder`, `required`, or `ingredientRef` linking), justify the new assertion as a necessary extension.

**Open question:** Does the `xmpMM:Ingredients` XMP field carry enough structure (role, order, required status) to serve the compound content use case? If yes, we can drop `c2pa.compound.content` and use `c2pa.metadata` with standard XMP fields. If no, the new assertion is justified but should be framed as extending the XMP Ingredients heritage.

**Blocking tasks:** 4.2.1

---

### D4: Should `role` be enumerated or removed from membership?

**What we lose by removing `role` from the membership assertion:**

The `role` field in `c2pa.compound.membership` tells a validator encountering a child in isolation what editorial function it served (e.g., "hero-image", "body-text"). Without it, a validator seeing a child with a membership assertion knows it belongs to a parent but not what role it played.

**Practical impact assessment:**
- The validator can still retrieve the parent manifest via `parentManifestURI` and find the child's role there (in the optional `c2pa.compound.content` assertion or by inspecting the `componentOf` ingredient).
- If the parent manifest is unavailable, the role information is lost. But the child's own manifest still carries its own provenance (who signed it, when, what format). The role is editorial context, not provenance data.
- The role is duplicated: it appears in both the child's membership assertion and the parent's content assertion. Removing it from the child eliminates this duplication.

**Recommendation: Remove from the C2PA spec assertion. Graduate to Encypher commercial layer.**

The role is editorial metadata about the parent's composition, not a property of the child's provenance. It belongs in the parent's structural description. The child's job is to say "I belong to this parent" (via URI), not to describe the parent's editorial structure. This aligns with lrosenthol's principle that C2PA assertions should not carry plain-text metadata fields (Comments #7, #9).

**Functionality lost from the standard:** A validator encountering a child in isolation without network access loses the ability to display "this image was the hero-image of [parent title]." This is a minor UX loss that trades against spec cleanliness. The child's own provenance (signature, creator, format) is unaffected.

**Commercial opportunity:** The C2PA spec supports entity-specific namespaced assertions (Assertions.adoc lines 25-26) and extensibility maps (`* tstr => any` in CDDL). Encypher can offer a `com.encypher.compound.membership` custom assertion (or namespaced extension fields within the standard assertion) that carries the rich editorial metadata stripped from the spec:
- `role` with Encypher-defined enumeration
- `parentTitle` for offline context display
- `parentClaimGenerator` using proper `claim_generator_info` structure
- Future fields: `siblingCount`, `publicationContext`, `editorialWeight`, etc.

This creates a clean two-tier model:
- **Standard tier** (C2PA spec, open): `c2pa.compound.membership` with `parentManifestURI` only. Minimal discovery.
- **Commercial tier** (Encypher, proprietary): `com.encypher.compound.membership` with rich editorial context. Enterprise publishers get role display, parent context, and sibling discovery even when the parent manifest is unavailable.

Generic C2PA validators process the standard assertion. Encypher-aware validators get the full editorial picture. The fields removed from the PR are not lost; they graduate to a differentiated commercial product.

**Follow-up task:** Create a separate internal PRD for `com.encypher.compound.membership` commercial assertion design.

**Blocking tasks:** 4.1.2

---

### D5: Can update manifests be used for adding membership to existing children?

**Research findings from the spec (Manifests.adoc lines 150-176, Validation.adoc lines 492-495):**

Update Manifest constraints:
- SHALL contain exactly one `c2pa.ingredient.v3` with `parentOf` relationship
- SHALL NOT contain hard binding assertions (`c2pa.hash.data`, etc.)
- SHALL NOT contain `c2pa.hash.multi-asset` or `c2pa.thumbnail`
- MAY contain `c2pa.actions` with only: `c2pa.edited.metadata`, `c2pa.opened`, `c2pa.published`, `c2pa.redacted`
- MAY contain time-stamp or certificate status assertions
- Validation enforces `manifest.update.wrongParents` for any deviation from one-`parentOf`-ingredient rule

**The key question:** Can a `c2pa.compound.membership` assertion be added via an Update Manifest?

The spec prohibits specific assertion types in Update Manifests (hard bindings, multi-asset hash, thumbnails). `c2pa.compound.membership` is NOT on the prohibited list. The Update Manifest already has the required `parentOf` ingredient (pointing to the child's previous active manifest). The question is whether adding a non-prohibited, non-ingredient assertion alongside the single `parentOf` ingredient is valid.

**Assessment: It should work, but with caveats.**

1. `c2pa.compound.membership` is not an ingredient assertion, not a hard binding, not a thumbnail, and not a multi-asset hash. It falls outside all explicit prohibitions.
2. The Update Manifest's `parentOf` ingredient preserves the child's provenance chain.
3. The actions whitelist is restrictive: only `c2pa.edited.metadata`, `c2pa.opened`, `c2pa.published`, `c2pa.redacted`. Adding compound membership is arguably `c2pa.edited.metadata` (adding metadata about the child's compound context without changing content).
4. Our own compound-content.adoc (lines 81, 224) says Update Manifests "are not suitable" - but this was written in the context of the authenticated binding path (which requires a `componentOf` ingredient in addition to `parentOf`). For discovery-only membership (just the assertion, no additional ingredient), the constraint does not apply.

**Recommended approach: Two options, present both.**

**Option A: Update Manifest (preferred for already-signed children).**
When a child asset already has a C2PA manifest and the claim generator wants to declare membership without modifying the content:
- Create an Update Manifest with the required `parentOf` ingredient referencing the child's current active manifest
- Add the `c2pa.compound.membership` assertion
- Add a `c2pa.edited.metadata` action describing the addition
- No hard binding needed (content unchanged)
- Lighter weight, preserves existing provenance chain cleanly

**Option B: New Standard Manifest (for first-time signing or content modification).**
When the child asset is being signed for the first time, or when content changes accompany the membership declaration:
- Full standard manifest with hard binding, membership assertion, and appropriate actions
- Required when no prior manifest exists

**The spec text should present both paths** and let the claim generator choose based on workflow. This directly addresses lrosenthol's Comment #13 ("Why not just do this as an update manifest?") while acknowledging that first-time signing requires a standard manifest.

**Blocking tasks:** 5.1.1

---

## Decision Summary

| ID | Decision | Resolution |
|----|----------|-----------|
| D1 | Authenticated child-to-parent binding | **REMOVE.** Parent's `componentOf` provides authentication. Membership URI provides discovery. Bidirectional auth is redundant and broken. |
| D2 | SoftBinding API for parentManifestURI | **HYBRID.** Keep URI, add note about soft binding as alternative discovery. Ask lrosenthol for clarification on his intent. Frame why both mechanisms serve different use cases. |
| D3 | `c2pa.compound.content` assertion | **RETAIN AND REFRAME** as XMP Ingredients heritage. Investigate whether `c2pa.metadata` with `xmpMM:Ingredients`/`xmpMM:Pantry` fields is sufficient. If not, justify the new assertion. |
| D4 | `role` in membership assertion | **REMOVE from spec. Graduate to commercial layer.** `role`, `parentTitle`, `parentClaimGenerator` become `com.encypher.compound.membership` proprietary assertion. Clean two-tier model: standard discovery (open) + rich editorial context (commercial). |
| D5 | Update manifests for membership | **YES, present as primary option** for already-signed children. New Standard Manifest for first-time signing. Two-path approach addresses Comment #13 directly. |

## Success Criteria

- All 26 inline comments addressed (resolved or explicitly responded to with rationale)
- No `componentOf` used in child-to-parent direction
- No network access required for validation
- Security content in Security section, validation content in Validation section
- No `[IMPORTANT]` blocks
- No redundant restatement of existing C2PA requirements
- CDDL schemas syntactically valid
- Metanorma build succeeds
- PR description updated to reflect revised scope

## Post-Implementation Review (Rosenthal-Style)

A simulated review using lrosenthol's editorial standards identified 5 BLOCKING and 6 SHOULD-FIX issues. All resolved:

### BLOCKING fixes applied
- B1: Added optional `parentManifestHash` (`$hashed-uri-map`) to membership assertion. Hash-verified child-to-parent reference via Update Manifest upgrade step.
- B2: Fixed heading levels in CompoundContentValidation.adoc (changed `====` to `###` to match Validation.adoc's Markdown-style convention).
- B3: Removed normative "shall" statements from CompoundContentThreats.adoc (Threats section convention: zero shall).
- B4: Added all 6 status codes to consolidated success/informational/failure tables in Validation.adoc.
- B5: Added assertion validation clauses for `c2pa.compound.membership` and `c2pa.compound.content` to Specific Assertion Validation list in Validation.adoc.

### SHOULD-FIX fixes applied
- SF6-SF11: Normative language consistency, cross-reference accuracy, network-optional phrasing, validation flow alignment.

### Reusable review skill
Created `/c2pa-spec-review` skill at `~/.claude/skills/c2pa-spec-review/SKILL.md` for future C2PA spec reviews.

## Completion Notes

All 26 inline comments addressed. All 5 design decisions implemented. Changes are local and uncommitted on `feat/compound-content-provenance` in specs-core. No commits made to public branch per user instruction. Next step: human review of changes, then commit and push.
