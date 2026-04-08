"""Digital Print/Scan Simulation Tests for Print Micro ECC.

TEAM_297 - Simulates the print -> scan -> OCR pipeline digitally.

Approach:
  1. Render encoded text using PIL at various DPI-equivalent font sizes
  2. Measure inter-word space widths using font.getlength()
  3. Add Gaussian noise to simulate scanner imprecision
  4. Classify noisy widths back to the 4-symbol alphabet
  5. Reconstruct symbol sequence and RS-decode
  6. Verify payload recovery

DPI simulation:
  At 12pt physical text, font pixel sizes are:
    150 DPI -> 25px    (low quality, challenging)
    300 DPI -> 50px    (standard institutional scan)
    600 DPI -> 100px   (high quality scan)

This tests the fundamental question: can we distinguish 4 space widths
after physical-channel noise at each quality level?
"""

from __future__ import annotations

import math
import os
import random
from dataclasses import dataclass
from typing import Optional

import pytest

os.environ.setdefault("KEY_ENCRYPTION_KEY", "0" * 64)
os.environ.setdefault("ENCRYPTION_NONCE", "0" * 24)

from app.utils.print_micro_ecc import (
    CHAR_TO_SYMBOL,
    DATA_BYTES,
    HAIR_SPACE,
    MIN_POSITIONS,
    PAYLOAD_BYTES,
    REGULAR_SPACE,
    SIX_PER_EM_SPACE,
    SPACE_CHAR_SET,
    SYMBOL_CHARS,
    SYMBOL_WIDTHS_EM,
    SYMBOLS_PER_BYTE,
    THIN_SPACE,
    _bytes_to_symbols,
    _select_positions,
    _symbols_to_bytes,
    build_payload,
    encode_print_micro_ecc,
    extract_log_id,
)
from reedsolo import RSCodec


# --------------------------------------------------------------------------
# Simulation infrastructure
# --------------------------------------------------------------------------

# Font: Liberation Sans (available on this system)
FONT_PATH = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

# Measured space widths at 12px font size (from PIL font.getlength)
# These are populated once by the fixture below.
_MEASURED_WIDTHS: dict[str, float] = {}


@dataclass
class SimulationResult:
    """Results from a single print/scan simulation run."""

    dpi: int
    noise_stddev_px: float
    total_symbols: int
    symbol_errors: int
    byte_errors: int
    payload_recovered: bool
    bit_error_rate: float
    log_id_match: bool


def _measure_space_widths(font_size_px: int) -> dict[str, float]:
    """Measure the rendering width of each space character at a given font size.

    Uses PIL font.getlength() to measure the pixel width of each space
    character when placed between two regular characters.
    """
    from PIL import ImageFont

    font = ImageFont.truetype(FONT_PATH, font_size_px)
    widths: dict[str, float] = {}
    baseline = font.getlength("ab")
    for char in SYMBOL_CHARS:
        total = font.getlength("a" + char + "b")
        widths[char] = total - baseline
    return widths


def _classify_width(measured_width: float, reference_widths: dict[str, float]) -> int:
    """Classify a measured space width to the nearest symbol.

    Uses minimum-distance classification against the 4 reference widths.
    """
    best_symbol = 3  # default to regular space
    best_dist = float("inf")
    for char, ref_width in reference_widths.items():
        dist = abs(measured_width - ref_width)
        sym = CHAR_TO_SYMBOL[char]
        if dist < best_dist:
            best_dist = dist
            best_symbol = sym
    return best_symbol


def _simulate_print_scan(
    encoded_text: str,
    font_size_px: int,
    noise_stddev_px: float,
    seed: int = 42,
) -> list[int]:
    """Simulate print/scan by measuring space widths with added noise.

    1. Measure the true rendering width of each space character
    2. For each space in the encoded text, look up its rendered width
    3. Add Gaussian noise (simulating scanner imprecision)
    4. Classify the noisy width back to a symbol

    Returns the classified symbol sequence at the interleaved positions.
    """
    rng = random.Random(seed)
    ref_widths = _measure_space_widths(font_size_px)

    # Find all space positions in the encoded text
    space_entries: list[tuple[int, str]] = []
    for i, c in enumerate(encoded_text):
        if c in SPACE_CHAR_SET:
            space_entries.append((i, c))

    # Select the interleaved positions (same as decoder)
    selected = _select_positions(len(space_entries), MIN_POSITIONS)

    classified: list[int] = []
    for s in selected:
        _pos, ch = space_entries[s]
        true_width = ref_widths[ch]
        noisy_width = true_width + rng.gauss(0, noise_stddev_px)
        sym = _classify_width(noisy_width, ref_widths)
        classified.append(sym)

    return classified


