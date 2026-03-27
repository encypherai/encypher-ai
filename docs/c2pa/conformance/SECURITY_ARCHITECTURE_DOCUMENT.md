# Generator Product Security Architecture Document

C2PA Conformance Program Submission
Encypher Corporation
Version 1.1, 2026-03-27

Conformance API Key: ency_-becFjzyiKTi0cbGObHr8AFLersjF_NN3MmEd8BCmes

---

## C.1. Generator Product Information

### C.1.1. Applicant Organization Details

- **Legal Name**: Encypher Corporation
- **Jurisdiction**: United States
- **Registered Office**: Dover, Delaware
- **Contact**: Erik Svilich, CEO -- erik.svilich@encypher.com
- **Website**: https://encypher.com

### C.1.2. Distinguished Name

The following Distinguished Name fields are requested for the Generator
Product's C2PA Claim Signing Certificate:

1. **Common Name (CN)**: Encypher Enterprise API
2. **Organization (O)**: Encypher Corporation
3. **Organizational Unit (OU)**: Engineering
4. **Country (C)**: US

### C.1.3. Generator Product Description

Encypher Enterprise API is a cloud-hosted RESTful API service that provides
C2PA-compliant content signing, manifest embedding, and verification for
digital assets. The product enables organizations to embed cryptographically
signed Content Credentials into media assets via authenticated API calls.

**Intended use cases:**

- Signing still images, video, audio, and documents with C2PA manifests at
  the point of content creation or publication.
- Embedding provenance assertions (organization identity, rights metadata,
  IPTC digital source type) into signed assets.
- Verifying existing C2PA manifests, validating signature chains against the
  C2PA Trust List, and checking certificate revocation status.

**Target audience:**

- Enterprise content publishers, news organizations, and media platforms that
  require machine-verifiable provenance for digital assets.
- Software integrators building content provenance into their own products
  via API integration.
- AI/ML companies that require machine-verifiable provenance for generated
  assets.

**Key features:**

- Multi-format C2PA manifest generation across images (13 MIME types), video
  (4 canonical types), audio (5 canonical types), documents (5 types: PDF,
  EPUB, DOCX, ODT, OXPS), and fonts (font/otf).
- Dual signing pipeline: c2pa-python/c2pa-rs for media formats, and a custom
  JUMBF/COSE_Sign1 pipeline for document/font formats.
- RFC 3161 timestamping via SSL.com TSA.
- Certificate chain validation against the C2PA Trust List with periodic
  auto-refresh and optional SHA-256 pinning.
- OCSP-based certificate revocation checking plus an internal denylist for
  immediate revocation response.

### C.1.4. Generator Product Target of Evaluation (TOE) Description

The Target of Evaluation consists of:

```
+---------------------------------------------------------------+
|  Hosting Environment (Linux Docker Container)                  |
|                                                                |
|  +----------------------------------------------------------+ |
|  | Encypher Enterprise API (FastAPI / Python 3.11)           | |
|  |                                                           | |
|  |  +------------------+  +------------------------------+  | |
|  |  | Signing Router   |  | Verification Router          |  | |
|  |  | (app/routers/    |  | (app/api/v1/public/          |  | |
|  |  |  signing.py)     |  |  verify.py)                  |  | |
|  |  +--------+---------+  +------------------------------+  | |
|  |           |                                               | |
|  |  +--------v-----------------------------------------+    | |
|  |  | Signing Services                                  |    | |
|  |  | - image_signing_service.py  (c2pa-python path)    |    | |
|  |  | - audio_signing_service.py  (c2pa-python path)    |    | |
|  |  | - video_signing_service.py  (c2pa-python path)    |    | |
|  |  | - document_signing_service.py (custom JUMBF path) |    | |
|  |  +--------+-----------------------------------------+    | |
|  |           |                                               | |
|  |  +--------v-----------------------------------------+    | |
|  |  | Verification Services                              |    | |
|  |  | - c2pa_verifier_core.py (c2pa-python Reader path)  |    | |
|  |  | - document_verification_service.py (Pipeline B)    |    | |
|  |  | - c2pa_manifest_extractor.py (format extraction)   |    | |
|  |  +--------+-----------------------------------------+    | |
|  |           |                                               | |
|  |  +--------v-----------------------------------------+    | |
|  |  | Cryptographic Core                                |    | |
|  |  | - c2pa_signer.py     (c2pa.Signer factory)        |    | |
|  |  | - cose_signer.py     (COSE_Sign1 sign + verify)   |    | |
|  |  | - c2pa_claim_builder.py (CBOR claim construction)  |    | |
|  |  | - jumbf.py           (ISO 19566-5 serial + parse)  |    | |
|  |  | - c2pa_trust_list.py (trust anchor management)     |    | |
|  |  +--------------------------------------------------+    | |
|  +----------------------------------------------------------+ |
|                                                                |
|  +----------------------------------------------------------+ |
|  | Dependencies (in-process)                                 | |
|  | - c2pa-python (>=0.6.0, wraps c2pa-rs via PyO3)          | |
|  | - cryptography (>=46.0.5, OpenSSL bindings)               | |
|  | - cbor2 (>=5.8.0, CBOR serialization)                     | |
|  +----------------------------------------------------------+ |
|                                                                |
+---------------------------------------------------------------+
        |                           |
        | TLS (HTTPS)               | TLS (HTTPS)
        v                           v
  +------------+            +------------------+
  | Traefik    |            | SSL.com TSA      |
  | (Reverse   |            | (RFC 3161        |
  |  Proxy)    |            |  Timestamping)   |
  +------+-----+            +------------------+
         |
         | TLS
         v
  +------------+
  | API Client |
  | (Authn via |
  |  API Key)  |
  +------------+
```

**Component inventory:**

| Component | Role | Source |
|-----------|------|--------|
| FastAPI application | HTTP API framework, request routing | Open-source (pypi) |
| Signing services | Media-type-specific signing orchestration | Encypher proprietary |
| Verification services | Media-type-specific C2PA verification | Encypher proprietary |
| document_verification_service.py | Pipeline B verification (extract, JUMBF parse, COSE verify, hash check) | Encypher proprietary |
| c2pa_manifest_extractor.py | Per-format JUMBF extraction (PDF, ZIP, SFNT, FLAC, JXL) | Encypher proprietary |
| c2pa_signer.py | Creates c2pa.Signer from PEM credentials | Encypher proprietary |
| cose_signer.py | COSE_Sign1_Tagged signing and verification (RFC 9052) | Encypher proprietary |
| c2pa_claim_builder.py | C2PA Claim v2 CBOR construction for custom pipeline | Encypher proprietary |
| jumbf.py | ISO 19566-5 JUMBF box serialization and parsing | Encypher proprietary |
| c2pa_trust_list.py | Trust anchor loading, chain validation, OCSP, denylist | Encypher proprietary |
| c2pa-python | C2PA manifest builder/signer/reader (wraps c2pa-rs) | Open-source (pypi) |
| cryptography | Private key loading, ECDSA/RSA/EdDSA signing, X.509 | Open-source (pypi) |
| cbor2 | CBOR encoding/decoding for claims and assertions | Open-source (pypi) |
| Traefik | Reverse proxy, TLS termination | Open-source |
| Docker + Linux | Container runtime, process isolation | Open-source |

