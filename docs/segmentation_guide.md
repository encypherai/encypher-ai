# Text Segmentation Guide
## Merkle Tree Attribution System

---

## Overview

The Merkle tree attribution system supports **multiple levels of text segmentation**, from coarse-grained (sections) to fine-grained (words). Each level can be used independently to build Merkle trees for content attribution.

### Segmentation Hierarchy

```
Document
├── Sections (e.g., chapters, major divisions)
│   ├── Paragraphs
│   │   ├── Sentences
│   │   │   └── Words (optional, finest granularity)
```

---

## Segmentation Levels

### 1. Word-Level (Finest Granularity)

**Use Case:** Maximum granularity for detecting even single-word copying

**Pros:**
- Detects the smallest possible copied units
- Useful for detecting paraphrasing (when combined with normalization)
- Can identify keyword usage patterns

**Cons:**
- Very large Merkle trees (high memory/storage)
- Many false positives (common words appear everywhere)
- Slower proof generation

**Example:**
```python
from app.utils.segmentation import segment_words_simple

text = "The quick brown fox jumps."
words = segment_words_simple(text)
# Result: ['The', 'quick', 'brown', 'fox', 'jumps']
```

**Recommended for:**
- Legal documents where every word matters
- Code plagiarism detection
- Highly sensitive content

### 2. Sentence-Level (Default)

**Use Case:** Standard granularity for most content attribution

**Pros:**
- Good balance of granularity and tree size
- Semantically meaningful units
- Reasonable false positive rate

**Cons:**
- May miss paraphrased content
- Sentence boundary detection can be imperfect

**Example:**
```python
from app.utils.segmentation import segment_sentences

text = "First sentence. Second sentence! Third sentence?"
sentences = segment_sentences(text)
# Result: ['First sentence.', 'Second sentence!', 'Third sentence?']
```

**Recommended for:**
- News articles
- Blog posts
- General content attribution
- Academic papers

### 3. Paragraph-Level

**Use Case:** Coarser granularity for detecting larger copied blocks

**Pros:**
- Smaller Merkle trees
- Faster proof generation
- Detects substantial copying

**Cons:**
- Misses sentence-level copying
- Paragraph boundaries can be ambiguous

**Example:**
```python
from app.utils.segmentation import segment_paragraphs

text = "First paragraph.\n\nSecond paragraph."
paragraphs = segment_paragraphs(text)
# Result: ['First paragraph.', 'Second paragraph.']
```

**Recommended for:**
- Books and long-form content
- When storage/performance is a concern
- Detecting large-scale plagiarism

### 4. Section-Level (Coarsest)

**Use Case:** Detecting major structural copying

**Pros:**
- Very small Merkle trees
- Fast operations
- Detects chapter/section copying

**Cons:**
- Only detects large-scale copying
- Not suitable for short documents

**Example:**
```python
from app.utils.segmentation import segment_sections

text = """# Introduction
Content here.

## Methods
More content."""

sections = segment_sections(text)
# Result: ['# Introduction\nContent here.', '## Methods\nMore content.']
```

**Recommended for:**
- Books and technical documentation
- Structural plagiarism detection
- High-level content organization

---

## Advanced Segmentation (spaCy)

For **perfect segmentation**, use the advanced NLP-based segmenter:

### Installation

```bash
# Add spaCy dependency
uv add spacy

# Download English language model
python -m spacy download en_core_web_sm

# For other languages
python -m spacy download es_core_news_sm  # Spanish
python -m spacy download fr_core_news_sm  # French
python -m spacy download de_core_news_sm  # German
```

### Features

1. **Accurate Sentence Boundary Detection**
   - Handles abbreviations correctly (Dr., Inc., etc.)
   - Understands decimal numbers (3.14)
   - Recognizes ellipsis (...)

2. **Word Tokenization**
   - Proper handling of contractions (don't → do, n't)
   - Punctuation separation
   - Unicode support

3. **Text Normalization**
   - Lemmatization (running → run, better → good)
   - Stopword removal (the, a, is, etc.)
   - Lowercase conversion
   - Punctuation removal

### Usage

```python
from app.utils.segmentation import AdvancedSegmenter, ADVANCED_AVAILABLE

if ADVANCED_AVAILABLE:
    segmenter = AdvancedSegmenter()
    
    # Accurate sentence segmentation
    text = "Dr. Smith works at Inc. Corp. He is great."
    sentences = segmenter.segment_sentences(text)
    # Result: ['Dr. Smith works at Inc. Corp.', 'He is great.']
    
    # Word tokenization
    words = segmenter.segment_words(text, remove_punctuation=True)
    # Result: ['Dr.', 'Smith', 'works', 'at', 'Inc.', 'Corp.', 'He', 'is', 'great']
    
    # Text normalization
    normalized = segmenter.normalize_text(
        "The cats are running quickly.",
        lowercase=True,
        lemmatize=True,
        remove_stopwords=True
    )
    # Result: "cat run quickly"
else:
    print("spaCy not installed. Using regex-based segmentation.")
```

