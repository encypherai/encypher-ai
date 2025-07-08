# Generating PDFs with Embedded Metadata

The `EncypherPDF` class provides functionality to create and verify PDF documents with embedded metadata using digital signatures. This guide demonstrates how to use these features effectively.

> **New in v1.1.0:** Support for image embedding, custom margins, and Word document (.docx) conversion.

## Basic Usage

This example demonstrates how to create a PDF containing text watermarked with a C2PA v2.2 compliant manifest using `EncypherPDF`.

```python
from cryptography.hazmat.primitives.asymmetric import ed25519
from encypher.pdf_generator import EncypherPDF

# Generate a key pair for signing
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
print("Signer ID:", signer)
print("Payload:", payload)
```

## Advanced Features

### Custom Fonts

You can use custom TrueType fonts for better Unicode support:

```python
EncypherPDF.from_text(
    text="Hello with custom font! 你好，世界！",
    output_path="custom_font.pdf",
    private_key=private_key,
    signer_id="example-signer",
    timestamp="2024-01-01T00:00:00Z",
    font_path="path/to/your/unicode_font.ttf",
    font_name="CustomFont",
    font_size=14,
)
```

### Custom Margins

You can customize page margins (defaults to 1 inch on all sides):

```python
EncypherPDF.from_text(
    text="Hello with custom margins!",
    output_path="custom_margins.pdf",
    private_key=private_key,
    signer_id="example-signer",
    timestamp="2024-01-01T00:00:00Z",
    margins={
        "left": 1.5 * 72,    # 1.5 inches from left (72 points per inch)
        "right": 1.0 * 72,  # 1 inch from right
        "top": 2.0 * 72,    # 2 inches from top
        "bottom": 1.0 * 72  # 1 inch from bottom
    }
)
```

### Image Embedding

You can embed images in your PDFs:

```python
EncypherPDF.from_text(
    text="Hello, world! This is a test PDF with embedded metadata.",
    output_path="output.pdf",
    private_key=private_key,
    signer_id="test-signer",
    timestamp="2024-01-01T00:00:00Z",
    images=[
        {
            "path": "path/to/image.jpg",  # Path to image file
            "x": 72,                     # X position in points (1 inch from left)
            "y": 400,                    # Y position in points
            "width": 216,                # Width in points (3 inches)
            "height": None,              # Height in points (auto-calculated if None)
            "preserve_aspect_ratio": True  # Maintain aspect ratio
        }
    ]
)
```

You can include multiple images by adding more dictionaries to the `images` list.

### Word Document Conversion

You can convert Word documents (.docx) to PDFs with embedded metadata:

```python
from datetime import datetime, timezone
from encypher.core.unicode_metadata import MetadataTarget

# Current timestamp for metadata
current_timestamp = datetime.now(timezone.utc)

EncypherPDF.from_docx(
    docx_file="document.docx",  # Note: parameter is docx_file, not docx_path
    output_file="document.pdf", # Note: parameter is output_file, not output_path
    private_key=private_key,
    signer_id="example-signer",
    timestamp=current_timestamp,  # Can be datetime object or ISO format string
    target=MetadataTarget.FIRST_LETTER,  # Control where metadata is embedded
    # All options from from_text are supported
    font_size=14,
    images=[{"path": "logo.png", "x": 72, "y": 700}],
    margins={"top": 1.5 * 72}
)
```

> **Note:** Word document conversion requires the `python-docx` package. Install it with `uv pip install python-docx`.

### Metadata Format Options

The `EncypherPDF` class supports different metadata formats:

```python
# Using basic metadata format
EncypherPDF.from_text(
    text="Hello with basic metadata!",
    output_path="basic_metadata.pdf",
    private_key=private_key,
    signer_id="example-signer",
    timestamp="2024-01-01T00:00:00Z",
    metadata_format="basic",  # Options: "basic", "manifest", "cbor_manifest", "c2pa_v2_2"
)
```

## Command Line Interface

The `EncypherPDF` class can also be used from the command line. Here's an example:

```bash
python -m encypher.examples.cli_example convert-to-pdf \
    --text "Hello, world! This is a test PDF with embedded metadata." \
    --output-file output.pdf \
    --private-key-file private_key.pem \
    --signer-id test-signer \
    --font-path path/to/font.ttf \
    --font-size 14
```