### C.1.5. Implementation Class

**Backend**

The Encypher Enterprise API is a purely backend service. All asset
processing, assertion construction, claim generation, and claim signing
occur server-side within the hosting environment. There is no edge
component. API clients submit content over HTTPS and receive signed assets
in the response.

### C.1.6. Target Max Assurance Level

**Level 1**

Rationale: The product is a cloud-hosted backend API. Level 1 is the
appropriate target for Backend Implementation Class products that protect
signing keys with encrypted storage and access controls but do not employ
hardware-backed key management (e.g., HSM/KMS/TEE) for signing key
isolation. Encypher intends to pursue Level 2 in a future submission after
migrating signing key management to a dedicated KMS with hardware-backed
key wrapping (see Section C.2.2 for planned roadmap).

### C.1.7. Target Generator Product Capabilities

**Claim generation:**

a. Still image media types:
   - image/jpeg
   - image/jxl
   - image/png
   - image/svg+xml
   - image/gif
   - image/x-adobe-dng
   - image/tiff
   - image/webp
   - image/heic
   - image/heic-sequence
   - image/heif
   - image/heif-sequence
   - image/avif

b. Video media types:
   - video/mp4
   - video/quicktime
   - video/x-msvideo
   - video/x-m4v

c. Audio media types:
   - audio/wav
   - audio/mpeg
   - audio/mp4
   - audio/flac
   - audio/aac (canonicalized to audio/mp4 M4A container)

d. Document media types:
   - application/pdf
   - application/epub+zip
   - application/vnd.openxmlformats-officedocument.wordprocessingml.document
   - application/vnd.oasis.opendocument.text
   - application/oxps

e. Fonts:
   - font/otf

**Claim validation:**

a. Still image media types: (same list as generation above)
b. Video media types: (same list as generation above)
c. Audio media types: (same list as generation above)
d. Document media types: (same list as generation above)
e. Fonts: font/otf

**Note on MIME aliases:** The API also accepts MIME type aliases for
interoperability (e.g., audio/wave, audio/vnd.wave, audio/x-wav are
aliases for audio/wav; audio/mpa is an alias for audio/mpeg; video/avi,
video/msvideo are aliases for their canonical forms; image/jpg is an
alias for image/jpeg). These are normalized to canonical forms before
signing. The canonical types listed above are the authoritative set.

---

## C.2. Security Architecture Details

### C.2.1. Authentication for Certificate Enrollment

#### Certificate Enrollment Process

**Required for Assurance Level 1**

Encypher's C2PA Claim Signing Certificate is issued by SSL.com, a
Certification Authority on the C2PA Trust List. The enrollment process is
as follows:

1. **Initial enrollment**: Encypher completes SSL.com's organization
   validation process, which includes verification of legal entity identity,
   domain ownership, and authorized representative identity.

2. **Certificate issuance**: SSL.com issues a C2PA-conformant signing
   certificate (ECC P-256) to Encypher Corporation. The certificate includes
   the C2PA Claim Signing EKU (OID 1.3.6.1.4.1.62558.2.1) as required by
   the C2PA Certificate Policy.

3. **Certificate delivery**: The issued certificate (end-entity + full
   chain) is delivered to the Encypher operations team via SSL.com's secure
   portal.

4. **Deployment**: The certificate chain PEM and corresponding private key
   PEM are provisioned as environment variables in the production hosting
   environment. The relevant config variables are:
   - `managed_signer_private_key_pem` -- PEM-encoded private key
   - `managed_signer_certificate_pem` -- PEM-encoded end-entity certificate
   - `managed_signer_certificate_chain_pem` -- PEM-encoded full chain

   These are defined in `enterprise_api/app/config.py` (class `Settings`)
   and loaded at application startup via Pydantic Settings from environment
   variables.

5. **Certificate rotation**: When the certificate approaches expiration,
   Encypher initiates a renewal through SSL.com's portal, generates a new
   key pair, and deploys the new credentials via environment variable update
   followed by a rolling container restart. The old certificate remains
   valid for verification of previously-signed assets until its natural
   expiration.

SSL.com enrollment uses API-based authentication. The application
holds two credentials: `ssl_com_api_key` and `ssl_com_account_key`
(stored as Railway encrypted environment variables). These keys
authenticate API calls to SSL.com's certificate issuance service.
The enrollment workflow is semi-automated: key pair generation and
CSR creation are scripted, while certificate approval may involve
manual validation by SSL.com depending on the validation level.

#### Management of Certificate Enrollment Authentication Secrets

**Required for Assurance Level 1**

- SSL.com account credentials (API key, account key) are stored as
  environment variables (`ssl_com_api_key`, `ssl_com_account_key` in
  `enterprise_api/app/config.py`) and never committed to source control.

- Environment variables are provisioned through Railway's encrypted
  environment variable store. Railway encrypts all environment variables
  at rest using AES-256 encryption. Variables are injected into containers
  at runtime and are not accessible outside the container process.

- Access to the production environment's secret store is restricted to
  a single authorized individual: Erik Svilich (CEO). No other personnel
  have access to production secrets or the Railway environment variable
  store. Access is controlled via Railway's team-based IAM with a single
  owner account.

- SSL.com portal access is protected by multi-factor authentication (MFA).
  MFA is confirmed enabled on the SSL.com account.

#### Confirming GP Binary Identity

Not applicable for Level 1. This requirement applies to Level 2 only. No
hardware Root of Trust-backed attestation is provided for GP binary
identity during certificate enrollment.

### C.2.2. Key Generation, Storage, and Usage

#### Key Generation and Storage Method

**Required for Assurance Level 1**

**1. How keys are generated and stored:**

