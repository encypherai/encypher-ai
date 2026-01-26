"""Test spaCy import and availability."""

print("Testing spaCy availability...")

from app.utils.segmentation import SPACY_AVAILABLE, segment_sentences_default

print(f"SPACY_AVAILABLE: {SPACY_AVAILABLE}")

if SPACY_AVAILABLE and segment_sentences_default is not None:
    print("✓ spaCy is available!")

    # Test segmentation
    text = "Dr. Smith works at Inc. Corp. He is great."
    sentences = segment_sentences_default(text, normalize=True)
    print(f"\nTest: {text}")
    print(f"Sentences: {sentences}")
    print(f"Count: {len(sentences)}")
elif SPACY_AVAILABLE:
    print("⚠ spaCy is available, but default segmenter is not loaded")
else:
    print("✗ spaCy not available")
