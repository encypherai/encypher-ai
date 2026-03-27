# TEAM_283 -- Icon Library Package

**Status**: Complete
**Date**: 2026-03-27

## Summary

Built the `@encypher/icons` package from scratch -- a centralized icon library replacing 6+ duplicated favicon.ico files, inconsistent SVG naming, and broken loader animations across the monorepo.

## What Was Done

1. **Package scaffold** (`packages/icons/`): package.json, tsconfig.json, directory structure
2. **Source modules**: `colors.ts` (SSOT brand colors), `paths.ts` (4 SVG path d-strings with corrected uniform scale), `types.ts` (TS interfaces)
3. **React components**: `EncypherMark.tsx` (parametric, 5 color options, background toggle), `EncypherLoader.tsx` (spinning outer ring at 35% opacity, corrected centering)
4. **Build script** (`scripts/build-icons.py`): Generates 38 assets via cairosvg + Pillow
   - 4 mark SVGs (navy/white x bg/nobg)
   - 2 loader SVGs (navy/white, animated)
   - 2 wordmark SVGs (navy/white, pathed-out Roboto Bold)
   - 1 adaptive favicon SVG (prefers-color-scheme)
   - 28 PNGs (4 variants x 7 sizes: 16-512px)
   - 1 multi-size ICO (16+32+48)
5. **Puppeteer verification**: All variants render correctly, loaders animate, wordmarks display pathed text
6. **Migration PRD**: `PRDs/CURRENT/PRD_Icon_Library_Migration.md` -- incremental per-app migration with Puppeteer before/after verification

## Key Technical Decisions

- **Uniform scale correction**: Fixed 1.43% Y-stretch from Illustrator export (0.26489337 vs 0.26868826 -> uniform 0.02354608)
- **24x24 viewBox**: Standard grid, centered via `translate(12.7657, 8.6617)`
- **Loader fix**: `transform-origin: 12px 12px` (true center) replacing broken `753px 682px`
- **Wordmark font independence**: Roboto Bold extracted as vector `<path d>` -- no font dependency
- **Navy + White only for static files**: Azure/teal available via React component `color` prop only

## Files Created

```
packages/icons/
  package.json, tsconfig.json, preview.html
  scripts/build-icons.py
  src/index.ts, colors.ts, paths.ts, types.ts
  src/components/EncypherMark.tsx, EncypherLoader.tsx
  svg/source/encypher-mark.svg
  svg/generated/ (9 SVGs)
  png/generated/ (28 PNGs in 7 size dirs)
  ico/generated/favicon.ico
```

## Suggested Commit Message

```
feat(icons): add @encypher/icons package with centralized brand assets

Build packages/icons/ with React components (EncypherMark, EncypherLoader),
Python build script generating 38 assets (9 SVG, 28 PNG, 1 ICO), and
corrected 24x24 viewBox with uniform scale fixing 1.43% Y-stretch.

Includes wordmark SVGs with pathed-out Roboto Bold (no font dependency),
adaptive favicon SVG (prefers-color-scheme), and multi-size ICO (16+32+48).
Loader animation uses corrected transform-origin: 12px 12px (true center).

Follow-up PRD written for incremental per-app migration with Puppeteer
verification: PRDs/CURRENT/PRD_Icon_Library_Migration.md
```

## Session 2 Fixes (context continuation)

- Fixed bg variant transform nesting in `build-icons.py`: `GROUP_TRANSFORM_BG` wrapper now correctly wraps *outside* `GROUP_TRANSFORM` (was incorrectly nested inside)
- Fixed TypeScript indexing errors: added `as keyof typeof` casts for color/size map lookups in both React components
- Ran `tsc --noEmit` -- zero errors
- Re-ran build script -- 38 files generated successfully
- Puppeteer verified all variants render correctly (light + dark sections)
- ICO generation updated (linter fix): explicit `.copy()` + `.resize()` for Pillow ICO save

## Next Steps

Execute `PRD_Icon_Library_Migration.md` -- migrate each app incrementally with Puppeteer before/after screenshots to verify zero visual regressions.