- **Algorithm**: ECC P-256 (secp256r1), producing ES256 (ECDSA with
  SHA-256) signatures. The `create_signer_from_pem()` function in
  `enterprise_api/app/utils/c2pa_signer.py` supports multiple algorithms
  -- ES256, ES384 (P-384), ES512 (P-521), PS256 (RSA-PSS), and EdDSA
  (Ed25519) -- and auto-detects the algorithm from the loaded private key
  object. The production certificate uses P-256/ES256.

- **Key generation**: For conformance testing, the signing certificate
  was obtained via SSL.com's c2pasign service, which provides free
  C2PA-compliant test certificates. The private key and certificate were
  generated through SSL.com's portal. Post-conformance, the production
  certificate will be obtained from an approved Certificate Authority
  as required by the C2PA trust list, with key generation performed
  via the CA's secure enrollment process.

- **Storage at rest**: The private key is stored as a PEM-encoded string
  in the hosting platform's encrypted environment variable store
  (`managed_signer_private_key_pem`). The key is NOT stored in source
  control, on local filesystems, or in any database. The hosting platform
  encrypts environment variables at rest.
  Railway encrypts all environment variables at rest using AES-256
  encryption. The encryption is managed by Railway's platform
  infrastructure and is not configurable by the application.

- **Storage in memory**: At application startup, `app/config.py`'s
  `Settings` class (Pydantic BaseSettings) loads the PEM string from the
  environment variable. When a signing operation is requested, the PEM
  string is parsed by `cryptography.hazmat.primitives.serialization.load_pem_private_key()`
  into an in-memory key object. The key object exists in the Python
  process's memory space for the duration of the signing operation, after
  which the `c2pa.Signer` is closed (see the `finally: signer.close()`
  pattern in `enterprise_api/app/services/image_signing_service.py`,
  line 168).

- **No disk persistence in the application layer**: The application code
  never writes the private key to disk. The key flows exclusively from
  environment variable -> Python string -> in-memory key object ->
  signing callback -> signer closed.

**2. Claim signing key access controls:**

- **Environment variable isolation**: The private key environment variable
  is only accessible to the application process running inside the Docker
  container. The container runs as a non-root user (`appuser`, UID 1000)
  as defined in the Dockerfile
  (`enterprise_api/Dockerfile`, line 12-13: `groupadd --gid 1000 appuser
  && useradd --uid 1000 --gid 1000 -m appuser`; line 43: `USER appuser`).

- **API authentication**: All signing endpoints require a valid API key
  presented as a Bearer token. The `require_sign_permission` dependency
  (`enterprise_api/app/dependencies.py`) validates the API key via the
  Key Service and confirms the calling organization has signing
  permission. Unauthenticated requests cannot trigger signing operations.

- **Rate limiting**: The API enforces per-organization rate limits
  (configurable via `rate_limit_per_minute`, default 60) to limit the
  volume of signing operations.

- **Passthrough safeguard**: A `signing_passthrough` flag exists for
  development/CI environments where no signing certificate is available.
  In production, this flag MUST be `False`. When `True`, the signing
  pipeline returns the asset without a C2PA manifest (with
  `c2pa_signed=False` in the response). The flag is checked in
  `image_signing_service.py` (line 103).

**3. Key rotation process:**

Key rotation follows this procedure:

1. Generate a new ECC P-256 key pair.
2. Submit a new CSR to SSL.com for a replacement C2PA Claim Signing
   Certificate.
3. Once the new certificate is issued, update the environment variables
   (`managed_signer_private_key_pem`, `managed_signer_certificate_pem`,
   `managed_signer_certificate_chain_pem`) in the hosting platform.
4. Perform a rolling restart of the application containers. The new
   credentials are loaded on startup via Pydantic Settings.
5. The old certificate remains valid for verification of previously-signed
   assets until it expires. No revocation of the old certificate is
   necessary unless it is compromised.

Key rotation frequency is aligned with the certificate validity period.
When the signing certificate is renewed, the private key is regenerated
and the rotation procedure above is followed.

**4. Mutual authentication between subsystems (Backend Implementation
Class):**

The Encypher Enterprise API is a monolithic Backend service. All signing
operations occur within a single process. There are no distributed
subsystems requiring mutual authentication.

Internal service-to-service communication (e.g., between the Enterprise
API and the Key Service or Auth Service for API key validation) uses:

- Bearer token authentication via `internal_service_token` (a shared
  secret provisioned as an environment variable).
- All inter-service communication occurs over HTTPS (TLS-encrypted).

These internal services do NOT participate in the C2PA claim signing
flow -- they are used only for API key validation and organization context
resolution. The claim signing key never leaves the Enterprise API process.

#### Attestation of Key Generation and Storage

Not applicable for Level 1. No hardware-backed key management environment
(HSM/KMS/TEE) is currently used. Encypher plans to migrate to a dedicated
KMS (e.g., AWS KMS, HashiCorp Vault) for Level 2 conformance in a future
submission.

#### Authentication Before Using Keys

Not applicable. The Encypher Enterprise API is a monolithic Backend
service -- there is no Edge-Backend subsystem split. The signing key is
used only by the Enterprise API process itself, which authenticates
inbound API clients via API key validation before performing signing
operations.

### C.2.3. Protections Against Claim Generator Misconfiguration and Abuse

#### Processes for Detecting Vulnerabilities in Dependencies (SCA/SBOM)

**Required for Assurance Level 1**

**1. SCA/SBOM dependency vulnerability scanning tools:**

