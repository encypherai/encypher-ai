#!/usr/bin/env python
"""
Test script for creating and extracting Unicode metadata from PDF files.
This script creates a PDF with Unicode variation selectors and then attempts to extract them
using various methods to verify which approach works best.
"""

import sys
from pathlib import Path

from rich.console import Console

# Initialize console for rich output
console = Console()


def debug_unicode(text):
    """Display Unicode code points in a string, highlighting variation selectors."""
    result = []
    for char in text:
        code_point = ord(char)
        if 0xFE00 <= code_point <= 0xFE0F:  # Variation selectors
            result.append(f"VS-{code_point - 0xFE00 + 1}({hex(code_point)})")
        elif code_point > 127:  # Non-ASCII
            result.append(f"{char}({hex(code_point)})")
        else:
            result.append(char)
    return "".join(result)


def create_test_pdf(output_path, text_with_variation_selectors):
    """Create a PDF with Unicode variation selectors embedded in multiple ways."""
    console.print("[yellow]Creating test PDF with Unicode variation selectors...[/yellow]")

    # Ensure required packages are installed using uv
    try:
        import reportlab
    except ImportError:
        console.print("[yellow]Installing reportlab with uv...[/yellow]")
        import subprocess

        subprocess.check_call([sys.executable, "-m", "uv", "add", "reportlab"])

    try:
        import pikepdf
    except ImportError:
        console.print("[yellow]Installing pikepdf with uv...[/yellow]")
        import subprocess

        subprocess.check_call([sys.executable, "-m", "uv", "add", "pikepdf"])
        import pikepdf

    # Import required modules
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    # Create a basic PDF
    pdf_path = str(output_path)
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    # Add title and explanatory text
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Unicode Variation Selectors Test")

    c.setFont("Helvetica", 12)
    y_position = height - 80

    c.drawString(50, y_position, "This PDF contains Unicode variation selectors embedded in multiple ways:")
    y_position -= 20
    c.drawString(50, y_position, "1. As document metadata (dc:description)")
    y_position -= 20
    c.drawString(50, y_position, "2. As an attached text file")
    y_position -= 20
    c.drawString(50, y_position, "3. As visible text (may not display all Unicode variation selectors)")
    y_position -= 40

    # Show the Unicode details
    c.drawString(50, y_position, "Unicode details of the test text:")
    y_position -= 20
    c.drawString(50, y_position, debug_unicode(text_with_variation_selectors[:50]) + "...")
    y_position -= 40

    # Add the text content (may not display all Unicode characters correctly)
    c.drawString(50, y_position, "Raw text (variation selectors may not be visible):")
    y_position -= 20
    c.drawString(50, y_position, text_with_variation_selectors[:50] + "...")

    c.save()
    console.print(f"[green]Created basic PDF at {pdf_path}[/green]")

    # Now add the Unicode text as metadata using pikepdf
    pdf = pikepdf.open(pdf_path)

    # Add metadata
    with pdf.open_metadata() as meta:
        meta["dc:description"] = text_with_variation_selectors
        meta["pdf:Producer"] = "Encypher Unicode Metadata Test"

    # Add text as attachment
    filespec = pdf.make_stream(text_with_variation_selectors.encode("utf-8"))
    pdf.attachments["original_text.txt"] = filespec

    # Save with metadata
    pdf.save(pdf_path)
    console.print(f"[green]Added Unicode metadata to PDF: {pdf_path}[/green]")

    return pdf_path


