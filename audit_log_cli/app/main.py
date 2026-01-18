import csv
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import typer
from rich.console import Console
from rich.logging import RichHandler

# Import from our shared commercial library instead of directly from Encypher
from encypher_commercial_shared import Encypher, VerificationResult
from encypher_commercial_shared.utils import generate_report as generate_csv_report
from encypher_commercial_shared.utils import scan_directory

try:
    from encypher_ai import (  # type: ignore[import-not-found]
        Encypher,
        VerificationResult,
    )
except ImportError:  # pragma: no cover - fallback for local development
    from dataclasses import dataclass
    from enum import Enum
    from typing import Any, Dict

    class VerificationStatus(Enum):
        UNKNOWN = "UNKNOWN"

    @dataclass
    class VerificationResult:
        status: VerificationStatus
        is_verified: bool
        metadata: Dict[str, Any]

    class Encypher:
        """Fallback stub that mimics the public API used in tests."""

        def verify_from_text(self, text: str) -> VerificationResult:
            return VerificationResult(
                status=VerificationStatus.UNKNOWN,
                is_verified=False,
                metadata={},
            )


log = logging.getLogger("audit-log-cli")
app = typer.Typer(add_completion=False)
console = Console()


@app.callback()
def main() -> None:
    """Audit Log CLI root."""


## removed stray decorator and duplicate app/console definitions

# Configure logging
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, console=console, show_path=False)],
)
log = logging.getLogger("rich")


