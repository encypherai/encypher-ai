---
description: Generate brand-compliant images using Gemini 3 Pro Image API. Supports blog headers, LinkedIn posts, and more. Accepts a user image description and optional preset type.
---

## Prerequisites
- `.env.skills` exists at repo root with `GEMINI_API_KEY=your-key-here`
- Node.js 20.6+ (`node --version` — currently v22 ✓)
- Get a key at https://aistudio.google.com/apikey

---

## How to invoke this skill

Tell Cascade:
> "Generate a [PRESET] image for [blog post file / description]. The image should show [YOUR IMAGE DESCRIPTION]."

**Arguments:**
- **PRESET** — one of: `blog-header`, `linkedin`, `twitter`, `presentation`, `diagram` (default: `blog-header`)
- **Blog post file** (optional) — path to `.md` file; Cascade reads `title` and `excerpt` automatically
- **YOUR IMAGE DESCRIPTION** — free-form description of the visual scene/concept to generate

If no image description is provided, Cascade will derive one from the blog post `title` and `excerpt` using the visual metaphor guide below.

---

## Steps

1. **Determine inputs.** Collect:
   - `PRESET` (default: `blog-header`)
   - `TITLE` — from blog post frontmatter, or user-supplied
   - `SUBTITLE` — from blog post `excerpt` (truncate to ~12 words if longer), or user-supplied
   - `IMAGE_DESCRIPTION` — user-supplied, or derived from title/excerpt using the Visual Metaphor Guide below
   - `OUTPUT_PATH` — from blog post frontmatter `image` field mapped to `apps/marketing-site/public/` + path, always `.png`; or user-specified path

2. **Look up the preset** from the Presets section below to get `ASPECT_RATIO`, `IMAGE_SIZE`, and `LAYOUT_INSTRUCTIONS`.

3. **Create the output directory** if it does not exist:
```powershell
New-Item -ItemType Directory -Force -Path "<parent-folder-of-OUTPUT_PATH>"
```

4. **Write the generation script** to `generate-image-temp.mjs` in the repo root. Substitute all values — do not leave any placeholder text:

```javascript
import https from 'https';
import fs from 'fs';

const apiKey = process.env.GEMINI_API_KEY;
if (!apiKey) { console.error('ERROR: GEMINI_API_KEY not set in .env.skills'); process.exit(1); }

const outputPath = 'OUTPUT_PATH';

const systemPrompt = `You are an expert technical illustrator for Encypher, a deep-tech infrastructure company. You create high-fidelity, institutional-grade visuals for a B2B audience of publisher General Counsels, CLOs, and C-suite executives. Your images look like they belong in a high-end security whitepaper or Bloomberg Terminal interface.

MANDATORY STYLE: Protocol Modernism. Flat, isometric, or 2D technical schematic. All imagery is clearly readable at a glance.
VIBE: "Verified Reality." Clean, precise, data-dense but not cluttered. Architectural Blueprint meets Cybersecurity Dashboard.
FINISH: Matte, non-reflective surfaces. No glossy glassmorphism. No 3D cartoonish rendering.
LIGHTING: Soft, diffuse, studio lighting. No dramatic cinematic shadows.
COMPOSITION: Structured, grid-based. Thin precise lines (1-2px) for connections.

MANDATORY COLOR PALETTE — dark mode first, strict adherence:
- Background: Deep Navy #1B2F50 — every image uses this
- Primary Elements: Azure Blue #2A87C4 — main nodes, active connections, key UI elements
- Secondary Elements: Light Sky Blue #B7D5ED — background graphs, grids, passive containers
- The Signal: Cyber Teal #00CED1 — MAX 5% of composition — verified/confirmed states only
- Text/Lines: Neutral Gray #A7AFBC — connecting lines, secondary labels
- Title Text: Pure White #FFFFFF — all title/header text in the image
- Subtitle Text: Light Sky Blue #B7D5ED — all subtitle/subheader text in the image
- Error State: Muted Coral #E07A5F — ONLY for failed/unverified states, max 10%
- Warning: Amber #F2CC8F — ONLY for pending/uncertain states, max 5%

FORBIDDEN: pure black #000000, bright red #FF0000, neon gradients, matrix green, gold/bronze/warm metallics, neon purple, any unlisted color.

