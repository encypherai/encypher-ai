# Merkle Tree-Based Hierarchical Content Attribution System
## Implementation Plan for Enterprise API

**Version:** 1.0  
**Date:** 2025-10-28  
**Status:** Planning Phase

---

## Executive Summary

This document outlines the implementation plan for adding a Merkle tree-based hierarchical content attribution system to the EncypherAI Enterprise API. The system will be offered as a premium "Enterprise" tier feature, while maintaining the existing basic C2PA embedding as a "Free" tier.

### Key Objectives
1. Implement Merkle tree construction for hierarchical text segmentation
2. Create efficient database indexing for sub-hash lookup
3. Build Merkle proof generation and verification
4. Develop plagiarism detection and source attribution APIs
5. Maintain backward compatibility with existing Free tier

### Business Model
- **Free Tier**: Basic C2PA manifest embedding (current functionality)
- **Enterprise Tier**: Merkle tree attribution + advanced features (new)

---

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Enterprise API                            │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐         ┌──────────────────────┐          │
│  │  Free Tier   │         │   Enterprise Tier    │          │
│  │              │         │                      │          │
│  │ • C2PA Sign  │         │ • Merkle Tree Build  │          │
│  │ • C2PA Verify│         │ • Source Attribution │          │
│  │ • Basic Lookup│        │ • Merkle Proofs      │          │
│  └──────────────┘         │ • Heat Maps          │          │
│                           │ • Statistical Analysis│          │
│                           └──────────────────────┘          │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│                    Shared Services                           │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  • Text Segmentation (sentence/paragraph/section)            │
│  • Cryptographic Hashing (SHA-256)                           │
│  • Database Access Layer                                     │
│  • Authentication & Authorization                            │
│  • Rate Limiting & Quota Management                          │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Database Schema Extensions

```sql
-- Merkle tree roots for source documents
CREATE TABLE merkle_roots (
    root_id UUID PRIMARY KEY,
    organization_id VARCHAR(255) NOT NULL,
    document_id VARCHAR(255) NOT NULL,
    root_hash VARCHAR(64) NOT NULL,
    tree_depth INTEGER NOT NULL,
    total_leaves INTEGER NOT NULL,
    segmentation_level VARCHAR(50) NOT NULL, -- 'sentence', 'paragraph', 'section'
    created_at TIMESTAMP NOT NULL,
    metadata JSONB,
    FOREIGN KEY (organization_id) REFERENCES organizations(organization_id),
    INDEX idx_root_hash (root_hash),
    INDEX idx_document_id (document_id)
);

-- Sub-hash index for efficient lookup
CREATE TABLE merkle_subhashes (
    subhash_id UUID PRIMARY KEY,
    hash_value VARCHAR(64) NOT NULL,
    root_id UUID NOT NULL,
    node_type VARCHAR(20) NOT NULL, -- 'leaf', 'branch', 'root'
    depth_level INTEGER NOT NULL,
    position_index INTEGER NOT NULL,
    parent_hash VARCHAR(64),
    left_child_hash VARCHAR(64),
    right_child_hash VARCHAR(64),
    text_content TEXT, -- Only for leaf nodes
    segment_metadata JSONB, -- location, length, etc.
    FOREIGN KEY (root_id) REFERENCES merkle_roots(root_id) ON DELETE CASCADE,
    INDEX idx_hash_value (hash_value),
    INDEX idx_root_id (root_id),
    INDEX idx_node_type (node_type)
);

-- Merkle proof cache for common queries
CREATE TABLE merkle_proof_cache (
    cache_id UUID PRIMARY KEY,
    target_hash VARCHAR(64) NOT NULL,
    root_id UUID NOT NULL,
    proof_path JSONB NOT NULL, -- Array of sibling hashes
    position_bits BYTEA NOT NULL, -- Binary path (left=0, right=1)
    created_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    FOREIGN KEY (root_id) REFERENCES merkle_roots(root_id) ON DELETE CASCADE,
    INDEX idx_target_root (target_hash, root_id),
    INDEX idx_expires (expires_at)
);

-- Attribution reports (for plagiarism detection)
CREATE TABLE attribution_reports (
    report_id UUID PRIMARY KEY,
    organization_id VARCHAR(255) NOT NULL,
    target_document_id VARCHAR(255),
    target_text_hash VARCHAR(64),
    scan_timestamp TIMESTAMP NOT NULL,
    total_segments INTEGER NOT NULL,
    matched_segments INTEGER NOT NULL,
    source_documents JSONB NOT NULL, -- Array of {doc_id, match_count, match_percentage}
    heat_map_data JSONB, -- Visualization data
    report_metadata JSONB,
    FOREIGN KEY (organization_id) REFERENCES organizations(organization_id),
    INDEX idx_org_timestamp (organization_id, scan_timestamp)
);

-- Tier configuration
ALTER TABLE organizations ADD COLUMN tier VARCHAR(50) DEFAULT 'free';
ALTER TABLE organizations ADD COLUMN merkle_enabled BOOLEAN DEFAULT FALSE;
ALTER TABLE organizations ADD COLUMN monthly_merkle_quota INTEGER DEFAULT 0;
ALTER TABLE organizations ADD COLUMN merkle_calls_this_month INTEGER DEFAULT 0;
```

