# TEAM_267 -- The Encypher Times Demo Site

## Status: Complete

## Summary
Building "The Encypher Times" -- a fully functional demo news publisher website at `apps/encypher-times/` that showcases Encypher's content provenance technology across all content types (text, images, audio, video).

## What Was Built
- New Next.js 15 app at `apps/encypher-times/` (port 3060)
- Static export ready (`output: 'export'`) -- 19 pages generated
- AP-inspired newspaper layout with UnifrakturCook blackletter masthead
- 8 fictional articles on content provenance topics across 5 sections
- 8 hero images (Unsplash CC0, signed via /api/v1/sign/rich)
- 1 audio file (30s podcast briefing, signed via /enterprise/audio/sign)
- 1 video file (15s C2PA demo, signed via /enterprise/video/sign)
- Placeholder content system that works pre-signing (development mode)
- Python seed script (`seed/seed.py`) for signing all content via enterprise API
- Copy-paste verification widget calling local gateway API
- C2PA SIGNED badges on all media components (images, audio, video)
- Content integrity info box on every article page (Document ID, Merkle Root)
- Section pages, verify page, about page

## Architecture
- Tech: Next.js 15, React 19, TypeScript 5, Tailwind CSS v4
- Data: Pre-signed content stored as `public/signed-content/manifest.json`
- Media: Signed images/audio/video in `public/signed-media/`
- Fallback: `src/lib/content.ts` provides placeholder articles for development
- Signing: `seed/seed.py` calls enterprise API endpoints (text, rich, audio, video)
- Verification: Client-side widget calls `POST /api/v1/verify` (default: localhost:8000)
- Chrome extension auto-detects ZWC markers in DOM text

## Key Files
- `apps/encypher-times/src/app/layout.tsx` -- root layout with newspaper typography
- `apps/encypher-times/src/app/page.tsx` -- homepage with lead story + section grid
- `apps/encypher-times/src/app/article/[slug]/page.tsx` -- article pages
- `apps/encypher-times/src/lib/content.ts` -- content data layer with 8 placeholder articles
- `apps/encypher-times/src/lib/api.ts` -- verify API client (NEXT_PUBLIC_API_BASE_URL)
- `apps/encypher-times/src/components/ui/VerifyWidget.tsx` -- copy-paste verification
- `apps/encypher-times/seed/seed.py` -- signing pipeline (text + images + audio + video)
- `apps/encypher-times/seed/content/images/` -- 8 hero images (Unsplash CC0)
- `apps/encypher-times/seed/content/audio/` -- podcast briefing MP3
- `apps/encypher-times/seed/content/video/` -- C2PA demo MP4

## Completed Work (Session 2)
- Signed all 8 articles via local enterprise API using demo API key
- Generated `public/signed-content/manifest.json` (2MB, VS256 markers in all articles)
- Fixed `content.ts` to use `fs.readFileSync()` (was hanging with `require()`)
- Fixed CORS: added `http://localhost:3060` to Traefik `routes-local.yml` allow list
- Created `.env.local` with `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000`
- End-to-end verification confirmed: article text -> verify widget -> API -> "Content Verified"
- Puppeteer visual verification of all page types (homepage, articles, sections, verify, about)
- 19 static pages build with zero errors

## Completed Work (Session 3)
- Downloaded 8 hero images from Lorem Picsum (Unsplash CC0, 1200x675 each)
- Generated audio file (30s 440Hz tone with fade, ffmpeg) and video file (15s navy+text, ffmpeg)
- Updated seed script to wire media metadata to articles and sign inline
- All 8 images signed via `/api/v1/sign/rich` with C2PA manifests
- Audio signed via `/api/v1/enterprise/audio/sign`
- Video signed via `/api/v1/enterprise/video/sign` (multipart)
- Updated VerifyWidget API URL default to `http://localhost:8000`
- Rebuilt with static export (`output: "export"`) -- 19 pages + all media in `out/`
- Verified end-to-end: copy paragraph -> paste into verify widget -> "Content Verified"

## Verification Results
- API verification: `valid: true`, `tampered: false`, `signer: Encypher Demo / Free Tier`
- VerifyWidget UI: green "Content Verified" box with signer info displayed correctly
- All 8 articles contain VS256 sentence-level markers in the DOM
- Homepage: hero image with caption/credit, lead story layout, section strips with image cards
- Article pages: hero image with C2PA SIGNED badge, signed body text, Content Integrity box
- c2pa-video-audio article: audio player (0:30) + video player (0:15) both with C2PA badges
- Section pages: full-width hero images, article grids
- Mobile responsive: all layouts adapt correctly at 390px width
- Verify page, about page, footer all render correctly

## Remaining / Future Work
- Deploy to staging (S3/CDN) -- static export in `out/` is deployment-ready
- Test Chrome extension verification on signed content
- Production API URL: set NEXT_PUBLIC_API_BASE_URL env var for deployed environment
- Replace generated audio/video with real open-source media content
- `output: "export"` is currently commented out for local `next start` -- re-enable for deploy

## Files Modified Outside encypher-times
- `infrastructure/traefik/routes-local.yml` -- added `http://localhost:3060` to CORS origins

## Commit Message Suggestion
```
feat(encypher-times): demo publisher site with signed content, media, and verification

Add "The Encypher Times" -- a static Next.js demo site showcasing what a
news publisher looks like with all content signed by Encypher. 8 articles
on content provenance with hero images, audio player, and video player --
all signed via enterprise API with C2PA manifests. AP-inspired newspaper
layout with UnifrakturCook masthead. Python seed script signs text (VS256
sentence-level markers), images (/sign/rich), audio (/enterprise/audio),
and video (/enterprise/video). Live copy-paste verification widget
confirms end-to-end provenance flow.
```
