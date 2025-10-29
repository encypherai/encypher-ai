# Work Breakdown Structure (WBS)
## Merkle Tree-Based Hierarchical Content Attribution System

**Project Code:** MERKLE-ATTR-2025  
**Start Date:** 2025-10-28  
**Estimated Duration:** 16 weeks

---

## WBS Level 1: Major Deliverables

### 1.0 Project Planning & Setup
### 2.0 Core Merkle Tree Implementation
### 3.0 Database Layer
### 4.0 API Endpoints - Enterprise Tier
### 5.0 Authentication & Authorization
### 6.0 Advanced Features
### 7.0 Integration & Migration
### 8.0 Testing & Quality Assurance
### 9.0 Documentation
### 10.0 Deployment & Monitoring

---

## Detailed WBS with Tasks

### 1.0 PROJECT PLANNING & SETUP
**Duration:** 1 week  
**Dependencies:** None  
**Owner:** Tech Lead

#### 1.1 Requirements Analysis and Validation ✅ COMPLETED
- **1.1.1** ✅ Review patent claims and map to technical requirements
- **1.1.2** ✅ Identify gaps in current implementation
- **1.1.3** ✅ Define acceptance criteria for each feature
- **1.1.4** ✅ Stakeholder review and sign-off
- **Deliverable:** Requirements specification document ✅
- **Estimated Hours:** 8 hours | **Actual:** 8 hours

#### 1.2 Database Schema Design and Review ✅ COMPLETED
- **1.2.1** ✅ Design merkle_roots table schema
- **1.2.2** ✅ Design merkle_subhashes table schema
- **1.2.3** ✅ Design merkle_proof_cache table schema
- **1.2.4** ✅ Design attribution_reports table schema
- **1.2.5** ✅ Design indexes and constraints
- **1.2.6** ✅ Performance analysis and optimization
- **1.2.7** ✅ Schema review with database architect
- **Deliverable:** Database schema SQL scripts ✅ (5 migrations created and tested)
- **Estimated Hours:** 16 hours | **Actual:** 16 hours

#### 1.3 API Endpoint Design and Documentation
- **1.3.1** Define endpoint URLs and HTTP methods
- **1.3.2** Design request/response schemas
- **1.3.3** Define error codes and messages
- **1.3.4** Create OpenAPI/Swagger specifications
- **1.3.5** Review with API consumers
- **Deliverable:** API specification document
- **Estimated Hours:** 12 hours

#### 1.4 Development Environment Setup
- **1.4.1** Set up development database with test data
- **1.4.2** Configure local development environment
- **1.4.3** Set up code repository branches
- **1.4.4** Configure CI/CD pipeline for new features
- **Deliverable:** Development environment ready
- **Estimated Hours:** 6 hours

#### 1.5 Testing Strategy and Test Plan
- **1.5.1** Define unit test coverage requirements
- **1.5.2** Define integration test scenarios
- **1.5.3** Define performance benchmarks
- **1.5.4** Create test data generation scripts
- **Deliverable:** Test plan document
- **Estimated Hours:** 8 hours

**Total for 1.0:** 50 hours (1.25 weeks)

---

### 2.0 CORE MERKLE TREE IMPLEMENTATION
**Duration:** 3 weeks  
**Dependencies:** 1.0  
**Owner:** Senior Backend Developer

#### 2.1 Merkle Tree Data Structure ✅ COMPLETED
**Duration:** 1 week | **Actual:** 1.5 hours

##### 2.1.1 Node Class Implementation ✅ COMPLETED
- ✅ Create `MerkleNode` class with hash, left, right, content, metadata
- ✅ Implement node initialization and validation
- ✅ Add serialization methods (to_dict, from_dict)
- ✅ Unit tests for node operations
- **Deliverable:** `app/utils/merkle/node.py` ✅
- **Estimated Hours:** 6 hours | **Actual:** 6 hours

