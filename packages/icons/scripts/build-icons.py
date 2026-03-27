#!/usr/bin/env python3
"""
Encypher Icon Library - Asset Generator
Generates all SVG, PNG, and ICO variants from the canonical source mark.

Requirements: cairosvg, Pillow (both installed system-wide)
Run: python3 packages/icons/scripts/build-icons.py
"""

import os
import sys
from pathlib import Path

import cairosvg
from PIL import Image, PngImagePlugin

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
PKG_DIR = SCRIPT_DIR.parent
SVG_SOURCE = PKG_DIR / "svg" / "source" / "encypher-mark.svg"
SVG_OUT = PKG_DIR / "svg" / "generated"
PNG_OUT = PKG_DIR / "png" / "generated"
ICO_OUT = PKG_DIR / "ico" / "generated"

# ---------------------------------------------------------------------------
# Brand colors
# ---------------------------------------------------------------------------
NAVY = "#1b2f50"
WHITE = "#ffffff"

# ---------------------------------------------------------------------------
# Path data (from src/paths.ts -- SSOT)
# ---------------------------------------------------------------------------
GROUP_TRANSFORM = "translate(12.7657,8.6617)"
GROUP_TRANSFORM_BG = "translate(1.8,1.8) scale(0.85)"  # 85% centered for bg variants

PATHS = [
    {
        "id": "outer-ring",
        "transform": "matrix(0.02354608,0,0,-0.02354608,9.12685,3.329909)",
        "d": "m 0,0 c 0,232.574 -188.539,421.113 -421.113,421.113 -232.574,0 -421.113,-188.539 -421.113,-421.113 0,-232.574 188.539,-421.113 421.113,-421.113 C -188.539,-421.113 0,-232.574 0,0 m -67.453,353 c 23.979,-23.981 10.797,-65.451 27.768,-92.817 18.974,-30.597 65.954,-33.172 79.076,-65.368 C 53.507,160.182 17.509,121.532 36.361,78.293 46.971,53.959 71.864,40.212 78.136,13.025 88.284,-30.962 46.909,-46.485 34.258,-81.182 c -15.204,-41.698 18.268,-74.005 5.128,-109.592 -10.999,-29.792 -41.748,-34.508 -64.249,-51.817 -35.197,-27.075 -17.661,-69.425 -38.048,-103.822 -23.241,-39.214 -88.417,-7.654 -119.92,-50.318 -15.57,-21.086 -19.66,-51.992 -47.602,-62.02 -37.141,-13.33 -73.918,26.168 -115.134,8.091 -25.387,-11.134 -41.467,-42.977 -71.635,-41.973 -40.694,1.354 -55.371,38.519 -90.549,46.161 -35.155,7.637 -70.921,-23.265 -105.134,-10.989 -29.976,10.755 -32.05,49.686 -54.486,68.033 -46.355,37.908 -104.624,-4.252 -121.466,74.566 -4.219,19.744 -3.26,41.357 -14.786,58.725 -18.598,28.025 -60.437,30.204 -75.202,61.504 -17.044,36.132 21.018,75.308 2.157,118.229 -9.922,22.582 -34.649,37.243 -40.879,61.005 -14.493,55.272 39.927,66.145 45.429,111.924 3.779,31.436 -14.077,58.522 -11.085,85.886 3.876,35.449 42.672,41.122 65.628,60.762 35.771,30.604 19.345,55.434 33.486,91.613 19.578,50.093 74.036,25.042 109.571,50.348 25.488,18.151 33.168,62.191 60.342,73.785 35.996,15.359 70.975,-19.554 106.446,-12.299 28.968,5.924 48.503,41.024 76.508,44.721 48.251,6.372 61.706,-38.856 102.102,-45.992 33.437,-5.906 59.88,20.108 92.391,16.301 38.545,-4.512 40.264,-55.377 66.904,-74.961 30.814,-22.653 78.673,-9.989 102.372,-33.689",
    },
    {
        "id": "inner-circle",
        "transform": "matrix(0.02354608,0,0,-0.02354608,-1.536626,-5.657183)",
        "d": "m 0,0 c -83.528,-5.076 -162.357,-38.8 -224.157,-94.394 -158.015,-142.145 -166.457,-385.295 -21.94,-540.428 165.409,-177.56 446.282,-154.97 588.662,38.19 84.213,114.248 95.688,274.838 27.221,399.718 C 297.105,-64.347 150.152,9.124 0,0 M 5.205,23.285 C 143.817,30.151 272.03,-27.605 356.728,-136.46 456.427,-264.595 466.08,-451.411 376.376,-587.884 263.962,-758.908 71.908,-818.956 -121.656,-750.26 c -32.852,11.659 -77.116,41.147 -104.929,62.729 -96.585,74.95 -157.627,226.56 -144.421,347.923 6.569,60.365 23.33,122.486 56.048,173.515 71.625,111.712 185.876,182.726 320.163,189.378",
    },
    {
        "id": "checkmark",
        "transform": "matrix(0.02354608,0,0,-0.02354608,2.376377,0.760557)",
        "d": "m 0,0 c 29.751,29.632 61.152,66.947 92.627,93.729 8.727,7.426 13.408,10.728 25.56,6.146 16.328,-6.156 45.296,-50.829 60.057,-63.748 2.451,-4.138 2.004,-9.397 -0.391,-13.439 -87.041,-90.36 -177.441,-177.881 -267.071,-265.566 -20.595,-20.148 -44.143,-48.328 -65.711,-65.836 -10.684,-8.674 -16.474,-8.656 -27.14,0 l -193.453,193.451 c -5.327,5.857 -6.63,16.108 -1.906,22.6 21.521,18.741 40.871,44.559 62.52,62.579 10.895,9.068 18.62,9.015 29.722,-0.002 36.955,-34.62 71.913,-79.106 110.22,-111.604 3.871,-3.284 10.239,-8.849 15.195,-9.415 13.191,-1.507 37.453,29.815 46.694,39.13 C -75.711,-74.315 -37.573,-37.422 0,0",
    },
    {
        "id": "inner-arc",
        "transform": "matrix(0.02354608,0,0,-0.02354608,3.544771,-1.265833)",
        "d": "m 0,0 c -0.216,0.126 -1.012,2.659 -2.026,3.71 -54.348,56.357 -145.316,79.861 -221.695,68.13 -72.555,-11.143 -128.881,-46.55 -174.916,-102.365 -117.608,-142.594 -43.035,-367.034 132.52,-416.806 113.594,-32.204 209.023,-4.247 287.25,82.155 53.615,59.218 77.446,146.726 59.953,225.052 0.463,2.527 14.054,16.355 15.468,14.84 16.044,-65.162 5.842,-132.859 -21.313,-193.404 -36.108,-80.507 -143.607,-155.591 -232.049,-160.015 -159.635,-7.985 -288.716,89.134 -312.403,248.714 -17.045,114.837 39.58,227.12 138.491,285.019 91.096,53.324 197.675,49.923 288.862,-0.821 C -34.567,50.151 15.294,16.303 15.289,12.073 12.155,9.902 3.731,-2.182 0,0",
    },
]

