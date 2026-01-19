"""Test spaCy import and availability."""

print("Testing spaCy availability...")

from app.utils.segmentation import SPACY_AVAILABLE, segment_sentences_default

print(f"SPACY_AVAILABLE: {SPACY_AVAILABLE}")

if SPACY_AVAILABLE:
    print("✓ spaCy is available!")

    # Test segmentation
    text = "Dr. Smith works at Inc. Corp. He is great."
    sentences = segment_sentences_default(text)
    print(f"\nTest: {text}")
    print(f"Sentences: {sentences}")
    print(f"Count: {len(sentences)}")
else:
    print("✗ spaCy not available")
