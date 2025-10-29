"""
Command-line interface for the Encypher Enterprise SDK.

Provides quick access to sign, verify, lookup, and stats operations. The CLI
loads configuration from environment variables and optional `.env` files to
mirror the Enterprise API onboarding flow.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import click
from dotenv import find_dotenv, load_dotenv
from rich.console import Console
from rich.table import Table
from rich.text import Text

from ..client import EncypherClient
from ..exceptions import EncypherError

console = Console()


def _load_environment() -> None:
    """
    Load environment variables from a .env file if present.
    """
    dotenv_path = find_dotenv(usecwd=True)
    if dotenv_path:
        load_dotenv(dotenv_path, override=False)


def _build_client(
    api_key: Optional[str],
    base_url: str,
    timeout: float,
    max_retries: int,
) -> EncypherClient:
    """
    Instantiate an EncypherClient using CLI options or environment variables.
    """
    key = api_key or os.getenv("ENCYPHER_API_KEY")
    if not key:
        raise click.BadParameter(
            "Missing API key. Provide --api-key or set ENCYPHER_API_KEY in your environment."
        )

    return EncypherClient(
        api_key=key,
        base_url=base_url,
        timeout=timeout,
        max_retries=max_retries,
    )


@click.group()
@click.option("--api-key", envvar="ENCYPHER_API_KEY", help="Enterprise API key.")
@click.option(
    "--base-url",
    default="https://api.encypherai.com",
    show_default=True,
    help="Base URL for the Enterprise API.",
)
@click.option("--timeout", default=30.0, show_default=True, help="HTTP request timeout (seconds).")
@click.option("--max-retries", default=3, show_default=True, help="Maximum retries for API calls.")
@click.pass_context
def cli(ctx: click.Context, api_key: Optional[str], base_url: str, timeout: float, max_retries: int) -> None:
    """
    Manage content signing and verification from the terminal.
    """
    _load_environment()
    client = _build_client(api_key, base_url, timeout, max_retries)

    ctx.ensure_object(dict)
    ctx.obj["client"] = client
    ctx.call_on_close(client.close)


def _read_text(text: Optional[str], file: Optional[Path]) -> str:
    """
    Resolve text input from CLI options.
    """
    if text and file:
        raise click.BadParameter("Provide either --text or --file, not both.")
    if file:
        return file.read_text(encoding="utf-8")
    if text:
        return text

    # fallback to stdin
    if not click.get_text_stream("stdin").isatty():
        return click.get_text_stream("stdin").read()

    raise click.BadParameter("No input provided. Use --text, --file, or pipe content via stdin.")


@cli.command("sign")
@click.option("--text", help="Text to sign.")
@click.option("--file", type=click.Path(path_type=Path), help="Path to file containing text to sign.")
@click.option("--title", help="Optional document title.")
@click.option("--url", help="Optional canonical document URL.")
@click.option(
    "--document-type",
    default="ai_output",
    show_default=True,
    help="Document type metadata for the signing request.",
)
@click.option("--output", type=click.Path(path_type=Path), help="Write signed text to a file.")
@click.pass_context
def sign_command(
    ctx: click.Context,
    text: Optional[str],
    file: Optional[Path],
    title: Optional[str],
    url: Optional[str],
    document_type: str,
    output: Optional[Path],
) -> None:
    """
    Sign text content with a C2PA manifest.
    """
    client: EncypherClient = ctx.obj["client"]
    content = _read_text(text, file)

    try:
        result = client.sign(
            text=content,
            title=title,
            url=url,
            document_type=document_type,
        )
    except EncypherError as exc:
        console.print(Text(f"Signing failed: {exc}", style="red"))
        ctx.exit(1)

    if output:
        output.write_text(result.signed_text, encoding="utf-8")
        console.print(Text(f"Signed text written to {output}", style="green"))
    else:
        console.print(Text(result.signed_text, style="green"))

    table = Table(title="Signing Result", box=None)
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="white")
    table.add_row("Document ID", result.document_id)
    table.add_row("Verification URL", result.verification_url or "-")
    table.add_row("Sentences Signed", str(result.total_sentences))
    console.print(table)


@cli.command("verify")
@click.option("--text", help="Signed text to verify.")
@click.option("--file", type=click.Path(path_type=Path), help="Path to file containing signed text.")
@click.pass_context
def verify_command(ctx: click.Context, text: Optional[str], file: Optional[Path]) -> None:
    """
    Verify signed content and display provenance metadata.
    """
    client: EncypherClient = ctx.obj["client"]
    content = _read_text(text, file)

    try:
        result = client.verify(content)
    except EncypherError as exc:
        console.print(Text(f"Verification failed: {exc}", style="red"))
        ctx.exit(1)

    status_style = "green" if result.is_valid else "red"
    console.print(Text(f"Valid: {result.is_valid}", style=status_style))
    console.print(Text(f"Signer ID: {result.signer_id}", style="cyan"))
    console.print(Text(f"Organization: {result.organization_name}", style="cyan"))
    console.print(Text(f"Signed At: {result.signature_timestamp}", style="cyan"))

    if result.manifest:
        manifest_json = json.dumps(result.manifest, indent=2)
        console.print(Text("\nManifest", style="bold"))
        console.print(manifest_json)


@cli.command("lookup")
@click.argument("sentence")
@click.pass_context
def lookup_command(ctx: click.Context, sentence: str) -> None:
    """
    Lookup provenance for a single sentence.
    """
    client: EncypherClient = ctx.obj["client"]

    try:
        result = client.lookup(sentence)
    except EncypherError as exc:
        console.print(Text(f"Lookup failed: {exc}", style="red"))
        ctx.exit(1)

    if not result.found:
        console.print(Text("Sentence not found in signed documents.", style="yellow"))
        return

    table = Table(title="Sentence Provenance", box=None)
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="white")
    table.add_row("Document Title", result.document_title or "-")
    table.add_row("Organization", result.organization_name or "-")
    table.add_row("Publication Date", str(result.publication_date) if result.publication_date else "-")
    table.add_row("Sentence Index", str(result.sentence_index) if result.sentence_index is not None else "-")
    table.add_row("Document URL", result.document_url or "-")
    console.print(table)


@cli.command("stats")
@click.pass_context
def stats_command(ctx: click.Context) -> None:
    """
    Display organization usage statistics.
    """
    client: EncypherClient = ctx.obj["client"]

    try:
        stats = client.get_stats()
    except EncypherError as exc:
        console.print(Text(f"Failed to fetch stats: {exc}", style="red"))
        ctx.exit(1)

    table = Table(title=f"Organization Stats - {stats.organization_name}", box=None)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")
    table.add_row("Tier", stats.tier)
    table.add_row("Documents Signed", str(stats.usage.documents_signed))
    table.add_row("Sentences Signed", str(stats.usage.sentences_signed))
    table.add_row("API Calls (This Month)", str(stats.usage.api_calls_this_month))
    table.add_row("Monthly Quota", str(stats.usage.monthly_quota))
    table.add_row("Quota Remaining", str(stats.usage.quota_remaining))
    console.print(table)


def main() -> None:
    cli(prog_name="encypher")


if __name__ == "__main__":  # pragma: no cover
    main()