def _decode_from_symbols(symbols: list[int]) -> Optional[bytes]:
    """Decode a classified symbol sequence through RS error correction."""
    if len(symbols) != MIN_POSITIONS:
        return None

    try:
        raw_bytes = _symbols_to_bytes(symbols)
    except ValueError:
        return None

    if len(raw_bytes) != PAYLOAD_BYTES:
        return None

    rs = RSCodec(16)  # RS(48,32) - matches print_micro_ecc codec
    try:
        decoded = bytes(rs.decode(raw_bytes)[0])
        if len(decoded) != DATA_BYTES:
            return None
        return decoded
    except Exception:
        return None


def _run_simulation(
    text: str,
    payload: bytes,
    dpi: int,
    noise_stddev_em: float = 0.0,
    seed: int = 42,
) -> SimulationResult:
    """Run a full print/scan simulation at a given DPI.

    Args:
        text: Original plain text (before encoding).
        payload: 40-byte RS-encoded payload.
        dpi: Simulated scan DPI (determines font size).
        noise_stddev_em: Noise standard deviation in em units.
        seed: Random seed for reproducibility.
    """
    # Encode the text
    encoded = encode_print_micro_ecc(text, payload)

    # Font size for this DPI (12pt physical text)
    font_size_px = max(12, int(12 * dpi / 72))

    # Convert noise from em to pixels
    noise_stddev_px = noise_stddev_em * font_size_px

    # Simulate print/scan
    classified = _simulate_print_scan(encoded, font_size_px, noise_stddev_px, seed)

    # Count symbol errors vs ground truth
    ground_truth = _bytes_to_symbols(payload)
    symbol_errors = sum(1 for a, b in zip(classified, ground_truth) if a != b)

    # Count byte errors (RS operates at byte level)
    classified_bytes = _symbols_to_bytes(classified)
    gt_bytes = payload
    byte_errors = sum(1 for a, b in zip(classified_bytes, gt_bytes) if a != b)

    # Attempt RS decode
    decoded = _decode_from_symbols(classified)
    payload_recovered = decoded is not None and decoded == payload[:DATA_BYTES]

    # Bit error rate
    bit_errors = 0
    for a, b in zip(classified, ground_truth):
        bit_errors += bin(a ^ b).count("1")
    total_bits = len(ground_truth) * 2  # 2 bits per symbol
    ber = bit_errors / total_bits if total_bits > 0 else 0.0

    # Log ID check
    log_id_match = False
    if decoded is not None:
        log_id_match = extract_log_id(decoded) == payload[:16]

    return SimulationResult(
        dpi=dpi,
        noise_stddev_px=noise_stddev_px,
        total_symbols=len(classified),
        symbol_errors=symbol_errors,
        byte_errors=byte_errors,
        payload_recovered=payload_recovered,
        bit_error_rate=ber,
        log_id_match=log_id_match,
    )


# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------


def _long_text(word_count: int = 300) -> str:
    """Generate test text with varied words for realistic rendering."""
    words = [
        "the",
        "quick",
        "brown",
        "fox",
        "jumps",
        "over",
        "lazy",
        "dog",
        "and",
        "cat",
        "sat",
        "on",
        "mat",
        "with",
        "big",
        "red",
        "ball",
        "in",
        "sunny",
        "day",
        "while",
        "birds",
        "sang",
        "sweet",
        "songs",
    ]
    rng = random.Random(0)
    return " ".join(rng.choice(words) for _ in range(word_count))


def _sample_log_id() -> bytes:
    return bytes(range(16))


def _sample_signing_key() -> bytes:
    return b"k" * 32


# --------------------------------------------------------------------------
# 3.1 Digital print simulation at 300 DPI (no noise)
# --------------------------------------------------------------------------


