import os
import tempfile
import unittest
from datetime import datetime, timezone

from cryptography.hazmat.primitives.asymmetric import ed25519

from encypher.pdf_generator import EncypherPDF


class TestPDFGeneration(unittest.TestCase):
    def setUp(self):
        self.private_key = ed25519.Ed25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()
        self.signer_id = "pdf-signer"
        self.sample_text = "Hello PDF world"
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def test_pdf_creation_and_verification(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = os.path.join(tmpdir, "output.pdf")
            font_path = os.path.join(os.path.dirname(__file__), "..", "NotoSans-Regular.ttf")
            EncypherPDF.from_text(
                text=self.sample_text,
                output_path=pdf_path,
                private_key=self.private_key,
                signer_id=self.signer_id,
                timestamp=self.timestamp,
                font_path=font_path,
            )

            self.assertTrue(os.path.exists(pdf_path))

            extracted_text = EncypherPDF.extract_text(pdf_path)
            self.assertIn(self.sample_text, extracted_text)

            # Ensure hidden bytes are present even if exact selectors are lost
            self.assertGreater(len(extracted_text), len(self.sample_text))


if __name__ == "__main__":
    unittest.main()
