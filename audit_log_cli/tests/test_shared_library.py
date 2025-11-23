"""
Test script to demonstrate the usage of the shared commercial library.

This script shows how to use the EncypherAI high-level API from the
encypher_commercial_shared library for metadata verification.
"""

from pathlib import Path

# Import from the shared commercial library
from encypher_commercial_shared import EncypherAI, VerificationResult
from encypher_commercial_shared.utils import scan_directory, generate_report

from rich.console import Console

console = Console()


def test_verify_from_text():
    """Test verifying metadata from text using the shared library."""
    console.print("[bold]Testing EncypherAI.verify_from_text[/bold]")
    
    # Sample text with metadata (this is just a placeholder)
    sample_text = "This is a sample text that might contain EncypherAI metadata."
    
    # Initialize the EncypherAI high-level API
    encypher = EncypherAI(verbose=True)
    
    # Verify metadata from text
    result = encypher.verify_from_text(sample_text)
    
    # Display the result
    console.print(f"Verification result: {result}")
    console.print(f"Has metadata: {result.has_metadata}")
    console.print(f"Verified: {result.verified}")
    console.print(f"Signer ID: {result.signer_id}")
    console.print(f"Timestamp: {result.timestamp}")
    console.print(f"Model ID: {result.model_id}")
    console.print(f"Format: {result.format}")
    
    return result


def test_scan_directory():
    """Test scanning a directory for files with metadata."""
    console.print("\n[bold]Testing scan_directory utility[/bold]")
    
    # Get the current directory
    current_dir = Path(__file__).parent
    
    # Initialize the EncypherAI high-level API
    encypher = EncypherAI(verbose=True)
    
    # Scan the current directory for files with metadata
    results = scan_directory(
        directory_path=str(current_dir),
        encypher_ai=encypher,
        file_extensions=[".py", ".txt", ".md"],
        show_progress=True,
    )
    
    # Display the results
    console.print(f"Found {len(results)} files with potential metadata")
    for file_path, result in results.items():
        console.print(f"File: {file_path}")
        console.print(f"  Has metadata: {result.has_metadata}")
        console.print(f"  Verified: {result.verified}")
    
    return results


def test_generate_report():
    """Test generating a report from verification results."""
    console.print("\n[bold]Testing generate_report utility[/bold]")
    
    # Initialize the EncypherAI high-level API
    encypher = EncypherAI(verbose=True)
    
    # Create some sample results
    results = {
        "file1.txt": VerificationResult(
            verified=True,
            signer_id="test-signer",
            raw_payload={"timestamp": "2025-06-03T11:00:00", "model_id": "test-model"}
        ),
        "file2.txt": VerificationResult(
            verified=False,
            signer_id="unknown-signer",
            raw_payload={"timestamp": "2025-06-03T12:00:00"}
        )
    }
    
    # Generate a report
    report_path = "test_report.csv"
    generate_report(results, report_path)
    
    console.print(f"Report generated at {report_path}")
    
    return report_path


if __name__ == "__main__":
    console.print("[bold green]Testing the EncypherAI Commercial Shared Library[/bold green]")
    
    # Run the tests
    test_verify_from_text()
    test_scan_directory()
    test_generate_report()
    
    console.print("[bold green]All tests completed![/bold green]")