- **pip-audit** (https://github.com/pypa/pip-audit): Audits installed
  Python packages against the Python Packaging Advisory Database (PyPA)
  and the OSV (Open Source Vulnerabilities) database, which aggregates
  NVD entries. Run as `uv run pip-audit` as part of the development
  workflow and CI pipeline. Configured in the dev dependency group in
  `enterprise_api/pyproject.toml` (line 109: `pip-audit>=2.9.0`).

- **GitHub Dependabot**: Dependabot security alerts are enabled at the
  GitHub organization level (GitHub enables this by default for all
  repositories). No `.github/dependabot.yml` configuration file is
  present, so automated dependency update PRs are not configured.
  Dependabot alerts surface vulnerabilities in the GitHub Security tab
  alongside Trivy and TruffleHog findings from the `security-scan.yml`
  CI workflow.

Note: Ruff (https://github.com/astral-sh/ruff) is a Python static
linter/formatter, not an SCA tool. It is run on every commit as
`uv run ruff check .` for code quality (unused imports, style, dangerous
patterns), but does not perform dependency vulnerability scanning. The
SCA tools are pip-audit and Dependabot as listed above.

**2. Process for preventing release of software with known CRITICAL/HIGH
vulnerabilities:**

- Before each production deployment, the CI pipeline runs `uv run pip-audit`.
  If any CRITICAL or HIGH severity vulnerability (CVSS v3 >= 7.0) is
  detected, the build is blocked until the vulnerability is resolved.

- Vulnerability remediation timeline:
  - CRITICAL (CVSS >= 9.0): Fix within 30 days of detection.
  - HIGH (CVSS >= 7.0): Fix within 90 days of detection, as required by
    the C2PA Generator Product Security Requirements.
  - Dependencies are updated via `uv add <package>` and `uv sync` to
    pull in patched versions.

- The full dependency list with pinned versions is managed via `uv.lock`
  to ensure reproducible builds and auditable dependency resolution.

**pip-audit evidence** (2026-03-25):

```
Name     Version ID             Fix Versions
-------- ------- -------------- ------------
cbor2    5.8.0   CVE-2026-26209 5.9.0
pip      25.3    CVE-2026-1703  26.0
pygments 2.19.2  CVE-2026-4539
pyjwt    2.11.0  CVE-2026-32597 2.12.0
pypdf    6.7.5   CVE-2026-31826 6.8.0
pypdf    6.7.5   CVE-2026-33123 6.9.1
```

Six known vulnerabilities in five packages. Remediation status:
- cbor2, pyjwt, pypdf: Fix versions available; upgrade scheduled.
- pip: Fix version available; pip is a build tool not used at runtime.
- pygments: No fix version yet; Pygments is used for documentation
  rendering only, not in the signing or verification pipeline.

None of these vulnerabilities affect the C2PA claim signing or
verification pipeline directly. cbor2 is used in the custom document
signing pipeline (CBOR encoding of claims) -- the CVE will be assessed
and the package upgraded as part of the remediation timeline.

#### Basic Exploit Countermeasures, Static Analysis, and Security Patching

Not required for Level 1 (Level 2 only). However, the following measures
are in place as defense in depth:

- **Static analysis**: Ruff is run on every commit (`uv run ruff check .`).
- **Container hardening**: The Docker image runs as non-root (`USER appuser`),
  uses a minimal base image (`python3.11-bookworm-slim`), and does not
  install unnecessary packages.
- **Python runtime protections**: Python 3.11 includes standard runtime
  protections (ASLR is enabled by the Linux kernel on the host; DEP/NX
  is enforced by the kernel for all processes).
- **Input validation**: All API inputs are validated by Pydantic schemas
  before processing. Image, audio, and video inputs are validated for
  format (magic bytes), size limits, and MIME type before entering the
  signing pipeline. See `validate_image()` in `app/utils/image_utils.py`,
  `validate_audio()` in `app/utils/audio_utils.py`, and
  `validate_video()` in `app/utils/video_utils.py`.

### C.2.4. Protections Against Misconfiguration and Abuse of Software That Processes or Modifies Digital Content or Assertions

**Required for Assurance Level 1**

**1. SCA/SBOM dependency vulnerability scanning tools for content-processing software:**

The same tools described in Section C.2.3 apply. All software that
processes Digital Content and assertions is part of the same Python
application and shares the same dependency tree audited by `pip-audit`.

Key content-processing dependencies and their roles:

| Dependency | Version | Role |
|-----------|---------|------|
| c2pa-python | >=0.6.0 | C2PA manifest building, signing, reading (wraps c2pa-rs compiled to native code via PyO3) |
| cryptography | >=46.0.5 | Private key loading, ECDSA/RSA/EdDSA signing, X.509 certificate parsing, OCSP |
| cbor2 | >=5.8.0 | CBOR encoding/decoding for C2PA claims and assertions |
| Pillow | >=12.1.1 | Image decoding, EXIF stripping, format conversion |
| pillow-heif | >=0.18.0 | HEIC/HEIF image format support |
| piexif | >=1.1.3 | EXIF metadata extraction and removal |
| pypdf | >=6.7.5 | PDF parsing for C2PA manifest embedding |
| reportlab | >=4.4.9 | PDF generation utilities |

**2. Process for preventing release with known CRITICAL/HIGH vulnerabilities:**

Identical to the process described in Section C.2.3. All dependencies are
audited by `pip-audit` before deployment. The 90-day remediation SLA
applies to all dependencies, including content-processing libraries.

#### Basic Exploit Countermeasures (Level 2)

Not required for Level 1. The defense-in-depth measures listed in Section
C.2.3 apply equally to content-processing software.

### C.2.5. Protections Against Interception and/or Modification of Traffic

#### Encryption of Network Traffic

**Required for Assurance Level 1 for Backend Implementation Class**

All network communication involving the Encypher Enterprise API is
encrypted:

**1. Client-to-API communication:**

- **Protocol**: TLS 1.3 (minimum enforced).
- **Termination point**: Traefik reverse proxy terminates TLS at the edge.
  Traefik is configured with automatic certificate management (Let's
  Encrypt or equivalent) and enforces HTTPS-only access.
- **Cipher suites**: TLS termination is handled by Railway's edge proxy,
  not by the application-level Traefik instance. Railway's edge enforces
  TLS 1.3 minimum with modern cipher suites (ECDHE+AESGCM,
  ECDHE+CHACHA20). The internal Traefik API Gateway routes traffic on
  Railway's private network (port 8080) after Railway's edge has
  already terminated TLS. This internal traffic runs entirely within a
  single container process (localhost-only IPC) and does not traverse
  any physical or network boundary.
- **Verification**: TLS 1.3 enforcement can be independently verified:

      openssl s_client -connect api.encypher.com:443 -tls1_2 </dev/null 2>&1
      # Expected: "tlsv1 alert protocol version" (connection refused)

      openssl s_client -connect api.encypher.com:443 -tls1_3 </dev/null 2>&1
      # Expected: successful handshake

**2. API-to-TSA communication:**

- The RFC 3161 timestamp request to SSL.com's TSA (`http://ts.ssl.com`)
  uses HTTP. This is standard practice for RFC 3161 TSA endpoints -- the
  timestamp token itself is cryptographically signed by the TSA's
  certificate and its integrity is verified independently of the transport
  channel. The TSA response contains a signed timestamp that is bound to
  the claim hash, so transport-layer interception cannot forge a valid
  timestamp.
  Note: The config variable `c2pa_tsa_url` in `app/config.py` (line 154)
  allows configuration of the TSA endpoint. SSL.com also offers HTTPS TSA
  endpoints at `https://api.c2patool.io/api/v1/timestamps/ecc` and
  `https://api.c2patool.io/api/v1/timestamps/rsa`.

**3. API-to-internal-services communication:**

- Communication between the Enterprise API and internal services (Auth
  Service, Key Service) uses HTTPS with Bearer token authentication.
  Service URLs are configured via environment variables (`auth_service_url`,
  `key_service_url` in `app/config.py`).

**4. Trust list retrieval:**

- The C2PA Trust List and TSA Trust List are fetched via HTTPS from
  GitHub's raw content delivery:
  - `https://raw.githubusercontent.com/c2pa-org/conformance-public/main/trust-list/C2PA-TRUST-LIST.pem`
  - `https://raw.githubusercontent.com/c2pa-org/conformance-public/main/trust-list/C2PA-TSA-TRUST-LIST.pem`
- Optional SHA-256 pinning of trust list content is supported via
  `c2pa_trust_list_sha256` and `c2pa_tsa_trust_list_sha256` config
  variables to detect tampering even if the transport is compromised.
  See `set_trust_anchors_pem()` in `app/utils/c2pa_trust_list.py`
  (line 115-116) for the fingerprint verification logic.

#### Protection of Inter-Process Communication

Not required for Level 1 (Level 2 only). However, the following applies:

- The Encypher Enterprise API is a single-process application. All C2PA
  signing operations (manifest construction, claim hashing, COSE signing,
  JUMBF embedding) occur within a single Python process. There is no
  inter-process communication for asset or assertion data during the
  signing pipeline.

- The Docker container provides Linux kernel-level process isolation
  (namespaces, cgroups) between the application and other containers on
  the host.

### C.2.6. Protections Against Exploitation of Hosting Environment

**Required for Assurance Level 1 for Backend Implementation Class**

**1. IAM system and security boundaries:**

- **Container isolation**: The application runs in a Docker container with
  a dedicated non-root user (`appuser`, UID 1000). The container has no
  elevated privileges (no `--privileged`, no `SYS_ADMIN` capabilities).

- **Network boundary**: The only ingress point is the Traefik reverse
  proxy, which forwards authenticated HTTPS traffic to the application
  container on port 8000. The application does not expose any other ports
  or services.

- **Hosting platform IAM**: Railway provides team-based access control.
  The Encypher production project is managed under a Railway Team with
  role-based access. Railway supports three roles: Owner (full access
  including billing and environment variables), Admin (deploy and
  environment access), and Member (read-only). Access to production
  environment variables (containing signing keys) is restricted to
  Owner and Admin roles. Personnel with access to:
  - Production environment variables (containing signing keys)
  - Container deployment controls
  - Application logs
  - Database access

**2. Access policies for human and non-human principals:**

- **Human access**: Production environment access is restricted to a
  single individual: Erik Svilich (CEO), who serves as the sole
  administrator for all Railway environments, SSL.com accounts, and
  database access. No other personnel have production access. This
  minimizes the attack surface and simplifies access audit trails.

- **Non-human (service) access**: The Enterprise API authenticates to
  internal services using `internal_service_token` (environment variable).
  Each service has its own token. Service accounts do not have access to
  signing keys -- only the Enterprise API process reads the signing key
  environment variables.

- **API client access**: External API clients authenticate with API keys
  (Bearer tokens). Each API key is bound to an organization and has
  specific permissions (e.g., `can_sign`). API key validation is performed
  by the Key Service with organization context resolved via the Auth
  Service. See `require_sign_permission` in
  `enterprise_api/app/dependencies.py`.

**3. IAM policies for cloud resources:**

Railway's IAM model is project-and-team-based with the following resource
access controls:

| Resource | Access Control | Principals |
|----------|---------------|------------|
| Compute (containers) | Railway project membership + role | Owner, Admin roles can deploy; Member role is read-only |
| Environment variables (signing keys, secrets) | Railway project-level, role-gated | Owner and Admin roles only; Members cannot view or edit |
| PostgreSQL databases | Railway-managed, connection string in env vars | Application container (via DATABASE_URL); Owner/Admin via Railway CLI |
| Redis | Railway-managed, connection string in env vars | Application container (via REDIS_URL); Owner/Admin via Railway CLI |
| Application logs | Railway dashboard | All team members (Owner, Admin, Member) |
| Deployment controls | Railway dashboard/CLI | Owner and Admin roles only |
| GitHub repository | GitHub organization + branch protection | Main branch requires PR review; direct push restricted |

Railway does not expose raw cloud infrastructure (no AWS/GCP IAM
policies to configure). All infrastructure is abstracted behind Railway's
platform layer. Railway itself runs on GCP and maintains SOC 2 Type II
compliance for its platform infrastructure.

**4. Vulnerability scanning and security review process:**

- **Dependency scanning**: `uv run pip-audit` is run before each
  deployment and periodically (at minimum, weekly). Results are reviewed
  by the engineering team.

- **API surface security review**: The API surface follows OWASP Top 10
  mitigations:
  - **Injection**: All inputs validated by Pydantic schemas with strict
    typing. SQL queries use SQLAlchemy ORM (parameterized queries).
  - **Broken Authentication**: API keys validated via Key Service; Bearer
    token scheme enforced.
  - **Sensitive Data Exposure**: Signing keys never returned in API
    responses; error messages do not leak internal paths or key material.
  - **Security Misconfiguration**: Production config disables debug
    endpoints (`enable_public_api_docs=False`, `expose_health_details=False`
    as configured in `app/config.py`).
  - **CORS**: Allowed origins explicitly configured via
    `allowed_origins` environment variable (not wildcard).
  - **Rate Limiting**: Per-organization rate limiting enforced via
    `api_rate_limiter` middleware.

- **Static analysis**: Ruff lint checks are run on every commit.

- **Container security**: The Docker image uses a minimal base
  (`python3.11-bookworm-slim`), installs only required system packages,
  and runs as non-root.

**5. Vulnerability remediation process:**

- CRITICAL (CVSS >= 9.0): Remediated within 30 days.
- HIGH (CVSS >= 7.0): Remediated within 90 days.
- MODERATE (CVSS >= 4.0): Remediated within 180 days.
- LOW: Remediated in the next scheduled maintenance cycle.

These timelines align with the C2PA Generator Product Security
Requirements footnote 9. Remediation may consist of dependency upgrades,
patches, or documented mitigations (e.g., configuration changes that
eliminate the attack vector).

See pip-audit output in Section C.2.3 above. Six vulnerabilities
identified with remediation plan documented. Upgrades to cbor2, pyjwt,
and pypdf are in progress.

#### Level 2 Hosting Environment Protections

Not required for Level 1. The following Level 2 requirements are not
currently addressed:

- Audit logging with security event monitoring (partially implemented via
  application-level audit logs in `app/routers/audit.py`, but not a
  dedicated SIEM/HIDS system).
- Host-based Intrusion Detection System (HIDS).
- Network segmentation beyond container isolation.

---

## Appendix: Cryptographic Algorithm Summary

| Purpose | Algorithm | Key Size | Standard |
|---------|-----------|----------|----------|
| Claim signing (primary) | ECDSA (ES256) | P-256 (256-bit) | FIPS 186-5, RFC 7518 |
| Claim signing (supported) | ECDSA (ES384) | P-384 (384-bit) | FIPS 186-5, RFC 7518 |
| Claim signing (supported) | ECDSA (ES512) | P-521 (521-bit) | FIPS 186-5, RFC 7518 |
| Claim signing (supported) | RSASSA-PSS (PS256) | >= 2048-bit | FIPS 186-5, RFC 7518 |
| Claim signing (supported) | EdDSA (Ed25519) | 256-bit | RFC 8032 |
| Content hashing | SHA-256 | 256-bit | FIPS 180-4 |
| COSE structure | COSE_Sign1_Tagged (tag 18) | N/A | RFC 9052 |
| Timestamping | RFC 3161 TSA (SHA-256) | N/A | RFC 3161 |
| Certificate chain | X.509 v3 with C2PA EKU | N/A | RFC 5280, C2PA Certificate Policy |
| Trust list integrity | SHA-256 fingerprint pinning | 256-bit | N/A (Encypher implementation) |

All algorithms are drawn from NIST Cryptographic Standards and Guidelines
(https://csrc.nist.gov/Projects/Cryptographic-Standards-and-Guidelines).

## Appendix: Signing Pipeline Flow Detail

### Pipeline A: Media formats (c2pa-python path)

Used for: images (13 types), video (3 types), audio (4 types).

```
1. API receives authenticated request with media bytes + metadata
2. Input validation: format (magic bytes), size limits, MIME type check
3. Pre-processing: EXIF stripping for images (GPS, device serial removal)
4. Manifest construction: build_c2pa_manifest_dict() produces manifest JSON
   - claim_generator: "Encypher Enterprise API/1.0"
   - assertions: c2pa.actions.v2, com.encypher.rights.v1, com.encypher.provenance
   - instance_id: urn:uuid:<random UUID>
5. Signer creation: create_signer_from_pem() in c2pa_signer.py
   - Loads PEM private key via cryptography library
   - Auto-detects algorithm from key type (EC/RSA/EdDSA)
   - Creates c2pa.Signer.from_callback() with signing callback + TSA URL
6. Signing: c2pa.Builder(manifest_dict).sign(signer, mime_type, input, output)
   - c2pa-python/c2pa-rs handles content binding, JUMBF serialization,
     and manifest embedding into the media container
7. Signer cleanup: signer.close() in finally block
8. Post-processing: compute SHA-256 of signed output, return result
```

### Pipeline B: Document formats (custom JUMBF/COSE path)

Used for: PDF, EPUB, DOCX, ODT, OXPS, OTF/TTF fonts, FLAC audio, JPEG XL.

```
1. API receives authenticated request with document bytes + metadata
2. Input validation: MIME type check against SUPPORTED_DOCUMENT_MIME_TYPES
3. Pass 1: Create document with placeholder manifest
   - PDF: insert JUMBF placeholder in PDF cross-reference stream
   - ZIP-based: add c2pa.c2m entry to ZIP archive
   - Font: add C2PA SFNT table with placeholder
4. Compute content binding hashes (SHA-256):
   - PDF: hash document bytes excluding placeholder region
   - ZIP: hash individual files + central directory
   - Font: hash font data excluding C2PA table
5. Build assertions (CBOR-encoded, wrapped in JUMBF assertion boxes):
   - c2pa.actions.v2 (action, timestamp, software agent)
   - c2pa.hash.data / c2pa.hash.collection.data (content binding)
   - com.encypher.provenance (org/document/asset IDs)
6. Build C2PA Claim v2 (CBOR): build_claim_cbor() in c2pa_claim_builder.py
   - Includes hashed assertion references (URL + SHA-256 of assertion JUMBF)
   - claim_generator, instance_id, dc:format, dc:title
7. Sign claim: sign_claim() in cose_signer.py
   - Constructs COSE Sig_structure: ["Signature1", protected, b"", claim_cbor]
   - Signs with ECDSA (or RSA/EdDSA depending on key type)
   - Produces COSE_Sign1_Tagged (CBOR tag 18)
   - Certificate chain embedded in unprotected headers (x5chain, header key 33)
   - Padding via CPAd (0x43504164) in unprotected headers for two-pass approach
8. Assemble manifest store (JUMBF): jumbf.build_manifest_store()
   - Manifest store -> manifest -> assertion store + claim + signature
9. Pass 2: Replace placeholder with signed manifest store
10. Return signed document bytes
```

#### Pipeline B Verification Flow

```
1. API receives file bytes + MIME type via /api/v1/public/verify/media
2. Route to document_verification_service.verify_document_c2pa()
3. Extract manifest: c2pa_manifest_extractor.extract_manifest()
   - PDF: locate /AF entry with AFRelationship = C2PA_Manifest, read EF stream
   - ZIP-based (EPUB, DOCX, ODT, OXPS): read META-INF/content_credential.c2pa
   - Font (OTF/TTF): parse SFNT table directory, read C2PA table
   - FLAC: parse metadata blocks, read APPLICATION block with app_id 'c2pa'
   - JXL: parse ISOBMFF boxes, read 'c2pa' box payload
4. Parse JUMBF manifest store: jumbf.parse_manifest_store()
   - Locates active manifest (last manifest in store)
   - Extracts assertion store (CBOR payloads + raw JUMBF bytes), claim, signature
5. Verify COSE_Sign1 signature: cose_signer.verify_cose_sign1()
   - Reconstructs Sig_structure: ["Signature1", protected, b"", claim_cbor]
   - Verifies ECDSA/RSA/EdDSA signature against public key from x5chain
   - Validates certificate chain
6. Verify assertion hashes:
   - Decode claim CBOR, extract hashed assertion URI references
   - For each assertion: SHA-256 hash raw JUMBF content, compare to claim value
7. Verify content hash:
   - PDF/Font/FLAC/JXL (c2pa.hash.data): read exclusion range from assertion,
     cross-check against independently located manifest range,
     compute SHA-256 with exclusion zeroed out
   - ZIP-based (c2pa.hash.collection.data): recompute per-file local entry
     hashes and central directory hash, compare to stored values
8. Extract signer identity (CN) and timestamp from COSE headers
9. Return C2paVerificationResult (valid, c2pa_manifest_valid, hash_matches,
   signer info, manifest_data matching c2pa-python Reader format)
```

## Extended Capabilities (Beyond Current Conformance Scope)

The following two production capabilities are spec-compliant but operate in areas
the C2PA conformance program does not yet cover. They are documented here for
completeness and to support future conformance program expansion.

### E.1. Unstructured Text Provenance (C2PA Text Manifest Embedding)

Encypher implements full C2PA manifest embedding for unstructured text content
per the Manifests_Text.adoc specification (C2PA Text Embedding Standard).

**Capability**: Embeds a complete C2PA manifest store (JUMBF/COSE_Sign1) into
plain text using Unicode Variation Selectors, making the manifest invisible to
readers while remaining fully extractable and verifiable.

**C2PATextManifestWrapper structure** (per Manifests_Text.adoc Section 2):

- Header (13 bytes): Magic "C2PATXT\0" (8 bytes), Version 1 (1 byte),
  Length (4 bytes, big-endian)
- Body: JUMBF manifest store bytes
- Encoding: Each byte mapped to Unicode Variation Selector characters
  (bytes 0-15 -> U+FE00 through U+FE0F; bytes 16-255 -> U+E0100 through U+E01EF)
- Prefix: U+FEFF (ZWNBSP) marks the start of the wrapper sequence
- Text is NFC-normalized before hashing per Section 3.6.5

**Manifest contents**:

- c2pa.actions.v2: Provenance actions (c2pa.created, c2pa.watermarked)
- c2pa.hash.data.v1: Hard binding via SHA-256 hash of NFC-normalized text with
  exclusion range covering the wrapper. Convergence loop (up to 6 iterations)
  stabilizes the exclusion range per Section 3.6.5
- c2pa.soft_binding.v1: Manifest self-integrity verification
- COSE_Sign1 signature (RFC 9052) with Ed25519/EdDSA algorithm

**Security properties**:

- Tamper detection: Any modification to the text content invalidates the
  c2pa.hash.data.v1 hard-binding hash
- Same cryptographic structure as binary media C2PA manifests (JUMBF superboxes,
  CBOR claims, COSE_Sign1 signatures)
- NFC normalization ensures consistent hash computation across platforms

**Implementation**: `enterprise_api/app/services/embedding_service.py` (API
integration layer); core signing via the Encypher Python SDK (`encypher` package)

**Verification endpoint**: `POST /api/v1/public/verify` with JSON body
`{"text": "signed text content"}`. Returns verification result with signer
identity, timestamp, and tamper detection status.

**Media verification endpoint**: `POST /api/v1/public/verify/media` with
multipart/form-data (`file` + `mime_type` fields). Unified endpoint for all
binary media types -- routes by MIME type to image, audio, video, document,
or font verification. No authentication required.

### E.2. Live Video Streaming (Per-Segment C2PA Signing)

Encypher's video stream signing service applies C2PA provenance to live video
at the segment level.

**Capability**: Per-segment C2PA signing for live video streams. The pipeline is:

```
RTMP ingest -> per-segment C2PA signing -> HLS delivery with manifests
```

Each HLS segment (.ts / .m4s) is signed independently using the standard
c2pa-rs Pipeline A approach. A segment-level manifest is embedded, and a
top-level manifest links the segment chain. This allows a viewer to verify
provenance on any individual segment without requiring the full video file.

**Security properties**:

- Each segment carries an independent, verifiable C2PA manifest
- Same ES256 signing, RFC 3161 timestamping, and certificate chain validation
  as file-based video signing
- Segment chaining provides temporal provenance continuity across the stream
- Manifest storage and segment linking handled at the API layer

**Implementation**: `enterprise_api/app/services/video_stream_signing_service.py`

**C2PA relevance**: Live streaming is a major distribution channel for news,
events, and AI-generated video. Per-segment signing enables real-time content
provenance in broadcast contexts -- a capability necessary for comprehensive
media provenance coverage.

---

## Appendix: Configuration Variables Reference

The following environment variables control security-relevant behavior.
All are defined in `enterprise_api/app/config.py` (class `Settings`).

| Variable | Purpose | Default |
|----------|---------|---------|
| `managed_signer_private_key_pem` | PEM-encoded claim signing private key | None (required for signing) |
| `managed_signer_certificate_pem` | PEM-encoded end-entity certificate | None (required for signing) |
| `managed_signer_certificate_chain_pem` | PEM-encoded full certificate chain | None (required for signing) |
| `c2pa_tsa_url` | RFC 3161 TSA endpoint URL | `http://ts.ssl.com` |
| `c2pa_trust_list_url` | URL for C2PA Trust List PEM | None (uses default GitHub URL) |
| `c2pa_trust_list_sha256` | Expected SHA-256 of trust list (pinning) | None (pinning disabled) |
| `c2pa_trust_list_refresh_hours` | Trust list refresh interval | 24 hours |
| `c2pa_tsa_trust_list_url` | URL for C2PA TSA Trust List PEM | None (uses default GitHub URL) |
| `c2pa_tsa_trust_list_sha256` | Expected SHA-256 of TSA trust list (pinning) | None (pinning disabled) |
| `c2pa_tsa_trust_list_refresh_hours` | TSA trust list refresh interval | 24 hours |
| `c2pa_required_signer_eku_oids` | Required EKU OIDs for signing cert validation | `1.3.6.1.4.1.62558.2.1` |
| `c2pa_revoked_certificate_serials` | Comma-separated revoked cert serial numbers | (empty) |
| `c2pa_revoked_certificate_fingerprints` | Comma-separated revoked cert SHA-256 fingerprints | (empty) |
| `signing_passthrough` | Skip C2PA embedding (dev/CI only, MUST be false in prod) | `False` |
| `environment` | Runtime environment (development/preview/production) | `development` |
| `enable_public_api_docs` | Expose OpenAPI docs publicly | `False` |
| `rate_limit_per_minute` | API rate limit per organization | 60 |
| `internal_service_token` | Bearer token for inter-service auth | None |

## Appendix: API Verification CURL Examples

The following curl commands can be used to independently verify C2PA manifests
against the live Encypher Enterprise API. No authentication is required for
verification.

**Verify any media file (image, audio, video):**

```
curl -X POST https://api.encypher.com/api/v1/public/verify/media \
  -F "file=@signed_file.jpg;type=image/jpeg" \
  -F "mime_type=image/jpeg"
```

Replace the file path and MIME type as appropriate. Supported MIME types include
image/jpeg, image/png, image/webp, image/tiff, image/gif, image/heic, image/heif,
image/avif, image/svg+xml, image/x-adobe-dng, audio/wav, audio/mpeg, audio/mp4,
audio/flac, audio/ogg, video/mp4, video/quicktime, video/x-msvideo, video/webm.

**Verify text with embedded provenance:**

```
curl -X POST https://api.encypher.com/api/v1/public/verify \
  -H "Content-Type: application/json" \
  -d '{"text": "<text with embedded provenance metadata>"}'
```

**Sign text (requires API key):**

```
curl -X POST https://api.encypher.com/api/v1/sign \
  -H "Authorization: Bearer <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"text": "Content to sign"}'
```

## Appendix: Requirement Traceability Matrix

This matrix maps each Level 1 security requirement from the C2PA Generator
Product Security Requirements document to the section of this document
that addresses it.

### O.1 -- Certificate Enrollment (Section 6.1.1)

| Req | Requirement | Section | Status |
|-----|-------------|---------|--------|
| 6.1.1.R1 | GP TOE implements secure authentication for automated certificate enrollment | C.2.1 | Addressed (SSL.com portal-based enrollment with org validation) |
| 6.1.1.SE1 | Document enrollment authentication method and secret management | C.2.1 | Addressed (SSL.com API-based enrollment, Railway encrypted env vars) |

### O.2 -- Signing Key Confidentiality (Section 6.2.1)

| Req | Requirement | Section | Status |
|-----|-------------|---------|--------|
| 6.2.1.R1 | Claim signing key stored in encrypted form | C.2.2 | Addressed (encrypted env var store) |
| 6.2.1.R2 | Access to signing key follows least privilege | C.2.2 | Addressed (non-root container, API auth, env var isolation) |
| 6.2.1.R3 | GP TOE capable of rotating claim signing key | C.2.2 | Addressed (rotation procedure documented) |
| 6.2.1.R4 | Edge subsystem authentication key used only for limiting access to Backend | C.2.2 | N/A -- Backend Implementation Class (Section 2.32). No Edge subsystem exists within the TOE. See Appendix A.1 for the reference Backend class architecture. |
| 6.2.1.R5 | Edge and Backend subsystems mutually authenticated | C.2.2 | N/A -- Backend Implementation Class. The product is a monolithic backend service with no distributed subsystems. Mutual authentication applies only to the Distributed Implementation Class (Section 2.33). |
| 6.2.1.R6 | Remote Backend SHALL authenticate calling client as valid Edge instance | C.2.2 | Addressed via API key authentication. While R6 is written for the Distributed class (it references "the Edge subsystem of the GP TOE"), our Backend-class product satisfies the security intent: every signing request requires a Bearer API key tied to a registered organization. Unauthenticated requests cannot trigger signing. This aligns with R6's accepted method of "shared secret/passphrase" and matches the trust model in Appendix A.1 (Backend Class: Video Generation Service). |
| 6.2.1.SE1a | Document key access controls including encryption | C.2.2 | Addressed |
| 6.2.1.SE1b | Document key rotation process | C.2.2 | Addressed |
| 6.2.1.SE1c | Document mutual authentication between subsystems | C.2.2 | N/A -- Backend Implementation Class, monolithic backend, no subsystem split. API key authentication provides caller verification at the TOE boundary. |

### O.3 -- Claim Generator Protection (Section 6.3.1)

| Req | Requirement | Section | Status |
|-----|-------------|---------|--------|
| 6.3.1.R1 | SCA/SBOM analysis performed | C.2.3 | Addressed (pip-audit against OSV/NVD) |
| 6.3.1.R2 | CRITICAL/HIGH vulns fixed within 90 days | C.2.3 | Addressed (30/90 day SLA documented) |
| 6.3.1.SE1a | Document SCA/SBOM tools | C.2.3 | Addressed (pip-audit, Dependabot) |
| 6.3.1.SE1b | Document process preventing release with known vulns | C.2.3 | Addressed (CI gate on pip-audit) |

### O.4 -- Content/Assertion Tamper Protection (Section 6.4.1)

| Req | Requirement | Section | Status |
|-----|-------------|---------|--------|
| 6.4.1.R1 | SCA/SBOM analysis on content-processing software | C.2.4 | Addressed (same pip-audit process) |
| 6.4.1.R2 | CRITICAL/HIGH vulns fixed within 90 days | C.2.4 | Addressed (same SLA) |

### O.5 -- Traffic Protection (Section 6.5.1)

| Req | Requirement | Section | Status |
|-----|-------------|---------|--------|
| 6.5.1.R1 | Network channels encrypted with TLS v1.3 or higher | C.2.5 | Addressed (Railway edge enforces TLS 1.3 minimum, HTTPS for all external comms) |
| 6.5.1.SE1a | Document TLS versions and crypto protocols | C.2.5 | Addressed (TLS 1.3 via Railway edge proxy, ECDHE+AESGCM/CHACHA20) |

### O.6 -- Hosting Environment Protection (Section 6.6.1)

| Req | Requirement | Section | Status |
|-----|-------------|---------|--------|
| 6.6.1.R1 | IAM with RBAC for asset/assertion generation resources | C.2.6 | Addressed (Railway team RBAC, container isolation, API key auth) |
| 6.6.1.R2 | Vulnerability scanning for dependencies and API surfaces | C.2.6 | Addressed (pip-audit, OWASP mitigations) |
| 6.6.1.R3 | Basic exploit countermeasures, timely patching | C.2.6 | Addressed (non-root container, minimal base image, kernel ASLR/NX) |
| 6.6.1.SE1 | Document IAM system and security boundaries | C.2.6 | Addressed (Railway team RBAC: Owner/Admin/Member roles documented) |
| 6.6.1.SE2 | Document access policies for human/non-human principals | C.2.6 | Addressed (human: Railway Owner/Admin roles; non-human: service tokens, API keys) |
| 6.6.1.SE3 | Document IAM policies for cloud resources | C.2.6 | Addressed (Railway project-level RBAC, resource access table in C.2.6) |
| 6.6.1.SE4 | Document vuln scanning process | C.2.6 | Addressed |
| 6.6.1.SE5 | Document vuln remediation process | C.2.6 | Addressed (30/90/180 day SLA) |

---

*Document prepared by Encypher Corporation for submission to the C2PA
Conformance Program. This document addresses all Level 1 security
requirements from the C2PA Generator Product Security Requirements
(Version 0.1, 2025-06-02).*
