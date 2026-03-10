#!/usr/bin/env python3
"""
Invisible Unicode character Word compatibility research tool.

USAGE
-----
Interactive (default) -- generates test lines then waits for you to paste back:
    python test_invisible_chars_word.py

Generate only (pipe to file or clipboard):
    python test_invisible_chars_word.py --generate

Verify a saved paste-back file:
    python test_invisible_chars_word.py --verify pasted_back.txt
    pbpaste | python test_invisible_chars_word.py --verify -   (macOS)
    xclip -o | python test_invisible_chars_word.py --verify -  (Linux)

WORKFLOW (interactive)
----------------------
1. Run:  python test_invisible_chars_word.py
2. Copy the test lines into Microsoft Word
3. In Word: Ctrl+A, Ctrl+C
4. Click back in the terminal, paste (Ctrl+V / Cmd+V)
5. Press Enter then Ctrl+D (Mac/Linux) or Ctrl+Z + Enter (Windows)
6. Results print immediately
"""

import sys
import unicodedata

# ---------------------------------------------------------------------------
# Character definitions
# Each entry: (short_name, codepoint, full_description, category)
# category: "baseline_good" | "baseline_bad" | "candidate"
# ---------------------------------------------------------------------------

CHARS = [
    # --- Confirmed working in Word (baselines) ---
    ("ZWNJ", 0x200C, "Zero-Width Non-Joiner", "baseline_good"),
    ("ZWJ", 0x200D, "Zero-Width Joiner", "baseline_good"),
    ("CGJ", 0x034F, "Combining Grapheme Joiner", "baseline_good"),
    ("MVS", 0x180E, "Mongolian Vowel Separator", "baseline_good"),
    # --- Confirmed broken in Word (baselines for comparison) ---
    ("ZWSP", 0x200B, "Zero-Width Space [Word STRIPS]", "baseline_bad"),
    ("WJ", 0x2060, "Word Joiner [shows as SPACE]", "baseline_bad"),
    # --- Directional format chars ---
    ("LRM", 0x200E, "Left-to-Right Mark", "candidate"),
    ("RLM", 0x200F, "Right-to-Left Mark", "candidate"),
    # --- Invisible math operators (U+2061-U+2064) ---
    ("FUNC", 0x2061, "Invisible Function Application", "candidate"),
    ("ITIMES", 0x2062, "Invisible Times", "candidate"),
    ("ISEP", 0x2063, "Invisible Separator", "candidate"),
    ("IPLUS", 0x2064, "Invisible Plus", "candidate"),
    # --- Deprecated format chars (U+206A-U+206F) ---
    ("ISS", 0x206A, "Inhibit Symmetric Swapping [deprecated]", "candidate"),
    ("ASS", 0x206B, "Activate Symmetric Swapping [deprecated]", "candidate"),
    ("IAFS", 0x206C, "Inhibit Arabic Form Shaping [deprecated]", "candidate"),
    ("AAFS", 0x206D, "Activate Arabic Form Shaping [deprecated]", "candidate"),
    ("NADS", 0x206E, "National Digit Shapes [deprecated]", "candidate"),
    ("NODS", 0x206F, "Nominal Digit Shapes [deprecated]", "candidate"),
    # --- Plane 14 tag characters (U+E0020-U+E007E) ---
    # Each is a surrogate pair in UTF-16 (Word's internal encoding).
    # Sampling across the range: space, digits, letters, cancel tag.
    ("TAG_SP", 0xE0020, "Tag Space (Plane 14)", "candidate"),
    ("TAG_0", 0xE0030, "Tag Digit Zero (Plane 14)", "candidate"),
    ("TAG_A", 0xE0041, "Tag Latin Capital A (Plane 14)", "candidate"),
    ("TAG_a", 0xE0061, "Tag Latin Small A (Plane 14)", "candidate"),
    ("TAG_z", 0xE007A, "Tag Latin Small Z (Plane 14)", "candidate"),
    ("TAG_END", 0xE007F, "Cancel Tag (Plane 14)", "candidate"),
    # --- Other Cf format chars sometimes overlooked ---
    ("NADS2", 0x2028, "Line Separator [may cause line break!]", "candidate"),
    ("SHY", 0x00AD, "Soft Hyphen [visible at line breaks]", "candidate"),
    ("ZWNBSP", 0xFEFF, "Zero-Width No-Break Space / BOM", "candidate"),
]