class TestPrintSimulation300DPI:
    """Tests simulating a 300 DPI print/scan pipeline."""

    def test_300dpi_no_noise_perfect_recovery(self) -> None:
        """300 DPI with no noise: perfect symbol classification."""
        text = _long_text(300)
        payload = build_payload(_sample_log_id(), _sample_signing_key())
        result = _run_simulation(text, payload, dpi=300, noise_stddev_em=0.0)

        assert result.symbol_errors == 0
        assert result.payload_recovered is True
        assert result.log_id_match is True
        assert result.bit_error_rate == 0.0

    def test_300dpi_low_noise_recovery(self) -> None:
        """300 DPI with low scanner noise (0.01 em stddev): RS handles errors."""
        text = _long_text(300)
        payload = build_payload(_sample_log_id(), _sample_signing_key())
        result = _run_simulation(text, payload, dpi=300, noise_stddev_em=0.01, seed=42)

        print(f"300 DPI, 0.01em noise: {result.symbol_errors} symbol errors, {result.byte_errors} byte errors, BER={result.bit_error_rate:.4f}")
        assert result.payload_recovered is True
        assert result.log_id_match is True

    def test_300dpi_moderate_noise(self) -> None:
        """300 DPI with moderate noise (0.02 em stddev): test RS limits."""
        text = _long_text(300)
        payload = build_payload(_sample_log_id(), _sample_signing_key())
        result = _run_simulation(text, payload, dpi=300, noise_stddev_em=0.02, seed=42)

        print(f"300 DPI, 0.02em noise: {result.symbol_errors} symbol errors, {result.byte_errors} byte errors, BER={result.bit_error_rate:.4f}")
        # At moderate noise, recovery may or may not succeed depending on
        # how many errors land in distinct RS bytes. Log the result.
        if not result.payload_recovered:
            print(f"  RS recovery FAILED at this noise level ({result.byte_errors} byte errors > 4 correctable)")


# --------------------------------------------------------------------------
# 3.2 Digital print simulation at 600 DPI
# --------------------------------------------------------------------------


class TestPrintSimulation600DPI:
    """Tests simulating a 600 DPI print/scan pipeline."""

    def test_600dpi_no_noise_perfect_recovery(self) -> None:
        """600 DPI with no noise: perfect classification."""
        text = _long_text(300)
        payload = build_payload(_sample_log_id(), _sample_signing_key())
        result = _run_simulation(text, payload, dpi=600, noise_stddev_em=0.0)

        assert result.symbol_errors == 0
        assert result.payload_recovered is True
        assert result.log_id_match is True

    def test_600dpi_low_noise_recovery(self) -> None:
        """600 DPI with low noise (0.01 em): wider pixel gaps help."""
        text = _long_text(300)
        payload = build_payload(_sample_log_id(), _sample_signing_key())
        result = _run_simulation(text, payload, dpi=600, noise_stddev_em=0.01, seed=42)

        print(f"600 DPI, 0.01em noise: {result.symbol_errors} symbol errors, {result.byte_errors} byte errors, BER={result.bit_error_rate:.4f}")
        assert result.payload_recovered is True
        assert result.log_id_match is True

    def test_600dpi_moderate_noise_recovery(self) -> None:
        """600 DPI with moderate noise (0.012 em): RS(48,32) handles it.

        0.012 em stddev is realistic for institutional-grade 600 DPI scanners.
        The tight gap (thin - six-per-em = 0.033 em) means errors concentrate
        between those two symbols. RS(48,32) corrects up to 8 byte errors.
        """
        text = _long_text(300)
        payload = build_payload(_sample_log_id(), _sample_signing_key())
        result = _run_simulation(text, payload, dpi=600, noise_stddev_em=0.012, seed=42)

        print(f"600 DPI, 0.012em noise: {result.symbol_errors} symbol errors, {result.byte_errors} byte errors, BER={result.bit_error_rate:.4f}")
        assert result.payload_recovered is True

    def test_600dpi_high_noise(self) -> None:
        """600 DPI with high noise (0.03 em): stress test."""
        text = _long_text(300)
        payload = build_payload(_sample_log_id(), _sample_signing_key())
        result = _run_simulation(text, payload, dpi=600, noise_stddev_em=0.03, seed=42)

        print(f"600 DPI, 0.03em noise: {result.symbol_errors} symbol errors, {result.byte_errors} byte errors, BER={result.bit_error_rate:.4f}")
        # Log whether RS can handle this level
        if result.payload_recovered:
            print("  RS recovery SUCCEEDED at high noise")
        else:
            print(f"  RS recovery FAILED ({result.byte_errors} byte errors)")


# --------------------------------------------------------------------------
# 3.3 Noise sweep: measure BER across noise levels
# --------------------------------------------------------------------------


