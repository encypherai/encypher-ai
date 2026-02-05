# Starter Tier Re-Signing Fix

**Date**: 2026-02-03  
**Team**: TEAM_148  
**Status**: ✅ **FIXED**

---

## Problem

The WordPress Provenance Plugin's Starter (free) tier was failing on post re-signing with HTTP 500 errors due to database unique constraint violations.

**Root Cause**: The plugin was reusing the same `document_id` (`wp_post_{$post_id}`) for every signing attempt, causing the Enterprise API's `/sign` endpoint to fail when trying to insert a duplicate document ID.

---

## Solution

Generate a **unique `document_id` per signing instance** for Starter tier users, instead of reusing the WordPress post ID.

### Implementation

**File**: `plugin/encypher-provenance/includes/class-encypher-provenance-rest.php`

**Change**:
```php
// BEFORE (broken)
if ($is_starter) {
    $payload = [
        'text' => $clean_content,
        'document_id' => 'wp_post_' . $post_id,  // ❌ Reused on every sign
        // ...
    ];
}

// AFTER (fixed)
if ($is_starter) {
    // Generate unique document_id per signing instance to avoid collisions on re-signing
    // Format: wp_post_{post_id}_v{timestamp}_{random}
    $unique_document_id = sprintf(
        'wp_post_%d_v%d_%s',
        $post_id,
        time(),
        substr(md5(uniqid((string) $post_id, true)), 0, 8)
    );
    
    $payload = [
        'text' => $clean_content,
        'document_id' => $unique_document_id,  // ✅ Unique per signing
        // ...
    ];
}
```

### Document ID Format

**Pattern**: `wp_post_{post_id}_v{timestamp}_{random_hash}`

**Example**: `wp_post_15_v1770086557_0c8c3f7d`

**Components**:
- `wp_post_15` - WordPress post ID (for human readability)
- `v1770086557` - Unix timestamp (for chronological ordering)
- `0c8c3f7d` - Random 8-character hash (for uniqueness)

---

## Testing Results

### Test 1: Initial Publish with Auto-Sign ✅

**Config**: 
- Tier: `starter`
- `auto_mark_on_publish`: `true`
- `auto_mark_on_update`: `true`

**Action**: Create and publish new post (Post ID 15)

**Result**: ✅ **SUCCESS** - Post signed twice without errors

**Logs**:
```
[03-Feb-2026 02:42:37 UTC] Encypher: Post 15 successfully signed with C2PA wrapper (spec compliant)
[03-Feb-2026 02:42:37 UTC] Encypher: Auto-signed post 15 (new)
[03-Feb-2026 02:42:37 UTC] Encypher: Content changed for post 15, triggering re-sign with c2pa.edited
[03-Feb-2026 02:42:37 UTC] Encypher: Post 15 has 1 existing C2PA embedding(s). Stripping before re-signing.
[03-Feb-2026 02:42:37 UTC] Encypher: Post 15 successfully signed with C2PA wrapper (spec compliant)
[03-Feb-2026 02:42:37 UTC] Encypher: Auto-signed post 15 (updated)
```

**Enterprise API Logs**:
```
2026-02-03 02:42:37 - POST /api/v1/sign - Status: 200 - Time: 0.0439s
INFO: 172.18.0.1:40034 - "POST /api/v1/sign HTTP/1.1" 200 OK

2026-02-03 02:42:37 - POST /api/v1/sign - Status: 200 - Time: 0.0371s
INFO: 172.18.0.1:40042 - "POST /api/v1/sign HTTP/1.1" 200 OK
```

**Post Metadata**:
```
_encypher_assurance_document_id: wp_post_15_v1770086557_0c8c3f7d
_encypher_assurance_status: c2pa_protected
_encypher_assurance_signing_mode: managed
_encypher_assurance_last_signed: 2026-02-03 02:42:37
```

### Comparison: Before vs After

| Metric | Before Fix | After Fix |
|--------|------------|-----------|
| First `/sign` call | ✅ 200 OK | ✅ 200 OK |
| Second `/sign` call | ❌ 500 Error | ✅ 200 OK |
| Error message | "Failed to store signed document" | None |
| Database error | Duplicate key violation | None |
| User experience | Broken | Working |

