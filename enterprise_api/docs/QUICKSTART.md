# Encypher Enterprise API - Quickstart Guide

Get started with the Encypher Enterprise API in 5 minutes.

## Prerequisites

- API key (contact sales@encypherai.com for beta access)
- `curl` or any HTTP client

## 1. Verify Your API Key

Test your API key with a health check:

```bash
curl https://api.encypherai.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "environment": "preview",
  "version": "1.0.0-preview"
}
```

## 2. Sign Your First Document

Sign a piece of content with a C2PA manifest:

```bash
curl -X POST https://api.encypherai.com/api/v1/sign \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Breaking news: Scientists discover new exoplanet. The planet is located 100 light-years away.",
    "document_title": "New Exoplanet Discovered",
    "options": {
      "segmentation_level": "sentence",
      "manifest_mode": "micro",
      "ecc": true,
      "embed_c2pa": true
    }
  }'
```

Expected response:
```json
{
  "success": true,
  "data": {
    "document": {
      "document_id": "doc_a1b2c3d4e5f6",
      "signed_text": "Breaking news: Scientists discover new exoplanet... [invisible markers/manifest embedded]",
      "verification_url": "https://verify.encypherai.com/doc_a1b2c3d4e5f6"
    },
    "metadata": {
      "manifest_mode": "micro"
    }
  },
  "error": null,
  "correlation_id": "req-123"
}
```

**Important:** Save the `signed_text` - it contains the invisible C2PA manifest!

## 3. Verify Signed Content

Verify the C2PA manifest you just created:

```bash
curl -X POST https://api.encypherai.com/api/v1/verify \
  -H "Content-Type: application/json" \
  -d '{
    "text": "<paste signed_text from step 2 here>"
  }'
```

Expected response:
```json
{
  "success": true,
  "data": {
    "valid": true,
    "tampered": false,
    "reason_code": "OK",
    "signer_id": "your_org_id",
    "signer_name": "Your Organization",
    "timestamp": "2025-01-15T10:30:00Z",
    "details": {
      "manifest": { "...": "..." },
      "duration_ms": 35,
      "payload_bytes": 4872
    }
  },
  "error": null,
  "correlation_id": "req-123"
}
```

## 4. Test Tamper Detection

Modify the signed text (e.g., change "100" to "200") and verify again:

```bash
curl -X POST https://api.encypherai.com/api/v1/verify \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Breaking news: Scientists discover new exoplanet. The planet is located 200 light-years away. [manifest]"
  }'
```

Expected response:
```json
{
  "success": true,
  "data": {
    "valid": false,
    "tampered": true,
    "reason_code": "SIGNATURE_INVALID",
    "signer_id": "your_org_id",
    "signer_name": "Your Organization",
    "details": {
      "manifest": {},
      "exception": "hash mismatch"
    }
  },
  "error": null,
  "correlation_id": "req-456"
}
```

The API detects the modification!

---

## Optional: Create Manifest JSON (Public Helper)

If you want a file-format-independent helper that creates a manifest JSON payload from plaintext, you can use the public `create-manifest` endpoint.

This endpoint is public and supports an *optional* API key for higher limits.

```bash
curl -X POST https://api.encypherai.com/api/v1/public/c2pa/create-manifest \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world. This will be signed.",
    "document_title": "Quickstart Manifest"
  }'
```

You can then feed the returned `signing` payload fields into `/api/v1/sign`:

```bash
curl -X POST https://api.encypherai.com/api/v1/sign \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world. This will be signed.",
    "document_title": "Quickstart Manifest",
    "claim_generator": "encypher.public.create-manifest",
    "actions": [{"action": "c2pa.created"}]
  }'
```

## Optional: Validate Manifest JSON (Public Helper)

If you want to validate the structure of a manifest JSON payload (including optional assertion schema validation), you can use the public `validate-manifest` endpoint.

This endpoint is public and supports an *optional* API key for higher limits.

```bash
curl -X POST https://api.encypherai.com/api/v1/public/c2pa/validate-manifest \
  -H "Content-Type: application/json" \
  -d '{
    "manifest": {
      "claim_generator": "example-generator",
      "assertions": [
        {"label": "c2pa.actions.v1", "data": {"actions": [{"action": "c2pa.created"}]}}
      ]
    }
  }'
```

