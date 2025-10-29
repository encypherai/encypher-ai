"""Quick test to verify spaCy is working."""
import spacy

print("Loading spaCy model...")
nlp = spacy.load('en_core_web_sm')
print("✓ spaCy model loaded successfully!")

# Test sentence segmentation
text = "Dr. Smith works at Inc. Corp. He is great."
doc = nlp(text)
sentences = [sent.text for sent in doc.sents]

print(f"\nTest text: {text}")
print(f"Sentences detected: {len(sentences)}")
for i, sent in enumerate(sentences, 1):
    print(f"  {i}. {sent}")

print("\n✓ spaCy is working correctly!")