# The ENCYPHER wordmark as a pathed-out Roboto Bold (from the original full logo SVG).
# This is already vector -- no font dependency.
WORDMARK_PATH_D = "M 486.47461,-102.83203 V 0 H 145.89844 V -102.83203 Z M 188.96484,-639.84375 V 0 H 57.128906 v -639.84375 z m 253.125,260.5957 v 100.19532 h -296.1914 v -100.19532 z m 43.94532,-260.5957 v 103.27148 H 145.89844 v -103.27148 z m 596.74574,0 V 0 H 950.94492 L 693.86484,-428.90625 V 0 H 562.0289 v -639.84375 h 131.83594 l 257.51953,429.3457 v -429.3457 z m 483.7464,427.58789 h 131.3965 q -3.955,64.59961 -35.5957,114.697266 -31.2011,50.097657 -87.4511,78.222657 -55.8106,28.1249995 -134.4727,28.1249995 -61.5234,0 -110.3027,-21.0937505 -48.7793,-21.533203 -83.4961,-61.523437 -34.2774,-39.990235 -52.295,-96.679685 -18.0175,-56.68946 -18.0175,-127.00196 v -44.38476 q 0,-70.3125 18.457,-127.00195 18.8965,-57.12891 53.6133,-97.11914 35.1562,-39.99024 83.9355,-61.52344 48.7793,-21.53321 108.9844,-21.53321 79.9805,0 134.9121,29.00391 55.3711,29.00391 85.6934,79.98047 30.7617,50.97656 36.914,116.01562 h -131.8359 q -2.1973,-38.67187 -15.3809,-65.47851 -13.1836,-27.24609 -39.9902,-40.86914 -26.3672,-14.0625 -70.3125,-14.0625 -32.959,0 -57.5684,12.30469 -24.6093,12.30468 -41.3085,37.35351 -16.6993,25.04883 -25.0489,63.28125 -7.9101,37.79297 -7.9101,88.76953 v 45.26367 q 0,49.65821 7.4707,87.45118 7.4707,37.35351 22.8515,63.28125 15.8203,25.48828 40.4297,38.67187 25.0488,12.744142 60.2051,12.744142 41.3086,0 68.1152,-13.183592 26.8067,-13.1836 40.8692,-39.11133 14.5019,-25.92773 17.1386,-64.59961 z m 306.4922,-427.58789 133.5938,291.79688 133.5937,-291.79688 h 143.7012 l -210.498,406.93359 V 0 h -133.5938 v -232.91016 l -210.9375,-406.93359 z m 722.8794,411.76758 H 2432.8618 V -330.9082 h 163.0371 q 37.793,0 61.5235,-12.30469 23.7304,-12.74414 34.7168,-35.15625 10.9863,-22.41211 10.9863,-50.53711 0,-28.56445 -10.9863,-53.17383 -10.9864,-24.60937 -34.7168,-39.55078 -23.7305,-14.94141 -61.5235,-14.94141 h -117.334 V 0 H 2346.729 v -639.84375 h 249.1699 q 75.1465,0 128.7598,27.24609 54.0527,26.80664 82.6172,74.26758 28.5644,47.46094 28.5644,108.54492 0,61.96289 -28.5644,107.22657 -28.5645,45.26367 -82.6172,69.87304 -53.6133,24.60938 -128.7598,24.60938 z m 760.739,-151.17188 v 102.83203 h -333.9843 v -102.83203 z m -294.873,-260.5957 V 0 H 2929.929 v -639.84375 z m 388.916,0 V 0 h -131.3965 v -639.84375 z m 543.0938,537.01172 V 0 H 3653.1985 V -102.83203 Z M 3696.2649,-639.84375 V 0 H 3564.429 v -639.84375 z m 253.125,260.5957 v 100.19532 h -296.1914 v -100.19532 z m 43.9453,-260.5957 v 103.27148 h -340.1367 v -103.27148 z m 75.9937,0 h 238.623 q 73.3887,0 126.1231,21.97266 53.1738,21.97265 81.7382,65.03906 28.5645,43.06641 28.5645,105.9082 0,51.41602 -17.5781,88.33008 -17.1387,36.47461 -48.7793,61.08398 -31.2012,24.16993 -73.3887,38.67188 l -41.7481,21.97266 h -207.4218 l -0.8789,-102.83204 h 154.248 q 34.7168,0 57.5684,-12.30468 22.8515,-12.30469 34.2773,-34.27735 11.8652,-21.97265 11.8652,-50.97656 0,-30.76172 -11.4257,-53.17383 -11.4258,-22.41211 -34.7168,-34.27734 -23.291,-11.86524 -58.4473,-11.86524 H 4201.1648 V 0 H 4069.3289 Z M 4427.0437,0 l -145.8984,-285.20508 139.3066,-0.8789 147.6563,279.9316363 V 0 Z"


# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------
def svg_metadata(title: str) -> str:
    return f"""  <title>{title}</title>
  <metadata>
    <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
             xmlns:dc="http://purl.org/dc/elements/1.1/">
      <rdf:Description>
        <dc:creator>Encypher Corporation</dc:creator>
        <dc:source>https://encypher.com</dc:source>
        <dc:rights>Copyright Encypher Corporation. All rights reserved.</dc:rights>
      </rdf:Description>
    </rdf:RDF>
  </metadata>"""


def png_metadata() -> PngImagePlugin.PngInfo:
    info = PngImagePlugin.PngInfo()
    info.add_text("Author", "Encypher Corporation")
    info.add_text("Copyright", "Copyright Encypher Corporation. All rights reserved.")
    info.add_text("Comment", "https://encypher.com")
    return info


# ---------------------------------------------------------------------------
# SVG Generators
# ---------------------------------------------------------------------------
def mark_paths_xml(fill: str, fill_opacity: str = "1") -> str:
    lines = []
    for p in PATHS:
        opacity_attr = f' fill-opacity="{fill_opacity}"' if fill_opacity != "1" else ""
        lines.append(f'    <path fill="{fill}"{opacity_attr} fill-rule="nonzero"' f' transform="{p["transform"]}" d="{p["d"]}"/>')
    return "\n".join(lines)


