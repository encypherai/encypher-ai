import csv
import logging
import os
from pathlib import Path

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress

from encypher_ai import Encypher

from .policy_parser import PolicySchemaError, load_policy
from .validator import validate_metadata

app = typer.Typer()
console = Console()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console, rich_tracebacks=True)],
)
log = logging.getLogger("policy_validator")


@app.command()
def validate_metadata(
    input_path: str = typer.Option(
        ..., "--input", "-i", help="Path to the directory or file to scan."
    ),
    policy_file: str = typer.Option(
        ..., "--policy", "-p", help="Path to the JSON policy file."
    ),
    output_file: str = typer.Option(
        "validation_report.csv",
        "--output",
        "-o",
        help="Path to save the validation CSV report.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed validation results in console output.",
    ),
):
    """
    Validates Encypher metadata against a defined policy.
    """
    # 1. Load and parse the policy file
    console.print(
        f":shield: Loading policy from: [bold yellow]{policy_file}[/bold yellow]"
    )
    try:
        policy_data = load_policy(Path(policy_file))
        console.print(
            f":white_check_mark: Policy '{policy_data['policy_name']}' loaded successfully with {len(policy_data['rules'])} rules."
        )
    except (PolicySchemaError, FileNotFoundError, Exception) as e:
        console.print(f":x: Error loading policy file: {e}", style="bold red")
        log.error(f"Error loading policy file: {e}", exc_info=True)
        raise typer.Exit(code=1)

    # 2. Collect files to scan
    input_path = Path(input_path)
    console.print(
        f":magnifying_glass_tilted_left: Scanning input: [bold cyan]{input_path}[/bold cyan]"
    )

    files_to_scan = []
    if input_path.is_file():
        files_to_scan.append(input_path)
    elif input_path.is_dir():
        for root, _, files in os.walk(input_path):
            for file in files:
                # Only scan text-based files (you might want to add more extensions)
                if file.endswith(
                    (".txt", ".md", ".json", ".py", ".js", ".html", ".css", ".xml")
                ):
                    files_to_scan.append(Path(root) / file)
    else:
        console.print(f":x: Input path does not exist: {input_path}", style="bold red")
        raise typer.Exit(code=1)

    if not files_to_scan:
        console.print(":warning: No files found to scan.", style="yellow")
        raise typer.Exit(code=0)

    console.print(f":page_facing_up: Found {len(files_to_scan)} files to scan.")
    console.print(
        f":page_facing_up: Validation report will be saved to: [bold green]{output_file}[/bold green]"
    )

    # 3. Initialize Encypher
    console.print("\n:gear: Initializing Encypher...")
    ea = Encypher()  # Using default configuration

    # 4. Process files and validate metadata
    all_results = []

    with Progress(console=console) as progress:
        task = progress.add_task("[cyan]Validating files...", total=len(files_to_scan))

        for file_path in files_to_scan:
            progress.update(
                task, description=f"[cyan]Validating: [bold]{file_path.name}[/bold]"
            )

            try:
                # Read file content
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                # Extract metadata using Encypher
                verification_result = ea.verify_from_text(content)

                # Validate metadata against policy rules
                if verification_result.metadata:
                    is_valid, validation_errors = validate_metadata(
                        dict(verification_result.metadata),
                        policy_data["rules"],
                        str(file_path),
                    )

                    result = {
                        "source": str(file_path),
                        "is_verified": verification_result.is_verified,
                        "status": verification_result.status.name,
                        "policy_valid": is_valid,
                        "errors": validation_errors,
                        "metadata": (
                            dict(verification_result.metadata)
                            if verification_result.metadata
                            else {}
                        ),
                    }
                else:
                    # No metadata found
                    result = {
                        "source": str(file_path),
                        "is_verified": verification_result.is_verified,
                        "status": verification_result.status.name,
                        "policy_valid": False,
                        "errors": ["No metadata found"],
                        "metadata": {},
                    }

                all_results.append(result)

                # Print detailed output if verbose mode is enabled
                if verbose:
                    console.print(f"\nFile: {file_path}")
                    console.print(
                        f"  Status: {verification_result.status.name}, Verified: {verification_result.is_verified}"
                    )
                    console.print(f"  Policy Valid: {result['policy_valid']}")
                    if result["errors"]:
                        console.print("  Errors:")
                        for error in result["errors"]:
                            console.print(f"    - {error}")
                    if verification_result.metadata:
                        console.print(
                            f"  Metadata: {dict(verification_result.metadata)}"
                        )

            except Exception as e:
                log.error(f"Error processing file {file_path}: {e}", exc_info=True)
                all_results.append(
                    {
                        "source": str(file_path),
                        "is_verified": False,
                        "status": "ERROR",
                        "policy_valid": False,
                        "errors": [f"Error processing file: {e}"],
                        "metadata": {},
                    }
                )

            finally:
                progress.advance(task)

    # 5. Write results to CSV
    try:
        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            # Determine all possible metadata keys across all files
            all_metadata_keys = set()
            for result in all_results:
                if result["metadata"]:
                    all_metadata_keys.update(result["metadata"].keys())

            # Create CSV writer with dynamic columns based on metadata keys
            fieldnames = ["source", "is_verified", "status", "policy_valid", "errors"]
            fieldnames.extend(sorted(all_metadata_keys))  # Add metadata keys as columns

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for result in all_results:
                # Prepare row data
                row_data = {
                    "source": result["source"],
                    "is_verified": result["is_verified"],
                    "status": result["status"],
                    "policy_valid": result["policy_valid"],
                    "errors": "; ".join(result["errors"]) if result["errors"] else "",
                }

                # Add metadata values
                for key in all_metadata_keys:
                    row_data[key] = result["metadata"].get(key, "")

                writer.writerow(row_data)

        console.print(
            f"\n:white_check_mark: Validation report saved to: [bold green]{output_file}[/bold green]"
        )
    except Exception as e:
        console.print(f":x: Error writing CSV report: {e}", style="bold red")
        log.error(f"Error writing CSV report: {e}", exc_info=True)
        raise typer.Exit(code=1)

    # 6. Print summary
    valid_count = sum(1 for r in all_results if r["policy_valid"])
    invalid_count = len(all_results) - valid_count

    console.print("\n:bar_chart: Validation Summary:")
    console.print(f"  Total files scanned: {len(all_results)}")
    console.print(f"  Policy compliant: {valid_count}")
    console.print(f"  Policy violations: {invalid_count}")

    if invalid_count > 0:
        console.print(
            "\n:warning: Some files do not comply with the policy. See the CSV report for details.",
            style="yellow",
        )
    else:
        console.print(
            "\n:party_popper: All files comply with the policy!", style="green"
        )


if __name__ == "__main__":
    app()
