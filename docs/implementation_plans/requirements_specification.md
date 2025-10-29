# Requirements Specification
## Merkle Tree-Based Hierarchical Content Attribution System

**Document Version:** 1.0  
**Date:** 2025-10-28  
**Status:** Draft  
**Task:** 1.1.1 - Review patent claims and map to technical requirements

---

## 1. Patent Claims Analysis

### Patent Claim 1: Source Determination Method

**Claim Text:**
> A method of determining the source of digital text content, the digital text content including one or more text strings, comprising:
> - segmenting a text string into one or more text segments based on a predetermined segmentation criteria;
> - cryptographically hashing each text segment of the text string to create a target hash;
> - querying a database for one or more instances of a source hash identical to the target hash to identify one or more candidate Merkle roots containing the source hash
> - generating a Merkle proof for the target hash in at least one of the candidate Merkle trees
> - based on the Merkle Proof and the target hash, determining a location in one or more of the candidate source documents where the text segment appears
> - outputting a list of the one or more of the candidate source documents in which the text segment appears and the location

#### Technical Requirements Mapping:

| Patent Element | Technical Requirement | Component | Priority |
|----------------|----------------------|-----------|----------|
| Segmenting text string | Text segmentation engine supporting sentence/paragraph/section levels | `app/utils/segmentation/` | P0 |
| Predetermined segmentation criteria | Configurable segmentation rules (regex, NLP, markers) | `SegmentationConfig` | P0 |
| Cryptographically hashing | SHA-256 hashing implementation for text segments | `app/utils/merkle/hashing.py` | P0 |
| Target hash creation | Hash computation for query text | `compute_hash()` function | P0 |
| Database query for source hash | Efficient hash lookup in merkle_subhashes table | `find_by_hash()` DB function | P0 |
| Identify candidate Merkle roots | Join query from subhashes to merkle_roots | `get_candidate_roots()` | P0 |
| Merkle tree representation | Tree data structure with nodes and hashes | `MerkleTree` class | P0 |
| Merkle proof generation | Algorithm to collect sibling hashes along path | `generate_proof()` method | P0 |
| Location determination | Extract segment index and metadata from tree | `determine_location()` | P0 |
| Output source list | API response with sources and locations | `AttributionResponse` model | P0 |

### Patent Claim 2: Plagiarism Detection Method

**Claim Text:**
> A method of identifying copied content, comprising:
> - scanning a repository of information including digital text content comprised of a plurality of text segments
> - performing the method of claim 1 on the digital text content to identify one or more candidate source documents
> - reporting to a user the one or more candidate source documents, locations in repository, and locations in source documents

#### Technical Requirements Mapping:

| Patent Element | Technical Requirement | Component | Priority |
|----------------|----------------------|-----------|----------|
| Scanning repository | Batch processing of multiple documents | `scan_repository()` | P0 |
| Plurality of text segments | Handle large document collections efficiently | Async processing | P0 |
| Perform claim 1 method | Reuse source attribution logic | Call `attribute_source()` | P0 |
| Identify candidate sources | Aggregate results across all segments | `aggregate_matches()` | P0 |
| Report locations in repository | Track original positions in target document | Position metadata | P0 |
| Report locations in sources | Include source document positions | Source metadata | P0 |
| User reporting | Generate structured report | `PlagiarismReport` model | P0 |

### Patent Claim 3: Heat Map Visualization

**Claim Text:**
> The method of claim 2, wherein the step of reporting includes generating a heat map of the locations in the repository of the one or more identified text segments.

#### Technical Requirements Mapping:

| Patent Element | Technical Requirement | Component | Priority |
|----------------|----------------------|-----------|----------|
| Heat map generation | Visual representation of match locations | `generate_heatmap()` | P1 |
| Location mapping | Map segment indices to visual positions | Position calculator | P1 |
| Identified text segments | Highlight matched vs unmatched segments | Match indicator | P1 |

### Patent Claim 4: Linked Heat Map

**Claim Text:**
> The method of claim 3, wherein the heat map includes one or more links to and/or identifiers of the corresponding locations in at least one of the source documents where the identified text segments appear.

#### Technical Requirements Mapping:

