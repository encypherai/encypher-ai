import csv
import logging
import os
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.logging import RichHandler

from encypher_commercial_shared import Encypher, VerificationResult
from encypher_commercial_shared.utils import generate_report as generate_csv_report
from encypher_commercial_shared.utils import scan_directory

app = typer.Typer(add_completion=False)
console = Console()

# Configure logging
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, console=console, show_path=False)],
)
log = logging.getLogger("audit-log-cli")


@app.callback()
def main() -> None:
    """Audit Log CLI root."""


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

    # Load trusted signers
    trusted_signers = {}
    if trusted_signers_dir:
        console.print(f"Loading trusted signers from {trusted_signers_dir}...")
        trusted_signers_path = Path(trusted_signers_dir)
        if trusted_signers_path.is_dir():
            for key_file in trusted_signers_path.glob("*public*.pem"):
                signer_id = key_file.stem.replace("-public", "")
                trusted_signers[signer_id] = str(key_file)
            console.print(f"Loaded {len(trusted_signers)} trusted signer(s).")
        else:
            console.print(
                f"Warning: Trusted signers directory not found: {trusted_signers_dir}",
                style="yellow",
            )

    # Initialize Encypher
    try:
        ea = Encypher(trusted_signers=trusted_signers, verbose=verbose)
    except Exception as e:
        log.warning("Error during Encypher initialization: %s", e)
        ea = Encypher(verbose=verbose)
        console.print("Warning: Continuing without trusted signers due to initialization error", style="yellow")

    results = {}

    # Process target (file or directory)
    if target:
        target_path = Path(target)
        if target_path.is_dir():
            console.print(f"Scanning directory: {target_path}")
            results = scan_directory(
                directory_path=str(target_path),
                encypher_ai=ea,
                file_extensions=[".txt", ".md", ".py", ".js", ".html", ".css", ".json", ".pdf", ".doc", ".docx"],
                recursive=True,
                show_progress=True,
                verify_content_integrity=verify_content_integrity,
            )
            console.print(f"Scanned {len(results)} file(s).")

            invalid_files = [file for file, result in results.items() if result.has_metadata and not result.verified]
            if invalid_files:
                console.print("\nWARNING: The following files have invalid signatures or tampered content:")
                for file in invalid_files:
                    console.print(f"  - [red]{file}[/red]")
            else:
                console.print("\n[green]All files with metadata have valid signatures[/green]")

        elif target_path.is_file():
            console.print(f"Scanning file: {target_path}")
            try:
                result = ea.verify_from_file(str(target_path))
                results[str(target_path)] = result
                console.print(f"  Result: {result}")
            except Exception as e:
                log.error("Error processing file %s: %s", target_path, e, exc_info=True)
                console.print(f"Error: {e}", style="bold red")
        else:
            log.error("Target path %s is not a valid file or directory.", target)
            console.print(f"Error: Target path [bold red]{target}[/bold red] is not a valid file or directory.")
            raise typer.Exit(code=1)

    # Process text input
    if text_input:
        console.print(f"Processing {len(text_input)} text string(s) directly.")
        for idx, text in enumerate(text_input):
            identifier = f"Text Input {idx + 1}"
            console.print(f"  Processing: {identifier}")
            try:
                result = ea.verify_from_text(text)
                results[identifier] = result
                console.print(f"  Result: {result}")
            except Exception as e:
                log.error("Error processing %s: %s", identifier, e, exc_info=True)
                console.print(f"Error: {e}", style="bold red")

    if not results:
        console.print("Warning: No results to write to report.", style="yellow")
        return

    console.print(f"\nWriting report to {output_file}...")
    try:
        generate_csv_report(results, output_file)
        console.print(f"[green]Report successfully generated at [bold]{output_file}[/bold][/green]")
    except Exception as e:
        log.error("Error writing CSV report to %s: %s", output_file, e, exc_info=True)
        console.print(f"Error writing CSV report to [bold red]{output_file}[/]: {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
