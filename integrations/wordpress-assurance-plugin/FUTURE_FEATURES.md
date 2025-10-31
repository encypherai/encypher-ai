# WordPress C2PA Plugin - Future Features

## 1. Manifest Chaining with WordPress Revisions

### Overview
Leverage WordPress's built-in revision system to create a complete C2PA provenance chain, showing the full edit history of content with cryptographic verification at each step.

### Current Implementation
- ✅ Auto-sign on publish (new posts)
- ✅ Auto-re-sign on update (edited posts)
- ✅ Strip old embeddings before re-signing
- ✅ Use `c2pa.created` for new posts
- ✅ Use `c2pa.edited` for updates

### Proposed Enhancement

#### Manifest Chain Structure
```
Original Post (v1)
  ↓ c2pa.created
Manifest 1 (hash of v1)
  ↓
Edit 1 (v2)
  ↓ c2pa.edited (references Manifest 1)
Manifest 2 (hash of v2, parent = Manifest 1)
  ↓
Edit 2 (v3)
  ↓ c2pa.edited (references Manifest 2)
Manifest 3 (hash of v3, parent = Manifest 2)
```

#### Features
- **Revision Tracking**: Store C2PA manifest hash with each WordPress revision
- **Parent References**: Each manifest references the previous version
- **Historical Verification**: Verify any past version of the content
- **Edit Timeline**: Visual timeline showing all edits with verification status
- **Rollback Support**: Restore and verify any previous version

#### Implementation Details

##### 1. Store Manifest Per Revision
```php
add_action('wp_insert_post_revision', function($revision_id) {
    $parent_id = wp_get_post_parent_id($revision_id);
    
    // Store C2PA data with revision
    $manifest_hash = get_post_meta($parent_id, '_encypher_manifest_hash', true);
    $document_id = get_post_meta($parent_id, '_encypher_assurance_document_id', true);
    $action_type = get_post_meta($parent_id, '_encypher_action_type', true);
    
    update_metadata('post', $revision_id, '_encypher_revision_manifest_hash', $manifest_hash);
    update_metadata('post', $revision_id, '_encypher_revision_document_id', $document_id);
    update_metadata('post', $revision_id, '_encypher_revision_action', $action_type);
    update_metadata('post', $revision_id, '_encypher_revision_timestamp', current_time('mysql'));
});
```

##### 2. Manifest Chaining in Enterprise API
```python
# When creating new manifest for edited content
previous_manifest_hash = get_previous_manifest_hash(document_id)

manifest_payload = {
    'action': 'c2pa.edited',
    'parent_manifest': previous_manifest_hash,  # Link to previous version
    'edit_timestamp': datetime.utcnow(),
    'editor': user_info,
    # ... other C2PA fields
}
```

##### 3. Revision History UI
- Add "C2PA History" tab in post editor
- Show timeline of all signed versions
- Display verification status for each revision
- Allow viewing/restoring any verified version

##### 4. Verification Endpoint
```php
// New REST endpoint: /encypher-assurance/v1/verify-revision
GET /wp-json/encypher-assurance/v1/verify-revision?post_id=1&revision_id=123

Response:
{
    "valid": true,
    "revision_id": 123,
    "manifest_hash": "abc123...",
    "parent_manifest": "def456...",
    "action": "c2pa.edited",
    "timestamp": "2025-10-31T12:00:00Z",
    "chain_valid": true,  // All parent manifests verified
    "chain_depth": 5      // Number of edits
}
```

### Tier-Based Feature Access

#### Free Tier
- Current implementation only
- Sign on publish, re-sign on update
- No revision tracking

#### Pro Tier
- Revision tracking enabled
- View edit history with C2PA data
- Verify current version only

#### Enterprise Tier
- Full manifest chaining
- Verify any historical version
- Visual provenance timeline
- Export complete edit history
- API access to revision chain

### Technical Requirements

#### Database Schema
```sql
-- Add to existing post meta
_encypher_manifest_hash          VARCHAR(64)   -- Current manifest hash
_encypher_parent_manifest_hash   VARCHAR(64)   -- Previous manifest hash
_encypher_chain_depth            INTEGER       -- Number of edits

-- Per revision metadata
_encypher_revision_manifest_hash VARCHAR(64)
_encypher_revision_document_id   VARCHAR(100)
_encypher_revision_action        VARCHAR(50)
_encypher_revision_timestamp     DATETIME
```

#### Enterprise API Changes
- Add `parent_manifest_hash` field to manifest creation
- Store manifest chain in database
- Add endpoint to retrieve full chain
- Validate chain integrity on verification

### Benefits

#### For Publishers
- **Complete audit trail**: Every edit is cryptographically verified
- **Accountability**: Know who edited what and when
- **Compliance**: Meet regulatory requirements for content history
- **Trust**: Readers can verify the entire edit history

#### For Readers
- **Transparency**: See how content evolved over time
- **Verification**: Confirm no unauthorized changes in history
- **Context**: Understand editorial process

