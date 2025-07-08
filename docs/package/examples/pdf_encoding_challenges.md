# PDF Encoding Challenges and Solutions

This document outlines the character encoding challenges encountered during the development of the EncypherPDF functionality and how they were addressed.

## Character Encoding Challenges

### Unicode Support in PDFs

PDF documents have historically had limited support for Unicode characters, especially for complex scripts and variation selectors. During our proof of concept (PoC) testing, we encountered several challenges:

1. **Variation Selectors**: Unicode variation selectors (VS1-VS16) were not consistently preserved when embedding text in PDFs and then extracting it.

2. **Complex Scripts**: Languages with complex scripts (e.g., Arabic, Thai) sometimes had character ordering issues when rendered in PDFs.

3. **Font Limitations**: Standard PDF fonts have limited Unicode coverage, requiring custom font embedding for comprehensive support.

4. **Metadata Preservation**: Ensuring that embedded metadata signatures remained valid after PDF generation and text extraction was challenging due to potential character transformations.

## Solutions Implemented

### PyMuPDF for Text Extraction

We chose PyMuPDF (imported as `fitz`) for text extraction due to its superior Unicode handling compared to alternatives:

```python
import fitz  # PyMuPDF

def extract_text(pdf_path):
    """Extract text from a PDF file using PyMuPDF."""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    finally:
        if 'doc' in locals():
            doc.close()
```

### Custom Font Support

To address font limitations, we implemented support for custom TrueType fonts:

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

### Text Normalization

To ensure consistent handling of Unicode characters, we implemented text normalization before embedding:

1. **NFC Normalization**: We use Unicode NFC (Normalization Form C) to ensure consistent character composition.
2. **Whitespace Handling**: We preserve significant whitespace while normalizing line endings.

### Verification Process

Our verification process accounts for potential character transformations:

1. **Extract text** from the PDF using PyMuPDF
2. **Normalize the extracted text** to account for any transformations
3. **Verify the metadata signature** using the normalized text

## Remaining Considerations

While our implementation successfully addresses many Unicode challenges, users should be aware of these considerations:

1. **Font Selection**: For documents with non-Latin scripts, always provide an appropriate Unicode-compatible font.

2. **Variation Selectors**: Some variation selectors may not be preserved in the PDF extraction process. Critical information should not rely solely on variation selectors.

3. **Text Layout**: Complex text layout (e.g., bidirectional text) may render differently than in the source text.

4. **Performance**: Text extraction from large PDFs can be memory-intensive. Consider processing large documents in chunks.

## Testing Recommendations

When working with Unicode-rich content in PDFs:

1. Always test the full round-trip process: text → PDF → extracted text → verification
2. Test with representative samples of your target scripts and languages
3. Use custom fonts with good coverage for your target languages
4. Verify that metadata signatures remain valid after extraction

## Future Improvements

Future versions may include:

1. Better handling of bidirectional text
2. Improved preservation of variation selectors
3. Support for more complex text layouts
4. Optimization for large documents