def generate_mark_svg(fill: str, bg_color: str | None, title: str) -> str:
    bg_rect = ""
    group_open = f'  <g transform="{GROUP_TRANSFORM}">'
    group_close = "  </g>"
    if bg_color:
        bg_rect = f'  <rect x="0.5" y="0.5" width="23" height="23" rx="3" fill="{bg_color}"/>\n'
        group_open = f'  <g transform="{GROUP_TRANSFORM_BG}">\n    <g transform="{GROUP_TRANSFORM}">'
        group_close = "    </g>\n  </g>"

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" role="img" aria-label="Encypher mark">
{svg_metadata(title)}
{bg_rect}{group_open}
{mark_paths_xml(fill)}
{group_close}
</svg>"""


def generate_loader_svg(fill: str, title: str) -> str:
    outer = PATHS[0]
    inner_paths = "\n".join(f'    <path fill="{fill}" fill-rule="nonzero"' f' transform="{p["transform"]}" d="{p["d"]}"/>' for p in PATHS[1:])
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" role="img" aria-label="Encypher loading">
{svg_metadata(title)}
  <style>
    @keyframes encypher-spin {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}
    .encypher-ring {{ animation: encypher-spin 2.5s linear infinite; transform-origin: -0.7657px 3.3383px; }}
  </style>
  <g transform="{GROUP_TRANSFORM}">
    <g class="encypher-ring">
      <path fill="{fill}" fill-opacity="0.35" fill-rule="nonzero" transform="{outer['transform']}" d="{outer['d']}"/>
    </g>
{inner_paths}
  </g>
</svg>"""


def generate_favicon_svg() -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" role="img" aria-label="Encypher">
{svg_metadata("Encypher")}
  <style>
    .mark {{ fill: {NAVY}; }}
    @media (prefers-color-scheme: dark) {{ .mark {{ fill: {WHITE}; }} }}
  </style>
  <g transform="{GROUP_TRANSFORM}">
    <path class="mark" fill-rule="nonzero" transform="{PATHS[0]['transform']}" d="{PATHS[0]['d']}"/>
    <path class="mark" fill-rule="nonzero" transform="{PATHS[1]['transform']}" d="{PATHS[1]['d']}"/>
    <path class="mark" fill-rule="nonzero" transform="{PATHS[2]['transform']}" d="{PATHS[2]['d']}"/>
    <path class="mark" fill-rule="nonzero" transform="{PATHS[3]['transform']}" d="{PATHS[3]['d']}"/>
  </g>
</svg>"""


# ---------------------------------------------------------------------------
# Wordmark SVG Generator
# ---------------------------------------------------------------------------
# The wordmark uses the corrected 24x24 mark icon on the left, and the
# pathed-out Roboto Bold "ENCYPHER" text on the right.
# Measured content bounds: x 0.23..133.77, y 0.41..23.59
# Tight viewBox: 0 0 134 24 (~0.23 symmetric padding)

WORDMARK_VB_WIDTH = 134


def _wordmark_text_transform() -> str:
    """Compute the matrix transform for the ENCYPHER text path."""
    sf = WORDMARK_VB_WIDTH / 7676.1865
    m_sx = 1.3333333 * sf
    m_sy = 1.3333333 * sf
    m_tx = 1459.4596 * sf
    m_ty = 1110.8593 * sf
    return f"matrix({m_sx:.8f},0,0,{m_sy:.8f},{m_tx:.6f},{m_ty:.6f})"


def generate_wordmark_svg(fill: str, bg_color: str | None, title: str) -> str:
    text_transform = _wordmark_text_transform()
    bg_rect = ""
    content_open = ""
    content_close = ""
    if bg_color:
        bg_rect = f'  <rect x="0" y="0" width="{WORDMARK_VB_WIDTH}" height="24" rx="3" fill="{bg_color}"/>\n'
        # Scale content to 90% centered inside the bg rect
        pad_x = WORDMARK_VB_WIDTH * 0.05
        content_open = f'  <g transform="translate({pad_x:.2f},1.2) scale(0.9)">\n'
        content_close = "  </g>\n"

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WORDMARK_VB_WIDTH} 24" width="{WORDMARK_VB_WIDTH}" height="24" role="img" aria-label="Encypher">
{svg_metadata(title)}
{bg_rect}{content_open}  <!-- Mark icon -->
  <g transform="{GROUP_TRANSFORM}">
{mark_paths_xml(fill)}
  </g>
  <!-- ENCYPHER wordmark (Roboto Bold, pathed out) -->
  <path fill="{fill}" transform="{text_transform}"
    aria-label="ENCYPHER"
    d="{WORDMARK_PATH_D}"/>
{content_close}</svg>"""


# ---------------------------------------------------------------------------
# PNG + ICO Generation
# ---------------------------------------------------------------------------
PNG_SIZES = [16, 32, 48, 64, 128, 256, 512]


def svg_to_png(svg_content: str, output_path: Path, size: int) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    png_data = cairosvg.svg2png(
        bytestring=svg_content.encode("utf-8"),
        output_width=size,
        output_height=size,
    )
    # Re-save with metadata
    import io

    img = Image.open(io.BytesIO(png_data))
    img.save(str(output_path), pnginfo=png_metadata())


