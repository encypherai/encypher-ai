"""
Test script to convert a Word document to PDF with embedded metadata.
"""

import os
from datetime import datetime, timezone
from cryptography.hazmat.primitives.asymmetric import ed25519
from encypher.pdf_generator import EncypherPDF

# Input and output paths
docx_path = r"C:\Users\eriks\encypher_ai_master\docs\AI Agent System Implementation Guide_gemini.docx"
output_dir = os.path.dirname(docx_path)
output_filename = os.path.splitext(os.path.basename(docx_path))[0] + ".pdf"
output_path = os.path.join(output_dir, output_filename)

# Generate a key pair for signing (in a real scenario, you'd load an existing key)
private_key = ed25519.Ed25519PrivateKey.generate()

# Sample metadata
metadata = {
    "title": "AI Agent System Implementation Guide",
    "author": "EncypherAI Team",
    "created": datetime.now(timezone.utc).isoformat(),
    "version": "2.5.0",
    "source": "Converted from DOCX using EncypherPDF"
}

print(f"Converting: {docx_path}")
print(f"Output to: {output_path}")
print(f"Embedding metadata: {metadata}")

try:
    # Convert the document with embedded metadata
    result_path = EncypherPDF.from_docx(
        docx_path=docx_path,
        output_path=output_path,
        private_key=private_key,
        signer_id="encypher-test",
        timestamp=int(datetime.now(timezone.utc).timestamp()),
        metadata_format="manifest",  # Using manifest format for richer metadata
        font_size=11,  # Standard font size
        # Add a logo image in the top right corner
        images=[{
            "path": os.path.join(os.path.dirname(__file__), "docs", "assets", "logo.png") 
            if os.path.exists(os.path.join(os.path.dirname(__file__), "docs", "assets", "logo.png")) else None,
            "x": 450,
            "y": 750,
            "width": 100,
            "preserve_aspect_ratio": True
        }] if os.path.exists(os.path.join(os.path.dirname(__file__), "docs", "assets", "logo.png")) else None,
        # Set standard margins
        margins={
            "left": 72,    # 1 inch
            "right": 72,   # 1 inch
            "top": 72,     # 1 inch
            "bottom": 72   # 1 inch
        }
    )
    
    print(f"\n✅ Success! PDF created at: {result_path}")
    
    # Verify the PDF
    print("\nVerifying PDF metadata...")
    ok, signer, payload = EncypherPDF.verify_pdf(
        result_path,
        lambda sid: private_key.public_key() if sid == "encypher-test" else None
    )
    
    if ok:
        print(f"✅ Verification successful!")
        print(f"  Signer ID: {signer}")
        print(f"  Payload: {payload}")
    else:
        print("❌ Verification failed")
        
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
