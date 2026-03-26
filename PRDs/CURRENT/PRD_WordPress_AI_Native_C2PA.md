# PRD: WordPress AI Plugin -- Native C2PA Signing

**Status:** In Progress
**Team:** TEAM_281
**Current Goal:** Replace the custom JSON manifest format in PR #294 with spec-compliant C2PA signing (JUMBF/COSE/ES256), address Jeff's review comments, and ship for WordPress 7.0.

## Overview

PR #294 on the official WordPress AI canonical plugin implements content provenance as an experiment, but uses a custom JSON manifest format that no C2PA verifier can parse. This PRD covers replacing that custom format with native PHP C2PA signing -- minimal JUMBF containers, COSE_Sign1 envelopes, ES256 signatures -- so that every WordPress site using this plugin produces content verifiable by c2patool, Content Credentials, and any standard C2PA tool. The Connected signer tier pre-populates the Encypher API as the default backend, creating the primary warm lead funnel from WordPress's 45% web market share.

## Objectives

- Produce spec-compliant C2PA 2.3 manifests that pass conformance validation (c2patool, Content Credentials)
- Use ES256 (ECDSA P-256) signing for SSL.com / DigiCert C2PA certificate compatibility
- Document-level manifests only -- no sentence-level granularity (commercial moat)
- Zero external PHP dependencies beyond the built-in openssl extension
- Pre-populate Connected signer tier with Encypher API URL and free tier CTA
- Fix .well-known/c2pa endpoint to use actual C2PA spec field names
- Address Jeff's review comments on PR #294
- Rebase, move out of draft, target WordPress 7.0 inclusion
- Extract CDN workers from PR #302 scope into standalone repo

## Tasks

### Epic 1: C2PA Manifest Infrastructure (PHP)

- [ ] 1.1 Implement minimal JUMBF box writer (ISO 19566-5)
  - [ ] 1.1.1 Superbox (type `jumb`) with description box (type `jumd`) and content box
  - [ ] 1.1.2 C2PA manifest store superbox (`c2pa`) containing a single manifest
  - [ ] 1.1.3 Claim superbox with assertion store, claim body, and signature boxes
  - [ ] 1.1.4 Unit tests: round-trip box serialization, validate output against known-good JUMBF bytes
- [ ] 1.2 Implement minimal CBOR encoder for COSE structures
  - [ ] 1.2.1 Evaluate `spomky-labs/cbor-php` (pure PHP, no C extensions) vs hand-rolled minimal encoder
  - [ ] 1.2.2 If hand-rolled: encode maps, byte strings, integers, text strings, arrays, tagged values (enough for COSE)
  - [ ] 1.2.3 Unit tests: encode/decode round-trip for each CBOR type used
- [ ] 1.3 Implement COSE_Sign1 builder
  - [ ] 1.3.1 Protected header: `{1: -7}` (alg: ES256)
  - [ ] 1.3.2 Unprotected header: certificate chain (`x5chain`, label 33)
  - [ ] 1.3.3 Payload: serialized claim bytes
  - [ ] 1.3.4 Signature: ECDSA P-256 via PHP `openssl_sign()` with `OPENSSL_ALGO_SHA256` over `Sig_structure1`
  - [ ] 1.3.5 Unit tests: verify produced COSE_Sign1 structure with known test vectors

### Epic 2: C2PA Claim Builder

- [ ] 2.1 Build C2PA claim structure per spec
  - [ ] 2.1.1 `c2pa.actions` assertion: `c2pa.created` action with `digitalSourceType`
  - [ ] 2.1.2 `c2pa.hash.data` assertion: SHA-256 hash binding to content
  - [ ] 2.1.3 `c2pa.soft_binding` assertion referencing the text embedding method (A.7 variation selectors)
  - [ ] 2.1.4 Claim generator field: `WordPress/AI Content Provenance Experiment`
  - [ ] 2.1.5 Claim signature reference pointing to the COSE_Sign1 box
- [ ] 2.2 Assertion store serialization into JUMBF content boxes
- [ ] 2.3 Integration test: build complete manifest, verify parseable by c2patool (if available in CI) or by manual hex inspection against spec structure

