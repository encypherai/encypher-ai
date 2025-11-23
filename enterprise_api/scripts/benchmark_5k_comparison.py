import argparse
import asyncio
import json
import os
import shutil
import time
import bz2
import re
from pathlib import Path
from urllib.request import urlretrieve
import httpx
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn, TimeRemainingColumn
from rich.table import Table

# Constants
DEFAULT_WIKI_DUMP_URL = "https://dumps.wikimedia.org/simplewiki/latest/simplewiki-latest-pages-articles.xml.bz2"
DATASET_DIR = Path("datasets")
WORK_DIR = Path("outputs")
PREPARED_DIR = WORK_DIR / "wikipedia_prepared"
C2PA_OUT_DIR = WORK_DIR / "c2pa_embedding"
MERKLE_OUT_DIR = WORK_DIR / "merkle_embedding"

console = Console()

def download_if_missing(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        console.print(f"[green]✓ Dump already present: {dest}[/green]")
        return
    console.print(f"[cyan]↓ Downloading dump: {url} -> {dest}[/cyan]")
    try:
        urlretrieve(url, dest)
    except Exception as e:
        if dest.exists():
            dest.unlink(missing_ok=True)
        raise RuntimeError(f"Failed to download dump: {e}")
    console.print("[green]✓ Download complete[/green]")

def simple_extract_dump(dump_path: Path, extract_dir: Path) -> None:
    """Minimal Wikipedia dump extractor."""
    out_file = extract_dir / "pages.json"
    if out_file.exists():
        console.print(f"[green]✓ Extraction exists: {out_file}[/green]")
        return

    count = 0
    page_buf = []
    capturing = False
    out_file.parent.mkdir(parents=True, exist_ok=True)
    
    console.print("[cyan]→ Extracting dump (simple mode)...[/cyan]")
    with bz2.open(dump_path, mode="rt", encoding="utf-8", errors="ignore") as fin, out_file.open("w", encoding="utf-8") as fout:
        for line in fin:
            if not capturing and "<page>" in line:
                capturing = True
                page_buf = [line]
                continue
            if capturing:
                page_buf.append(line)
                if "</page>" in line:
                    page_xml = "".join(page_buf)
                    m_title = re.search(r"<title>(.*?)</title>", page_xml, re.DOTALL)
                    title = m_title.group(1).strip() if m_title else ""
                    m_text = re.search(r"<text[^>]*>(.*?)</text>", page_xml, re.DOTALL)
                    text = m_text.group(1).strip() if m_text else ""
                    if text:
                        obj = {"title": title, "text": text}
                        fout.write(json.dumps(obj, ensure_ascii=False) + "\n")
                        count += 1
                    capturing = False
    console.print(f"[green]✓ Extracted {count:,} pages[/green]")

def prepare_txt_corpus(extract_dir: Path, prepared_dir: Path, limit: int) -> list[Path]:
    if prepared_dir.exists():
        files = list(prepared_dir.glob("article_*.txt"))
        if len(files) >= limit:
            console.print(f"[green]✓ Prepared corpus exists with {len(files)} files[/green]")
            return sorted(files)[:limit]
        # If not enough, clear and rebuild (simplified)
        shutil.rmtree(prepared_dir)
    
    prepared_dir.mkdir(parents=True, exist_ok=True)
    
    files = []
    count = 0
    json_file = extract_dir / "pages.json"
    
    if not json_file.exists():
        raise FileNotFoundError(f"Extracted JSON not found at {json_file}")

    with json_file.open("r", encoding="utf-8") as f:
        for line in f:
            if count >= limit:
                break
            try:
                obj = json.loads(line)
                text = obj.get("text", "").strip()
                title = obj.get("title", "")
                if not text: continue
                
                content = f"{title}\n\n{text}"
                file_path = prepared_dir / f"article_{count:05d}.txt"
                file_path.write_text(content, encoding="utf-8")
                files.append(file_path)
                count += 1
            except json.JSONDecodeError:
                continue
                
    console.print(f"[green]✓ Prepared {len(files)} files[/green]")
    return files

async def run_benchmark(files: list[Path], url: str, output_dir: Path, mode: str, concurrency: int) -> float:
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Demo API Key for local testing
    headers = {"Authorization": "Bearer demo-key-load-test", "Content-Type": "application/json"}
    
    sem = asyncio.Semaphore(concurrency)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Warmup
        try:
            await client.get(url.replace("/api/v1/sign", "/health").replace("/api/v1/enterprise/merkle/encode", "/health"))
        except:
            pass

        async def worker(file_path: Path):
            text = file_path.read_text(encoding="utf-8")
            payload = {}
            
            if mode == "c2pa":
                payload = {"text": text, "title": "Benchmark Doc"}
            elif mode == "merkle":
                payload = {"text": text, "document_id": file_path.stem, "segmentation_levels": ["sentence"]}
            
            async with sem:
                try:
                    resp = await client.post(url, json=payload, headers=headers)
                    resp.raise_for_status()
                    
                    # Save output
                    out_file = output_dir / f"{file_path.stem}.{'signed.txt' if mode == 'c2pa' else 'merkle.json'}"
                    if mode == "c2pa":
                        data = resp.json()
                        out_file.write_text(data.get("signed_text", ""), encoding="utf-8")
                    else:
                        out_file.write_text(resp.text, encoding="utf-8")
                        
                except Exception as e:
                    # console.print(f"[red]Error processing {file_path.name}: {e}[/red]")
                    pass

        start_time = time.time()
        
        with Progress(
            SpinnerColumn(),
            TextColumn(f"[bold blue]{mode.upper()} Benchmark[/bold blue]"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            task = progress.add_task("Processing...", total=len(files))
            
            tasks = []
            for f in files:
                t = asyncio.create_task(worker(f))
                t.add_done_callback(lambda _: progress.advance(task))
                tasks.append(t)
            
            await asyncio.gather(*tasks)
            
    return time.time() - start_time

def main():
    parser = argparse.ArgumentParser(description="5K Document Benchmark")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API Base URL")
    parser.add_argument("--limit", type=int, default=5000, help="Number of docs")
    parser.add_argument("--concurrency", type=int, default=10, help="Concurrent requests")
    args = parser.parse_args()

    # 1. Prepare Data
    wiki_dir = DATASET_DIR / "wikipedia"
    dump_path = wiki_dir / "simplewiki-latest-pages-articles.xml.bz2"
    extract_dir = wiki_dir / "extracted_json"
    
    download_if_missing(DEFAULT_WIKI_DUMP_URL, dump_path)
    simple_extract_dump(dump_path, extract_dir)
    files = prepare_txt_corpus(extract_dir, PREPARED_DIR, args.limit)

    if not files:
        console.print("[red]No files prepared![/red]")
        return

    # 2. Run C2PA Benchmark
    console.print("\n[bold]Starting C2PA Benchmark...[/bold]")
    c2pa_url = f"{args.base_url}/api/v1/sign"
    c2pa_time = asyncio.run(run_benchmark(files, c2pa_url, C2PA_OUT_DIR, "c2pa", args.concurrency))
    
    # 3. Run Merkle Benchmark
    console.print("\n[bold]Starting Merkle Benchmark...[/bold]")
    merkle_url = f"{args.base_url}/api/v1/enterprise/merkle/encode"
    merkle_time = asyncio.run(run_benchmark(files, merkle_url, MERKLE_OUT_DIR, "merkle", args.concurrency))

    # 4. Results
    table = Table(title="Benchmark Results (5k Docs)")
    table.add_column("Metric", style="cyan")
    table.add_column("C2PA Sign", style="magenta")
    table.add_column("Merkle Encode", style="green")
    
    c2pa_tps = len(files) / c2pa_time
    merkle_tps = len(files) / merkle_time
    
    table.add_row("Total Time", f"{c2pa_time:.2f}s", f"{merkle_time:.2f}s")
    table.add_row("Throughput", f"{c2pa_tps:.2f} docs/s", f"{merkle_tps:.2f} docs/s")
    table.add_row("Avg Latency", f"{(c2pa_time/len(files)*1000):.2f} ms", f"{(merkle_time/len(files)*1000):.2f} ms")
    
    console.print("\n")
    console.print(table)

if __name__ == "__main__":
    main()
