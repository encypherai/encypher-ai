# ENCYPHER ENTERPRISE V1 - WBS TASK LIST
## Lean MVP: Publisher Article Signing API

**Goal:** Production-ready API for publishers to sign articles with sentence-level tracking, full C2PA compliance, and independent verification - deployable in 3-4 months with minimal operational cost.

**Key Constraints:**
- ✅ Industry-approved signatures (C2PA 2.2 + Ed25519)
- ✅ Low operational cost (<$10K/month)
- ✅ Encypher as source of truth (centralized, trusted)
- ✅ Court-admissible evidence
- ✅ Fast time to market

---

## PHASE 1: CORE INFRASTRUCTURE (Weeks 1-4)

### 1.1 Database Setup

**Deliverable:** Production PostgreSQL database with core tables

- [ ] **1.1.1** Set up PostgreSQL 15+ (AWS RDS or managed service)
  - Single region (US-East) for v1
  - Automated backups (point-in-time recovery)
  - Encryption at rest

- [ ] **1.1.2** Create `publishers` table
  ```sql
  CREATE TABLE publishers (
    publisher_id VARCHAR(100) PRIMARY KEY,
    organization_name VARCHAR(500) NOT NULL,
    email VARCHAR(255) NOT NULL,
    tier VARCHAR(50) NOT NULL, -- 'free', 'business', 'enterprise'
    key_management VARCHAR(50) NOT NULL, -- 'encypher_managed', 'publisher_managed'
    public_key_pem TEXT,
    certificate_pem TEXT,
    monthly_quota INTEGER DEFAULT 1000,
    created_at TIMESTAMP DEFAULT NOW()
  );
  ```

- [ ] **1.1.3** Create `sentence_records` table (CRITICAL)
  ```sql
  CREATE TABLE sentence_records (
    uuid VARCHAR(32) PRIMARY KEY,
    publisher_id VARCHAR(100) NOT NULL,
    
    -- Content
    sentence_text TEXT NOT NULL,
    sentence_hash VARCHAR(64) NOT NULL,
    sentence_index INTEGER NOT NULL,
    
    -- Article reference
    article_id VARCHAR(100) NOT NULL,
    article_title VARCHAR(500),
    article_url VARCHAR(1000),
    
    -- Signature (KEY INNOVATION)
    signature VARCHAR(128) NOT NULL, -- Ed25519 signature hex
    signature_timestamp TIMESTAMP NOT NULL,
    signer_key_id VARCHAR(100) NOT NULL,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_sentence_hash (sentence_hash),
    INDEX idx_publisher (publisher_id),
    INDEX idx_article (article_id)
  );
  ```

- [ ] **1.1.4** Create `articles` table
  ```sql
  CREATE TABLE articles (
    article_id VARCHAR(100) PRIMARY KEY,
    publisher_id VARCHAR(100) NOT NULL,
    title VARCHAR(500),
    url VARCHAR(1000),
    total_sentences INTEGER NOT NULL,
    
    -- C2PA manifest
    manifest_cbor BYTEA NOT NULL,
    manifest_signature VARCHAR(256) NOT NULL,
    
    publication_date TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_publisher_date (publisher_id, publication_date)
  );
  ```

- [ ] **1.1.5** Create `api_keys` table
  ```sql
  CREATE TABLE api_keys (
    api_key VARCHAR(64) PRIMARY KEY,
    publisher_id VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    last_used_at TIMESTAMP,
    revoked BOOLEAN DEFAULT FALSE
  );
  ```

- [ ] **1.1.6** Set up connection pooling (PgBouncer)
  - Max 100 connections
  - Connection timeout: 30s

**Success Criteria:**
- Database deployed and accessible
- All tables created with proper indexes
- Backup schedule configured (daily)
- Connection pooling operational

**Estimated Time:** 3 days  
**Cost:** $200/month (RDS db.t3.medium)

---

### 1.2 Cryptographic Signing Module

**Deliverable:** Ed25519 signing/verification library (industry-standard)

- [ ] **1.2.1** Create `crypto_utils.py` module
  - Use `cryptography` library (industry standard)
  - Ed25519 key generation
  - Ed25519 signing
  - Ed25519 verification

- [ ] **1.2.2** Implement signing functions
  ```python
  def sign_sentence_record(
      record: dict,
      private_key: Ed25519PrivateKey
  ) -> str:
      """
      Sign sentence record with Ed25519.
      Returns hex-encoded signature.
      """
      # Canonical serialization (CBOR)
      canonical = cbor2.dumps(record, canonical=True)
      
      # Sign
      signature = private_key.sign(canonical)
      
      return signature.hex()
  ```

- [ ] **1.2.3** Implement verification functions
  ```python
  def verify_sentence_signature(
      record: dict,
      signature_hex: str,
      public_key: Ed25519PublicKey
  ) -> bool:
      """
      Verify Ed25519 signature on sentence record.
      """
      canonical = cbor2.dumps(record, canonical=True)
      signature = bytes.fromhex(signature_hex)
      
      try:
          public_key.verify(signature, canonical)
          return True
      except InvalidSignature:
          return False
  ```

