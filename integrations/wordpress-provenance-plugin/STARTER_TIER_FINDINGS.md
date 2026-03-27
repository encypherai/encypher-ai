# WordPress Plugin - Starter (Free) Tier Functionality Assessment

**Date**: 2026-02-03
**Team**: TEAM_148
**Status**: ⚠️ **CRITICAL BUG IDENTIFIED**

---

## Executive Summary

The WordPress Provenance Plugin has **limited functionality for Starter (free) tier users** due to a critical bug in the Enterprise API's `/sign` endpoint. While the plugin correctly uses tier-appropriate endpoints, the basic `/sign` endpoint **fails on document re-signing**, making it unsuitable for WordPress's auto-update workflow.

---

## Starter Tier Feature Matrix

### ✅ Working Features

| Feature | Status | Details |
|---------|--------|---------|
| **Initial Signing** | ✅ Working | First-time signing of published posts succeeds |
| **C2PA Compliance** | ✅ Working | Embeds C2PA-compliant wrappers in content |
| **Document-Level Signing** | ✅ Working | Uses `/sign` endpoint (not `/sign/advanced`) |
| **Managed Keys** | ✅ Working | Uses Encypher-managed certificates (no BYOK) |
| **Verification Badge** | ✅ Required | Badge display is mandatory for free tier |
| **Coalition Participation** | ✅ Required | Must participate in Encypher coalition |
| **Branding** | ✅ Required | "Powered by Encypher" branding mandatory |
| **Bulk Marking Limit** | ✅ Working | 100 posts per batch operation |

### ❌ Broken Features

| Feature | Status | Issue |
|---------|--------|-------|
| **Auto-Sign on Update** | ❌ **BROKEN** | `/sign` endpoint fails with 500 error on re-signing |
| **Content Re-Signing** | ❌ **BROKEN** | Database unique constraint violation on duplicate `document_id` |
| **Provenance Chain** | ❌ **NOT AVAILABLE** | No `c2pa.edited` action support in `/sign` endpoint |
| **Edit Tracking** | ❌ **NOT AVAILABLE** | No `previous_instance_id` or edit history |

---

## Critical Bug Details

### Issue: `/sign` Endpoint Fails on Re-Signing

**Symptom**: When WordPress auto-signs a post on update, the second signing attempt fails with HTTP 500.

**Root Cause**: The `/sign` endpoint attempts to insert a new document record with the same `document_id`, violating the database's unique constraint.

**Error Log**:
```
INSERT INTO documents (
    id, organization_id, title, url, document_type,
    total_sentences, signed_text, text_hash, publication_date, created_at
)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)

[parameters: ('wp_post_13', 'org_demo', ...)]
(Background on this error at: https://sqlalche.me/e/20/gkpj)

2026-02-03 02:19:42 - POST /api/v1/sign - Status: 500 - Time: 0.0344s
INFO: 172.18.0.1:59540 - "POST /api/v1/sign HTTP/1.1" 500 Internal Server Error
```

**WordPress Plugin Logs**:
```
[03-Feb-2026 02:19:42 UTC] Encypher: Post 13 successfully signed with C2PA wrapper (spec compliant)
[03-Feb-2026 02:19:42 UTC] Encypher: Content changed for post 13, triggering re-sign with c2pa.edited
[03-Feb-2026 02:19:42 UTC] Encypher: Post 13 has 1 existing C2PA embedding(s). Stripping before re-signing.
[03-Feb-2026 02:19:42 UTC] Encypher: Auto-sign failed for post 13: Backend responded with status 500: Failed to store signed document
```

### Impact

**For Free Tier Users**:
- ❌ **Cannot use auto-sign on update** - Must disable `auto_mark_on_update` setting
- ❌ **Cannot re-sign edited posts** - Each post can only be signed once
- ❌ **No edit provenance** - No tracking of content changes over time
- ⚠️ **Manual workaround required** - Users must manually re-sign posts after editing

**For WordPress Workflow**:
- The plugin's default behavior (`auto_mark_on_publish: true`, `auto_mark_on_update: true`) is **incompatible** with Starter tier
- Users experience signing failures on every post update
- Error messages are not user-friendly (generic 500 error)

---