N = 10  # Number of invisible chars to embed per test line
SEP = ">>"  # Visible start marker
END = "<<"  # Visible end marker
COL_NAME = 16  # Column width for name
COL_CP = 10  # Column width for code point


def unicode_info(codepoint: int) -> str:
    """Return Unicode category and name for a codepoint."""
    try:
        ch = chr(codepoint)
        cat = unicodedata.category(ch)
        name = unicodedata.name(ch, "unknown")
        return f"{cat} - {name}"
    except (ValueError, OverflowError):
        return "invalid codepoint"


def make_test_line(short_name: str, codepoint: int, description: str) -> str:
    """
    Build one copy-paste test line.

    Format:
        NAME (U+XXXX) | sentence start >>[10x invisible]<< sentence end | description
    """
    try:
        ch = chr(codepoint)
    except (ValueError, OverflowError):
        return f"{short_name:<{COL_NAME}} U+{codepoint:05X} | [invalid codepoint] | {description}"

    invisible_block = ch * N
    label = f"{short_name:<{COL_NAME}} U+{codepoint:05X}"
    body = f"Sentence start {SEP}{invisible_block}{END} sentence end"
    return f"{label} | {body} | {description}"


def generate(out=sys.stdout):
    """Print all test lines to stdout."""
    width = 78

    out.write("=" * width + "\n")
    out.write("INVISIBLE UNICODE WORD COMPATIBILITY TEST\n")
    out.write("=" * width + "\n")
    out.write(f"Each line embeds {N} contiguous copies of one invisible character\n")
    out.write(f"between the markers {SEP!r} and {END!r}.\n")
    out.write("\n")
    out.write("HOW TO TEST:\n")
    out.write("  1. Copy everything below the dashed line into Microsoft Word\n")
    out.write("  2. Note any visual oddities (reversed text = bidi char, visible char = broken)\n")
    out.write("  3. Select all in Word (Ctrl+A), copy (Ctrl+C)\n")
    out.write("  4. Paste into a new file, then run:\n")
    out.write("       python test_invisible_chars_word.py --verify pasted_back.txt\n")
    out.write("\n")
    out.write("INTERPRETING RESULTS:\n")
    out.write("  PASS  - all 10 chars still present between markers\n")
    out.write("  STRIP - chars removed by Word (markers appear adjacent)\n")
    out.write("  PARTIAL - some chars removed (partial survival)\n")
    out.write("  VISIBLE - char renders as a visible glyph (check the sentence!)\n")
    out.write("-" * width + "\n")
    out.write("\n")

    sections = [
        ("baseline_good", "BASELINE: confirmed working in Word"),
        ("baseline_bad", "BASELINE: confirmed broken in Word (for reference)"),
        ("candidate", "CANDIDATES: untested in Word -- this is the research"),
    ]

    for cat_key, cat_label in sections:
        out.write(f"--- {cat_label} ---\n")
        for short_name, codepoint, description, category in CHARS:
            if category != cat_key:
                continue
            out.write(make_test_line(short_name, codepoint, description) + "\n")
        out.write("\n")