- [ ] **1.2.4** Create key management utilities
  ```python
  def generate_keypair() -> Tuple[Ed25519PrivateKey, Ed25519PublicKey]:
      """Generate Ed25519 keypair for publisher."""
      private_key = ed25519.Ed25519PrivateKey.generate()
      public_key = private_key.public_key()
      return private_key, public_key
  
  def export_public_key_pem(public_key: Ed25519PublicKey) -> str:
      """Export public key to PEM format."""
      return public_key.public_bytes(
          encoding=serialization.Encoding.PEM,
          format=serialization.PublicFormat.SubjectPublicKeyInfo
      ).decode()
  ```

- [ ] **1.2.5** Implement Encypher master keys (for free tier)
  - Generate Encypher Ed25519 keypair
  - Store private key in AWS Secrets Manager
  - Document key rotation procedure

- [ ] **1.2.6** Write unit tests
  - Test key generation
  - Test signing/verification
  - Test signature tamper detection
  - Test key serialization/deserialization

**Success Criteria:**
- Sign 10K records/second
- Verify 50K signatures/second
- 100% tamper detection
- Zero false positives

**Estimated Time:** 5 days  
**Cost:** $10/month (Secrets Manager)

---

### 1.3 UUID Generation System

**Deliverable:** Hierarchical UUID generation (IDF-001 simplified)

- [ ] **1.3.1** Create `uuid_generator.py` module
  ```python
  def generate_uuid(
      sentence: str,
      publisher_id: str,
      sentence_index: int,
      timestamp: datetime
  ) -> str:
      """
      Generate 128-bit hierarchical UUID.
      
      Structure:
      - 4 bits: version (0001)
      - 44 bits: timestamp (milliseconds since epoch)
      - 32 bits: publisher hash
      - 32 bits: sentence hash (truncated SHA-256)
      - 16 bits: sentence index
      
      Returns: 32-character hex string
      """
  ```

- [ ] **1.3.2** Implement UUID encoding
  - Bitwise operations for field packing
  - Hex encoding (32 characters)
  - Deterministic generation

- [ ] **1.3.3** Implement UUID decoding
  - Parse hex string back to fields
  - Extract timestamp, publisher, index
  - Validation

- [ ] **1.3.4** Write unit tests
  - Test encoding/decoding
  - Test collision probability (Monte Carlo)
  - Test deterministic generation
  - Test edge cases (max values)

**Success Criteria:**
- Generate 50K UUIDs/second
- Zero collisions in 10M test UUIDs
- Decode UUID in <1ms
- 100% deterministic

**Estimated Time:** 3 days  
**Cost:** $0

---

### 1.4 Unicode Embedding Module

**Deliverable:** Invisible UUID embedding at sentence level

- [ ] **1.4.1** Create `unicode_embedder.py` module
  - Use variation selectors (U+FE00 to U+FE0F)
  - Base64 encoding of UUID
  - Embed at sentence terminators

- [ ] **1.4.2** Implement embedding function
  ```python
  def embed_uuid_at_sentence(
      text: str,
      uuid: str,
      sentence_end_position: int
  ) -> str:
      """
      Embed UUID at sentence terminator using Unicode variation selectors.
      Invisible to readers, preserved through copy/paste.
      """
  ```

- [ ] **1.4.3** Implement extraction function
  ```python
  def extract_uuids(text: str) -> List[Dict[str, Any]]:
      """
      Extract all embedded UUIDs from text.
      Returns list of {uuid, position, sentence_index}
      """
  ```

- [ ] **1.4.4** Test survivability
  - Copy/paste across platforms (Windows, Mac, Linux)
  - Test in different text editors (Word, Google Docs, Notepad)
  - Test in web forms (Twitter, Reddit character limits)
  - Document survival rate

- [ ] **1.4.5** Implement manifest embedding
  - C2PA manifest at end of document
  - CBOR encoding
  - Unicode-based embedding
  - Extraction and validation

**Success Criteria:**
- Embedding: <1ms per sentence
- Extraction: <50ms per 1K sentences
- Survivability: >90% across platforms
- Zero visible artifacts

**Estimated Time:** 5 days  
**Cost:** $0

---

## PHASE 2: C2PA COMPLIANCE (Weeks 5-6)

### 2.1 C2PA Manifest Builder

**Deliverable:** C2PA 2.2 compliant manifest generation

- [ ] **2.1.1** Create `c2pa_manifest.py` module
  - Use `pycose` library for COSE_Sign1
  - Use `cbor2` for canonical serialization

- [ ] **2.1.2** Implement required assertions
  ```python
  def create_actions_assertion(
      action: str = "c2pa.published",
      timestamp: datetime = None,
      software_agent: str = None
  ) -> dict:
      """Create c2pa.actions.v1 assertion."""
      return {
          "label": "c2pa.actions.v1",
          "data": {
              "actions": [{
                  "action": action,
                  "when": (timestamp or datetime.utcnow()).isoformat() + "Z",
                  "softwareAgent": software_agent or "Encypher Enterprise API"
              }]
          }
      }
  ```

- [ ] **2.1.3** Implement hard binding assertion
  ```python
  def create_hard_binding_assertion(content: str) -> dict:
      """Create c2pa.hash.data.v1 assertion (hard binding)."""
      content_hash = hashlib.sha256(content.encode()).digest()
      return {
          "label": "c2pa.hash.data.v1",
          "data": {
              "alg": "sha256",
              "hash": base64.b64encode(content_hash).decode(),
              "name": "document_content"
          }
      }
  ```