def generate_ico(png_paths: dict[int, Path], output_path: Path) -> None:
    """Generate a multi-size ICO from PNG files."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sizes_needed = [16, 32, 48]
    # Load the largest PNG and let Pillow resize internally
    largest = max(s for s in sizes_needed if s in png_paths)
    img = Image.open(str(png_paths[largest])).copy()
    img.save(
        str(output_path),
        format="ICO",
        sizes=[(s, s) for s in sizes_needed if s in png_paths],
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    print("Encypher Icon Library - Asset Generator")
    print("=" * 50)

    # Ensure output dirs exist
    SVG_OUT.mkdir(parents=True, exist_ok=True)
    ICO_OUT.mkdir(parents=True, exist_ok=True)

    generated: list[str] = []

    # --- SVG Mark Variants ---
    mark_variants = [
        ("mark-navy-nobg.svg", NAVY, None, "Encypher mark"),
        ("mark-navy-bg.svg", NAVY, WHITE, "Encypher mark with background"),
        ("mark-white-nobg.svg", WHITE, None, "Encypher mark"),
        ("mark-white-bg.svg", WHITE, NAVY, "Encypher mark with background"),
    ]
    svg_contents: dict[str, str] = {}

    for filename, fill, bg, title in mark_variants:
        svg = generate_mark_svg(fill, bg, title)
        out_path = SVG_OUT / filename
        out_path.write_text(svg, encoding="utf-8")
        svg_contents[filename] = svg
        generated.append(f"svg/generated/{filename}")
        print(f"  [SVG] {filename}")

    # --- SVG Loader Variants ---
    loader_variants = [
        ("loader-navy.svg", NAVY, "Encypher loading indicator"),
        ("loader-white.svg", WHITE, "Encypher loading indicator"),
    ]
    for filename, fill, title in loader_variants:
        svg = generate_loader_svg(fill, title)
        out_path = SVG_OUT / filename
        out_path.write_text(svg, encoding="utf-8")
        generated.append(f"svg/generated/{filename}")
        print(f"  [SVG] {filename}")

    # --- SVG Favicon ---
    favicon_svg = generate_favicon_svg()
    (SVG_OUT / "favicon.svg").write_text(favicon_svg, encoding="utf-8")
    generated.append("svg/generated/favicon.svg")
    print("  [SVG] favicon.svg")

    # --- SVG Wordmark Variants ---
    wordmark_variants = [
        ("wordmark-navy-nobg.svg", NAVY, None, "Encypher"),
        ("wordmark-navy-bg.svg", NAVY, WHITE, "Encypher"),
        ("wordmark-white-nobg.svg", WHITE, None, "Encypher"),
        ("wordmark-white-bg.svg", WHITE, NAVY, "Encypher"),
    ]
    for filename, fill, bg, title in wordmark_variants:
        svg = generate_wordmark_svg(fill, bg, title)
        out_path = SVG_OUT / filename
        out_path.write_text(svg, encoding="utf-8")
        generated.append(f"svg/generated/{filename}")
        print(f"  [SVG] {filename}")

    # --- PNG Generation ---
    print()
    png_registry: dict[str, dict[int, Path]] = {}

    for svg_name, svg_content in svg_contents.items():
        png_base = svg_name.replace(".svg", "")
        png_registry[png_base] = {}
        for size in PNG_SIZES:
            out_dir = PNG_OUT / str(size)
            out_path = out_dir / f"{png_base}.png"
            svg_to_png(svg_content, out_path, size)
            png_registry[png_base][size] = out_path
            generated.append(f"png/generated/{size}/{png_base}.png")
        print(f"  [PNG] {png_base} x {len(PNG_SIZES)} sizes")

    # --- ICO Generation ---
    print()
    navy_nobg_pngs = png_registry.get("mark-navy-nobg", {})
    if navy_nobg_pngs:
        ico_path = ICO_OUT / "favicon.ico"
        generate_ico(navy_nobg_pngs, ico_path)
        generated.append("ico/generated/favicon.ico")
        print("  [ICO] favicon.ico (16+32+48)")

    # --- Summary ---
    print()
    print(f"Generated {len(generated)} files:")
    svg_count = sum(1 for f in generated if f.endswith(".svg"))
    png_count = sum(1 for f in generated if f.endswith(".png"))
    ico_count = sum(1 for f in generated if f.endswith(".ico"))
    print(f"  {svg_count} SVG, {png_count} PNG, {ico_count} ICO")
    print("Done.")


if __name__ == "__main__":
    main()