def extract_text_from_pdf(pdf_path):
    """Test various methods of extracting text from PDF with Unicode variation selectors."""
    console.print(f"[yellow]Testing text extraction from PDF: {pdf_path}[/yellow]")

    # Method 1: Extract using pikepdf metadata
    try:
        import pikepdf

        pdf = pikepdf.open(pdf_path)

        # Try to extract from metadata
        console.print("[yellow]Method 1: Extracting from PDF metadata using pikepdf...[/yellow]")
        with pdf.open_metadata() as meta:
            if "dc:description" in meta:
                text = meta["dc:description"]
                console.print(f"[green]Successfully extracted {len(text)} characters from metadata[/green]")
                console.print(f"[blue]First 50 characters with Unicode details: {debug_unicode(text[:50])}...[/blue]")
            else:
                console.print("[red]No dc:description metadata found[/red]")

        # Try to extract from attachment
        console.print("[yellow]Method 2: Extracting from PDF attachment using pikepdf...[/yellow]")
        if "original_text.txt" in pdf.attachments:
            attachment = pdf.attachments["original_text.txt"]
            text = attachment.read().decode("utf-8")
            console.print(f"[green]Successfully extracted {len(text)} characters from attachment[/green]")
            console.print(f"[blue]First 50 characters with Unicode details: {debug_unicode(text[:50])}...[/blue]")
        else:
            console.print("[red]No original_text.txt attachment found[/red]")

    except Exception as e:
        console.print(f"[red]Error extracting with pikepdf: {e}[/red]")

    # Method 3: Extract using PyPDF2
    try:
        import PyPDF2

        console.print("[yellow]Method 3: Extracting using PyPDF2...[/yellow]")

        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()

            if text:
                console.print(f"[green]Successfully extracted {len(text)} characters with PyPDF2[/green]")
                console.print(f"[blue]First 50 characters with Unicode details: {debug_unicode(text[:50])}...[/blue]")
            else:
                console.print("[red]PyPDF2 extracted empty text[/red]")

                # Try to get raw content streams
                console.print("[yellow]Method 3b: Attempting to extract raw content streams with PyPDF2...[/yellow]")
                raw_text = ""
                for page in reader.pages:
                    if "/Contents" in page:
                        contents = page["/Contents"]
                        if isinstance(contents, list):
                            for obj in contents:
                                if hasattr(obj, "get_data"):
                                    raw_text += obj.get_data().decode("utf-8", errors="replace")
                        elif hasattr(contents, "get_data"):
                            raw_text += contents.get_data().decode("utf-8", errors="replace")

                if raw_text:
                    console.print(f"[green]Successfully extracted {len(raw_text)} characters from raw content streams[/green]")
                    console.print(f"[blue]Raw content sample: {raw_text[:100]}...[/blue]")
                else:
                    console.print("[red]Failed to extract raw content streams[/red]")
    except Exception as e:
        console.print(f"[red]Error extracting with PyPDF2: {e}[/red]")

    # Method 4: Extract using pdfminer.six
    try:
        from pdfminer.high_level import extract_text as pdfminer_extract_text

        console.print("[yellow]Method 4: Extracting using pdfminer.six...[/yellow]")

        text = pdfminer_extract_text(pdf_path)
        if text:
            console.print(f"[green]Successfully extracted {len(text)} characters with pdfminer.six[/green]")
            console.print(f"[blue]First 50 characters with Unicode details: {debug_unicode(text[:50])}...[/blue]")
        else:
            console.print("[red]pdfminer.six extracted empty text[/red]")
    except Exception as e:
        console.print(f"[red]Error extracting with pdfminer.six: {e}[/red]")

    # Method 5: Binary extraction as fallback
    try:
        console.print("[yellow]Method 5: Binary extraction fallback...[/yellow]")
        with open(pdf_path, "rb") as f:
            content = f.read()
            # Try to decode as UTF-8
            binary_text = content.decode("utf-8", errors="replace")

            # Check if the text contains Unicode variation selectors (0xFE00-0xFE0F)
            import re

            vs_pattern = re.compile(r"[\uFE00-\uFE0F]")
            if vs_pattern.search(binary_text):
                console.print("[green]Found Unicode variation selectors in binary extraction[/green]")
                matches = vs_pattern.findall(binary_text)
                console.print(f"[blue]Found {len(matches)} variation selectors in binary data[/blue]")
            else:
                console.print("[red]No Unicode variation selectors found in binary data[/red]")
    except Exception as e:
        console.print(f"[red]Error with binary extraction: {e}[/red]")


def main():
    """Main function to test PDF creation and extraction with Unicode variation selectors."""
    # Create a test string with Unicode variation selectors
    test_text = "This is a test with Unicode variation selectors: A󠄀 B󠄁 C󠄂 D󠄃 E󠄄 F󠄅 G󠄆 H󠄇 I󠄈 J󠄉 K󠄊 L󠄋 M󠄌 N󠄍 O󠄎 P󠄏"

    # Add more variation selectors
    for i in range(0xFE00, 0xFE0F + 1):
        char = chr(i)
        test_text += f" VS{i - 0xFE00 + 1}:{char}"

    # Create output directory if it doesn't exist
    output_dir = Path(__file__).parent / "unicode_test_output"
    output_dir.mkdir(exist_ok=True)

    # Create test PDF
    pdf_path = output_dir / "unicode_test.pdf"
    created_pdf = create_test_pdf(pdf_path, test_text)

    # Extract and test
    extract_text_from_pdf(created_pdf)

    console.print(f"[green]Test completed. PDF saved at: {pdf_path}[/green]")


if __name__ == "__main__":
    main()