---

## Work Breakdown Structure (WBS)

### 1.0 Project Planning & Setup
- **1.1** Requirements analysis and validation
- **1.2** Database schema design and review
- **1.3** API endpoint design and documentation
- **1.4** Development environment setup
- **1.5** Testing strategy and test plan

### 2.0 Core Merkle Tree Implementation
- **2.1** Merkle tree data structure
  - **2.1.1** Node class implementation
  - **2.1.2** Tree construction algorithm
  - **2.1.3** Hash computation and combining
  - **2.1.4** Tree serialization/deserialization
- **2.2** Text segmentation engine
  - **2.2.1** Sentence-level segmentation
  - **2.2.2** Paragraph-level segmentation
  - **2.2.3** Section-level segmentation
  - **2.2.4** Hierarchical structure builder
- **2.3** Merkle proof generation
  - **2.3.1** Proof path calculation
  - **2.3.2** Sibling hash collection
  - **2.3.3** Proof serialization
  - **2.3.4** Proof verification algorithm

### 3.0 Database Layer
- **3.1** Schema migration scripts
  - **3.1.1** Create merkle_roots table
  - **3.1.2** Create merkle_subhashes table
  - **3.1.3** Create merkle_proof_cache table
  - **3.1.4** Create attribution_reports table
  - **3.1.5** Alter organizations table for tiers
- **3.2** Database access layer
  - **3.2.1** Merkle root CRUD operations
  - **3.2.2** Sub-hash indexing operations
  - **3.2.3** Proof cache operations
  - **3.2.4** Attribution report operations
- **3.3** Query optimization
  - **3.3.1** Index tuning
  - **3.3.2** Query performance testing
  - **3.3.3** Caching strategy implementation

### 4.0 API Endpoints - Enterprise Tier
- **4.1** Document encoding endpoint
  - **4.1.1** POST /api/v1/enterprise/encode
  - **4.1.2** Request validation
  - **4.1.3** Merkle tree construction
  - **4.1.4** Database storage
  - **4.1.5** Response formatting
- **4.2** Source attribution endpoint
  - **4.2.1** POST /api/v1/enterprise/attribute
  - **4.2.2** Target text segmentation
  - **4.2.3** Hash matching and lookup
  - **4.2.4** Merkle proof generation
  - **4.2.5** Location determination
  - **4.2.6** Response with source list
- **4.3** Plagiarism detection endpoint
  - **4.3.1** POST /api/v1/enterprise/detect-plagiarism
  - **4.3.2** Repository scanning
  - **4.3.3** Multi-source matching
  - **4.3.4** Statistical analysis
  - **4.3.5** Heat map generation
  - **4.3.6** Report generation and storage
- **4.4** Merkle proof verification endpoint
  - **4.4.1** POST /api/v1/enterprise/verify-proof
  - **4.4.2** Proof validation
  - **4.4.3** Root hash verification
  - **4.4.4** Response with verification result

### 5.0 Authentication & Authorization
- **5.1** Tier-based access control
  - **5.1.1** Middleware for tier checking
  - **5.1.2** Feature flag system
  - **5.1.3** Quota enforcement