### CLI with Custom Margins

```bash
python -m encypher.examples.cli_example convert-to-pdf \
    --text "Hello, world! This is a test PDF with embedded metadata." \
    --output-file output.pdf \
    --private-key-file private_key.pem \
    --signer-id test-signer \
    --margin-left 1.5 \
    --margin-top 2.0 \
    --margin-right 1.0 \
    --margin-bottom 1.0
```

### CLI with Image Embedding

```bash
python -m encypher.examples.cli_example convert-to-pdf \
    --text "Hello, world! This is a test PDF with embedded metadata." \
    --output-file output.pdf \
    --private-key-file private_key.pem \
    --signer-id test-signer \
    --image-path path/to/image.jpg \
    --image-x 72 \
    --image-y 400 \
    --image-width 216
```

Additional image options include:
- `--image-height`: Height of the image in points (auto-calculated if not specified)
- `--no-preserve-aspect-ratio`: Flag to disable aspect ratio preservation

### CLI with Word Document Conversion

```bash
python -m encypher.examples.cli_example convert-to-pdf \
    --docx-file document.docx \
    --output-file document.pdf \
    --private-key-file private_key.pem \
    --signer-id test-signer \
    --target first_letter \
    --image-path logo.png \
    --margin-top 1.5
```

The `--target` parameter controls where metadata is embedded and accepts these values:
- `whitespace`: Embed in whitespace (default)
- `first_letter`: Embed in the first letter of words
- `punctuation`: Embed in punctuation marks
- `all`: Embed in all possible locations

## Error Handling

The `EncypherPDF` class includes robust error handling for common issues:

```python
from encypher.pdf_generator import EncypherPDF, FontError, PDFGenerationError, SignatureError, ImageError, ConversionError

try:
    # Attempt to create a PDF with a non-existent font
    EncypherPDF.from_text(
        text="This will fail",
        output_path="error_example.pdf",
        private_key=private_key,
        signer_id="example-signer",
        timestamp="2024-01-01T00:00:00Z",
        font_path="non_existent_font.ttf",
    )
except FontError as e:
    print(f"Font error: {e}")
except ImageError as e:
    print(f"Image error: {e}")
except PDFGenerationError as e:
    print(f"PDF generation error: {e}")

try:
    # Attempt to convert a Word document that doesn't exist
    EncypherPDF.from_docx(
        docx_path="non_existent_document.docx",
        output_path="document.pdf",
        private_key=private_key,
        signer_id="example-signer",
        timestamp="2024-01-01T00:00:00Z",
    )
except FileNotFoundError as e:
    print(f"File not found: {e}")
except ConversionError as e:
    print(f"Conversion error: {e}")

try:
    # Attempt to verify a PDF with an incorrect public key
    ok, signer, payload = EncypherPDF.verify_pdf(
        "example.pdf",
        lambda sid: None,  # This will fail as no public key is provided
    )
except SignatureError as e:
    print(f"Signature verification error: {e}")
except FileNotFoundError as e:
    print(f"File error: {e}")
```

## Extracting Text from PDFs

You can extract text from PDFs using the `extract_text` method:

```python
try:
    text = EncypherPDF.extract_text("example.pdf")
    print("Extracted text:", text[:100], "...")
except PDFGenerationError as e:
    print(f"Error extracting text: {e}")
```

## Integration with Other EncypherAI Features

The `EncypherPDF` class integrates seamlessly with other EncypherAI features:

```python
from encypher.core.unicode_metadata import UnicodeMetadata

# First, create metadata-rich text
embedded_text = UnicodeMetadata.embed_metadata(
    text="Hello from EncypherAI!",
    private_key=private_key,
    signer_id="example-signer",
    timestamp="2024-01-01T00:00:00Z",
)

# Then, create a PDF with the pre-embedded text
pdf_path = "pre_embedded.pdf"
EncypherPDF.from_text(
    text=embedded_text,  # Already contains metadata
    output_path=pdf_path,
    private_key=private_key,
    signer_id="example-signer",
    timestamp="2024-01-01T00:00:00Z",
    # This will add a second layer of metadata
)
```