| Patent Element | Technical Requirement | Component | Priority |
|----------------|----------------------|-----------|----------|
| Links to source locations | Hyperlinks or references to source positions | Link generator | P1 |
| Source identifiers | Document IDs and segment indices | Metadata structure | P1 |
| Corresponding locations | Accurate mapping between target and source | Location mapper | P1 |

---

## 2. Additional Concepts from Patent (Dependent Claims)

### 2.1 Text Normalization

**Requirement:** Normalize both source and target text before hashing to improve matching

| Feature | Technical Requirement | Component | Priority |
|---------|----------------------|-----------|----------|
| Whitespace normalization | Remove extra spaces, tabs, newlines | `normalize_whitespace()` | P1 |
| Case normalization | Convert to lowercase for matching | `normalize_case()` | P1 |
| Punctuation handling | Optionally remove or normalize punctuation | `normalize_punctuation()` | P2 |
| Unicode normalization | NFC/NFD normalization | `normalize_unicode()` | P1 |

### 2.2 Hierarchical Segmentation

**Requirement:** Support multiple levels of segmentation hierarchy

| Feature | Technical Requirement | Component | Priority |
|---------|----------------------|-----------|----------|
| Sentence level | Split on sentence boundaries | `segment_sentences()` | P0 |
| Paragraph level | Split on paragraph markers | `segment_paragraphs()` | P0 |
| Section level | Split on section headers | `segment_sections()` | P0 |
| Hierarchical tree | Build nested structure | `build_hierarchy()` | P1 |
| Granularity slider | Allow user to choose segmentation level | API parameter | P2 |

### 2.3 Statistical Analysis

**Requirement:** Identify most likely source documents based on match statistics

| Feature | Technical Requirement | Component | Priority |
|---------|----------------------|-----------|----------|
| Match percentage | Calculate % of target segments found in each source | `calculate_match_percentage()` | P0 |
| Match count | Count number of matching segments | `count_matches()` | P0 |
| Source ranking | Rank sources by match percentage | `rank_sources()` | P0 |
| Confidence scoring | Compute confidence based on match quality | `compute_confidence()` | P1 |
| Threshold filtering | Filter sources below minimum threshold | Configurable threshold | P1 |

### 2.4 Merkle Proof Packaging

**Requirement:** Include Merkle proofs in structured data packages

| Feature | Technical Requirement | Component | Priority |
|---------|----------------------|-----------|----------|
| Proof serialization | Convert proof to portable format (JSON) | `serialize_proof()` | P0 |
| Proof verification | Allow clients to verify proofs independently | `verify_proof()` | P0 |
| Proof caching | Cache proofs for repeated queries | `merkle_proof_cache` table | P1 |
| Proof compression | Reduce proof size for transmission | Compression algorithm | P2 |

### 2.5 Near-Match Detection

**Requirement:** Find segments that are similar but not identical

| Feature | Technical Requirement | Component | Priority |
|---------|----------------------|-----------|----------|
| Fuzzy matching | Use edit distance or similarity metrics | `fuzzy_match()` | P2 |
| Transformation analysis | Detect paraphrasing, synonym substitution | NLP analysis | P3 |
| Similarity threshold | Configurable similarity threshold | API parameter | P2 |
| Near-match reporting | Include near-matches in results | Extended response | P2 |

---

## 3. Database Requirements

### 3.1 Merkle Roots Table

**Purpose:** Store root hashes for each source document's Merkle tree

| Field | Type | Constraints | Purpose |
|-------|------|-------------|---------|
| root_id | UUID | PRIMARY KEY | Unique identifier |
| organization_id | VARCHAR(255) | NOT NULL, FK | Owner organization |
| document_id | VARCHAR(255) | NOT NULL | Source document ID |
| root_hash | VARCHAR(64) | NOT NULL, INDEXED | Merkle root hash |
| tree_depth | INTEGER | NOT NULL | Tree height |
| total_leaves | INTEGER | NOT NULL | Number of leaf nodes |
| segmentation_level | VARCHAR(50) | NOT NULL | sentence/paragraph/section |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| metadata | JSONB | NULL | Additional metadata |

**Indexes:**
- `idx_root_hash` on `root_hash` for fast lookup
- `idx_document_id` on `document_id` for document queries
- `idx_org_level` on `(organization_id, segmentation_level)` for filtering

