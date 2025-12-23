# Legacy PEM Keys Migration Guide

## Problem

Old content was signed using PEM format Ed25519 keys via environment variables:
- `DEMO_PRIVATE_KEY_PEM`
- `DEMO_PUBLIC_KEY_PEM`

The new backend uses raw Ed25519 keys (32 bytes hex format), so old signatures cannot be verified without the original PEM keys.

## Solution

### Step 1: Locate Your Old PEM Keys

Find the PEM keys from your old backend deployment. They look like:

```
-----BEGIN PRIVATE KEY-----
MC4CAQAwBQYDK2VwBCIEIGg5...
-----END PRIVATE KEY-----
```

```
-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAXYZ1...
-----END PUBLIC KEY-----
```

### Step 2: Set Environment Variables

In your Railway deployment, add these environment variables:

```bash
DEMO_PRIVATE_KEY_PEM="-----BEGIN PRIVATE KEY-----
MC4CAQAwBQYDK2VwBCIEIGg5...
-----END PRIVATE KEY-----"

DEMO_PUBLIC_KEY_PEM="-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAXYZ1...
-----END PUBLIC KEY-----"
```

**Important**: Include the newlines in the PEM format. Railway supports multi-line environment variables.

### Step 3: Run Population Script

After setting the environment variables, run the population script:

```bash
railway run uv run python enterprise_api/scripts/populate_demo_public_key.py
```

The script will:
1. ✅ Detect the PEM format keys
2. ✅ Load and parse them
3. ✅ Extract the raw public key bytes
4. ✅ Store in the database for Trust Anchor verification

### Step 4: Verify

Test with old signed content at https://encypherai.com/tools/decode

Expected result:
```
✅ Verification Status: Success
✅ Signer: demo-signer-id (Verified via Trust Anchor)
✅ Signature: Valid
✅ Content: Unmodified
```

## How It Works

### PEM Format
PEM (Privacy Enhanced Mail) is a Base64-encoded format for cryptographic keys:

```
-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAXYZ1234567890abcdefghijklmnopqrstuvwxyz
-----END PUBLIC KEY-----
```

This encodes:
- ASN.1 structure with algorithm identifier (Ed25519)
- Raw 32-byte public key

### Raw Format
The new backend uses raw Ed25519 keys (32 bytes hex):

```
58667d123456789...  (64 hex characters = 32 bytes)
```

### Conversion
The population script converts PEM → Raw:

```python
# Load PEM
public_key = serialization.load_pem_public_key(pem_str.encode())

# Extract raw bytes
raw_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PublicFormat.Raw
)  # Returns 32 bytes
```

## Fallback Behavior

The population script tries keys in this order:

1. **PEM Public Key** (`DEMO_PUBLIC_KEY_PEM`) - Preferred for old content
2. **PEM Private Key** (`DEMO_PRIVATE_KEY_PEM`) - Derives public key
3. **Hex Private Key** (`DEMO_PRIVATE_KEY_HEX` or `SECRET_KEY`) - Current format
4. **Generated Key** - Ephemeral key (not recommended for production)

## Security Considerations

### Should You Keep Old Keys?

**Yes, if:**
- You have old signed content in production
- Users need to verify historical content
- You want backward compatibility

**No, if:**
- All old content has been re-signed with new keys
- You're starting fresh
- Old content is no longer relevant

### Key Rotation Strategy

1. **Phase 1** (Current): Support both old PEM keys and new hex keys
2. **Phase 2** (Future): Re-sign all old content with new keys
3. **Phase 3** (Future): Deprecate PEM key support

## Troubleshooting

### Error: "PEM does not contain an Ed25519 public key"

**Cause**: Wrong key type (RSA, ECDSA, etc.)

**Solution**: Ensure your old backend used Ed25519 keys. Check with:
```bash
openssl pkey -in private_key.pem -text -noout
```

Should show: `ED25519 Private-Key`

### Error: "Failed to load PEM public key"

**Cause**: Malformed PEM string (missing newlines, wrong format)

**Solution**: Ensure PEM includes header/footer and newlines:
```
-----BEGIN PUBLIC KEY-----\nMCowBQ...\n-----END PUBLIC KEY-----
```

### Old Content Still Fails Verification

**Possible causes:**
1. Wrong PEM keys loaded (not the ones used to sign)
2. Content was actually modified (legitimate tamper detection)
3. Signer ID mismatch (content signed with different signer_id)

**Debug steps:**
```bash
# Check what key is in database
railway run psql $DATABASE_URL -c "SELECT id, encode(public_key, 'hex') FROM organizations WHERE id = 'demo-signer-id';"

# Check what key the script loaded
railway run uv run python enterprise_api/scripts/populate_demo_public_key.py
```

## Example: Full Migration

```bash
# 1. Get your old PEM keys from old backend
export OLD_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----
MC4CAQAwBQYDK2VwBCIEIGg5...
-----END PRIVATE KEY-----"

# 2. Set in Railway
railway variables set DEMO_PRIVATE_KEY_PEM="$OLD_PRIVATE_KEY"

# 3. Run migration (if not already done)
railway run psql $DATABASE_URL -f enterprise_api/migrations/015_add_public_key_to_organizations.sql

# 4. Populate keys
railway run uv run python enterprise_api/scripts/populate_demo_public_key.py

# 5. Test
curl -X POST https://api.encypherai.com/api/v1/tools/decode \
  -H "Content-Type: application/json" \
  -d '{"encoded_text": "YOUR_OLD_SIGNED_CONTENT"}'
```

## Related Files

- `app/config.py` - Added `demo_private_key_pem` and `demo_public_key_pem` settings
- `scripts/populate_demo_public_key.py` - Updated to support PEM format
- `migrations/015_add_public_key_to_organizations.sql` - Database schema
- `.env.example` - Documented PEM environment variables

## Questions?

If old content still doesn't verify after following this guide:
1. Check Railway logs for PEM loading errors
2. Verify the PEM keys are the exact ones used to sign the content
3. Confirm the signer_id in the manifest matches the database entry