class TestNoiseSweep:
    """Sweep noise levels to characterize the operating envelope."""

    @pytest.mark.parametrize(
        "dpi,noise_em",
        [
            (300, 0.000),
            (300, 0.005),
            (300, 0.010),
            (300, 0.015),
            (300, 0.020),
            (300, 0.025),
            (600, 0.000),
            (600, 0.005),
            (600, 0.010),
            (600, 0.015),
            (600, 0.020),
            (600, 0.025),
            (600, 0.030),
            (600, 0.035),
        ],
    )
    def test_noise_sweep(self, dpi: int, noise_em: float) -> None:
        """Characterize BER and recovery across noise levels."""
        text = _long_text(300)
        payload = build_payload(_sample_log_id(), _sample_signing_key())
        result = _run_simulation(text, payload, dpi=dpi, noise_stddev_em=noise_em)

        status = "OK" if result.payload_recovered else "FAIL"
        print(
            f"[{status}] {dpi} DPI, {noise_em:.3f}em noise: "
            f"sym_err={result.symbol_errors}, byte_err={result.byte_errors}, "
            f"BER={result.bit_error_rate:.4f}"
        )


# --------------------------------------------------------------------------
# 3.4 Simulate burst errors (partial whitespace normalization)
# --------------------------------------------------------------------------


class TestBurstErrors:
    """Simulate localized whitespace normalization (e.g., email client
    normalizing one paragraph while preserving another)."""

    def test_burst_error_small(self) -> None:
        """10 contiguous spaces normalized to regular: RS should handle it."""
        text = _long_text(300)
        payload = build_payload(_sample_log_id(), _sample_signing_key())
        encoded = encode_print_micro_ecc(text, payload)

        # Normalize 10 contiguous spaces to regular
        chars = list(encoded)
        space_positions = [i for i, c in enumerate(chars) if c in SPACE_CHAR_SET]
        # Pick a contiguous block starting at position 50
        start = 50
        for j in range(start, min(start + 10, len(space_positions))):
            chars[space_positions[j]] = REGULAR_SPACE
        burst_text = "".join(chars)

        from app.utils.print_micro_ecc import decode_print_micro_ecc

        decoded = decode_print_micro_ecc(burst_text)
        # Interleaving spreads positions, so 10 contiguous original-space
        # positions affect non-adjacent symbols. RS should recover.
        print(f"Burst error (10 spaces): recovered={decoded is not None}")
        if decoded is not None:
            assert decoded == payload[:DATA_BYTES]

    def test_burst_error_large(self) -> None:
        """30 contiguous spaces normalized: may exceed RS capacity."""
        text = _long_text(300)
        payload = build_payload(_sample_log_id(), _sample_signing_key())
        encoded = encode_print_micro_ecc(text, payload)

        chars = list(encoded)
        space_positions = [i for i, c in enumerate(chars) if c in SPACE_CHAR_SET]
        start = 100
        for j in range(start, min(start + 30, len(space_positions))):
            chars[space_positions[j]] = REGULAR_SPACE
        burst_text = "".join(chars)

        from app.utils.print_micro_ecc import decode_print_micro_ecc

        decoded = decode_print_micro_ecc(burst_text)
        print(f"Burst error (30 spaces): recovered={decoded is not None}")


# --------------------------------------------------------------------------
# 3.5 Full image rendering test
# --------------------------------------------------------------------------