### 3.2 Merkle Sub-hashes Table

**Purpose:** Index all hashes in Merkle trees for efficient lookup

| Field | Type | Constraints | Purpose |
|-------|------|-------------|---------|
| subhash_id | UUID | PRIMARY KEY | Unique identifier |
| hash_value | VARCHAR(64) | NOT NULL, INDEXED | Hash value |
| root_id | UUID | NOT NULL, FK | Parent Merkle root |
| node_type | VARCHAR(20) | NOT NULL | leaf/branch/root |
| depth_level | INTEGER | NOT NULL | Distance from root |
| position_index | INTEGER | NOT NULL | Position in level |
| parent_hash | VARCHAR(64) | NULL | Parent node hash |
| left_child_hash | VARCHAR(64) | NULL | Left child hash |
| right_child_hash | VARCHAR(64) | NULL | Right child hash |
| text_content | TEXT | NULL | Original text (leaves only) |
| segment_metadata | JSONB | NULL | Position, length, etc. |

**Indexes:**
- `idx_hash_value` on `hash_value` for fast lookup (CRITICAL)
- `idx_root_id` on `root_id` for tree queries
- `idx_node_type` on `node_type` for filtering
- `idx_hash_root` on `(hash_value, root_id)` for combined queries

**Query Pattern:** 
```sql
-- Find all Merkle roots containing a specific hash
SELECT DISTINCT mr.* 
FROM merkle_subhashes ms
JOIN merkle_roots mr ON ms.root_id = mr.root_id
WHERE ms.hash_value = :target_hash;
```

### 3.3 Merkle Proof Cache Table

**Purpose:** Cache generated proofs for performance

| Field | Type | Constraints | Purpose |
|-------|------|-------------|---------|
| cache_id | UUID | PRIMARY KEY | Unique identifier |
| target_hash | VARCHAR(64) | NOT NULL | Hash being proved |
| root_id | UUID | NOT NULL, FK | Merkle root |
| proof_path | JSONB | NOT NULL | Array of sibling hashes |
| position_bits | BYTEA | NOT NULL | Binary path (L=0, R=1) |
| created_at | TIMESTAMP | NOT NULL | Cache creation time |
| expires_at | TIMESTAMP | NOT NULL, INDEXED | Expiration time |

**Indexes:**
- `idx_target_root` on `(target_hash, root_id)` for lookup
- `idx_expires` on `expires_at` for cleanup

**TTL:** 24 hours (configurable)

### 3.4 Attribution Reports Table

**Purpose:** Store plagiarism detection reports

| Field | Type | Constraints | Purpose |
|-------|------|-------------|---------|
| report_id | UUID | PRIMARY KEY | Unique identifier |
| organization_id | VARCHAR(255) | NOT NULL, FK | Report owner |
| target_document_id | VARCHAR(255) | NULL | Target document ID |
| target_text_hash | VARCHAR(64) | NULL | Hash of target text |
| scan_timestamp | TIMESTAMP | NOT NULL | When scan was performed |
| total_segments | INTEGER | NOT NULL | Total segments scanned |
| matched_segments | INTEGER | NOT NULL | Segments with matches |
| source_documents | JSONB | NOT NULL | Array of source matches |
| heat_map_data | JSONB | NULL | Visualization data |
| report_metadata | JSONB | NULL | Additional metadata |

**Indexes:**
- `idx_org_timestamp` on `(organization_id, scan_timestamp)` for listing

---

## 4. API Requirements

### 4.1 Document Encoding API

**Endpoint:** `POST /api/v1/enterprise/encode`

**Purpose:** Encode a source document into Merkle trees and index all hashes

**Request Schema:**
```json
{
  "text": "string (required, max 10MB)",
  "document_id": "string (required)",
  "segmentation_levels": ["sentence", "paragraph", "section"] (optional, default: ["sentence"]),
  "normalization": {
    "whitespace": true,
    "case": true,
    "punctuation": false,
    "unicode": true
  } (optional),
  "metadata": {
    "title": "string",
    "author": "string",
    "date": "string"
  } (optional)
}
```

