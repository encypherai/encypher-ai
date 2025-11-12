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


@cli.command("stream-sign")
@click.option("--text", help="Text to stream through the signing endpoint.")
@click.option("--file", type=click.Path(path_type=Path), help="File containing text to stream.")
@click.option("--document-title", help="Optional document title metadata.")
@click.option(
    "--document-type",
    default="article",
    show_default=True,
    help="Document type metadata for streaming request.",
)
@click.option("--document-id", help="Optional document identifier.")
@click.option("--run-id", help="Provide to resume/associate with an existing stream run.")
@click.pass_context
def stream_sign_command(
    ctx: click.Context,
    text: Optional[str],
    file: Optional[Path],
    document_title: Optional[str],
    document_type: str,
    document_id: Optional[str],
    run_id: Optional[str],
) -> None:
    """
    Call the Enterprise SSE endpoint and stream signing progress events.
    """
    client: EncypherClient = ctx.obj["client"]
    content = _read_text(text, file)

    try:
        for event in client.stream_sign(
            content,
            document_title=document_title,
            document_type=document_type,
            document_id=document_id,
            run_id=run_id,
        ):
            console.print(
                Text(
                    f"[{event.event}] {json.dumps(event.data)}",
                    style="cyan" if event.event != "error" else "red",
                )
            )
    except EncypherError as exc:
        console.print(Text(f"Streaming sign failed: {exc}", style="red"))
        ctx.exit(1)


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


@cli.command("verify-sentence")
@click.option("--text", help="Text containing invisible embeddings to verify.")
@click.option("--file", type=click.Path(path_type=Path), help="File containing embedded text.")
@click.pass_context
def verify_sentence_command(ctx: click.Context, text: Optional[str], file: Optional[Path]) -> None:
    """
    Verify a single embedded sentence/segment using the public extract endpoint.
    """
    client: EncypherClient = ctx.obj["client"]
    content = _read_text(text, file)

    try:
        result = client.verify_sentence(content)
    except EncypherError as exc:
        console.print(Text(f"Sentence verification failed: {exc}", style="red"))
        ctx.exit(1)

    table = Table(title="Sentence Verification", box=None)
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="white")
    table.add_row("Valid", "Yes" if result.valid else "No")

    if result.document:
        table.add_row("Document ID", result.document.document_id)
        if result.document.title:
            table.add_row("Title", result.document.title)
        table.add_row("Organization", result.document.organization)

    if result.content:
        table.add_row("Leaf Index", str(result.content.leaf_index))
        table.add_row("Leaf Hash", result.content.leaf_hash[:16] + "…")

    if result.merkle_proof:
        table.add_row("Merkle Root", result.merkle_proof.root_hash[:16] + "…")

    console.print(table)


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