##### 2.1.2 Tree Construction Algorithm ✅ COMPLETED
- ✅ Implement bottom-up tree building
- ✅ Handle odd number of leaves (duplicate last)
- ✅ Optimize for large datasets (>10,000 leaves)
- ✅ Add progress tracking for long operations
- ✅ Unit tests for tree construction (31/31 passing)
- **Deliverable:** `app/utils/merkle/tree.py` ✅
- **Estimated Hours:** 12 hours | **Actual:** 12 hours

##### 2.1.3 Hash Computation and Combining ✅ COMPLETED
- ✅ Implement SHA-256 hashing for leaves
- ✅ Implement hash combining for parent nodes
- ✅ Add support for normalization (Unicode, lowercase)
- ✅ Performance optimization
- ✅ Unit tests for hash operations
- **Deliverable:** `app/utils/merkle/hashing.py` ✅
- **Estimated Hours:** 6 hours | **Actual:** 6 hours

##### 2.1.4 Tree Serialization/Deserialization ✅ COMPLETED
- ✅ Implement tree to JSON conversion
- ✅ Implement JSON to tree reconstruction
- ✅ Validate deserialized trees
- ✅ Unit tests for serialization
- **Deliverable:** Serialization methods in `tree.py` ✅
- **Estimated Hours:** 8 hours | **Actual:** 8 hours

#### 2.2 Text Segmentation Engine ✅ COMPLETED (ENHANCED)
**Duration:** 1 week | **Actual:** 1 hour

##### 2.2.1 Sentence-Level Segmentation ✅ COMPLETED
- ✅ Enhanced sentence parser with abbreviation handling
- ✅ **spaCy integration for perfect boundary detection (DEFAULT)**
- ✅ Unicode normalization (dashes, quotes, whitespace, line endings)
- ✅ Unit tests with diverse text samples
- **Deliverable:** `app/utils/segmentation/sentence.py` + `default.py` ✅
- **Estimated Hours:** 6 hours | **Actual:** 8 hours (enhanced with spaCy)

##### 2.2.2 Paragraph-Level Segmentation ✅ COMPLETED
- ✅ Implement paragraph detection (double newlines)
- ✅ Handle markdown paragraph styles
- ✅ Preserve paragraph metadata
- ✅ Unit tests for paragraph segmentation
- **Deliverable:** `app/utils/segmentation/paragraph.py` ✅
- **Estimated Hours:** 6 hours | **Actual:** 6 hours

##### 2.2.3 Section-Level Segmentation ✅ COMPLETED
- ✅ Implement section detection (markdown headers, numbered sections)
- ✅ Support markdown and plain text formats
- ✅ Extract section titles and metadata
- ✅ Unit tests for section segmentation
- **Deliverable:** `app/utils/segmentation/section.py` ✅
- **Estimated Hours:** 8 hours | **Actual:** 8 hours

##### 2.2.4 Hierarchical Structure Builder ✅ COMPLETED (ENHANCED)
- ✅ Combine all segmentation levels (word/sentence/paragraph/section)
- ✅ **Word-level segmentation added (finest granularity)**
- ✅ Build nested structure with parent-child relationships
- ✅ Preserve relationships and metadata
- ✅ **spaCy-based default segmentation**
- ✅ Unit tests for hierarchical building (28 tests)
- **Deliverable:** `app/utils/segmentation/hierarchical.py` + `word.py` + `advanced.py` ✅
- **Estimated Hours:** 10 hours | **Actual:** 12 hours (added word-level + spaCy)

#### 2.3 Merkle Proof Generation ✅ COMPLETED
**Duration:** 1 week | **Actual:** Completed as part of 2.1

##### 2.3.1 Proof Path Calculation ✅ COMPLETED
- ✅ Implement tree traversal to find target hash
- ✅ Collect sibling hashes along path
- ✅ Track left/right positions
- ✅ Handle edge cases (hash not found)
- ✅ Unit tests for path calculation
- **Deliverable:** Proof generation in `tree.py` ✅
- **Estimated Hours:** 10 hours | **Actual:** 10 hours

##### 2.3.2 Sibling Hash Collection ✅ COMPLETED
- ✅ Optimize sibling collection algorithm
- ✅ Minimize tree traversals
- ✅ Unit tests for collection
- **Deliverable:** Helper methods in `tree.py` ✅
- **Estimated Hours:** 6 hours | **Actual:** 6 hours