- **5.2** API key management
  - **5.2.1** Enterprise tier key generation
  - **5.2.2** Key validation and rotation
- **5.3** Usage tracking
  - **5.3.1** Call counting per organization
  - **5.3.2** Quota reset scheduling
  - **5.3.3** Overage handling

### 6.0 Advanced Features
- **6.1** Statistical analysis engine
  - **6.1.1** Match percentage calculation
  - **6.1.2** Source ranking algorithm
  - **6.1.3** Confidence scoring
- **6.2** Heat map generation
  - **6.2.1** Location mapping
  - **6.2.2** Visualization data structure
  - **6.2.3** Export formats (JSON, SVG)
- **6.3** Near-match detection
  - **6.3.1** Fuzzy matching algorithm
  - **6.3.2** Edit distance calculation
  - **6.3.3** Transformation analysis
- **6.4** Text normalization
  - **6.4.1** Whitespace normalization
  - **6.4.2** Case normalization
  - **6.4.3** Punctuation handling
  - **6.4.4** Unicode normalization

### 7.0 Integration & Migration
- **7.1** Backward compatibility
  - **7.1.1** Free tier endpoint preservation
  - **7.1.2** Existing client compatibility
- **7.2** Data migration
  - **7.2.1** Existing document re-encoding (optional)
  - **7.2.2** Sentence hash migration to Merkle trees
- **7.3** Dashboard integration
  - **7.3.1** Enterprise tier UI components
  - **7.3.2** Attribution report viewer
  - **7.3.3** Heat map visualization

### 8.0 Testing & Quality Assurance
- **8.1** Unit tests
  - **8.1.1** Merkle tree operations
  - **8.1.2** Proof generation/verification
  - **8.1.3** Database operations
- **8.2** Integration tests
  - **8.2.1** End-to-end API workflows
  - **8.2.2** Multi-document scenarios
  - **8.2.3** Performance benchmarks
- **8.3** Security testing
  - **8.3.1** Authorization bypass attempts
  - **8.3.2** Input validation
  - **8.3.3** SQL injection prevention

### 9.0 Documentation
- **9.1** API documentation
  - **9.1.1** OpenAPI/Swagger specs
  - **9.1.2** Endpoint examples
  - **9.1.3** Error codes and handling
- **9.2** Developer guides
  - **9.2.1** Merkle tree concepts
  - **9.2.2** Integration guide
  - **9.2.3** Best practices
- **9.3** User documentation
  - **9.3.1** Feature comparison (Free vs Enterprise)
  - **9.3.2** Use case examples
  - **9.3.3** Pricing and quotas

### 10.0 Deployment & Monitoring
- **10.1** Deployment preparation
  - **10.1.1** Database migration scripts
  - **10.1.2** Configuration management
  - **10.1.3** Rollback procedures
- **10.2** Monitoring setup
  - **10.2.1** Performance metrics
  - **10.2.2** Error tracking
  - **10.2.3** Usage analytics
- **10.3** Production rollout
  - **10.3.1** Staged deployment
  - **10.3.2** Beta testing with select customers
  - **10.3.3** Full production release

---

## Technical Specifications

### Merkle Tree Construction Algorithm