- [ ] **2.1.4** Implement proprietary assertions
  ```python
  def create_encypher_uuids_assertion(uuids: List[str]) -> dict:
      """Create encypher.sentence_uuids.v1 assertion."""
      return {
          "label": "encypher.sentence_uuids.v1",
          "data": {
              "uuids": uuids,
              "verification_api": "https://api.encypher.com/v1/verify/sentence/",
              "signature_info": "Each UUID references signed database record"
          }
      }
  ```

- [ ] **2.1.5** Implement manifest assembly
  ```python
  def create_manifest(
      content: str,
      uuids: List[str],
      publisher_id: str,
      article_metadata: dict
  ) -> dict:
      """Assemble complete C2PA manifest."""
      return {
          "claim_generator": "encypher-enterprise-api/1.0.0",
          "assertions": [
              create_actions_assertion(...),
              create_hard_binding_assertion(content),
              create_encypher_uuids_assertion(uuids),
              # Add metadata assertions
          ]
      }
  ```

- [ ] **2.1.6** Implement COSE_Sign1 signing
  ```python
  def sign_manifest(
      manifest: dict,
      private_key: Ed25519PrivateKey,
      signer_id: str
  ) -> bytes:
      """Sign manifest with COSE_Sign1 structure."""
      # Serialize to canonical CBOR
      payload = cbor2.dumps(manifest, canonical=True)
      
      # Create COSE_Sign1 message
      protected_header = {
          1: -8,  # EdDSA algorithm
          3: "application/c2pa-manifest+cbor"
      }
      
      msg = Sign1Message(
          phdr=protected_header,
          payload=payload
      )
      msg.key = private_key
      
      return msg.encode()
  ```

- [ ] **2.1.7** Test C2PA compliance
  - Validate against C2PA spec 2.2
  - Test with c2pa-rs validator (if available)
  - Ensure CBOR canonical serialization
  - Verify all required assertions present

**Success Criteria:**
- C2PA 2.2 spec compliant
- Generate manifest in <10ms
- COSE_Sign1 structure correct
- Passes validation tools

**Estimated Time:** 7 days  
**Cost:** $0

---

## PHASE 3: ARTICLE SIGNING ENGINE (Weeks 7-8)

### 3.1 Sentence Parser

**Deliverable:** Robust sentence segmentation

- [ ] **3.1.1** Create `sentence_parser.py` module
  - Rule-based sentence detection (.!?)
  - Handle abbreviations (Dr., Mr., etc.)
  - Handle URLs, email addresses
  - Handle ellipses (...)

- [ ] **3.1.2** Implement parsing function
  ```python
  def parse_sentences(text: str) -> List[Dict[str, Any]]:
      """
      Parse text into sentences.
      
      Returns:
          List of {
              text: str,
              start_pos: int,
              end_pos: int,
              index: int
          }
      """
  ```

- [ ] **3.1.3** Test edge cases
  - Abbreviations: "Dr. Smith said..."
  - URLs: "Visit example.com. Next sentence."
  - Numbers: "Cost is $1.99. Next sentence."
  - Ellipses: "And then... something happened."

**Success Criteria:**
- Parse 10K sentences/second
- 95%+ accuracy on news articles
- Handle common edge cases correctly

**Estimated Time:** 3 days  
**Cost:** $0

---

### 3.2 Article Signing Workflow

**Deliverable:** End-to-end article signing

- [ ] **3.2.1** Create `article_signer.py` module
  ```python
  class ArticleSigner:
      def sign_article(
          self,
          content: str,
          publisher_id: str,
          metadata: dict,
          private_key: Ed25519PrivateKey
      ) -> SignedArticle:
          """
          Complete article signing workflow:
          1. Parse sentences
          2. Generate UUID per sentence
          3. Sign each sentence record
          4. Store in database
          5. Create C2PA manifest
          6. Sign manifest
          7. Embed UUIDs + manifest
          """
  ```

- [ ] **3.2.2** Implement sentence-level signing
  ```python
  def sign_sentence_records(
      self,
      sentences: List[dict],
      publisher_id: str,
      article_id: str,
      private_key: Ed25519PrivateKey
  ) -> List[str]:
      """
      Generate signed UUID for each sentence.
      Store signed records in database.
      Return list of UUIDs.
      """
      uuids = []
      
      for sentence in sentences:
          # Generate UUID
          uuid = generate_uuid(...)
          
          # Create record
          record = {
              "uuid": uuid,
              "sentence_text": sentence["text"],
              "sentence_hash": hashlib.sha256(sentence["text"].encode()).hexdigest(),
              "sentence_index": sentence["index"],
              "publisher_id": publisher_id,
              "article_id": article_id,
              "signature_timestamp": datetime.utcnow().isoformat()
          }
          
          # Sign record
          signature = sign_sentence_record(record, private_key)
          
          # Store in database
          db.insert_sentence_record(record, signature)
          
          uuids.append(uuid)
      
      return uuids
  ```

- [ ] **3.2.3** Implement manifest creation and signing
  ```python
  def create_and_sign_manifest(
      self,
      content: str,
      uuids: List[str],
      publisher_id: str,
      article_metadata: dict,
      private_key: Ed25519PrivateKey
  ) -> bytes:
      """
      Create C2PA manifest and sign with COSE_Sign1.
      """
      manifest = create_manifest(...)
      signed_manifest = sign_manifest(manifest, private_key, publisher_id)
      return signed_manifest
  ```

