# Segmenter Zero-Drop and spaCy Migration

**Status:** Complete
**Current Goal:** Done
**Team:** TEAM_285

## Overview

Short text segments (headings, short paragraphs, captions) are silently dropped during signing
because the three segmenters have minimum-length defaults that filter out real content. When
copy-pasted content triggers the C2PA verification fallback, these unsigned segments have no
coverage. This PRD eliminates silent drops and ensures all secondary sentence-segmentation
call sites use the spaCy-backed segmenter already in place for the primary signing path.

## Objectives

- Zero segments silently dropped: all non-empty content receives a per-segment ZWC marker
- Copy-paste verification works for short content (headings, list items, captions)
- spaCy is the consistent sentence segmenter across all call sites (primary + secondary)
- No existing test regression

## Tasks

### 1.0 P1 -- Eliminate Silent Segment Drops

- [x] 1.1 Lower `sentence.py` default `min_length` from 3 to 1 (regex fallback path)
- [x] 1.2 Lower `paragraph.py` default `min_length` from 10 to 1
- [x] 1.3 Lower `section.py` default `min_length` from 50 to 1
- [x] 1.4 Add tests: short-segment content is never dropped with default arguments

### 2.0 P2 -- Migrate Secondary Callers to segment_sentences_default (spaCy)

- [x] 2.1 `embedding_service.py` lines 635/641 -- Merkle location scan
- [x] 2.2 `verification_logic.py` -- kept as segment_sentences (regex): this function scans
       ZWC-embedded text where spaCy misdetects boundaries due to zero-width chars
- [x] 2.3 `multi_embedding.py` lines 417/419 -- sentence scan during multi-embedding
- [x] 2.4 Regression test confirmed passing for verification_logic path

### 3.0 Testing and Validation

- [x] 3.1 Existing segmentation tests pass -- ✅ pytest 56/56
- [x] 3.2 New short-segment tests pass -- ✅ pytest 10/10 new TestZeroDropGuarantee
- [x] 3.3 No regression in embedding_service / verification tests -- ✅ pytest 61/61

## Success Criteria

- `segment_paragraphs("Short.")` returns `["Short."]` (not `[]`) -- ✅
- `segment_sections("# Hi\nYes.")` returns `["# Hi\nYes."]` (not `[]`) -- ✅
- embedding_service and multi_embedding secondary callers use segment_sentences_default -- ✅
- verification_logic kept as regex (ZWC-embedded text safety) -- ✅
- All tests pass -- ✅

## Completion Notes

P1: Changed min_length defaults from 3/10/50 to 1 in sentence.py, paragraph.py, section.py.
No content is ever silently dropped. Callers that need filtering pass explicit min_length.

P2: Migrated embedding_service.py (Merkle location scan) and multi_embedding.py (hash
re-verification) to segment_sentences_default. Kept verification_logic.py on regex segmenter
because _extract_sentence_for_signature scans ZWC-embedded text and spaCy misidentifies
sentence boundaries when zero-width characters are present around terminal punctuation.