```python
class MerkleNode:
    def __init__(self, hash_value: str, left=None, right=None, 
                 content=None, metadata=None):
        self.hash = hash_value
        self.left = left
        self.right = right
        self.content = content  # For leaf nodes
        self.metadata = metadata or {}

class MerkleTree:
    def __init__(self, segments: List[str], segmentation_level: str):
        self.segments = segments
        self.level = segmentation_level
        self.root = self._build_tree(segments)
    
    def _build_tree(self, segments: List[str]) -> MerkleNode:
        # Create leaf nodes
        leaves = [
            MerkleNode(
                hash_value=self._hash(segment),
                content=segment,
                metadata={'index': i, 'level': self.level}
            )
            for i, segment in enumerate(segments)
        ]
        
        # Build tree bottom-up
        return self._build_level(leaves)
    
    def _build_level(self, nodes: List[MerkleNode]) -> MerkleNode:
        if len(nodes) == 1:
            return nodes[0]
        
        # Pair nodes and create parent level
        parent_nodes = []
        for i in range(0, len(nodes), 2):
            left = nodes[i]
            right = nodes[i + 1] if i + 1 < len(nodes) else left
            
            combined_hash = self._combine_hashes(left.hash, right.hash)
            parent = MerkleNode(
                hash_value=combined_hash,
                left=left,
                right=right
            )
            parent_nodes.append(parent)
        
        return self._build_level(parent_nodes)
    
    def _hash(self, data: str) -> str:
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def _combine_hashes(self, left: str, right: str) -> str:
        return self._hash(left + right)
    
    def generate_proof(self, target_hash: str) -> Optional[List[Dict]]:
        """Generate Merkle proof for a target hash"""
        path = []
        
        def find_path(node: MerkleNode, target: str, 
                      current_path: List) -> bool:
            if node.hash == target:
                return True
            
            if node.left is None:  # Leaf node
                return False
            
            # Try left subtree
            if find_path(node.left, target, current_path):
                current_path.append({
                    'hash': node.right.hash,
                    'position': 'right'
                })
                return True
            
            # Try right subtree
            if find_path(node.right, target, current_path):
                current_path.append({
                    'hash': node.left.hash,
                    'position': 'left'
                })
                return True
            
            return False
        
        if find_path(self.root, target_hash, path):
            return path
        return None
    
    def verify_proof(self, target_hash: str, proof: List[Dict], 
                     root_hash: str) -> bool:
        """Verify a Merkle proof"""
        current_hash = target_hash
        
        for step in proof:
            sibling_hash = step['hash']
            position = step['position']
            
            if position == 'left':
                current_hash = self._combine_hashes(sibling_hash, current_hash)
            else:
                current_hash = self._combine_hashes(current_hash, sibling_hash)
        
        return current_hash == root_hash
```

### Hierarchical Segmentation

```python
class HierarchicalSegmenter:
    def segment_document(self, text: str) -> Dict[str, List[str]]:
        """
        Segment document at multiple levels:
        - sentences
        - paragraphs
        - sections
        """
        return {
            'sentences': self._segment_sentences(text),
            'paragraphs': self._segment_paragraphs(text),
            'sections': self._segment_sections(text)
        }
    
    def _segment_sentences(self, text: str) -> List[str]:
        # Use existing sentence parser
        return parse_sentences(text)
    
    def _segment_paragraphs(self, text: str) -> List[str]:
        # Split on double newlines
        paragraphs = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paragraphs if p.strip()]
    
    def _segment_sections(self, text: str) -> List[str]:
        # Split on markdown headers or other section markers
        sections = re.split(r'\n#{1,6}\s+', text)
        return [s.strip() for s in sections if s.strip()]
```

---

## API Endpoint Specifications

### 1. Encode Document (Enterprise Tier)

**Endpoint:** `POST /api/v1/enterprise/encode`

**Request:**
```json
{
  "text": "Full document text...",
  "document_id": "doc_12345",
  "segmentation_levels": ["sentence", "paragraph", "section"],
  "metadata": {
    "title": "Document Title",
    "author": "Author Name",
    "date": "2025-10-28"
  }
}
```

**Response:**
```json
{
  "success": true,
  "document_id": "doc_12345",
  "merkle_roots": [
    {
      "level": "sentence",
      "root_hash": "abc123...",
      "total_leaves": 150,
      "tree_depth": 8
    },
    {
      "level": "paragraph",
      "root_hash": "def456...",
      "total_leaves": 25,
      "tree_depth": 5
    },
    {
      "level": "section",
      "root_hash": "ghi789...",
      "total_leaves": 5,
      "tree_depth": 3
    }
  ],
  "indexed_hashes": 180
}
```

### 2. Attribute Source (Enterprise Tier)

**Endpoint:** `POST /api/v1/enterprise/attribute`

**Request:**
```json
{
  "text_segment": "This is the text to attribute...",
  "segmentation_level": "sentence",
  "include_proof": true
}
```

**Response:**
```json
{
  "success": true,
  "found": true,
  "sources": [
    {
      "document_id": "doc_12345",
      "root_hash": "abc123...",
      "location": {
        "segment_index": 42,
        "level": "sentence"
      },
      "merkle_proof": {
        "target_hash": "xyz789...",
        "proof_path": [
          {"hash": "aaa111...", "position": "right"},
          {"hash": "bbb222...", "position": "left"}
        ],
        "verified": true
      },
      "metadata": {
        "title": "Source Document",
        "author": "Original Author"
      }
    }
  ]
}
```