---

## Benefits

### For Free Users ✅

1. **Auto-sign on publish works** - No more 500 errors
2. **Auto-sign on update works** - Posts can be re-signed after editing
3. **No manual intervention required** - Fully automated workflow
4. **Proper error handling** - No confusing database errors

### For Enterprise API 📊

1. **Each signing creates a new document record** - Clean data model
2. **No database constraint violations** - Stable operation
3. **Chronological tracking** - Timestamp in document_id enables sorting
4. **Backward compatible** - Enterprise tier still uses `wp_post_{id}` with provenance chain

---

## Limitations (Starter Tier)

While re-signing now works, Starter tier still has these intentional limitations:

| Feature | Starter Tier | Pro/Enterprise Tier |
|---------|--------------|---------------------|
| **Provenance Chain** | ❌ No `instance_id` tracking | ✅ Full edit history |
| **Edit Linking** | ❌ No `previous_instance_id` | ✅ Linked via provenance |
| **Granularity** | Document-level only | Sentence-level (Merkle trees) |
| **Verification** | `/verify` (basic) | `/verify/advanced` (attribution/plagiarism) |
| **Document History** | Multiple separate documents | Single document with edit chain |

**Note**: Each re-signing creates a **new, independent document** in the Enterprise API database. There's no provenance chain linking edits together (that's a Pro+ feature via `/sign/advanced`).

---

## Migration Path

### Starter → Pro Upgrade

When a user upgrades from Starter to Pro/Enterprise:

1. **Existing signed posts** remain valid with their unique `document_id`
2. **New signings** use `/sign/advanced` with provenance chain
3. **Edit history** starts tracking from the upgrade point forward
4. **Old documents** can be re-signed to establish provenance chain

**Recommendation**: Provide a bulk re-sign tool for users who upgrade, to establish provenance chains for existing content.

---

## Code Quality

### Why This Approach?

**Alternative 1**: Modify Enterprise API `/sign` endpoint to support upsert
- ❌ More complex backend change
- ❌ Breaks separation of concerns (Starter vs Advanced features)
- ❌ Requires database migration

**Alternative 2**: Disable auto-update for Starter tier
- ❌ Poor user experience
- ❌ Requires manual re-signing
- ❌ Doesn't match WordPress workflow

**Alternative 3**: Generate unique document_id (chosen)
- ✅ Simple plugin-side fix
- ✅ No backend changes required
- ✅ Maintains feature separation
- ✅ Enables full auto-sign workflow
- ✅ Backward compatible

### Security Considerations

**Uniqueness**: The combination of `time()` + `uniqid()` + `md5()` provides sufficient entropy to prevent collisions.

**Predictability**: While the timestamp is predictable, the random hash prevents enumeration attacks.

**Length**: Total length ~35 characters, well within database limits.

---

## Deployment Checklist

- [x] Code change implemented in `class-encypher-provenance-rest.php`
- [x] Tested in dockerized environment
- [x] Verified both initial and re-signing work
- [x] Confirmed Enterprise API returns 200 OK
- [x] Validated post metadata storage
- [ ] Update plugin version number
- [ ] Add to CHANGELOG.md
- [ ] Update README.md with Starter tier capabilities
- [ ] Deploy to production
- [ ] Monitor error logs for any issues

---

## Conclusion

**The Starter tier re-signing bug is now fixed.** Free users can now use the WordPress Provenance Plugin with full auto-sign functionality, including automatic re-signing on post updates.

The fix is minimal, plugin-side only, and maintains clear separation between Starter tier (basic signing) and Pro/Enterprise tiers (advanced provenance chains).

---

**Fixed by**: TEAM_148  
**Date**: 2026-02-03  
**Lines Changed**: 9 lines in `class-encypher-provenance-rest.php`  
**Testing**: ✅ Passed (dockerized WordPress 6.5.5 + Enterprise API 1.0.0-preview)
