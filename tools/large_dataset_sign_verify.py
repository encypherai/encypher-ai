#!/usr/bin/env python3
"""
Large-scale local signing & verification runner.

Features:
- Downloads a Wikipedia dump if missing (skips if already present)
- Extracts articles using WikiExtractor with JSON output (skips if already extracted)
- Prepares plain .txt files up to a limit (subdirectory chunking)
- Batch signs all prepared files using the Enterprise SDK
- Verifies all signed outputs and prints detailed stats

Usage examples:
  uv run python tools/large_dataset_sign_verify.py --limit 10000 --concurrency 8 \
      --base-url http://localhost:9000 --dataset wikipedia

  uv run python tools/large_dataset_sign_verify.py --limit 50000 --concurrency 12 \
      --base-url http://localhost:9000

Requirements:
  - ENCYPHER_API_KEY must be set in your environment (for non-public signing)
  - wikiextractor must be installed in the UV environment:
      uv add wikiextractor

Notes:
  - Datasets and outputs are ignored by git (.gitignore updated)
  - Default dump is Simple English Wikipedia (smaller, still large). Override with --dump-url.
"""
import argparse
import asyncio
import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List

# Avoid adding new deps; use stdlib urllib for download
from urllib.request import urlretrieve, urlopen
import bz2
import re

# Optional rich progress
try:
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn, TimeRemainingColumn
    HAVE_RICH = True
except Exception:
    HAVE_RICH = False

# SDK imports
try:
    from encypher_enterprise import EncypherClient
    from encypher_enterprise.async_client import AsyncEncypherClient
    from encypher_enterprise.batch import RepositorySigner
    from encypher_enterprise.verification import RepositoryVerifier
except Exception:
    print("Error: enterprise SDK is not available in this workspace.")
    print("Make sure 'enterprise_sdk' is part of the UV workspace and synced.")
    raise


DEFAULT_DATASETS_DIR = Path("datasets")
DEFAULT_WORK_DIR = Path("outputs")
DEFAULT_WIKI_DUMP_URL = (
    # Simple English Wikipedia (smaller than enwiki, still large for tests)
    "https://dumps.wikimedia.org/simplewiki/latest/simplewiki-latest-pages-articles.xml.bz2"
)


@dataclass
class Stats:
    total_files: int
    total_time_s: float
    per_file_times: List[float]

    @property
    def avg_ms(self) -> float:
        return (self.total_time_s / max(self.total_files, 1)) * 1000.0


def human(n: int) -> str:
    return f"{n:,}"