## Starter Tier Limitations (By Design)

These are intentional limitations for the free tier:

### 1. Signing Granularity
- **Starter**: Document-level only (entire post as one unit)
- **Pro/Enterprise**: Sentence-level segmentation with Merkle trees

**Code Evidence**:
```php
// @class-encypher-provenance-rest.php:249-260
$is_starter = ($tier === 'starter');

if ($is_starter) {
    $payload = [
        'text' => $clean_content,
        'document_id' => 'wp_post_' . $post_id,
        'document_title' => $post->post_title,
        'document_url' => get_permalink($post),
        'document_type' => 'article',
        'claim_generator' => 'WordPress/Encypher Plugin v' . ENCYPHER_ASSURANCE_VERSION,
    ];
    $response = $this->call_backend('/sign', $payload, true);
}
```

### 2. Signing Mode
- **Starter**: Managed keys only (shared Encypher certificate)
- **Pro/Enterprise**: BYOK (Bring Your Own Key) support

**Code Evidence**:
```php
// @class-encypher-provenance-admin.php:403-406
if ('starter' === $sanitized['tier']) {
    $sanitized['signing_mode'] = 'managed';
    $sanitized['signing_profile_id'] = '';
}
```

### 3. Bulk Operations
- **Starter**: 100 posts per batch
- **Pro/Enterprise**: Unlimited

**Code Evidence**:
```php
// @class-encypher-provenance-bulk.php:307-311
if ('starter' === $tier && count($post_ids) > 100) {
    wp_send_json_error([
        'message' => __('Free tier limit: 100 posts per bulk operation. Upgrade to Pro for unlimited marking.', 'encypher-provenance')
    ]);
}
```

### 4. UI Customization
- **Starter**: Badge required, branding required, position fixed (bottom-right)
- **Pro/Enterprise**: Customizable badge, optional branding, flexible positioning

**Code Evidence**:
```php
// @class-encypher-provenance-admin.php:428-432
if ($sanitized['tier'] === 'starter') {
    $sanitized['show_badge'] = true;
    $sanitized['badge_position'] = 'bottom-right';
    $sanitized['coalition_enabled'] = true;
    $sanitized['show_branding'] = true;
}
```

### 5. Verification Endpoint
- **Starter**: `/verify` (basic verification, no attribution/plagiarism)
- **Pro/Enterprise**: `/verify/advanced` (attribution, plagiarism detection, heat maps)

**Code Evidence**:
```php
// @class-encypher-provenance-rest.php:464-467
$tier = isset($settings['tier']) ? $settings['tier'] : 'starter';
$use_advanced = in_array($tier, ['professional', 'business', 'enterprise'], true);
$endpoint = $use_advanced ? '/verify/advanced' : '/verify';
```

---

## Recommended Fixes

### Option 1: Fix `/sign` Endpoint (Preferred)

**Change**: Make `/sign` endpoint support document updates by checking if `document_id` exists and updating instead of inserting.

**Implementation**:
```python
# In signing_executor.py
async def execute_signing(...):
    # Check if document exists
    existing_doc = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    doc = existing_doc.scalar_one_or_none()

    if doc:
        # Update existing document
        doc.signed_text = signed_text
        doc.text_hash = text_hash
        doc.updated_at = datetime.now(timezone.utc)
    else:
        # Insert new document
        doc = Document(
            id=document_id,
            organization_id=org_id,
            signed_text=signed_text,
            # ...
        )
        db.add(doc)
```

**Impact**: Enables Starter tier users to re-sign posts without errors.

**Limitation**: Still no provenance chain (no `previous_instance_id` tracking), but at least re-signing works.

### Option 2: Disable Auto-Update for Starter Tier

**Change**: Force `auto_mark_on_update = false` for Starter tier in plugin settings.

**Implementation**:
```php
// In class-encypher-provenance-admin.php
if ($sanitized['tier'] === 'starter') {
    $sanitized['auto_mark_on_update'] = false; // Force disable
}
```

**Impact**: Prevents errors but requires manual re-signing after edits.

**User Experience**: Clear messaging that "Auto-sign on update requires Pro tier".

### Option 3: Upgrade Prompt on Re-Sign Attempt