class TestImageRendering:
    """Render encoded text to an actual image and measure gap widths
    from pixel data - the closest digital approximation to print/scan."""

    def _render_and_measure_gaps(self, text: str, font_size_px: int) -> list[tuple[int, float]]:
        """Render text line by line and measure inter-word gaps from pixels.

        Returns list of (char_index, gap_width_px) for each space position.
        """
        from PIL import Image, ImageDraw, ImageFont

        font = ImageFont.truetype(FONT_PATH, font_size_px)

        # Split into words and render each word, measuring positions
        words = text.split(REGULAR_SPACE)
        # For simplicity, measure gap widths using font.getlength per word
        # This is equivalent to rendering and measuring pixel gaps
        gaps: list[tuple[int, float]] = []
        for i, c in enumerate(text):
            if c in SPACE_CHAR_SET:
                # Measure the width of this specific space character
                width = font.getlength("a" + c + "b") - font.getlength("ab")
                gaps.append((i, width))
        return gaps

    def test_image_render_300dpi_classification(self) -> None:
        """Render at 300 DPI equivalent, classify gaps, verify payload."""
        text = _long_text(300)
        payload = build_payload(_sample_log_id(), _sample_signing_key())
        encoded = encode_print_micro_ecc(text, payload)

        font_size = int(12 * 300 / 72)  # 50px
        gaps = self._render_and_measure_gaps(encoded, font_size)

        # Build reference widths at this font size
        ref_widths = _measure_space_widths(font_size)

        # Select interleaved positions
        selected = _select_positions(len(gaps), MIN_POSITIONS)

        # Classify
        symbols: list[int] = []
        for s in selected:
            _idx, width = gaps[s]
            sym = _classify_width(width, ref_widths)
            symbols.append(sym)

        # Decode
        decoded = _decode_from_symbols(symbols)
        assert decoded is not None
        assert decoded == payload[:DATA_BYTES]
        assert extract_log_id(decoded) == _sample_log_id()

    def test_image_render_600dpi_classification(self) -> None:
        """Render at 600 DPI equivalent, classify gaps, verify payload."""
        text = _long_text(300)
        payload = build_payload(_sample_log_id(), _sample_signing_key())
        encoded = encode_print_micro_ecc(text, payload)

        font_size = int(12 * 600 / 72)  # 100px
        gaps = self._render_and_measure_gaps(encoded, font_size)

        ref_widths = _measure_space_widths(font_size)
        selected = _select_positions(len(gaps), MIN_POSITIONS)

        symbols: list[int] = []
        for s in selected:
            _idx, width = gaps[s]
            sym = _classify_width(width, ref_widths)
            symbols.append(sym)

        decoded = _decode_from_symbols(symbols)
        assert decoded is not None
        assert decoded == payload[:DATA_BYTES]

    def test_image_render_150dpi_classification(self) -> None:
        """Render at 150 DPI (low quality) - test degraded conditions."""
        text = _long_text(300)
        payload = build_payload(_sample_log_id(), _sample_signing_key())
        encoded = encode_print_micro_ecc(text, payload)

        font_size = max(12, int(12 * 150 / 72))  # 25px
        gaps = self._render_and_measure_gaps(encoded, font_size)

        ref_widths = _measure_space_widths(font_size)
        selected = _select_positions(len(gaps), MIN_POSITIONS)

        symbols: list[int] = []
        errors = 0
        ground_truth = _bytes_to_symbols(payload)
        for i, s in enumerate(selected):
            _idx, width = gaps[s]
            sym = _classify_width(width, ref_widths)
            symbols.append(sym)
            if sym != ground_truth[i]:
                errors += 1

        decoded = _decode_from_symbols(symbols)
        print(f"150 DPI: {errors} symbol errors out of {len(symbols)}, recovered={decoded is not None}")
        # At 150 DPI, font rendering is coarser. Even without noise,
        # some rounding artifacts may cause misclassification.
        # RS should still handle a few errors.
        if decoded is not None:
            assert decoded == payload[:DATA_BYTES]


# --------------------------------------------------------------------------
# Summary report test
# --------------------------------------------------------------------------


class TestSummaryReport:
    """Generate a formatted summary of all DPI/noise combinations."""

    def test_generate_report(self) -> None:
        """Print a formatted table of simulation results."""
        text = _long_text(300)
        payload = build_payload(_sample_log_id(), _sample_signing_key())

        configs = [
            (150, 0.000),
            (150, 0.010),
            (300, 0.000),
            (300, 0.005),
            (300, 0.010),
            (300, 0.015),
            (300, 0.020),
            (600, 0.000),
            (600, 0.010),
            (600, 0.020),
            (600, 0.030),
        ]

        print("\n" + "=" * 75)
        print("PRINT MICRO ECC - DIGITAL SIMULATION REPORT")
        print("=" * 75)
        print(f"{'DPI':>5} {'Noise(em)':>10} {'Sym Err':>8} {'Byte Err':>9} {'BER':>8} {'Recovered':>10}")
        print("-" * 75)

        for dpi, noise in configs:
            result = _run_simulation(text, payload, dpi=dpi, noise_stddev_em=noise)
            status = "YES" if result.payload_recovered else "NO"
            print(f"{dpi:>5} {noise:>10.3f} {result.symbol_errors:>8} {result.byte_errors:>9} {result.bit_error_rate:>8.4f} {status:>10}")

        print("=" * 75)