def download_if_missing(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        print(f"✓ Dump already present: {dest}")
        return
    print(f"↓ Downloading dump: {url}\n  → {dest}")
    try:
        urlretrieve(url, dest)
    except Exception as e:
        if dest.exists():
            dest.unlink(missing_ok=True)
        raise RuntimeError(f"Failed to download dump: {e}")
    print("✓ Download complete")


def run_wikiextractor(dump_path: Path, extract_dir: Path, processes: int = 4) -> None:
    """Run WikiExtractor with JSON output. Skips if extract_dir has content."""
    if extract_dir.exists() and any(extract_dir.rglob("*.json")):
        print(f"✓ Extraction exists: {extract_dir}")
        return
    if extract_dir.exists():
        shutil.rmtree(extract_dir)
    extract_dir.mkdir(parents=True, exist_ok=True)

    # Prefer CLI if available; otherwise fallback to module path
    cli_path = shutil.which("wikiextractor")
    if cli_path:
        cmd = [
            cli_path,
            "--json",
            "--no-templates",
            "--links",
            "--processes",
            str(processes),
            "-o",
            str(extract_dir),
            str(dump_path),
        ]
    else:
        cmd = [
            sys.executable,
            "-m",
            "wikiextractor.WikiExtractor",
            "--json",
            "--no-templates",
            "--links",
            "--processes",
            str(processes),
            "-o",
            str(extract_dir),
            str(dump_path),
        ]
    print("→ Running WikiExtractor:", " ".join(cmd))
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        raise RuntimeError(
            "wikiextractor not found. Install it with: uv add wikiextractor"
        )
    except subprocess.CalledProcessError:
        print("! WikiExtractor failed; falling back to simple extractor (no multiprocessing)")
        simple_extract_dump(dump_path, extract_dir)
    print("✓ Extraction complete")


def simple_extract_dump(dump_path: Path, extract_dir: Path) -> None:
    """Minimal Wikipedia dump extractor that writes JSONL with title and text.
    Designed to work on Windows without multiprocessing.
    Output file: extract_dir/pages.json (one JSON per line)
    """
    out_file = extract_dir / "pages.json"
    count = 0
    page_buf: list[str] = []
    capturing = False
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with bz2.open(dump_path, mode="rt", encoding="utf-8", errors="ignore") as fin, out_file.open("w", encoding="utf-8") as fout:
        for line in fin:
            if not capturing and "<page>" in line:
                capturing = True
                page_buf = [line]
                continue
            if capturing:
                page_buf.append(line)
                if "</page>" in line:
                    # Process one page
                    page_xml = "".join(page_buf)
                    # Extract <title>...</title>
                    m_title = re.search(r"<title>(.*?)</title>", page_xml, re.DOTALL)
                    title = m_title.group(1).strip() if m_title else ""
                    # Extract <text ...>...</text>
                    m_text = re.search(r"<text[^>]*>(.*?)</text>", page_xml, re.DOTALL)
                    text = m_text.group(1).strip() if m_text else ""
                    if text:
                        obj = {"title": title, "text": text}
                        fout.write(json.dumps(obj, ensure_ascii=False) + "\n")
                        count += 1
                    capturing = False
        
    print(f"✓ Simple extracted {count:,} pages to {out_file}")

def prepare_txt_corpus(extract_dir: Path, prepared_dir: Path, limit: int, chunk_size: int = 1000) -> int:
    """Convert JSON lines from WikiExtractor into individual .txt files with subdir chunking.
    Skips work for already-prepared files if count >= limit.
    Returns the number of prepared files.
    """
    if prepared_dir.exists():
        existing = len(list(prepared_dir.rglob("*.txt")))
        if existing >= limit:
            print(f"✓ Prepared corpus exists with {human(existing)} files: {prepared_dir}")
            return existing
    else:
        prepared_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    part = 0
    current_dir = prepared_dir / f"part_{part:05d}"
    current_dir.mkdir(parents=True, exist_ok=True)

    # Iterate all JSON files from WikiExtractor.
    json_files = list(extract_dir.rglob("*.json"))
    if not json_files:
        print("Warning: No JSON files found from WikiExtractor output.")

    for jf in json_files:
        with jf.open("r", encoding="utf-8") as f:
            for line in f:
                if count >= limit:
                    print(f"✓ Prepared {human(count)} files")
                    return count
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                # Typical keys: id, url, title, text
                text = obj.get("text", "").strip()
                title = obj.get("title", "")
                if not text:
                    continue
                if count % chunk_size == 0 and count != 0:
                    part += 1
                    current_dir = prepared_dir / f"part_{part:05d}"
                    current_dir.mkdir(parents=True, exist_ok=True)
                file_name = f"article_{count:07d}.txt"
                content = text if not title else f"{title}\n\n{text}"
                (current_dir / file_name).write_text(content, encoding="utf-8")
                count += 1

    print(f"✓ Prepared {human(count)} files (exhausted extractor output)")
    return count


def detect_optimal_concurrency(user_value: Optional[int]) -> int:
    """Pick a sensible default: target ~80% of logical cores when not specified."""
    if user_value and user_value > 0:
        return user_value
    cores = os.cpu_count() or 4
    target = max(2, int(cores * 0.8))
    # Clamp to a sane range
    return min(target, 64)


def detect_extract_procs(user_value: Optional[int]) -> int:
    if user_value and user_value > 0:
        return user_value
    cores = os.cpu_count() or 4
    # On Windows, WikiExtractor uses multiprocessing with 'fork' which is unavailable.
    # Force single process to avoid failures.
    if os.name == "nt":
        return 1
    # Otherwise use up to half the cores, clamp [2, 8]
    return max(2, min(cores // 2, 8))


def check_backend_health(base_url: str, timeout: float = 3.0) -> bool:
    """Check if Enterprise API backend is running and healthy."""
    url = base_url.rstrip("/") + "/health"
    try:
        with urlopen(url, timeout=timeout) as resp:
            if getattr(resp, "status", 200) != 200:
                return False
            data = resp.read()
            try:
                payload = json.loads(data.decode("utf-8", errors="ignore"))
                return payload.get("status") == "healthy"
            except Exception:
                return False
    except Exception:
        return False


def sign_corpus(prepared_dir: Path, concurrency: int, use_sentence_tracking: bool = True, base_url: str = "http://localhost:9000") -> Stats:
    api_key = os.getenv("ENCYPHER_API_KEY")
    if not api_key:
        raise RuntimeError("ENCYPHER_API_KEY is not set. Export it for local signing.")

    # Prefer async client to utilize concurrency
    aclient = AsyncEncypherClient(api_key=api_key, base_url=base_url)
    signer = RepositorySigner(aclient, use_sentence_tracking=use_sentence_tracking, max_concurrent=concurrency)

    start = time.perf_counter()
    # Spinner while signing
    if HAVE_RICH:
        with Progress(SpinnerColumn(), TextColumn("[bold]Signing documents...")) as progress:
            task = progress.add_task("sign", total=None)
            result = signer.sign_directory(
                directory=prepared_dir,
                patterns=["*.txt"],
                exclude_patterns=["**/*.signed.*"],
                recursive=True,
                output_dir=None,
                save_manifest=False,
                incremental=True,
                state_file=prepared_dir / ".encypher-state.json",
                force_resign=False,
                track_versions=False,
            )
            progress.remove_task(task)
    else:
        result = signer.sign_directory(
            directory=prepared_dir,
            patterns=["*.txt"],
            exclude_patterns=["**/*.signed.*"],
            recursive=True,
            output_dir=None,
            save_manifest=False,
            incremental=True,
            state_file=prepared_dir / ".encypher-state.json",
            force_resign=False,
            track_versions=False,
        )
    total = time.perf_counter() - start

    per_file = [r.processing_time for r in result.results]
    print("\nSigning Summary:")
    print(result.summary())

    return Stats(total_files=result.total_files, total_time_s=total, per_file_times=per_file)


def verify_signed(prepared_dir: Path, base_url: str = "http://localhost:9000") -> Stats:
    api_key = os.getenv("ENCYPHER_API_KEY")
    if not api_key:
        raise RuntimeError("ENCYPHER_API_KEY is not set. Export it for local verification.")

    client = EncypherClient(api_key=api_key, base_url=base_url)
    verifier = RepositoryVerifier(client)

    start = time.perf_counter()
    # Progress spinner for verification (SDK does sync verify internally)
    if HAVE_RICH:
        with Progress(SpinnerColumn(), TextColumn("[bold]Verifying documents...")) as progress:
            task = progress.add_task("verify", total=None)
            result = verifier.verify_directory(
                directory=prepared_dir,
                patterns=["*.signed.txt", "*.signed.md", "*.signed.html"],
                exclude_patterns=["node_modules/**", ".git/**"],
                recursive=True,
                fail_on_tampered=False,
            )
            progress.remove_task(task)
    else:
        result = verifier.verify_directory(
            directory=prepared_dir,
            patterns=["*.signed.txt", "*.signed.md", "*.signed.html"],
            exclude_patterns=["node_modules/**", ".git/**"],
            recursive=True,
            fail_on_tampered=False,
        )
    total = time.perf_counter() - start

    per_file = [r.processing_time for r in result.results]
    print("\nVerification Summary:")
    print(result.summary())

    return Stats(total_files=result.total_files, total_time_s=total, per_file_times=per_file)


def print_stats(label: str, stats: Stats) -> None:
    p50 = sorted(stats.per_file_times)[len(stats.per_file_times) // 2] * 1000.0 if stats.per_file_times else 0.0
    p95 = sorted(stats.per_file_times)[int(len(stats.per_file_times) * 0.95)] * 1000.0 if stats.per_file_times else 0.0
    print(f"\n{label} Performance:")
    print(f"  Files: {human(stats.total_files)}")
    print(f"  Total Time: {stats.total_time_s:.2f}s")
    print(f"  Avg per file: {stats.avg_ms:.2f} ms")
    print(f"  P50 per file: {p50:.2f} ms")
    print(f"  P95 per file: {p95:.2f} ms")


async def encode_merkle_async(files: list[Path], base_url: str, concurrency: int) -> Stats:
    api_key = os.getenv("ENCYPHER_API_KEY")
    if not api_key:
        raise RuntimeError("ENCYPHER_API_KEY is not set. Export it for local signing.")
    # Use threadpool to run blocking client in parallel? Better: use httpx directly
    import httpx
    headers = {"Authorization": f"Bearer {api_key}"}
    url = base_url.rstrip("/") + "/api/v1/enterprise/merkle/encode"
    sem = asyncio.Semaphore(concurrency)
    start = time.perf_counter()
    per_file: list[float] = []
    async with httpx.AsyncClient(timeout=60.0, headers=headers) as client:
        async def worker(path: Path):
            text = path.read_text(encoding="utf-8")
            data = {"document_id": path.stem, "text": text, "segmentation_levels": ["sentence"]}
            t0 = time.perf_counter()
            async with sem:
                r = await client.post(url, json=data)
            r.raise_for_status()
            per_file.append(time.perf_counter() - t0)

        if HAVE_RICH:
            with Progress(SpinnerColumn(), TextColumn("[bold]Merkle encoding..."), BarColumn(), TimeElapsedColumn(), TimeRemainingColumn()) as progress:
                task = progress.add_task("encode", total=len(files))
                for i, f in enumerate(files):
                    await worker(f)
                    progress.update(task, advance=1)
        else:
            for f in files:
                await worker(f)
    total = time.perf_counter() - start
    return Stats(total_files=len(files), total_time_s=total, per_file_times=per_file)


async def encode_embeddings_async(files: list[Path], base_url: str, concurrency: int) -> Stats:
    api_key = os.getenv("ENCYPHER_API_KEY")
    if not api_key:
        raise RuntimeError("ENCYPHER_API_KEY is not set. Export it for local signing.")
    import httpx
    headers = {"Authorization": f"Bearer {api_key}"}
    url = base_url.rstrip("/") + "/api/v1/enterprise/embeddings/encode-with-embeddings"
    sem = asyncio.Semaphore(concurrency)
    start = time.perf_counter()
    per_file: list[float] = []
    async with httpx.AsyncClient(timeout=60.0, headers=headers) as client:
        async def worker(path: Path):
            text = path.read_text(encoding="utf-8")
            data = {
                "document_id": path.stem,
                "text": text,
                "segmentation_level": "sentence",
            }
            t0 = time.perf_counter()
            async with sem:
                r = await client.post(url, json=data)
            r.raise_for_status()
            # Save embedded content
            response_json = r.json()
            embedded = response_json.get("embedded_content")
            if embedded:
                out = path.parent / f"{path.stem}.embedded{path.suffix}"
                out.write_text(embedded, encoding="utf-8")
                print(f"✓ Saved {out.name} ({len(embedded)} chars)")
            else:
                print(f"✗ No embedded_content in response for {path.name}")
            per_file.append(time.perf_counter() - t0)

        if HAVE_RICH:
            with Progress(SpinnerColumn(), TextColumn("[bold]Embedding (minimal) sentences..."), BarColumn(), TimeElapsedColumn(), TimeRemainingColumn()) as progress:
                task = progress.add_task("embed", total=len(files))
                for f in files:
                    await worker(f)
                    progress.update(task, advance=1)
        else:
            for f in files:
                await worker(f)
    total = time.perf_counter() - start
    return Stats(total_files=len(files), total_time_s=total, per_file_times=per_file)


def main() -> None:
    parser = argparse.ArgumentParser(description="Large-scale local signing & verification runner")
    parser.add_argument("--dataset", default="wikipedia", choices=["wikipedia"], help="Dataset to use")
    parser.add_argument("--dump-url", default=DEFAULT_WIKI_DUMP_URL, help="Override dump URL (Wikipedia)")
    parser.add_argument("--datasets-dir", type=Path, default=DEFAULT_DATASETS_DIR, help="Datasets base dir")
    parser.add_argument("--work-dir", type=Path, default=DEFAULT_WORK_DIR, help="Working/output dir")
    parser.add_argument("--limit", type=int, default=10000, help="Number of articles to prepare/sign")
    parser.add_argument("--concurrency", type=int, default=0, help="Max concurrent signing tasks (0=auto)")
    parser.add_argument("--extract-procs", type=int, default=0, help="WikiExtractor processes (0=auto)")
    parser.add_argument("--base-url", default="http://localhost:9000", help="Enterprise API base URL")
    parser.add_argument("--mode", choices=["c2pa", "merkle", "embeddings"], default="c2pa", help="Operation mode")
    parser.add_argument("--no-verify", action="store_true", help="Skip verification stage")
    parser.add_argument("--verify-sample", type=int, default=0, help="Verify only N files (0=all)")
    parser.add_argument("--verify-concurrency", type=int, default=0, help="Verification concurrency (0=auto)")

    args = parser.parse_args()

    datasets_dir: Path = args.datasets_dir
    work_dir: Path = args.work_dir

    # Paths
    wiki_dir = datasets_dir / "wikipedia"
    dump_path = wiki_dir / Path(args.dump_url).name
    extract_dir = wiki_dir / "extracted_json"
    prepared_dir = work_dir / "wikipedia_prepared"

    # 0) Check backend health
    if not check_backend_health(args.base_url):
        print(f"Error: backend not healthy at {args.base_url}. Start the API (e.g., uv run uvicorn app.main:app --port 9000) and retry.")
        sys.exit(1)

    # 1) Download dump if missing
    download_if_missing(args.dump_url, dump_path)

    # 2) Extract to JSON if missing
    extract_procs = detect_extract_procs(args.extract_procs)
    print(f"Using extract processes: {extract_procs}")
    run_wikiextractor(dump_path, extract_dir, processes=extract_procs)

    # 3) Prepare .txt corpus up to limit
    if HAVE_RICH:
        with Progress(SpinnerColumn(), TextColumn("[bold]Preparing corpus...")) as progress:
            task = progress.add_task("prepare", total=None)
            prepared_count = prepare_txt_corpus(extract_dir, prepared_dir, limit=args.limit)
            progress.remove_task(task)
    else:
        prepared_count = prepare_txt_corpus(extract_dir, prepared_dir, limit=args.limit)
    if prepared_count == 0:
        print("No articles prepared; nothing to sign.")
        sys.exit(1)

    # 4) Execute based on mode
    concurrency = detect_optimal_concurrency(args.concurrency)
    print(f"Using concurrency: {concurrency}")
    # Only use raw prepared articles (exclude already-processed files like .signed.* or .embedded.*)
    import re as _re
    _all_txt = sorted(prepared_dir.rglob("*.txt"))
    files = [p for p in _all_txt if _re.fullmatch(r"article_\d+\.txt", p.name)][: args.limit]
    if args.mode == "c2pa":
        sign_stats = sign_corpus(prepared_dir, concurrency=concurrency, base_url=args.base_url)
        print_stats("Signing", sign_stats)
    elif args.mode == "merkle":
        merkle_stats = asyncio.run(encode_merkle_async(files, args.base_url, concurrency))
        print_stats("Merkle Encode", merkle_stats)
    elif args.mode == "embeddings":
        embed_stats = asyncio.run(encode_embeddings_async(files, args.base_url, concurrency))
        print_stats("Embeddings", embed_stats)

    # 5) Verification controls (only for c2pa where .signed files exist)
    if args.mode == "c2pa" and not args.no_verify:
        if args.verify_sample and args.verify_sample > 0:
            # Move sample to temp dir and verify subset
            sample_files = sorted((prepared_dir).rglob("*.signed.txt"))[: args.verify_sample]
            if HAVE_RICH:
                with Progress(SpinnerColumn(), TextColumn("[bold]Verifying sample..."), BarColumn(), TimeElapsedColumn(), TimeRemainingColumn()) as progress:
                    task = progress.add_task("verify-sample", total=len(sample_files))
                    # Use SDK verifier but on subset: create a temp dir view by copying paths list
                    # For simplicity, just read and verify per file here
                    api_key = os.getenv("ENCYPHER_API_KEY")
                    from encypher_enterprise import EncypherClient
                    client = EncypherClient(api_key=api_key, base_url=args.base_url)
                    start = time.perf_counter()
                    per_times = []
                    for p in sample_files:
                        t0 = time.perf_counter()
                        client.verify(p.read_text(encoding="utf-8"))
                        per_times.append(time.perf_counter() - t0)
                        progress.update(task, advance=1)
                    total = time.perf_counter() - start
                    print_stats("Verification (sample)", Stats(total_files=len(sample_files), total_time_s=total, per_file_times=per_times))
            else:
                api_key = os.getenv("ENCYPHER_API_KEY")
                from encypher_enterprise import EncypherClient
                client = EncypherClient(api_key=api_key, base_url=args.base_url)
                start = time.perf_counter()
                per_times = []
                for p in sample_files:
                    t0 = time.perf_counter()
                    client.verify(p.read_text(encoding="utf-8"))
                    per_times.append(time.perf_counter() - t0)
                total = time.perf_counter() - start
                print_stats("Verification (sample)", Stats(total_files=len(sample_files), total_time_s=total, per_file_times=per_times))
        else:
            verify_stats = verify_signed(prepared_dir, base_url=args.base_url)
            print_stats("Verification", verify_stats)


if __name__ == "__main__":
    main()
