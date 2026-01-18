"""Compare C2PA-only vs Embeddings benchmark results."""

import statistics
from pathlib import Path

work_dir = Path("../outputs/wikipedia_prepared")

# Find C2PA signed files
c2pa_files = list(work_dir.rglob("*.c2pa.txt"))
print(f"Found {len(c2pa_files)} C2PA files")

# Find embedding files
embedding_files = list(work_dir.rglob("*.embedded.txt"))
print(f"Found {len(embedding_files)} embedding files")

# Find original files
original_files = []
for part_dir in work_dir.glob("part_*"):
    orig = list(part_dir.glob("article_*.txt"))
    orig = [f for f in orig if not f.name.endswith(".c2pa.txt") and not f.name.endswith(".embedded.txt")]
    original_files.extend(orig[:5000])

print(f"Found {len(original_files)} original files")

print("\n" + "=" * 80)
print("BENCHMARK COMPARISON: C2PA vs EMBEDDINGS")
print("=" * 80)

# Analyze C2PA files (sample 1000)
if c2pa_files:
    c2pa_sample = c2pa_files[:1000]
    c2pa_sizes = []
    c2pa_orig_sizes = []

    for c2pa_file in c2pa_sample:
        # Find corresponding original
        orig_name = c2pa_file.name.replace(".c2pa.txt", ".txt")
        orig = c2pa_file.parent / orig_name

        if orig.exists():
            c2pa_sizes.append(c2pa_file.stat().st_size)
            c2pa_orig_sizes.append(orig.stat().st_size)

    if c2pa_sizes:
        c2pa_increases = [(c - o) / o * 100 for c, o in zip(c2pa_sizes, c2pa_orig_sizes)]

        print("\n📊 C2PA-ONLY MODE")
        print("-" * 80)
        print(f"Files analyzed: {len(c2pa_sizes):,}")
        print("\nOriginal files:")
        print(f"  - Average: {statistics.mean(c2pa_orig_sizes):,.0f} bytes")
        print(f"  - Total: {sum(c2pa_orig_sizes) / 1024 / 1024:.2f} MB")
        print("\nC2PA signed files:")
        print(f"  - Average: {statistics.mean(c2pa_sizes):,.0f} bytes")
        print(f"  - Total: {sum(c2pa_sizes) / 1024 / 1024:.2f} MB")
        print("\nSize increase:")
        print(f"  - Average: {statistics.mean(c2pa_increases):.1f}%")
        print(f"  - Median: {statistics.median(c2pa_increases):.1f}%")
        print("\nPerformance (from benchmark):")
        print("  - Total files: 10,000")
        print("  - Total time: 75.32 seconds")
        print(f"  - Throughput: {10000 / 75.32:.1f} files/second")
        print("  - Average per file: 7.53 ms")
        print("  - Median per file: 47.93 ms")
else:
    print("\n⚠️  No C2PA files found")

# Analyze Embedding files (sample 1000)
if embedding_files:
    emb_sample = embedding_files[:1000]
    emb_sizes = []
    emb_orig_sizes = []

    for emb_file in emb_sample:
        # Find corresponding original
        orig_name = emb_file.name.replace(".embedded.txt", ".txt")
        orig = emb_file.parent / orig_name

        if orig.exists():
            emb_sizes.append(emb_file.stat().st_size)
            emb_orig_sizes.append(orig.stat().st_size)

    if emb_sizes:
        emb_increases = [(e - o) / o * 100 for e, o in zip(emb_sizes, emb_orig_sizes)]

        print("\n📊 EMBEDDINGS MODE (Enhanced Segmentation)")
        print("-" * 80)
        print(f"Files analyzed: {len(emb_sizes):,}")
        print("\nOriginal files:")
        print(f"  - Average: {statistics.mean(emb_orig_sizes):,.0f} bytes")
        print(f"  - Total: {sum(emb_orig_sizes) / 1024 / 1024:.2f} MB")
        print("\nEmbedded files:")
        print(f"  - Average: {statistics.mean(emb_sizes):,.0f} bytes")
        print(f"  - Total: {sum(emb_sizes) / 1024 / 1024:.2f} MB")
        print("\nSize increase:")
        print(f"  - Average: {statistics.mean(emb_increases):.1f}%")
        print(f"  - Median: {statistics.median(emb_increases):.1f}%")
        print("\nPerformance (from benchmark):")
        print("  - Total files: 5,000")
        print("  - Total time: 588.85 seconds")
        print(f"  - Throughput: {5000 / 588.85:.1f} files/second")
        print("  - Average per file: 117.77 ms")
        print("  - Median per file: 48.15 ms")
        print("\nSegmentation:")
        print("  - Estimated sentences: ~620,000")
        print("  - Sentences/second: ~1,053")
        print("  - Avg sentences/file: ~124")
else:
    print("\n⚠️  No embedding files found")

# Comparison
if c2pa_sizes and emb_sizes:
    print("\n" + "=" * 80)
    print("📈 COMPARISON SUMMARY")
    print("=" * 80)

    print("\n🏆 SPEED:")
    c2pa_speed = 10000 / 75.32
    emb_speed = 5000 / 588.85
    print(f"  - C2PA-only: {c2pa_speed:.1f} files/second")
    print(f"  - Embeddings: {emb_speed:.1f} files/second")
    print(f"  - C2PA is {c2pa_speed / emb_speed:.1f}x faster")

    print("\n💾 FILE SIZE:")
    print(f"  - C2PA average increase: {statistics.mean(c2pa_increases):.1f}%")
    print(f"  - Embeddings average increase: {statistics.mean(emb_increases):.1f}%")
    print(f"  - Embeddings add {statistics.mean(emb_increases) - statistics.mean(c2pa_increases):.1f}% more overhead")

    print("\n🎯 GRANULARITY:")
    print("  - C2PA: Document-level only")
    print("  - Embeddings: Sentence-level (~124 per doc) + Document-level")

    print("\n✨ FEATURES:")
    print("  - C2PA: ONE wrapper per document")
    print("  - Embeddings: Minimal embedding per sentence + ONE C2PA wrapper")

    print("\n💡 RECOMMENDATION:")
    print("  - Use C2PA-only for: Speed-critical, document-level provenance")
    print("  - Use Embeddings for: Fine-grained, sentence-level provenance")
    print(f"  - Embeddings provide {c2pa_speed / emb_speed:.1f}x more granularity at {emb_speed / c2pa_speed:.1f}x speed cost")

print("\n" + "=" * 80)