## Optional: Look Up Trust Anchor (Public Helper)

If you are building an external verifier, you can retrieve a signer's public key via the public trust anchor endpoint.

```bash
curl https://api.encypherai.com/api/v1/public/c2pa/trust-anchors/encypher.public
```

## 5. Look Up Sentence Provenance

Look up where a sentence came from:

```bash
curl -X POST https://api.encypherai.com/api/v1/lookup \
  -H "Content-Type: application/json" \
  -d '{
    "sentence_text": "Breaking news: Scientists discover new exoplanet."
  }'
```

Expected response:
```json
{
  "success": true,
  "found": true,
  "document_title": "New Exoplanet Discovered",
  "organization_name": "Your Organization",
  "publication_date": "2025-01-15T10:30:00Z",
  "sentence_index": 0
}
```

## 6. Check Your Usage

Get your organization's usage statistics:

```bash
curl -X GET https://api.encypherai.com/api/v1/usage \
  -H "Authorization: Bearer YOUR_API_KEY"
```

Expected response:
```json
{
  "success": true,
  "organization_id": "your_org_id",
  "organization_name": "Your Organization",
  "tier": "enterprise",
  "usage": {
    "documents_signed": 1,
    "sentences_signed": 2,
    "api_calls_this_month": 3,
    "quota": {
      "limit": "...",
      "remaining": "..."
    }
  }
}
```

For up-to-date limits and remaining quota for your organization, use:

- `GET /api/v1/account/quota`

---

## Next Steps

### Request a Certificate

For production use, request an SSL.com code signing certificate:

```bash
curl -X POST https://api.encypherai.com/api/v1/onboarding/request-certificate \
  -H "Authorization: Bearer YOUR_API_KEY"
```

You'll receive a validation URL. Complete the identity verification process.

### Check Certificate Status

Monitor your certificate request:

```bash
curl -X GET https://api.encypherai.com/api/v1/onboarding/certificate-status \
  -H "Authorization: Bearer YOUR_API_KEY"
```

---

## Code Examples

### Python

```python
import requests

API_KEY = "encypher_your_api_key"
BASE_URL = "https://api.encypherai.com"

# Sign content
response = requests.post(
    f"{BASE_URL}/api/v1/sign",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={
        "text": "Your content here.",
        "document_title": "Document Title",
        "options": {"manifest_mode": "micro", "segmentation_level": "sentence"}
    }
)
result = response.json()
signed_text = result["data"]["document"]["signed_text"]

# Verify content
response = requests.post(
    f"{BASE_URL}/api/v1/verify",
    json={"text": signed_text}
)
verification = response.json()
verdict = verification["data"]
print(f"Valid: {verdict['valid']} (correlation_id={verification['correlation_id']})")
```

### JavaScript (Node.js)

```javascript
const axios = require('axios');

const API_KEY = 'encypher_your_api_key';
const BASE_URL = 'https://api.encypherai.com';

async function signContent(text) {
  const response = await axios.post(
    `${BASE_URL}/api/v1/sign`,
    { text, document_title: 'My Document' },
    { headers: { Authorization: `Bearer ${API_KEY}` } }
  );
  return response.data;
}

async function verifyContent(text) {
  const response = await axios.post(
    `${BASE_URL}/api/v1/verify`,
    { text }
  );
  return response.data;
}

// Usage
(async () => {
  const signed = await signContent('Your content here.');
  console.log('Signed:', signed.data.document.document_id);

  const verified = await verifyContent(signed.data.document.signed_text);
  console.log('Valid:', verified.data.valid);
})();
```

---

## Troubleshooting

### "Invalid API key"
- Check that your API key is correct
- Ensure the key hasn't expired
- Verify you're using the `Authorization: Bearer` header

### "No private key found"
- Your organization needs to complete certificate onboarding
- Use `/api/v1/onboarding/request-certificate` to start the process

### "Monthly quota exceeded"
- Upgrade your plan at https://dashboard.encypherai.com
- Contact sales@encypherai.com for enterprise pricing

---

## Support

- **Documentation:** https://docs.encypherai.com
- **API Reference:** See [API.md](./API.md)
- **Email:** support@encypherai.com
