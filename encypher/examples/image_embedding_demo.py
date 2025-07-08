"""
Image Embedding Demo for EncypherPDF

This example demonstrates how to embed images in PDFs using the EncypherPDF class.
"""

import os
import sys
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

# Add the parent directory to the path so we can import the encypher package
sys.path.append(str(Path(__file__).parent.parent.parent))

from encypher.pdf_generator import EncypherPDF, FontError, PDFGenerationError, ImageError


def main():
    # Create a directory for the output files
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Generate a key pair for signing
    private_key = Ed25519PrivateKey.generate()
    
    # Example text
    text = """
    # Image Embedding Demo
    
    This PDF demonstrates the image embedding feature of EncypherPDF.
    
    The image below is embedded in the PDF using the `images` parameter.
    
    
    
    
    
    
    
    
    
    
    
    
    Text continues below the image. The image position is automatically calculated
    to ensure it doesn't overlap with the text.
    
    EncypherPDF supports embedding multiple images in a single PDF, with control
    over position, size, and aspect ratio.
    """
    
    # Path to an example image
    # Note: You'll need to replace this with an actual image path
    image_path = "path/to/your/image.jpg"
    
    # Check if the image exists, if not, provide instructions
    if not os.path.exists(image_path):
        print(f"Image not found at {image_path}")
        print("Please update the script with a valid image path.")
        print("Example usage:")
        print("    python image_embedding_demo.py path/to/your/image.jpg")
        
        # If command line argument is provided, use it as the image path
        if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
            image_path = sys.argv[1]
            print(f"Using provided image: {image_path}")
        else:
            return
    
    # Generate a PDF with an embedded image
    try:
        pdf_path = output_dir / "image_demo.pdf"
        
        EncypherPDF.from_text(
            text=text,
            output_path=str(pdf_path),
            private_key=private_key,
            signer_id="demo-signer",
            timestamp="2024-01-01T00:00:00Z",
            images=[
                {
                    "path": image_path,
                    "x": 72,                # 1 inch from left margin
                    "y": 400,               # Y position in points
                    "width": 450,           # Width in points (6.25 inches)
                    "preserve_aspect_ratio": True
                }
            ]
        )
        
        print(f"PDF with embedded image created at: {pdf_path.absolute()}")
        
        # Example with multiple images
        pdf_path_multi = output_dir / "multi_image_demo.pdf"
        
        EncypherPDF.from_text(
            text="This PDF contains multiple embedded images.",
            output_path=str(pdf_path_multi),
            private_key=private_key,
            signer_id="demo-signer",
            timestamp="2024-01-01T00:00:00Z",
            images=[
                {
                    "path": image_path,
                    "x": 72,                # 1 inch from left margin
                    "y": 500,               # Y position in points
                    "width": 200,           # Width in points
                    "preserve_aspect_ratio": True
                },
                {
                    "path": image_path,
                    "x": 300,               # X position in points
                    "y": 500,               # Y position in points
                    "width": 200,           # Width in points
                    "preserve_aspect_ratio": True
                }
            ]
        )
        
        print(f"PDF with multiple embedded images created at: {pdf_path_multi.absolute()}")
        
    except ImageError as e:
        print(f"Image error: {e}")
    except FontError as e:
        print(f"Font error: {e}")
    except PDFGenerationError as e:
        print(f"PDF generation error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
