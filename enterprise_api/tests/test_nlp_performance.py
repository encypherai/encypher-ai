# Set env vars to avoid pydantic errors during import
import os
from unittest.mock import MagicMock, patch

os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost/db"
os.environ["KEY_ENCRYPTION_KEY"] = "00" * 32
os.environ["ENCRYPTION_NONCE"] = "00" * 12
os.environ["SSL_COM_API_KEY"] = "test_key"

from app.utils.segmentation.advanced import segment_sentences_advanced


def test_spacy_reloads_every_time():
    """
    Test that demonstrates the current implementation reloads the Spacy model on every call.
    We want to refactor this to use caching/singleton.
    """
    # Mock spacy.load
    with patch("spacy.load") as mock_load:
        mock_nlp = MagicMock()
        # Mock nlp object call (it's callable)
        mock_doc = MagicMock()
        mock_sent = MagicMock()
        mock_sent.text = "Sentence."
        mock_doc.sents = [mock_sent]
        mock_nlp.return_value = mock_doc
        mock_load.return_value = mock_nlp
        
        # First call
        segment_sentences_advanced("First text.")
        
        # Second call
        segment_sentences_advanced("Second text.")
        
        # Check call count
        # If it's not cached, it will be 2
        # If it IS cached, it will be 1
        
        # Assert it is 1 (demonstrating the fix)
        assert mock_load.call_count == 1
        
        # Also verify it was called with the correct model
        mock_load.assert_called_with("en_core_web_sm")