### Epic 3: ES256 Key Management

- [ ] 3.1 Replace RSA-2048 key generation with ECDSA P-256
  - [ ] 3.1.1 Local tier: generate EC P-256 keypair via `openssl_pkey_new()` with `ec` / `prime256v1` curve
  - [ ] 3.1.2 Store keypair in WordPress options (existing storage pattern)
  - [ ] 3.1.3 Generate self-signed X.509 certificate for the local keypair (needed for COSE x5chain)
- [ ] 3.2 BYOK tier: accept PEM-encoded EC or RSA private key + certificate chain
  - [ ] 3.2.1 Validate certificate has C2PA claim signing EKU (OID 1.3.6.1.4.1.62558.2.1) -- warn if missing but don't block
  - [ ] 3.2.2 Validate key algorithm is ES256, ES384, or RSA (not Ed25519 -- incompatible with C2PA trust list CAs)
- [ ] 3.3 Unit tests: key generation, self-signed cert generation, BYOK validation

### Epic 4: Update Signing Tiers

- [ ] 4.1 Refactor `Local_Signer` to produce JUMBF/COSE manifests with ES256
  - [ ] 4.1.1 Replace `openssl_sign(..., OPENSSL_ALGO_SHA256)` RSA path with EC signing
  - [ ] 4.1.2 Build full C2PA manifest store using Epic 1 + Epic 2 components
  - [ ] 4.1.3 Return manifest bytes (not JSON string)
- [ ] 4.2 Refactor `Connected_Signer` for Encypher API integration
  - [ ] 4.2.1 Pre-populate service URL with Encypher API endpoint (e.g., `https://api.encypher.com/v1/c2pa/sign`)
  - [ ] 4.2.2 Add "Get your free API key at encypher.com" helper text in settings UI
  - [ ] 4.2.3 POST content to Connected endpoint, receive JUMBF manifest bytes back
  - [ ] 4.2.4 Display trust tier difference in settings: "Local: self-signed (untrusted by verifiers) | Connected: Encypher-issued certificate (C2PA trust list verified)"
- [ ] 4.3 Refactor `BYOK_Signer` for CA-issued certificates
  - [ ] 4.3.1 Load publisher's private key + certificate chain from settings
  - [ ] 4.3.2 Build COSE_Sign1 with full certificate chain in x5chain
  - [ ] 4.3.3 Move to advanced settings tab (this persona reaches us through enterprise sales, not plugin discovery)
- [ ] 4.4 Integration tests: each tier produces a valid C2PA manifest store

### Epic 5: Update Embedding Layer

- [ ] 5.1 Update `Unicode_Embedder` to wrap JUMBF bytes instead of JSON
  - [ ] 5.1.1 Keep the C2PA A.7 variation selector encoding (this part is already close to spec)
  - [ ] 5.1.2 Replace JSON payload with raw JUMBF manifest store bytes
  - [ ] 5.1.3 Verify `C2PATXT\0` magic + version + length header is correct per A.7
- [ ] 5.2 Update extraction/verification to parse JUMBF from decoded bytes
- [ ] 5.3 Integration test: embed manifest in text, extract, verify JUMBF parses correctly

### Epic 6: Fix .well-known/c2pa Endpoint

- [ ] 6.1 Replace custom field names with C2PA spec fields
  - [ ] 6.1.1 Use spec-defined fields: `c2pa_version`, `publisher`, `trust_anchors`, `tsa_urls`
  - [ ] 6.1.2 Remove custom fields: `verify_url`, `supported_tiers`, `active_tier`
  - [ ] 6.1.3 Fix conflicting `@context` URIs (two different strings in current PR)
- [ ] 6.2 Remove dead code: `Well_Known_Handler.php` class is unused (inline handler in Content_Provenance.php duplicates it)
- [ ] 6.3 Unit test: validate JSON output matches C2PA well-known schema

### Epic 7: Verification Path

- [ ] 7.1 Update `extract_and_verify()` to validate COSE_Sign1 signatures
  - [ ] 7.1.1 Decode JUMBF manifest store from variation selector bytes
  - [ ] 7.1.2 Extract COSE_Sign1 structure, verify ES256 signature against embedded certificate
  - [ ] 7.1.3 Verify content hash binding (SHA-256 of stripped text matches `c2pa.hash.data` assertion)