**Response Schema:**
```json
{
  "success": true,
  "document_id": "string",
  "merkle_roots": [
    {
      "level": "sentence",
      "root_hash": "string",
      "total_leaves": 150,
      "tree_depth": 8,
      "root_id": "uuid"
    }
  ],
  "indexed_hashes": 450,
  "processing_time_ms": 1234
}
```

**Performance Requirements:**
- Process 1000 sentences in < 2 seconds
- Handle documents up to 10MB
- Return response in < 5 seconds for typical documents

### 4.2 Source Attribution API

**Endpoint:** `POST /api/v1/enterprise/attribute`

**Purpose:** Find source documents containing a specific text segment

**Request Schema:**
```json
{
  "text_segment": "string (required)",
  "segmentation_level": "sentence" (optional, default: "sentence"),
  "include_proof": true (optional, default: false),
  "normalization": {
    "whitespace": true,
    "case": true
  } (optional)
}
```

**Response Schema:**
```json
{
  "success": true,
  "found": true,
  "sources": [
    {
      "document_id": "string",
      "root_id": "uuid",
      "root_hash": "string",
      "location": {
        "segment_index": 42,
        "level": "sentence",
        "text_content": "string"
      },
      "merkle_proof": {
        "target_hash": "string",
        "proof_path": [
          {"hash": "string", "position": "left|right"}
        ],
        "verified": true
      } (if include_proof=true),
      "metadata": {
        "title": "string",
        "author": "string"
      }
    }
  ],
  "query_time_ms": 123
}
```

**Performance Requirements:**
- Query response in < 100ms
- Support concurrent queries (100+ req/sec)

### 4.3 Plagiarism Detection API

**Endpoint:** `POST /api/v1/enterprise/detect-plagiarism`

**Purpose:** Scan a document for copied content from indexed sources

**Request Schema:**
```json
{
  "target_text": "string (required)",
  "segmentation_level": "sentence" (optional),
  "min_match_threshold": 0.1 (optional, 0.0-1.0),
  "generate_heat_map": true (optional),
  "max_sources": 10 (optional),
  "normalization": {
    "whitespace": true,
    "case": true
  } (optional)
}
```

**Response Schema:**
```json
{
  "success": true,
  "report_id": "uuid",
  "summary": {
    "total_segments": 100,
    "matched_segments": 45,
    "match_percentage": 45.0,
    "unique_sources": 3,
    "scan_time_ms": 5678
  },
  "sources": [
    {
      "document_id": "string",
      "match_count": 30,
      "match_percentage": 66.7,
      "confidence": 0.95,
      "rank": 1,
      "metadata": {
        "title": "string",
        "author": "string"
      }
    }
  ],
  "heat_map": {
    "segments": [
      {
        "index": 0,
        "matched": true,
        "source_document_id": "string",
        "source_segment_index": 42
      }
    ]
  } (if generate_heat_map=true)
}
```

**Performance Requirements:**
- Process 1000 segments in < 10 seconds
- Generate heat map in < 1 second additional
- Support async processing for large documents

### 4.4 Merkle Proof Verification API

**Endpoint:** `POST /api/v1/enterprise/verify-proof`

**Purpose:** Verify a Merkle proof independently

**Request Schema:**
```json
{
  "target_hash": "string (required)",
  "root_hash": "string (required)",
  "proof_path": [
    {"hash": "string", "position": "left|right"}
  ] (required)
}
```

**Response Schema:**
```json
{
  "success": true,
  "verified": true,
  "reconstructed_root": "string",
  "matches_expected": true,
  "verification_time_ms": 5
}
```

**Performance Requirements:**
- Verify proof in < 10ms
- Support batch verification

---

## 5. Non-Functional Requirements

### 5.1 Performance

| Metric | Requirement | Measurement |
|--------|-------------|-------------|
| Tree construction | < 100ms per 1000 segments | Benchmark test |
| Hash lookup | < 50ms | Database query time |
| Proof generation | < 50ms | Algorithm execution time |
| API response time | < 500ms (p95) | Load testing |
| Concurrent requests | 100+ req/sec | Load testing |
| Database queries | < 100ms (p95) | Query profiling |

### 5.2 Scalability

| Metric | Requirement | Strategy |
|--------|-------------|----------|
| Documents per organization | 1M+ | Partitioning |
| Segments per document | 100K+ | Async processing |
| Concurrent users | 1000+ | Horizontal scaling |
| Database size | 1TB+ | Sharding |
| Query throughput | 10K+ queries/sec | Caching, indexing |

