"""
Single source of truth for signing-related constants.

TEAM_165: All schema validators for manifest_mode, embedding_strategy,
segmentation_level, etc. MUST import from here. Never duplicate these lists.

NOTE: Public-facing names only. Internal implementation details (e.g. the
encoding used by micro_c2pa) must NOT appear in these constants.
"""

# --- Manifest Modes ---
# Controls how the C2PA manifest and per-segment markers are embedded.
#
# Naming convention (TEAM_165):
#   "micro"          — ultra-compact per-sentence markers (36 invisible chars)
#   "micro_ecc"      — same + Reed-Solomon error correction (44 chars, 128-bit HMAC)
#   "micro_c2pa"     — micro markers + full C2PA document manifest
#   "micro_ecc_c2pa" — micro_ecc markers + full C2PA document manifest
#
# Internal implementation uses VS256 encoding — do NOT expose that detail
# in public API surfaces (descriptions, error messages, docs).
MANIFEST_MODES: list[str] = [
    "full",
    "lightweight_uuid",
    "minimal_uuid",
    "hybrid",
    "zw_embedding",
    "micro",
    "micro_ecc",
    "micro_c2pa",
    "micro_ecc_c2pa",
]

# --- Embedding Strategies ---
# Controls how the invisible signature is placed within each segment.
EMBEDDING_STRATEGIES: list[str] = [
    "single_point",
    "distributed",
    "distributed_redundant",
]

# --- Segmentation Levels ---
# Controls the granularity at which text is split for signing.
SEGMENTATION_LEVELS: list[str] = [
    "document",
    "word",
    "sentence",
    "paragraph",
    "section",
]

# Subset allowed for Merkle tree multi-level indexing.
MERKLE_SEGMENTATION_LEVELS: set[str] = {
    "sentence",
    "paragraph",
    "section",
}

# --- Distribution Targets ---
# Controls which characters are used for distributed embedding placement.
DISTRIBUTION_TARGETS: list[str] = [
    "whitespace",
    "punctuation",
    "all_chars",
]

# --- C2PA Actions ---
C2PA_ACTIONS: list[str] = [
    "c2pa.created",
    "c2pa.edited",
]
