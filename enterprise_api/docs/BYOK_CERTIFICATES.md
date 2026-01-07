# BYOK Certificate Setup Guide

This guide explains how enterprise customers can use their own CA-signed certificates for content signing with Encypher.

## Overview

Encypher supports two BYOK (Bring Your Own Key) options:

1. **Raw Public Key** - Register an Ed25519/EC/RSA public key directly
2. **CA-Signed Certificate** - Upload an X.509 certificate from a C2PA-trusted CA

For maximum trust and interoperability with the C2PA ecosystem, we recommend using CA-signed certificates.

## C2PA Trusted Certificate Authorities

Certificates must chain to a CA in the [official C2PA trust list](https://github.com/c2pa-org/conformance-public/blob/main/trust-list/C2PA-TRUST-LIST.pem):

| CA | Certificate Types | Notes |
|----|-------------------|-------|
| **Google** | EC P-384 | C2PA Root CA G3 |
| **SSL.com** | RSA, EC P-384 | C2PA RSA/ECC Root CA 2025 |
| **DigiCert** | RSA-4096, EC P-384 | C2PA Root CAs |
| **Adobe** | EC P-384 | Product Issuing CA |
| **Trufo** | EC P-384 | Root CA (2025) |
| **vivo** | EC P-384/521 | Content Provenance Root CA |
| **Xiaomi** | EC P-384 | Root CA |
| **Irdeto** | EC P-384 | C2PA Root CA G1 |

### Recommended: SSL.com Partnership

Encypher has an integration with SSL.com for streamlined certificate provisioning. Contact us for discounted rates on C2PA-compliant certificates.

## Option 1: Upload CA-Signed Certificate

### Prerequisites

- Business tier or higher subscription
- X.509 certificate from a C2PA-trusted CA
- Certificate chain (intermediate certificates)

### Step 1: Obtain a Certificate

Contact one of the trusted CAs above to obtain a code signing certificate. You'll need:

1. Generate a private key (keep this secure!)
2. Create a Certificate Signing Request (CSR)
3. Complete the CA's identity verification process
4. Receive your signed certificate

Example using OpenSSL (for SSL.com or DigiCert):

```bash
# Generate EC P-384 private key
openssl ecparam -genkey -name secp384r1 -out private_key.pem

# Create CSR
openssl req -new -key private_key.pem -out request.csr \
  -subj "/CN=Your Organization/O=Your Company/C=US"

# Submit CSR to your chosen CA...
# After approval, you'll receive certificate.pem and chain.pem
```

### Step 2: Upload Certificate to Encypher

```bash
# List trusted CAs (optional - verify your CA is supported)
curl -X GET "https://api.encypherai.com/api/v1/byok/trusted-cas" \
  -H "X-API-Key: YOUR_API_KEY"

# Upload your certificate
curl -X POST "https://api.encypherai.com/api/v1/byok/certificates" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "certificate_pem": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----",
    "chain_pem": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----",
    "key_name": "Production Signing Certificate"
  }'
```

Response:
```json
{
  "success": true,
  "data": {
    "key_id": "pk_abc123...",
    "subject": "CN=Your Organization,O=Your Company,C=US",
    "issuer": "CN=SSL.com C2PA RSA Root CA 2025,O=SSL Corporation,C=US",
    "algorithm": "EC-secp384r1",
    "expires_at": "2027-01-15T00:00:00Z",
    "fingerprint": "SHA256:abc123..."
  }
}
```

### Step 3: Configure Signing

After uploading, content signed by your organization will use your certificate identity. The signer identity in C2PA manifests will show your organization name from the certificate.

## Option 2: Register Raw Public Key

For simpler setups or testing, you can register a raw public key without CA validation.

### Step 1: Generate Key Pair

```bash
# Generate Ed25519 key pair
openssl genpkey -algorithm Ed25519 -out private_key.pem
openssl pkey -in private_key.pem -pubout -out public_key.pem
```

### Step 2: Register Public Key

```bash
curl -X POST "https://api.encypherai.com/api/v1/byok/public-keys" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "public_key_pem": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----",
    "key_name": "My Signing Key",
    "key_algorithm": "Ed25519"
  }'
```

## API Reference

### List Trusted CAs

```
GET /api/v1/byok/trusted-cas
```

Returns the list of C2PA-trusted Certificate Authorities.

### Upload Certificate

```
POST /api/v1/byok/certificates
```

Upload a CA-signed X.509 certificate. Requires Business tier or higher.

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `certificate_pem` | string | Yes | PEM-encoded X.509 certificate |
| `chain_pem` | string | No | PEM-encoded intermediate certificates |
| `key_name` | string | No | Friendly name for the certificate |

### Register Public Key

```
POST /api/v1/byok/public-keys
```

Register a raw public key (no CA validation).

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `public_key_pem` | string | Yes | PEM-encoded public key |
| `key_name` | string | No | Friendly name |
| `key_algorithm` | string | No | Algorithm (Ed25519, RSA-2048, RSA-4096) |

### List Public Keys

```
GET /api/v1/byok/public-keys
```

List all registered public keys for your organization.

### Revoke Public Key

```
DELETE /api/v1/byok/public-keys/{key_id}?reason=...
```

Revoke a registered public key. Revoked keys cannot be used for verification.

## Security Best Practices

1. **Protect Private Keys** - Never share or expose your private key
2. **Use Hardware Security Modules (HSM)** - For production, store keys in HSM
3. **Rotate Certificates** - Plan for certificate renewal before expiry
4. **Monitor Usage** - Review verification logs for anomalies
5. **Revoke Compromised Keys** - Immediately revoke if key is compromised

## WordPress Plugin Integration

The WordPress Provenance Plugin can use BYOK certificates:

1. Upload your certificate via the API (above)
2. The plugin will automatically use your organization's certificate for signing
3. Verification will show your organization identity

## Troubleshooting

### "Certificate validation failed"

- Ensure your certificate chains to a C2PA-trusted root CA
- Include all intermediate certificates in `chain_pem`
- Check certificate hasn't expired

### "BYOK requires Business tier"

- Upgrade to Business tier or higher to use BYOK features

### "Public key already registered"

- The same public key cannot be registered twice
- Use a different key or revoke the existing one

## Support

For assistance with BYOK setup:
- Email: support@encypherai.com
- Documentation: https://docs.encypherai.com