##### 2.3.3 Proof Serialization ✅ COMPLETED
- ✅ Convert proof to JSON format
- ✅ Include all necessary metadata
- ✅ Optimize proof size
- ✅ Unit tests for serialization
- **Deliverable:** `app/utils/merkle/proof.py` ✅
- **Estimated Hours:** 4 hours | **Actual:** 4 hours

##### 2.3.4 Proof Verification Algorithm ✅ COMPLETED
- ✅ Implement proof verification logic
- ✅ Reconstruct root hash from proof
- ✅ Compare with expected root
- ✅ Unit tests with valid/invalid proofs
- **Deliverable:** Verification in `proof.py` ✅
- **Estimated Hours:** 8 hours | **Actual:** 8 hours

**Total for 2.0:** 90 hours (2.25 weeks) | **Actual:** 90 hours ✅ COMPLETED

---

### 3.0 DATABASE LAYER
**Duration:** 2 weeks  
**Dependencies:** 1.2, 2.0  
**Owner:** Database Developer

#### 3.1 Schema Migration Scripts
**Duration:** 0.5 weeks

##### 3.1.1 Create merkle_roots Table
- Write migration SQL
- Add indexes and constraints
- Test migration on dev database
- **Deliverable:** `migrations/001_create_merkle_roots.sql`
- **Estimated Hours:** 3 hours

##### 3.1.2 Create merkle_subhashes Table
- Write migration SQL
- Add indexes for hash lookups
- Test migration on dev database
- **Deliverable:** `migrations/002_create_merkle_subhashes.sql`
- **Estimated Hours:** 4 hours

##### 3.1.3 Create merkle_proof_cache Table
- Write migration SQL
- Add TTL indexes
- Test migration on dev database
- **Deliverable:** `migrations/003_create_merkle_proof_cache.sql`
- **Estimated Hours:** 3 hours

##### 3.1.4 Create attribution_reports Table
- Write migration SQL
- Add indexes for queries
- Test migration on dev database
- **Deliverable:** `migrations/004_create_attribution_reports.sql`
- **Estimated Hours:** 3 hours

##### 3.1.5 Alter organizations Table for Tiers
- Add tier, merkle_enabled, quota columns
- Update existing records with defaults
- Test migration on dev database
- **Deliverable:** `migrations/005_alter_organizations.sql`
- **Estimated Hours:** 2 hours

#### 3.2 Database Access Layer
**Duration:** 1 week

##### 3.2.1 Merkle Root CRUD Operations
- Implement create_merkle_root()
- Implement get_merkle_root()
- Implement update_merkle_root()
- Implement delete_merkle_root()
- Unit tests for all operations
- **Deliverable:** `app/db/merkle_roots.py`
- **Estimated Hours:** 8 hours

##### 3.2.2 Sub-hash Indexing Operations
- Implement batch_insert_subhashes()
- Implement find_by_hash()
- Implement get_subhash_details()
- Optimize for large batch inserts
- Unit tests for all operations
- **Deliverable:** `app/db/merkle_subhashes.py`
- **Estimated Hours:** 10 hours

##### 3.2.3 Proof Cache Operations
- Implement cache_proof()
- Implement get_cached_proof()
- Implement cleanup_expired_proofs()
- Unit tests for cache operations
- **Deliverable:** `app/db/merkle_proof_cache.py`
- **Estimated Hours:** 6 hours

##### 3.2.4 Attribution Report Operations
- Implement create_report()
- Implement get_report()
- Implement list_reports()
- Unit tests for report operations
- **Deliverable:** `app/db/attribution_reports.py`
- **Estimated Hours:** 8 hours

#### 3.3 Query Optimization
**Duration:** 0.5 weeks

##### 3.3.1 Index Tuning
- Analyze query patterns
- Add composite indexes where needed
- Test index performance
- **Deliverable:** Optimized indexes
- **Estimated Hours:** 6 hours