@cli.command("sign-repo")
@click.argument("directory", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--pattern",
    "-p",
    multiple=True,
    default=["*.md", "*.txt"],
    help="File patterns to match (can specify multiple)",
)
@click.option(
    "--exclude",
    "-e",
    multiple=True,
    default=["node_modules/**", ".git/**", "**/__pycache__/**"],
    help="Patterns to exclude",
)
@click.option("--author", help="Author name for C2PA metadata")
@click.option("--publisher", help="Publisher name for C2PA metadata")
@click.option("--license", help="License for content (e.g., CC-BY-4.0)")
@click.option("--output-dir", type=click.Path(path_type=Path), help="Output directory for signed files")
@click.option("--save-manifest/--no-save-manifest", default=False, help="Save C2PA manifest to separate file")
@click.option("--recursive/--no-recursive", default=True, help="Recursively scan subdirectories")
@click.option("--incremental", is_flag=True, help="Only sign changed files (uses .encypher-state.json)")
@click.option("--force-resign", is_flag=True, help="Force re-signing even if unchanged (with --incremental)")
@click.option("--state-file", type=click.Path(path_type=Path), help="Custom state file path")
@click.option("--use-git-metadata", is_flag=True, help="Extract metadata from git history")
@click.option("--use-frontmatter", is_flag=True, help="Extract metadata from YAML/TOML/JSON frontmatter")
@click.option("--track-changes", is_flag=True, help="Track version history and generate diffs")
@click.option("--language", help="Specify document language (ISO 639-1 code, e.g., 'en', 'es')")
@click.option("--detect-language", is_flag=True, help="Auto-detect document language")
@click.option("--report", type=click.Path(path_type=Path), help="Save JSON report to file")
@click.option("--report-format", type=click.Choice(['json', 'html', 'markdown', 'csv']), default='json', help="Report format")
@click.option("--report-title", help="Title for HTML/Markdown reports")
@click.pass_context
def sign_repo_command(
    ctx: click.Context,
    directory: Path,
    pattern: tuple,
    exclude: tuple,
    author: Optional[str],
    publisher: Optional[str],
    license: Optional[str],
    output_dir: Optional[Path],
    save_manifest: bool,
    recursive: bool,
    incremental: bool,
    force_resign: bool,
    state_file: Optional[Path],
    use_git_metadata: bool,
    use_frontmatter: bool,
    track_changes: bool,
    language: Optional[str],
    detect_language: bool,
    report: Optional[Path],
    report_format: str,
    report_title: Optional[str],
) -> None:
    """
    Sign all files in a repository with C2PA-compliant metadata.
    
    Examples:
        # Basic signing
        encypher sign-repo ./articles --author "Jane Doe" --publisher "Acme News"
        
        # With metadata extraction
        encypher sign-repo ./articles --use-git-metadata --use-frontmatter
        
        # With version tracking
        encypher sign-repo ./articles --incremental --track-changes
        
        # With language detection
        encypher sign-repo ./articles --detect-language
        encypher sign-repo ./articles --language en
    """
    from ..batch import RepositorySigner, FileMetadata
    from ..metadata_providers import GitMetadataProvider, FrontmatterMetadataProvider, CombinedMetadataProvider
    from ..language import LanguageDetector, detect_language_from_file
    
    client: EncypherClient = ctx.obj["client"]
    
    # Create metadata function based on options
    if use_git_metadata or use_frontmatter:
        providers = []
        
        # Frontmatter takes priority if both are enabled
        if use_frontmatter:
            frontmatter_provider = FrontmatterMetadataProvider(
                fallback_author=author,
                fallback_publisher=publisher
            )
            providers.append(frontmatter_provider)
        
        if use_git_metadata:
            try:
                git_provider = GitMetadataProvider(repo_path=directory)
                providers.append(git_provider)
            except ImportError:
                console.print(Text("Warning: gitpython not installed. Install with: uv add gitpython", style="yellow"))
        
        if len(providers) > 1:
            combined_provider = CombinedMetadataProvider(providers)
            metadata_fn = combined_provider.get_metadata
        elif len(providers) == 1:
            metadata_fn = providers[0].get_metadata
        else:
            # Fallback to manual metadata
            def metadata_fn(file_path: Path) -> FileMetadata:
                return FileMetadata(
                    author=author,
                    publisher=publisher,
                    license=license,
                    created=datetime.fromtimestamp(file_path.stat().st_ctime),
                    modified=datetime.fromtimestamp(file_path.stat().st_mtime),
                )
    else:
        # Manual metadata
        def metadata_fn(file_path: Path) -> FileMetadata:
            return FileMetadata(
                author=author,
                publisher=publisher,
                license=license,
                created=datetime.fromtimestamp(file_path.stat().st_ctime),
                modified=datetime.fromtimestamp(file_path.stat().st_mtime),
            )
    
    # Wrap metadata function with language detection if requested
    if detect_language or language:
        base_metadata_fn = metadata_fn
        lang_detector = LanguageDetector() if detect_language else None
        
        def metadata_fn_with_language(file_path: Path) -> FileMetadata:
            metadata = base_metadata_fn(file_path)
            
            # Add language to custom metadata
            if not metadata.custom:
                metadata.custom = {}
            
            if language:
                # Use specified language
                metadata.custom['language'] = language
            elif detect_language and lang_detector:
                # Auto-detect language
                try:
                    lang_info = detect_language_from_file(file_path, fallback='en')
                    metadata.custom['language'] = lang_info.language
                    metadata.custom['language_confidence'] = lang_info.confidence
                except Exception:
                    # Fallback to English if detection fails
                    metadata.custom['language'] = 'en'
            
            return metadata
        
        metadata_fn = metadata_fn_with_language
    
    console.print(Text(f"\nSigning repository: {directory}", style="bold cyan"))
    console.print(f"Patterns: {', '.join(pattern)}")
    console.print(f"Exclude: {', '.join(exclude)}")
    if incremental:
        console.print(f"Mode: Incremental (only changed files)")
    if track_changes:
        console.print(f"Version tracking: Enabled")
    if language:
        console.print(f"Language: {language}")
    elif detect_language:
        console.print(f"Language detection: Enabled")
    
    # Sign repository
    signer = RepositorySigner(client, use_sentence_tracking=True)
    
    try:
        result = signer.sign_directory(
            directory=directory,
            patterns=list(pattern),
            exclude_patterns=list(exclude),
            metadata_fn=metadata_fn,
            recursive=recursive,
            output_dir=output_dir,
            save_manifest=save_manifest,
            incremental=incremental,
            state_file=state_file,
            force_resign=force_resign,
            track_versions=track_changes,
        )
    except Exception as exc:
        console.print(Text(f"Repository signing failed: {exc}", style="red"))
        ctx.exit(1)
    
    # Display summary
    console.print(Text("\n" + result.summary(), style="bold green"))
    
    # Display results table
    table = Table(title="Signing Results")
    table.add_column("File", style="cyan")
    table.add_column("Status", style="white")
    table.add_column("Document ID", style="yellow")
    table.add_column("Time", style="magenta")
    
    for r in result.results:
        status = "✓" if r.success else "✗"
        status_style = "green" if r.success else "red"
        table.add_row(
            str(r.file_path.name),
            Text(status, style=status_style),
            r.document_id or r.error or "-",
            f"{r.processing_time:.2f}s",
        )
    
    console.print(table)
    
    # Save report if requested
    if report:
        from ..reports import ReportGenerator
        
        generator = ReportGenerator()
        
        if report_format == 'json':
            result.to_json(report)
        elif report_format == 'html':
            title = report_title or f"Content Verification Report - {directory.name}"
            generator.generate_html(result, report, title=title, publisher=publisher)
        elif report_format == 'markdown':
            title = report_title or f"Content Verification Report - {directory.name}"
            generator.generate_markdown(result, report, title=title)
        elif report_format == 'csv':
            generator.generate_csv(result, report)
        
        console.print(Text(f"\n✓ {report_format.upper()} report saved to: {report}", style="green"))


