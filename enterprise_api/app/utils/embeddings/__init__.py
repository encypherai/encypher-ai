"""
Embedding utilities for injecting signed references into content.

Invisible Unicode embeddings are handled by the crypto modules in app/utils/:
  vs256_crypto.py        -- base-256 VS encoding (Google Docs, browsers)
  vs256_rs_crypto.py     -- VS256 + Reed-Solomon ECC
  legacy_safe_crypto.py  -- base-6 ZWC encoding (Word-safe)
  legacy_safe_rs_crypto.py -- base-6 + Reed-Solomon ECC
"""