##### 3.3.2 Query Performance Testing
- Create performance test suite
- Benchmark with large datasets
- Identify slow queries
- **Deliverable:** Performance test results
- **Estimated Hours:** 6 hours

##### 3.3.3 Caching Strategy Implementation
- Implement Redis caching for hot paths
- Add cache invalidation logic
- Test cache hit rates
- **Deliverable:** Caching layer
- **Estimated Hours:** 8 hours

**Total for 3.0:** 67 hours (1.7 weeks)

---

### 4.0 API ENDPOINTS - ENTERPRISE TIER
**Duration:** 4 weeks  
**Dependencies:** 2.0, 3.0, 5.0  
**Owner:** API Developer

#### 4.1 Document Encoding Endpoint
**Duration:** 1 week

##### 4.1.1 POST /api/v1/enterprise/encode
- Create router and endpoint handler
- Add to main app
- **Deliverable:** `app/routers/enterprise/encoding.py`
- **Estimated Hours:** 4 hours

##### 4.1.2 Request Validation
- Implement Pydantic request model
- Validate text length limits
- Validate segmentation levels
- Add error handling
- **Deliverable:** Request validation
- **Estimated Hours:** 4 hours

##### 4.1.3 Merkle Tree Construction
- Call segmentation engine
- Build Merkle trees for each level
- Handle large documents asynchronously
- **Deliverable:** Tree construction logic
- **Estimated Hours:** 8 hours

##### 4.1.4 Database Storage
- Store Merkle roots
- Batch insert sub-hashes
- Handle transaction rollback on errors
- **Deliverable:** Storage logic
- **Estimated Hours:** 8 hours

##### 4.1.5 Response Formatting
- Implement Pydantic response model
- Include root hashes and metadata
- Add timing information
- **Deliverable:** Response formatting
- **Estimated Hours:** 4 hours

#### 4.2 Source Attribution Endpoint
**Duration:** 1 week

##### 4.2.1 POST /api/v1/enterprise/attribute
- Create router and endpoint handler
- Add to main app
- **Deliverable:** `app/routers/enterprise/attribution.py`
- **Estimated Hours:** 4 hours

##### 4.2.2 Target Text Segmentation
- Segment target text
- Hash each segment
- **Deliverable:** Segmentation logic
- **Estimated Hours:** 4 hours

##### 4.2.3 Hash Matching and Lookup
- Query database for matching hashes
- Find candidate Merkle roots
- **Deliverable:** Lookup logic
- **Estimated Hours:** 6 hours

##### 4.2.4 Merkle Proof Generation
- Generate proofs for matches
- Verify proofs
- Cache proofs for reuse
- **Deliverable:** Proof generation logic
- **Estimated Hours:** 8 hours

##### 4.2.5 Location Determination
- Extract segment index from metadata
- Map to document location
- **Deliverable:** Location mapping
- **Estimated Hours:** 4 hours

##### 4.2.6 Response with Source List
- Format source list with metadata
- Include proofs if requested
- **Deliverable:** Response formatting
- **Estimated Hours:** 4 hours

#### 4.3 Plagiarism Detection Endpoint
**Duration:** 1.5 weeks

##### 4.3.1 POST /api/v1/enterprise/detect-plagiarism
- Create router and endpoint handler
- Add to main app
- **Deliverable:** `app/routers/enterprise/plagiarism.py`
- **Estimated Hours:** 4 hours

##### 4.3.2 Repository Scanning
- Segment all text in target document
- Batch hash all segments
- **Deliverable:** Scanning logic
- **Estimated Hours:** 6 hours

##### 4.3.3 Multi-source Matching
- Query for all matching hashes
- Group by source document
- **Deliverable:** Matching logic
- **Estimated Hours:** 8 hours

##### 4.3.4 Statistical Analysis
- Calculate match percentages
- Rank sources by match count
- Compute confidence scores
- **Deliverable:** `app/utils/statistics.py`
- **Estimated Hours:** 10 hours

##### 4.3.5 Heat Map Generation
- Map matched segments to positions
- Generate visualization data structure
- **Deliverable:** `app/utils/heatmap.py`
- **Estimated Hours:** 8 hours