@cli.command("merkle-encode")
@click.option("--text", help="Text to encode.")
@click.option("--file", type=click.Path(path_type=Path), help="Path to file containing text.")
@click.option("--document-id", required=True, help="Unique document identifier")
@click.option(
    "--level",
    "-l",
    multiple=True,
    default=["sentence", "paragraph"],
    help="Segmentation levels (can specify multiple)",
)
@click.pass_context
def merkle_encode_command(
    ctx: click.Context,
    text: Optional[str],
    file: Optional[Path],
    document_id: str,
    level: tuple,
) -> None:
    """
    Encode document into Merkle trees for attribution tracking (Enterprise tier).
    
    Example:
        encypher merkle-encode --file article.txt --document-id doc_123
    """
    client: EncypherClient = ctx.obj["client"]
    content = _read_text(text, file)
    
    try:
        result = client.encode_document_merkle(
            text=content,
            document_id=document_id,
            segmentation_levels=list(level),
        )
    except EncypherError as exc:
        console.print(Text(f"Merkle encoding failed: {exc}", style="red"))
        ctx.exit(1)
    
    console.print(Text("✓ Document encoded successfully", style="green"))
    
    table = Table(title="Merkle Roots")
    table.add_column("Level", style="cyan")
    table.add_column("Root Hash", style="yellow")
    table.add_column("Nodes", style="white")
    
    for level_data in result.get("roots", []):
        table.add_row(
            level_data.get("level", "-"),
            level_data.get("root_hash", "-")[:16] + "...",
            str(level_data.get("node_count", 0)),
        )
    
    console.print(table)


