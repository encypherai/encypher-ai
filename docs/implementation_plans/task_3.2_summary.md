# Task 3.2: Database Access Layer - COMPLETED ✅

**Date:** 2025-10-28  
**Duration:** 1 hour  
**Status:** Fully Implemented and Tested

---

## Deliverables

### 1. SQLAlchemy Models (`app/models/merkle.py`)

Created comprehensive ORM models for all Merkle-related tables:

#### **MerkleRoot**
- Stores root hashes and metadata for Merkle trees
- Tracks tree depth, total leaves, segmentation level
- Foreign key to organizations
- Relationships to subhashes and proof cache

#### **MerkleSubhash**
- Index of all hashes (leaves and branches) in trees
- Enables efficient lookup of any hash value
- Stores node type, depth, position, parent/child relationships
- Preserves original text content for leaf nodes

#### **MerkleProofCache**
- Caches generated Merkle proofs
- Automatic expiration (24-hour TTL)
- Stores proof path and position bits

#### **AttributionReport**
- Plagiarism detection and source attribution reports
- Tracks matched segments, source documents
- Includes heat map visualization data
- Check constraints for data integrity

### 2. CRUD Operations (`app/crud/merkle.py`)

Implemented async CRUD operations following repository pattern:

#### **MerkleRoot Operations:**
- `create_merkle_root()` - Create new root entry
- `get_merkle_root_by_id()` - Retrieve by ID
- `get_merkle_roots_by_document()` - Get all roots for a document
- `get_merkle_roots_by_organization()` - Paginated org query
- `delete_merkle_root()` - Delete with cascade

#### **MerkleSubhash Operations:**
- `create_merkle_subhash()` - Create single subhash
- `bulk_create_merkle_subhashes()` - Bulk insert for performance
- `find_subhashes_by_hash()` - Core attribution lookup
- `find_subhashes_by_root()` - Get all subhashes for a tree
- `batch_find_subhashes()` - Efficient multi-hash lookup

#### **MerkleProofCache Operations:**
- `create_proof_cache()` - Cache a proof
- `get_cached_proof()` - Retrieve non-expired proof
- `delete_expired_proofs()` - Cleanup expired entries

#### **AttributionReport Operations:**
- `create_attribution_report()` - Create new report
- `get_attribution_report()` - Retrieve by ID
- `get_attribution_reports_by_organization()` - Paginated query
- `delete_attribution_report()` - Delete report

### 3. Service Layer (`app/services/merkle_service.py`)

High-level business logic combining CRUD with Merkle tree operations:

#### **MerkleService Methods:**

**`encode_document()`**
- Segments text at multiple levels
- Builds Merkle trees for each level
- Stores roots and all subhashes in database
- Returns dictionary of MerkleRoot instances

**`find_sources()`**
- Finds source documents containing a text segment
- Normalizes text before hashing
- Returns list of (subhash, root) tuples

**`generate_attribution_report()`**
- Comprehensive plagiarism detection
- Segments target text and checks each segment
- Aggregates matches by source document
- Calculates match percentages and confidence scores
- Generates heat map visualization data
- Creates and stores AttributionReport

**`verify_segment_in_document()`**
- Verifies a segment exists in a specific document
- Checks proof cache first for performance
- Returns MerkleProof if found

### 4. Unit Tests (`tests/test_merkle_crud.py`)

Comprehensive test suite with 12 tests covering all CRUD operations:

- **TestMerkleRootCRUD** (4 tests)
  - Create, retrieve, filter, delete operations
  - Multi-level segmentation support

- **TestMerkleSubhashCRUD** (4 tests)
  - Single and bulk creation
  - Hash-based and root-based queries
  - Batch lookup operations

- **TestMerkleProofCacheCRUD** (2 tests)
  - Cache creation and retrieval
  - Expiration handling

- **TestAttributionReportCRUD** (2 tests)
  - Report creation
  - Organization-based queries

---

## Key Features

### ✅ Best Practices Implemented

1. **Repository Pattern**
   - Clean separation of concerns
   - Database logic isolated from business logic

2. **Async/Await Throughout**
   - All operations are async for performance
   - Non-blocking database access

3. **Eager Loading**
   - Uses `selectinload()` to avoid N+1 queries
   - Efficient relationship loading

4. **Bulk Operations**
   - `bulk_create_merkle_subhashes()` for performance
   - `batch_find_subhashes()` for efficient multi-hash lookup

5. **Pagination Support**
   - `limit` and `offset` parameters
   - Prevents memory issues with large datasets