- [ ] **3.2.4** Implement embedding
  ```python
  def embed_signatures(
      self,
      content: str,
      uuids: List[str],
      sentences: List[dict],
      manifest: bytes
  ) -> str:
      """
      Embed UUIDs at each sentence + manifest at end.
      """
      # Embed UUID at each sentence terminator
      for uuid, sentence in zip(uuids, sentences):
          content = embed_uuid_at_sentence(
              content,
              uuid,
              sentence["end_pos"]
          )
      
      # Embed manifest at end
      content = embed_manifest(content, manifest)
      
      return content
  ```

- [ ] **3.2.5** Implement transaction handling
  - All-or-nothing (rollback on failure)
  - Database transactions
  - Error handling and logging

**Success Criteria:**
- Sign 500-sentence article in <500ms
- Atomic operations (no partial failures)
- All signatures valid
- All records in database

**Estimated Time:** 5 days  
**Cost:** $0

---

## PHASE 4: REST API (Weeks 9-10)

### 4.1 API Framework Setup

**Deliverable:** FastAPI application with authentication

- [ ] **4.1.1** Set up FastAPI project structure
  ```
  api/
  ├── main.py
  ├── routers/
  │   ├── publishers.py
  │   ├── articles.py
  │   └── verification.py
  ├── models/
  │   ├── publisher.py
  │   ├── article.py
  │   └── verification.py
  ├── auth/
  │   └── api_key.py
  └── database/
      └── db.py
  ```

- [ ] **4.1.2** Implement API key authentication
  ```python
  from fastapi import Security, HTTPException
  from fastapi.security import APIKeyHeader
  
  api_key_header = APIKeyHeader(name="X-API-Key")
  
  async def verify_api_key(api_key: str = Security(api_key_header)):
      """Verify API key and return publisher_id."""
      publisher = db.get_publisher_by_api_key(api_key)
      if not publisher:
          raise HTTPException(status_code=401, detail="Invalid API key")
      return publisher
  ```

- [ ] **4.1.3** Implement rate limiting
  - Use `slowapi` library
  - Tier-based limits:
    - Free: 100 requests/hour
    - Business: 1000 requests/hour
    - Enterprise: 10000 requests/hour

- [ ] **4.1.4** Set up CORS
  - Allow specific origins for dashboard
  - Restrict for production

**Success Criteria:**
- API responds in <10ms (health check)
- Authentication works correctly
- Rate limiting enforces quotas
- CORS configured properly

**Estimated Time:** 3 days  
**Cost:** $50/month (EC2 t3.small or App Engine)

---

### 4.2 Publisher Endpoints

**Deliverable:** Publisher registration and key management

- [ ] **4.2.1** Create registration endpoint
  ```python
  @router.post("/v1/publishers/register")
  async def register_publisher(
      organization: str,
      email: str,
      tier: str = "free",
      key_management: str = "encypher_managed"
  ):
      """
      Register new publisher.
      
      Returns:
          {
              "publisher_id": "...",
              "api_key": "ency_...",
              "public_key": "..." (if encypher_managed),
              "status": "active"
          }
      """
  ```

- [ ] **4.2.2** Implement key generation (encypher_managed)
  ```python
  if key_management == "encypher_managed":
      # Generate keypair
      private_key, public_key = generate_keypair()
      
      # Store private key in Secrets Manager
      store_private_key(publisher_id, private_key)
      
      # Store public key in database
      db.store_public_key(publisher_id, public_key)
  ```

- [ ] **4.2.3** Implement key upload (publisher_managed)
  ```python
  @router.post("/v1/publishers/{publisher_id}/upload-key")
  async def upload_public_key(
      publisher_id: str,
      public_key_pem: str,
      publisher: Publisher = Depends(verify_api_key)
  ):
      """Upload publisher's public key (for publisher-managed keys)."""
  ```

- [ ] **4.2.4** Create publisher info endpoint
  ```python
  @router.get("/v1/publishers/me")
  async def get_publisher_info(
      publisher: Publisher = Depends(verify_api_key)
  ):
      """Get current publisher information and quota."""
  ```

**Success Criteria:**
- Registration completes in <1 second
- Keys stored securely
- Quota tracking works
- API key generation secure

**Estimated Time:** 4 days  
**Cost:** $0

---

### 4.3 Article Signing Endpoint (PRIMARY USE CASE)

**Deliverable:** Core signing API

- [ ] **4.3.1** Create signing endpoint
  ```python
  @router.post("/v1/articles/sign")
  async def sign_article(
      content: str,
      metadata: ArticleMetadata,
      publisher: Publisher = Depends(verify_api_key)
  ):
      """
      Sign article with sentence-level UUIDs + C2PA manifest.
      
      Request:
          {
              "content": "Article text...",
              "metadata": {
                  "title": "...",
                  "author": "...",
                  "url": "...",
                  "publication_date": "2025-10-21T..."
              }
          }
      
      Response:
          {
              "article_id": "...",
              "signed_content": "Article with embedded UUIDs and manifest...",
              "sentence_count": 347,
              "uuids": ["uuid1", "uuid2", ...],
              "manifest_hash": "...",
              "verification_url": "https://verify.encypher.com/article/...",
              "quota_remaining": 823
          }
      """
  ```

