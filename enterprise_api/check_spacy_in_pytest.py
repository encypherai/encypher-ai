"""Check if spaCy is available in pytest context."""
# Check if spaCy is available
try:
    import spacy
    print(f"✓ spaCy imported: {spacy.__version__}")
    try:
        _nlp = spacy.load("en_core_web_sm")
        print("✓ Model loaded: en_core_web_sm")
        SPACY_AVAILABLE = True
    except OSError as e:
        print(f"✗ Model load failed: {e}")
        SPACY_AVAILABLE = False
except ImportError as e:
    print(f"✗ spaCy import failed: {e}")
    SPACY_AVAILABLE = False

print(f"\nSPACY_AVAILABLE = {SPACY_AVAILABLE}")

# Now try importing from our module
from app.utils.segmentation import SPACY_AVAILABLE as MODULE_SPACY_AVAILABLE
print(f"MODULE SPACY_AVAILABLE = {MODULE_SPACY_AVAILABLE}")