### 5.3 Reliability

| Metric | Requirement | Implementation |
|--------|-------------|----------------|
| Uptime | 99.9% | Load balancing, failover |
| Data durability | 99.999% | Database replication |
| Error rate | < 0.1% | Error handling, retries |
| Recovery time | < 5 minutes | Automated recovery |

### 5.4 Security

| Requirement | Implementation |
|-------------|----------------|
| Authentication | API key validation |
| Authorization | Tier-based access control |
| Data encryption | TLS in transit, encryption at rest |
| Input validation | Pydantic models, sanitization |
| Rate limiting | Per-organization quotas |
| Audit logging | All API calls logged |

### 5.5 Maintainability

| Requirement | Implementation |
|-------------|----------------|
| Code coverage | > 80% | Unit and integration tests |
| Documentation | Comprehensive API docs | OpenAPI/Swagger |
| Monitoring | Metrics and alerts | Prometheus, Grafana |
| Logging | Structured logging | JSON logs |
| Versioning | Semantic versioning | Git tags |

---

## 6. Acceptance Criteria

### 6.1 Functional Acceptance

- [ ] Document encoding creates Merkle trees at all specified levels
- [ ] All hashes are indexed in database for lookup
- [ ] Source attribution finds all matching sources
- [ ] Merkle proofs are generated correctly
- [ ] Merkle proofs can be verified independently
- [ ] Plagiarism detection identifies copied content
- [ ] Statistical analysis ranks sources correctly
- [ ] Heat maps visualize match locations
- [ ] API responses match schema specifications
- [ ] Error handling covers all edge cases

### 6.2 Performance Acceptance

- [ ] Tree construction meets performance targets
- [ ] Database queries meet latency targets
- [ ] API endpoints meet response time targets
- [ ] System handles target concurrent load
- [ ] No memory leaks under sustained load

### 6.3 Security Acceptance

- [ ] Tier-based access control enforced
- [ ] API keys validated on all requests
- [ ] Quotas enforced correctly
- [ ] Input validation prevents injection attacks
- [ ] Sensitive data encrypted

### 6.4 Quality Acceptance

- [ ] Code coverage > 80%
- [ ] All tests passing
- [ ] No critical bugs
- [ ] Documentation complete
- [ ] Code review approved

---

## 7. Dependencies and Constraints

### 7.1 External Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| PostgreSQL | 14+ | Database |
| Redis | 6+ | Caching |
| Python | 3.10+ | Runtime |
| FastAPI | 0.100+ | Web framework |
| SQLAlchemy | 2.0+ | ORM |
| Pydantic | 2.0+ | Data validation |

### 7.2 Constraints

- Must maintain backward compatibility with Free tier
- Must not impact existing API performance
- Database migrations must be reversible
- Must support existing authentication system
- Must work with current deployment infrastructure

### 7.3 Assumptions

- Organizations will upgrade to Enterprise tier for advanced features
- Average document size is < 1MB
- Most queries will be for recent documents
- Proof verification will be done client-side in most cases
- Heat maps will be generated on-demand, not pre-computed

---

## 8. Open Questions

1. **Q:** Should we support custom hash algorithms beyond SHA-256?
   **A:** TBD - Start with SHA-256, add extensibility for future

2. **Q:** How long should we retain attribution reports?
   **A:** TBD - Propose 90 days default, configurable per organization

3. **Q:** Should near-match detection be in MVP or Phase 2?
   **A:** TBD - Recommend Phase 2 due to complexity

4. **Q:** What is the pricing model for Enterprise tier?
   **A:** TBD - Business team to define

5. **Q:** Should we support bulk document encoding via batch API?
   **A:** TBD - Recommend yes for large customers

---

## 9. Next Steps

1. **Review this document** with stakeholders
2. **Get sign-off** on requirements
3. **Proceed to Task 1.2** (Database Schema Design)
4. **Update WBS** based on any requirement changes

---

**Document Status:** Ready for Review  
**Prepared by:** Claude (AI Assistant)  
**Review Required:** Tech Lead, Product Manager, Legal  
**Target Approval Date:** 2025-10-29