- [ ] **4.3.2** Implement quota checking
  ```python
  # Check quota before signing
  if publisher.usage_this_month >= publisher.monthly_quota:
      raise HTTPException(
          status_code=429,
          detail="Monthly quota exceeded. Upgrade tier or wait for reset."
      )
  ```

- [ ] **4.3.3** Implement signing workflow
  ```python
  # Get publisher's private key
  private_key = get_publisher_private_key(publisher.publisher_id)
  
  # Sign article
  signer = ArticleSigner()
  signed_article = signer.sign_article(
      content=content,
      publisher_id=publisher.publisher_id,
      metadata=metadata.dict(),
      private_key=private_key
  )
  
  # Update quota
  db.increment_usage(publisher.publisher_id)
  
  return signed_article
  ```

- [ ] **4.3.4** Add response metadata
  - Article ID
  - Signed content
  - Sentence count
  - All UUIDs
  - Verification URL
  - Quota status

- [ ] **4.3.5** Implement error handling
  - Malformed content
  - Missing metadata
  - Quota exceeded
  - Signing failures
  - Database errors

**Success Criteria:**
- Sign 500-sentence article in <500ms
- Quota enforcement works
- All signatures valid
- Error responses clear and actionable

**Estimated Time:** 5 days  
**Cost:** $0

---

### 4.4 Verification Endpoints

**Deliverable:** Sentence and article verification APIs

- [ ] **4.4.1** Create sentence verification endpoint
  ```python
  @router.get("/v1/verify/sentence/{uuid}")
  async def verify_sentence(uuid: str):
      """
      Verify single sentence by UUID.
      
      Response:
          {
              "status": "VERIFIED" | "TAMPERED" | "UNKNOWN",
              "uuid": "...",
              "sentence": {
                  "text": "...",
                  "hash": "...",
                  "index": 42
              },
              "signature": {
                  "valid": true,
                  "signer": "nyt-prod-001",
                  "timestamp": "2025-10-21T..."
              },
              "publisher": {
                  "id": "nyt",
                  "name": "The New York Times"
              },
              "source": {
                  "article_id": "...",
                  "title": "...",
                  "url": "...",
                  "publication_date": "..."
              }
          }
      """
  ```

- [ ] **4.4.2** Implement verification logic
  ```python
  # Get record from database
  record = db.get_sentence_record(uuid)
  if not record:
      return {"status": "UNKNOWN", "message": "UUID not found"}
  
  # Get publisher's public key
  public_key = db.get_publisher_public_key(record.publisher_id)
  
  # Verify signature
  is_valid = verify_sentence_signature(
      record.to_dict(),
      record.signature,
      public_key
  )
  
  if is_valid:
      return {"status": "VERIFIED", ...}
  else:
      return {"status": "TAMPERED", ...}
  ```

- [ ] **4.4.3** Create extracted text verification
  ```python
  @router.post("/v1/verify/sentence-text")
  async def verify_sentence_text(
      text: str,
      uuid: str
  ):
      """
      Verify extracted sentence matches database record.
      
      Response:
          {
              "match": true | false,
              "stored_hash": "...",
              "provided_hash": "...",
              "status": "VERIFIED" | "TAMPERED"
          }
      """
  ```

- [ ] **4.4.4** Create article verification endpoint
  ```python
  @router.post("/v1/verify/article")
  async def verify_article(content: str):
      """
      Verify entire article (extract manifest, verify signature).
      
      Response:
          {
              "status": "VERIFIED",
              "manifest": {...},
              "signature_valid": true,
              "sentence_count": 347,
              "all_sentences_valid": true
          }
      """
  ```

- [ ] **4.4.5** Implement caching
  - Cache verification results (5 min TTL)
  - Cache publisher public keys (1 hour TTL)
  - Use Redis for caching

**Success Criteria:**
- Verification latency: <100ms (p99)
- Cache hit rate: >80%
- 100% accuracy on tamper detection
- Clear status messages

**Estimated Time:** 5 days  
**Cost:** $20/month (ElastiCache Redis)

---

## PHASE 5: VERIFICATION DASHBOARD (Weeks 11-12)

### 5.1 Public Verification Page

**Deliverable:** https://verify.encypher.com/{article_id}

- [ ] **5.1.1** Create React app (or Next.js)
  - Simple, fast, mobile-responsive
  - No complex state management needed

- [ ] **5.1.2** Build verification display
  - Extract article_id from URL
  - Call API: GET /v1/verify/article/{article_id}
  - Display:
    - ✅ or ❌ verification status
    - Publisher name and logo
    - Article title, author, date
    - Signature details
    - Sentence count

- [ ] **5.1.3** Add interactive features
  - Click sentence → show UUID
  - Click UUID → show database record
  - Copy UUID to clipboard

- [ ] **5.1.4** Create embed code generator
  ```html
  <script src="https://verify.encypher.com/embed.js"></script>
  <div data-encypher-article="article-id"></div>
  ```

- [ ] **5.1.5** Deploy to CDN
  - Cloudflare Pages or Vercel
  - Global edge distribution
  - SSL/HTTPS

**Success Criteria:**
- Load time: <2 seconds
- Mobile responsive
- Works without JavaScript (progressive enhancement)
- Professional appearance

