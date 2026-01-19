"""Quick test to verify spaCy is working."""

import pytest


spacy = pytest.importorskip("spacy")


def test_spacy_sentence_segmentation_smoke() -> None:
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        pytest.skip("spaCy model 'en_core_web_sm' not installed")

    text = "Dr. Smith works at Inc. Corp. He is great."
    doc = nlp(text)
    sentences = [sent.text for sent in doc.sents]

    assert sentences
