#!/usr/bin/env python
"""
Test script to convert a specific Word document to PDF with metadata embedded in the first word.
"""
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

# Add the parent directory to sys.path to ensure imports work
sys.path.insert(0, str(Path(__file__).parent))

# Use correct import paths
from encypher.core.unicode_metadata import UnicodeMetadata, MetadataTarget
from encypher.pdf_generator import EncypherPDF

def main():
    """Test converting a specific Word document to PDF with metadata in the first word."""
    print("Testing specific Word document conversion with metadata embedding in first word...")
    
    # Path to the specific Word document
    docx_file = r"C:\Users\eriks\encypher_ai_master\docs\AI Agent System Implementation Guide_gemini.docx"
    
    # Check if the file exists
    if not os.path.exists(docx_file):
        print(f"Error: File not found at {docx_file}")
        return
    
    # Generate output PDF path
    output_pdf = os.path.join(os.path.dirname(docx_file), "AI_Agent_System_Implementation_Guide_with_metadata.pdf")
    
    # Generate a key pair for signing and current timestamp
    private_key = Ed25519PrivateKey.generate()
    signer_id = "test-signer"
    current_timestamp = datetime.now(timezone.utc)
    
    print(f"Converting {docx_file} to PDF with metadata embedded in first word...")
    
    try:
        # Convert docx to PDF with metadata targeting the first word
        pdf_path = EncypherPDF.from_docx(
            docx_file=docx_file,
            output_file=output_pdf,
            private_key=private_key,
            signer_id=signer_id,
            timestamp=current_timestamp,
            target=MetadataTarget.FIRST_LETTER  # Target the first letter of words
        )
        
        print(f"Successfully generated PDF at: {pdf_path}")
        
        # Extract and verify the text from the PDF
        print("Extracting text from the generated PDF...")
        extracted_text = EncypherPDF.extract_text(pdf_path)
        
        # Check if metadata is present in the extracted text
        metadata = UnicodeMetadata.extract_metadata(extracted_text)
        if metadata:
            print("✅ Metadata successfully embedded and extracted from PDF!")
            print(f"Metadata: {metadata}")
        else:
            print("❌ No metadata found in the extracted text.")
            print("Checking if metadata was embedded as an attachment...")
            
            # Check if the PDF has an embedded metadata file
            import fitz
            doc = fitz.open(pdf_path)
            names = doc.embfile_names()
            
            if "embedded_metadata.txt" in names:
                buffer = doc.embfile_get("embedded_metadata.txt")
                if buffer and isinstance(buffer, dict) and "content" in buffer:
                    embedded_text = buffer["content"].decode("utf-8")
                    metadata = UnicodeMetadata.extract_metadata(embedded_text)
                elif buffer and isinstance(buffer, bytes):
                    embedded_text = buffer.decode("utf-8")
                    metadata = UnicodeMetadata.extract_metadata(embedded_text)
                    
                if metadata:
                    print("✅ Metadata found in embedded attachment!")
                    print(f"Metadata: {metadata}")
                else:
                    print("❌ No valid metadata found in embedded attachment.")
            else:
                print("❌ No embedded metadata attachment found in PDF.")
        
        print("\nTest completed.")
        
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