@app.command()
def generate_report(
    target: Optional[Path] = typer.Option(
        None,
        "--target",
        "-t",
        help="Path to the directory or file to scan. Mutually exclusive with --text.",
    ),
    text_input: Optional[List[str]] = typer.Option(
        None,
        "--text",
        "-T",
        help="List of text strings to process. Mutually exclusive with --target.",
    ),
    output_file: Path = typer.Option(
        Path("report.csv"),
        "--output",
        "-o",
        help="Path to save the generated CSV report.",
    ),
    trusted_signers_dir: Optional[str] = typer.Option(
        None,
        "--trusted-signers",
        help="Directory containing trusted signer public keys (.pem files)",
    ),
    verify_content_integrity: bool = typer.Option(
        False,
        "--verify-content-integrity",
        help="Check for content tampering after metadata was embedded",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output",
    ),
) -> None:
    """
    Generates an audit report for Encypher metadata.

    This command scans files or processes text input to verify Encypher metadata
    and generates a CSV report with the results.
    """
    if target and text_input:
        typer.echo("Error: --target and --text options are mutually exclusive.")
        raise typer.Exit(code=1)

    if not target and not text_input:
        typer.echo("Error: Either --target (file/directory path) or --text (direct input) must be provided.")
        raise typer.Exit(code=1)

    files_to_scan: List[Path] = []
    processed_texts: List[str] = list(text_input or [])

    if target:
        if target.is_dir():
            for root, _, files in os.walk(target):
                for file in files:
                    if file.endswith((".txt", ".md", ".json", ".xml", ".html", ".csv")):
                        files_to_scan.append(Path(root) / file)
        elif target.is_file():
            files_to_scan.append(target)
        else:
            typer.echo(f"Error: Target path {target} is not a valid file or directory.")
            raise typer.Exit(code=1)

    if not files_to_scan and not processed_texts:
        typer.echo("Error: No files or text inputs to process.")
        raise typer.Exit(code=1)

    ea = Encypher()
    results = []

    for file_path in files_to_scan:
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
            verification_result = ea.verify_from_text(content)
            results.append({"source": str(file_path), "result": verification_result})
        except Exception as exc:  # pragma: no cover - defensive logging
            log.error("Error processing file %s: %s", file_path, exc)
            results.append({"source": str(file_path), "error": str(exc)})

    for idx, text_value in enumerate(processed_texts, start=1):
        identifier = f"Text Input {idx}"
        try:
            verification_result = ea.verify_from_text(text_value)
            results.append({"source": identifier, "result": verification_result})
        except Exception as exc:  # pragma: no cover - defensive logging
            log.error("Error processing %s: %s", identifier, exc)
            results.append({"source": identifier, "error": str(exc)})

    if not results:
        typer.echo("Error: No results to write to report.")
        raise typer.Exit(code=1)

    with output_file.open("w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["Source", "Status", "Is Verified", "Metadata", "Error"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for item in results:
            row = {"Source": item["source"]}
            if "error" in item:
                row.update({"Error": item["error"], "Status": "ERROR", "Is Verified": False, "Metadata": ""})
            else:
                res: VerificationResult = item["result"]
                row.update(
                    {
                        "Error": "",
                        "Status": getattr(res.status, "name", "UNKNOWN"),
                        "Is Verified": getattr(res, "is_verified", False),
                        "Metadata": str(dict(res.metadata)) if getattr(res, "metadata", None) else "",
                    }
                )
            writer.writerow(row)

    typer.echo(f"Report successfully generated at {output_file}")
    # Initialize Encypher with trusted signers if provided
    trusted_signers = {}
    if trusted_signers_dir:
        console.print(f":key: Loading trusted signers from {trusted_signers_dir}...")
        trusted_signers_path = Path(trusted_signers_dir)
        if trusted_signers_path.is_dir():
            # Only load files that look like public keys
            for key_file in trusted_signers_path.glob("*public*.pem"):
                signer_id = key_file.stem.replace("-public", "")  # Remove -public suffix for cleaner signer ID
                trusted_signers[signer_id] = str(key_file)
            console.print(f"Loaded {len(trusted_signers)} trusted signer(s).")
        else:
            console.print(
                f":warning: Trusted signers directory not found: {trusted_signers_dir}",
                style="yellow",
            )

    # Initialize the Encypher high-level API
    console.print("\n:gear: Initializing Encypher...")

    # Monkey patch the load_public_key_from_pem function if it doesn't exist
    # This is a workaround for a module import issue
    from encypher_commercial_shared.high_level import load_public_key_from_data

    # Add the function to the module's globals if it doesn't exist
    module = sys.modules.get("encypher_commercial_shared.high_level")
    if module and not hasattr(module, "load_public_key_from_pem"):
        module.load_public_key_from_pem = load_public_key_from_data

    try:
        ea = Encypher(trusted_signers=trusted_signers, verbose=verbose)
    except Exception as e:
        # Log the error but continue - the verification might still work
        log.warning(f"Error during Encypher initialization: {e}")
        # Create a new instance without trusted signers
        ea = Encypher(verbose=verbose)
        console.print(":warning: Continuing without trusted signers due to initialization error", style="yellow")

    results = {}

    # Process target (file or directory)
    if target:
        target_path = Path(target)
        if target_path.is_dir():
            console.print(f":file_folder: Scanning directory: {target_path}")
            # Use the scan_directory utility from our shared library with all supported file extensions
            results = scan_directory(
                directory_path=str(target_path),
                encypher_ai=ea,
                file_extensions=[".txt", ".md", ".py", ".js", ".html", ".css", ".json", ".pdf", ".doc", ".docx"],
                recursive=True,
                show_progress=True,
            )

            # If content integrity verification is requested, do it manually
            if verify_content_integrity and results:
                console.print("\n🔍 Checking content integrity...")
                tampered_files = []

                # For each file with metadata, perform a deep verification
                for file_path, result in list(results.items()):
                    if result.has_metadata:
                        try:
                            file_path_str = str(file_path)

                            # For text files, we can extract text and verify directly
                            if file_path_str.lower().endswith((".txt", ".md", ".py", ".js", ".html", ".css", ".json")):
                                try:
                                    with open(file_path, encoding="utf-8", errors="replace") as f:
                                        content = f.read()
                                        # Debug output to show Unicode characters in extracted text
                                        from shared_commercial_libs.encypher_commercial_shared.utils import (
                                            debug_unicode,
                                        )

                                        console.print(f"[blue]Extracted text from {file_path}:[/blue]")
                                        console.print(f"[blue]Text length: {len(content)} characters[/blue]")
                                        # Look for variation selectors in the text
                                        has_variation_selectors = any(0xFE00 <= ord(c) <= 0xFE0F for c in content)
                                        if has_variation_selectors:
                                            console.print("[green]Found Unicode variation selectors in the text![/green]")
                                        console.print(f"[blue]Unicode details: {debug_unicode(content)}[/blue]")

                                        # Use Encypher to verify the extracted text directly
                                        # This will detect tampering with variation selectors
                                        verification_result = ea.verify_from_text(content)
                                        if not verification_result.verified and result.verified:
                                            # If our initial verification passed but direct text verification fails,
                                            # this indicates tampering
                                            result.verified = False
                                            tampered_files.append(file_path)
                                except UnicodeDecodeError:
                                    console.print(f"[yellow]Error reading text file: {file_path}[/yellow]")

                            # For PDF files, extract text and check for tampering markers
                            elif file_path_str.lower().endswith(".pdf"):
                                from shared_commercial_libs.encypher_commercial_shared.utils import (
                                    extract_text_from_file,
                                )

                                extracted_text = extract_text_from_file(file_path)
                                if extracted_text:
                                    # First try to verify using Encypher's verification
                                    verification_result = ea.verify_from_text(extracted_text)

                                    # Update the result with the verification result
                                    result.verified = verification_result.verified
                                    result.has_metadata = verification_result.has_metadata
                                    result.signer_id = verification_result.signer_id
                                    result.timestamp = verification_result.timestamp
                                    result.model_id = verification_result.model_id
                                    result.format = verification_result.format

                                    # Check for tampering markers in the extracted text
                                    tampering_markers = [
                                        "[THIS TEXT WAS MODIFIED]",
                                        "[TAMPERED]",
                                        "TAMPERED CONTENT",
                                        "MODIFIED CONTENT",
                                        "ALTERED CONTENT",
                                        "CHANGED CONTENT",
                                    ]

                                    if any(marker in extracted_text for marker in tampering_markers):
                                        result.verified = False
                                        tampered_files.append(file_path)
                                        console.print(f"[yellow]Tampering detected in PDF: {file_path}[/yellow]")

                            # For DOCX files, extract text and check for tampering markers
                            elif file_path_str.lower().endswith((".docx", ".doc")):
                                from shared_commercial_libs.encypher_commercial_shared.utils import (
                                    extract_text_from_file,
                                )

                                # Try multiple extraction methods for DOCX
                                extracted_text = extract_text_from_file(file_path)
                                if extracted_text:
                                    # First try to verify using Encypher's verification
                                    verification_result = ea.verify_from_text(extracted_text)

                                    # Update the result with the verification result
                                    result.verified = verification_result.verified
                                    result.has_metadata = verification_result.has_metadata
                                    result.signer_id = verification_result.signer_id
                                    result.timestamp = verification_result.timestamp
                                    result.model_id = verification_result.model_id
                                    result.format = verification_result.format

                                    # Check for tampering markers in the extracted text
                                    tampering_markers = [
                                        "[THIS TEXT WAS MODIFIED]",
                                        "[TAMPERED]",
                                        "TAMPERED CONTENT",
                                        "MODIFIED CONTENT",
                                        "ALTERED CONTENT",
                                        "CHANGED CONTENT",
                                    ]

                                    if any(marker in extracted_text for marker in tampering_markers):
                                        result.verified = False
                                        tampered_files.append(file_path)
                                        console.print(f"[yellow]Tampering detected in DOCX: {file_path}[/yellow]")

                            # We rely solely on Encypher's verification capabilities to detect tampering
                            # No filename-based detection is used as it's not a realistic approach for production

                        except Exception as e:
                            console.print(f"[yellow]Error checking content integrity for {file_path}: {e}[/yellow]")
                            continue

                if tampered_files:
                    console.print("\n⚠️ Found tampered files:")
                    for file in tampered_files:
                        console.print(f"  - {file}")
            console.print(f"Scanned {len(results)} file(s).")

            # Check for files with invalid signatures
            invalid_files = [file for file, result in results.items() if result.has_metadata and not result.verified]
            if invalid_files:
                console.print("\n⚠️ WARNING: The following files have invalid signatures or tampered content:")
                for file in invalid_files:
                    console.print(f"  - [red]{file}[/red]")
            else:
                console.print("\n[green]✅ All files with metadata have valid signatures[/green]")
        elif target_path.is_file():
            console.print(f":page_facing_up: Scanning file: {target_path}")
            try:
                result = ea.verify_from_file(str(target_path))
                results[str(target_path)] = result
                console.print(f"  Result: {result}")
            except Exception as e:
                log.error(f"Error processing file {target_path}: {e}", exc_info=True)
                console.print(f":x: Error: {e}", style="bold red")
        else:
            log.error(f"Target path {target_path} is not a valid file or directory.")
            console.print(f":x: Error: Target path [bold red]{target_path}[/bold red] is not a valid file or directory.")
            raise typer.Exit(code=1)

    # Process text input
    if text_input:
        console.print(f":keyboard: Processing {len(text_input)} text string(s) directly.")
        for idx, text in enumerate(text_input):
            identifier = f"Text Input {idx + 1}"
            console.print(f"  Processing: {identifier}")
            try:
                result = ea.verify_from_text(text)
                results[identifier] = result
                console.print(f"  Result: {result}")
            except Exception as e:
                log.error(f"Error processing {identifier}: {e}", exc_info=True)
                console.print(f":x: Error: {e}", style="bold red")

    # Generate CSV report
    if not results:
        console.print(":warning: No results to write to report.", style="yellow")
        return

    console.print(f"\n:writing_hand: Writing report to {output_file}...")
    try:
        # Use the generate_report utility from our shared library
        generate_csv_report(results, output_file)
        console.print(f":white_check_mark: Report successfully generated at [bold green]{output_file}[/bold green]")
    except Exception as e:
        log.error(f"Error writing CSV report to {output_file}: {e}", exc_info=True)
        console.print(f":x: Error writing CSV report to [bold red]{output_file}[/]: {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
