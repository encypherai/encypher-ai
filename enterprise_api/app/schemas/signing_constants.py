"""
Single source of truth for signing-related constants.

TEAM_165: All schema validators for manifest_mode, embedding_strategy,
segmentation_level, etc. MUST import from here. Never duplicate these lists.

NOTE: Public-facing names only. Internal implementation details (e.g. the
encoding used by micro mode) must NOT appear in these constants.
"""

# --- Manifest Modes ---
# Controls how the C2PA manifest and per-segment markers are embedded.
#
# Two modes are available:
#   full  - standard C2PA document manifest embedded at end of content
#   micro - ultra-compact per-segment markers; behaviour controlled by flags:
#     ecc=True        -> Reed-Solomon error correction (44 chars, default)
#     ecc=False       -> plain HMAC (36 chars)
#     embed_c2pa=True -> full C2PA document manifest embedded in content (default)
#     embed_c2pa=False-> per-sentence markers only; C2PA manifest DB-only
#     legacy_safe=True-> ZW6 base-6 encoding (Word+terminal safe, 100/112 chars)
#
# A C2PA-compatible manifest is ALWAYS generated for micro mode.
# store_c2pa_manifest controls DB persistence; embed_c2pa controls in-content embedding.
#
# Internal implementation uses VS256 encoding (default) or ZW6 (legacy_safe=True).
# Do NOT expose internal encoding names in public API surfaces.
MANIFEST_MODES: list[str] = [
    "full",
    "micro",
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