### Estimated Implementation

#### Phase 1: Basic Revision Tracking (1-2 weeks)
- Store manifest hash with each revision
- Display revision history in admin
- Verify current version only

#### Phase 2: Manifest Chaining (2-3 weeks)
- Implement parent manifest references
- Update Enterprise API for chain support
- Add chain validation

#### Phase 3: Advanced Features (2-3 weeks)
- Visual timeline UI
- Historical version verification
- Export/API access
- Performance optimization

### Priority
**Medium-High** - Valuable differentiator for Pro/Enterprise tiers, aligns with C2PA best practices

### Dependencies
- Current auto-signing implementation (✅ Complete)
- Enterprise API manifest storage
- WordPress revision system (built-in)

### Notes
- WordPress keeps last 25 revisions by default (configurable)
- Consider storage implications for high-edit posts
- May need revision cleanup policy for very old manifests
- Could offer "snapshot" feature to preserve specific versions permanently

---

## 2. C2PA Spec Compliance: Document-Level Wrapper

### Overview
Update Enterprise API to add ONE final `C2PATextManifestWrapper` at the end of the document, in addition to sentence-level embeddings.

### Current Implementation (Non-Compliant)
- Creates one `C2PATextManifestWrapper` per sentence
- Violates C2PA spec: "Quantity: Zero or one"
- Will trigger `manifest.text.multipleWrappers` error in standard validators

### Required Implementation (Spec-Compliant)
```
Sentence 1 text [invisible proprietary embedding]
Sentence 2 text [invisible proprietary embedding]  
Sentence 3 text [invisible proprietary embedding]
[ONE C2PATextManifestWrapper at end - spec compliant]
```

### Benefits
- ✅ **Sentence-level verification**: Our proprietary feature for granular content authentication
- ✅ **C2PA compliance**: Standard validators can verify the document
- ✅ **Backward compatible**: Works with all C2PA tools
- ✅ **Best of both worlds**: Granular + standard verification

### Implementation Details

#### Current Code (WRONG - Creates Multiple Wrappers)
```python
# enterprise_api/app/services/embedding_service.py:182
for idx, (segment, leaf_hash) in enumerate(zip(segments, leaf_hashes)):
    embedded_text = UnicodeMetadata.embed_metadata(  # ← Creates wrapper per sentence!
        text=segment,
        private_key=self.private_key,
        signer_id=self.signer_id,
        metadata_format="c2pa",  # ← Each call creates a C2PATextManifestWrapper
        ...
    )
```

#### Required Fix (CORRECT - One Wrapper for Document)
```python
# Step 1: Create sentence-level embeddings WITHOUT C2PA wrappers
for idx, (segment, leaf_hash) in enumerate(zip(segments, leaf_hashes)):
    embedded_text = UnicodeMetadata.embed_metadata(
        text=segment,
        private_key=self.private_key,
        signer_id=self.signer_id,
        metadata_format="invisible",  # ← Proprietary format, no C2PA wrapper
        custom_metadata={'leaf_hash': leaf_hash, 'index': idx},
        ...
    )
    # Append to document
    full_document += embedded_text

# Step 2: Add ONE C2PATextManifestWrapper at the end
final_document = UnicodeMetadata.embed_metadata(
    text=full_document,  # ← Entire document with sentence embeddings
    private_key=self.private_key,
    signer_id=self.signer_id,
    metadata_format="c2pa",  # ← Creates ONE wrapper at end
    add_hard_binding=True,
    claim_generator=f"EncypherAI Enterprise API/{organization_id}",
    actions=[{"action": "c2pa.created"}],
    ...
)
```

#### Files to Modify
1. **`enterprise_api/app/services/embedding_service.py`**
   - Update `create_embeddings()` method
   - Add two-phase embedding: invisible + C2PA wrapper
   
2. **`encypher-ai` library** (if needed)
   - Ensure `metadata_format="invisible"` option exists
   - Or use a different method for proprietary embeddings

3. **WordPress Plugin**
   - Update detection to recognize both formats
   - Validate final C2PA wrapper only

### Reference
See `docs/c2pa/Manifests_Text.adoc` lines 24, 92, 132

### Priority
**High** - Required for C2PA spec compliance and interoperability

---

## 3. Other Future Features (To Be Added)

### Bulk Signing
- Sign multiple posts at once
- Pro/Enterprise feature
- Background processing for large batches

### Post List Column
- Show C2PA status in post list
- Quick visual indicator (✓ Signed, ⚠️ Modified, ✗ Not Signed)
- Sortable/filterable

### Settings UI Enhancements
- Badge position selector (end of content vs inline header)
- Auto-sign toggle
- Post type selection
- Custom badge styling

### Public Verification Page
- Standalone page for readers to verify content
- Paste text or upload file
- Show full provenance report
- Shareable verification links

---

*Last Updated: October 31, 2025*
