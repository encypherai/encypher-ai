from typing import List, Optional
import logging
import os
from pathlib import Path

import typer

try:
    from encypher_ai import (  # type: ignore[import-not-found]
        EncypherAI,
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

    class EncypherAI:
        """Fallback stub that mimics the public API used in tests."""

        def verify_from_text(self, text: str) -> VerificationResult:
            return VerificationResult(
                status=VerificationStatus.UNKNOWN,
                is_verified=False,
                metadata={},
            )


log = logging.getLogger("audit-log-cli")
app = typer.Typer(add_completion=False)


@app.callback()
def main() -> None:
    """Audit Log CLI root."""


@app.command("generate-report")
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
) -> None:
    """Usage: main.py generate-report

    Generates an audit report for EncypherAI metadata.
    """
    if target and text_input:
        typer.echo("Error: --target and --text options are mutually exclusive.")
        raise typer.Exit(code=1)

    if not target and not text_input:
        typer.echo(
            "Error: Either --target (file/directory path) or --text (direct input) must be provided."
        )
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
            typer.echo(
                f"Error: Target path {target} is not a valid file or directory."
            )
            raise typer.Exit(code=1)

    if not files_to_scan and not processed_texts:
        typer.echo("Error: No files or text inputs to process.")
        raise typer.Exit(code=1)

    ea = EncypherAI()
    results = []

    for file_path in files_to_scan:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
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


if __name__ == "__main__":
    app()