TYPOGRAPHY RULES — critical, follow exactly:
- Title font: Roboto Bold or equivalent geometric sans-serif. Pure White (#FFFFFF). Large, dominant, highly legible. Minimum effective size for someone with impaired vision.
- Subtitle font: Roboto Regular or equivalent. Light Sky Blue (#B7D5ED). Clearly readable, positioned directly below the title.
- Technical labels: Roboto Mono. Neutral Gray or Light Sky Blue. Used for hash strings, timestamps, document IDs, status labels.
- Realistic technical data examples: hash 0x4A1F6E8D2C9B5A7F, timestamp 2026-02-05 14:30:00 UTC, doc ID DOC-5548-AF9B, status CRYPTOGRAPHIC SIGNATURE: VALID.
- ALL text must be large enough to read comfortably without squinting. Err on the side of larger text.

HUMAN FIGURES: Avoid entirely. Use abstract nodes, icons, interface panels. Stylized silhouettes only if absolutely necessary — no faces, no realistic proportions.

NO LOGOS: Do not attempt to render any company logos, wordmarks, or brand symbols. No Encypher logo. No C2PA logo. No third-party logos.

ENCYPHER MARK (for verified/confirmed states only): When a verification badge or certified checkmark is needed, render a circular badge with an organic/wavy outer border ring (not a perfect circle — the border has subtle irregular curves at regular intervals around the circumference), a smooth inner concentric circle ring, and a bold wide checkmark inside. The outer border is the most distinctive element — it reads as a circle but with a slightly irregular, hand-drawn quality to the edge. Fill in Cyber Teal (#00CED1). Use sparingly — max 5% of composition.

The exact SVG paths for this mark are in `apps/marketing-site/public/encypher-mark-teal.svg` (and white/azure/navy variants). The four paths that make up the mark, expressed in the SVG coordinate space (viewBox="0 0 264.58 264.58", group transform="translate(141.02291,94.720831)"):

PATH 1 — Outer wavy circle (fill, transform matrix(0.26489337,0,0,-0.26868826,102.67706,37.461479)):
"m 0,0 c 0,232.574 -188.539,421.113 -421.113,421.113 -232.574,0 -421.113,-188.539 -421.113,-421.113 0,-232.574 188.539,-421.113 421.113,-421.113 C -188.539,-421.113 0,-232.574 0,0 m -67.453,353 c 23.979,-23.981 10.797,-65.451 27.768,-92.817 18.974,-30.597 65.954,-33.172 79.076,-65.368 C 53.507,160.182 17.509,121.532 36.361,78.293 46.971,53.959 71.864,40.212 78.136,13.025 88.284,-30.962 46.909,-46.485 34.258,-81.182 c -15.204,-41.698 18.268,-74.005 5.128,-109.592 -10.999,-29.792 -41.748,-34.508 -64.249,-51.817 -35.197,-27.075 -17.661,-69.425 -38.048,-103.822 -23.241,-39.214 -88.417,-7.654 -119.92,-50.318 -15.57,-21.086 -19.66,-51.992 -47.602,-62.02 -37.141,-13.33 -73.918,26.168 -115.134,8.091 -25.387,-11.134 -41.467,-42.977 -71.635,-41.973 -40.694,1.354 -55.371,38.519 -90.549,46.161 -35.155,7.637 -70.921,-23.265 -105.134,-10.989 -29.976,10.755 -32.05,49.686 -54.486,68.033 -46.355,37.908 -104.624,-4.252 -121.466,74.566 -4.219,19.744 -3.26,41.357 -14.786,58.725 -18.598,28.025 -60.437,30.204 -75.202,61.504 -17.044,36.132 21.018,75.308 2.157,118.229 -9.922,22.582 -34.649,37.243 -40.879,61.005 -14.493,55.272 39.927,66.145 45.429,111.924 3.779,31.436 -14.077,58.522 -11.085,85.886 3.876,35.449 42.672,41.122 65.628,60.762 35.771,30.604 19.345,55.434 33.486,91.613 19.578,50.093 74.036,25.042 109.571,50.348 25.488,18.151 33.168,62.191 60.342,73.785 35.996,15.359 70.975,-19.554 106.446,-12.299 28.968,5.924 48.503,41.024 76.508,44.721 48.251,6.372 61.706,-38.856 102.102,-45.992 33.437,-5.906 59.88,20.108 92.391,16.301 38.545,-4.512 40.264,-55.377 66.904,-74.961 30.814,-22.653 78.673,-9.989 102.372,-33.689"

PATH 2 — Inner circle ring (fill, transform matrix(0.26489337,0,0,-0.26868826,-17.287041,-63.64331)):
"m 0,0 c -83.528,-5.076 -162.357,-38.8 -224.157,-94.394 -158.015,-142.145 -166.457,-385.295 -21.94,-540.428 165.409,-177.56 446.282,-154.97 588.662,38.19 84.213,114.248 95.688,274.838 27.221,399.718 C 297.105,-64.347 150.152,9.124 0,0 M 5.205,23.285 C 143.817,30.151 272.03,-27.605 356.728,-136.46 456.427,-264.595 466.08,-451.411 376.376,-587.884 263.962,-758.908 71.908,-818.956 -121.656,-750.26 c -32.852,11.659 -77.116,41.147 -104.929,62.729 -96.585,74.95 -157.627,226.56 -144.421,347.923 6.569,60.365 23.33,122.486 56.048,173.515 71.625,111.712 185.876,182.726 320.163,189.378"

PATH 3 — Checkmark (fill, transform matrix(0.26489337,0,0,-0.26868826,26.73424,8.5562629)):
"m 0,0 c 29.751,29.632 61.152,66.947 92.627,93.729 8.727,7.426 13.408,10.728 25.56,6.146 16.328,-6.156 45.296,-50.829 60.057,-63.748 2.451,-4.138 2.004,-9.397 -0.391,-13.439 -87.041,-90.36 -177.441,-177.881 -267.071,-265.566 -20.595,-20.148 -44.143,-48.328 -65.711,-65.836 -10.684,-8.674 -16.474,-8.656 -27.14,0 l -193.453,193.451 c -5.327,5.857 -6.63,16.108 -1.906,22.6 21.521,18.741 40.871,44.559 62.52,62.579 10.895,9.068 18.62,9.015 29.722,-0.002 36.955,-34.62 71.913,-79.106 110.22,-111.604 3.871,-3.284 10.239,-8.849 15.195,-9.415 13.191,-1.507 37.453,29.815 46.694,39.13 C -75.711,-74.315 -37.573,-37.422 0,0"

PATH 4 — Inner arc accent (fill, transform matrix(0.26489337,0,0,-0.26868826,39.878672,-14.24062)):
"m 0,0 c -0.216,0.126 -1.012,2.659 -2.026,3.71 -54.348,56.357 -145.316,79.861 -221.695,68.13 -72.555,-11.143 -128.881,-46.55 -174.916,-102.365 -117.608,-142.594 -43.035,-367.034 132.52,-416.806 113.594,-32.204 209.023,-4.247 287.25,82.155 53.615,59.218 77.446,146.726 59.953,225.052 0.463,2.527 14.054,16.355 15.468,14.84 16.044,-65.162 5.842,-132.859 -21.313,-193.404 -36.108,-80.507 -143.607,-155.591 -232.049,-160.015 -159.635,-7.985 -288.716,89.134 -312.403,248.714 -17.045,114.837 39.58,227.12 138.491,285.019 91.096,53.324 197.675,49.923 288.862,-0.821 C -34.567,50.151 15.294,16.303 15.289,12.073 12.155,9.902 3.731,-2.182 0,0"

To embed the mark in a React/Next.js component, use `<Image src="/encypher-mark-teal.svg" />` or inline the SVG from the file above.

CRITICAL RULES — never violate:
1. Never render font names ("Roboto", "Roboto Mono", "Roboto Bold", or any font name) as visible text anywhere in the image. Font names are rendering instructions only.
2. Never render revenue percentages, split ratios, or revenue language ("60/40", "80/20", "majority", "you keep more", "revenue share") anywhere in the image.
3. Never render layout instruction text ("LAYOUT:", "TOP THIRD:", "BOTTOM TWO-THIRDS:", "1.9:1", "wide format") as visible text. These are composition instructions only.

NEGATIVE CONSTRAINTS: no stock photography, no photorealism, no human faces, no detailed cartoons, no 3D characters, no grunge textures, no bright red, no neon purple, no gold, no bronze, no warm metallics, no gradients, no lens flare, no glossy surfaces, no dramatic shadows, no pure black backgrounds, no logos of any kind, no font names as visible text, no revenue splits or percentages.`;

const articlePrompt = `LAYOUT_INSTRUCTIONS

TITLE TEXT TO RENDER IN THE IMAGE (Roboto Bold, Pure White #FFFFFF, large and dominant):
"TITLE"

SUBTITLE TEXT TO RENDER IN THE IMAGE (Roboto Regular, Light Sky Blue #B7D5ED, clearly readable, directly below title):
"SUBTITLE"

IMAGE SCENE (render below/behind the text, filling the composition):
IMAGE_DESCRIPTION`;

const fullPrompt = systemPrompt + '\n\n---\n\nGenerate this image now:\n\n' + articlePrompt;

const body = JSON.stringify({
  contents: [{ parts: [{ text: fullPrompt }] }],
  generationConfig: {
    responseModalities: ['IMAGE'],
    imageConfig: {
      aspectRatio: 'ASPECT_RATIO',
      image_size: 'IMAGE_SIZE'
    }
  }
});

const options = {
  hostname: 'generativelanguage.googleapis.com',
  path: '/v1beta/models/gemini-3-pro-image-preview:generateContent',
  method: 'POST',
  headers: {
    'x-goog-api-key': apiKey,
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(body)
  }
};

const req = https.request(options, (res) => {
  let data = '';
  res.on('data', chunk => data += chunk);
  res.on('end', () => {
    try {
      const json = JSON.parse(data);
      if (json.error) { console.error('API error:', JSON.stringify(json.error, null, 2)); process.exit(1); }
      const parts = json.candidates?.[0]?.content?.parts ?? [];
      const imgPart = parts.find(p => p.inlineData);
      if (!imgPart) { console.error('No image in response:\n', data); process.exit(1); }
      const buf = Buffer.from(imgPart.inlineData.data, 'base64');
      fs.writeFileSync(outputPath, buf);
      console.log('✓ Saved:', outputPath, `(${(buf.length / 1024).toFixed(0)} KB)`);
    } catch (e) {
      console.error('Parse error:', e.message, '\nRaw:', data.slice(0, 500));
      process.exit(1);
    }
  });
});
req.on('error', e => { console.error('Request error:', e.message); process.exit(1); });
req.write(body);
req.end();
```

5. **Run the script:**
```powershell
node --env-file=.env.skills generate-image-temp.mjs
```

6. **Verify:**
```powershell
Get-Item "OUTPUT_PATH" | Select-Object Name, Length
```

7. **Fix frontmatter** if the blog post `image` field extension doesn't match `.png` — update it.

8. **Clean up:**
```powershell
Remove-Item generate-image-temp.mjs
```

9. Show the generated image to the user and ask if they want any adjustments.

---

## Presets

### `blog-header` (default)
| Field | Value |
|-------|-------|
| `ASPECT_RATIO` | `16:9` |
| `IMAGE_SIZE` | `1K` |
| `LAYOUT_INSTRUCTIONS` | See below |

```
LAYOUT: Blog header image, 1.9:1 wide format. 
TOP THIRD: Title text (Roboto Bold, Pure White, very large — dominant element of the composition) with subtitle directly below it (Roboto Regular, Light Sky Blue, clearly readable). Both left-aligned or centered, with generous padding from edges (minimum 80px safe zone). 
BOTTOM TWO-THIRDS: The visual scene fills this area and bleeds behind the text area with enough contrast that white text remains legible. Use a subtle dark overlay or deep navy gradient behind the text area only if needed for legibility. No logos anywhere.
```

### `linkedin`
| Field | Value |
|-------|-------|
| `ASPECT_RATIO` | `16:9` |
| `IMAGE_SIZE` | `1K` |
| `LAYOUT_INSTRUCTIONS` | See below |

```
LAYOUT: LinkedIn post image, 1.91:1 format. Clean, professional, designed to stop the scroll.
CENTER or TOP-CENTER: Title text (Roboto Bold, Pure White, very large — must be readable as a thumbnail). Subtitle below (Roboto Regular, Light Sky Blue). Both centered with generous padding.
BACKGROUND: The visual scene fills the entire canvas behind the text. Ensure strong contrast so text is always legible. No logos anywhere.
```

### `twitter`
| Field | Value |
|-------|-------|
| `ASPECT_RATIO` | `16:9` |
| `IMAGE_SIZE` | `1K` |
| `LAYOUT_INSTRUCTIONS` | See below |

```
LAYOUT: Twitter/X post image, 16:9 format. Bold, high-contrast, readable at small sizes.
TOP or CENTER: Title text (Roboto Bold, Pure White, very large). Subtitle below (Roboto Regular, Light Sky Blue). Centered layout.
BACKGROUND: Full-bleed visual scene. Strong contrast behind text. No logos anywhere.
```

### `presentation`
| Field | Value |
|-------|-------|
| `ASPECT_RATIO` | `16:9` |
| `IMAGE_SIZE` | `2K` |
| `LAYOUT_INSTRUCTIONS` | See below |

```
LAYOUT: Presentation slide, 16:9, 2K resolution. More detail permitted than headers.
TOP: Title (Roboto Bold, Pure White, large). Subtitle below (Roboto Regular, Light Sky Blue).
BODY AREA: Detailed technical diagram, schematic, or data visualization filling the lower 70% of the slide. Include technical labels, data values, connection lines. Grid-aligned. No logos anywhere.
```

### `diagram`
| Field | Value |
|-------|-------|
| `ASPECT_RATIO` | `4:3` |
| `IMAGE_SIZE` | `1K` |
| `LAYOUT_INSTRUCTIONS` | See below |

```
LAYOUT: In-article explanatory diagram, 3:2 format. Optimized for clarity and detail.
TOP: Short title label (Roboto Bold, Pure White, medium size). No subtitle needed.
BODY: The diagram fills the entire canvas. Maximize technical detail, labels, data flow arrows, node labels. Every element must be clearly legible. No logos anywhere.
```

---

## Visual Metaphor Guide

Use this to derive `IMAGE_DESCRIPTION` from a blog post title/excerpt when the user hasn't specified one.

| Article Topic | Visual Metaphor | Key Elements |
|---------------|----------------|--------------|
| Watermarking / provenance | X-Ray effect — document with Cyber Teal cryptographic signature glowing beneath the surface | Document layers, hash strings, signature status |
| Verification / detection | Left→Center→Right flow — problem state → processing node → verified output | Panels, data flow arrows, checkmarks |
| Copyright / legal / RAG liability | Two-stage pipeline — document nodes with copyright symbols flowing into an INDEX cylinder (ingestion), then RETRIEVAL arrow pulling content into a response window (output). Muted Coral warning badges label each liability stage. Monospace labels: "COPY 1: INDEX INGESTION", "COPY 2: QUERY RESPONSE", "LICENSED: UNKNOWN" | Document stacks with (c) symbols, cylindrical database, terminal node, response window, coral warning badges |
| AI training / scraping | Data pipeline — content flowing through extraction nodes into a processing system | Pipeline stages, document blocks, ingestion nodes |
| Standards / C2PA / coalition | Network constellation — hexagonal nodes connected by precise Azure Blue lines | Orderly node network, institution labels, central hub |
| Regulation / compliance | Compliance pipeline — fragmented input → regulatory engine → verified compliant output | Regulatory grid, compliance status, enforcement timestamps |
| AI hallucination / quote integrity | Comparison panel — claimed quote (Muted Coral uncertainty) vs. verified source (Cyber Teal confirmed) | Side-by-side panels, source attribution, accuracy status |
| Infrastructure / how it works | Isometric stacked layers — foundation → processing → output | Layer diagram, data containers, connection lines |
| Year in review / editorial | Abstract data landscape — timeline with milestone nodes and data points | Timeline, milestone markers, trend lines |

---

## Proven Style: Simple Pipeline Diagrams

The clearest blog headers use a **2-3 stage left-to-right pipeline** as the scene:
- Each stage is a distinct labeled node (document stack, cylinder, terminal, window panel)
- **Muted Coral badges** name the problem at each stage (e.g., "INGESTION LIABILITY", "OUTPUT LIABILITY")
- **Azure Blue arrows** connect stages with direction
- **Roboto Mono labels** below nodes provide technical detail (e.g., "COPY 1: INDEX INGESTION", "LICENSED: UNKNOWN")
- Title in the top third is very large — dominant over the scene
- Scene fills the bottom two-thirds without competing with the text

Keep scenes **simple and readable**: 3-5 elements max, no overlapping labels, generous spacing. This style scales well from thumbnail to full size and reads clearly at a glance. Prefer this over abstract or decorative compositions for any article that has a clear process or mechanism to illustrate.

---

## Notes
- **Model:** `gemini-3-pro-image-preview` — 1K/2K/4K, `image_size` must use uppercase K
- **Text rendering:** The model renders title/subtitle text directly. Instructions specify font, color, size, and position explicitly. Always verify text legibility in the output.
- **No logos:** Explicitly forbidden in system prompt and layout instructions. Never ask the model to render Encypher, C2PA, or any other logo.
- **Encypher mark:** The brand mark is a circular badge with organic/wavy outer border + checkmark. Available as clean SVGs at `apps/marketing-site/public/encypher-mark.svg` (navy), `encypher-mark-white.svg`, `encypher-mark-teal.svg`, `encypher-mark-azure.svg`. Use these SVGs in UI/web contexts. For AI-generated images, describe the shape as instructed in the system prompt above.
- **No font names in image:** Never include "Roboto", "Roboto Mono", or any font name in the `IMAGE_DESCRIPTION` or `LAYOUT_INSTRUCTIONS` — only in the system prompt typography rules.
- **No revenue language:** Never include revenue splits, percentages, or "majority to publisher" / "you keep more" language in any image prompt.
- **Batch mode:** Repeat steps 1–8 for each image needed. Clean up temp script between runs.
- **Retry:** If the output doesn't match expectations, adjust `IMAGE_DESCRIPTION` and re-run. The model responds well to more specific scene descriptions.