**Estimated Time:** 5 days  
**Cost:** $0 (free tier on Vercel/Cloudflare)

---

### 5.2 Publisher Dashboard (Minimal v1)

**Deliverable:** Basic dashboard for publishers

- [ ] **5.2.1** Create authentication
  - Email/password login
  - Use Firebase Auth or Auth0 (free tier)
  - Link to publisher_id in database

- [ ] **5.2.2** Build article list view
  - Show all signed articles
  - Pagination (100 per page)
  - Columns: Title, Date, Sentences, Status

- [ ] **5.2.3** Create article detail view
  - Show article metadata
  - List all sentence UUIDs
  - Verification URL
  - Download signed content

- [ ] **5.2.4** Add usage stats
  - Articles signed this month
  - Quota remaining
  - Simple bar chart (Chart.js)

- [ ] **5.2.5** Add API key management
  - View current API key
  - Regenerate API key
  - Copy to clipboard

**Success Criteria:**
- Dashboard loads in <1 second
- All CRUD operations work
- Quota tracking accurate
- API key management functional

**Estimated Time:** 7 days  
**Cost:** $0 (Firebase/Auth0 free tier)

---

## PHASE 6: TESTING & DEPLOYMENT (Weeks 13-14)

### 6.1 Testing

**Deliverable:** Comprehensive test suite

- [ ] **6.1.1** Write unit tests
  - Cryptography module (100% coverage)
  - UUID generation (100% coverage)
  - Sentence parsing (>90% coverage)
  - Manifest creation (100% coverage)

- [ ] **6.1.2** Write integration tests
  - End-to-end signing workflow
  - Verification workflow
  - API endpoints
  - Database operations

- [ ] **6.1.3** Write security tests
  - Signature forgery attempts
  - Tamper detection
  - API key authentication
  - SQL injection prevention
  - XSS prevention

- [ ] **6.1.4** Performance testing
  - Load test: 1000 concurrent requests
  - Signing latency: 500-sentence article
  - Verification latency: 1000 lookups
  - Database query performance

- [ ] **6.1.5** Manual QA testing
  - Test on different browsers
  - Test on mobile devices
  - Test copy/paste across platforms
  - Test with real articles (NYT, Medium)

**Success Criteria:**
- 90%+ code coverage
- All security tests pass
- Performance targets met
- Zero critical bugs

**Estimated Time:** 7 days  
**Cost:** $0

---

### 6.2 Production Deployment

**Deliverable:** Live production system

- [ ] **6.2.1** Set up production infrastructure
  - API: AWS App Runner or Google Cloud Run
  - Database: AWS RDS (PostgreSQL)
  - Cache: AWS ElastiCache (Redis)
  - DNS: Cloudflare
  - SSL: Let's Encrypt (via Cloudflare)

- [ ] **6.2.2** Configure monitoring
  - Application monitoring: Sentry (free tier)
  - Uptime monitoring: UptimeRobot (free tier)
  - Log aggregation: CloudWatch or Papertrail

- [ ] **6.2.3** Set up CI/CD
  - GitHub Actions (free for public repos)
  - Automated testing on push
  - Deploy on merge to main

- [ ] **6.2.4** Create runbooks
  - Incident response procedures
  - Database backup/restore
  - Key rotation
  - Scaling procedures

- [ ] **6.2.5** Launch checklist
  - [ ] All tests passing
  - [ ] Documentation complete
  - [ ] Monitoring configured
  - [ ] Backups enabled
  - [ ] Rate limiting configured
  - [ ] SSL certificates valid
  - [ ] Domain configured

**Success Criteria:**
- 99.9% uptime (first month)
- <100ms median latency
- Zero security vulnerabilities
- All monitoring working

**Estimated Time:** 5 days  
**Cost:** See cost summary below

---

## PHASE 7: DOCUMENTATION & LAUNCH (Weeks 15-16)

### 7.1 Documentation

**Deliverable:** Complete API documentation

- [ ] **7.1.1** Write API documentation
  - OpenAPI/Swagger spec
  - Host on https://docs.encypher.com
  - Examples for each endpoint
  - Authentication guide
  - Error codes reference

- [ ] **7.1.2** Write integration guides
  - Quick start (5-minute guide)
  - Publisher registration flow
  - Article signing tutorial
  - Verification examples
  - Code samples (Python, Node.js, cURL)

- [ ] **7.1.3** Create video tutorials
  - Getting started (5 min)
  - Signing your first article (10 min)
  - Understanding verification (5 min)

- [ ] **7.1.4** Write legal documentation
  - Terms of Service
  - Privacy Policy
  - Data Processing Agreement (for GDPR)
  - Acceptable Use Policy

**Success Criteria:**
- Documentation is clear and comprehensive
- All endpoints documented
- Code samples work
- Legal docs reviewed by counsel

**Estimated Time:** 7 days  
**Cost:** $2K (legal review)

---

### 7.2 Beta Launch

**Deliverable:** Onboard 3-5 pilot publishers

- [ ] **7.2.1** Recruit beta testers
  - Reach out to 10 mid-size publishers
  - Target: 3-5 accepting beta invite
  - Offer: Free enterprise tier for 6 months

- [ ] **7.2.2** Onboard beta publishers
  - Personal onboarding calls
  - Help with integration
  - Answer questions
  - Gather feedback