- [ ] 7.2 Update Gutenberg sidebar badge states
  - [ ] 7.2.1 "Verified (trusted)" -- manifest valid, certificate chains to C2PA trust list CA
  - [ ] 7.2.2 "Verified (self-signed)" -- manifest valid, self-signed certificate (Local tier)
  - [ ] 7.2.3 "Unverified" -- no manifest found
  - [ ] 7.2.4 "Tampered" -- manifest found but hash or signature check fails
- [ ] 7.3 Update REST API verify endpoint to return structured verification result
- [ ] 7.4 Integration tests for each badge state

### Epic 8: Address Jeff's Review Comments + PR Hygiene

- [ ] 8.1 Pull and review Jeff's comments on PR #294
- [ ] 8.2 Address each comment (track individually once reviewed)
- [ ] 8.3 Rebase PR #294 onto current `develop`
- [ ] 8.4 Run full test suite: PHPUnit integration tests, PHPStan level 8, PHP 7.4-8.4 compat
- [ ] 8.5 Move PR out of draft status
- [ ] 8.6 Write clear PR description grounding the contribution in C2PA 2.3 publication (Jan 8, 2026) and conformance program alignment

### Epic 9: PR #302 Scope Extraction

- [ ] 9.1 Extract CDN worker templates (Cloudflare, Lambda@Edge, Fastly) from PR #302
- [ ] 9.2 Image Provenance core (upload signing, C2PA-Manifest-URL headers, REST endpoints) remains in PR #302 scope
- [ ] 9.3 Hold PR #302 submission until PR #294 has merged or has clear review consensus (per Anne's guidance)

## Success Criteria

- [ ] Local tier manifest passes `c2patool manifest <file>` validation (if c2patool supports text extraction, otherwise hex-level JUMBF structure validation)
- [ ] Content Credentials viewer can parse and display the manifest from signed WordPress content
- [ ] Connected tier pre-populates Encypher API URL -- admin can sign up and start signing in under 2 minutes
- [ ] BYOK tier accepts SSL.com C2PA certificate and produces trusted manifests
- [ ] .well-known/c2pa endpoint returns spec-compliant discovery document
- [ ] All existing PHPUnit tests pass + new tests for JUMBF/COSE/ES256 components
- [ ] PHPStan level 8 clean, PHP 7.4-8.4 compatible
- [ ] PR #294 moved out of draft with Jeff's comments addressed
- [ ] Zero external Composer dependencies (openssl extension only)

## Design Decisions Log

| Decision | Choice | Rationale |
|---|---|---|
| Signing algorithm | ES256 (ECDSA P-256) | SSL.com and DigiCert C2PA certs are RSA/EC only. No trust list CA issues Ed25519. ES256 is C2PA-approved and PHP openssl-native. |
| Manifest format | JUMBF (ISO 19566-5) | C2PA spec requires it. Custom JSON is not parseable by any C2PA verifier. |
| Signing envelope | COSE_Sign1 | C2PA spec requires COSE. Raw openssl_sign() is not interoperable. |
| Granularity | Document-level only | Sentence-level Merkle trees are Encypher's commercial moat (patent-pending ENC0100). |
| CBOR encoding | Evaluate library vs hand-roll | Prefer hand-roll if subset is small enough to avoid Composer dependency. Decision in 1.2.1. |
| Connected signer default | Encypher API pre-populated | Primary warm lead funnel. Trust gap (self-signed vs CA-issued) is the conversion trigger. |
| BYOK tier placement | Advanced settings tab | BYOK persona is enterprise, not plugin discovery. Reduce settings UI noise for typical publisher. |
| CDN workers | Extract to separate repo | Wrong scope for WordPress plugin PR. CDN infra reviewed by DevOps, not WP maintainers. Protects enterprise feature IP. |
| PR strategy | Ship #294 first, hold #302 | Per Anne McCarthy's guidance. Build reviewer trust before expanding scope. |

## Completion Notes

(To be filled on completion)
