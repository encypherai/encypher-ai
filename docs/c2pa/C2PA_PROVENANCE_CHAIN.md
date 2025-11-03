# C2PA Provenance Chain Implementation

## Overview

The Enterprise API and WordPress plugin now support complete C2PA provenance chain tracking with ingredient references, enabling users to trace content back to its original creation date through all edits.

## Features

### ✅ C2PA-Compliant Actions
- **`c2pa.created`**: Applied on initial content creation
- **`c2pa.edited`**: Applied on subsequent edits
- **`c2pa.watermarked`**: Automatically added for Unicode variation selector embedding

### ✅ Ingredient References
- Each edit includes the previous version's complete C2PA manifest as an "ingredient"
- Enables traversal of the complete edit history
- Preserves original creation timestamp through the chain

### ✅ Database Storage
- Full C2PA manifests stored in `content_references.manifest_data` (JSONB)
- Instance IDs tracked in `content_references.instance_id`
- Previous version references in `content_references.previous_instance_id`
- Indexed for efficient lookups

### ✅ WordPress UI
- **Provenance Chain Viewer**: Visual display of complete edit history
- Shows creation and edit timestamps
- Displays instance IDs for each version
- Copy button for full JSON manifest

## Technical Implementation

### Enterprise API

#### Manifest Creation Flow

1. **Initial Creation** (`c2pa.created`):
   ```json
   {
     "instance_id": "uuid-1",
     "actions": [{"label": "c2pa.created", "when": "2025-11-03T..."}],
     "assertions": [...]
   }
   ```

2. **First Edit** (`c2pa.edited`):
   ```json
   {
     "instance_id": "uuid-2",
     "actions": [{"label": "c2pa.edited", "when": "2025-11-03T..."}],
     "ingredients": [{
       "title": "Previous version",
       "instance_id": "uuid-1",
       "relationship": "parentOf",
       "c2pa_manifest": {
         "instance_id": "uuid-1",
         "actions": [{"label": "c2pa.created", "when": "..."}],
         "assertions": [...]
       }
     }],
     "assertions": [...]
   }
   ```

3. **Subsequent Edits**: Each edit includes the previous version as an ingredient, creating a complete chain.

#### Database Schema

```sql
-- Added columns to content_references table
ALTER TABLE content_references ADD COLUMN instance_id VARCHAR(255);
ALTER TABLE content_references ADD COLUMN previous_instance_id VARCHAR(255);
ALTER TABLE content_references ADD COLUMN manifest_data JSONB;

CREATE INDEX ix_content_references_instance_id ON content_references(instance_id);
CREATE INDEX ix_content_references_previous_instance_id ON content_references(previous_instance_id);
```

#### API Endpoints

**Encode with Embeddings** (`POST /api/v1/enterprise/embeddings/encode-with-embeddings`):
- Accepts `action` parameter: `"c2pa.created"` or `"c2pa.edited"`
- Accepts `previous_instance_id` parameter for edit tracking
- Returns `instance_id` in response metadata

**Extract and Verify** (`POST /api/v1/public/extract-and-verify`):
- Extracts complete manifest including ingredients
- Verifies signature, soft binding, and hard binding
- Returns full provenance chain

### WordPress Plugin

#### Automatic Signing

- **On Publish**: Automatically signs with `c2pa.created`
- **On Edit**: Automatically re-signs with `c2pa.edited`
- Prevents double-signing through cached content hash comparison

#### Provenance Chain Viewer

Located in the verification modal:

```
🔗 View Provenance Chain
  ✏️ Edited at 2025-11-03T22:43:29Z
     Instance: ac217e84...
  
  ✏️ Edited at 2025-11-03T22:39:56Z
     Instance: da590ad0...
  
  🌱 Created at 2025-11-03T22:39:56Z
     Instance: fdad7d4d...
```

#### Copy Button

- Displays: `📋 Copy to Clipboard`
- Copies full JSON manifest to clipboard
- Shows confirmation: `✓ Copied!`

## C2PA Compliance

### Specification Adherence

✅ **C2PA 2.2 Compliant**
- Uses official C2PA JSON-LD context: `https://c2pa.org/schemas/v2.2/c2pa.jsonld`
- Follows C2PA action vocabulary
- Implements ingredient references per spec
- Uses COSE_Sign1 for signatures

✅ **Required Assertions**
- `c2pa.actions.v1`: Action history
- `c2pa.hash.data.v1`: Content hash (hard binding)
- `c2pa.soft_binding.v1`: Soft binding hash

✅ **Ingredient Structure**
```json
{
  "title": "Previous version",
  "instance_id": "uuid-of-previous",
  "relationship": "parentOf",
  "c2pa_manifest": { /* complete previous manifest */ }
}
```

### Verification

All three binding types verified:
1. **Signature Verification**: COSE_Sign1 signature validated
2. **Soft Binding**: Unicode variation selector hash verified
3. **Hard Binding**: Content hash verified with exclusions

## Usage Examples

### Creating Content

```php
// WordPress automatically handles this
// On publish: c2pa.created action applied
// Manifest stored with instance_id
```

### Editing Content

```php
// WordPress automatically handles this
// On edit: c2pa.edited action applied
// Previous manifest fetched and included as ingredient
// New manifest stored with reference to previous
```

### Verifying Content

```javascript
// Click verification button in WordPress
// Modal displays:
// - Verification status
// - Provenance chain viewer
// - Full JSON manifest
// - Copy button
```

### API Integration

```python
# Create content
response = requests.post(
    "http://enterprise-api:8000/api/v1/enterprise/embeddings/encode-with-embeddings",
    json={
        "text": "Content to sign",
        "document_id": "doc_123",
        "action": "c2pa.created"
    },
    headers={"X-API-Key": api_key}
)
instance_id = response.json()["metadata"]["instance_id"]

# Edit content
response = requests.post(
    "http://enterprise-api:8000/api/v1/enterprise/embeddings/encode-with-embeddings",
    json={
        "text": "Updated content",
        "document_id": "doc_123",
        "action": "c2pa.edited",
        "previous_instance_id": instance_id
    },
    headers={"X-API-Key": api_key}
)
```

## Benefits

### For Content Creators
- **Transparency**: Complete edit history visible
- **Trust**: Original creation date preserved
- **Authenticity**: Cryptographic proof of provenance

### For Consumers
- **Verification**: Can trace content to original source
- **Context**: Understand content evolution
- **Trust**: See when content was created vs edited

### For Publishers
- **Compliance**: C2PA-compliant implementation
- **Automation**: Automatic signing on create/edit
- **Integration**: Works seamlessly with WordPress workflow

## Troubleshooting

### Double-Signing Issues
**Fixed**: Cached content hash comparison prevents re-signing when only the C2PA wrapper changes.

### Missing Ingredients
**Fixed**: Previous manifests are fetched from database and embedded as ingredients on edits.

### Verification Failures
**Check**:
1. Content hasn't been modified outside WordPress
2. Database contains previous manifest for `previous_instance_id`
3. Signature keys are valid

## Future Enhancements

- [ ] Support for multiple ingredient relationships
- [ ] Ingredient thumbnails/previews
- [ ] Export provenance chain as standalone file
- [ ] Provenance chain visualization graph
- [ ] Support for forked content (multiple parents)

## References

- [C2PA Technical Specification](https://c2pa.org/specifications/specifications/2.2/specs/C2PA_Specification.html)
- [C2PA Implementation Guidance](./C2PA%20Implimentation%20Guidance.md)
- [C2PA UX Guidance](./C2PA%20UX%20Guidance.md)