6. **Caching Strategy**
   - Proof cache with TTL
   - Automatic expiration cleanup

7. **Data Integrity**
   - Check constraints on models
   - Foreign key relationships with cascade delete
   - Proper indexing for performance

### ✅ Performance Optimizations

1. **Indexes Created:**
   - `idx_merkle_roots_org_level` - Organization + level queries
   - `idx_merkle_roots_created_at` - Time-based queries
   - `idx_merkle_subhashes_hash_root` - Hash + root lookups
   - `idx_merkle_proof_cache_target_root` - Proof cache lookups
   - `idx_attribution_reports_org_timestamp` - Report queries

2. **Bulk Operations:**
   - Bulk insert for subhashes (1 query vs N queries)
   - Batch find for multiple hashes

3. **Relationship Loading:**
   - Eager loading with `selectinload()`
   - Prevents N+1 query problems

---

## Database Schema Alignment

All models align with migrations 006-010:

| Model | Table | Migration |
|-------|-------|-----------|
| MerkleRoot | merkle_roots | 006 |
| MerkleSubhash | merkle_subhashes | 007 |
| MerkleProofCache | merkle_proof_cache | 008 |
| AttributionReport | attribution_reports | 009 |

**Note:** Column name changes to avoid SQLAlchemy reserved words:
- `metadata` → `doc_metadata` (in Python, maps to `metadata` in DB)
- `segment_metadata` → `seg_metadata`
- `report_metadata` → `report_meta`

---

## Test Results

```
tests/test_merkle_crud.py::TestMerkleRootCRUD::test_create_merkle_root PASSED
tests/test_merkle_crud.py::TestMerkleRootCRUD::test_get_merkle_root_by_id PASSED
tests/test_merkle_crud.py::TestMerkleRootCRUD::test_get_merkle_roots_by_document PASSED
tests/test_merkle_crud.py::TestMerkleRootCRUD::test_delete_merkle_root PASSED
tests/test_merkle_crud.py::TestMerkleSubhashCRUD::test_create_merkle_subhash PASSED
tests/test_merkle_crud.py::TestMerkleSubhashCRUD::test_bulk_create_subhashes PASSED
tests/test_merkle_crud.py::TestMerkleSubhashCRUD::test_find_subhashes_by_hash PASSED
tests/test_merkle_crud.py::TestMerkleSubhashCRUD::test_batch_find_subhashes PASSED
tests/test_merkle_crud.py::TestMerkleProofCacheCRUD::test_create_and_get_cached_proof PASSED
tests/test_merkle_crud.py::TestMerkleProofCacheCRUD::test_expired_proof_not_returned PASSED
tests/test_merkle_crud.py::TestAttributionReportCRUD::test_create_attribution_report PASSED
tests/test_merkle_crud.py::TestAttributionReportCRUD::test_get_attribution_reports_by_organization PASSED

12/12 tests passing ✅
Total project tests: 102/102 passing ✅
```

---

## Files Created

1. `app/models/merkle.py` (155 lines)
2. `app/crud/merkle.py` (490 lines)
3. `app/services/merkle_service.py` (280 lines)
4. `tests/test_merkle_crud.py` (380 lines)

**Total:** 1,305 lines of production code + tests

---

## Usage Examples

### Encoding a Document

```python
from app.services.merkle_service import MerkleService

# Encode document at multiple levels
roots = await MerkleService.encode_document(
    db=db,
    organization_id="org_123",
    document_id="doc_456",
    text="Document text here...",
    segmentation_levels=["sentence", "paragraph"],
    metadata={"title": "My Document", "author": "John Doe"}
)

# Returns: {'sentence': MerkleRoot(...), 'paragraph': MerkleRoot(...)}
```

### Finding Sources

```python
# Find which documents contain a specific text segment
sources = await MerkleService.find_sources(
    db=db,
    text_segment="This is a copied sentence.",
    segmentation_level="sentence"
)

# Returns: [(MerkleSubhash, MerkleRoot), ...]
```

### Generating Attribution Report

```python
# Generate plagiarism detection report
report = await MerkleService.generate_attribution_report(
    db=db,
    organization_id="org_123",
    target_text="Text to check for plagiarism...",
    segmentation_level="sentence",
    include_heat_map=True
)

# Returns: AttributionReport with matched segments and source documents
```

---

## Next Steps

**Task 4.1: Document Encoding Endpoint**
- Create FastAPI endpoint for document encoding
- Input validation with Pydantic
- Rate limiting and quota enforcement
- Response formatting

---

*Implementation completed: 2025-10-28*  
*Ready for API endpoint integration*
