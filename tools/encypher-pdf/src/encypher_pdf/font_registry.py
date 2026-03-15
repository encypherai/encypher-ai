from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FontVariant:
    regular: tuple[str, ...]
    bold: tuple[str, ...] = ()
    italic: tuple[str, ...] = ()
    bold_italic: tuple[str, ...] = ()
    license_label: str = "system"
    bundled: bool = False
    support_tier: str = "supported"


@dataclass(frozen=True)
class ResolvedFont:
    family: str
    path: str
    bold: bool
    italic: bool
    source: str
    support_tier: str


class FontResolutionError(FileNotFoundError):
    pass


_FONT_FAMILIES: dict[str, FontVariant] = {
    "roboto": FontVariant(
        regular=(
            "/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Regular.ttf",
            "/usr/share/fonts/truetype/roboto/Roboto-Regular.ttf",
            "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ),
        bold=(
            "/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Bold.ttf",
            "/usr/share/fonts/truetype/roboto/Roboto-Bold.ttf",
            "/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ),
        italic=(
            "/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Italic.ttf",
            "/usr/share/fonts/truetype/roboto/Roboto-Italic.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Italic.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
        ),
        bold_italic=(
            "/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-BoldItalic.ttf",
            "/usr/share/fonts/truetype/roboto/Roboto-BoldItalic.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-BoldItalic.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf",
        ),
    ),
    "arial": FontVariant(
        regular=(
            "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ),
        bold=(
            "/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ),
        italic=(
            "/usr/share/fonts/truetype/msttcorefonts/Arial_Italic.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Italic.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
        ),
        bold_italic=(
            "/usr/share/fonts/truetype/msttcorefonts/Arial_Bold_Italic.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-BoldItalic.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf",
        ),
    ),
    "liberation_sans": FontVariant(
        regular=(
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ),
        bold=(
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ),
        italic=(
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Italic.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf",
        ),
        bold_italic=(
            "/usr/share/fonts/truetype/liberation2/LiberationSans-BoldItalic.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf",
        ),
    ),
    "dejavu_sans": FontVariant(
        regular=("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",),
        bold=("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",),
        italic=("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",),
        bold_italic=("/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf",),
    ),
    "times": FontVariant(
        regular=(
            "/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        ),
        bold=(
            "/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman_Bold.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSerif-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        ),
        italic=(
            "/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman_Italic.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSerif-Italic.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",
        ),
        bold_italic=(
            "/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman_Bold_Italic.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSerif-BoldItalic.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-BoldItalic.ttf",
        ),
    ),
    "liberation_serif": FontVariant(
        regular=(
            "/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
        ),
        bold=(
            "/usr/share/fonts/truetype/liberation2/LiberationSerif-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        ),
        italic=(
            "/usr/share/fonts/truetype/liberation2/LiberationSerif-Italic.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
        ),
        bold_italic=(
            "/usr/share/fonts/truetype/liberation2/LiberationSerif-BoldItalic.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf",
        ),
    ),
    "dejavu_serif": FontVariant(
        regular=("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",),
        bold=("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",),
        italic=("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",),
        bold_italic=("/usr/share/fonts/truetype/dejavu/DejaVuSerif-BoldItalic.ttf",),
    ),
}

_ALIAS_MAP = {
    "sans": "roboto",
    "sans-serif": "roboto",
    "serif": "times",
    "times_new_roman": "times",
    "times-roman": "times",
    "times new roman": "times",
    "arial": "arial",
    "roboto": "roboto",
    "liberation sans": "liberation_sans",
    "liberation serif": "liberation_serif",
    "dejavu sans": "dejavu_sans",
    "dejavu serif": "dejavu_serif",
}


def _normalize_family_name(family: str | None) -> str:
    if not family:
        return "roboto"
    key = family.strip().lower().replace("-", "_").replace(" ", "_")
    return _ALIAS_MAP.get(key, key)


def _existing_path(candidates: tuple[str, ...]) -> str | None:
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def list_supported_font_families() -> list[str]:
    return sorted(_FONT_FAMILIES.keys())


def resolve_font_path(
    family: str | None = None,
    *,
    bold: bool = False,
    italic: bool = False,
    font_path: str | None = None,
) -> ResolvedFont:
    if font_path:
        candidate = Path(font_path)
        if not candidate.exists():
            raise FontResolutionError(f"Font path not found: {font_path}")
        family_name = family or candidate.stem
        return ResolvedFont(
            family=family_name,
            path=str(candidate),
            bold=bold,
            italic=italic,
            source="explicit_path",
            support_tier="custom",
        )

    family_key = _normalize_family_name(family)
    variant = _FONT_FAMILIES.get(family_key)
    if variant is None:
        raise FontResolutionError(f"Unsupported font family '{family}'. Supported families: {', '.join(list_supported_font_families())}")

    if bold and italic:
        candidates = variant.bold_italic or variant.bold or variant.italic or variant.regular
    elif bold:
        candidates = variant.bold or variant.regular
    elif italic:
        candidates = variant.italic or variant.regular
    else:
        candidates = variant.regular

    path = _existing_path(candidates)
    if path is None:
        fallback_candidates = tuple(
            p
            for fallback in ("roboto", "arial", "liberation_sans", "dejavu_sans", "times", "liberation_serif", "dejavu_serif")
            for p in _FONT_FAMILIES[fallback].regular
        )
        path = _existing_path(fallback_candidates)
        if path is None:
            raise FontResolutionError("No supported font files found on this system. Install Liberation, DejaVu, Roboto, or Arial-compatible fonts.")
        return ResolvedFont(
            family=family_key,
            path=path,
            bold=bold,
            italic=italic,
            source="fallback",
            support_tier=variant.support_tier,
        )

    return ResolvedFont(
        family=family_key,
        path=path,
        bold=bold,
        italic=italic,
        source="family_registry",
        support_tier=variant.support_tier,
    )
