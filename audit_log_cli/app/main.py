import csv
import logging
import os
from pathlib import Path

import typer
from encypher_ai import (  # Assuming VerificationResult is relevant for summarizing
    EncypherAI, VerificationResult)
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress

app = typer.Typer()
console = Console()

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
    target: str = typer.Option(
        None,
        "--target",
        "-t",
        help="Path to the directory or file to scan. Mutually exclusive with --text.",
    ),
    text_input: list[str] = typer.Option(
        None,
        "--text",
        "-T",
        help="List of text strings to process. Mutually exclusive with --target.",
    ),
    output_file: str = typer.Option(
        "report.csv", "--output", "-o", help="Path to save the generated CSV report."
    ),
):
    """
    Generates an audit report for EncypherAI metadata.
    """
    if target and text_input:
        log.error("User provided both --target and --text options.")
        console.print(
            ":x: Error: --target and --text options are mutually exclusive.",
            style="bold red",
        )
        raise typer.Exit(code=1)

    if not target and not text_input:
        log.error("User provided neither --target nor --text option.")
        console.print(
            ":x: Error: Either --target (file/directory path) or --text (direct input) must be provided.",
            style="bold red",
        )
        raise typer.Exit(code=1)

    files_to_scan = []
    processed_texts = []

    if target:
        console.print(
            f":magnifying_glass_tilted_left: Scanning target: [bold cyan]{target}[/bold cyan]"
        )
        target_p = Path(target)
        if target_p.is_dir():
            console.print(f"Scanning directory: {target_p}")
            for root, _, files in os.walk(target_p):
                for file in files:
                    # Basic filter for text-like files, can be expanded
                    if file.endswith((".txt", ".md", ".json", ".xml", ".html", ".csv")):
                        files_to_scan.append(Path(root) / file)
        elif target_p.is_file():
            console.print(f"Scanning single file: {target_p}")
            files_to_scan.append(target_p)
        else:
            log.error(f"Target path {target_p} is not a valid file or directory.")
            console.print(
                f":x: Error: Target path [bold red]{target_p}[/bold red] is not a valid file or directory."
            )
            raise typer.Exit(code=1)

        if not files_to_scan:
            console.print(
                ":warning: No files found to scan at the specified target.",
                style="yellow",
            )
            # If only target was specified and no files found, we might want to exit or just proceed if text_input is also handled.
            # For now, if target is given and no files, and no text_input, it's an issue.
            if not text_input:
                return
        else:
            console.print(f"Found {len(files_to_scan)} potential file(s) to scan:")
            for f_path in files_to_scan:
                console.print(f"  - {f_path}")

    if text_input:
        console.print(
            f":keyboard: Processing {len(text_input)} text string(s) directly."
        )
        # Here we would directly process the strings in text_input
        # For now, just acknowledge them. Later, they'll be passed to encypher-ai
        processed_texts = list(text_input)
        for idx, text_item in enumerate(processed_texts):
            console.print(
                f"  - Text input {idx+1}: '{text_item[:50]}...'"
                if len(text_item) > 50
                else f"  - Text input {idx+1}: '{text_item}'"
            )

    if not files_to_scan and not processed_texts:
        console.print(":warning: No files or text inputs to process.", style="yellow")
        return

    console.print(
        f":page_facing_up: Generating report at: [bold green]{output_file}[/bold green]"
    )

    # Placeholder for actual logic
    # 1. Scan files/inputs - (Initial path collection done)
    # 2. Use encypher-ai to extract and verify metadata
    console.print("\n:gear: Initializing EncypherAI...")
    ea = EncypherAI()  # Using default configuration for now

    all_results = []

    # Process files
    if files_to_scan:
        console.print("\n:page_facing_up: Processing files...")
        with Progress(console=console) as progress:
            task = progress.add_task(
                "[cyan]Scanning files...", total=len(files_to_scan)
            )
            for file_path in files_to_scan:
                progress.update(
                    task, description=f"[cyan]Scanning: [bold]{file_path.name}[/bold]"
                )
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    verification_result = ea.verify_from_text(content)
                    all_results.append(
                        {"source": str(file_path), "result": verification_result}
                    )
                    # Suppress verbose output during progress
                    # console.print(f"    Status: {verification_result.status.name}, Valid Signatures: {verification_result.is_verified}")
                    # if verification_result.metadata:
                    #     console.print(f"    Metadata: {dict(verification_result.metadata)}")
                except Exception as e:
                    log.error(f"Error processing file {file_path}: {e}", exc_info=True)
                    all_results.append({"source": str(file_path), "error": str(e)})
                finally:
                    progress.advance(task)

    # Process direct text inputs
    if processed_texts:
        console.print("\n:keyboard: Processing direct text inputs...")
        with Progress(console=console) as progress:
            task = progress.add_task(
                "[cyan]Processing texts...", total=len(processed_texts)
            )
            for idx, text_content in enumerate(processed_texts):
                identifier = f"Text Input {idx+1}"
                progress.update(
                    task, description=f"[cyan]Processing: [bold]{identifier}[/bold]"
                )
                try:
                    verification_result = ea.verify_from_text(text_content)
                    all_results.append(
                        {"source": identifier, "result": verification_result}
                    )
                    # Suppress verbose output during progress
                    # console.print(f"    Status: {verification_result.status.name}, Valid Signatures: {verification_result.is_verified}")
                    # if verification_result.metadata:
                    #     console.print(f"    Metadata: {dict(verification_result.metadata)}")
                except Exception as e:
                    log.error(f"Error processing {identifier}: {e}", exc_info=True)
                    all_results.append({"source": identifier, "error": str(e)})
                finally:
                    progress.advance(task)

    # 3. Aggregate results
    # 4. Write to CSV
    if not all_results:
        console.print("\n:warning: No results to write to report.", style="yellow")
        return

    console.print(f"\n:writing_hand: Writing report to {output_file}...")
    try:
        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["Source", "Status", "Is Verified", "Metadata", "Error"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for item in all_results:
                row = {"Source": item["source"]}
                if "error" in item:
                    row["Error"] = item["error"]
                    row["Status"] = "ERROR"
                    row["Is Verified"] = False
                    row["Metadata"] = ""
                elif "result" in item and isinstance(
                    item["result"], VerificationResult
                ):
                    res = item["result"]
                    row["Status"] = res.status.name
                    row["Is Verified"] = res.is_verified
                    row["Metadata"] = str(dict(res.metadata)) if res.metadata else ""
                    row["Error"] = ""
                else:
                    # Should not happen if logic is correct
                    row["Error"] = "Unknown result structure"
                    row["Status"] = "UNKNOWN"
                    row["Is Verified"] = False
                    row["Metadata"] = ""
                writer.writerow(row)
        console.print(
            f":white_check_mark: Report successfully generated at [bold green]{output_file}[/bold green]"
        )
    except Exception as e:
        log.error(f"Error writing CSV report to {output_file}: {e}", exc_info=True)
        console.print(
            f":x: Error writing CSV report to [bold red]{output_file}[/]: {e}"
        )
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