### 3. Detect Plagiarism (Enterprise Tier)

**Endpoint:** `POST /api/v1/enterprise/detect-plagiarism`

**Request:**
```json
{
  "target_text": "Text to check for plagiarism...",
  "segmentation_level": "sentence",
  "min_match_threshold": 0.7,
  "generate_heat_map": true
}
```

**Response:**
```json
{
  "success": true,
  "report_id": "report_abc123",
  "summary": {
    "total_segments": 100,
    "matched_segments": 45,
    "match_percentage": 45.0,
    "unique_sources": 3
  },
  "sources": [
    {
      "document_id": "doc_12345",
      "match_count": 30,
      "match_percentage": 66.7,
      "confidence": 0.95,
      "metadata": {
        "title": "Source Document 1"
      }
    },
    {
      "document_id": "doc_67890",
      "match_count": 15,
      "match_percentage": 33.3,
      "confidence": 0.88,
      "metadata": {
        "title": "Source Document 2"
      }
    }
  ],
  "heat_map": {
    "segments": [
      {"index": 0, "matched": true, "source": "doc_12345"},
      {"index": 1, "matched": false},
      {"index": 2, "matched": true, "source": "doc_12345"}
    ]
  }
}
```

---

## Implementation Timeline

### Phase 1: Foundation (Weeks 1-3)
- **Week 1**: Database schema design and migration scripts
- **Week 2**: Core Merkle tree implementation
- **Week 3**: Text segmentation engine and testing

### Phase 2: Core Features (Weeks 4-7)
- **Week 4**: Merkle proof generation and verification
- **Week 5**: Database access layer and indexing
- **Week 6**: Document encoding endpoint
- **Week 7**: Source attribution endpoint

### Phase 3: Advanced Features (Weeks 8-10)
- **Week 8**: Plagiarism detection endpoint
- **Week 9**: Statistical analysis and heat maps
- **Week 10**: Near-match detection and normalization

### Phase 4: Integration & Testing (Weeks 11-13)
- **Week 11**: Tier-based access control and quotas
- **Week 12**: Dashboard integration
- **Week 13**: Comprehensive testing and bug fixes

### Phase 5: Documentation & Deployment (Weeks 14-16)
- **Week 14**: API documentation and developer guides
- **Week 15**: Beta testing with select customers
- **Week 16**: Production deployment and monitoring

**Total Duration:** 16 weeks (4 months)

---

## Success Metrics

### Technical Metrics
- Merkle tree construction time: < 100ms per 1000 segments
- Proof generation time: < 50ms
- Database query time: < 100ms for hash lookup
- API response time: < 500ms for attribution requests

### Business Metrics
- Enterprise tier adoption rate: Target 20% of active users
- API call volume: Track usage patterns
- Customer satisfaction: NPS score > 8
- Revenue impact: Track conversion from Free to Enterprise

---

## Risk Assessment

### Technical Risks
1. **Performance**: Large documents may cause slow tree construction
   - *Mitigation*: Implement async processing and caching
2. **Storage**: Merkle tree data may consume significant database space
   - *Mitigation*: Implement data retention policies and compression
3. **Complexity**: Merkle proof verification may be difficult for clients
   - *Mitigation*: Provide SDK with built-in verification

### Business Risks
1. **Adoption**: Customers may not see value in Enterprise tier
   - *Mitigation*: Clear use case documentation and demos
2. **Pricing**: May be difficult to determine optimal pricing
   - *Mitigation*: Start with beta pricing and adjust based on feedback
3. **Competition**: Other solutions may emerge
   - *Mitigation*: Focus on patent protection and unique features

---

## Next Steps

1. **Review and approve** this implementation plan
2. **Allocate resources** (developers, QA, DevOps)
3. **Set up project tracking** (Jira, GitHub Projects, etc.)
4. **Begin Phase 1** with database schema design
5. **Schedule weekly progress reviews**

---

*Document prepared by: Claude (AI Assistant)*  
*Last updated: 2025-10-28*