@cli.command("merkle-tree")
@click.argument("root_id")
@click.pass_context
def merkle_tree_command(ctx: click.Context, root_id: str) -> None:
    """
    Retrieve a stored Merkle tree by root ID.
    """
    client: EncypherClient = ctx.obj["client"]
    try:
        tree = client.get_merkle_tree(root_id)
    except EncypherError as exc:
        console.print(Text(f"Failed to retrieve Merkle tree: {exc}", style="red"))
        ctx.exit(1)

    table = Table(title="Merkle Tree", box=None)
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="white")
    table.add_row("Root Hash", tree.root_hash)
    table.add_row("Tree Depth", str(tree.tree_depth or "-"))
    table.add_row("Leaf Count", str(tree.leaf_count or "-"))
    if tree.metadata:
        table.add_row("Metadata Keys", ", ".join(tree.metadata.keys()))
    console.print(table)

    leaves = [node for node in tree.nodes if node.is_leaf][:5]
    if leaves:
        leaf_table = Table(title="First Leaves", box=None)
        leaf_table.add_column("Leaf Index", style="cyan")
        leaf_table.add_column("Hash", style="white")
        for leaf in leaves:
            idx = leaf.leaf_index if leaf.leaf_index is not None else "-"
            leaf_table.add_row(str(idx), leaf.hash[:32] + "…")
        console.print(leaf_table)


@cli.command("merkle-proof")
@click.argument("root_id")
@click.option("--leaf-index", type=int, help="Leaf index to prove.")
@click.option("--leaf-hash", help="Leaf hash to prove.")
@click.pass_context
def merkle_proof_command(
    ctx: click.Context,
    root_id: str,
    leaf_index: Optional[int],
    leaf_hash: Optional[str],
) -> None:
    """
    Retrieve a Merkle proof for a specific leaf.
    """
    client: EncypherClient = ctx.obj["client"]
    try:
        proof = client.get_merkle_proof(root_id, leaf_index=leaf_index, leaf_hash=leaf_hash)
    except EncypherError as exc:
        console.print(Text(f"Failed to retrieve Merkle proof: {exc}", style="red"))
        ctx.exit(1)

    table = Table(title="Merkle Proof", box=None)
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="white")
    table.add_row("Root Hash", proof.root_hash)
    if proof.leaf_index is not None:
        table.add_row("Leaf Index", str(proof.leaf_index))
    if proof.target_hash:
        table.add_row("Target Hash", proof.target_hash)
    table.add_row("Verified", "Yes" if proof.verified else "No")
    console.print(table)

    if proof.proof_path:
        path_table = Table(title="Proof Path", box=None)
        path_table.add_column("#", style="cyan")
        path_table.add_column("Position", style="white")
        path_table.add_column("Hash", style="white")
        for idx, step in enumerate(proof.proof_path, start=1):
            path_table.add_row(str(idx), step.position or "-", step.hash[:32] + "…")
        console.print(path_table)


