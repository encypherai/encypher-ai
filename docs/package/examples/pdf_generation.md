# Generating PDFs with Embedded Metadata

This example demonstrates how to create a PDF containing text watermarked with a C2PA v2.2 compliant manifest using `EncypherPDF`.

```python
from cryptography.hazmat.primitives.asymmetric import ed25519
from encypher.pdf_generator import EncypherPDF

private_key = ed25519.Ed25519PrivateKey.generate()
public_key = private_key.public_key()

pdf_path = "example.pdf"
EncypherPDF.from_text(
    text="Hello from EncypherAI!",
    output_path=pdf_path,
    private_key=private_key,
    signer_id="example-signer",
    timestamp="2024-01-01T00:00:00Z",
)

# Later, verify the PDF
ok, signer, payload = EncypherPDF.verify_pdf(
    pdf_path,
    lambda sid: public_key if sid == "example-signer" else None,
)
print("Verified:", ok)
```