def verify(path: str, out=sys.stdout, _text: str | None = None):
    """
    Read pasted-back text and report which invisible chars survived.

    Matches lines by the label prefix (NAME U+XXXXX) and counts how many
    of the expected invisible chars remain between the >> and << markers.

    _text: pre-read text (used by interactive mode to avoid re-reading stdin).
    """
    if _text is not None:
        text = _text
    elif path == "-":
        text = sys.stdin.read()
    else:
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()

    # Build a lookup from label -> (codepoint, description)
    lookup: dict[str, tuple[int, str]] = {}
    for short_name, codepoint, description, _ in CHARS:
        label = f"{short_name:<{COL_NAME}} U+{codepoint:05X}"
        lookup[label] = (codepoint, description)

    out.write("\n")
    out.write("=" * 78 + "\n")
    out.write("WORD COPY-PASTE SURVIVAL RESULTS\n")
    out.write("=" * 78 + "\n")
    out.write(f"{'Name':<{COL_NAME}} {'Codepoint':<{COL_CP}} {'Result':<12} {'Survived':<10} Description\n")
    out.write("-" * 78 + "\n")

    found: set[str] = set()

    for line in text.splitlines():
        # Try to match each known label prefix
        for label, (codepoint, description) in lookup.items():
            if not line.startswith(label):
                continue
            found.add(label)

            # Extract content between >> and <<
            start_idx = line.find(SEP)
            end_idx = line.find(END, start_idx + len(SEP) if start_idx != -1 else 0)

            if start_idx == -1 or end_idx == -1:
                result = "NO MARKERS"
                survived = "?"
            else:
                inner = line[start_idx + len(SEP) : end_idx]
                try:
                    ch = chr(codepoint)
                    count = sum(1 for c in inner if c == ch)
                except (ValueError, OverflowError):
                    count = 0
                survived = f"{count}/{N}"
                if count == N:
                    result = "PASS"
                elif count == 0:
                    result = "STRIPPED"
                else:
                    result = "PARTIAL"

            short_name = label.split()[0]
            cp_str = f"U+{codepoint:05X}"
            out.write(f"{short_name:<{COL_NAME}} {cp_str:<{COL_CP}} {result:<12} {survived:<10} {description}\n")
            break

    # Report any chars whose lines weren't found in the pasted text
    missing = [lbl for lbl in lookup if lbl not in found]
    if missing:
        out.write("\n")
        out.write("Lines not found in pasted text (check your paste captured everything):\n")
        for lbl in missing:
            out.write(f"  {lbl}\n")

    out.write("\n")
    out.write("Unicode properties of candidates:\n")
    out.write("-" * 78 + "\n")
    for short_name, codepoint, description, category in CHARS:
        if category != "candidate":
            continue
        info = unicode_info(codepoint)
        cp_str = f"U+{codepoint:05X}"
        out.write(f"  {short_name:<{COL_NAME}} {cp_str:<{COL_CP}} {info}\n")


def interactive():
    """Generate test lines, then wait for the user to paste back from Word."""
    generate()

    sys.stdout.write("\n")
    sys.stdout.write("=" * 78 + "\n")
    sys.stdout.write("PASTE BACK FROM WORD\n")
    sys.stdout.write("=" * 78 + "\n")
    sys.stdout.write("1. Copy the lines above into Microsoft Word\n")
    sys.stdout.write("2. In Word: Ctrl+A to select all, Ctrl+C to copy\n")
    sys.stdout.write("3. Click back here in the terminal and paste (Ctrl+V / Cmd+V)\n")
    sys.stdout.write("4. Press Enter, then Ctrl+D (Mac/Linux) or Ctrl+Z + Enter (Windows)\n")
    sys.stdout.write("-" * 78 + "\n")
    sys.stdout.flush()

    try:
        pasted = sys.stdin.read()
    except KeyboardInterrupt:
        sys.stdout.write("\nAborted.\n")
        sys.exit(0)

    if not pasted.strip():
        sys.stdout.write("Nothing pasted.\n")
        sys.exit(0)

    verify("-", _text=pasted)


def main():
    args = sys.argv[1:]
    if "--verify" in args:
        idx = args.index("--verify")
        if idx + 1 >= len(args):
            print("Usage: python test_invisible_chars_word.py --verify <file_or_dash>", file=sys.stderr)
            sys.exit(1)
        path = args[idx + 1]
        verify(path)
    elif "--generate" in args:
        generate()
    else:
        interactive()


if __name__ == "__main__":
    main()