@cli.command("find-sources")
@click.option("--text", help="Text to find sources for.")
@click.option("--file", type=click.Path(path_type=Path), help="Path to file containing text.")
@click.option("--min-similarity", default=0.8, help="Minimum similarity threshold (0.0-1.0)")
@click.option("--max-results", default=10, help="Maximum number of results")
@click.pass_context
def find_sources_command(
    ctx: click.Context,
    text: Optional[str],
    file: Optional[Path],
    min_similarity: float,
    max_results: int,
) -> None:
    """
    Find source documents for given text (Enterprise tier).
    
    Example:
        encypher find-sources --text "Some text to check" --min-similarity 0.85
    """
    client: EncypherClient = ctx.obj["client"]
    content = _read_text(text, file)
    
    try:
        result = client.find_sources(
            text=content,
            min_similarity=min_similarity,
            max_results=max_results,
        )
    except EncypherError as exc:
        console.print(Text(f"Source attribution failed: {exc}", style="red"))
        ctx.exit(1)
    
    matches = result.get("matches", [])
    
    if not matches:
        console.print(Text("No sources found", style="yellow"))
        return
    
    console.print(Text(f"\nFound {len(matches)} source(s)", style="green"))
    
    table = Table(title="Source Matches")
    table.add_column("Document", style="cyan")
    table.add_column("Similarity", style="yellow")
    table.add_column("Matched Text", style="white")
    
    for match in matches:
        table.add_row(
            match.get("document_id", "-"),
            f"{match.get('similarity', 0):.2%}",
            match.get("matched_text", "-")[:50] + "...",
        )
    
    console.print(table)


@cli.command("verify-repo")
@click.argument("directory", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--pattern",
    "-p",
    multiple=True,
    default=["*.signed.md", "*.signed.txt", "*.signed.html"],
    help="File patterns to match (can specify multiple)",
)
@click.option(
    "--exclude",
    "-e",
    multiple=True,
    default=["node_modules/**", ".git/**"],
    help="Patterns to exclude",
)
@click.option("--recursive/--no-recursive", default=True, help="Recursively scan subdirectories")
@click.option("--fail-on-tampered", is_flag=True, help="Exit with error if tampered files found")
@click.option("--report", type=click.Path(path_type=Path), help="Save verification report")
@click.option("--report-format", type=click.Choice(['json', 'html', 'markdown', 'csv']), default='json', help="Report format")
@click.pass_context
def verify_repo_command(
    ctx: click.Context,
    directory: Path,
    pattern: tuple,
    exclude: tuple,
    recursive: bool,
    fail_on_tampered: bool,
    report: Optional[Path],
    report_format: str,
) -> None:
    """
    Verify all signed files in a repository.
    
    Example:
        encypher verify-repo ./articles
        encypher verify-repo ./articles --fail-on-tampered
    """
    from ..verification import RepositoryVerifier
    
    client: EncypherClient = ctx.obj["client"]
    
    console.print(Text(f"Verifying repository: {directory}", style="bold cyan"))
    console.print(f"Patterns: {', '.join(pattern)}")
    
    # Verify repository
    verifier = RepositoryVerifier(client)
    
    try:
        result = verifier.verify_directory(
            directory=directory,
            patterns=list(pattern),
            exclude_patterns=list(exclude),
            recursive=recursive,
            fail_on_tampered=fail_on_tampered
        )
    except ValueError as exc:
        console.print(Text(f"\n✗ {exc}", style="red bold"))
        ctx.exit(1)
    except Exception as exc:
        console.print(Text(f"Verification failed: {exc}", style="red"))
        ctx.exit(1)
    
    # Display summary
    console.print(Text("\n" + result.summary(), style="bold green"))
    
    # Display results table
    table = Table(title="Verification Results")
    table.add_column("File", style="cyan")
    table.add_column("Status", style="white")
    table.add_column("Organization", style="yellow")
    table.add_column("Time", style="magenta")
    
    for r in result.results:
        if r.is_valid and not r.tampered:
            status = "✓ Valid"
            status_style = "green"
        elif r.tampered:
            status = "⚠ Tampered"
            status_style = "red bold"
        else:
            status = "✗ Invalid"
            status_style = "red"
        
        table.add_row(
            str(r.file_path.name),
            Text(status, style=status_style),
            r.organization_name or r.error or "-",
            f"{r.processing_time:.2f}s",
        )
    
    console.print(table)
    
    # Save report if requested
    if report:
        import json
        
        if report_format == 'json':
            with open(report, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, indent=2)
        elif report_format in ['html', 'markdown', 'csv']:
            # Convert verification result to signing result format for report generator
            from ..batch import BatchSigningResult, SigningResult
            from ..reports import ReportGenerator
            
            signing_results = [
                SigningResult(
                    file_path=r.file_path,
                    success=r.is_valid and not r.tampered,
                    document_id=None,
                    signed_content=None,
                    verification_url=None,
                    error="Tampered" if r.tampered else r.error,
                    metadata=None,
                    processing_time=r.processing_time
                )
                for r in result.results
            ]
            
            signing_result = BatchSigningResult(
                total_files=result.total_files,
                successful=result.valid,
                failed=result.tampered + result.failed,
                results=signing_results,
                total_time=result.total_time
            )
            
            generator = ReportGenerator()
            
            if report_format == 'html':
                generator.generate_html(signing_result, report, title="Verification Report")
            elif report_format == 'markdown':
                generator.generate_markdown(signing_result, report, title="Verification Report")
            elif report_format == 'csv':
                generator.generate_csv(signing_result, report)
        
        console.print(Text(f"\n✓ {report_format.upper()} report saved to: {report}", style="green"))
    
    # Exit with error if tampered files found
    if fail_on_tampered and result.tampered > 0:
        ctx.exit(1)