**Change**: Detect re-sign attempts for Starter tier and show upgrade prompt instead of failing.

**Implementation**:
```php
// In class-encypher-provenance-rest.php
if ($is_starter && $is_marked) {
    return new WP_Error(
        'starter_tier_limit',
        __('Re-signing edited posts requires Pro tier. Upgrade to enable automatic provenance tracking.', 'encypher-provenance'),
        ['status' => 403, 'upgrade_url' => 'https://encypher.com/pricing']
    );
}
```

**Impact**: Better user experience with clear upgrade path.

---

## Testing Results

### Test 1: Initial Signing (Starter Tier) ✅
- **Config**: `tier: starter`, `auto_mark_on_publish: true`, `auto_mark_on_update: false`
- **Action**: Create and publish new post
- **Result**: ✅ **SUCCESS** - Post signed with `/sign` endpoint
- **Logs**: `Post 13 successfully signed with C2PA wrapper (spec compliant)`

### Test 2: Re-Signing (Starter Tier) ❌
- **Config**: `tier: starter`, `auto_mark_on_publish: true`, `auto_mark_on_update: true`
- **Action**: Create and publish new post (triggers double-sign due to WordPress workflow)
- **Result**: ❌ **FAILED** - Second sign attempt returns 500 error
- **Error**: `Backend responded with status 500: Failed to store signed document`
- **Database**: Unique constraint violation on `documents.id`

### Test 3: Enterprise Tier Comparison ✅
- **Config**: `tier: enterprise`, `auto_mark_on_publish: true`, `auto_mark_on_update: true`
- **Action**: Create and publish new post
- **Result**: ✅ **SUCCESS** - Post signed twice with `/sign/advanced`, provenance chain tracked
- **Logs**:
  - `Stored new instance_id for post 7: 476ae886-8bff-4000-81ab-07ecc13e9070`
  - `Post 7 is being edited. Previous instance_id: 476ae886-8bff-4000-81ab-07ecc13e9070`
  - `Stored new instance_id for post 7: 2cae2070-99c9-4861-9c00-a417fca6dedd`

---

## User Impact Assessment

### Current State for Free Users

**What Works**:
- ✅ Sign posts on first publish
- ✅ Verify signed content
- ✅ Display verification badge
- ✅ Participate in coalition
- ✅ Bulk mark up to 100 posts (one-time)

**What Doesn't Work**:
- ❌ Auto-sign on post updates
- ❌ Re-sign edited content
- ❌ Track edit history
- ❌ Customize badge appearance
- ❌ Remove branding

**Workaround**:
Users must **disable `auto_mark_on_update`** in plugin settings to avoid 500 errors. This means:
1. Publish post → auto-signed ✅
2. Edit post → **NOT** auto-signed ❌
3. Manual re-sign required via editor sidebar

---

## Recommendations

### Immediate Actions (P0)

1. **Fix `/sign` endpoint** to support document updates (upsert instead of insert-only)
2. **Add clear error messaging** for Starter tier re-sign attempts
3. **Update plugin documentation** to clarify Starter tier limitations

### Short-Term Actions (P1)

1. **Force `auto_mark_on_update = false`** for Starter tier in plugin settings
2. **Add upgrade prompts** in editor sidebar when re-signing is attempted
3. **Update README** with Starter tier feature matrix

### Long-Term Actions (P2)

1. **Consider basic provenance chain** for Starter tier (limited to 5 edits?)
2. **Add tier comparison table** in WordPress admin dashboard
3. **Implement graceful degradation** for all tier-gated features

---

## Conclusion

**The WordPress Provenance Plugin is NOT fully functional for free (Starter) tier users** due to a critical bug in the Enterprise API's `/sign` endpoint. While initial signing works correctly, the inability to re-sign edited posts makes the plugin unsuitable for real-world WordPress workflows without manual intervention.

**Recommended Priority**: **P0 - Critical Bug Fix Required**

The `/sign` endpoint must be updated to support document updates (upsert logic) to enable Starter tier users to have a functional, albeit limited, experience with the plugin.

---

**Verified by**: TEAM_148
**Date**: 2026-02-03
**Environment**: Docker (WordPress 6.5.5 + Enterprise API 1.0.0-preview)