---

## Normalization Techniques

### Why Normalize?

Normalization helps match text that has minor variations:
- Different capitalization
- Extra whitespace
- Punctuation differences
- Word forms (running vs run)

### Basic Normalization (No Dependencies)

```python
from app.utils.merkle import compute_normalized_hash

text = "  The Quick   Brown Fox!  "

# Lowercase + whitespace normalization
hash1 = compute_normalized_hash(
    text,
    lowercase=True,
    remove_whitespace=True
)

# Will match: "the quick brown fox!"
```

### Advanced Normalization (spaCy)

```python
from app.utils.segmentation import normalize_text_advanced, ADVANCED_AVAILABLE

if ADVANCED_AVAILABLE:
    text = "The cats were running quickly through the forest."
    
    normalized = normalize_text_advanced(
        text,
        lowercase=True,
        lemmatize=True,
        remove_stopwords=True,
        remove_punctuation=True
    )
    # Result: "cat run quickly forest"
    
    # This will match paraphrased versions like:
    # "A cat runs quick in forests"
```

---

## Choosing the Right Level

### Decision Matrix

| Use Case | Recommended Level | Normalization | Advanced NLP |
|----------|------------------|---------------|--------------|
| Legal documents | Word | No | Optional |
| News articles | Sentence | Basic | Recommended |
| Blog posts | Sentence | Basic | Optional |
| Academic papers | Sentence | Advanced | Recommended |
| Books | Paragraph | Basic | Optional |
| Code documentation | Section | No | No |
| Paraphrase detection | Sentence | Advanced | Required |
| Keyword tracking | Word | Advanced | Required |

### Performance Considerations

**Tree Size (for 1000-word document):**
- Word level: ~1000 leaves, depth ~10, ~2000 total nodes
- Sentence level: ~50 leaves, depth ~6, ~100 total nodes
- Paragraph level: ~10 leaves, depth ~4, ~20 total nodes
- Section level: ~3 leaves, depth ~2, ~6 total nodes

**Proof Size:**
- Word level: ~10 sibling hashes
- Sentence level: ~6 sibling hashes
- Paragraph level: ~4 sibling hashes
- Section level: ~2 sibling hashes

**Database Storage (per document):**
- Word level: ~1000 hash records
- Sentence level: ~50 hash records
- Paragraph level: ~10 hash records
- Section level: ~3 hash records

---

## Multi-Level Strategy

For comprehensive attribution, use **multiple levels simultaneously**:

```python
from app.utils.segmentation import HierarchicalSegmenter

# Segment at all levels
segmenter = HierarchicalSegmenter(text, include_words=True)

# Build Merkle trees at each level
from app.utils.merkle import MerkleTree

word_tree = MerkleTree(segmenter.words, segmentation_level='word')
sentence_tree = MerkleTree(segmenter.sentences, segmentation_level='sentence')
paragraph_tree = MerkleTree(segmenter.paragraphs, segmentation_level='paragraph')

# Store all trees in database
# This allows querying at any granularity
```

**Benefits:**
- Query at appropriate granularity for each use case
- Detect copying at multiple scales
- Provide evidence at different levels

**Cost:**
- 4x storage (word + sentence + paragraph + section)
- 4x indexing time
- More complex queries

---

## API Usage

### Document Encoding with Segmentation Level

```python
# POST /api/v1/enterprise/encode
{
  "text": "Document text...",
  "document_id": "doc_123",
  "segmentation_levels": ["word", "sentence", "paragraph"],
  "normalization": {
    "lowercase": true,
    "lemmatize": true,
    "remove_stopwords": false
  }
}
```

### Source Attribution with Level Selection

```python
# POST /api/v1/enterprise/attribute
{
  "text_segment": "Text to attribute...",
  "segmentation_level": "sentence",  # or "word", "paragraph", "section"
  "include_proof": true,
  "normalization": {
    "lowercase": true
  }
}
```

---

## Best Practices

### 1. Start with Sentence-Level
Begin with sentence-level segmentation for most use cases. It provides good balance.

### 2. Add Word-Level for High-Value Content
Use word-level only for content where every word matters (legal, financial).

### 3. Use Normalization for Paraphrase Detection
Enable normalization when you need to detect paraphrased content.

### 4. Consider Storage Costs
Word-level creates large trees. Ensure adequate database capacity.

### 5. Test with Sample Data
Test different levels with your actual content to find the right balance.

### 6. Use Advanced Segmentation for Production
Install spaCy for production deployments to get accurate segmentation.

---

## Future Enhancements

### Planned Features
- [ ] Multi-language support (spaCy models for 60+ languages)
- [ ] Custom segmentation rules
- [ ] Semantic similarity matching (beyond exact hash matching)
- [ ] N-gram segmentation (2-word, 3-word phrases)
- [ ] Fuzzy matching with edit distance
- [ ] Machine learning-based paraphrase detection

---

*Last Updated: 2025-10-28*