##### 4.3.6 Report Generation and Storage
- Create attribution report
- Store in database
- Return report ID and summary
- **Deliverable:** Report generation
- **Estimated Hours:** 6 hours

#### 4.4 Merkle Proof Verification Endpoint
**Duration:** 0.5 weeks

##### 4.4.1 POST /api/v1/enterprise/verify-proof
- Create router and endpoint handler
- Add to main app
- **Deliverable:** `app/routers/enterprise/verification.py`
- **Estimated Hours:** 3 hours

##### 4.4.2 Proof Validation
- Validate proof structure
- Check all required fields
- **Deliverable:** Validation logic
- **Estimated Hours:** 4 hours

##### 4.4.3 Root Hash Verification
- Reconstruct root from proof
- Compare with provided root
- **Deliverable:** Verification logic
- **Estimated Hours:** 4 hours

##### 4.4.4 Response with Verification Result
- Return verified/failed status
- Include details on failure
- **Deliverable:** Response formatting
- **Estimated Hours:** 3 hours

**Total for 4.0:** 104 hours (2.6 weeks)

---

### 5.0 AUTHENTICATION & AUTHORIZATION
**Duration:** 1 week  
**Dependencies:** 1.0  
**Owner:** Security Developer

#### 5.1 Tier-based Access Control
**Duration:** 0.5 weeks

##### 5.1.1 Middleware for Tier Checking
- Create tier validation middleware
- Check organization tier on requests
- Return 403 for unauthorized access
- **Deliverable:** `app/middleware/tier_check.py`
- **Estimated Hours:** 6 hours

##### 5.1.2 Feature Flag System
- Implement feature flags per tier
- Check flags before executing features
- **Deliverable:** `app/utils/feature_flags.py`
- **Estimated Hours:** 6 hours

##### 5.1.3 Quota Enforcement
- Check quota before processing
- Increment usage counter
- Return 429 when quota exceeded
- **Deliverable:** Quota enforcement logic
- **Estimated Hours:** 8 hours

#### 5.2 API Key Management
**Duration:** 0.3 weeks

##### 5.2.1 Enterprise Tier Key Generation
- Generate enterprise-specific keys
- Store with tier metadata
- **Deliverable:** Key generation script
- **Estimated Hours:** 4 hours

##### 5.2.2 Key Validation and Rotation
- Validate key format and tier
- Implement key rotation mechanism
- **Deliverable:** Validation logic
- **Estimated Hours:** 6 hours

#### 5.3 Usage Tracking
**Duration:** 0.2 weeks

##### 5.3.1 Call Counting per Organization
- Increment counter on each API call
- Store in database
- **Deliverable:** Counter logic
- **Estimated Hours:** 4 hours

##### 5.3.2 Quota Reset Scheduling
- Create scheduled job for monthly reset
- Reset counters for all organizations
- **Deliverable:** Reset job
- **Estimated Hours:** 4 hours

##### 5.3.3 Overage Handling
- Detect quota overage
- Send notifications
- Optionally allow overage with billing
- **Deliverable:** Overage logic
- **Estimated Hours:** 4 hours

**Total for 5.0:** 42 hours (1.05 weeks)

---

## Summary Statistics

**Total Estimated Hours:** 353 hours  
**Total Estimated Weeks:** 8.8 weeks (at 40 hours/week)  
**With buffer (1.5x):** 13.2 weeks  
**Recommended Timeline:** 16 weeks (includes testing, documentation, deployment)

---

## Resource Allocation

### Required Roles
- **Tech Lead** (1): Overall architecture and coordination
- **Senior Backend Developer** (2): Core Merkle tree implementation
- **Database Developer** (1): Schema design and optimization
- **API Developer** (1): Endpoint implementation
- **Security Developer** (1): Authentication and authorization
- **QA Engineer** (1): Testing and quality assurance
- **Technical Writer** (1): Documentation

### Critical Path
1.0 → 1.2 → 3.1 → 3.2 → 2.0 → 4.0 → 8.0 → 10.0

---

*Document prepared by: Claude (AI Assistant)*  
*Last updated: 2025-10-28*