@cli.command("diff")
@click.argument("file1", type=click.Path(exists=True, path_type=Path))
@click.argument("file2", type=click.Path(exists=True, path_type=Path))
@click.option("--format", type=click.Choice(['text', 'html', 'json']), default='text', help="Output format")
@click.option("--output", type=click.Path(path_type=Path), help="Save diff to file")
def diff_command(
    file1: Path,
    file2: Path,
    format: str,
    output: Optional[Path]
) -> None:
    """
    Generate diff between two file versions.
    
    Example:
        encypher diff article_v1.md article_v2.md
        encypher diff old.md new.md --format html --output diff.html
    """
    from ..diff import generate_diff_report
    
    # Read files
    content1 = file1.read_text(encoding='utf-8')
    content2 = file2.read_text(encoding='utf-8')
    
    # Generate diff
    diff_report = generate_diff_report(
        content1,
        content2,
        old_version=file1.name,
        new_version=file2.name,
        format=format
    )
    
    # Output
    if output:
        output.write_text(diff_report, encoding='utf-8')
        console.print(Text(f"✓ Diff saved to: {output}", style="green"))
    else:
        console.print(diff_report)


@cli.command("detect-language")
@click.option("--text", help="Text to analyze")
@click.option("--file", type=click.Path(exists=True, path_type=Path), help="File to analyze")
@click.option("--top-n", default=1, help="Number of top languages to show")
def detect_language_command(
    text: Optional[str],
    file: Optional[Path],
    top_n: int
) -> None:
    """
    Detect language of text content.
    
    Example:
        encypher detect-language --text "This is English"
        encypher detect-language --file article.md --top-n 3
    """
    from ..language import LanguageDetector
    
    # Get content
    if file:
        content = file.read_text(encoding='utf-8')
    elif text:
        content = text
    else:
        console.print(Text("Error: Provide either --text or --file", style="red"))
        return
    
    # Detect language
    detector = LanguageDetector()
    
    try:
        if top_n == 1:
            lang_info = detector.detect(content)
            lang_name = detector.get_language_name(lang_info.language)
            
            console.print(Text(f"\nDetected Language:", style="bold cyan"))
            console.print(f"  Language: {lang_name} ({lang_info.language})")
            console.print(f"  Confidence: {lang_info.confidence:.1%}")
        else:
            langs = detector.detect_multiple(content, top_n=top_n)
            
            console.print(Text(f"\nTop {len(langs)} Languages:", style="bold cyan"))
            for i, lang in enumerate(langs, 1):
                lang_name = detector.get_language_name(lang.language)
                console.print(f"  {i}. {lang_name} ({lang.language}): {lang.confidence:.1%}")
    
    except ValueError as e:
        console.print(Text(f"Error: {e}", style="red"))


def main() -> None:
    cli(prog_name="encypher")


if __name__ == "__main__":  # pragma: no cover
    main()