- [ ] **7.2.3** Monitor usage
  - Track API calls
  - Monitor errors
  - Collect feedback
  - Fix bugs rapidly

- [ ] **7.2.4** Iterate based on feedback
  - Prioritize requested features
  - Fix UX issues
  - Improve documentation

- [ ] **7.2.5** Success metrics
  - 3+ publishers signed up
  - 100+ articles signed
  - <5% error rate
  - Positive feedback

**Success Criteria:**
- 3+ active beta publishers
- 100+ articles signed
- No critical bugs
- Ready for public launch

**Estimated Time:** 2 weeks (parallel with Phase 8)  
**Cost:** $0 (comp'd service)

---

## V1 COST SUMMARY

### Monthly Operational Costs (Estimated)

| Service | Cost/Month | Notes |
|---------|-----------|-------|
| **Database (RDS)** | $200 | PostgreSQL db.t3.medium |
| **API Hosting (App Runner)** | $50 | Pay-per-request + small always-on |
| **Cache (ElastiCache)** | $20 | Redis t3.micro |
| **Secrets Manager** | $10 | Store private keys |
| **Monitoring (Sentry)** | $0 | Free tier (10K events/month) |
| **Domain & DNS** | $10 | Domain + Cloudflare |
| **Backup Storage (S3)** | $20 | Database backups |
| **Total** | **$310/month** | ~$3,700/year |

### One-Time Costs

| Item | Cost | Notes |
|------|------|-------|
| **Legal Review** | $2,000 | Terms, Privacy Policy, DPA |
| **Development** | $0 | Assuming internal team |
| **Total** | **$2,000** | |

### **Total Year 1 Cost: ~$5,700**

**Extremely affordable** for SaaS infrastructure!

---

## V1 TIMELINE SUMMARY

```
┌─────────────────────────────────────────────────────────┐
│                   V1 DEVELOPMENT TIMELINE               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Weeks 1-4:   Phase 1 - Core Infrastructure            │
│  Weeks 5-6:   Phase 2 - C2PA Compliance                │
│  Weeks 7-8:   Phase 3 - Article Signing Engine         │
│  Weeks 9-10:  Phase 4 - REST API                       │
│  Weeks 11-12: Phase 5 - Verification Dashboard         │
│  Weeks 13-14: Phase 6 - Testing & Deployment           │
│  Weeks 15-16: Phase 7 - Documentation & Beta Launch    │
│                                                         │
│  TOTAL: 16 weeks (4 months)                            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**With 2 full-time engineers: 3 months**  
**With 1 engineer + part-time: 4-5 months**

---

# V2 FUTURE FEATURES LIST

## Enhancements to Add Based on Customer Demand

### 1. Blockchain Anchoring (Premium Feature)

**Add when:** 3+ enterprise customers request it OR competitive pressure

**Implementation:**
- [ ] Optimism/Arbitrum L2 anchoring
- [ ] Batch 1000 records per transaction
- [ ] Smart contract deployment and audit
- [ ] Blockchain verification API
- [ ] "Blockchain-verified" badge on verification page

**Cost:** $212K first year, $100K/year after  
**Pricing:** +$1K/month premium add-on  
**Timeline:** 3 months

---

### 2. Merkle Tree Evidence Packages

**Add when:** Publishers need litigation support

**Implementation:**
- [ ] Sentence-level Merkle tree construction
- [ ] Merkle proof generation
- [ ] Matching engine (exact + fuzzy)
- [ ] PDF report generation (court-admissible)
- [ ] Heatmap visualization

**Cost:** $30K development  
**Pricing:** $500/evidence package or $50K/year unlimited  
**Timeline:** 6 weeks

---

### 3. Advanced Analytics Dashboard

**Add when:** Publishers want usage insights

**Implementation:**
- [ ] Track where content appears (web crawling)
- [ ] Viral tracking (which sentences spread)
- [ ] Attribution reports (ROI metrics)
- [ ] Geographic distribution
- [ ] Time-series analysis

**Cost:** $50K development + $5K/month operational  
**Pricing:** Included in Business/Enterprise tiers  
**Timeline:** 2 months

---

### 4. Streaming Authentication (IDF-004)

**Add when:** AI labs want real-time signing (ChatGPT, Claude)

**Implementation:**
- [ ] Streaming handler (chunk-by-chunk)
- [ ] Dual-binding security (hard + soft)
- [ ] Post-stream enrichment
- [ ] Probabilistic fingerprints

**Cost:** $40K development  
**Pricing:** $50K/year for AI labs  
**Timeline:** 6 weeks

---

### 5. AI Parameter Tracking (IDF-003)

**Add when:** AI labs want performance optimization

**Implementation:**
- [ ] Parameter capture (temperature, top_p, etc.)
- [ ] Performance tracking (views, engagement)
- [ ] Correlation engine (ML-based)
- [ ] A/B testing framework
- [ ] Optimization recommendations

**Cost:** $80K development + $10K/month operational  
**Pricing:** $100K/year for AI labs  
**Timeline:** 3 months

---

### 6. Mobile SDKs

**Add when:** Publishers want mobile app integration

**Implementation:**
- [ ] iOS SDK (Swift)
- [ ] Android SDK (Kotlin)
- [ ] React Native SDK
- [ ] Flutter SDK

**Cost:** $60K development  
**Pricing:** Included in paid tiers  
**Timeline:** 3 months

---

### 7. CMS Integrations

**Add when:** 50+ publishers request it

**Implementation:**
- [ ] WordPress plugin
- [ ] Ghost integration
- [ ] Medium API integration
- [ ] Substack integration
- [ ] Contentful plugin

**Cost:** $40K development  
**Pricing:** Free (drives adoption)  
**Timeline:** 2 months

---

### 8. Browser Extensions

**Add when:** Users want to verify articles while browsing

**Implementation:**
- [ ] Chrome extension
- [ ] Firefox extension
- [ ] Safari extension
- [ ] Automatic verification on news sites

**Cost:** $25K development  
**Pricing:** Free (marketing tool)  
**Timeline:** 1 month

---

### 9. Multi-Region Deployment

**Add when:** 1000+ publishers OR GDPR requirement

**Implementation:**
- [ ] EU region (Frankfurt)
- [ ] Asia-Pacific region (Singapore)
- [ ] Database replication
- [ ] Latency-based routing

**Cost:** $300/month additional operational  
**Pricing:** Included in Enterprise tier  
**Timeline:** 2 weeks

---

### 10. White-Label Solution

**Add when:** Large publisher wants branded verification

**Implementation:**
- [ ] Custom verification domain
- [ ] Custom branding (logo, colors)
- [ ] Custom email templates
- [ ] Dedicated infrastructure

**Cost:** $100K development  
**Pricing:** $250K/year  
**Timeline:** 3 months

---

### 11. Bulk Import/Export

**Add when:** Publishers want to retroactively sign old content

**Implementation:**
- [ ] Batch signing API (1000s of articles)
- [ ] CSV import
- [ ] Archive export (all signed articles)
- [ ] Bulk verification

**Cost:** $15K development  
**Pricing:** Included in Enterprise tier  
**Timeline:** 3 weeks

---

### 12. Webhook Notifications

**Add when:** Publishers want real-time alerts

**Implementation:**
- [ ] Webhook on verification attempt
- [ ] Webhook on tamper detection
- [ ] Webhook on usage detection
- [ ] Configurable webhook endpoints

**Cost:** $10K development  
**Pricing:** Included in paid tiers  
**Timeline:** 2 weeks

---

### 13. API Rate Limit Overrides

**Add when:** High-volume publishers need more

**Implementation:**
- [ ] Custom rate limits per customer
- [ ] Burst allowance
- [ ] Rate limit dashboard
- [ ] Auto-scaling triggers

**Cost:** $5K development  
**Pricing:** Custom pricing  
**Timeline:** 1 week

---

### 14. Compliance Reports

**Add when:** Publishers need SOC 2 / ISO compliance

**Implementation:**
- [ ] Audit log exports
- [ ] Compliance dashboard
- [ ] Automated reports (monthly)
- [ ] Data retention policies

**Cost:** $20K development  
**Pricing:** Included in Enterprise tier  
**Timeline:** 1 month

---

### 15. Multi-Language Support

**Add when:** International expansion

**Implementation:**
- [ ] i18n for dashboard
- [ ] Multi-language verification page
- [ ] Non-English sentence parsing
- [ ] Unicode normalization improvements

**Cost:** $30K development  
**Pricing:** Included in all tiers  
**Timeline:** 6 weeks

---

## V2 PRIORITIZATION FRAMEWORK

### High Priority (Add in Year 1 if 3+ customers request)
1. **Merkle Tree Evidence Packages** - Core litigation value
2. **Advanced Analytics** - Publisher retention driver
3. **Blockchain Anchoring** - Enterprise differentiation

### Medium Priority (Add in Year 2)
4. **CMS Integrations** - Reduces friction, drives adoption
5. **Mobile SDKs** - Future-proofing
6. **Browser Extensions** - User-facing marketing

### Low Priority (Add when scaling)
7. **Streaming Authentication** - AI lab use case (different market)
8. **AI Parameter Tracking** - AI lab use case
9. **White-Label** - Large enterprise only

### Operational Improvements
10. **Multi-Region** - Add when latency becomes issue
11. **Bulk Import** - Add when requested
12. **Webhooks** - Add when integration needs grow

---

## SUMMARY: V1 LAUNCH CHECKLIST

### ✅ Core Features (Must-Have)
- [x] Ed25519 signing (industry-standard)
- [x] Signed UUID per sentence (innovation)
- [x] C2PA 2.2 compliant manifests
- [x] Publisher registration
- [x] Article signing API
- [x] Sentence verification API
- [x] Public verification page
- [x] Publisher dashboard (basic)

### ✅ Operational Requirements
- [x] <$400/month operational cost
- [x] 99.9% uptime SLA capability
- [x] API documentation
- [x] Legal docs (ToS, Privacy)
- [x] Monitoring & alerting
- [x] Backup/restore procedures

### ✅ Launch Criteria
- [x] 3+ beta publishers signed up
- [x] 100+ articles signed
- [x] All tests passing
- [x] Security audit complete
- [x] Documentation complete

### ⏱️ Timeline: 16 weeks (4 months)

### 💰 Cost: $5,700 year 1 ($310/month operational)

---

**This is your focused, achievable v1. Ship it, get feedback, iterate to v2.**