-- SQLite initialization for local Merkle tests
PRAGMA foreign_keys = ON;

-- Minimal organizations table (for demo org)
CREATE TABLE IF NOT EXISTS organizations (
  organization_id TEXT PRIMARY KEY,
  organization_name TEXT,
  organization_type TEXT,
  email TEXT,
  tier TEXT DEFAULT 'demo',
  monthly_quota INTEGER DEFAULT 10000,
  documents_signed INTEGER DEFAULT 0,
  sentences_signed INTEGER DEFAULT 0,
  api_calls_this_month INTEGER DEFAULT 0,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO organizations (
  organization_id, organization_name, organization_type, email, tier
) VALUES (
  'org_demo', 'Demo Organization', 'demo', 'demo@encypher.local', 'demo'
);

-- Merkle tables
CREATE TABLE IF NOT EXISTS merkle_roots (
  root_id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL,
  document_id TEXT NOT NULL,
  root_hash TEXT NOT NULL,
  tree_depth INTEGER NOT NULL,
  total_leaves INTEGER NOT NULL,
  segmentation_level TEXT NOT NULL,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  metadata TEXT,
  FOREIGN KEY (organization_id) REFERENCES organizations(organization_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_merkle_roots_org_level ON merkle_roots (organization_id, segmentation_level);
CREATE INDEX IF NOT EXISTS idx_merkle_roots_created_at ON merkle_roots (created_at);
CREATE INDEX IF NOT EXISTS idx_merkle_roots_root_hash ON merkle_roots (root_hash);

CREATE TABLE IF NOT EXISTS merkle_subhashes (
  subhash_id TEXT PRIMARY KEY,
  hash_value TEXT NOT NULL,
  root_id TEXT NOT NULL,
  node_type TEXT NOT NULL,
  depth_level INTEGER NOT NULL,
  position_index INTEGER NOT NULL,
  parent_hash TEXT,
  left_child_hash TEXT,
  right_child_hash TEXT,
  text_content TEXT,
  segment_metadata TEXT,
  FOREIGN KEY (root_id) REFERENCES merkle_roots(root_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_merkle_subhashes_hash_root ON merkle_subhashes (hash_value, root_id);
CREATE INDEX IF NOT EXISTS idx_merkle_subhashes_node_type ON merkle_subhashes (node_type);

CREATE TABLE IF NOT EXISTS merkle_proof_cache (
  cache_id TEXT PRIMARY KEY,
  target_hash TEXT NOT NULL,
  root_id TEXT NOT NULL,
  proof_path TEXT NOT NULL,
  position_bits BLOB NOT NULL,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  expires_at TEXT NOT NULL,
  FOREIGN KEY (root_id) REFERENCES merkle_roots(root_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_merkle_proof_cache_target_root ON merkle_proof_cache (target_hash, root_id);
CREATE INDEX IF NOT EXISTS idx_merkle_proof_cache_expires ON merkle_proof_cache (expires_at);

CREATE TABLE IF NOT EXISTS attribution_reports (
  report_id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL,
  target_document_id TEXT,
  target_text_hash TEXT,
  scan_timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
  total_segments INTEGER NOT NULL,
  matched_segments INTEGER NOT NULL,
  source_documents TEXT NOT NULL,
  heat_map_data TEXT,
  report_metadata TEXT,
  FOREIGN KEY (organization_id) REFERENCES organizations(organization_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_attribution_reports_org_timestamp ON attribution_reports (organization_id, scan_timestamp);

-- Content references for minimal embeddings
CREATE TABLE IF NOT EXISTS content_references (
  ref_id INTEGER PRIMARY KEY,
  merkle_root_id TEXT,
  leaf_hash TEXT NOT NULL,
  leaf_index INTEGER NOT NULL,
  organization_id TEXT NOT NULL,
  document_id TEXT NOT NULL,
  text_content TEXT,
  text_preview TEXT,
  c2pa_manifest_url TEXT,
  c2pa_manifest_hash TEXT,
  license_type TEXT,
  license_url TEXT,
  instance_id TEXT,
  previous_instance_id TEXT,
  manifest_data TEXT,
  signature_hash TEXT NOT NULL,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  expires_at TEXT,
  embedding_metadata TEXT,
  FOREIGN KEY (organization_id) REFERENCES organizations(organization_id) ON DELETE CASCADE,
  FOREIGN KEY (merkle_root_id) REFERENCES merkle_roots(root_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_content_refs_org_doc ON content_references (organization_id, document_id);
CREATE INDEX IF NOT EXISTS idx_content_refs_org_created ON content_references (organization_id, created_at);
